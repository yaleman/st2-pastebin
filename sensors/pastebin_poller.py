from st2reactor.sensor.base import PollingSensor

import requests

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
        # Setup stuff goes here. For example, you might establish connections
        # to external system once and reuse it. This is called only once by the system.
        pass

    def poll(self):
        limit = 50 # default, need to make this a config item
        try:
            req = requests.get("{}?limit={}".format(SCRAPE_URL, limit))

            if req and req.status_code == 200:
                data = req.json()
                for paste in data:
                    if paste['date'] > self._get_last_time():
                        # this is the timestamp of the last processed paste
                        self._set_last_time(last_time=paste['date'])
                        # do the thing
                        self._sensor_service.dispatch(trigger=self._trigger_ref, payload={'key' : paste['key']})
        except:
            pass
        return
   
    def _get_last_time(self):
        """ returns the last timestamp that was processed by the poller """
        if not self._last_time and hasattr(self._sensor_service, 'get_value')):
            self._last_time = self._sensor_service.get_value(name='last_time')
        return self._last_time

    def _set_last_time(self, last_time):
        self._last_time = last_time
        if hasattr(self._sensor_service, 'set_value'):
            self._sensor_service.set_value(name='last_time', value=last_time)
            
