import memcache
import hashlib

mc = None

from django.conf import settings

import roku
import logging

def get_memcache_client():
    """
    Don't use this unless you really need to. You should use check_cache.
    """
    global mc
    if not mc:
        # TODO add error checking to make sure memcache loads properly
        #   (right now its silent)
        memcache_servers = settings.MEMCACHE_SERVERS
        memcache_servers = memcache_servers.split(";")

        mc = memcache.Client(memcache_servers, debug=0)

    return mc

def is_enabled():
    return True
    
def get(key):
    """
    Don't use this unless you really need to. You should use check_cache.

    :param key: The string holding the memcache key.

    :return: The value of the key or None if it's not available.
    """
    if not is_enabled():
        return None
    
    global mc

    hashed_key = hashlib.md5(key).hexdigest()
    
    hashed_key = hashed_key.encode('utf-8')

    if mc is None:
        mc = get_memcache_client()

    return mc.get(hashed_key)

def set(key, value, timeout=3600):
    """
    Don't use this unless you really need to. You should use check_cache.

    :param key: The string holding the memcache key.
    :param timeout: The number of seconds to allow the key to be valid.

    :return: Non-zero on success or zero for failure.
    """
    if not is_enabled():
        print 'Attempting to cache %s, but caching is disabled. Set cache var in your ini to true to enable.' % key
        return True
    
    global mc
    
    hashed_key = hashlib.md5(key).hexdigest()
    
    hashed_key =hashed_key.encode('utf-8')
    if mc is None:
        mc = get_memcache_client()
    
    success = mc.set(hashed_key, value, timeout)
    if not success:
        print "Could not set key %s in memcache. Is it too large?" % key

    return success

def clear():
    """
    Use this sparingly, if ever. It wipes out all of memcache.
    """
    global mc

    if mc is None:
        mc = get_memcache_client()
    mc.flush_all()

def check_cache(key, func, expires=3600, options={}):
    """
    Checks if memcache has a valid value for the given key, if not execute the
    function and save it.

    Also, it prepends the application version in order to ensure the cache is
    flushed between versions.

    IMPORTANT, caching is only enabled by the pylons configuration variable
    'cache'.

    :param func: A function which returns the value when the value doesn't
        exist or has expired.
    :param expires: Seconds in which the data will expire. (optional)
    :param options: A dictionary of function arguments to pass to the caching
        function.
    """

    val = get(key)
    if not val:
        val = func(**options)
        set(key, val, timeout=expires)
    return val


def get_roku_cache(create_roku_fn):
    def miss():
        r = create_roku_fn()
        return {
            'current_song_info': r.current_song_info,
            'current_index': r.current_index,
            'current_server_info': r.current_server_info,
            'queue': r.queue
        }
    
    return check_cache('roku_song_data', miss, expires=15)
