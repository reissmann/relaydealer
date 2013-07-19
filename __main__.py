'''
Copyright (c) 2013, Sven Reissmann <sven@0x80.io>

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
'''

import os
import web


# the full path to the relay device
DEVICE = '/tmp/bits'



class Relay:
    ''' we are serving exactly one page (the index page /). if called without
        any parameters, the relay status is shown. if called with a relay id
        as the first (and only evaluated) parameter, the selected array will
        change state and again, the status is shown.
    '''

    def __init__(self):
        pass


    def GET(self, relay_id):
        ''' called for each page request. get relay status, optionally
            manipulate it, print new status
        '''
        # get current relay status
        msg = ''
        status = int(self.get_relay_status())

        # manipulate relay status
        if relay_id:
            try:
                relay_id = int(relay_id)
            except ValueError:
                msg = 'Invalid Relay ID. Value must be numeric.'
            else:
                if 0 <= relay_id < 8:
                    status = self.toggle_bit(status, relay_id)
                    if self.set_relay_status(status) == 0:
                        msg = 'Relay status changed'
                else:
                    msg = 'Invalid Relay ID. Value must be between 0 and 7.'

        # print relay status
        page = web.template.frender(os.path.join(os.path.dirname(__file__),
                                                 'templates/relay.html'))
        return page(status, self.gen_bitlist(status)[::-1], msg)


    def get_relay_status(self):
        ''' get the current relay status
        '''
        return os.popen('cat ' + DEVICE).read()


    def set_relay_status(self, status):
        ''' set a new relay status
        '''
        return os.system('echo ' + str(status) + ' > ' + DEVICE)


    def toggle_bit(self, bitfield, offset):
        ''' return bitfield with the bit at position offset toggled
        '''
        return (bitfield ^ (1 << offset))


    def gen_bitlist(self, status):
        ''' convert the integer describing the bitfield status to a list of
            single bits. needed for visualization with individual buttons
        '''
        return [1 if b == '1' else 0 for b in format(status, '#010b')[2:]]



# run the application
# note: wsgi should be the prefered method
urls = (
    '/(.*)', 'Relay'
)

if __name__ == '__main__':
    web.application(urls, globals()).run()
else:
    application = web.application(urls, globals()).wsgifunc()
