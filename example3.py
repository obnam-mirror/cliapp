# Copyright (C) 2012  Lars Wirzenius
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


'''Example for cliapp framework.

Demonstrate the compute_setting_values method.

'''


import urlparse

import cliapp


class ExampleApp(cliapp.Application):

    '''A little fgrep-like tool.'''

    def add_settings(self):
        self.settings.string(['url'], 'a url')
        self.settings.string(['protocol'], 'the protocol')

    def compute_setting_values(self, settings):
        if not self.settings['protocol']:
            schema = urlparse.urlparse(self.settings['url'])[0]
            self.settings['protocol'] = schema

    def process_args(self, args):
        return


app = ExampleApp()
app.run()

