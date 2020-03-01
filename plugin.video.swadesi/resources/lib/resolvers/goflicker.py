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

import re

from aftershock.common import client, logger

def resolve(url):
    try:
        result = client.request(url)

        url = re.findall('sources: \[(.+?)\]',result)[0]
        url = url.split(',')
        for i in url:
            i = i.replace('\"','')
            if 'mp4' in i:
                url = i;
                break ;
        logger.debug('URL [%s]' % url, __name__)
        return url
    except Exception as e:
        return False