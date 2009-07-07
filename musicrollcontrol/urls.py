from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'soundbridge_control.musicrollcontrol.views.index', name="index"),
    
    url(r'^filtersongs$', 'soundbridge_control.musicrollcontrol.views.filtersongs', name="filtersongs"),
    url(r'^serverconnect$', 'soundbridge_control.musicrollcontrol.views.serverconnect', name="serverconnect"),
    url(r'^filteraction$', 'soundbridge_control.musicrollcontrol.views.filteraction', name="filteraction"),
    
    url(r'^getplaylist$', 'soundbridge_control.musicrollcontrol.views.getplaylist', name="getplaylist"),
    
    url(r'^playlistaction$', 'soundbridge_control.musicrollcontrol.views.playlistaction', name="playlistaction"),
    
    url(r'^volume$', 'soundbridge_control.musicrollcontrol.views.volume', name="volume"),
)
