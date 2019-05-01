import time

import requests

import json
from sonos import my_sonos


class test:
    def __init__ (self):
        self.a = "f"

    def passable (self, path, data):
        print(path)

    def test_req (self):
        try:
            r = requests.get("http://www.google.com/moi")
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as err:
            raise err

    def te (self):
        try:
            b = self.test_req()
            print(b)
        except Exception as err:
            print(err)
            print("failed")


if __name__ == '__main__':

    # some JSON:
    x = '{ "name":"John", "age":30, "city":"New York"}'

    # parse x:
    y = json.loads(x)

    # the result is a Python dictionary:
    print(y.get("c", None))

