# kodi.idolpx.com

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import sys, os, time, shutil, hashlib, glob, json, re, subprocess

from libs import requests
from libs import kodi
from libs import maintenance
from libs import zfile as zipfile

window = xbmcgui.Window(10000)
dp = xbmcgui.DialogProgress()

def size_format(num):
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if abs(num) < 1024.0:
            return "%3.2f%s" % (num, unit)
        num /= 1024.0
    return "%3.2f%s" % (num, 'PB')


def xml_data_advSettings(size):
	xml_data="""<advancedsettings>
	  <network>
	    <curlclienttimeout>10</curlclienttimeout>
	    <curllowspeedtime>20</curllowspeedtime>
	    <curlretries>2</curlretries>    
	  </network>
	  <cache>
		<memorysize>%s</memorysize> 
		<buffermode>2</buffermode>
		<readfactor>20</readfactor>
	  </cache>
</advancedsettings>""" % size
	return xml_data


def adjust_advancedSettings():
	XML_FILE   =  xbmc.translatePath('special://home/userdata/advancedsettings.xml')
	MEM        =  kodi.get_info("System.Memory(total)")
	FREEMEM    =  kodi.get_info("System.FreeMemory")
	BUFFER_F   =  re.sub('[^0-9]','',FREEMEM)
	BUFFER_F   = int(BUFFER_F) / 3
	BUFFERSIZE = BUFFER_F * 1024 * 1024
		
	with open(XML_FILE, "w") as f:
		xml_data = xml_data_advSettings(str(BUFFERSIZE))
		f.write(xml_data)
        kodi.notify('Advanced Settings', 'Buffer set to: ' + size_format(BUFFER_F))


def do_maintenance():
    packagesdir    =  xbmc.translatePath('special://home/addons/packages')
    thumbnails    =  xbmc.translatePath('special://home/userdata/Thumbnails')

    auto_clean  = kodi.get_setting('startup.cache')
    filesize = int(kodi.get_setting('filesize_alert'))
    filesize_thumb = int(kodi.get_setting('filesizethumb_alert'))
    maxpackage_zips = int(kodi.get_setting('packagenumbers_alert'))

    total_size2 = 0
    total_size = 0
    count = 0

    maintenance.purgeHome()
    kodi.debug('Home Purged!')

    for dirpath, dirnames, filenames in os.walk(packagesdir):
        count = 0
        for f in filenames:
            count += 1
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    total_sizetext = "%.0f" % (total_size/1024000.0)
        
    if int(total_sizetext) > filesize:
        maintenance.purgePackages()
        kodi.debug('Packages Purged!')
                
    for dirpath2, dirnames2, filenames2 in os.walk(thumbnails):
        for f2 in filenames2:
            fp2 = os.path.join(dirpath2, f2)
            total_size2 += os.path.getsize(fp2)
    total_sizetext2 = "%.0f" % (total_size2/1024000.0)

    if int(total_sizetext2) > filesize_thumb:
        maintenance.deleteThumbnails()
        kodi.debug('Thumbnails Deleted!')
            
    total_sizetext = "%.0f" % (total_size/1024000.0)
    total_sizetext2 = "%.0f" % (total_size2/1024000.0)
        
    kodi.debug('Maintenance Status -> Packages: '+ str(total_sizetext) +  ' MB'  ' - Images: ' + str(total_sizetext2) + ' MB')
    time.sleep(3)
    if auto_clean  == 'true': 
        maintenance.clearCache()
        kodi.debug('Cache cleared!')

#***************************************************************
def FIX_SPECIAL(url):
    USERDATA     =  xbmc.translatePath('special://home/userdata')
    ADDONS       =  xbmc.translatePath('special://home/addons')
    dp.create('idolpx Installer',
              'Converting physical path to special://',
              '',
              'Please wait...')
    for root, dirs, files in os.walk(url):
        for file in files:
            if file.endswith(".xml"):
                try:
                    a = open((os.path.join(root, file))).read()
                    b = a.replace(USERDATA, 'special://profile/').replace(ADDONS,'special://home/addons/')
                    if '/\\' in b:
                        c = b.split('/\\')
                        b='/'.join([c[0],c[1].replace('\\','/')])
                    if '//' in b[10:]:
                        b = b.split('://')
                        b[1] = b[1].replace('//','/')
                        b = '://'.join([b[0],b[1]])
                    f = open((os.path.join(root, file)), mode='w')
                    f.write(str(b))
                    f.close()
                except:
                    pass
    dp.close()

