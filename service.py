import xbmc, xbmcgui
import os, time, json

from libs import requests
from libs import kodi

import installer

addon_id = kodi.addon_id()
addon_name = kodi.addon_name()

kodi.debug('STARTING ' + addon_name.upper() + ' SERVICE')

# Get Current Version
current = json.loads('{"config_version": "00000000","test_version": "00000000"}')
path = xbmc.translatePath('special://userdata')
version_file = path+'version.json'
try: current = json.load(open(version_file))
except: pass

def getParams():
    params = {
                'd' : kodi.get_mac(),
                'os': kodi.get_info('System.OSVersionInfo'),
                'id': kodi.get_setting('deviceid'),
                'kv': kodi.get_version()
            }
    return params


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    wait = 10 #900 # Set wait to 15mins
    kodi.update_lastused('script.idolpx.installer')
    kodi.update_lastused('plugin.video.mediasnatcher')
    window = xbmcgui.Window(10000)
    window.clearProperty('idolpx.installer.running')
    installer.do_maintenance()

    while not monitor.abortRequested():

        # Start idolpx Installer if runonstart is set
        if kodi.get_setting('runonstart') == 'true':
            kodi.get_setting('runonstart', 'false')
            kodi.execute('XBMC.RunScript('+addon_id+')', True)

        # Clean up Kodi apk after install
        cleanup = kodi.get_setting('cleanup')
        if len(cleanup):
            try: 
                os.remove(cleanup)
                kodi.set_setting('cleanup', '')
            except: pass

        # Sleep/wait for abort for 10 seconds 12 hours is 43200   1 hours is 3600
        # 24hrs = 86400, 5min = 300
        if monitor.waitForAbort(wait):
            # Abort was requested while waiting. We should exit
            kodi.debug('CLOSING ' + addon_name.upper() + ' SERVICES')
            break  

        # Is something playing?
        if kodi.is_playing() or installer.window.getProperty('idolpx.installer.running') == 'true':
            kodi.debug('Something is playing or addons is running!')
            wait = 300
        else:
            kodi.debug('Not Playing!')

            # Check for update
            kodi.debug('Check for Update.')

            # Get Remote Settings
            try:
                if kodi.get_setting('update_test') != 'true':
                    current_version = current['config_version']
                else:
                    current_version = current['test_version']

                params = getParams()
                params['cv'] = current_version
                response = requests.get(kodi.get_setting('update_url'), params=params)
                remote = json.loads(response.text)

                # If kodi version is different on server then execute installer
                if kodi.get_setting('update_kodi') == 'true':
                    if kodi.platform() == 'android' and remote['kodi_version'] != kodi.get_version():
                        # Start idolpx Installer
                        kodi.execute('XBMC.RunScript('+addon_id+',updateKodi)', True)

                if kodi.get_setting('update_test') != 'true':
                    remote_version = remote['config_version']
                    url = remote['config_url']
                else:
                    remote_version = remote['test_version']
                    url = remote['test_url']

                # If config version is different on server then execute installer
                if current_version != remote_version:
                    kodi.debug("New confguration version available.")

                    # Setup variables
                    path = xbmc.translatePath('special://home')
                    filename = url.split('/')[-1]
                    destination_file = os.path.join(path, filename)

                    # Download in background
                    #kodi.debug('Downloading '+url+' to '+destination_file)
                    #if installer.download_with_resume(url, destination_file, installer._download_background):

                    # Start idolpx Installer
                    kodi.execute('XBMC.RunScript('+addon_id+')', True)
                else:
                    kodi.debug("No configuration update is available.")

            except: 
                kodi.debug('Error getting version info.')

            # Set wait to 12hrs
            wait = 43200
