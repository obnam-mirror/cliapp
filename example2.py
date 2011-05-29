# Copyright 2011  Lars Wirzenius
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


'''Example for cliapp framework.

Greet or insult people.

'''


import cliapp
import logging


class ExampleApp(cliapp.Application):

    def cmd_greet(self, args):
        for arg in args:
            self.output.write('greetings, %s\n' % arg)
            
    def cmd_insult(self, args):
        for arg in args:
            self.output.write('you suck, %s\n' % arg)
    
    
app = ExampleApp(version='0.1.2', description='''
Greet the user.
Or possibly insult them. User's choice.
''',
epilog='''
This is the epilog.

I hope you like it.
''')
app.settings.config_files = ['example.conf']
app.run()

