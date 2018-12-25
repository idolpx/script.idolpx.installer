import xbmc, xbmcgui
import os, json, sqlite3

from libs import requests
from libs import kodi
from datetime import datetime
import installer

addon_id = kodi.addon_id
addon_name = kodi.addon.getAddonInfo('name')
KODI = xbmc.getInfoLabel('System.BuildVersion')[:2]

addon_py = xbmc.translatePath(os.path.join('special://home', 'addons', addon_id, 'addon.py'))

kodi.log('STARTING ' + addon_name.upper() + ' SERVICE')

# Get Current Version
current = json.loads('{"config_version": "00000000","test_version": "00000000"}')
path = xbmc.translatePath(os.path.join('special://', 'userdata'))
version_file = path+'version.json'
try: current = json.load(open(version_file))
except: pass

def getParams():
    params = {
                'd': kodi.getInfoLabel('Network.MacAddress'),
                'os': kodi.getInfoLabel('System.OSVersionInfo'),
                'id': kodi.get_setting('deviceid'),
                'kv': kodi.get_version()
            }
    return params

def addon_database():
    db_version = {

        '17': 27,# Krypton
        '18': 28 # Leia
    }
    return xbmc.translatePath("special://database/Addons%s.db"
                              % db_version.get(KODI, "")).decode('utf-8')

def update_lastused():
    conn = sqlite3.connect(addon_database(), isolation_level=None, timeout=120)
    cursor = conn.cursor()
    cursor.execute("UPDATE installed SET lastUsed = '"+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') +"' WHERE addonId = 'script.idolpx.installer'")
    cursor.execute("UPDATE installed SET lastUsed = '"+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') +"' WHERE addonId = 'plugin.video.mediasnatcher'")
    cursor.close()
    conn.close()
    #xbmc.executebuiltin('ReloadSkin()')

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    wait = 10 #900 # Set wait to 15mins
    kodi.set_setting('isrunning', 'false')
    update_lastused()

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
            kodi.log('CLOSING ' + addon_name.upper() + ' SERVICES')
            break  

        # Is something playing?
        if kodi.isPlaying() or installer.window.getProperty('idolpx.installer.running') == 'true':
            kodi.log('Something is playing or addons is running!')
            wait = 300
        else:
            kodi.log('Not Playing!')

            # Check for update
            kodi.log('Check for Update.')

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
                        kodi.execute('XBMC.RunScript('+addon_id+')', True)

                if kodi.get_setting('update_test') != 'true':
                    remote_version = remote['config_version']
                    url = remote['config_url']
                else:
                    remote_version = remote['test_version']
                    url = remote['test_url']

                # If config version is different on server then execute installer
                if current_version != remote_version:
                    kodi.log("New confguration version available.")

                    # Setup variables
                    path = xbmc.translatePath(os.path.join('special://','home'))
                    filename = url.split('/')[-1]
                    destination_file = os.path.join(path, filename)

                    # Download in background
                    #kodi.log('Downloading '+url+' to '+destination_file)
                    #if installer.download_with_resume(url, destination_file, installer._download_background):

                    # Start idolpx Installer
                    kodi.execute('XBMC.RunScript('+addon_id+')', True)
                else:
                    kodi.log("No configuration update is available.")

            except: 
                kodi.log('Error getting version info.')

            # Set wait to 12hrs
            wait = 43200
