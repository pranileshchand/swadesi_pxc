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

import urllib
import urlparse

from aftershock.common import client, logger

import urlresolver

def request(url, allowDebrid=False):
    try:
        tUrl = url.split('##')
        if len(tUrl) > 0:
            url = tUrl
        else :
            url = urlparse.urlparse(url).path

        links = []
        for item in url:
            r = resolve(item, allowDebrid=allowDebrid)
            if not r :
                raise Exception()
            links.append(r)
        url = links
        return url
    except:
        return False

def resolve(url, allowDebrid=False):
    u = url
    url = False
    # Custom Resolvers
    try:
        host = client.host(u)

        r = [i['class'] for i in info() if host in i['host']][0]
        r = __import__(r, globals(), locals(), [], -1)
        url = r.resolve(u)
        if url == False:
            raise Exception()
    except:
        pass

    # URLResolvers
    try:
        if not url == False : raise Exception()
        logger.debug('Trying URL Resolver for %s' % u, __name__)
        hmf = urlresolver.HostedMediaFile(url=u, include_disabled=True, include_universal=allowDebrid)
        if hmf.valid_url() == True: url = hmf.resolve()
        else: url = False
    except:
        pass

    try: headers = url.rsplit('|', 1)[1]
    except: headers = ''
    headers = urllib.quote_plus(headers).replace('%3D', '=').replace('%26','&') if ' ' in headers else headers
    headers = dict(urlparse.parse_qsl(headers))

    if url.startswith('http') and '.m3u8' in url:
        result = client.request(url.split('|')[0], headers=headers, output='geturl', timeout='20')
        if result == None: raise Exception()

    elif url.startswith('http'):

        result = client.request(url.split('|')[0], headers=headers, output='chunk', timeout='20')
        if result == None:
            logger.debug('Resolved %s but unable to play' % url, __name__)
            raise Exception()

    return url

def info():
    return [
        {'class': 'desiflicks', 'host': ['desiflicks.com']}
        , {'class': 'playwire', 'host': ['playwire.com']}
        , {'class': 'xpressvids', 'host': ['xpressvids']}
        , {'class': 'apnasave', 'host': ['apnasave.in']}
        , {'class': 'ditto', 'host': ['dittotv.com']}
        , {'class': 'dynns', 'host': ['dynns.com']}
        , {'class': 'dailymotion', 'host': ['dailymotion.com']}
        , {'class': 'goflicker', 'host': ['goflicker.com']}
        , {'class': 'genericresolver', 'host': ['playu.net', 'watchify.com', 'watchvideo13.us', 'vidwatch.me','vidshare.us', 'idowatch.us', 'tvlogy.to',  'speedplay.pw', 'speedwatch.us', 'embedupload.com', 'fifastop.com']}
    ]