#****************************************************************
def installConfig(url, hash=None):
    path = xbmc.translatePath('special://home')
    filename = url.split('/')[-1]
    destination_file = os.path.join(path, filename)

    # Download File
    dp.create('idolpx Installer',
              'Downloading: '+filename,
              '',
              'Please wait...')

    while 1:
        kodi.debug('Downloading '+url+' to '+destination_file)
        if download_with_resume(url, destination_file, _download_progress):

            # Check to make sure file validates before install
            if validate_file(destination_file, hash) or hash == '':

#                # Delete 'addons' folder
#                dp.update(100, "Removing 'addons' folder",
#                        '',
#                        'Please wait...')
#                try: 
#                    addons = xbmc.translatePath('special://home/addons')
#                    os.rename(addons, addons+'.old')
#                except: 
#                    xbmcgui.Dialog().ok(
#                        'idolpx Installer',
#                        '[COLOR red]Error renaming addons![/COLOR]',
#                        '',
#                        '[B]'+addons[-40:]+'[/B]'
#                    )
#                    return False
#                    break

                # Rename addons folder
                try:
                    addons = xbmc.translatePath('special://home/addons')
                    os.rename(addons, addons+'.old')
                except: 
                    xbmcgui.Dialog().ok(
                        'idolpx Installer',
                        '[COLOR red]Error renaming addons![/COLOR]',
                        '',
                        '[B]'+addons[-40:]+'[/B]'
                    )
                    return False
                    break

                # Rename userdata folder
                try:
                    userdata = xbmc.translatePath('special://home/userdata')
                    os.rename(userdata, userdata+'.old')
                except:
                    xbmcgui.Dialog().ok(
                        'idolpx Installer',
                        '[COLOR red]Error renaming userdata![/COLOR]',
                        '',
                        '[B]'+userdata[-40:]+'[/B]'
                    )
                    return False
                    break

                # Extract File
                try:
                    extract_path = xbmc.translatePath('special://home')
                    unzip(destination_file, extract_path)
                except Exception, e: 
                    xbmcgui.Dialog().ok(
                        'idolpx Installer',
                        '[COLOR red]Error Extracting![/COLOR]',
                        str(e),
                        '[B]['+destination_file[-40:]+'][/B]'
                    )
                    
                    # Restore old addons and data
                    #shutil.rmtree(addons)
                    #shutil.rmtree(userdata)
                    #os.rename(addons+'.old', addons)
                    #os.rename(userdata+'.old', userdata)
                    return False
                    break

                # Copy settings files back into place
                dp.update(100, 'Restoring Settings',
                        '',
                        'Please wait...')

                # Copy addon settings back into place
                try: shutil.copyfile(os.path.join(userdata+'.old', 'addon_data', kodi.addon_id(), 'settings.xml'),
                                     os.path.join(userdata, 'addon_data', kodi.addon_id(), 'settings.xml'))
                except: pass

                if kodi.get_setting('keepadv') == 'true':
                    try: shutil.copyfile(os.path.join(userdata+'.old', 'advancedsettings.xml'), os.path.join(userdata, 'advancedsettings.xml'))
                    except: pass
                if kodi.get_setting('keepfavourites') == 'true':
                    try: shutil.copyfile(os.path.join(userdata+'.old', 'favourites.xml'), os.path.join(userdata, 'favourites.xml'))
                    except: pass
                if kodi.get_setting('keepgui') == 'true':
                    try: shutil.copyfile(os.path.join(userdata+'.old', 'guisettings.xml'), os.path.join(userdata, 'guisettings.xml'))
                    except: pass
                if kodi.get_setting('keepsources') == 'true':
                    try: shutil.copyfile(os.path.join(userdata+'.old', 'sources.xml'), os.path.join(userdata, 'sources.xml'))
                    except: pass
                    try:
                        if kodi.get_setting('keepmuisc') == 'true':
                            for file in glob.glob(os.path.join(userdata+'.old', 'Database', 'MyMusic*.db')):
                                shutil.copyfile(file, os.path.join(userdata, 'Database'))

                        if kodi.get_setting('keepvideos') == 'true':
                            for file in glob.glob(os.path.join(userdata+'.old','Database','MyVideos*.db')):
                                shutil.copyfile(file, os.path.join(userdata, 'Database'))
                    except: pass

                # Enable Adult Addons
                if kodi.get_setting('adultstatus') == 'true':
                    kodi.debug('Adult Addons Enabled')
                    kodi.execute('XBMC.RunScript(%s,%s,%s,%s)' % (kodi.addon_id(), 'showadult', 'true', kodi.get_setting('adultpin')))
                else:
                    kodi.debug('Adult Addons Disabled')

                # Delete old 'userdata' folder
                dp.update(100, "Cleaning up",
                        '',
                        'Please wait...')
                try: 
                    shutil.rmtree(addons+'.old')
                    shutil.rmtree(userdata+'.old')
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
    
    #Fix_Special:
    USERDATA     =  xbmc.translatePath('special://home/userdata')
    if kodi.get_setting('fix_special') == 'true':
                    try: FIX_SPECIAL(USERDATA)
                    except: pass
    
    source = [xbmc.translatePath('special://home/addons')]
    source.append(xbmc.translatePath('special://home/userdata'))

    path = xbmc.translatePath('special://home')
    version = time.strftime("%Y%m%d_%H%M")
    destination_file = 'kodi.'+version+'.zip'
    
    # Update version.json file
    current = json.loads('{"config_version": "'+version+'","test_version": "'+version+'"}')
    version_path = xbmc.translatePath('special://userdata')
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
    #std_addons = xbmc.translatePath(os.path.join('special://home', 'addons', kodi.addon_id(), 'resources', 'std_addons.dat'))
    #kodi.debug(std_addons)
    #with open(std_addons, 'r') as myfile:
    #    exclusions = myfile.read().split('\n')

    # Ignore certain files too
    #exclusions.extend(
    exclusions = ['.pyc', '.pyd', '.pyo', 'Thumbs.db', '.DS_Store', '__MACOSX',
                  'addons'+os.sep+'packages', 'addons'+os.sep+'temp', 'userdata'+os.sep+'library',
                  'userdata'+os.sep+'peripheral_data', 'userdata'+os.sep+'playlists', 
                  'userdata'+os.sep+'Thumbnails', 'Textures13.db', 'MyMusic', 'MyVideos', '.lock']

    # Cleanse installer settings before backup
    deviceid = kodi.get_setting('deviceid')
    mac = kodi.get_setting('mac')
    update_test = kodi.get_setting('update_test')

    kodi.set_setting('deviceid', '')
    kodi.set_setting('mac', '')
    kodi.set_setting('update_test', 'false')

    # Backup Files
    dp.create('idolpx Installer', 
              'Creating Backup: '+destination_file, 
              '', 
              'Please wait...')
    kodi.debug('Creating Configuration Backup: '+destination_file)
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
        
    # Restore installer settings after backup
    kodi.set_setting('deviceid', deviceid)
    kodi.set_setting('mac', mac)
    kodi.set_setting('update_test', update_test)

