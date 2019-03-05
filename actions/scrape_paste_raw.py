#!/usr/bin/env python
import traceback
import socket

import requests

if __name__ != '__main__':
    from st2common.content import utils
    from st2common.runners.base_action import Action

URL = 'https://scrape.pastebin.com/api_scrape_item.php?i={}'

__all__ = ['ScrapePasteRaw',]

old_getaddrinfo = socket.getaddrinfo

def getaddrinfoIPv6(host, port, family=0, type=0, proto=0, flags=0):
    """ monkeypatched getaddrinfo to force IPv6 """
    return old_getaddrinfo(host=host, port=port, family=socket.AF_INET6, proto=proto, flags=flags)

def getaddrinfoIPv4(host, port, family=0, type=0, proto=0, flags=0):
    """ monkeypatched getaddrinfo to force IPv4 """
    return old_getaddrinfo(host=host, port=port, family=socket.AF_INET, proto=proto, flags=flags)

def request_get_versioned(url, ipversion):
    """ does a request with different versions of socket.getaddrinfo - forces IPv4 or IPv6 """
    # monkeypatching requests to work with ipv4 or ipv6 specifically
    if ipversion == 6:
        socket.getaddrinfo = getaddrinfoIPv6
    else:
        socket.getaddrinfo = getaddrinfoIPv4
    return requests.get(url)

class ScrapePasteRaw(Action):
    def run(self, key):
        """ uploads a file from the local disk """
        try:
            # do the HTTP request
            self.logger.debug("Doing the request to {}".format(self.url))
            req = request_get_versioned(URL.format(key), self.config['ipversion'])

            if req and not req.raise_for_status():
                self.logger.debug("Got a response from the API")
                
                data = str(req.text())
                
                if "VISIT: https://pastebin.com/doc_scraping_api TO GET ACCESS!" in req.text:
                    return (False,"Our source IP is not whitelisted.")
                return (True, data)
            else:
                return (False, "No response from the API (status_code: {})".format(req.status_code))
        except Exception as error_message:
            self.logger.debug("Threw an error: {}".format(error_message))
            self.logger.debug(traceback.format_exc())
            return (False, error_message)
