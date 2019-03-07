# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta
from caldav.elements import dav, cdav
import caldav, vobject, requests, locale

from config import calendar_url, calendar_name, mattermost_url, icon_url, username, channel
"""
config.py:

# Caldav config
calendar_url = 'https://user:passwd@host/remote.php/dav/'
calendar_name = '...'

# Mattermost config
mattermost_url = '...'  # incoming webhook(non-personal, needs to be created by an admin)
icon_url = '...'        # URL of Icon that should be used for posts
username = '...'        # Username the Bot should use
channel = '...'         # Channel that events shall be posted to
"""

locale.setlocale(locale.LC_ALL, '')

def post_message(message, channel, username, icon_url):
    data = '{"text": "%s", "channel": "%s", "username": "%s", "icon_url": "%s"}' % (message.encode('ascii', 'xmlcharrefreplace'), escape(channel), escape(username), icon_url)
    response = requests.post(mattermost_url, data=data, headers={'Content-Type': 'application/json'})
    response.raise_for_status()

def escape(data):
    result = ''
    for symbol in data:        
        codepoint = ord(symbol)
        if codepoint > 127:
            result += '\\u%04x' % codepoint
        else:
            result += symbol
    return result

client = caldav.DAVClient(calendar_url)
principal = client.principal()

now = datetime.now()
then = now + timedelta(days=1)

for calendar in principal.calendars():    
    if calendar.name == calendar_name: 
        for event in calendar.date_search(now, then):
            vcalobj = vobject.readOne(event.data)
            title = vcalobj.vevent.summary.value
            description = '_keine weitere Beschreibung..._'
            if hasattr(vcalobj.vevent, 'description'):
                description = vcalobj.vevent.description.value
            date = escape(vcalobj.vevent.dtstart.value.strftime('%d. %B'))
            message = 'Geplant am %s:\n%s\n%s' %(date, title, description)
            post_message(message, channel, username, icon_url)

    