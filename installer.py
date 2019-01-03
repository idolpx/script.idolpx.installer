# kodi.idolpx.com

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import sys, os, time, shutil, zipfile, hashlib, glob, json

from libs import requests
from libs import kodi

window = xbmcgui.Window(10000)
dp = xbmcgui.DialogProgress()

def size_format(num):
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if abs(num) < 1024.0:
            return "%3.2f%s" % (num, unit)
        num /= 1024.0
    return "%3.2f%s" % (num, 'PB')

#****************************************************************
def installConfig(url, hash=None):
    path = xbmc.translatePath(os.path.join('special://', 'home'))
    filename = url.split('/')[-1]
    destination_file = os.path.join(path, filename)

    # Download File
    dp.create('idolpx Installer',
              'Downloading: '+filename,
              '',
              'Please wait...')

    while 1:
        kodi.log('Downloading '+url+' to '+destination_file)
        if download_with_resume(url, destination_file, _download_progress):

            # Check to make sure file validates before install
            if validate_file(destination_file, hash) or hash == '':

                # Delete 'addons' folder
                dp.update(100, "Removing 'addons' folder",
                        '',
                        'Please wait...')
                try: shutil.rmtree(xbmc.translatePath(os.path.join('special://home', 'addons')))
                except: pass

                # Rename userdata folder
                try:
                    userdata = xbmc.translatePath(os.path.join('special://', 'userdata'))[:-1]
                    os.rename(userdata, userdata+'.old')
                except: pass

                try:
                    # Extract File
                    extract_path = xbmc.translatePath(os.path.join('special://', 'home'))
                    unzip(destination_file, extract_path)
                except: pass

                # Copy settings files back into place
                dp.update(100, 'Restoring Settings',
                        '',
                        'Please wait...')
                if kodi.get_setting('keepadv') == 'true':
                    try: shutil.copyfile(userdata+".old/advancedsettings.xml", userdata+"/advancedsettings.xml")
                    except: pass
                if kodi.get_setting('keepfavourites') == 'true':
                    try: shutil.copyfile(userdata+".old/favourites.xml", userdata+"/favourites.xml")
                    except: pass
                if kodi.get_setting('keepgui') == 'true':
                    try: shutil.copyfile(userdata+".old/guisettings.xml", userdata+"/guisettings.xml")
                    except: pass
                if kodi.get_setting('keepsources') == 'true':
                    try: shutil.copyfile(userdata+".old/sources.xml", userdata+"/sources.xml")
                    except: pass
                    try:
                        if kodi.get_setting('keepmuisc') == 'true':
                            for file in glob.glob(userdata+".old/Database/MyMusic*.db"):
                                shutil.copyfile(file, userdata+"/Database/")

                        if kodi.get_setting('keepvideos') == 'true':
                            for file in glob.glob(userdata+".old/Database/MyVideos*.db"):
                                shutil.copyfile(file, userdata+"/Database/")
                    except: pass

                # Copy addon settings back into place
                try: shutil.copyfile(userdata+".old/addon_data/"+kodi.addon_id+"/settings.xml",
                                    userdata+"/addon_data/"+kodi.addon_id+"/settings.xml")
                except: pass

                # Delete old 'userdata' folder
                dp.update(100, "Cleaning up",
                        '',
                        'Please wait...')
                try: shutil.rmtree(userdata+'.old')
                except: pass

                # Delete archives and partial downloads
                try:
                    for file in glob.glob(extract_path+"kodi.*.zip"):
                        os.remove(file)
                    for file in glob.glob(extract_path+"kodi.*.part"):
                        os.remove(file)
                    for file in glob.glob(extract_path+"kodi.*.md5"):
                        os.remove(file)
                    for file in glob.glob(extract_path+"update.*"):
                        os.remove(file)
                except: pass

                return True
                break

            else:
                choice = xbmcgui.Dialog().yesno('idolpx Installer',
                                                'File Validation Failed!',
                                                '',
                                                'Would you like to retry?')
                if choice == 0:
                    return False
                    break

        else:
            choice = xbmcgui.Dialog().yesno('idolpx Installer',
                                            'Transfer incomplete!',
                                            '',
                                            'Would you like to retry?')
            if choice == 0:
                return False
                break


