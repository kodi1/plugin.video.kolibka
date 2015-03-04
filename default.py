# -*- coding: utf-8 -*-
import re
import sys
import os
import urllib
import urllib2
import time
import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs


__addon_id__= 'plugin.video.kolibka'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.kolibka')

prevedeni = __settings__.getSetting("prevedeni")
sorting = __settings__.getSetting("sorting")

searchicon = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/search.png")
SUBS_PATH = xbmc.translatePath(__Addon.getAddonInfo('path') + "/kolibkasub.rar")
ADDON_PATH = xbmc.translatePath(__Addon.getAddonInfo('path'))

UA = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'

parameters=''
if prevedeni=='true':
    parameters = parameters + '&showbg=yes'
if sorting==0:
    parameters = parameters + '&orderby=moviedate'
if sorting==1:
    parameters = parameters + '&orderby=subsdate'
if sorting==2:
    parameters = parameters + '&orderby=moviename'




def CATEGORIES():


    addDir('Търси във Колибка','http://kolibka.com/search.php?orderby=subsdate&q=',3,searchicon)
    addDir('Вселена','http://kolibka.com/movies.php?cat=space',1,'http://kolibka.com/images/vselena1.jpg')
    addDir('Технологии','http://kolibka.com/movies.php?cat=technology',1,'http://kolibka.com/images/techno1.jpg')
    addDir('Енергия','http://kolibka.com/movies.php?cat=energy',1,'http://kolibka.com/images/energy1.jpg')
    addDir('Конфликти','http://kolibka.com/movies.php?cat=conflicts',1,'http://kolibka.com/images/war1.jpg')
    addDir('Природа','http://kolibka.com/movies.php?cat=nature',1,'http://kolibka.com/images/nature2.jpg')
    addDir('Морски свят','http://kolibka.com/movies.php?cat=sea',1,'http://kolibka.com/images/more1.jpg')
    addDir('Палеонтология','http://kolibka.com/movies.php?cat=paleontology',1,'http://kolibka.com/images/dino1.jpg')
    addDir('Животни','http://kolibka.com/movies.php?cat=animals',1,'http://kolibka.com/images/animals1.jpg')
    addDir('Екология','http://kolibka.com/movies.php?cat=ecology',1,'http://kolibka.com/images/eko1.jpg')
    addDir('Катастрофи','http://kolibka.com/movies.php?cat=catastrophes',1,'http://kolibka.com/images/katastrofi1.jpg')
    addDir('По света','http://kolibka.com/movies.php?cat=world',1,'http://kolibka.com/images/posveta1.jpg')
    addDir('Цивилизации','http://kolibka.com/movies.php?cat=civilizations',1,'http://kolibka.com/images/civil1.jpg')
    addDir('Човек','http://kolibka.com/movies.php?cat=human',1,'http://kolibka.com/images/chovek1.jpg')
    addDir('Общество','http://kolibka.com/movies.php?cat=society',1,'http://kolibka.com/images/ob6testvo1.jpg')
    addDir('Личности','http://kolibka.com/movies.php?cat=biography',1,'http://kolibka.com/images/lichnost1.jpg')
    addDir('Изкуство','http://kolibka.com/movies.php?cat=art',1,'http://kolibka.com/images/art1.jpg')
    addDir('Духовни учения','http://kolibka.com/movies.php?cat=spiritual',1,'http://kolibka.com/images/duh1.jpg')
    addDir('Загадки','http://kolibka.com/movies.php?cat=mysteries',1,'http://kolibka.com/images/zagadka1.jpg')
    addDir('БГ творчество','http://kolibka.com/movies.php?cat=bg',1,'http://kolibka.com/images/bg1.jpg')



