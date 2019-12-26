import xbmc, xbmcgui
import os, shutil
import kodi

thumbnailPath = xbmc.translatePath('special://thumbnails');
cachePath = xbmc.translatePath('special://home/cache')
databasePath = xbmc.translatePath('special://database')
tempPath = xbmc.translatePath('special://temp')

#class cacheEntry:
#    def __init__(self, namei, pathi):
#        self.name = namei
#        self.path = pathi
#
#def setupCacheEntries():
#    entries = 5 #make sure this refelcts the amount of entries you have
#    dialogName = ["WTF", "4oD", "BBC iPlayer", "Simple Downloader", "ITV"]
#    pathName = ["special://profile/addon_data/plugin.video.whatthefurk/cache", "special://profile/addon_data/plugin.video.4od/cache",
#				 "special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache","special://profile/addon_data/script.module.simple.downloader",
#                "special://profile/addon_data/plugin.video.itv/Images"]
#
#    cacheEntries = []
#    
#    for x in range(entries):
#        cacheEntries.append(cacheEntry(dialogName[x],pathName[x]))
#    
#    return cacheEntries


def clearCache(mode='verbose'):

    if os.path.exists(cachePath)==True:    
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        if (f == "kodi.log" or f == "kodi.old.log"): continue
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass
            else:
                pass
                
    if os.path.exists(tempPath)==True:    
        for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        if (f == "kodi.log" or f == "kodi.old.log"): continue
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass
            else:
                pass
                
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                pass
                
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                pass    
                
#    cacheEntries = []
#    for entry in cacheEntries:
#        clear_cache_path = xbmc.translatePath(entry.path)
#        if os.path.exists(clear_cache_path)==True:    
#            for root, dirs, files in os.walk(clear_cache_path):
#                file_count = 0
#                file_count += len(files)
#                if file_count > 0:
#                        for f in files:
#                            os.unlink(os.path.join(root, f))
#                        for d in dirs:
#                            shutil.rmtree(os.path.join(root, d))
#                else:
#                    pass
                
    if mode == 'verbose': 
        kodi.notify('Maintenance' , 'Clean Completed')    
    
def deleteThumbnails(mode='verbose'):

    if os.path.exists(thumbnailPath):
		try:	
			for root, dirs, files in os.walk(thumbnailPath):
				file_count = 0
				file_count += len(files)
				# Count files and give option to delete
				if file_count > 0:
						for f in files:	os.unlink(os.path.join(root, f))
						for d in dirs: shutil.rmtree(os.path.join(root, d))
		except:
			pass
			
    try:
		text13 = os.path.join(databasePath,"Textures13.db")
		os.unlink(text13)
    except:
		pass
        
    if mode == 'verbose': 
        kodi.notify('Maintenance' , 'Clean Thumbs Completed')  
     
def purgePackages(mode='verbose'):

    purgePath = xbmc.translatePath('special://home/addons/packages')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(purgePath):
        file_count = 0
        file_count += len(files)
        if file_count > 0:            
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
                
    if mode == 'verbose': 
        kodi.notify('Maintenance' , 'Clean Packages Completed')    
    
        
def purgeHome(mode='verbose'):

    exclusions = ['addons', 'media', 'system', 'userdata', 'temp', 'kodi.']

    purgePath = xbmc.translatePath('special://home')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(purgePath):
        file_count = 0
        file_count += len(files)
        if file_count > 0:            
            for f in files:
                if not any(e in f for e in exclusions):
                    os.unlink(os.path.join(root, f))
                else:
                    kodi.debug("purgeHome Excluding '%s'." % f)
            for d in dirs:
                if not any(e in d for e in exclusions):
                    shutil.rmtree(os.path.join(root, d))
                else:
                    kodi.debug("purgeHome Excluding '%s'." % d)
        break
                
    if mode == 'verbose':
        kodi.notify('Maintenance' , 'Clean Packages Completed') 