#****************************************************************
def installAPK(url):
    path = '/storage/emulated/0/Download' #xbmc.translatePath('special://home/addons/packages')
    filename = url.split('/')[-1]
    destination_file = os.path.join(path, filename)


    # Download File
    dp.create('idolpx Installer', 
            'Downloading: '+filename, 
            '', 
            'Please wait...')
    kodi.debug('Downloading '+url+' to '+destination_file)

    while 1:
        if download_with_resume(url, destination_file, _download_progress):

            # Give instructions for installing APK


            # Install APK
            kodi.debug('Installing APK:'+destination_file)
            kodi.get_setting('runonstart', 'true')
            kodi.set_setting('cleanup', destination_file)
            #kodi.execute('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+destination_file+'")')
            #kodi.execute('StartAndroidActivity("","android.intent.action.INSTALL_PACKAGE ","application/vnd.android.package-archive","content://%s")' % destination_file)
            #FMANAGER  = {0:'com.android.documentsui',1:CUSTOM}[int(REAL_SETTINGS.getSetting('File_Manager'))]
            #xbmc.executebuiltin('StartAndroidActivity(%s,,,"content://%s")'%(FMANAGER,apkfile))

            command = 'pm install -rgd ' + destination_file
            launch_command(command)

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

def launch_command(command_launch):
    try:
        kodi.debug('[%s] %s' % ('LAUNCHING SUBPROCESS:', command_launch), 2)
        external_command = subprocess.call(command_launch, shell = True, executable = '/system/bin/sh')
    except Exception, e:
        try:
            kodi.debug('[%s] %s' % ('ERROR LAUNCHING COMMAND !!!', e.message, external_command), 2)
            kodi.debug('[%s] %s' % ('LAUNCHING OS:', command_launch), 2)
            external_command = os.system(command_launch)
        except:
            kodi.debug('[%s]' % ('ERROR LAUNCHING COMMAND !!!', external_command), 2)


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

    kodi.debug('MD5 Hash:'+m.hexdigest())
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
        kodi.debug('File already downloaded.')
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
        kodi.debug('File size is %s' % file_size)
        kodi.debug('Starting at %s' % first_byte)
        kodi.debug('File Mode %s' % file_mode)

        # If tmp_file is bigger then something is screwy. Start over.
        if first_byte > file_size:
            kodi.debug('File bigger. Starting over.')
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
                            kodi.debug('Pausing transfer!')
                            return False
                        
                        if percent % 10 == 0:
                            kodi.debug('Download @ '+str(percent)+'%')

    except IOError as e:
        kodi.debug('IO Error - %s' % e)
        return False

    except Exception, e: 
        kodi.debug(str(e))
        return False

    finally:
        # rename the temp download file to the correct name if fully downloaded
        if file_size == os.path.getsize(tmp_file_path):
            # if there's a hash value, validate the file
            if hash and not validate_file(tmp_file_path, hash):
                raise Exception('Error validating the file against its MD5 hash')
                return False

            shutil.move(tmp_file_path, file_path)
            kodi.debug('Transfer complete!')
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
    if kodi.is_playing() or window.getProperty('idolpx.installer.running') == 'true':
        return -1
    else:
        return percent

