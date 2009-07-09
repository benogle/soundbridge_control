'''
Copyright (c) 2009 Mitch Walker, Ben Ogle

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

import socket
import re

READ_CHUNK = 4096

class Rcp(object):
    buffer = ''
    def __init__(self, hostname, port=5555):
        self.connect(hostname, port)

    def connect(self, hostname, port):
        self.wire = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.wire.connect((hostname, port))

    def write(self, s):
        self.wire.send(s)

    def read(self, command='', expect_dict=False):
        if expect_dict:
            # Multiline responses without ListResult or Transaction bookends
            d = {}
            line = self.read_line(command)
            
            if line == 'ErrorDisconnected':
                return line
            
            while line != 'OK':
                key, value = line.split(': ', 1)
                d[key] = value
                line = self.read_line(command)
            return d

        transaction = False
        line = self.read_line(command)
        if line == 'TransactionInitiated':
            transaction = True
            line = self.read_line(command)
            
        result_list = re.search('ListResultSize\s+(\d+)', line)
        if result_list:
            result = []
            list_size = int(result_list.group(1))
            for i in xrange(0,list_size):
                result.append(self.read_line(command))
            self.read_line(command)
            if transaction:
                self.read_line(command)
            return result
        elif transaction:
            nline = self.read_line(command)
            while not 'TransactionComplete' in nline:
                line.append('\n%s' % nline)
                nline = self.read_line(command)
                
        return line

    def read_line(self, command=''):
        response = self.buffer
        while not response.endswith('\r\n'):
            response += self.wire.recv(READ_CHUNK)
        (response, overread) = response.split('\r\n', 1)
        self.buffer = overread
        if command and response.startswith(command):
            response = re.sub('^%s: ' % command, '', response)
        return response

    def command(self, c, **kw):
        self.write(c + '\r\n')
        
        #grab the command name
        if ' ' in c:  c, args = c.split(' ', 1)
        
        response = self.read(c, **kw)
        return response            

    def close(self):
        self.command('Exit')
        self.wire.close()

class Sketch:
    def __init__(self, hostname, port=4444):
        self.connect(hostname, port)
        self.command('sketch')

    def connect(self, hostname, port):
        self.wire = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.wire.connect((hostname, port))

    def command(self, command):
        self.wire.send(command+'\r\n')
        self.wire.recv(READ_CHUNK)

    def __del__(self):
        self.command('exit')
        self.wire.close()

class Roku(Rcp):
    FILTER_ARTIST = 0
    FILTER_ALBUM = 1
    
    _BROWSE_FILTERS = {
        FILTER_ARTIST: 'SetBrowseFilterArtist',
        FILTER_ALBUM: 'SetBrowseFilterAlbum'
    }
    
    def __init__(self, hostname, port=5555, port_sketch=4444, sketch=False):
        super(self.__class__, self).__init__(hostname, port)
        self.read()
        
        if sketch:
            init_sketch()
            
        self.command('GetConnectedServer')

    def init_sketch(self):
        self.sketch = Sketch(hostname, port_sketch)

    def text(self, message):
        self.sketch.command('text 0 5 "%s"' % message.replace('"', '\"'))

    def scroll(self, message):
        self.sketch.command('marquee -start "%s"' % message.replace('"', "''"))

    def pixel(self, x, y, color=1):
        self.sketch.command('color %d' % color)
        self.sketch.command('point %d %d' % (x,y))

    def get_volume(self):
        return int(self.command('GetVolume'))

    def set_volume(self, volume):
        return self.command('SetVolume %d' % int(volume))
        
        
    def _song_list(self, songs):
        return [ {'index': i, 'title': songs[i]} for i in range(len(songs)) ]

    def next(self):
        return self.command('Next')
        
    def previous(self):
        return self.command('Previous')

    def stop(self):
        return self.command('Stop')
        
    def pause(self):
        return self.command('Pause')

    def play(self, n=None):
        if n != None:
            return self.command('PlayIndex %d' % n)
        else:
            return self.command('Play')


    def play_all(self, n):
        return self.command('QueueAndPlay %d' % n)
        
    def enqueue_all(self):
        return self.command('NowPlayingInsert all')
    
    def enqueue(self, n):
        return self.command('NowPlayingInsert %d' % n)
        
    def clear_queue(self):
        return self.command('NowPlayingClear')
        
    def remove(self, n):
        return self.command('NowPlayingRemoveAt %d' % n)
        
    @property
    def current_song_info(self):
        return self.command('GetCurrentSongInfo', expect_dict=True)

    @property
    def queue(self):
        songs = self.command('ListNowPlayingQueue')
        
        return self._song_list(songs)
        
    @property
    def current_index(self):
        ind = self.command('GetCurrentNowPlayingIndex')
        try:
            ind = int(ind)
            return ind
        except:
            return None

    @property
    def q(self):
        return self.queue

    @property
    def shuffle(self):
        return self.command('Shuffle')

    def set_shuffle(self, n):
        return self.command('Shuffle %s' % n and 'on' or 'off')



    @property
    def servers(self):
        servers = self.command('ListServers')
        return servers
    
    @property
    def current_server_capabilities(self):
        return self.command('ServerGetCapabilities', expect_dict=True)

    @property
    def current_server_info(self):
        return self.command('GetActiveServerInfo', expect_dict=True)
        
    def disconnect_server(self):
        return self.command('ServerDisconnect')

    def connect_server(self, n):
        return self.command('ServerConnect %d' % n)



    @property
    def playlists(self):
        return self.command('ListPlaylists')

    def playlist_songs(self, n):
        return self.command('ListPlaylistSongs %d' % n)
        
        

    def set_browse_filter(self, filter_type, filter):
        if filter_type in self._BROWSE_FILTERS:
            self.command('%s %s' % (self._BROWSE_FILTERS[filter_type], filter))
    
    def list_songs(self):
        return self.command('ListSongs')
        
    def list_artists(self):
        return self.command('ListArtists')
    
    def list_albums(self):
        return self.command('ListAlbums')
    
    def list_albums_for_artist(self, artist):
        self.set_browse_filter(self.FILTER_ARTIST, artist)
        return self.list_albums()
        
    def list_songs_for_artist(self, artist):
        """
        Make tons of API calls and a bunch of looping because the API sucks.
        I just want the album name! Fuckers.
        """
        self.set_browse_filter(self.FILTER_ARTIST, artist)
        albums = self.list_albums()
        
        #this little reverse lookup breaks if there are multiple songs with
        #the same name in different albums. Poop.
        rlook = {}
        for a in albums:
            songs = self.list_songs_for_album(artist, a)
            for s in songs:
                rlook[s['title']] = a
        
        #do this last so we can do an enqueue if we want after calling this fn
        self.set_browse_filter(self.FILTER_ARTIST, artist)
        songs = self._song_list(self.list_songs())
        
        for s in songs:
            title = s['title']
            if title in rlook:
                s['album'] = rlook[title]
            else:
                s['album'] = 'Unknown album'
            
        return songs
    
    def list_songs_for_album(self, artist, album):
        self.set_browse_filter(self.FILTER_ARTIST, artist)
        self.set_browse_filter(self.FILTER_ALBUM, album)
        
        songs = self.list_songs()
        
        return self._song_list(songs)

    volume = property(get_volume, set_volume)

if __name__ == '__main__':
    r = Roku('192.168.1.103')
    r.playlists
    
    servers = r.servers
    
    import sys
    
    print servers
    print r.disconnect_server()
    print r.connect_server(int(sys.argv[1]))
    
    
    