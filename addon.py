"""idolpx Installer"""

import xbmc, xbmcgui
import os, sys, json, time, shutil

from libs import requests
from libs import kodi
import installer

# Initialize Global Variables
window = xbmcgui.Window(10000)
current = json.loads('{"config_version": "00000000","test_version": "00000000"}')
current_version = '00000000'
remote = json.loads('{"config_version": "00000000","test_version": "00000000"}')
remote_version = '00000000'
version_file = ''
url = ''
hash = ''


def getParams():
    params = {
                'd' : kodi.get_mac(),
                'os': kodi.get_info('System.OSVersionInfo'),
                'id': kodi.get_setting('deviceid'),
                'kv': kodi.get_version()
            }
    return params


# Get Current Version
def getLocalVersion():
    global current, current_version, version_file
    
    path = xbmc.translatePath('special://userdata')
    version_file = path+'version.json'
    kodi.debug(version_file)
    try: 
        current = json.load(open(version_file))

        # Prompt for Configuration Update
        if kodi.get_setting('update_test') != 'true':
            current_version = current['config_version']
        else:
            current_version = current['test_version']

    except Exception, e: 
        kodi.debug('getLocalVersion: '+str(e))
        
    kodi.debug('Current Version: '+current_version)


# Get Remote Settings
def getRemoteVersion():
    global remote, remote_version, url, hash
    
    dp = xbmcgui.DialogProgress()
    dp.create('idolpx Installer', 
            'Checking for update...', 
            '', 
            'Please wait...')
    dp.update(100)

    try:
        # Prompt for Device ID if it is not set
        if not kodi.get_setting('deviceid'):
            kb = xbmc.Keyboard('default', 'heading')
            kb.setHeading('Enter your name or something so I know who you are \r\nand will allow you access to updates')
            kb.setDefault('')
            kb.setHiddenInput(False)
            kb.doModal()
            if (kb.isConfirmed()):
                kb_input = kb.getText()
                if (len(kb_input) > 3):
                    kodi.set_setting('deviceid', kb_input)
                    kodi.notify('Device ID set!', '['+kb_input+']')
                else:
                    kodi.notify('Access denied!', 'Device ID not set.')
                    return
            else:
                kodi.notify('Access denied!', 'Device ID not set.')
                return

        params = getParams()
        params['cv'] = current_version
        kodi.debug('Config URL: '+kodi.get_setting('update_url'))
        response = requests.get(kodi.get_setting('update_url'), params=params)
        remote = json.loads(response.text)
        kodi.debug(json.dumps(remote))

        if kodi.get_setting('update_test') != 'true':
            remote_version = remote['config_version']
            url = remote['config_url']
        else:
            remote_version = remote['test_version']
            url = remote['test_url']
        
        response = requests.get(url+'.md5')
        hash = response.text
        kodi.debug('MD5 HASH: '+hash)

    except Exception, e: 
        kodi.debug('getRemoteVersion: '+str(e))
        
    dp.close()
    kodi.debug('Remote Version: '+remote_version)


def updateKodi():
    global remote

    try:
        # Prompt for Kodi Update
        if kodi.get_setting('update_kodi') == 'true':
            if kodi.platform() == 'android' and remote['kodi_version'] != kodi.get_version():
                choice = xbmcgui.Dialog().yesno('idolpx Installer',
                                                'A new version of Kodi is available!',
                                                'Current version is [B]'+kodi.get_version()+'[/B].[CR]',
                                                'Would you like to install version [B]'+remote['kodi_version'] +'[/B]?')
                if choice == 1:
                    installer.installAPK(remote['kodi_url'])
                    
    except Exception, e: 
        kodi.debug('updateKodi: '+str(e))


