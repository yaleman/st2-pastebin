""" does a regular poll of the pastebin scrape API to get new pastes,
    emits a trigger to say a new paste has occurred """

from traceback import format_exc
import socket

import requests.packages.urllib3.util.connection as urllib3_cn
from requests import get as requests_get

from st2reactor.sensor.base import PollingSensor

__all__ = ['PasteBinPoller',]

SCRAPE_URL = 'https://scrape.pastebin.com/api_scraping.php'


"""
fix from https://stackoverflow.com/questions/33046733/force-requests-to-use-ipv4-ipv6/46972341#46972341
relates to https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
"""
def allowed_gai_family_v4():
    return socket.AF_INET

def allowed_gai_family_v6():
    return socket.AF_INET6


class PasteBinPoller(PollingSensor):
    """ regularly polls the pastebin scrape API endpoint and reports back new keys """

    def __init__(self, sensor_service, config=None, poll_interval=None):
        """ sets up the thing """
        super(PasteBinPoller, self).__init__(sensor_service=sensor_service,
                                             config=config, 
                                             poll_interval=poll_interval)
        self._trigger_ref = 'pastebin.new_paste'
        self._logger = self._sensor_service.get_logger(__name__)
        self._logger.debug("PastebinPoller.__init__() start")
        #self._last_time = self._get_last_time()
        self._url = "{}?limit={}".format(SCRAPE_URL, self._config['poll_maxresults'])
        self._logger.debug("PastebinPoller.__init__() done")


    def setup(self):
        """ Setup stuff goes here. This is called only once by the system."""
        self._logger.debug("PastebinPoller.setup() start")
        poll_interval = self._config['poll_interval']
        self._logger.debug("Config poll interval: {}".format(poll_interval))
        self.set_poll_interval(poll_interval)
        self._logger.debug('set poll interval to {}'.format(poll_interval))

        # rebind the IP Version thing
        # pastebin only allows you to whitelist a single source IP and dual-stack randomly uses a different source IP 
        if self._config['ipversion'] == 4:
            urllib3_cn.allowed_gai_family = allowed_gai_family_v4
        elif self._config['ipversion'] == 6:
            urllib3_cn.allowed_gai_family = allowed_gai_family_v6
        else:
            self._logger.debug("No IP Version set in configuration")
            return False
        # end rebind the IP Version thing
        
        self._logger.debug("PastebinPoller.setup() end")

    def poll(self):
        """ does the polling action
            if it finds a "new" paste, emits a payload:
                {
                    'date' : int,
                    'key' : str,
                    'title' : str,
                    'user' : str,
                    'size' : int,
                    'syntax' : str,
                }
        """
        try:
            self._logger.debug("PastebinPoller.poll() start")
            #self.set_poll_interval(self._config['poll_interval'])
            #self._logger.debug('set poll interval to {}'.format(self._config['poll_interval']))
            
            
            # do the HTTP request
            self._logger.debug("Doing the request to {}".format(self._url))
            #req = request_get_versioned(self._url, self._config['ipversion'])
            req = requests_get(self._url)

            if req and not req.raise_for_status():
                self._logger.debug("Got a response from the API")
                try:
                    jsondata = req.json()
                except TypeError:
                    self._logger.debug("JSON Decode failed, stopping. Probably not running from a whitelisted IP")
                    return
                if "VISIT: https://pastebin.com/doc_scraping_api TO GET ACCESS!" in req.text:
                    self._logger.debug("Our source IP is not whitelisted, stoppping.")
                    return
                # sort by timestamp, it comes in most-recent-first
                data = sorted(jsondata, key=lambda k: k['date'])
                for paste in data:
                    self._logger.debug("PastebinPoller found paste - time:{} key:{}".format(paste['date'], paste['key']))
                    if paste['date'] > self._get_last_time():
                        # this is the timestamp of the last processed paste
                        self._set_last_time(last_time=paste['date'])
                        # do the thing
                        payload = {'date' : int(paste['date']), 
                                   'key' : paste['key'],
                                   'size' : int(paste['size']),
                                   'user' : paste['user'],
                                   'title' : paste['title'],
                                   'syntax' : paste['syntax'],
                                   }
                        self._logger.debug("Trigger running...")
                        self._sensor_service.dispatch(trigger=self._trigger_ref, payload=payload)
                        self._logger.debug("Trigger done.")
                    else:
                        self._logger.debug("Skipping paste {} {}".format(paste['key'], paste['date']))
            else:
                self._logger.debug("No response from the API (status_code: {})".format(req.status_code))
                return
        except Exception as error_message:
                self._logger.debug("Threw an error: {}".format(error_message))
                self._logger.debug(format_exc())
        self._logger.debug("PastebinPoller.poll() end")

    def _get_last_time(self):
        """ returns the last timestamp that was processed by the poller """
        self._logger.debug("PastebinPoller._get_last_time() start")
        if (not hasattr(self, '_last_time') or not self._last_time) and hasattr(self._sensor_service, 'get_value'):
            self._last_time = self._sensor_service.get_value(name='last_time')
        self._logger.debug("PastebinPoller._get_last_time() end, returning {}".format(self._last_time))
        return self._last_time

    def _set_last_time(self, last_time):
        """ stores the last timestamp seen by the thing """
        self._logger.debug("PastebinPoller._set_last_time({}) start".format(last_time))
        self._last_time = last_time
        if hasattr(self._sensor_service, 'set_value'):
            self._sensor_service.set_value(name='last_time', value=last_time)
        self._logger.debug("PastebinPoller._set_last_time({}) end".format(last_time))


    def cleanup(self):
        """ cleanup handler """
        self._logger.debug("PastebinPoller.cleanup() noop")
        pass

    def add_trigger(self, trigger):
        """ run when the trigger is added to the system """
        self._logger.debug("PastebinPoller.add_trigger({}) noop".format(trigger))
        pass

    def update_trigger(self, trigger):
        """ run when there's a change to the trigger """
        self._logger.debug("PastebinPoller.update_trigger({}) noop".format(trigger))
        pass

    def remove_trigger(self, trigger):
        """ run when the trigger is removed """
        self._logger.debug("PastebinPoller.remove_trigger({}) noop".format(trigger))
        pass
