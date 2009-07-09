/**
 * .disableTextSelect - Disable Text Select Plugin
 *
 * Version: 1.0
 * Updated: 2007-08-11
 *
 * Used to stop users from selecting text
 *
 * Copyright (c) 2007 James Dempster (letssurf@gmail.com, http://www.jdempster.com/category/jquery/disabletextselect/)
 *
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 **/
(function($) {
    if ($.browser.mozilla) {
        $.fn.disableTextSelect = function() {
            return this.each(function() {
                $(this).css({
                    'MozUserSelect' : 'none'
                });
            });
        };
    } else if ($.browser.msie) {
        $.fn.disableTextSelect = function() {
            return this.each(function() {
                $(this).bind('selectstart', function() {
                    return false;
                });
            });
        };
    } else {
        $.fn.disableTextSelect = function() {
            return this.each(function() {
                $(this).mousedown(function() {
                    return false;
                });
            });
        };
    }
})(jQuery);

/*
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
*/

//bens stuff
$(document).ready(function(){
    
    function bindActions(){
        
        function actOnFoundSongs(index, action){
            $('#song-index').val(index);
            var params = $('#filterform').formSerialize();
            
            $.post('/filteraction', params + '&action=' + action);
            
            refreshPlaylist();
            
            return false;
        }
        
        //bind the action links like play all, enqueue all, etc
        $('#action-play-all').click(function(){
            return actOnFoundSongs(0, 'playall');
        });
        
        $('#action-enqueue-all').click(function(){
            return actOnFoundSongs(0, 'enqueueall');
        });
        
        $('.action-enqueue').click(function(){
            var index = $(this).attr('index');
            return actOnFoundSongs(index, 'enqueue');
        });
    }
    
    function sendPlaylistAction(index, action, doRefresh){
        var params = {action: action}
        if(index != null)
            params.index = index
            
        $.post('/playlistaction', params, function(){
            if(doRefresh)
                refreshPlaylist();
        }, 'json');
        
        return false;
    }
    
    function bindPlaylistActions(){
        
        // do the bindage
        $('.action-remove').click(function(){
            return sendPlaylistAction($(this).attr('index'), 'remove', true);
        });
        
        $('#action-clear-playlist').click(function(){
            if(confirm('Are you totally completely absolutely like really really sure you want to clear the entire playlist?'))
                return sendPlaylistAction(null, 'clear', true)
            return false;
        });
        
        $('#playlist .song .title').bind('dblclick', function(){
            
            $('#playlist-list .song').removeClass('current-index');
            $(this).parent().addClass('current-index');
            
            var index = $(this).attr('index');
            return sendPlaylistAction(index, 'play', false);
        });
        
        $('#playlist-list .title').disableTextSelect();
    }
    
    function bindPlaylistControls(){
        $('#action-prev').click(function(){
            return sendPlaylistAction(null, 'prev', false);
        });
        
        $('#action-play').click(function(){
            return sendPlaylistAction(null, 'play', true);
        });
        
        $('#action-pause').click(function(){
            return sendPlaylistAction(null, 'pause', false);
        });
        
        $('#action-stop').click(function(){
            return sendPlaylistAction(null, 'stop', true);
        });
        
        $('#action-next').click(function(){
            return sendPlaylistAction(null, 'next', false);
        });
        
        function setVolume(val){
            var param = {val: val}
            
            $.post('/volume', param, function(data){
                $('#volume-label').text(data.volume+"%");
            }, 'json');
            
            return false;
        }
        
        $('#volume-up').click(function(){
            return setVolume('5');
        })
        
        $('#volume-down').click(function(){
            return setVolume('-5');
        })
    }
    
    function refreshPlaylist() {
        $.get('/getplaylist', {}, function(data){
            
            if(data && data.status == 'success'){
                $('#playlist-data').html(data.playlist);
                bindPlaylistActions();
            }
            
        }, 'json');
    }
    
    $('#filterform').ajaxForm({
        dataType: 'json',
        success: function(data){
            if(data.albums){
                var art = $('#album')
                art.html('<option selected="selected">all albums</option>');
                for(var i = 0; i < data.albums.length; i++)
                    art.append('<option>'+data.albums[i]+'</option>');
            }
            
            $('#songs').html(data.songs);
            
            bindActions();
        }
    });
    
    $('#artist').change(function(){
        $("#album option:eq(0)").attr("selected", "selected"); //select the 'all albums'
        $('#filterform').submit();
    });
    
    $('#album').change(function(){
        $('#filterform').submit();
    });
    
    
    $('#filterform').submit();
    bindPlaylistActions();
    bindPlaylistControls();
    setInterval(refreshPlaylist, 10000);
    
    $('#serverform').submit(function(){
        return confirm("You _really_ want to switch library servers??");
    });
    
});