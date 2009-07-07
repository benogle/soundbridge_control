from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'rokucontrol.musicrollcontrol.views.index', name="index"),
    
    url(r'^filtersongs$', 'rokucontrol.musicrollcontrol.views.filtersongs', name="filtersongs"),
    url(r'^serverconnect$', 'rokucontrol.musicrollcontrol.views.serverconnect', name="serverconnect"),
    url(r'^filteraction$', 'rokucontrol.musicrollcontrol.views.filteraction', name="filteraction"),
    
    url(r'^getplaylist$', 'rokucontrol.musicrollcontrol.views.getplaylist', name="getplaylist"),
    
    url(r'^playlistaction$', 'rokucontrol.musicrollcontrol.views.playlistaction', name="playlistaction"),
    
    url(r'^volume$', 'rokucontrol.musicrollcontrol.views.volume', name="volume"),
)
