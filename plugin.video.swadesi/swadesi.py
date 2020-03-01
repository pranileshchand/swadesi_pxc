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

import sys
import urlparse

from aftershock.common import analytics, logger, control

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

logger.debug(params, __name__)

action = params.get('action')
name = params.get('name').decode('UTF-8') if params.get('name') else None
title = params.get('title').decode('UTF-8') if params.get('title') else None
year = params.get('year')
season = params.get('season')
episode = params.get('episode').decode('utf-8') if params.get('episode') else None
tvshowtitle = params.get('tvshowtitle').decode('utf-8') if params.get('tvshowtitle') else None
date = params.get('date')
url = params.get('url')
image = params.get('image')
meta = params.get('meta').decode('utf-8') if params.get('meta') else None
query = params.get('query')
source = params.get('source')
content = params.get('content')
provider = params.get('provider')
genre = params.get('genre')
lang = params.get('lang')

imdb = '0' if params.get('imdb') == None else params.get('imdb')
tvdb = '0' if params.get('tvdb') == None else params.get('tvdb')

select = '1' if params.get('select') == None else params.get('select')

if action == None:
    from resources.lib.indexers import navigator
    navigator.navigator().root()

elif action == 'movieLangNavigator':
    from resources.lib.indexers import movies
    movies.movies().languages()

elif action == 'movieLangHome':
    from resources.lib.indexers import movies
    movies.movies().home(lang=lang)

elif action == 'movieLangGenre':
    from resources.lib.indexers import movies
    movies.movies().genres(lang=lang)

elif action == 'movieLangYears':
    from resources.lib.indexers import movies
    movies.movies().years(lang=lang)

elif action == 'movies':
    from resources.lib.indexers import movies
    #analytics.sendAnalytics('%s-%s' % (action, lang))
    movies.movies().get(url, lang=lang)

elif action == 'movieSearch':
    from resources.lib.indexers import movies
    movies.movies().search(query, lang)

elif action == 'desiTVNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().desiTV()

elif action == 'artwork':
    control.artwork()

elif action == 'tvshows':
    from resources.lib.indexers import tvshows
    #analytics.sendAnalytics('%s-%s' % (action, name))
    tvshows.tvshows().get(url, provider=provider, network=name)

elif action == 'seasons':
    from resources.lib.indexers import episodes
    episodes.seasons().get(tvshowtitle, year, imdb, tvdb)

elif action == 'episodes':
    from resources.lib.indexers import episodes
    #analytics.sendAnalytics('%s-%s' % (action, tvshowtitle))
    episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season, episode, provider=provider, url=url)

elif action == 'addItem':
    from resources.lib.sources import sources
    sources().addItem(title, content)

elif action == 'download':
    import json
    from resources.lib.sources import sources
    from aftershock.common import downloader
    try: downloader.download(name, image, sources().sourcesResolve(json.loads(source)[0]))
    except: pass

elif action == 'play':
    from resources.lib.sources import sources
    sources().play(name, title, year, imdb, tvdb, season, episode, tvshowtitle, date, meta, url, select)

elif action == 'playItem':
    from resources.lib.sources import sources
    sources().playItem(content, title, source)

elif action == 'trailer':
    from aftershock.common import trailer
    trailer.trailer().play(name, url)

elif action == 'addView':
    from aftershock.common import views
    views.addView(content)

elif action == 'refresh':
    control.refresh()

elif action == 'queueItem':
    control.queueItem()

elif action == 'moviePlaycount':
    from aftershock.common import playcount
    playcount.movies(title, year, imdb, query)

elif action == 'episodePlaycount':
    from aftershock.common import playcount
    playcount.episodes(imdb, tvdb, season, episode, query)

elif action == 'tvPlaycount':
    from aftershock.common import playcount
    playcount.tvshows(name, year, imdb, tvdb, season, query)

elif action == 'alterSources':
    from resources.lib.sources import sources
    sources().alterSources(url, meta)

elif action == 'openSettings':
    control.openSettings(query)

elif action == 'clearCache':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCache(url)

elif action == 'changelog':
    from aftershock.common import changelog
    changelog.get('1')
elif action == 'tools':
    from resources.lib.indexers import navigator
    navigator.navigator().tools()
elif action == 'urlresolversettings' :
    import urlresolver
    urlresolver.display_settings()