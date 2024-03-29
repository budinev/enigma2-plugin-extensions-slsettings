#!/usr/bin/python
# -*- coding: utf-8 -*-
#--------------------#
#  coded by Lululla  #
#   skin by MMark
#    mod daimon
#     22/02/2022     #
#--------------------#
#Info http://sat-lodge.it
from __future__ import print_function
from . import _
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_PLUGINS
from Tools.Directories import pathExists, fileExists, resolveFilename, copyfile
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getDesktop, loadPNG
from enigma import eListbox, eTimer, eListboxPythonMultiContent, eConsoleAppContainer, gFont
from os import path, listdir, remove, mkdir, access, X_OK, chmod
from os.path import splitext
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import gettext
import os
import re
import sys
import shutil
import ssl
import glob
import six
try:
    from Plugins.Extensions.slSettings.Utils import *
except:
    from . import Utils
from .Lcn import *

global category
global set
set = 0

PY3 = sys.version_info.major >= 3
if PY3:
        import http.client
        from http.client import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
        from urllib.error import URLError, HTTPError
        from urllib.request import urlopen, Request
        from urllib.parse import urlparse
        from urllib.parse import parse_qs, urlencode, quote
        unicode = str; unichr = chr; long = int
        PY3 = True
else:
# if os.path.exists('/usr/lib/python2.7'):
        from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
        from urllib2 import urlopen, Request, URLError, HTTPError
        from urlparse import urlparse, parse_qs
        from urllib import urlencode, quote
        import httplib
        import six

try:
    import zipfile
except:
    pass

if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext=ssl._create_unverified_context()
    except:
        sslContext=None

def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context= sslContext)
    else:
        return urlopen(url)

def make_request(url):
    try:
        import requests
        link = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}).text
        return link
    except ImportError:
        req = Request(url)
        req.add_header('User-Agent', 'TVS')
        response = urlopen(req, None, 7)
        link = response.read().decode('utf-8')
        response.close()
        return link
    except:
        e = URLError
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return
    return

def ReloadBouquets():
    # global set
    print('\n----Reloading bouquets----\n')
    # if set == 1:
        # set = 0
        # terrestrial_rest()
    try:
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        print('bouquets reloaded...')
    except ImportError:
        eDVBDB = None
        os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')
        print('bouquets reloaded...')

def ReloadBouquet():
    global set
    print('\n----Reloading bouquets----')
    if set == 1:
        set = 0
        terrestrial_rest()
    ReloadBouquets()

os.system('rm -fr /usr/lib/enigma2/python/Plugins/Extensions/slSettings/temp/*')# clean /temp
currversion='1.7'
title_plug='..:: SatLodge Settings V. %s ::..' % currversion
name_plug='SatLodge Settings'
category = 'lululla.xml'
plugin_path=os.path.dirname(sys.modules[__name__].__file__)
ico_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/logo.png".format('slSettings'))
res_plugin_path= resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/".format('slSettings'))
skin_path=resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/hd/".format('slSettings'))
if isFHD():
    skin_path=resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/fhd/".format('slSettings'))
if DreamOS():
    skin_path=skin_path + 'dreamOs/'

Panel_Dlist=[
 ('SETTINGS MANUTEK'),
 ('SETTINGS VHANNIBAL'),
 ('UPDATE SATELLITES.XML'),
 ('UPDATE TERRESTRIAL.XML'),
 ]

class OneSetList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        textfont=int(22)
        self.l.setFont(0, gFont('Regular', textfont))        
        if isFHD():
            self.l.setItemHeight(50)
            textfont=int(34)
            self.l.setFont(0, gFont('Regular', textfont))


def DListEntry(name, idx):
    res=[name]
    pngs=resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('slSettings'))
    res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngs)))
    res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color= 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))    
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color= 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

def OneSetListEntry(name):
    res= [name]
    pngx=resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/plugins.png".format('slSettings'))
    res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
    res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color= 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))    
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color= 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res