def createConfig():
    source = [xbmc.translatePath(os.path.join('special://home', 'addons'))]
    source.append(xbmc.translatePath(os.path.join('special://', 'userdata')).rstrip(os.sep))

    path = xbmc.translatePath(os.path.join('special://','home'))
    version = time.strftime("%Y%m%d_%H%M")
    destination_file = 'kodi.'+version+'.zip'
    
    # Update version.json file
    current = json.loads('{"config_version": "'+version+'","test_version": "'+version+'"}')
    version_path = xbmc.translatePath(os.path.join('special://', 'userdata'))
    version_file = version_path+'version.json'
    with open(version_file, "w") as outfile:
        json.dump(current, outfile)

    # Delete archives and partial downloads
    try:
        for file in glob.glob(path+"kodi.*.zip"):
            os.remove(file)
        for file in glob.glob(version_path+"kodi.*.zip"):
            os.remove(file)
        for file in glob.glob(path+"kodi.*.part"):
            os.remove(file)
        for file in glob.glob(path+"kodi.*.md5"):
            os.remove(file)
    except: pass

    # Ignore standard addons
    #std_addons = xbmc.translatePath(os.path.join('special://home', 'addons', kodi.addon_id, 'resources', 'std_addons.dat'))
    #kodi.log(std_addons)
    #with open(std_addons, 'r') as myfile:
    #    exclusions = myfile.read().split('\n')

    # Ignore certain files too
    #exclusions.extend(
    exclusions = ['.pyc', '.pyd', '.pyo', 'Thumbs.db', '.DS_Store', '__MACOSX',
                       'addons/packages', 'addons/temp', 'userdata/library',
                       'userdata/peripheral_data', 'userdata/playlists', 'userdata/Thumbnails', 
                       'Textures13.db', 'MyMusic', 'MyVideos']

    # Download File
    dp.create('idolpx Installer', 
              'Creating Backup: '+destination_file, 
              '', 
              'Please wait...')
    kodi.log('Creating Configuration Backup: '+destination_file)
    if zip(source, path + destination_file, exclusions):
        validate_file(path + destination_file, "MD5")
        xbmcgui.Dialog().ok(
            'idolpx Installer',
            '[COLOR green]Backup Successful![/COLOR]',
            '',
            '[B]'+destination_file+'[/B]'
        )
    else:
        xbmcgui.Dialog().ok(
            'idolpx Installer',
            '[COLOR red]Backup Error![/COLOR]',
            '',
            '[B]'+destination_file+'[/B]'
        )


