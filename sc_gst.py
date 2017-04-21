# -*- coding: utf-8 -*-

# Copyright 2012 Activity Central, Inc., Ariel Calzada - ariel@activitycentral.com
# Copyright 2012 Activity Central, Inc., Flavio Danesse - flavio@activitycentral.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# gobject used for subclassing and finally for managing signals
import gobject

# gstreamer
import gst

# os
import os

# time lib used for saving time of video
import time

class ScreencastGstreamer(gobject.GObject):

    __gsignals__ = {
    "update-info": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,gobject.TYPE_STRING,))
    }

    def __init__(self, videofile):
        """ Constructor
        """
        
        super(ScreencastGstreamer, self).__init__()
        
        self._audioitems = False
        self._startclock = False
        self._videofile = videofile
        self._pipeline = False
        self._timer = False
        self._oggmux = False
        self._videoitems = False
        self._filesink = False

    def stop(self):
        """ Stop recording
        """
        
        if self._timer:
            gobject.source_remove(self._timer)
            self._timer = False
            
        self._pipeline.set_state(gst.STATE_PAUSED)
        self._pipeline.set_state(gst.STATE_NULL)

    def start(self, recordsound):
        """ Start recording
        """
        
        if self._pipeline:
            del(self._pipeline)
            
        if self._timer:
            gobject.source_remove(self._timer)
            self._timer = None
            
        self.createPipeline()
        
        self.addItems(recordsound)
        self.linkItems(recordsound)
        
        self._pipeline.set_state(gst.STATE_PLAYING)
        self._startclock = time.time()
        self._timer = gobject.timeout_add(1000, self.updateInfo)

    def addItems(self, recordsound):
        """ Add items to pipeline
        """

        for videoitem in self._videoitems:
            self._pipeline.add(videoitem)

        if recordsound:
            for audioitem in self._audioitems:
                self._pipeline.add(audioitem)

        self._pipeline.add(self._oggmux)
        self._pipeline.add(self._filesink)

    def linkItems(self, recordsound):
        """ Link items to pipeline
        """

        if recordsound:
            l1 = self._videoitems
            l1.append(self._oggmux)
            gst.element_link_many(*l1)

            l2 = self._audioitems
            l2.append(self._oggmux)
            gst.element_link_many(*l2)

            gst.element_link_many(
                self._oggmux,
                self._filesink
            )

        else:
            l = self._videoitems
            l.append(self._oggmux)
            l.append(self._filesink)
            gst.element_link_many(*l)


    def updateInfo(self):
        """ Update info
        """
        
        videofilesize = "0 Kb"
        videolength = "%s s" % ( int(time.time() - self._startclock))

        if os.path.exists(self._videofile):
            videofilesize = "%s Kb" % ( int(int(os.path.getsize(self._videofile)) / 1024))

        self.emit('update-info', videofilesize, videolength)

        return True


    def createVideoItems(self):
        """ Create video items
        """
        
        ximagesrc = gst.element_factory_make('ximagesrc', "ximagesrc")
        ximagesrc.set_property('startx', 0)
        ximagesrc.set_property('endx', 1200)
        ximagesrc.set_property('starty', 0)
        ximagesrc.set_property('endy', 900)

        ffmpegcolorspace = gst.element_factory_make('ffmpegcolorspace', "ffmpegcolorspace")

        videoscale = gst.element_factory_make("videoscale", "videoscale")

        videocaps = gst.element_factory_make("capsfilter", "videocapsfilter")
        videocaps.set_property("caps", gst.Caps("video/x-raw-yuv,width=640,height=480"))

        theoraenc = gst.element_factory_make('theoraenc', 'theoraenc')

        videoqueue = gst.element_factory_make('queue', "videoqueue")
        videoqueue.set_property('max-size-buffers', 8000)
        videoqueue.set_property('max-size-bytes', 0)
        videoqueue.set_property('max-size-time', 0)

        self._videoitems = [ ximagesrc, ffmpegcolorspace, videoscale, videocaps, theoraenc, videoqueue ]

    def createAudioItems(self):
        """ Create audio items
        """

        autoaudiosrc = gst.element_factory_make('autoaudiosrc', "autoaudiosrc")

        audiorate = gst.element_factory_make("audiorate", "audiorate")
        audiorate.set_property('silent', True)
        audiorate.set_property('tolerance', 1000)

        audiocaps = gst.element_factory_make("capsfilter", "audiocapsfilter")
        audiocaps.set_property("caps", gst.Caps("audio/x-raw-int,rate=8000,channels=1,width=16,depth=16"))

        audioconvert = gst.element_factory_make('audioconvert', "audioconvert")

        vorbisenc = gst.element_factory_make('vorbisenc', "vorbisenc")

        soundqueue = gst.element_factory_make('queue', "audioqueue")
        soundqueue.set_property('max-size-buffers', 10000)
        soundqueue.set_property('max-size-bytes', 0)
        soundqueue.set_property('max-size-time', 0)

        self._audioitems = [ autoaudiosrc, audiorate, audiocaps, audioconvert, vorbisenc, soundqueue ]

    def createPipeline(self):
        """ Create pipeline

            gst-launch-0.10 ximagesrc startx=0 endx=1200 starty=0 endy=900 ! \
               ffmpegcolorspace ! \
               videoscale ! \
               video/x-raw-yuv,width=640,height=480 ! \
               theoraenc ! \
               queue max-size-buffers=10000 max-size-bytes=0 max-size-time=0 ! \
               mux. oggmux name=mux \
               autoaudiosrc ! \
               audiorate silent=True tolerance=1000 ! \
               audio/x-raw-int,width=16,depth=16,rate=8000,channels=1 ! \
               audioconvert ! \
               vorbisenc ! \
               queue max-size-buffers=10000 max-size-bytes=0 max-size-time=0 ! \
               mux. mux. ! \
               filesink location=video.ogg
        """
        
        self._pipeline = gst.Pipeline("player")
        
        self.createVideoItems()
        self.createAudioItems()
        
        self._oggmux = gst.element_factory_make('oggmux', "oggmux")
        self._filesink = gst.element_factory_make('filesink', "filesink")
        self._filesink.set_property("location", self._videofile)
