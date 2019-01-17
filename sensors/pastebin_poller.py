""" does a regular poll of the pastebin scrape API to get new pastes,
    emits a trigger to say a new paste has occurred """

import traceback
import json
import requests

from st2reactor.sensor.base import PollingSensor

__all__ = ['PasteBinPoller',]

SCRAPE_URL = 'https://scrape.pastebin.com/api_scraping.php'

class PasteBinPoller(PollingSensor):
    """ regularly polls the pastebin scrape API endpoint and reports back new keys """

    def __init__(self, sensor_service, config=None, poll_interval=None):
        """ sets up the thing """
        super(PasteBinPoller, self).__init__(sensor_service=sensor_service,
                                             config=config, poll_interval=poll_interval)
        self._trigger_ref = 'pastebin.new_paste'
        self._logger = self._sensor_service.get_logger(__name__)
        self._last_time = None
        limit = 50 # default, TODO: make this a config item
        self._url = "{}?limit={}".format(SCRAPE_URL, limit)

    def setup(self):
        """ Setup stuff goes here. This is called only once by the system."""
        pass

    def poll(self):
        """ does the polling action """
        try:
            # do the HTTP request
            req = requests.get(self._url)
            self._logger.debug("Doing the request to {}".format(self._url))
            if req and req.status_code == 200:
                self._logger.debug("Got a response from the API")
                try:
                    jsondata = req.json()
                except json.JSONDecodeError:
                    self._logger.debug("JSON Decode failed, stopping. Probably not running from a whitelisted IP")
                    return False
                if "VISIT: https://pastebin.com/doc_scraping_api TO GET ACCESS!" in req.text:
                    self._logger.debug("Our source IP is not whitelisted, stoppping.")
                    return False
                # sort by timestamp, it comes in most-recent-first
                data = sorted(jsondata, key=lambda k: k['date'])
                for paste in data:
                    self._logger.debug("time:{} key:{}".format(paste['date'], paste['key']))
                    if paste['date'] > self._get_last_time():
                        # this is the timestamp of the last processed paste
                        self._set_last_time(last_time=paste['date'])
                        # do the thing
                        payload = {'date' : paste['date'], 'key' : paste['key']}
                        self._sensor_service.dispatch(trigger=self._trigger_ref, payload=payload)
                    else:
                        self._logger.debug("Skipping paste {} {}".format(paste['key'], paste['date']))
            else:
                self._logger.debug("No response from the API (status_code: {})".format(req.status_code))
        except Exception as error_message:
            self._logger.debug("Threw an error: {}".format(error_message))
            self._logger.debug(traceback.format_exc())
        return

    def _get_last_time(self):
        """ returns the last timestamp that was processed by the poller """
        if not self._last_time and hasattr(self._sensor_service, 'get_value'):
            self._last_time = self._sensor_service.get_value(name='last_time')
        return self._last_time

    def _set_last_time(self, last_time):
        """ stores the last timestamp seen by the thing """
        self._last_time = last_time
        if hasattr(self._sensor_service, 'set_value'):
            self._sensor_service.set_value(name='last_time', value=last_time)


    def cleanup(self):
        """ cleanup handler """
        pass

    def add_trigger(self, trigger):
        """ run when the trigger is added to the system """
        pass

    def update_trigger(self, trigger):
        """ run when there's a change to the trigger """
        pass

    def remove_trigger(self, trigger):
        """ run when the trigger is removed """
        pass