#****************************************************************
def installAPK(url):
    path = xbmc.translatePath(os.path.join('special://home','addons', 'packages', ''))
    filename = url.split('/')[-1]
    destination_file = os.path.join(path, filename)


    # Download File
    dp.create('idolpx Installer', 
            'Downloading: '+filename, 
            '', 
            'Please wait...')
    kodi.log('Downloading '+url+' to '+destination_file)

    while 1:
        if download_with_resume(url, destination_file, _download_progress):

            # Give instructions for installing APK


            # Install APK
            kodi.log('Installing APK:'+destination_file)
            kodi.get_setting('runonstart', 'true')
            kodi.set_setting('cleanup', destination_file)
            kodi.execute('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+destination_file+'")')
            return True
            break
        else:
            choice = xbmcgui.Dialog().yesno('idolpx Installer',
                                'Transfer incomplete!',
                                '',
                                'Would you like to retry?')
            if choice == 0:
                return False
                break


#****************************************************************
def validate_file(file_path, hash):
    """
    Validates a file against an MD5 hash value
 
    :param file_path: path to the file for hash validation
    :type file_path:  string
    :param hash:      expected hash value of the file
    :type hash:       string -- MD5 hash value
    """
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(1000 * 1000) # 1MB
            if not chunk:
                break
            m.update(chunk)

    with open(file_path+'.md5', 'w') as f:
        f.write("%s" % m.hexdigest())

    kodi.log('MD5 Hash:'+m.hexdigest())
    return m.hexdigest() == hash

def download_with_resume(url, file_path, callback=None, hash=None, timeout=10):
    """
    Performs a HTTP(S) download that can be restarted if prematurely terminated.
    The HTTP server must support byte ranges.
 
    :param file_path: the path to the file to write to disk
    :type file_path:  string
    :param hash: hash value for file validation
    :type hash:  string (MD5 hash value)
    """
     # don't download if the file exists
    if os.path.exists(file_path):
        kodi.log('File already downloaded.')
        return True

    try:
        block_size = 1000 * 1000 # 1MB
        filename = url.split('/')[-1]
        tmp_file_path = file_path + '.part'
        first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
        last_byte = first_byte
        file_mode = 'ab' if first_byte else 'wb'
        file_size = -1

        file_size = int(requests.head(url).headers['Content-length'])
        kodi.log('File size is %s' % file_size)
        kodi.log('Starting at %s' % first_byte)
        kodi.log('File Mode %s' % file_mode)

        # If tmp_file is bigger then something is screwy. Start over.
        if first_byte > file_size:
            kodi.log('File bigger. Starting over.')
            os.remove(tmp_file_path)
            first_byte = 0

        headers = {"Range": "bytes=%s-" % first_byte}
        r = requests.get(url, headers=headers, stream=True)
        with open(tmp_file_path, file_mode) as f:
            for chunk in r.iter_content(chunk_size=block_size): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

                    if callback:
                        last_byte = last_byte + block_size \
                            if last_byte < file_size \
                            else file_size

                        # Update dialog
                        percent = callback(filename, last_byte, file_size)
                        if percent == -1:
                            kodi.log('Pausing transfer!')
                            return False
                        
                        if percent % 10 == 0:
                            kodi.log('Download @ '+str(percent)+'%')

    except IOError as e:
        kodi.log('IO Error - %s' % e)
        return False

    except Exception, e: 
        kodi.log(str(e))
        return False

    finally:
        # rename the temp download file to the correct name if fully downloaded
        if file_size == os.path.getsize(tmp_file_path):
            # if there's a hash value, validate the file
            if hash and not validate_file(tmp_file_path, hash):
                raise Exception('Error validating the file against its MD5 hash')
                return False

            shutil.move(tmp_file_path, file_path)
            kodi.log('Transfer complete!')
            return True

        elif file_size == -1:
            raise Exception('Error getting Content-Length from server: %s' % url)
            return False


def _download_progress(filename, bytes_received, bytes_total):
    percent = min((bytes_received * 100) / bytes_total, 100)
    dp.update(percent, "Downloading: "+filename, 
                       '', 
                       'Transferred: [B]' + size_format(bytes_received) + '[/B] of [B]' + size_format(bytes_total) + '[/B] ([B]' + str(percent) + '%[/B])')

    if dp.iscanceled():
        raise Exception("Canceled")
        return -1
    else:
        return percent

def _download_background(filename, bytes_received, bytes_total):
    percent = min((bytes_received * 100) / bytes_total, 100)
    if kodi.isPlaying() or window.getProperty('idolpx.installer.running') == 'true': # kodi.get_setting('isrunning') == 'true':
        return -1
    else:
        return percent

def zip(_in, _out, exclusions):
    zout = _out.split('/')[-1]
    zip_file = zipfile.ZipFile(_out, 'w', zipfile.ZIP_DEFLATED)
    try:
        for zin in _in:
            parent_folder = os.path.dirname(zin)
            kodi.log('Source :'+parent_folder)
            for root, folders, files in os.walk(zin):
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + os.sep, '')
                    if not any(e in relative_path for e in exclusions):
                        kodi.log("Adding '%s' to archive." % relative_path)
                        zip_file.write(absolute_path, relative_path)
                    else:
                        kodi.log("Excluding '%s' from the archive." % relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + os.sep, '')
                    if not any(e in relative_path for e in exclusions):
                        kodi.log("Adding '%s' to archive." % relative_path)
                        dp.update(100, 'Archiving: '+zout, 
                                         '', 
                                         '[B]' + relative_path + '[/B]')
                        zip_file.write(absolute_path, relative_path)
                    else:
                        kodi.log("Excluding '%s' from the archive." % relative_path)

        return True

    except IOError, e:
        kodi.log(str(e))
        return False
    except OSError, e:
        kodi.log(str(e))
        return False
    except zipfile.BadZipfile, e:
        kodi.log(str(e))
        return False
    finally:
        zip_file.close()

def unzip(_in, _out):
    zin = _in.split('/')[-1]
    zip_file = zipfile.ZipFile(_in, 'r')
    nFiles = float(len(zip_file.infolist()))
    count = 0

    try:
        for item in zip_file.infolist():
            count += 1
            update = count / nFiles * 100
            dp.update(int(update), 'Extracting: '+zin, 
                                   '', 
                                   '[B]' + str(item.filename) + '[/B]')
            try:
                zip_file.extract(item, _out)
            except Exception, e:
                kodi.log(str(e))


    except Exception, e:
        kodi.log(str(e))
        return False

    return True