def INDEX(url):
    url = url + parameters
    req = urllib2.Request(url)
    req.add_header('User-Agent', UA)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    #print link

    newpage=re.compile('page=(.+?)&amp;orderby=movie&amp;.*\n.*alt="следваща страница"').findall(link)

    #Nachalo na obhojdaneto
    
    matcht = re.compile('<table((.|[\r\n])+?)</table').findall(link)
    for table in matcht:
        titl = str(table)

        matchp = re.compile('<img src=.*thumbs/(.+?)" alt=').findall(titl)
        for thumb in matchp:
            thumbnail = 'http://kolibka.com/thumbs/' + thumb

        match = re.compile('mid=(.+?)" title="(.+?)">(.+?)<').findall(titl)
        for mid,title2,title1 in match:
            title1 = urllib.unquote_plus(title1).decode('utf-8', errors='ignore').encode('utf-8', errors='ignore')
            #print 'title1:' + title1
            title2 = urllib.unquote_plus(title2).decode('cp1251', errors='ignore').encode('utf-8', errors='ignore')
            title2 = title2[:-4]
            title2 = title2.replace('.', ' ')
            title2 = title2.replace(' www', '')
            title2 = title2.replace(' valio', '')
            title2 = title2.replace(' kolibka', '')
            title2 = title2.replace(' com', '')
            title2 = title2.replace('DVDRip', '')
            title2 = title2.replace('DVDvRip', '')
            title2 = title2.replace('TVRip', '')
            title2 = title2.replace('PDTV', '')
            title2 = title2.replace('Divx', '')
            title2 = title2.replace('XviD', '')
            title2 = title2.replace('x264', '')
            title2 = title2.replace('AC3', '')
            title2 = title2.replace('  ', ' ')
            #print 'title2:' + title2
            title=title1 + ' :: ' + title2
            #print title
            addLink(title,mid,2,thumbnail)
    #Kray na obhojdaneto

    #If results are on more pages
    if newpage <> []:
        if 'http://kolibka.com/movies.php' in url:
            lisearch = re.compile('(.+?)&page=.*').findall(url)
            for exactmatch in lisearch:
                url = exactmatch
        url = url + '&page=' + newpage[0][0]
        print 'URL OF THE NEXT PAGE IS' + url
        thumbnail='DefaultFolder.png'
        addDir('следваща страница>>',url,1,thumbnail)


def VIDEOLINKS(mid,name):
    #Get Play URL and subtitles
    playurl = 'http://kolibka.com/download.php?mid=' + mid
    suburl = 'http://kolibka.com/download.php?sid=' + mid
    print 'playurl:' + playurl
    print 'suburl:' + suburl

    #Delete old subs
    files = os.listdir(ADDON_PATH)
    patern = '.*\.(zip|rar)$'
    for filename in files:
        if re.match(patern, filename):
            file = ADDON_PATH + '/' + filename
            os.unlink(file)
    patern = '.*\.(srt|sub)$'
    for filename in files:
        if re.match(patern, filename):
            file = ADDON_PATH + '/' + filename
            os.unlink(file)

    #Save new sub to HDD
    SUBS_PATH = xbmc.translatePath(__Addon.getAddonInfo('path') + "/kolibkasub.rar")
    try:
        urllib.urlretrieve(suburl, SUBS_PATH)
    except:
        print "Timed-out exception: " + suburl
    if os.path.getsize(SUBS_PATH) > 0:
        xbmc.sleep(500)
        xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (SUBS_PATH, ADDON_PATH)).encode('utf-8'), True)
    else:
        os.unlink(SUBS_PATH)

    #Rename subs
    files = os.listdir(ADDON_PATH)
    patern = '.*\.(srt|sub)$'
    for filename in files:
        if re.match(patern, filename):
            file = ADDON_PATH + '/' + filename
            subfile = ADDON_PATH + '/kolibkasub.srt'
            os.rename(file, subfile)
    else:
        if xbmcvfs.exists(SUBS_PATH):
            os.rename(SUBS_PATH, ADDON_PATH + '/kolibkasub.zip')
        SUBS_PATH = ADDON_PATH + '/kolibkasub.zip'
        xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (SUBS_PATH, ADDON_PATH)).encode('utf-8'), True)
        files = os.listdir(ADDON_PATH)
        patern = '.*\.(srt|sub)$'
        for filename in files:
            if re.match(patern, filename):
                file = ADDON_PATH + '/' + filename
                subfile = ADDON_PATH + '/kolibkasub.srt'
                os.rename(file, subfile)


    #Play Selected Item
    li = xbmcgui.ListItem(path=playurl)
    li.setInfo('video', { 'title': name })
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = playurl))
    #Set subtitles if any or disable them
    if os.path.isfile(SUBS_PATH):
        while not xbmc.Player().isPlaying():
            xbmc.sleep(100) #wait until video is being played
            xbmc.Player().setSubtitles(subfile)
    else:
        xbmc.Player().showSubtitles(False)




def SEARCH(url):
    keyb = xbmc.Keyboard('', 'Търсачка на клипове')
    keyb.doModal()
    searchText = ''
    if (keyb.isConfirmed()):
        searchText = urllib.quote_plus(keyb.getText())
        url= url + searchText
        url = url.encode('utf-8')
        print 'SEARCHING:' + url
        INDEX(url.lower())
    else:
        addDir('Върнете се назад в главното меню за да продължите','','',"DefaultFolderBack.png")

def addLink(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty("IsPlayable" , "true")
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok


def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok



def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]

    return param



params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass


if mode==None or url==None or len(url)<1:
    print ""
    CATEGORIES()

elif mode==1:
    print ""+url
    INDEX(url)

elif mode==2:
    print ""+url
    VIDEOLINKS(url,name)

elif mode==3:
    print ""+url
    SEARCH(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
