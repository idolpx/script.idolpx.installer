# script.idolpx.installer
Private Kodi build installer/updater<br>

The main functionality is working.  There are some features that still need to be completed.<br>

## Kodi Addon Setup

1. Edit the "update_url" setting in "resources/settings.xml" to match your domain that you upload the server scripts to
2. Zip addon (Make sure the top level folder "script.idolpx.installer" is in the zip and the addon files are inside it.)
3. Install addon in Kodi with "Install from zip file" option
4. Configure all of your other addons the way you want them
5. Go to the "idolpx Installer" settings (Advanced) then select "Backup Current Configuration"
6. When the backup is complete, the archive will be in your Kodi data folder witha matching '.md5' file
7. Upload the zip file to the "kodi" folder on your server
8. Edit the "version.php" file in the "kodi" folder on your server to match the archive name and set the "_md5" value that is contained in the matching ".md5" file
<br>
You can have a current config and a test config on the server.  If the "Select Test Configuration" option is set in the addon then it will use the test config specified in the "version.php" file.  That way you can check everything out before promoting it to the current config. 

## Web App Requirements

Apache/Nginx/IIS webserver with PHP<br>
composer  - https://getcomposer.org/

## Web App Installation

1. Upload the contents of the "server" folder to a folder named "kodi" on your web server
2. Change directory into the "kodi/auth" folder and issue the following command

```
composer install
```

3. Set owner to the user that your web service runs as
4. Make the "data" and "logs" folders writable by the webserver
5. Change directory into the "includes" folder and edit the settings in "config.php"
6. Use basic authentication to restrict access to the "kodi/auth" folder

## Usage

Browse to  http://youdomain.com/kodi/auth to get to the main user interface.
