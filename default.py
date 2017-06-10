# -*- coding: utf-8 -*-

import re
import sys
import os
import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
from ga import ga
import urllib

__addon_id__= 'plugin.video.kolibka'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id=__addon_id__)
__version__ = __Addon.getAddonInfo('version')
__scriptname__ = __Addon.getAddonInfo('name')
__cwd__ = xbmc.translatePath(__Addon.getAddonInfo('path')).decode('utf-8')
__resource__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode('utf-8')
searchicon = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'search.png')).decode('utf-8')

_UA = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'}

_sorting = {
    '0': 'moviedate',
    '1': 'subsdate',
    '2': 'moviename'
}

prevedeni = __settings__.getSetting("prevedeni")
sorting = __settings__.getSetting("sorting")

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
    if (__settings__.getSetting("viewset") == '' or
        more_info == False):
        return
    xbmc.executebuiltin('Container.SetViewMode(%s)' % __settings__.getSetting("viewset"))

def select_1(lst):
    dialog = xbmcgui.Dialog()
    return dialog.select('Select subtitle', lst)

def CATEGORIES():
    addDir('Търси във Колибка','search',3,searchicon)
    addDir('Вселена','space',1,'http://kolibka.com/images/vselena1.jpg')
    addDir('Технологии','technology',1,'http://kolibka.com/images/techno1.jpg')
    addDir('Енергия','energy',1,'http://kolibka.com/images/energy1.jpg')
    addDir('Конфликти','conflicts',1,'http://kolibka.com/images/war1.jpg')
    addDir('Природа','nature',1,'http://kolibka.com/images/nature2.jpg')
    addDir('Морски свят','sea',1,'http://kolibka.com/images/more1.jpg')
    addDir('Палеонтология','paleontology',1,'http://kolibka.com/images/dino1.jpg')
    addDir('Животни','animals',1,'http://kolibka.com/images/animals1.jpg')
    addDir('Екология','ecology',1,'http://kolibka.com/images/eko1.jpg')
    addDir('Катастрофи','catastrophes',1,'http://kolibka.com/images/katastrofi1.jpg')
    addDir('По света','world',1,'http://kolibka.com/images/posveta1.jpg')
    addDir('Цивилизации','civilizations',1,'http://kolibka.com/images/civil1.jpg')
    addDir('Човек','human',1,'http://kolibka.com/images/chovek1.jpg')
    addDir('Общество','society',1,'http://kolibka.com/images/ob6testvo1.jpg')
    addDir('Личности','biography',1,'http://kolibka.com/images/lichnost1.jpg')
    addDir('Изкуство','art',1,'http://kolibka.com/images/art1.jpg')
    addDir('Духовни учения','spiritual',1,'http://kolibka.com/images/duh1.jpg')
    addDir('Загадки','mysteries',1,'http://kolibka.com/images/zagadka1.jpg')
    addDir('БГ творчество','bg',1,'http://kolibka.com/images/bg1.jpg')

def INDEX(url, page, search=False):
    if search:
      __s = requests.Session()
      r = __s.post('http://kolibka.com/search2.php', headers=_UA, data = {'search':url, 'orderby': _sorting[sorting]})
    else:
      d = {'cat': url,
           'orderby': _sorting[sorting]
           }
      if page:
        d['page'] = page
      if prevedeni == 'true':
        d['showbg'] = 'yes'

      log_my('params', str(d))
      r = requests.get('http://kolibka.com/movies.php', headers=_UA, params=d)

    link=r.text
    thumbnail = 'DefaultVideo.png'

    newpage = re.compile(u'<a\shref="\?.*page=(\d+).*?">\n.*alt="следваща страница"').findall(link)

    for l in get_movs(link):
      addLink(l[1], l[2], 2, l[4], l[5], l[3])

    #If results are on more pages
    if newpage:
        log_my ('Next page is: ' + newpage[0])
        thumbnail='DefaultFolder.png'
        addDir('следваща страница>>',url,1,thumbnail, newpage[0])

def VIDEOLINKS(mid,name):
    #Get Play URL and subtitles
    playurl = 'http://kolibka.com/download.php?mid=' + mid
    suburl = 'http://kolibka.com/download.php?sid=' + mid

    #Stop player if it's running
    xbmc.executebuiltin('PlayerControl(Stop)')
    while xbmc.Player().isPlaying():
      xbmc.sleep(100) #wait until video is played

    #Delete old subs
    files = os.listdir(__cwd__)
    patern = '.*\.(srt|sub|zip|rar|html)$'
    for filename in files:
      if re.match(patern, filename):
        file = os.path.join(__cwd__, filename)
        os.unlink(file)

    try:
      r = requests.get(suburl)
      sname = 'tmp_kolibka.bg'
      ext = r.headers['content-type'].split('/')[1]
      if ext:
        sname = sname + '.%s' % ext
    except:
      r = None
      print "Timed-out exception: " + suburl

    if r:
      # Save new sub to HDD
      SUBS_PATH = xbmc.translatePath(os.path.join(__cwd__, sname))
      file = open(SUBS_PATH, 'wb')
      file.write(r.content)
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
        xbmc.sleep(300) #wait until video is being played
      xbmc.sleep(500)
      xbmc.Player().setSubtitles(os.path.join(__cwd__, ll[snum]))
    else:
      xbmc.Player().showSubtitles(False)
    if more_info:
      update(name, mid)

def SEARCH(url):
    keyb = xbmc.Keyboard('', 'Търсачка на клипове')
    keyb.doModal()
    if (keyb.isConfirmed()):
      addDir(keyb.getText().encode('utf-8'), urllib.quote_plus(keyb.getText().encode('utf-8')), '4', 'DefaultFolderBack.png')
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

def addDir(name,url,mode,iconimage,page=None):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    if page:
      u = u+"&page="+urllib.quote_plus(page)

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
page=None

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
try:
    page=int(params["page"])
except:
    pass

if mode==None or url==None or len(url)<1:
    CATEGORIES()

elif mode==1:
    try:
      INDEX(url, page)
    except:
      update('exception', url, sys.exc_info())
      raise

elif mode==2:
    try:
      VIDEOLINKS(url,name)
    except:
      update('exception', url, sys.exc_info())
      raise

elif mode==3:
    try:
      SEARCH(url)
    except:
      update('exception', url, sys.exc_info())
      raise

elif mode==4:
    try:
      INDEX(url, page, True)
    except:
      update('exception', url, sys.exc_info())
      raise

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
setviewmode()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
