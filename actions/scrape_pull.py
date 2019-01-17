import sys

from st2common.runners.base_action import Action

import requests

class ScrapePull(Action):
    def run(self, url, limit):
        #print(message)
        req = requests.get(url)

        if req:
            return (True, req.status_code)
        return (False, False)
        #if message == 'working':
        #    return (True, message)
        #return (False, message)

