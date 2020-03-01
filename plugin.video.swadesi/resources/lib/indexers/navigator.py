# -*- coding: utf-8 -*-

'''
    Swadesi Add-on
    Copyright (C) 2017 Aftershockpy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import urlparse

from aftershock.common import control, logger, views, analytics, cache, changelog

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])

artPath = control.artPath() ; addonFanart = control.addonFanart()

try: action = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))['action']
except: action = None

imdbMode = False if control.setting('imdb_user') == '' else True

class navigator:
    def __init__(self):
        self.index_provider = control.setting('idx_provider')

    def root(self):

        self.addDirectoryItem(30860, 'movieLangNavigator', 'movies.png','DefaultMovies.png')
        self.addDirectoryItem(30861, 'desiTVNavigator', 'tv-vod.png','DefaultMovies.png')

        self.addDirectoryItem(90116, 'tools', 'settings.png', 'DefaultMovies.png')
        self.addDirectoryItem(90117, 'clearCache', 'clearcache.png', 'DefaultMovies.png')
        #self.addDirectoryItem(30864, 'changelog', 'changelog.png', 'DefaultMovies.png')

        #cache.get(changelog.get, 600000000, control.addonInfo('version'), table='changelog')
        #cache.get(self.donation, 336, control.addonInfo('version'), table='changelog')
        #cache.get(control.resetSettings, 600000000, 'true', control.addonInfo('version'), table='changelog')
        #cache.get(analytics.sendAnalytics, 600000000, ("Installed-%s" % control.addonInfo('version')), table='changelog')

        self.endDirectory()

    def tools(self):
        self.addDirectoryItem('[B]URL Resolver[/B]: Settings', 'urlresolversettings', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]Swadesi[/B]: General', 'openSettings&query=0.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]Swadesi[/B]: Playback', 'openSettings&query=1.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]Swadesi[/B]: Accounts', 'openSettings&query=2.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]Swadesi[/B]: Downloads', 'openSettings&query=3.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]Swadesi[/B]: Scrapers', 'openSettings&query=4.0', 'settings.png', 'DefaultAddonProgram.png')
        self.endDirectory()

    #def donation(self, version):
        #control.okDialog("If you like the addon please consider making a donation to [B]aftershockpy@gmail.com[/B]")
        #return 1

    def clearCache(self, url=None):
        try :
            if url == None:
                self.addDirectoryItem(90124, 'clearCache&url=main', 'clearcache.png','DefaultMovies.png')
                self.addDirectoryItem(90125, 'clearCache&url=providers', 'clearcache.png','DefaultMovies.png')
                self.addDirectoryItem(90127, 'clearCache&url=meta', 'clearcache.png','DefaultMovies.png')

                self.endDirectory()
            elif url == 'main':
                cache.clear()
            elif url == 'providers':
                cache.clear(['rel_src', 'rel_url'])
            elif url == 'live' :
                control.deleteAll('.json')
                control.delete('user.db')
                cache.clear(['rel_live', 'rel_logo', 'live_meta'])
                cache.clear(['live_cache'])
            elif url == 'meta':
                cache.clear(['meta', 'meta_imdb'], control.metacacheFile)
        except Exception as e:
            logger.error(e)

    def desiTV(self):
        listItems = []

        provider = control.setting('tvshow.provider')

        if not provider == None:
            call = __import__('resources.lib.sources.%s' % provider, globals(), locals(), ['source'], -1).source()
            listItems = call.networks()
        else:
            from resources.lib.sources import desirulez
            listItems = desirulez.source().networks()

        listItems.sort()

        try:
            for item in listItems:
                self.addDirectoryItem(item['name'], '%s&provider=%s&url=%s' % (item['action'],item['provider'], item['url']), os.path.join(
                control.logoPath(), item['image']), 'DefaultMovies.png')
        except Exception as e:
            logger.error(e)

        self.endDirectory()

    def search(self):
        self.addDirectoryItem(30151, 'movieSearch', 'search.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30152, 'tvSearch', 'search.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30153, 'moviePerson', 'moviePerson.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30154, 'tvPerson', 'tvPerson.jpg', 'DefaultTVShows.png')

        self.endDirectory()

    def addDirectoryItem(self, name, query, thumb, icon, context=None, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s&name=%s' % (sysaddon, query, name) if isAction == True else query

        if not 'http' in thumb :
            thumb = os.path.join(artPath, thumb) if not artPath == None else icon

        cm = []

        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
        item.addContextMenuItems(cm)
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, cacheToDisc=False):
        control.directory(syshandle, cacheToDisc=cacheToDisc)