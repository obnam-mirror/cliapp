Example
=======

::

    class ExampleApp(cliapp.Application):

        def add_settings(self):
            self.settings.string_list(['pattern', 'e'],
                                      'search for regular expression PATTERN',
                                      metavar='REGEXP')

        # We override process_inputs to be able to do something after the last
        # input line.
        def process_inputs(self, args):
            self.matches = 0
            cliapp.Application.process_inputs(self, args)
            self.output.write('There were %s matches.\\n' % self.matches)

        def process_input_line(self, name, line):
            for pattern in self.settings['pattern']:
                if pattern in line:
                    self.output.write('%s:%s: %s' % (name, self.lineno, line))
                    self.matches += 1
                    logging.debug('Match: %s line %d' % (name, self.lineno))


    if __name__ == '__main__':
        ExampleApp().run()

