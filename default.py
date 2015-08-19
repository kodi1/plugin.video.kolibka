# -*- coding: utf-8 -*-

import re
import sys
import os
import urllib
import urllib2
import time
import requests
import HTMLParser
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
from ga import ga

__addon_id__= 'plugin.video.kolibka'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id=__addon_id__)
__version__ = __Addon.getAddonInfo('version')
__scriptname__ = __Addon.getAddonInfo('name')
__cwd__ = xbmc.translatePath(__Addon.getAddonInfo('path')).decode('utf-8')
__resource__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode('utf-8')
searchicon = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'search.png')).decode('utf-8')
UA = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0'

sys.path.insert(0, __resource__)
from helper import get_all_episode as get_movs

if __settings__.getSetting("firstrun") == "true":
  __settings__.openSettings()
  __settings__.setSetting("firstrun", "false")

def log_my(*msg):
  # xbmc.log((u"### !!!-> %s" % (msg,)).encode('utf-8'),level=xbmc.LOGNOTICE)
  xbmc.log((u"### !!!-> %s" % (msg,)).encode('utf-8'), level=xbmc.LOGERROR)

if 'true' == __settings__.getSetting('more_info'):
  more_info = True
  fanart = xbmc.translatePath(os.path.join(__cwd__,'fanart.jpg')).decode('utf-8')
else:
  fanart = None
  more_info = False

def update(name, dat, crash=None):
  payload = {}
  payload['an'] = __scriptname__
  payload['av'] = __version__
  payload['ec'] = name
  payload['ea'] = 'movie_start'
  payload['ev'] = '1'
  payload['dl'] = urllib.quote_plus(dat.encode('utf-8'))
  ga().update(payload, crash)

def setviewmode():
    if (xbmc.getSkinDir() != "skin.confluence" or
        __settings__.getSetting("viewset") != 'true' or
        more_info == False):
        return
    mode = {
              '0': '52',
              '1': '502',
              '2': '51',
              '3': '500',
              '4': '501',
              '5': '508',
              '6': '504',
              '7': '503',
              '8': '515'
            }
    xbmc.executebuiltin('Container.SetViewMode(%s)' % mode[__settings__.getSetting("viewmode")])

def select_1(lst):
    dialog = xbmcgui.Dialog()
    return dialog.select('Select subtitle', lst)

prevedeni = __settings__.getSetting("prevedeni")
sorting = __settings__.getSetting("sorting")

parameters = ''
if prevedeni == 'true':
  parameters = parameters + '&showbg=yes'
if sorting == '0':
  parameters = parameters + '&orderby=moviedate'
if sorting == '1':
  parameters = parameters + '&orderby=subsdate'
if sorting == '2':
  parameters = parameters + '&orderby=moviename'

def CATEGORIES():
    addDir('Търси във Колибка','http://kolibka.com/search.php?q=',3,searchicon)
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
    thumbnail = 'DefaultVideo.png'
    #print link

    newpage = re.compile(r'<a\shref="(\?.*?)">\n.*alt="следваща страница"').findall(link)

    if False == more_info:
      #Nachalo na obhojdaneto
      pars = HTMLParser.HTMLParser()
      matcht = re.compile('<table((.|[\r\n])+?)</table').findall(link)
      for table in matcht:
        titl = str(table)

        thumbnail='DefaultVideo.png'
        matchp = re.compile('<img src=.*thumbs/(.+?)" alt="(.+?)"').findall(titl)
        for thumb,title1 in matchp:
          thumbnail = 'http://kolibka.com/thumbs/' + thumb
          #title1=urllib.unquote_plus(title1).decode('unicode_escape', errors='ignore').encode('ascii', errors='ignore')
          title1=pars.unescape(title1).decode('unicode_escape').encode('ascii', 'ignore')
          title1=title1.replace('  ',' ')
          title1=title1.replace('/   ','')
          title1=title1.replace('/  ','')
          title1=title1.replace(' / ','')
          title1=title1.replace('a ( )','')
          title1=title1.replace(' ( )','')
          title1=title1.replace('-  ','- ')
          title1=title1.replace('  ',' ')
          title1=title1.replace('&quot;','"')
          #print title1

        match = re.compile('mid=(.+?)" title="(.+?)">(.+?)<').findall(titl)
        for mid,t,title2 in match:
          #title2=urllib.unquote_plus(title2).decode('unicode_escape', errors='ignore').encode('ascii', errors='ignore')
          title2=pars.unescape(title2).decode('unicode_escape').encode('ascii', 'ignore')
          title2=title2.replace('&quot;','"')
          title=title1+ ' :: '+title2
          #print title
          addLink(title,mid,2,thumbnail)
      #Kray na obhojdaneto
    else:
      for l in get_movs(link):
        addLink(l[1], l[2], 2, l[4], l[5], l[3])

    #If results are on more pages
    if newpage:
      if 'http://kolibka.com/movies.php' in url:
        url = re.sub(r'\?.*$', '', url)
        url = url + re.sub(r'\&amp;', '&', newpage[0])
        print 'URL OF THE NEXT PAGE IS: ' + url
        thumbnail='DefaultFolder.png'
        addDir('следваща страница>>',url,1,thumbnail)

