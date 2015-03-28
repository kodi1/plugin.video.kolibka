#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import os
from bs4 import BeautifulSoup
import time

audio_l = {
        'bg': ['българскиезик'],
        'ru': ['рускоаудио', 'рускиезик'],
        'fr': ['френскиезик'],
        'de': ['немскиезик'],
        }
subs_l = {
        'en': ['англ.суб', 'английскисуб'],
        'ru': ['рускисуб'],
        'bg': ['българскисуб', 'субтитринабългарски'],
        'nl': ['холандскисуб'],
        }

def clean_info(dat):
  dat = re.sub(r"(<\/?div.*?>|<br.\/>|<\/?b>|<\/?a.*?>)", " ", dat)
  return re.sub("  ", " ", dat)

def get_lang_data(d):
  lan_info = {
    'audio':{'language': None},
    'subtitle':{'language': None},
  }

  if d.a:
    #episode subs found
    txt = re.sub(r'\s+', '', d.a.get_text().encode('utf-8', 'replace'))
    lan_info['subtitle']['language'] = 'bg'
  else:
    txt = re.sub(r'\s+', '', d.get_text().encode('utf-8', 'replace'))

  for l, auds in audio_l.items():
    if any(a in txt for a in auds):
      lan_info['audio']['language'] = l

  for l, ss in subs_l.items():
    if any(s in txt for s in ss):
      lan_info['subtitle']['language'] = l

  return lan_info

def get_e_info(e):
  for ss in e.find_parent('tr').find_previous_siblings('tr'):
    desc = ''
    if not ss.attrs:
      if ss.td.a:
        desc = clean_info(ss.td.a.get('onclick').encode('utf-8', 'replace').split("overlib('")[1].split("', CAPTION")[0])
      title = ss.td.img.get('alt').encode('utf-8', 'replace')
      thumbnail = ss.td.img.get('src').encode('utf-8', 'replace')
  return title, desc, thumbnail

def get_episode(t):
  #find all movie episode links
  movs = t.findAll('a', href=re.compile(r'(?:download.php\?mid=\d+)'))
  #find movie info
  name, d, thumb = get_e_info(movs[0])
  subs = movs[0].find_parent('td').find_next_sibling('td').findAll('font', face=re.compile(r'(times new roman)'))
  for m in movs:
    i = movs.index(m)
    #get episode name
    _name = m.get_text().encode('utf-8', 'replace').strip() + '::' + name
    # return all episode data
    yield i, _name, m['href'].split('=')[1], get_lang_data(subs[i]), thumb, d

def get_all_episode(link):
  s = BeautifulSoup(link, 'html5lib')
  l = s('table')
  #skip first and last tables
  for ll in l[1:-1]:
    for r in get_episode(ll):
      yield r

def get_data(link):
  for r in get_all_episode(link):
    print r[1], r[4]

if __name__ == "__main__":
  os.system('cls')
  f = open(sys.argv[1],'r')
  lll = f.read()
  start = time.time()
  get_data(lll)
  mid = time.time()
  old_get_data(lll)
  end = time.time()
  print "Time - new: %s old: %s" % (mid - start, end - mid)
  f.close()