def zip(_in, _out, exclusions):
    zout = _out.split(os.sep)[-1]
    zip_file = zipfile.ZipFile(_out, 'w', zipfile.ZIP_DEFLATED)
    try:
        for zin in _in:
            parent_folder = os.path.dirname(zin)
            kodi.debug('Source :'+parent_folder)
            for root, folders, files in os.walk(zin):
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + os.sep, '')
                    if not any(e in relative_path for e in exclusions):
                        kodi.debug("Adding '%s' to archive." % relative_path)
                        zip_file.write(absolute_path, relative_path)
                    else:
                        kodi.debug("Excluding '%s' from the archive." % relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + os.sep, '')
                    if not any(e in relative_path for e in exclusions):
                        kodi.debug("Adding '%s' to archive." % relative_path)
                        dp.update(100, 'Archiving: '+zout, 
                                         '', 
                                         '[B]' + relative_path + '[/B]')
                        zip_file.write(absolute_path, relative_path)
                    else:
                        kodi.debug("Excluding '%s' from the archive." % relative_path)

        return True

    except IOError, e:
        kodi.debug(str(e))
        return False
    except OSError, e:
        kodi.debug(str(e))
        return False
    except zipfile.BadZipfile, e:
        kodi.debug(str(e))
        return False
    finally:
        zip_file.close()

def unzip(_in, _out):
    zin = _in.split(os.sep)[-1]
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
                kodi.debug(str(e))


    except Exception, e:
        kodi.debug(str(e))
        return False

    return True
