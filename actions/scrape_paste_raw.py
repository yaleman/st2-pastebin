#!/usr/bin/env python
import traceback
import socket

from requests import get
import requests.packages.urllib3.util.connection as urllib3_cn


if __name__ != '__main__':
    from st2common.content import utils
    from st2common.runners.base_action import Action

URL = 'https://scrape.pastebin.com/api_scrape_item.php?i={}'

__all__ = ['ScrapePasteRaw',]

"""
fix from https://stackoverflow.com/questions/33046733/force-requests-to-use-ipv4-ipv6/46972341#46972341
relates to https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
"""
def allowed_gai_family_v4():
    return socket.AF_INET

def allowed_gai_family_v6():
    return socket.AF_INET6

class ScrapePasteRaw(Action):

    def run(self, key):
        # rebind the IP Version thing
        # pastebin only allows you to whitelist a single source IP and dual-stack randomly uses a different source IP 
        if self.config['ipversion'] == 4:
            urllib3_cn.allowed_gai_family = allowed_gai_family_v4
        elif self.config['ipversion'] == 6:
            urllib3_cn.allowed_gai_family = allowed_gai_family_v6
        else:
            self._logger.debug("No IP Version set in configuration")
            return False

        """ grabs a raw paste based on the key """
        try:
            # do the HTTP request
            url = URL.format(key)
            self.logger.debug("Doing the request to {}".format(url))
            req = get(url, self.config['ipversion'])

            if req and not req.raise_for_status():
                self.logger.debug("Got a response from the API")
                
                # TODO: fix this: 
                """  "elapsed_seconds": 5.184091,
  "web_url": "https://st2.housenet.yaleman.org/#/history/5c7e760852364c07a0828fc0/general",
  "parent": "5c7e760652364c0577281375",
  "result": {
    "result": "'ascii' codec can't encode character u'\\xe4' in position 58: ordinal not in range(128)",
    "exit_code": 0,
    "stderr": "st2.actions.python.ScrapePasteRaw: DEBUG    Doing the request to https://scrape.pastebin.com/api_scrape_item.php?i=g1Uh1Pwe
st2.actions.python.ScrapePasteRaw: DEBUG    Got a response from the API
st2.actions.python.ScrapePasteRaw: DEBUG    Threw an error: 'ascii' codec can't encode character u'\\xe4' in position 58: ordinal not in range(128)
st2.actions.python.ScrapePasteRaw: DEBUG    Traceback (most recent call last):
  File \"/opt/stackstorm/packs/pastebin/actions/scrape_paste_raw.py\", line 50, in run
    data = str(req.text)
UnicodeEncodeError: 'ascii' codec can't encode character u'\\xe4' in position 58: ordinal not in range(128)
"""
                
                data = req.text.encode('utf-8')
                
                if "VISIT: https://pastebin.com/doc_scraping_api TO GET ACCESS!" in data:
                    return (False,"Our source IP is not whitelisted.")
                return (True, data)
            else:
                return (False, "No response from the API (status_code: {})".format(req.status_code))
        except Exception as error_message:
            self.logger.debug("Threw an error: {}".format(error_message))
            self.logger.debug(traceback.format_exc())
            return (False, error_message)
