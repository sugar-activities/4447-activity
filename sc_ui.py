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

# gobject used for subclassing and finally for managing signals
import gobject

# Toolbar
from sugar.activity.activity import ActivityToolbox

# i18n
import i18n

# gtk
import gtk

# Alert popup
from sugar.graphics.alert import NotifyAlert

class ScreencastUserInterface(gobject.GObject):

    __gsignals__ = {
    'recordbutton-clicked': (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, ()),
    'stopbutton-clicked': (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, ())}

    def __init__(self, activity):
        """ Constructor
        """
        super(ScreencastUserInterface, self).__init__()

        self._toolbox = None
        self._toolbar = None
        self._recordbutton = None
        self._stopbutton = None
        self._buttonsbox = None
        self._box = None
        self._boxalign = None
        self._checkbox = None
        self._label = None
    
        self._activity = activity
        
        # Widgets
        self.buildToolbar()
        self.buildButtons()
        self.buildCheckbox()
        self.buildLabel()

        # Main box
        self._box = gtk.VBox(spacing=20)
        self._box.pack_start(self._buttonsbox)
        self._box.pack_start(self._checkbox)
        self._box.pack_start(self._label)

        # Align box
        self._boxalign = gtk.Alignment(0.5, 0.5, 0, 0)
        self._boxalign.add(self._box)

        # Set canvas with box alignment
        self._activity.set_canvas(self._boxalign)

    def buildToolbar(self):
        """ Build GUI Toolbar
        """
        self._toolbox = ActivityToolbox(self._activity)
        self._toolbar = self._toolbox.get_activity_toolbar()

        # Remove share button
        self._toolbar.remove(self._toolbar.share)
        self._toolbar.share = None

        self._activity.set_toolbox(self._toolbox)

        # we do not have collaboration features
        # make the share option insensitive
        self._activity.max_participants = 1

    def buildButtons(self):
        """ Build buttons
        """
        # Record button
        self._recordbutton = gtk.Button(i18n.I18N_RECORD_BUTTON)
        self._recordbutton.connect("clicked", self.recordbuttonClicked)
        self._recordbutton.set_size_request(150, 150)
        recordbuttonIcon = gtk.Image()
        recordbuttonIcon.set_from_icon_name("media-record", -1)
        self._recordbutton.set_image(recordbuttonIcon)

        # Stop button
        self._stopbutton = gtk.Button(i18n.I18N_STOP_BUTTON)
        self._stopbutton.connect("clicked", self.stopbuttonClicked)
        self._stopbutton.set_size_request(150, 150)
        self._stopbutton.set_sensitive(False)
        stopbuttonIcon = gtk.Image()
        stopbuttonIcon.set_from_icon_name("media-playback-stop", -1)
        self._stopbutton.set_image(stopbuttonIcon)

        # Buttons hbox
        self._buttonsbox = gtk.HBox(spacing=20)
        self._buttonsbox.pack_start(self._recordbutton)
        self._buttonsbox.pack_start(self._stopbutton)

    def buildCheckbox(self):
        """ Build checkbox for display state
        """
        self._checkbox = gtk.CheckButton(label=i18n.I18N_RECORD_SOUND_CHECKBOX)
        self._checkbox.set_active(True)

    def buildLabel(self):
        """ Build label for display state
        """
        self._label = gtk.Label(i18n.I18N_STATUS_STOPPED)

    def recordbuttonClicked(self, widget):
        """ Event click handler
        """
        self.emit('recordbutton-clicked')

    def stopbuttonClicked(self,widget):
        """ Event click handler
        """
        self.emit('stopbutton-clicked')

    def changeLabelText(self, text):
        """ Change text of status label
        """
        self._label.set_text(text)

    def refreshLabelRecordText(self, text1, text2):
        """ Change text of label
        """
        text = i18n.I18N_STATUS_RECORDING + ", " + text1 + ", " + text2
        self.changeLabelText(text)

    def changeButtonsState(self,newstate="recording"):
        """ Change state of the buttons
        """
        if newstate == "recording":
            self._recordbutton.set_sensitive(False)
            self._stopbutton.set_sensitive(True)
            self.changeLabelText(i18n.I18N_STATUS_RECORDING)
            self._checkbox.set_sensitive(False)
        else:
            self._recordbutton.set_sensitive(True)
            self._stopbutton.set_sensitive(False)
            self.changeLabelText(i18n.I18N_STATUS_STOPPED)
            self._checkbox.set_sensitive(True)

    def showInterface(self):
        """ Show user interface
        """
        self._activity.show_all()

    def getRecordSoundOption(self):
        """ Get record sound option
        """
        return self._checkbox.get_active()

    def alert(self, title, text=None):
        """ Alert popup
        """
        alert = NotifyAlert(timeout=10)
        alert.props.title = title
        alert.props.msg = text
        self._activity.add_alert(alert)
        alert.connect('response', self.alert_cancel_cb)
        alert.show()

    def alert_cancel_cb(self, alert, response_id):
        """ Destroy alert popup
        """
        self._activity.remove_alert(alert)
