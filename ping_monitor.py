#!/usr/bin/env python

# Adapte from:
# https://bitbucket.org/cpbotha/indicator-cpuspeed/src

# Requires python version 2.5 or higher, because
# 1) the deque()'s second parameter,
#       maxlen, was introduced in 2.6
# 2) Wer'e using the `TRUE if EXPR ELSE FALSE` ternary operator
#       it was introduced in 2.5

from subprocess import check_output
from collections import deque

from gi.repository import Gtk, GLib

try:
       from gi.repository import AppIndicator3 as AppIndicator
except:
       from gi.repository import AppIndicator

import re

class IndicatorPing:
    def __init__(self):
        # param1: identifier of this indicator
        # param2: name of icon. this will be searched for in the standard dirs
        # finally, the category. We're monitoring network, so COMMUNICATIONS.
        self.ind = AppIndicator.Indicator.new(
                            "indicator-ping",
                            "", #onboard-mono",
                            AppIndicator.IndicatorCategory.COMMUNICATIONS)

        # need to set this for indicator to be shown
        self.ind.set_status (AppIndicator.IndicatorStatus.ACTIVE)

        # have to give indicator a menu
        self.menu = Gtk.Menu()

        # Create a menu-item to restart Network Manager
        item = Gtk.MenuItem()
        item.set_label("Restart Network Manager")
        item.connect("activate", self.handler_restart_network_manager)
        item.show()
        self.menu.append(item)

        # this is for exiting the app
        item = Gtk.MenuItem()
        item.set_label("Exit")
        item.connect("activate", self.handler_menu_exit)
        item.show()
        self.menu.append(item)

        self.menu.show()
        self.ind.set_menu(self.menu)

        # Maintain a deque of at most 10 elements
        self.past = deque("", 10)
        self.latest_counter = 0 # How many of the latest pings have been failing

        self.ping_hard_timeout = 2
        self.callback_interval = 3 # This should be greater than ping_hard_timeout

        self.update_ui()

        # Start updating every 3 seconds. Don't use a value less than 2 here, see
		# the link below.
        # http://developer.gnome.org/pygobject/stable/glib-functions.html#function-glib--timeout-add-seconds
        GLib.timeout_add_seconds(self.callback_interval, self.handler_timeout)

    def ping(self):
        """Pings google.com and returns dot (.) on success, or an X on failure.
        """

        return check_output(["sh", "-c", "{ timeout "+ str(self.ping_hard_timeout) +" ping -w 3 -c 2 -i 1 google.com >/dev/null 2>&1 && echo -n . ; } || { echo -n X ; }"])

    def handler_menu_exit(self, evt):
        Gtk.main_quit()

    def handler_restart_network_manager(self, evt):
        # we can change the icon at any time
        check_output(["sh", "-c", "sudo service network-manager restart"])

    def handler_timeout(self):
        """This will be called every few seconds by the GLib.timeout.
        """

        self.update_ui()
        # return True so that we get called again
        # returning False will make the timeout stop
        return True

    def update_ui(self):
        f = self.ping()
        self.past.append(f)

        if f == "X":
            self.latest_counter += 1
        else:
            self.latest_counter = 0

        n1 = self.latest_counter
        n2 = self.past.count("X")
        n3 = min(self.past.maxlen, len(self.past))

        label = ("ping "
                + (" " if n1 < 10 else "") + str(n1) + ", "
                + (" " if n2 < 10 else "") + str(n2) + "/"
                + (" " if n3 < 10 else "") + str(n3))

        self.ind.set_label(label, "ping 99, 99, 99")

        if self.latest_counter > 0:
            print label + ": " + str(self.past)

    def main(self):
        Gtk.main()

if __name__ == "__main__":
    ind = IndicatorPing()
    ind.main()