def showlist(data, list):
    icount= 0
    plist= []
    for line in data:
        name= data[icount]
        plist.append(OneSetListEntry(name))
        icount= icount+1
        list.setList(plist)

class MainSetting(Screen):
    def __init__(self, session):
        self.session= session
        skin= skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin= f.read()
        self.setup_title= ('MainSetting')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self['text']=OneSetList([])
        self['title']=Label(_(title_plug))
        self['info']=Label('')
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Select'))
        self['key_red']=Button(_('Exit'))
        self['key_yellow'] = Button('')
        self['key_yellow'].hide()
        self.LcnOn = False
        if os.path.exists('/etc/enigma2/lcndb'):
          self['key_yellow'].show()
          self['key_yellow'] = Button('Lcn')
          self.LcnOn = True
        self["key_blue"]=Button('')
        self['key_blue'].hide()
        self['actions']=ActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
         'green': self.okRun,
         'back': self.cancel,
         'red': self.cancel,
         'yellow': self.Lcn,
         'cancel': self.cancel}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

    def Lcn(self):
        self.mbox=self.session.open(MessageBox, _('Reorder Terrestrial channels with Lcn rules'), MessageBox.TYPE_INFO, timeout=5)
        lcnstart()

    def cancel(self):
        deletetmp()    
        self.close()

    def updateMenuList(self):
        self.menu_list=[]
        for x in self.menu_list:
            del self.menu_list[0]
        list=[]
        idx=0
        for x in Panel_Dlist:
            list.append(DListEntry(x, idx))
            self.menu_list.append(x)
            idx += 1
        self['text'].setList(list)
        self['info'].setText(_('Please select ...'))

    def okRun(self):
        self.keyNumberGlobalCB(self['text'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel=self.menu_list[idx]
        if sel== ('SETTINGS MANUTEK'):
            self.session.open(SettingManutek)
        elif sel== ('SETTINGS VHANNIBAL'):
            self.session.open(SettingVhan)
        elif sel== _('UPDATE SATELLITES.XML'):
            self.okSATELLITE()
        elif sel== _('UPDATE TERRESTRIAL.XML'):
            self.okTERRESTRIAL()
            
    def okSATELLITE(self):
        self.session.openWithCallback(self.okSatInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okSatInstall(self, result):
        if result:
            if checkInternet():
                try:
                    url_sat_oealliance = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
                    link_sat = ssl_urlopen(url_sat_oealliance)
                    dirCopy = '/etc/tuxbox/satellites.xml'
                    import requests
                    r = requests.get(link_sat)
                    with open(dirCopy,'wb') as f:
                      f.write(r.content)
                    self.session.open(MessageBox, _('Satellites.xml Updated!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation done !!!'))
                except:
                    return
            else:
                session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

    def okTERRESTRIAL(self):
        self.session.openWithCallback(self.okTerrInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okTerrInstall(self, result):
        if result:
            if checkInternet():
                try:
                    url_sat_oealliance = 'https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/terrestrial.xml'
                    link_ter = ssl_urlopen(url_sat_oealliance)
                    dirCopy = '/etc/tuxbox/terrestrial.xml'
                    import requests
                    r = requests.get(link_ter)
                    with open(dirCopy,'wb') as f:
                      f.write(r.content)
                    self.session.open(MessageBox, _('Terrestrial.xml Updated!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation done !!!'))
                except:
                    return
            else:
                self.session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

class SettingVhan(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Vhannibal')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()
        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        self.names=[]
        self.urls=[]
        try:
            urlsat='https://www.vhannibal.net/enigma2.php'
            r=make_request(urlsat)
            print('rrrrrrrr ', r)
            if PY3:
                r  = six.ensure_str(r)
            match   = re.compile('<td><a href="(.+?)" target="_blank">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(r)
            for url, name, date in match:
                name = name + ' ' + date
                url = "https://www.vhannibal.net/" + url
                url = checkStr(url)
                name = checkStr(name)
                print('url : ', url)
                print('name : ', name)
                self.urls.append(url)
                self.names.append(name)
            urldtt = 'https://www.vhannibal.net/enigma2dtt.php'
            r2=make_request(urldtt)
            print('rrrrrrrr ', r2)
            if PY3:
                r2  = six.ensure_str(r2)
            match2   = re.compile('<td><a href="(.+?)" target="_blank">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(r2)
            for url, name, date in match2:
                name = name + ' ' + date
                url = "https://www.vhannibal.net/" + url
                url = checkStr(url)
                name = checkStr(name)
                print('url : ', url)
                print('name : ', name)
                self.urls.append(url)
                self.names.append(name)
            self.downloading = True
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)

                if 'dtt' not in self.name.lower():
                    set = 1
                    terrestrial()
                if os.path.exists(dest):
                    fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        cmd = "rm -rf '/tmp/unzipped'"
                        os.system(cmd)
                    os.makedirs('/tmp/unzipped')
                    cmd2 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
                    os.system(cmd2)
                    for root, dirs, files in os.walk(fdest1):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &; sleep 3"], closeOnSuccess =False)
                    self['info'].setText(_('Settings Installed ...'))
                else:
                    self['info'].setText(_('Settings Not Installed ...'))
            else:
                self['info'].setText(_('No Downloading ...'))

    def yes(self):
        ReloadBouquet()

class SettingMilenka6121(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Milenka61')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()
        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://178.63.156.75/tarGz/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            regex   = '<a href="Satvenus(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match   = re.compile(regex).findall(r)
            for url, date1, date2, date3 in match:
                if url.find('.tar.gz') != -1 :
                    name = url.replace('_EX-YU_Lista_za_milenka61_', '')
                    name = name + ' ' + date1 + '-' + date2 + '-' + date3
                    name = name.replace("_", " ").replace(".tar.gz", "")
                    url = "http://178.63.156.75/tarGz/Satvenus" + url
                    url = checkStr(url)
                    name = checkStr(name)
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists('/tmp/settings.tar.gz'):
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["tar -xvf /tmp/settings.tar.gz -C /; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess =False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()

class SettingManutek(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Manutek')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()
        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://www.manutek.it/isetting/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            regex   = 'href=".*?file=(.+?).zip">'
            match   = re.compile(regex).findall(r)
            for url in match:
                # if 'zip' in url.lower():
                name = url
                name = name.replace(".zip", "").replace("%20", " ").replace("NemoxyzRLS_", "").replace("_", " ")
                url = 'http://www.manutek.it/isetting/enigma2/' + url + '.zip'
                url = checkStr(url)
                name = checkStr(name)
                self.urls.append(url)
                self.names.append(name)
                self.downloading = True
                self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists(dest):
                    fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        cmd = "rm -rf '/tmp/unzipped'"
                        os.system(cmd)
                    os.makedirs('/tmp/unzipped')
                    cmd2 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
                    os.system(cmd2)
                    for root, dirs, files in os.walk(fdest1):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &; sleep 3"], closeOnSuccess =False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()

class SettingMorpheus2(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Morpheus')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()
        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = r'http://morpheus883.altervista.org/download/index.php'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            regex   = 'href="/download/.*?file=(.*?)">'
            match   = re.compile(regex).findall(r)
            for url in match:
                if 'zip' in url.lower():
                    self.downloading = True
                    if 'settings' in url.lower():
                        continue
                    name = url
                    name = name.replace(".zip", "").replace("%20", " ").replace("_", " ")
                    name = name.replace("Morph883", "Morpheus883").replace("E2", "")
                    url = "http://morpheus883.altervista.org/settings/" + url
                    url = checkStr(url)
                    name = checkStr(name)
                    self.urls.append(url)
                    self.names.append(name)
                    print("url =", url)
                    print("name =", name)
                    self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        print("self.downloading is =", self.downloading)
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists(dest):
                    fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    # pth = ''
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    cmd = []
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"],closeOnSuccess =False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()

class SettingCiefp(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Ciefp')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = OneSetList([])
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        # self['progress'] = ProgressBar()
        # self["progress"].hide()
        # self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading = False
        self.timer = eTimer()
        if DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'https://github.com/ciefp/ciefpsettings-enigma2-zipped'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            n1 = r.find('Details">', 0)
            n2 = r.find('href="#readme">', n1)
            r = r[n1:n2]
            regex   = 'title="ciefp-E2-(.*?)".*?href="(.*?)"'
            match   = re.compile(regex).findall(r)
            for name, url in match:
                if url.find('.zip') != -1 :
                    if 'ddt' in name.lower():
                        continue
                    if 'Sat' in name.lower():
                        continue
                    name = checkStr(name)
                    url = url.replace('blob', 'raw')
                    url = 'https://github.com' + url
                    url = checkStr(url)
                    print('name ', name)
                    print('url ', url)
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists(dest):
                    fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"] , closeOnSuccess =False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()
        
class SettingPredrag(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Predrag')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()
        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://178.63.156.75/paneladdons/Predr@g/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            regex   = '<a href="predrag(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match   = re.compile(regex).findall(r)
            for url, date1, date2, date3 in match:
                if url.find('.tar.gz') != -1 :
                    name = url
                    name = name.replace('-settings-e2-','Predrag ')
                    name = name + date1 + '-' + date2 + '-' + date3
                    name = name.replace(".tar.gz", " ")
                    url = "http://178.63.156.75/paneladdons/Predr@g/predrag" + url
                    url = checkStr(url)
                    name = checkStr(name)
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists('/tmp/settings.tar.gz'):
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["tar -xvf /tmp/settings.tar.gz -C /; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess =False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()

class CirusSetting(Screen):
    def __init__(self, session):
        self.session=session
        skin=skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin=f.read()
        self.setup_title=('Setting Cyrus')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list=[]
        self['text']=OneSetList([])
        self.icount=0
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green']=Button(_('Install'))
        self['key_red']=Button(_('Back'))
        self['key_yellow']=Button(_(''))
        self["key_blue"]=Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.downloading=False
        self.timer=eTimer()

        if DreamOS():
            self.timer_conn=self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title']=Label(_(title_plug))
        self['actions']=ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://www.cyrussettings.com/Set_29_11_2011/Dreambox-IpBox/Config.xml'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names  = []
        self.urls   = []
        try:
            n1 = r.find('name="Sat">', 0)
            n2 = r.find("/ruleset>", n1)
            r = r[n1:n2]
            regex   = 'Name="(.*?)".*?Link="(.*?)".*?Date="(.*?)"><'
            match   = re.compile(regex).findall(r)
            for name, url, date in match:
                if url.find('.zip') != -1 :
                    if 'ddt' in name.lower():
                        continue
                    if 'Sat' in name.lower():
                        continue
                    name = name + ' ' + date
                    name = checkStr(name)
                    url = checkStr(url)
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))                                                                   

    def okRun(self):
        self.session.openWithCallback(self.okInstall, MessageBox,(_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                        set = 1
                        terrestrial()
                import requests
                r = requests.get(url)
                with open(dest,'wb') as f:
                  f.write(r.content)
                if os.path.exists(dest):
                    fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, slConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"] , closeOnSuccess =False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()

class slConsole(Screen):
    def __init__(self, session, title ="Console", cmdlist =None, finishedCallback =None, closeOnSuccess =False, endstr =''):
        self.session = session
        skin = skin_path + 'slConsole.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Console')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.endstr = endstr
        self.errorOcurred = False
        self['title'] = Label(_(title_plug))
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.cancel,
         'back': self.cancel,
         'red': self.cancel,
         "blue": self.restartenigma,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.newtitle = _(title_plug)
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run=0
        try:
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['text'].setText(_('Execution Progress:') + '\n\n')
        print('Console: executing in run', self.run, ' the command:', self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            self.show()
            self.finished = True
            str= self["text"].getText()
            if not retval and self.endstr.startswith("Swapping"):
               str += _("\n\n" + self.endstr)
            else:
               str += _("Execution finished!!\n")
            self["text"].setText(str)
            self["text"].lastPage()
            # if self.finishedCallback != None:
                    # self.finishedCallback(retval)
            # if not retval and self.closeOnSuccess:
            self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            try:
                self.appClosed_conn = None
                self.dataAvail_conn = None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)

    def cancelCallback(self, ret = None):
        self.cancel_msg = None
        if ret:
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
            self.container.kill()
            self.close()
        return

    def dataAvail(self, data):
        if PY3:
            data = data.decode("utf-8")
        try:
            self["text"].setText(self["text"].getText() + data)
        except:
            trace_error()
        return
        if self["text"].getText().endswith("Do you want to continue? [Y/n] "):
            msg= self.session.openWithCallback(self.processAnswer, MessageBox, _("Additional packages must be installed. Do you want to continue?"), MessageBox.TYPE_YESNO)

    def processAnswer(self, retval):
        if retval:
            self.container.write("Y",1)
        else:
            self.container.write("n",1)
        self.dataSent_conn = self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)

    def closeConsole(self):
        if self.finished:
            try:
                self.container.appClosed.append(self.runFinished)
                self.container.dataAvail.append(self.dataAvail)
            except:
                self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
                self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
                self.close()
            else:
                self.show()

def main(session, **kwargs):
    try:
        from Plugins.Extensions.slSettings.Utils import checkInternet
    except:
        from . import Utils
    checkInternet()
    if checkInternet():
        try:
            from Plugins.Extensions.slSettings.Update import upd_done
            upd_done()
        except:
            pass
    session.open(MainSetting)


def StartSetup(menuid):
    if menuid== 'scan':
        return [('SatLodge Settings',
          main,
          'SatLodge Settings',
          None)]
    else:
        return []

def Plugins(**kwargs):
    ico_path='logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        ico_path=plugin_path + '/res/pics/logo.png'
    return [PluginDescriptor(name=name_plug, description=_(title_plug), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=ico_path, fnc=main),
     PluginDescriptor(name=_(name_plug), description=_(title_plug), where=PluginDescriptor.WHERE_MENU, fnc=StartSetup),
     PluginDescriptor(name=name_plug, description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]

def terrestrial():
    SavingProcessTerrestrialChannels=StartSavingTerrestrialChannels()
    import time
    now=time.time()
    ttime=time.localtime(now)
    tt=str('{0:02d}'.format(ttime[2])) + str('{0:02d}'.format(ttime[1])) + str(ttime[0])[2:] + '_' + str('{0:02d}'.format(ttime[3])) + str('{0:02d}'.format(ttime[4])) + str('{0:02d}'.format(ttime[5]))
    os.system('tar -czvf /tmp/' + tt + '_enigma2settingsbackup.tar.gz' + ' -C / /etc/enigma2/*.tv /etc/enigma2/*.radio /etc/enigma2/lamedb')
    if SavingProcessTerrestrialChannels:
        print('ok')
    return

def terrestrial_rest():
    if LamedbRestore():
        TransferBouquetTerrestrialFinal()
        icount=0
        terrr=plugin_path + '/temp/TerrestrialChannelListArchive'
        if os.path.exists(terrr):
                os.system("cp -rf " + plugin_path + "/temp/TerrestrialChannelListArchive /etc/enigma2/userbouquet.terrestrial.tv")
        os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
        with open('/etc/enigma2/bouquets.tv', 'r+') as f:
            bouquetTvString='#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.terrestrial.tv" ORDER BY bouquet\n'
            if bouquetTvString not in f:
                new_bouquet=open('/etc/enigma2/new_bouquets.tv', 'w')
                new_bouquet.write('#NAME User - bouquets (TV)\n')
                new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.terrestrial.tv" ORDER BY bouquet\n')
                file_read=open('/etc/enigma2/bouquets.tv').readlines()
                for line in file_read:
                    if line.startswith("#NAME"):
                        continue
                    new_bouquet.write(line)
                new_bouquet.close()
                os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                os.system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
        if os.path.exists('/etc/enigma2/lcndb'):
            lcnstart()

def lcnstart():
    print(' lcnstart ')
    if os.path.exists('/etc/enigma2/lcndb'):
        lcn=LCN()
        lcn.read()
        if len(lcn.lcnlist) > 0:
            lcn.writeBouquet()
            # lcn.reloadBouquets()
            ReloadBouquets()
    return

def StartSavingTerrestrialChannels():
    def ForceSearchBouquetTerrestrial():
        for file in sorted(glob.glob("/etc/enigma2/*.tv")):
            if 'SatLodge' in file:
                continue
            f=open(file, "r").read()
            x=f.strip().lower()
            if x.find('http'):
                continue
            if x.find('eeee0000')!= -1:
                if x.find('82000')== -1 and x.find('c0000')== -1:
                    return file
                    break
        # return

    def ResearchBouquetTerrestrial(search):
        for file in sorted(glob.glob("/etc/enigma2/*.tv")):
            if 'SatLodge' in file:
                continue
            f=open(file, "r").read()
            x=f.strip().lower()
            x1=f.strip()
            if x1.find("#NAME") != -1:
                if x.lower().find((search.lower())) != -1:
                    if x.find('http'):
                        continue
                    if x.find('eeee0000')!= -1:
                        return file
                        break
        # return

    def SaveTrasponderService():
        TrasponderListOldLamedb=open(plugin_path +'/temp/TrasponderListOldLamedb', 'w')
        ServiceListOldLamedb=open(plugin_path +'/temp/ServiceListOldLamedb', 'w')
        Trasponder=False
        inTransponder=False
        inService=False
        try:
          LamedbFile=open('/etc/enigma2/lamedb')
          while 1:
            line=LamedbFile.readline()
            if not line: break
            if not (inTransponder or inService):
              if line.find('transponders')== 0:
                inTransponder=True
              if line.find('services')== 0:
                inService=True
            if line.find('end')== 0:
              inTransponder=False
              inService=False
            line=line.lower()
            if line.find('eeee0000') != -1:
              Trasponder=True
              if inTransponder:
                TrasponderListOldLamedb.write(line)
                line=LamedbFile.readline()
                TrasponderListOldLamedb.write(line)
                line=LamedbFile.readline()
                TrasponderListOldLamedb.write(line)
              if inService:
                tmp=line.split(':')
                ServiceListOldLamedb.write(tmp[0] +":"+tmp[1]+":"+tmp[2]+":"+tmp[3]+":"+tmp[4]+":0\n")
                line=LamedbFile.readline()
                ServiceListOldLamedb.write(line)
                line=LamedbFile.readline()
                ServiceListOldLamedb.write(line)
          TrasponderListOldLamedb.close()
          ServiceListOldLamedb.close()
          if not Trasponder:
            os.system('rm -fr ' + plugin_path + '/temp/TrasponderListOldLamedb')
            os.system('rm -fr ' + plugin_path + '/temp/ServiceListOldLamedb')
        except:
            pass
        return Trasponder

    def CreateBouquetForce():
        WritingBouquetTemporary=open(plugin_path +'/temp/TerrestrialChannelListArchive','w')
        WritingBouquetTemporary.write('#NAME Terrestre\n')
        ReadingTempServicelist=open(plugin_path +'/temp/ServiceListOldLamedb').readlines()
        for jx in ReadingTempServicelist:
          if jx.find('eeee') != -1:
             String=jx.split(':')
             WritingBouquetTemporary.write('#SERVICE 1:0:%s:%s:%s:%s:%s:0:0:0:\n'% (hex(int(String[4]))[2:],String[0],String[2],String[3],String[1]))
        WritingBouquetTemporary.close()

    def SaveBouquetTerrestrial():
        NameDirectory=ResearchBouquetTerrestrial('terr')
        if not NameDirectory:
          NameDirectory=ForceSearchBouquetTerrestrial()
        try:
          shutil.copyfile(NameDirectory,plugin_path +'/temp/TerrestrialChannelListArchive')
          return True
        except :
          pass
        # return

    Service=SaveTrasponderService()
    if Service:
      if not SaveBouquetTerrestrial():
        CreateBouquetForce()
      return True
    # return

def LamedbRestore():
    try:
      TrasponderListNewLamedb=open(plugin_path +'/temp/TrasponderListNewLamedb', 'w')
      ServiceListNewLamedb=open(plugin_path +'/temp/ServiceListNewLamedb', 'w')
      inTransponder=False
      inService=False
      infile=open("/etc/enigma2/lamedb")
      while 1:
        line=infile.readline()
        if not line: break
        if not (inTransponder or inService):
          if line.find('transponders')== 0:
            inTransponder=True
          if line.find('services')== 0:
            inService=True
        if line.find('end')== 0:
          inTransponder=False
          inService=False
        if inTransponder:
          TrasponderListNewLamedb.write(line)
        if inService:
          ServiceListNewLamedb.write(line)
      TrasponderListNewLamedb.close()
      ServiceListNewLamedb.close()
      WritingLamedbFinal=open("/etc/enigma2/lamedb", "w")
      WritingLamedbFinal.write("eDVB services /4/\n")
      TrasponderListNewLamedb=open(plugin_path +'/temp/TrasponderListNewLamedb').readlines()
      for x in TrasponderListNewLamedb:
        WritingLamedbFinal.write(x)
      try:
        TrasponderListOldLamedb=open(plugin_path +'/temp/TrasponderListOldLamedb').readlines()
        for x in TrasponderListOldLamedb:
          WritingLamedbFinal.write(x)
      except:
        pass
      WritingLamedbFinal.write("end\n")
      ServiceListNewLamedb=open(plugin_path +'/temp/ServiceListNewLamedb').readlines()
      for x in ServiceListNewLamedb:
        WritingLamedbFinal.write(x)
      try:
        ServiceListOldLamedb=open(plugin_path +'/temp/ServiceListOldLamedb').readlines()
        for x in ServiceListOldLamedb:
          WritingLamedbFinal.write(x)
      except:
        pass
      WritingLamedbFinal.write("end\n")
      WritingLamedbFinal.close()
      return True
    except:
      return False

def TransferBouquetTerrestrialFinal():
        def RestoreTerrestrial():
          for file in os.listdir("/etc/enigma2/"):
            if re.search('^userbouquet.*.tv', file):
              f=open("/etc/enigma2/" + file, "r")
              x=f.read()
              if re.search("#NAME Digitale Terrestre",x, flags=re.IGNORECASE):
                return "/etc/enigma2/"+file
        try:
          TerrestrialChannelListArchive=open(plugin_path +'/temp/TerrestrialChannelListArchive').readlines()
          DirectoryUserBouquetTerrestrial=RestoreTerrestrial()
          if DirectoryUserBouquetTerrestrial:
            TrasfBouq=open(DirectoryUserBouquetTerrestrial,'w')
            for Line in TerrestrialChannelListArchive:
              if Line.lower().find('#name') != -1 :
                TrasfBouq.write('#NAME Digitale Terrestre\n')
              else:
                TrasfBouq.write(Line)
            TrasfBouq.close()
            return True
        except:
          return False
#======================================================