def VIDEOLINKS(mid,name):
    #Get Play URL and subtitles
    playurl = 'http://kolibka.com/download.php?mid=' + mid
    suburl = 'http://kolibka.com/download.php?sid=' + mid
    print 'playurl:' + playurl
    print 'suburl:' + suburl

    #Stop player if it's running
    xbmc.executebuiltin('PlayerControl(Stop)')
    while xbmc.Player().isPlaying():
      xbmc.sleep(100) #wait until video is played

    #Delete old subs
    files = os.listdir(__cwd__)
    patern = '.*\.(zip|rar)$'
    for filename in files:
      if re.match(patern, filename):
        file = os.path.join(__cwd__, filename)
        os.unlink(file)
    patern = '.*\.(srt|sub)$'
    for filename in files:
      if re.match(patern, filename):
        file = os.path.join(__cwd__, filename)
        os.unlink(file)

    try:
      response = urllib2.urlopen(suburl)
    except:
      print "Timed-out exception: " + suburl

    # Save new sub to HDD
    SUBS_PATH = xbmc.translatePath(os.path.join(__cwd__, 'tmp_kolibka.bg.') + response.info()['Content-Type'].split('/')[1])
    file = open(SUBS_PATH, 'wb')
    file.write(response.read())
    file.close()

    if os.path.getsize(SUBS_PATH) > 0:
      xbmc.sleep(500)
      xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (SUBS_PATH, __cwd__)).encode('utf-8'), True)
    else:
      os.unlink(SUBS_PATH)

    #Rename subs
    ll = []
    files = os.listdir(__cwd__)
    patern = '.*\.(srt|sub)$'
    for filename in files:
      if re.match(patern, filename):
        ll.append(filename)

    snum = 0
    if len(ll) > 1:
      snum = select_1(ll)

    #Play Selected Item
    li = xbmcgui.ListItem(path=playurl)
    li.setInfo('video', { 'title': name })
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = playurl))
    #Set subtitles if any or disable them
    if len(ll) > 0:
      while not xbmc.Player().isPlaying():
        xbmc.sleep(100) #wait until video is being played
      xbmc.sleep(50)
      xbmc.Player().setSubtitles(os.path.join(__cwd__, ll[snum]))
    else:
      xbmc.Player().showSubtitles(False)
    if more_info:
      update(name, mid)

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

def addLink(name, url, mode, iconimage, desc = '', lang = None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name })

    if lang:
      for t, arg in lang.items():
        for k, v in arg.items():
          if v:
            # print "Set %s -> %s = %s" % (t, k , v)
            desc = "[COLOR 7700FF00]%s: %s[/COLOR] " % (t, v) + desc

    liz.setInfo(type="Video", infoLabels={ "plot": desc })
    liz.setProperty('fanart_image', iconimage)
    liz.setProperty("IsPlayable" , "true")

    # liz.addStreamInfo('video', { 'codec': 'h264', 'aspect': 1.78, 'width': 1280, 'height': 720, 'duration': 60 })
    # liz.addStreamInfo('audio', { 'codec': 'dts', 'language': 'en', 'channels': 2 })
    # liz.addStreamInfo('subtitle', { 'language': 'en' })
    # for t, arg in lang.items():
     # for k, v in arg.items():
       # if v is not None:
         # liz.addStreamInfo(t, arg)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    return ok

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    if fanart is not None:
      liz.setProperty('fanart_image', fanart)

    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

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
    try:
      INDEX(url)
    except:
      update('exception', url, sys.exc_info())
      raise

elif mode==2:
    print ""+url
    try:
      VIDEOLINKS(url,name)
    except:
      update('exception', url, sys.exc_info())
      raise

elif mode==3:
    print ""+url
    SEARCH(url)

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
setviewmode()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
