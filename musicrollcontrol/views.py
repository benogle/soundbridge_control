'''
Copyright (c) 2009 Ben Ogle

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
'''

from django.template import Context, loader
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson as json
from django import forms

from django.core.urlresolvers import reverse

import roku
import cache

from datetime import datetime
import logging

def _roku():
    r = roku.Roku(settings.ROKU_SERVER)
    r.playlists
    
    if r.current_server_info == 'ErrorDisconnected':
        r.servers
        r.disconnect_server()
        r.connect_server(0)
        
    return r

def _roku_song_data():
    return cache.get_roku_cache(_roku)

def _render(path, ctx):
    t = loader.get_template(path)
    c = Context(ctx)
    return t.render(c)
    
def _get_playlist_data():
    r = _roku_song_data()
    
    cursong = r['current_song_info']
    if not 'title' in cursong: cursong = None
    
    curi = r['current_index']
    if curi != None:
        curi += 1
        
    return _render('playlist.html', {
        'current_song': cursong,
        'songs': r['queue'],
        'current_index': curi,
        'current_server': r['current_server_info']['Name']
    })


def index(req):
    r = _roku()
    
    srv_name = r.current_server_info['Name']
    
    servers = r.servers
    servers = [ {'index': i, 'name': servers[i]} for i in range(len(servers)) if servers[i] != srv_name ]
    
    artists = None
    if srv_name != 'Internet Radio': #otherwise it _hangs_ Ugh.
        artists = r.list_artists()
        
        if type(artists) is str: #curb the 'GenericError' BS that occasionally happens.
            artists = None
    
    data = {
        'artists': artists,
        'server_name': r.current_server_info['Name'],
        'playlist': _get_playlist_data(),
        'servers': servers,
        'volume': r.volume
    }
    
    return render_to_response('index.html', data)
    
def getplaylist(req):
    
    data = {
        'status': 'success',
        'playlist': _get_playlist_data()
    }
    
    return HttpResponse(json.dumps(data))
    
def filtersongs(req):
    r = _roku()
    
    ret = {
        'status': 'fail',
        'albums': [],
        'songs': [] 
    }
    
    if 'artist' in req.POST:
        art = req.POST['artist']
        
        album = None
        if 'album' in req.POST and req.POST['album'] != 'all albums':
            album = req.POST['album']
        
        if album:
            albums = None
            songs = r.list_songs_for_album(art, album)
        else:
            albums = r.list_albums_for_artist(art)
            songs = r.list_songs_for_artist(art)
        
        ret = {
            'status': 'success',
            'albums': albums,
            'songs': _render('songs.html', {'songs':songs}) 
        }
        
    return HttpResponse(json.dumps(ret))
    
def filteraction(req):
    
    r = _roku()
    
    ret = {
        'status': 'fail'
    }
    
    if 'artist' in req.POST and 'action' in req.POST:
        action = req.POST['action']
        art = req.POST['artist']
        
        index = 0
        if 'index' in req.POST:
            index = int(req.POST['index'])
        
        album = None
        if 'album' in req.POST and req.POST['album'] != 'all albums':
            album = req.POST['album']
        
        #the songs resulting from the following query will be acted on by the actions.
        if album:
            songs = r.list_songs_for_album(art, album)
        else:
            songs = r.list_songs_for_artist(art)
        
        if action == 'playall':
            r.play_all(index) #play all from index
        elif action == 'enqueueall':
            r.enqueue_all() #enqueue all 
        elif action == 'enqueue':
            r.enqueue(index)
        
        ret['status'] = 'success'
        
    return HttpResponse(json.dumps(ret))
    

def playlistaction(req):
    r = _roku()
    
    ret = {
        'status': 'fail'
    }
    
    if 'action' in req.POST:
        action = req.POST['action']
        
        index = None
        if 'index' in req.POST:
            try:
                index = int(req.POST['index'])
            except:
                pass
        
        if action == 'play':
            r.play(index)
        elif action == 'stop':
            r.stop()
        elif action == 'next':
            r.next()
        elif action == 'prev':
            r.previous()
        elif action == 'pause':
            r.pause()
        elif action == 'clear':
            r.clear_queue()
        elif action == 'remove' and index != None:
            r.remove(index)
            
        ret['status'] = 'success'
        
    return HttpResponse(json.dumps(ret))
    
def volume(req):
    r = _roku()
    
    ret = {'volume': 0}
    if 'val' in req.POST:
        
        try:
            val = int(req.POST['val'])
        except:
            val = 0
            
        vol = r.volume + val
    
        vol = max(0, min(100, vol))
        
        r.volume = vol
        
        ret['volume'] = vol
        
    return HttpResponse(json.dumps(ret))
    
def serverconnect(req):
    r = _roku()
    
    if 'server' in req.POST:
        try:
            index = int(req.POST['server'])
            servers = r.servers
            
            if index < len(servers):
                servers
                r.disconnect_server()
                r.connect_server(index)
                
        except:
            pass
    
    return HttpResponseRedirect('/')
    
    