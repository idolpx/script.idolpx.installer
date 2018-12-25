"""idolpx Installer"""

import xbmc, xbmcgui
import os, sys, json, time

from libs import requests
from libs import kodi
import installer

def main():
    dp = xbmcgui.DialogProgress()
    dp.create('idolpx Installer', 
            'Checking for update...', 
            '', 
            'Please wait...')
    dp.update(100)

    # Get Current Version
    update_file = xbmc.translatePath(os.path.join('special://', 'home'))+'update.zip'

    current = json.loads('{"config_version": "00000000","test_version": "00000000"}')
    path = xbmc.translatePath(os.path.join('special://', 'userdata'))
    version_file = path+'version.json'
    try: current = json.load(open(version_file))
    except: pass

    # Get Remote Settings
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

        # Prompt for Configuration Update
        if kodi.get_setting('update_test') != 'true':
            current_version = current['config_version']
        else:
            current_version = current['test_version']

        params = {
                    'd': kodi.getInfoLabel('Network.MacAddress'),
                    'os': kodi.getInfoLabel('System.OSVersionInfo'),
                    'id': kodi.get_setting('deviceid'),
                    'kv': kodi.get_version()
                }

        params['cv'] = current_version
        kodi.log('Config URL: '+kodi.get_setting('update_url'))
        response = requests.get(kodi.get_setting('update_url'), params=params)
        remote = json.loads(response.text)
        kodi.log(json.dumps(remote))
        dp.close()

        if kodi.get_setting('update_test') != 'true':
            remote_version = remote['config_version']
            url = remote['config_url']
            hash = remote['config_md5']
        else:
            remote_version = remote['test_version']
            url = remote['test_url']
            hash = remote['test_md5']

        # Prompt for Kodi Update
        if kodi.get_setting('update_kodi') == 'true':
            if kodi.platform() == 'android' and remote['kodi_version'] != kodi.get_version():
                choice = xbmcgui.Dialog().yesno('idolpx Installer',
                                                'A new version of Kodi is available!',
                                                'Current version is [B]'+kodi.get_version()+'[/B].[CR]',
                                                'Would you like to install version [B]'+remote['kodi_version'] +'[/B]?')
                if choice == 1:
                    installer.installAPK(remote['kodi_url'])

        kodi.log('Update File: '+update_file)
        if os.path.exists(update_file):
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

                choice = xbmcgui.Dialog().yesno('idolpx Installer', 
                                                'A restart is required. Would you like to restart Kodi now?')
                if choice == 1:
                    kodi.kill()

                xbmcgui.Dialog().ok('idolpx Installer', 
                                    'Update checks complete!')
            else:

                xbmcgui.Dialog().ok('idolpx Installer', 
                                    'Update canelled!')
                                     
                
    except Exception, e: 
        kodi.log(str(e))


def backup():
    choice = xbmcgui.Dialog().yesno(
                'idolpx Installer', 
                'Backup Current Configuration?'
            )
    if choice == 1:
        installer.createConfig()


if __name__ == '__main__':
    window = xbmcgui.Window(10000)
    if window.getProperty('idolpx.installer.running') == 'true':
        kodi.log('Addon is already running. Exiting...')
    else:
        window.setProperty('idolpx.installer.running', 'true')

        arg = None
        try: arg = sys.argv[1].lower()
        except: pass

        if arg == 'backup':
            backup()
        else:
            main()

        window.clearProperty('idolpx.installer.running')

