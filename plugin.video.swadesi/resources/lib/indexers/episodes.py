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

import datetime
import json
import os
import sys
import urllib

from aftershock.common import control, logger, views, playcount

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])

class episodes:
    def __init__(self):
        self.list = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.info_lang = control.setting('infoLang') or 'en'

    def get(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, idx=True, provider=None, url=None):
        try:
            if idx == True:
                if not provider == None:
                    call = __import__('resources.lib.sources.%s' % provider, globals(), locals(), ['source'], -1).source()
                    self.list = call.episodes(tvshowtitle, url)
                    if self.list == [] : raise Exception(control.lang(30516).encode('utf-8'))
                    self.list = self.super_info(self.list)

                try :
                    logger.debug('Before Episode Direcotry', __name__)
                    self.episodeDirectory(self.list, provider)
                    logger.debug('After Episode Direcotry', __name__)
                except Exception as e:
                    logger.error(e)

                return self.list
        except Exception as e:
            logger.error(e)
            control.infoDialog(control.lang(30516).encode('utf-8'))
            pass

    def super_info(self, items):
        logger.debug('INSIDE SUPER_INFO', __name__)
        try :
            for i in range(0, len(items)):
                season = '0' if items[i].get('season') == None else items[i].get('season')
                self.list[i].update({'season':season, 'episode':self.list[i]['name'],'imdb':'0', 'tvdb':'0', 'year':'0', 'poster':'0', 'banner':'0', 'fanart':'0', 'thumb':'0', 'premiered':'0', 'duration':'30'})
            logger.debug('COMPLETE SUPER_INFO', __name__)
            return self.list
        except Exception as e:
            logger.error(e)
            pass


    def episodeDirectory(self, items, provider=None, confViewMode='list', estViewMode='widelist'):
        if items == None or len(items) == 0: return

        isFolder = True if control.setting('host_select') == '1' else False
        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        playbackMenu = control.lang(30271).encode('utf-8') if control.setting('host_select') == '2' else control.lang(30270).encode('utf-8')

        cacheToDisc = False

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        indicators = playcount.getTVShowIndicators(refresh=True)

        try: multi = [i['tvshowtitle'] for i in items]
        except Exception as e:
            logger.error(e)
            multi = []

        multi = len([x for y,x in enumerate(multi) if x not in multi[:y]])
        multi = True if multi > 1 else False

        sysaction = '' if items[0].get('action') == None else items[0].get('action')

        for i in items:
            try:
                try :
                    if i['title'] == '0':
                        label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                    elif i['season'] == '0':
                        label = '%s' % (i['episode'])
                    else :
                        label = '%sx%02d . %s' % (i['season'], int(i['episode']), i['title'])
                except:
                    label = i['title']
                if multi == True:
                    label = '%s - %s' % (i['tvshowtitle'], label)

                systitle = sysname = urllib.quote_plus(i['tvshowtitle'].encode('utf-8'))
                episodetitle, episodename = urllib.quote_plus(i['title'].encode('utf-8'), safe=':/'), urllib.quote_plus(i['name'].encode('utf-8'), safe=':/')
                syspremiered = urllib.quote_plus(i['premiered'])
                imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                poster, banner, fanart, thumb = i['poster'], i['banner'], i['fanart'], i['thumb']
                if poster == '0': poster = addonPoster
                if banner == '0' and poster == '0': banner = addonBanner
                elif banner == '0': banner = poster
                if thumb == '0' and fanart == '0': thumb = addonFanart
                elif thumb == '0': thumb = fanart

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                if i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = '%s?action=play&name=%s&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&date=%s&meta=%s&t=%s' % (sysaddon, episodename, episodetitle, year, imdb, tvdb, season, episode, systitle, syspremiered, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)

                if sysaction == 'episodes':
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode)
                    isFolder = True ; cacheToDisc = True

                cm = []

                if isFolder == False:
                    cm.append((control.lang(30261).encode('utf-8'), 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((control.lang(30272).encode('utf-8'), 'Action(Info)'))

                if multi == True:
                    cm.append((control.lang(30274).encode('utf-8'), 'ActivateWindow(Videos,%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s,return)' % (sysaddon, systitle, year, imdb, tvdb)))

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                item = control.item(label=label, iconImage=thumb, thumbnailImage=thumb)

                try: item.setArt({'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': banner, 'tvshow.banner': banner, 'season.banner': banner})
                except: pass

                if settingFanart == 'true' and not fanart == '0':
                    item.setProperty('Fanart_Image', fanart)
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setInfo(type='Video', infoLabels = meta)
                item.setProperty('Video', 'true')
                item.setProperty('IsPlayable', isPlayable)
                item.setProperty('resumetime',str(0))
                item.setProperty('totaltime',str(1))
                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except Exception as e:
                logger.error(e)
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()
            url = '%s?action=episodes&tvshowtitle=%s&url=%s&provider=%s' % (sysaddon, systitle, urllib.quote_plus(url), provider)
            addonNext = control.addonNext()
            item = control.item(label=control.lang(30213).encode('utf-8'), iconImage=addonNext, thumbnailImage=addonNext)
            item.addContextMenuItems([])
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass


        content = 'episodes'
        control.content(syshandle, content)
        control.directory(syshandle, cacheToDisc=cacheToDisc)
        views.setView(content, {'skin.confluence': control.viewMode['confluence'][confViewMode], 'skin.estuary':
            control.viewMode['esturary'][estViewMode]})

    def addDirectory(self, items):
        if items == None or len(items) == 0: return

        addonFanart = control.addonFanart()
        addonThumb = control.addonThumb()
        artPath = control.artPath()

        for i in items:
            try:
                try: name = control.lang(i['name']).encode('utf-8')
                except: name = i['name']

                if not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
                item.addContextMenuItems([])
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.directory(syshandle, cacheToDisc=True)