# -*- coding: utf-8 -*-

'''
    Aftershock Add-on
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
import re
import urlparse

from resources.lib import resolvers
from aftershock.common import client, cache, logger, cleantitle

class source:
    def __init__(self):
        self.base_link_1 = 'http://www.desirulez.cc'
        self.base_link_2 = 'http://www.desirulez.me'
        self.base_link_3 = 'http://www.desirulez.net'
        self.search_link = '/feed/?s=%s&submit=Search'

        self.info_link = ''
        self.now = datetime.datetime.now()

        self.awards_link = 'forumdisplay.php?f=36'
        self.star_plus_link = 'forumdisplay.php?f=42'
        self.zee_tv_link = 'forumdisplay.php?f=73'
        self.sony_link = 'forumdisplay.php?f=63'
        self.life_ok_link = 'forumdisplay.php?f=1375'
        self.colors_link = 'forumdisplay.php?f=176'
        self.sony_sab_link = 'forumdisplay.php?f=254'
        self.star_jalsha_link = 'forumdisplay.php?f=667'
        self.sahara_one_link = 'forumdisplay.php?f=134'
        self.and_tv_link = 'forumdisplay.php?f=3138'
        self.star_pravah_link = 'forumdisplay.php?f=1138'
        self.sony_pal_link = 'forumdisplay.php?f=2757'
        self.mtv_india_link = 'forumdisplay.php?f=339'
        self.utv_bindass_link = 'forumdisplay.php?f=504'
        self.channel_v_link = 'forumdisplay.php?f=633'
        self.utv_stars_link = 'forumdisplay.php?f=1274'
        self.big_magic_link = 'forumdisplay.php?f=1887'
        self.zee_marathi_link = 'forumdisplay.php?f=1299'
        self.zee_bangla = 'forumdisplay.php?f=676'
        self.star_vijay_link = 'forumdisplay.php?f=1609'
        self.zoom_link = 'forumdisplay.php?f=1876'
        self.zing_link = 'forumdisplay.php?f=2624'
        self.zee_yuva_link = 'forumdisplay.php?f=4229'
        self.colors_marathi_link = 'forumdisplay.php?f=2369'
        self.colors_bangla_link = 'forumdisplay.php?f=2117'
        self.maa_link = 'forumdisplay.php?f=3165'
        self.star_bharat_link = 'forumdisplay.php?f=4856'

        self.hungama_link = 'forumdisplay.php?f=472'
        self.cartoon_network_link = 'forumdisplay.php?f=509'

        self.zee_zindagi_link = 'forumdisplay.php?f=2679'

        self.srcs = []

    def networks(self):
        listItems = []
        provider = 'desirulez'
        listItems.append({'provider':provider, 'name':90200, 'image': 'star_plus_hk.png', 'action': 'tvshows', 'url':self.star_plus_link})
        listItems.append({'provider':provider, 'name':90201, 'image': 'zee_tv_in.png', 'action': 'tvshows', 'url':self.zee_tv_link})
        listItems.append({'provider':provider, 'name':90203, 'image': 'sony_set.png', 'action': 'tvshows', 'url':self.sony_link})
        listItems.append({'provider':provider, 'name':90205, 'image': 'life_ok_in.png', 'action': 'tvshows', 'url':self.life_ok_link})
        listItems.append({'provider':provider, 'name':90206, 'image': 'sahara_one_in.png', 'action': 'tvshows', 'url':self.sahara_one_link})
        listItems.append({'provider':provider, 'name':90207, 'image': 'star_jalsha.png', 'action': 'tvshows', 'url':self.star_jalsha_link})
        listItems.append({'provider':provider, 'name':90208, 'image': 'colors_in.png', 'action': 'tvshows', 'url':self.colors_link})
        listItems.append({'provider':provider, 'name':90209, 'image': 'sony_sab_tv_in.png', 'action': 'tvshows', 'url':self.sony_sab_link})
        listItems.append({'provider':provider, 'name':90210, 'image': 'star_pravah.png', 'action': 'tvshows', 'url':self.star_pravah_link})
        listItems.append({'provider':provider, 'name':90212, 'image': 'mtv_us.png', 'action': 'tvshows', 'url':self.mtv_india_link})
        listItems.append({'provider':provider, 'name':90213, 'image': 'channel_v_in.png', 'action': 'tvshows', 'url':self.channel_v_link})
        listItems.append({'provider':provider, 'name':90214, 'image': 'bindass_in.png', 'action': 'tvshows', 'url':self.utv_bindass_link})
        listItems.append({'provider':provider, 'name':90215, 'image': 'utv_stars.png', 'action': 'tvshows', 'url':self.utv_stars_link})
        listItems.append({'provider':provider, 'name':90218, 'image': 'hungama.png', 'action': 'tvshows', 'url':self.hungama_link})
        listItems.append({'provider':provider, 'name':90219, 'image': 'cartoon_network_global.png', 'action': 'tvshows', 'url':self.cartoon_network_link})
        listItems.append({'provider':provider, 'name':90220, 'image': 'and_tv_in.png', 'action': 'tvshows', 'url':self.and_tv_link})
        listItems.append({'provider':provider, 'name':90222, 'image': 'colors_in_bangla.png', 'action': 'tvshows', 'url':self.colors_bangla_link})
        listItems.append({'provider':provider, 'name':90223, 'image': 'zee_zindagi_in.png', 'action': 'tvshows', 'url':self.zee_zindagi_link})
        listItems.append({'provider':provider, 'name':90224, 'image': 'big_magic_in.png', 'action': 'tvshows', 'url':self.big_magic_link})
        listItems.append({'provider':provider, 'name':90225, 'image': 'colors_in_marathi.png', 'action': 'tvshows', 'url':self.colors_marathi_link})
        listItems.append({'provider':provider, 'name':90226, 'image': 'maa_tv.png', 'action': 'tvshows', 'url':self.maa_link})
        listItems.append({'provider':provider, 'name':90227, 'image': 'zee_marathi.png', 'action': 'tvshows', 'url':self.zee_marathi_link})
        listItems.append({'provider':provider, 'name':90228, 'image': 'zee_bangla.png', 'action': 'tvshows', 'url':self.zee_bangla})
        listItems.append({'provider':provider, 'name':90229, 'image': 'zoom_tv_in.png', 'action': 'tvshows', 'url':self.zoom_link})
        listItems.append({'provider':provider, 'name':90230, 'image': 'star_vijay.png', 'action': 'tvshows', 'url':self.star_vijay_link})
        listItems.append({'provider':provider, 'name':90231, 'image': 'sony_pal_in.png', 'action': 'tvshows', 'url':self.sony_pal_link})
        listItems.append({'provider':provider, 'name':90232, 'image': 'zee_zing.png', 'action': 'tvshows', 'url':self.zing_link})
        listItems.append({'provider':provider, 'name':90233, 'image': 'zee_yuva_in.png', 'action': 'tvshows', 'url':self.zee_yuva_link})
        url = 'episodes&tvshowtitle=awards&year=0&imdb=0&tvdb=0'
        listItems.append({'provider':provider, 'name':90234, 'image': 'awards_in.png', 'action': url, 'url':self.awards_link})
        listItems.append({'provider':provider, 'name':90235, 'image': 'star_bharat.png', 'action': 'tvshows', 'url':self.star_bharat_link})

        return listItems

    def tvshows(self, name, url):
        try:
            result = ''
            shows = []
            links = [self.base_link_1, self.base_link_2, self.base_link_3]
            for base_link in links:
                try:
                    result, response_code, response_headers, headers, cookie = client.request('%s/%s' % (base_link, url), output='extended')
                    if result == None:
                        raise Exception()
                except: result = ''
                if 'forumtitle' in result: break

            #result = result.decode('ISO-8859-1').encode('utf-8')
            result = result.decode('windows-1252').encode('utf-8')
            result = client.parseDOM(result, "h2", attrs = {"class" : "forumtitle"})

            for item in result:
                title = ''
                url = ''

                try :
                    title = client.parseDOM(item, "a", attrs = {"class": "title threadtitle_unread"})[0]
                except:
                    title = client.parseDOM(item, "a", attrs = {"class": "title"})
                    title = title[0] if title else client.parseDOM(item, "a")[0]

                #title = cleantitle.unicodetoascii(title)
                title = client.replaceHTMLCodes(title)

                if title == 'Naamkarann':
                    title = 'Naamkaran'

                url = client.parseDOM(item, "a", ret="href")

                if not url:
                    url = client.parseDOM(item, "a", attrs = {"class": "title"}, ret="href")

                if type(url) is list and len(url) > 0:
                    url = str(url[0])

                if not 'Past Shows' in title:
                    # name , title, poster, imdb, tvdb, year, poster, banner, fanart, duration
                    shows.append({'name':title, 'title':title, 'url':url, 'poster': '0', 'banner': '0', 'fanart': '0', 'next': '0','year':'0','duration':'0','provider':'desirulez'})
            return shows
        except Exception as e:
            logger.error(e)
            return

    def episodes(self, title, url):
        try :
            episodes = []
            links = [self.base_link_1, self.base_link_2, self.base_link_3]
            tvshowurl = url
            for base_link in links:
                try:
                    url = url.replace(base_link, '')
                    result = client.request(base_link + '/' + url)
                    if result == None:
                        raise Exception()
                except:
                    result = ''

                if 'threadtitle' in result: break

            rawResult = result.decode('windows-1252').encode('utf-8')

            result = client.parseDOM(rawResult, "h3", attrs = {"class" : "title threadtitle_unread"})
            result += client.parseDOM(rawResult, "h3", attrs = {"class" : "threadtitle"})

            for item in result:
                name = client.parseDOM(item, "a", attrs = {"class": "title"})
                name += client.parseDOM(item, "a", attrs = {"class": "title threadtitle_unread"})
                if type(name) is list:
                    name = name[0]
                url = client.parseDOM(item, "a", ret="href")
                if type(url) is list:
                    url = url[0]
                if "Online" not in name: continue
                name = name.replace(title, '')
                if not title == 'awards'  :
                    try :
                        name = re.compile('([\d{1}|\d{2}]\w.+\d{4})').findall(name)[0]
                    except:
                        pass
                name = name.strip()
                try :
                    season = title.lower()
                    season = re.compile('[0-9]+').findall(season)[0]
                except :
                    season = '0'
                episodes.append({'season':season, 'tvshowtitle':title, 'title':name, 'name':name,'url' : url, 'provider':'desirulez', 'tvshowurl':tvshowurl})

            next = client.parseDOM(rawResult, "span", attrs={"class": "prev_next"})
            next = client.parseDOM(next, "a", attrs={"rel": "next"}, ret="href")[0]
            episodes[0].update({'next':next})

        except Exception as e:
            logger.error(e)

        logger.debug(episodes, __name__)
        return episodes