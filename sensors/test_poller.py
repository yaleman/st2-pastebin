""" does a regular poll of the pastebin scrape API to get new pastes,
    emits a trigger to say a new paste has occurred """

import traceback

from st2reactor.sensor.base import PollingSensor

__all__ = ['TestPoller',]

class TestPoller(PollingSensor):
    """ regularly polls the pastebin scrape API endpoint and reports back new keys """

    def __init__(self, sensor_service, config=None, poll_interval=None):
        """ sets up the thing """
        super(TestPoller, self).__init__(sensor_service=sensor_service,
                                             config=config, poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self._logger.debug("TEST LOGGING __init__() start")


    def setup(self):
        """ Setup stuff goes here. This is called only once by the system."""
        self._logger.debug("TEST LOGGING setup() noop")
        pass

    def poll(self):
        self._logger.debug("TEST LOGGING poll()")

    
        return

    def cleanup(self):
        """ cleanup handler """
        self._logger.debug("TEST LOGGING cleanup() noop")
        pass

    def add_trigger(self, trigger):
        """ run when the trigger is added to the system """
        self._logger.debug("TEST LOGGING add_trigger({}) noop".format(trigger))
        pass

    def update_trigger(self, trigger):
        """ run when there's a change to the trigger """
        self._logger.debug("TEST LOGGING update_trigger({}) noop".format(trigger))
        pass

    def remove_trigger(self, trigger):
        """ run when the trigger is removed """
        self._logger.debug("TEST LOGGING remove_trigger({}) noop".format(trigger))
        pass
