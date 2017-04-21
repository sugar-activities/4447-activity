# -*- coding: utf-8 -*-

# Copyright 2008 Chris Ball.
# Copyright 2012 Activity Central, Inc., Rafael Ortiz - rafael@activitycentral.com
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

# Activity base class
from sugar.activity import activity

# User interface
import sc_ui

# Gstreamer interface
import sc_gst

# os
import os

# bundlepath
from sugar.activity.activity import get_activity_root

# datetime for journal entry name
import datetime

# i18n
import i18n

class ScreencastActivity(activity.Activity):

    def __init__(self, handle):
        """ Constructor
        """
        # Call super class "Activity" constructor method
        super(ScreencastActivity, self).__init__(handle)
        
        # User interface object
        self._ui = sc_ui.ScreencastUserInterface(self)

        # Set video file
        directory = os.path.join(get_activity_root(), "data")
        if not os.path.exists(directory):
            os.makedir(directory)

        self._videofile =  os.path.join( directory, "screencast.ogg" )

        # Gstreamer interface object
        self._gst = sc_gst.ScreencastGstreamer(self._videofile)

        # State
        self._state = "stopped"

        # Connect user interface signals
        self._ui.connect('recordbutton-clicked', self.recordbuttonClicked)
        self._ui.connect('stopbutton-clicked', self.stopbuttonClicked)

        # Connect gstreamer interface signals
        self._gst.connect('update-info', self.updateInfo)

        # Show user interface
        self._ui.showInterface()

    def recordbuttonClicked(self, widget):
        """ Record button clicked
        """
        self._state = "recording"
        self._ui.changeButtonsState(self._state)
        self._gst.start(self._ui.getRecordSoundOption())

    def stopbuttonClicked(self, widget):
        """ Stop button clicked
        """
        self._state = "stopped"
        self._ui.changeButtonsState(self._state)
        self._gst.stop()

    def updateInfo(self, widget, videosize, videolength):
        """ Update info
        """
        self._ui.refreshLabelRecordText(videosize, videolength)

    def write_file(self, filePath):
        """ Send file to journal
        """

        if os.path.exists(self._videofile) and self._state == "stopped":
            self.metadata['mime_type'] = 'video/ogg'

            if self._jobject.metadata['title_set_by_user'] == '1':
                title = self.metadata['title']
            else:
                title = "My Screencast video " + datetime.datetime.now().strftime("%Y%m%d%H%M%s")

            cmd = "copy-to-journal %s -m video/ogg -t \"%s\"" % ( self._videofile, title )
            os.system(cmd)

    def can_close(self):
        """ Close hook
        """
        if self._state == "stopped":
            return True

        self._ui.alert(i18n.I18N_EXIT_ALERT)
        return False

    def flush_events(self):
        """ Wait for graphics events finish
        """
        gtk.gdk.threads_enter()
        while gtk.events_pending():
            gtk.main_iteration(True)
        gtk.gdk.flush()
        gtk.gdk.threads_leave()