def updateConfig():
    global current, current_version, remote, remote_version, version_file, url, hash

    try:
        updateKodi()

        # Is There an existing update.zip file ready to install?
        update_file = xbmc.translatePath('special://home/update.zip')
        if os.path.exists(update_file):
            kodi.debug('Update File: '+update_file)
            url = '/update.zip'
            hash = ''
            choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                                'An update file exists!',
                                                '',
                                                'Would you like to install this update?')
        else:
            if remote_version != current_version:
                choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                                'A new configuration is available!',
                                                'Current version is [B]'+current_version+'[/B].[CR]',
                                                'Would you like to install version [COLOR green][B]'+remote_version+'[/B][/COLOR]?')
            else:
                choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                                'Current version is [B]'+current_version+'[/B].[CR]',
                                                'Would you like to reinstall version [B]'+remote_version+'[/B]?')

        if choice == 1:
            # Give service enough time to stop downloading
            time.sleep(3)

            if installer.installConfig(url, hash):
            
                # Save Installed Version to file
                with open(version_file, "w") as outfile:
                    json.dump(remote, outfile)

                # Adjust Advanced Settings
                installer.adjust_advancedSettings()

                choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                                'A restart is required. Would you like to restart Kodi now?')
                if choice == 1:
                    kodi.kill()

                xbmcgui.Dialog().ok('idolpx Installer', 
                                    'Update checks complete!')
            else:

                xbmcgui.Dialog().ok('idolpx Installer', 
                                    'Update canceled!')
                                     
    except Exception, e: 
        kodi.debug('updateConfig: '+str(e))

def showAdult(status, pin='0'):
    global window

    if status == None:
        status = window.getProperty('idolpx.installer.adultstatus')

    if status == 'true':
        # Enable Adult Addons
        if pin == '0':
            pin = xbmcgui.Dialog().numeric(0,'Enter PIN')

        if pin == kodi.get_setting('adultpin'):
            status = 'true'
        else:
            status = 'abort'
    else:
        # Disable Adult Addons
        status = 'false'

    kodi.debug('Adult Addons Enabled: ' + status)
    if status != 'abort':
        window.setProperty('idolpx.installer.adultstatus', status)
        
        addonPath = xbmc.translatePath(os.path.join('special://home', 'addons'))
        resourcePath = os.path.join(addonPath, kodi.addon_id(), 'resources')
        nsfw_addons = os.path.join(resourcePath, 'nsfw_addons.dat')
        with open(nsfw_addons, 'r') as myfile:
            addons = myfile.read().split('\n')

        for addon in addons:
            try:
                # Move Addon
                if status == 'true':
                    shutil.move(os.path.join(resourcePath, addon), os.path.join(addonPath, addon))
                    #kodi.update_enabled(addon, 1)
                else:
                    shutil.move(os.path.join(addonPath, addon), os.path.join(resourcePath, addon))
                    #kodi.update_enabled(addon, 0)

                # Enable/Disable Addon
                query = '{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled","params":{"addonid":"%s", "enabled":%s}}' % (addon, status)
                kodi.execute_jsonrpc(query)
                kodi.debug(query)
                xbmc.sleep(200)

            except:
                pass

        kodi.execute('UpdateLocalAddons()')
        kodi.execute('UpdateAddonRepos()')
        #xbmc.sleep(1000)
        #kodi.execute('ReloadSkin()')
        
        kodi.set_setting('adultstatus', status)         
        
        if status == 'true': 
            kodi.notify('Adult Addons','Enabled!')
        else: 
            kodi.notify('Adult Addons', 'Disabled!')
       
    else:
        kodi.notify('Adult Addons', 'Invalid PIN!')

def optimize():
    installer.adjust_advancedSettings()
    choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                    'A restart is required. Would you like to restart Kodi now?')
    if choice == 1:
        kodi.kill()


def backup():
    choice = xbmcgui.Dialog().yesno(
                'idolpx Installer', 
                'Backup Current Configuration?'
            )
    if choice == 1:
        installer.createConfig()


if __name__ == '__main__':
        kodi.debug(sys.argv)

        arg = None
        try: 
            arg = sys.argv[1].lower()
            kodi.debug(arg)
        except: pass

        if arg == 'backup':
            backup()

        elif arg == 'optimize':
            optimize()

        elif arg == 'showadult':
            showAdult(sys.argv[2].lower(), sys.argv[3].lower())

        elif arg == 'updateKodi':
            getLocalVersion()
            getRemoteVersion()
            updateKodi()

        else:
            
            if window.getProperty('idolpx.installer.running') == 'true':
                kodi.debug('Addon is already running. Exiting...')
            else:
                window.setProperty('idolpx.installer.running', 'true')

                getLocalVersion()
                getRemoteVersion()
                updateConfig()

            window.clearProperty('idolpx.installer.running')
