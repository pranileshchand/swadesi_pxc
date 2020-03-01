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
import pkgutil
import random
import re
import sys
import time
import urllib
import urlparse

try: import xbmc
except: pass

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from aftershock.common import control, cleantitle, client, workers, debrid, cache, logger
from aftershock.common.player import player
from resources.lib import resolvers

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])

class sources:
    def __init__(self):
        self.resolverList = self.getResolverList()
        self.hostDict = self.getHostDict()
        self.hostprDict = self.getHostPrDict()
        self.srcs = []
        self.debridDict = debrid.debridDict()
        self.itemProperty = "%s.itemProperty" % control.addonInfo('name')
        self.metaProperty = "%s.itemMeta" % control.addonInfo('name')

    def addItem(self, title, content):
        try:
            control.playlist.clear()

            items = control.window.getProperty(self.itemProperty)
            items = json.loads(items)

            if items == []: raise Exception()

            meta = control.window.getProperty(self.metaProperty)
            meta = json.loads(meta)

            infoMenu = control.lang(30502).encode('utf-8')

            downloads = True if control.setting('downloads') == 'true' and not control.setting('movie.download.path') == '' else False

            #if 'tvshowtitle' in meta and 'season' in meta and 'episode' in meta:
            #    name = '%s S%02dE%02d' % (title, int(meta['season']), int(meta['episode']))
            #el
            if 'year' in meta:
                name = '%s (%s)' % (title, meta['year'])
            else:
                name = title

            systitle = urllib.quote_plus(title.encode('utf-8'))

            sysname = urllib.quote_plus(name.encode('utf-8'))

            poster = meta['poster'] if 'poster' in meta else '0'
            banner = meta['banner'] if 'banner' in meta else '0'
            thumb = meta['thumb'] if 'thumb' in meta else poster
            fanart = meta['fanart'] if 'fanart' in meta else '0'

            if poster == '0': poster = control.addonPoster()
            if banner == '0' and poster == '0': banner = control.addonBanner()
            elif banner == '0': banner = poster
            if thumb == '0' and fanart == '0': thumb = control.addonFanart()
            elif thumb == '0': thumb = fanart
            if control.setting('fanart') == 'true' and not fanart == '0': pass
            else: fanart = control.addonFanart()

            for i in range(len(items)):
                try :
                    parts = int(items[i]['parts'])
                except:
                    parts = 1

                label = items[i]['label']

                syssource = urllib.quote_plus(json.dumps([items[i]]))

                sysurl = '%s?action=playItem&title=%s&source=%s&content=%s' % (sysaddon, systitle, syssource, content)

                item = control.item(label=label)

                cm = []
                cm.append((control.lang(30504).encode('utf-8'), 'RunPlugin(%s?action=queueItem)' % sysaddon))
                if content != 'live':
                    if downloads == True and parts <= 1:
                        sysimage = urllib.quote_plus(poster.encode('utf-8'))
                        cm.append((control.lang(30505).encode('utf-8'), 'RunPlugin(%s?action=download&name=%s&image=%s&source=%s)' % (sysaddon, systitle, sysimage, syssource)))
                item.setArt({'icon': thumb, 'thumb': thumb, 'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': banner, 'tvshow.banner': banner, 'season.banner': banner})

                if not fanart == None: item.setProperty('Fanart_Image', fanart)

                item.addContextMenuItems(cm)
                item.setInfo(type='Video', infoLabels = meta)

                control.addItem(handle=syshandle, url=sysurl, listitem=item, isFolder=False)

            control.directory(syshandle, cacheToDisc=True)
        except Exception as e:
            logger.error(e.message)
            control.infoDialog(control.lang(30501).encode('utf-8'))

    def play(self, name, title, year, imdb, tvdb, season, episode, tvshowtitle, date, meta, url, select=None):
        try:
            if not control.infoLabel('Container.FolderPath').startswith('plugin://'):
                control.playlist.clear()

            control.resolve(syshandle, True, control.item(path=''))
            control.execute('Dialog.Close(okdialog)')

            if imdb == '0': imdb = '0000000'
            imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

            content = 'movie' if tvshowtitle == None else 'episode'

            self.srcs = self.getSources(name, title, year, imdb, tvdb, season, episode, tvshowtitle, date, meta)

            items = self.sourcesFilter()

            if len(items) > 0:
                try :
                    select = control.setting('host_select') if select == None else select
                except:
                    pass

                if select == '1' and 'plugin' in control.infoLabel('Container.PluginName'):
                    logger.debug('INSIDE select=1', __name__)
                    control.window.clearProperty(self.itemProperty)
                    control.window.setProperty(self.itemProperty, json.dumps(items))

                    control.window.clearProperty(self.metaProperty)
                    control.window.setProperty(self.metaProperty, meta)

                    control.sleep(200)
                    return control.execute('Container.Update(%s?action=addItem&title=%s&content=%s)' % (sysaddon, urllib.quote_plus(title.encode('utf-8')), content))

                elif select == '0' or select == '1':
                    url = self.sourcesDialog(items)

                else:
                    url = self.sourcesDirect(items)

            if url == None: raise Exception()
            if url == 'close://': return

            if control.setting('playback_info') == 'true':
                control.infoDialog(self.selectedSource, heading=name)

            control.sleep(200)

            player().run(content, name, url, year, imdb, tvdb, meta)

            return url
        except Exception as e:
            logger.error(e.message)
            control.infoDialog(control.lang(30501).encode('utf-8'))

    def playItem(self, content, title, source):
        try:
            #self.isRegistered()
            control.resolve(syshandle, True, control.item(path=''))
            control.execute('Dialog.Close(okdialog)')

            next = [] ; prev = [] ; total = []
            meta = control.window.getProperty(self.metaProperty)
            #meta = self.metaProperty
            meta = json.loads(meta)

            year = meta['year'] if 'year' in meta else None
            imdb = meta['imdb'] if 'imdb' in meta else None
            tvdb = meta['tvdb'] if 'tvdb' in meta else None


            for i in range(1,10000):
                try:
                    u = control.infoLabel('ListItem(%s).FolderPath' % str(i))

                    if u in total: raise Exception()
                    total.append(u)
                    u = dict(urlparse.parse_qsl(u.replace('?','')))
                    if 'meta' in u: meta = u['meta']
                    u = json.loads(u['source'])[0]
                    next.append(u)
                except:
                    break
            for i in range(-10000,0)[::-1]:
                try:
                    u = control.infoLabel('ListItem(%s).FolderPath' % str(i))
                    if u in total: raise Exception()
                    total.append(u)
                    u = dict(urlparse.parse_qsl(u.replace('?','')))
                    if 'meta' in u: meta = u['meta']
                    u = json.loads(u['source'])[0]
                    prev.append(u)
                except:
                    break

            items = json.loads(source)
            items = [i for i in items+next+prev][:40]

            self.progressDialog = control.progressDialog
            self.progressDialog.create(control.addonInfo('name'), '')
            self.progressDialog.update(0)

            block = None

            for i in range(len(items)):
                try:
                    self.progressDialog.update(int((100 / float(len(items))) * i), str(items[i]['label']), str(' '))

                    if items[i]['source'] == block: raise Exception()

                    w = workers.Thread(self.sourcesResolve, items[i])
                    w.start()

                    m = ''

                    for x in range(3600):
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        k = control.condVisibility('Window.IsActive(virtualkeyboard)')
                        if k: m += '1'; m = m[-1]
                        if (w.is_alive() == False or x > 30) and not k: break
                        time.sleep(1.0)

                    for x in range(3600):
                        if m == '': break
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        if w.is_alive() == False: break
                        time.sleep(1.0)


                    if w.is_alive() == True: block = items[i]['source']

                    if self.url == None: raise Exception()

                    try: self.progressDialog.close()
                    except: pass

                    control.sleep(200)

                    if control.setting('playback_info') == 'true':
                        control.infoDialog(items[i]['label'])

                    player().run(content, title, self.url, year, imdb, tvdb, meta)

                    return self.url
                except Exception as e:
                    logger.error(e, __name__)
                    pass

            try: self.progressDialog.close()
            except: pass

            raise Exception()

        except Exception as e:
            logger.error(e.message)
            control.infoDialog(control.lang(30501).encode('utf-8'))
            pass

    def getSources(self, name, title, year, imdb, tvdb, season, episode, tvshowtitle, date, meta=None):

        content = 'movie' if tvshowtitle == None else 'episode'

        control.makeFile(control.dataPath)
        self.sourceFile = control.sourcescacheFile

        logger.debug('Content [%s]' % content, __name__)

        try: timeout = int(control.setting('sources_timeout_40'))
        except: timeout = 40

        try: allowDebrid = bool(control.setting('allow_debrid'))
        except: allowDebrid = False

        import desiscrapers

        control.init('script.module.desiscrapers')
        totalScrapers = len(desiscrapers.relevant_scrapers(scraper_type=content))
        if content == 'movie':
            title = cleantitle.normalize(title)
            links_scraper = desiscrapers.scrape_movie(title, year, imdb, timeout=timeout, enable_debrid=allowDebrid)

        elif content == 'episode':
            tvshowtitle = cleantitle.normalize(tvshowtitle)
            imdb = json.loads(meta)['url']
            show_year = year
            tvshowtitle = tvshowtitle.replace('Season','').replace('season','')
            links_scraper = desiscrapers.scrape_episode(tvshowtitle, show_year, year, season, episode, imdb, tvdb, timeout=timeout, enable_debrid=allowDebrid)
        control.init('plugin.video.swadesi')

        control.idle()


        self.progressDialog = control.progressDialog
        self.progressDialog.create(control.addonInfo('name'), '')
        self.progressDialog.update(0)

        thread = workers.Thread(self.get_desi_sources, links_scraper, totalScrapers)

        thread.start()

        for i in range(0, timeout * 4):
            try:
                if xbmc.abortRequested:
                    return sys.exit()
                try:
                    if self.progressDialog.iscanceled():
                        break
                except:
                    pass
                if not thread.is_alive(): break
                time.sleep(0.5)
            except:
                pass

        self.progressDialog.close()

        for i in range(0, len(self.srcs)): self.srcs[i].update({'content': content})

        return self.srcs

    def get_desi_sources(self, links_scraper, totalScrapers):
        links_scraper = links_scraper()
        done = 0

        start_time = time.time()

        timeElapsed = control.lang(30512).encode('utf-8')
        seconds = control.lang(30513).encode('utf-8')
        processedSources = control.lang(30514).encode('utf-8')

        hdcount = 0
        sdcount = 0
        othercount = 0
        allcount = 0

        for scraper_links in links_scraper:
            done += 1
            end_time = time.time()
            duration = end_time - start_time
            try:
                if xbmc.abortRequested == True: return sys.exit()

                info = '%s/%s' % (done, totalScrapers)

                done = totalScrapers if done >= totalScrapers else done


                for scraper_link in scraper_links:
                    try:
                        q = scraper_link['quality']
                        if "1080" in q:
                            hdcount += 1
                        elif "HD" in q:
                            hdcount += 1
                        elif "720" in q:
                            hdcount += 1
                            scraper_link["quality"] = "HD"
                        elif "720" in q:
                            hdcount += 1
                            scraper_link["quality"] = "HD"
                        elif "560" in q:
                            hdcount += 1
                            scraper_link["quality"] = "HD"
                        elif "SD" in q:
                            sdcount += 1
                        else:
                            othercount += 1
                    except:
                        pass

                allcount = hdcount + sdcount + othercount


                self.progressDialog.update(int((100 / float(totalScrapers)) * done),
                                           str('%s: %s %s  HD : [COLOR red][B]%s[/B][/COLOR] SD : [COLOR blue][B]%s[/B][/COLOR] ([COLOR lime][B]%s[/B][/COLOR])' % (timeElapsed, int(duration), seconds, hdcount, sdcount, allcount)),
                                           str('%s: %s' % (processedSources, str(info))))

                if scraper_links is not None and len(scraper_links) > 0:
                    self.srcs.extend(scraper_links)

                if self.progressDialog.iscanceled(): break

            except:
                pass

    def sourcesDialog(self, items):
        try:

            labels = [i['label'] for i in items]

            select = control.selectDialog(labels)
            if select == -1: return 'close://'

            #self.isRegistered()

            next = [y for x,y in enumerate(items) if x >= select]
            prev = [y for x,y in enumerate(items) if x < select][::-1]

            items = [items[select]]
            items = [i for i in items+next+prev][:40]

            header = control.addonInfo('name')
            header2 = header.upper()

            progressDialog = control.progressDialog
            progressDialog.create(control.addonInfo('name'), '')
            progressDialog.update(0)

            block = None

            for i in range(len(items)):
                try:
                    if items[i]['source'] == block: raise Exception()

                    w = workers.Thread(self.sourcesResolve, items[i])
                    w.start()

                    try:
                        if progressDialog.iscanceled(): break
                        progressDialog.update(int((100 / float(len(items))) * i), str(items[i]['label']), str(' '))
                    except:
                        progressDialog.update(int((100 / float(len(items))) * i), str(header2), str(items[i]['label']))

                    m = ''

                    for x in range(3600):
                        try:
                            if xbmc.abortRequested == True: return sys.exit()
                            if progressDialog.iscanceled(): return progressDialog.close()
                        except:
                            pass

                        k = control.condVisibility('Window.IsActive(virtualkeyboard)')
                        if k: m += '1'; m = m[-1]
                        if (w.is_alive() == False or x > 30) and not k: break
                        k = control.condVisibility('Window.IsActive(yesnoDialog)')
                        if k: m += '1'; m = m[-1]
                        if (w.is_alive() == False or x > 30) and not k: break
                        time.sleep(0.5)


                    for x in range(30):
                        try:
                            if xbmc.abortRequested == True: return sys.exit()
                            if progressDialog.iscanceled(): return progressDialog.close()
                        except:
                            pass

                        if m == '': break
                        if w.is_alive() == False: break
                        time.sleep(0.5)


                    if w.is_alive() == True: block = items[i]['source']

                    if self.url == None: raise Exception()

                    self.selectedSource = items[i]['label']

                    try: progressDialog.close()
                    except: pass

                    control.execute('Dialog.Close(virtualkeyboard)')
                    control.execute('Dialog.Close(yesnoDialog)')
                    return self.url
                except:
                    pass

            try: progressDialog.close()
            except: pass

        except Exception as e:
            logger.error(e.message)
            try: progressDialog.close()
            except: pass

    def sourcesDirect(self, items):

        u = None

        self.progressDialog = control.progressDialog
        self.progressDialog.create(control.addonInfo('name'), '')
        self.progressDialog.update(0)

        #self.isRegistered()
        for i in range(len(items)):
            try:
                if self.progressDialog.iscanceled(): break

                self.progressDialog.update(int((100 / float(len(items))) * i), str(items[i]['label']), str(' '))

                if xbmc.abortRequested == True: return sys.exit()

                url = self.sourcesResolve(items[i])
                if url == None: raise Exception()
                if u == None: u = url

                self.selectedSource = items[i]['label']
                self.progressDialog.close()

                return url
            except:
                pass

        try: self.progressDialog.close()
        except: pass

        return u

    def alterSources(self, url, meta):
        try:
            if control.setting('host_select') == '2': url += '&select=1'
            else: url += '&select=2'
            control.execute('RunPlugin(%s)' % url)
        except:
            pass

    def sourcesFilter(self):
        logger.debug('Calling sources.filter()', __name__)
        logger.debug('ORIGINAL SOURCE COUNT : %s' % len(self.srcs), __name__)
        for i in range(len(self.srcs)): self.srcs[i]['source'] = self.srcs[i]['source'].lower()
        self.srcs = sorted(self.srcs, key=lambda k: k['source'])

        originalSrcs = self.srcs

        quality = control.setting('playback_quality')
        if quality == '': quality = '0'

        #set content
        filter = []
        try:filter += [i for i in self.srcs if i['content'] == 'live']
        except:
            filter += [dict(i.items() + [('content', '')]) for i in self.srcs]
            self.srcs = filter

        filter = []

        if debrid.status() == True:
            for d in self.debridDict: filter += [dict(i.items() + [('debrid', d)]) for i in self.srcs if i['source'].lower() in self.debridDict[d]]
            for host in self.hostDict : filter += [i for i in self.srcs if i['source'] in host and not i['content'] == 'live' and 'debridonly' not in i and i['source'] not in self.hostprDict]
        else :
            for host in self.hostDict : filter += [i for i in self.srcs if i['source'] in host and not i['content'] == 'live' and 'debridonly' not in i]

        filter += [i for i in self.srcs if i['direct'] == True and not i['content'] == 'live']
        try:filter += [i for i in self.srcs if i['content'] == 'live']
        except:pass
        self.srcs = filter

        logger.debug('FINAL SOURCE COUNT : %s' % len(self.srcs), __name__)

        #random.shuffle(self.srcs)

        filter = []
        if quality == '0' : filter += [i for i in self.srcs if i['quality'] == '1080p' and 'debrid' in i]
        if quality == '0' : filter += [i for i in self.srcs if i['quality'] == '1080p' and not 'debrid' in i]
        if quality == '0' or quality == '1': filter += [i for i in self.srcs if i['quality'] == 'HD' and 'debrid' in i]
        if quality == '0' or quality == '1': filter += [i for i in self.srcs if i['quality'] == 'HD' and not 'debrid' in i]
        filter += [i for i in self.srcs if i['quality'] == 'SD' and not 'debrid' in i]
        filter += [i for i in self.srcs if i['quality'] == 'SCR']
        filter += [i for i in self.srcs if i['quality'] == 'CAM']
        if len(filter) < 100:filter += [i for i in self.srcs if i['quality'] == '']
        self.srcs = filter

        r = [x for x in self.srcs + originalSrcs if x not in self.srcs or x not in originalSrcs]

        logger.debug('Filtered Sources : %s' % r, __name__)

        for i in range(len(self.srcs)):

            s = self.srcs[i]['source'].lower()
            try :
                p = self.srcs[i]['provider']
            except:
                p = self.srcs[i]['scraper']
            p = re.sub('v\d*$', '', p)

            q = self.srcs[i]['quality']

            try: f = (' | '.join(['[I]%s [/I]' % info.strip() for info in self.srcs[i]['info'].split('|')]))
            except: f = ''

            try: d = self.srcs[i]['debrid']
            except: d = self.srcs[i]['debrid'] = ''

            if not d == '': label = '%02d | [I]%s[/I] | [B]%s[/B] | ' % (int(i+1), d, p)
            else: label = '%02d | [B]%s[/B] | ' % (int(i+1), p)

            if q in ['1080p', 'HD']: label += '%s | %s | [B][I]%s [/I][/B]' % (s.rsplit('.', 1)[0], f, q)
            #elif q == 'SD': label += '%s | %s' % (s.rsplit('.', 1)[0], f)
            else: label += '%s | %s | [I]%s [/I]' % (s.rsplit('.', 1)[0], f, q)
            label = label.replace('| 0 |', '|').replace(' | [I]0 [/I]', '')
            label = label.replace('[I]HEVC [/I]', 'HEVC')
            label = re.sub('\[I\]\s+\[/I\]', ' ', label)
            label = re.sub('\|\s+\|', '|', label)
            label = re.sub('\|(?:\s+|)$', '', label)

            pts = None
            try : pts = self.srcs[i]['parts']
            except:pass

            if not pts == None and int(pts) > 1:
                label += ' [%s]' % pts

            self.srcs[i]['label'] = label.upper()
        return self.srcs

    def sourcesResolve(self, item):
        try:
            logger.debug('selected url : %s' % item['url'], __name__)
            logger.debug('selected item : %s' % item, __name__)
            u = url = item['url']

            if url == None or url == False : raise Exception()

            direct = item['direct']

            if not direct == True :
                logger.debug('Resolving [%s]' % url, __name__)

                try: allowDebrid = bool(control.setting('allow_debrid'))
                except: allowDebrid = False

                from resources.lib import resolvers
                u = resolvers.request(url, allowDebrid=allowDebrid)

                if 'plugin.video.f4mTester' in u:
                    try :
                        title = item['name']
                        title = urllib.quote_plus(title.encode('utf-8'))
                        iconImage = item['poster']
                    except:
                        pass
                    u += '&name=%s&iconImage=%s' % (title, iconImage)
                logger.debug('Resolved [%s]' % u, __name__)
                if u == False: raise Exception()

            url = u
            try :
                ext = url.split('?')[0].split('&')[0].split('|')[0].rsplit('.')[-1].replace('/', '').lower()
            except :
                ext = None
            if ext == 'rar': raise Exception()

            self.url = url
            return url
        except:
            self.url = None
            return

    def getResolverList(self):
        try:
            import urlresolver
            resolverList = []
            try: allowDebrid = bool(control.setting('allow_debrid'))
            except: allowDebrid = False
            try: resolverList = urlresolver.relevant_resolvers(order_matters=True, include_universal=allowDebrid)
            except: resolverList = urlresolver.plugnplay.man.implementors(urlresolver.UrlResolver)
            resolverList = [i for i in resolverList if not '*' in i.domains]
        except:
            resolverList = []
        return resolverList

    def getHostDict(self):
        try:
            hostDict = [i.domains for i in self.resolverList]
            hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
            hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]

            customHostDict = [x['host'] for x in resolvers.info()]
            customHostDict = [i.lower() for i in reduce(lambda x, y: x+y, customHostDict)]
            customHostDict = [x for y,x in enumerate(customHostDict) if x not in customHostDict[:y]]
            hostDict += customHostDict
            hostDict = list(set(hostDict))
        except:
            hostDict = []
        return hostDict

    def getHostPrDict(self):
        hostPrDict = ['dailymotion.com', 'openload.co']
        return hostPrDict

    #def isRegistered(self):
        #email = control.setting('email')

        #if email == None or email == '':
            #playCount = self.unRegPlay()
            #if playCount <= 3 :
                #control.okDialog(control.lang(30519).encode('utf-8'), control.lang(30520).encode('utf-8'))
            #else :
                #control.okDialog(control.lang(30521).encode('utf-8'), control.lang(30522).encode('utf-8'))
                #sys.exit()
        #else :
            #error = control.moderator()
            #if error == 'Email not registred':
                #playCount = self.unRegPlay()
                #if playCount <= 3 :
                    #control.okDialog(control.lang(30519).encode('utf-8'), control.lang(30520).encode('utf-8'), control.lang(30524).encode('utf-8'))
                #else :
                    #control.okDialog(control.lang(30521).encode('utf-8'), control.lang(30522).encode('utf-8'))
                    #sys.exit()

    #def unRegPlay(self):
        #count = 1
        #try:
            #now = datetime.datetime.now()
            #currentDate = now.strftime("%Y-%m-%d")
            #dbcon = database.connect(control.cacheFile)
            #dbcur = dbcon.cursor()
            #try:
                #dbcur.execute("SELECT playCount FROM playCount where date = '%s'" % currentDate)
                #playCount = dbcur.fetchone()[0]
                #if playCount == None :
                    #raise Exception()
                #playCount = playCount + 1
                #dbcur.execute("DELETE FROM playCount where date = '%s'" % currentDate)
                #dbcur.execute("INSERT INTO playCount Values (?, ?)", (playCount, currentDate))
                #dbcon.commit()
            #except Exception as e:
                #logger.error(e, __name__)
                #playCount = 1
                #dbcur.execute("CREATE TABLE IF NOT EXISTS playCount (""playCount INTEGER, ""date TEXT)")
                #dbcur.execute("INSERT INTO playCount Values (?, ?)", (playCount, currentDate))
                
#dbcon.commit()

        #except Exception as e:
            #logger.error(e, __name__)
            #return playCount
        #return playCount