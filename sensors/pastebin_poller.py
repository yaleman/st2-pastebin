from st2reactor.sensor.base import PollingSensor

import requests
import traceback
__all__ = [ 'PasteBinPoller', ]

SCRAPE_URL = 'https://scrape.pastebin.com/api_scraping.php'

class PasteBinPoller(PollingSensor):
    """ regularly polls the pastebin scrape API endpoint and reports back new keys """

    def __init__(self, sensor_service, config=None, poll_interval=None):
        """ sets up the thing """
        super(PasteBinPoller, self).__init__(sensor_service=sensor_service, config=config, poll_interval=poll_interval)
        self._trigger_ref = 'pastebin.scrape_paste_raw'
        self._logger = self._sensor_service.get_logger(__name__)

    def setup(self):
        # Setup stuff goes here. This is called only once by the system.
        self._last_time = None
        limit = 50 # default, TODO: make this a config item
        self._url = "{}?limit={}".format(SCRAPE_URL, limit)

    def poll(self):
        """ does the polling action """
        try:
            # do the HTTP request
            req = requests.get(self._url)
            print("Doing the request")
            if req and req.status_code == 200:
                print("Got a value")
                # sort by timestamp, it comes in most-recent-first
                data = sorted(req.json(), key=lambda k: k['date'])
                for paste in data:
                    print("time:{} key:{}".format(paste['date'], paste['key']))
                    if paste['date'] > self._get_last_time():
                        # this is the timestamp of the last processed paste
                        self._set_last_time(last_time=paste['date'])
                        # do the thing
                        self._sensor_service.dispatch(trigger=self._trigger_ref, payload={'key' : paste['key']})
        except Exception as e:
            print("Threw an error: {}".format(e))
            print(traceback.format_exc())
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
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass
