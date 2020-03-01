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

import base64
import datetime
import json
import os
import re
import sys
import urllib
import urlparse

try: action = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))['action']
except: action = None

from aftershock.common import control, trakt, client, cache, metacache, workers, views, logger, playcount

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])

class movies:
    def __init__(self):
        self.list = []
        self.languagesList = [
            ('Hindi', 'hi'),
            ('Tamil', 'ta'),
            ('Telugu', 'te'),
            ('Marathi', 'mr'),
            ('Panjabi', 'pa'),
            ('Bengali', 'bn'),
            ('Gujarati', 'gu'),
            ('Malayalam', 'ml'),
            ('Kannada','kn')
        ]

        self.imdb_link = 'http://www.imdb.com'
        self.tmdb_key = base64.urlsafe_b64decode('MTdmMjI3YmVjNTdkOTQ4OGJiYzgyNzYyZmMxNDQ0NmM=')
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.imdb_user = control.setting('imdb_user').replace('ur', '')
        self.info_lang = control.setting('infoLang') or 'en'
        self.imdb_info_link = 'http://www.omdbapi.com/?i=%s&plot=full&r=json'
        self.trakt_info_link = 'http://api-v2launch.trakt.tv/movies/%s?extended=images'

        self.tm_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=%s' % ('%s',self.tmdb_key)
        self.tm_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=credits,images,trailers' % ('%s',self.tmdb_key)
        self.tm_img_link = 'https://image.tmdb.org/t/p/w%s%s'


        self.search_link = 'http://www.imdb.com/search/title?sort=release_date,desc&title=%s'
        self.language_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&languages=%s&count=40&start=1&sort=release_date,desc&start=1'
        self.featured_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=%s&num_votes=1000,&production_status=released&release_date=date[365],date[60]&sort=moviemeter,asc&count=40&start=1'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=%s&num_votes=1000,&production_status=released&groups=top_1000&sort=moviemeter,asc&count=40&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=%s&num_votes=100,&release_date=date[730],date[30]&genres=%s&sort=release_date,desc&count=40&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=%s&num_votes=100,&production_status=released&year=%s,%s&sort=release_date,desc&count=40&start=1'


    def get(self, url, idx=True, provider=None, lang=None):
        logger.debug('url [%s] provider [%s] lang [%s] ' % (url, provider, lang), self.__class__)
        self.lang = lang
        try:
            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass
            if u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 48, url)
                if idx == True: self.worker()

            if idx == True: self.movieDirectory(self.list, lang=lang)
            return self.list
        except Exception as e:
            logger.error(e, __name__)
            pass

    def imdb_list(self, url):
        try:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            result = client.request(url)

            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')

            items = client.parseDOM(result, 'div', attrs = {'class': 'lister-item mode-advanced'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
                year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
                year = re.findall('(\d{4})', year[0])[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]
                imdb = imdb.encode('utf-8')

                tmdb = '0'

                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
                poster = re.sub('(?:_SX\d+?|)(?:_SY\d+?|)(?:_UX\d+?|)_CR\d+?,\d+?,\d+?,\d*','_SX500', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})[0]
                except: genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = re.findall('(\d+?) min(?:s|)', item)[-1]
                except: duration = '0'
                duration = duration.encode('utf-8')

                rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: pass
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                except: pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
                except: votes = '0'
                try: votes = re.findall('\((.+?) vote(?:s|)\)', votes)[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                try: director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: director = '0'
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                try: cast = re.findall('Stars(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: cast = '0'
                cast = client.replaceHTMLCodes(cast)
                cast = cast.encode('utf-8')
                cast = client.parseDOM(cast, 'a')
                if cast == []: cast = '0'

                plot = '0'
                try: plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
                except: pass
                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': '0', 'cast': cast, 'plot': plot, 'code': imdb, 'imdb': imdb, 'tvdb': '0', 'tmdb': tmdb, 'poster': poster, 'banner': '0', 'fanart': '0', 'next': next})
            except:
                pass

        return self.list

    def search(self, query=None, lang=None):
        try:
            if query == None:
                t = control.lang(30201).encode('utf-8')
                k = control.keyboard('', t) ; k.doModal()
                self.query = k.getText() if k.isConfirmed() else None
            else:
                self.query = query

            if (self.query == None or self.query == ''): return

            url = self.search_link % (urllib.quote_plus(self.query))
            self.list = cache.get(self.imdb_list, 0, url)

            self.worker()
            self.movieDirectory(self.list)
            return self.list
        except:
            return

    def home(self, lang=None):
        self.list.append({'name': 90109, 'image': 'genre.png', 'action': 'movieLangGenre&lang=%s' % lang})
        self.list.append({'name': 90110, 'image': 'year.png', 'action': 'movieLangYears&lang=%s' % lang})
        self.list.append({'name': 90103, 'url': self.language_link % lang, 'image': 'theater.png', 'action': 'movies'})
        self.list.append({'name': 90104, 'url': self.featured_link % lang, 'image': 'featured.png', 'action': 'movies'})
        self.list.append({'name': 90105, 'url': self.popular_link % lang, 'image': 'popular.png', 'action': 'movies'})

        self.addDirectory(self.list, confViewMode='thumbnails')

    def genres(self, lang=None):
        genres = [
            ('Action', 'action'),
            ('Adventure', 'adventure'),
            ('Animation', 'animation'),
            ('Biography', 'biography'),
            ('Comedy', 'comedy'),
            ('Crime', 'crime'),
            ('Drama', 'drama'),
            ('Family', 'family'),
            ('Fantasy', 'fantasy'),
            ('History', 'history'),
            ('Horror', 'horror'),
            ('Musical', 'musical'),
            ('Mystery', 'mystery'),
            ('Romance', 'romance'),
            ('Science Fiction', 'sci_fi'),
            ('Sport', 'sport'),
            ('Thriller', 'thriller')
        ]

        for i in genres: self.list.append({'name': i[0], 'url': self.genre_link % (lang, i[1]), 'image': '%s.png' % i[1], 'action': 'movies&lang=%s' % lang})
        self.addDirectory(self.list)
        return self.list

    def years(self, lang=None):
        year = (self.datetime.strftime('%Y'))
        for i in range(int(year)-0, int(year)-50, -1): self.list.append({'name': str(i), 'url': self.year_link % (lang, str(i), str(i)), 'image': 'year.png', 'action': 'movies&lang=%s' % lang})
        self.addDirectory(self.list)
        return self.list

    def languages(self):
        self.list.append({'name':30201, 'url':'movieSearch', 'image':'search.png', 'action':'movieSearch'})
        for i in self.languagesList: self.list.append({'name': str(i[0]), 'image': 'language.png', 'action': 'movieLangHome&lang=%s' % (str(i[1]))})
        self.addDirectory(self.list)
        return self.list

    def worker(self):
        self.meta = []
        total = len(self.list)
        for i in range(0, total): self.list[i].update({'metacache': False})
        self.list = metacache.fetch(self.list, self.info_lang)

        itemsPerPage = 25
        for r in range(0, total, itemsPerPage):
            threads = []
            for i in range(r, r+itemsPerPage):
                if i <= total: threads.append(workers.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

        if len(self.meta) > 0: metacache.insert(self.meta)

    def super_info(self, i):
        try:

            if self.list[i]['metacache'] == True: raise Exception()

            imdb = self.list[i]['imdb']

            url = self.tm_info_link % imdb

            item = client.request(url, timeout='10')

            item = json.loads(item)

            tmdb = item.get('id')
            self.list[i].update({'tmdb':tmdb})

            title = item.get('title')
            title = title.encode('utf-8')
            if not title == '0': self.list[i].update({'title': title})

            year = item.get('release_date')
            match = re.search('\d{4}', year)
            year = match.group(0) if match else '0'
            year = year.encode('utf-8')
            if not year == '0': self.list[i].update({'year': year})

            imdb = item.get('imdb_id')
            if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'
            imdb = imdb.encode('utf-8')
            if not imdb == '0': self.list[i].update({'imdb': imdb, 'code': imdb})

            premiered = item.get('release_date')
            if premiered == None or premiered == '' or premiered == 'N/A': premiered = '0'
            premiered = premiered.encode('utf-8')
            if not premiered == '0': self.list[i].update({'premiered': premiered})

            genre = item.get('genres')
            genre = [x['name'] for x in genre]
            genre = " / ".join(genre)
            if genre == None or genre == '' or genre == 'N/A': genre = '0'
            genre = genre.encode('utf-8')
            if not genre == '0': self.list[i].update({'genre': genre})

            duration = item.get('runtime')
            if duration == None or duration == '' or duration == 'N/A': duration = '0'
            duration = re.sub('[^0-9]', '', str(duration))
            duration = duration.encode('utf-8')
            if not duration == '0': self.list[i].update({'duration': duration})

            rating = votes = mpaa = '0'

            crew = item.get('credits').get('crew')
            director = [x.get('name') for x in crew if x.get('job') == 'Director']
            director = " / ".join(director)
            if director == None or director == '' or director == 'N/A': director = '0'
            director = re.sub(r'\(.*?\)', '', director)
            director = ' '.join(director.split())
            director = director.encode('utf-8')
            if not director == '0': self.list[i].update({'director': director})

            writer = [x.get('name') for x in crew if x.get('job') == 'Writer']
            writer = " / ".join(writer)
            if writer == None or writer == '' or writer == 'N/A': writer = '0'
            writer = re.sub(r'\(.*?\)', '', writer)
            writer = ' '.join(writer.split())
            writer = writer.encode('utf-8')
            if not writer == '0': self.list[i].update({'writer': writer})

            cast = item.get('credits').get('cast')
            cast = [(x.get('name'), x.get('character')) for x in cast]
            if cast == None or cast == '' or cast == 'N/A' or cast == []: cast = '0'
            if not cast == '0': self.list[i].update({'cast': cast})

            plot = item.get('overview')
            if plot == None or plot == '' or plot == 'N/A': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
            if not plot == '0': self.list[i].update({'plot': plot})

            art = item.get('images')
            try:
                poster = art.get('posters')
                poster = sorted(poster, key=lambda k: k['width'], reverse=True)
                poster = [(x['width'], x['file_path']) for x in poster]
                poster = [(x[0], x[1]) if x[0] < 500 else ('500', x[1]) for x in poster]
                poster = self.tm_img_link % poster[0]
                poster = poster.encode('utf-8')
                if not poster == '0': self.list[i].update({'poster': poster})
            except:
                poster = '0'

            try:
                fanart = art.get('backdrops')
                fanart = sorted(fanart, key=lambda k: k['width'], reverse=True)
                fanart = [(x['width'], x['file_path']) for x in fanart]
                fanart = [(x[0], x[1]) if x[0] < 1280 else ('1280', x[1]) for x in fanart]
                fanart = self.tm_img_link % fanart[0]
                fanart = fanart.encode('utf-8')
                if not fanart == '0': self.list[i].update({'fanart': fanart})
            except:
                fanart = '0'


            trailer = item.get('trailers')
            if trailer :
                trailer = trailer.get('youtube')
                found_trailer = next((x for x in trailer if x['type'] == 'Trailer'), None)
                if found_trailer:
                    trailer = found_trailer['source']
                    self.list[i].update({'trailer': trailer})
                else:
                    trailer = '0'

            studio = self.list[i]['studio']

            url = self.trakt_info_link % imdb

            art3 = trakt.getTrakt(url)
            try : art3 = json.loads(art3)
            except:pass

            if poster == '0':
                try: poster = art3['images']['poster']['medium']
                except: pass
                if poster == None or not '/posters/' in poster: poster = '0'
                poster = poster.rsplit('?', 1)[0]
                if poster == '0': poster = self.list[i]['poster']
                poster = poster.encode('utf-8')
                if not poster == '0': self.list[i].update({'poster': poster})

            banner = '0'
            try: banner = art3['images']['banner']['full']
            except: pass
            if banner == None or not '/banners/' in banner: banner = '0'
            banner = banner.rsplit('?', 1)[0]
            banner = banner.encode('utf-8')
            if not banner == '0': self.list[i].update({'banner': banner})

            if fanart == '0':
                try: fanart = item['images']['fanart']['full']
                except: pass
                if fanart == None or not '/fanarts/' in fanart: fanart = '0'
                fanart = fanart.rsplit('?', 1)[0]
                if fanart == '0': poster = self.list[i]['fanart']
                fanart = fanart.encode('utf-8')
                if not fanart == '0': self.list[i].update({'fanart': fanart})

            # add code for watched overlay
            self.meta.append({'imdb': imdb, 'tmdb':tmdb, 'tvdb': '0', 'lang': self.lang, 'item': {'title': title, 'year': year, 'code': imdb, 'imdb': imdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'trailer':trailer}})
        except Exception as e:
            #logger.error(e, __name__)
            pass

    def movieDirectory(self, items, lang=None):
        if items == None or len(items) == 0:
            control.infoDialog(control.lang(30518).encode('utf-8'))
            return

        indicators = playcount.getMovieIndicators()

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        playbackMenu = control.lang(30204).encode('utf-8') if control.setting('host_select') == '2' else control.lang(30203).encode('utf-8')

        cacheToDisc = False if not action == 'movieSearch' else True

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        for i in items:
            try:
                label = '%s (%s)' % (i['title'], i['year'])
                imdb, title, year, trailer = i['imdb'], i['title'], i['year'], i.get('trailer')
                sysname = urllib.quote_plus('%s (%s)' % (title, year))
                systitle = urllib.quote_plus(title)

                poster, banner, fanart = i['poster'], i['banner'], i['fanart']
                if poster == '0': poster = addonPoster
                if banner == '0' and poster == '0': banner = addonBanner
                elif banner == '0': banner = poster

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'trailer': '%s?action=trailer&name=%s&url=%s' % (sysaddon, sysname, trailer)})
                if i['duration'] == '0': meta.update({'duration': '120'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                sysmeta = urllib.quote_plus(json.dumps(meta))


                url = '%s?action=play&name=%s&title=%s&year=%s&imdb=%s&meta=%s&t=%s' % (sysaddon, sysname, systitle, year, imdb, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)

                cm = []

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta))) # AUTOPLAY

                cm.append((control.lang(30214).encode('utf-8'), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sysaddon, sysname, trailer))) # TRAILER
                cm.append((control.lang(30205).encode('utf-8'), 'Action(Info)')) # MOVIEINFORMATION

                cm.append((control.lang(30212).encode('utf-8'), 'RunPlugin(%s?action=addView&content=movies)' % sysaddon)) # SET MOVIES VIEW


                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    #logger.debug('imdb : %s Overlay : %s' % (imdb, overlay), __name__)
                    if overlay == 7:
                        cm.append((control.lang(30206).encode('utf-8'), 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((control.lang(30207).encode('utf-8'), 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except Exception as e:
                    logger.error(e, __name__)
                    pass

                item = control.item(label=label, iconImage=poster, thumbnailImage=poster)

                try: item.setArt({'poster': poster, 'banner': banner})
                except: pass

                if settingFanart == 'true' and not fanart == '0':
                    item.setProperty('Fanart_Image', fanart)
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setInfo(type='Video', infoLabels = meta)
                item.setProperty('Video', 'true')
                item.setProperty('IsPlayable', isPlayable)
                item.addContextMenuItems(cm)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except Exception as e:
                logger.error(e, __name__)
                pass
        try:
            url = items[0]['next']
            if url == '': raise Exception()
            url = '%s?action=movies&url=%s' % (sysaddon, urllib.quote_plus(url))
            addonNext = control.addonNext()
            item = control.item(label=control.lang(30213).encode('utf-8'), iconImage=addonNext, thumbnailImage=addonNext)
            item.addContextMenuItems([])
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except Exception as e:
            logger.error(e, __name__)
            pass

        content = 'movies'
        control.content(syshandle, content)
        control.directory(syshandle, cacheToDisc=cacheToDisc)
        views.setView(content, {'skin.confluence': control.viewMode['confluence']['thumbnails'], 'skin.estuary':
            control.viewMode['esturary']['list']})


    def addDirectory(self, items, estViewMode='biglist', confViewMode='list'):
        if items == None or len(items) == 0: return
        addonFanart = control.addonFanart()
        addonThumb = control.addonThumb()
        artPath = control.artPath()

        for i in items:
            try:
                try: name = control.lang(i['name']).encode('utf-8')
                except: name = i['name']

                if i['image'].startswith('http://'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                cm = []

                item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
                item.addContextMenuItems(cm)
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except Exception as e:
                logger.error(e, __name__)
                pass
        control.directory(syshandle, cacheToDisc=True)