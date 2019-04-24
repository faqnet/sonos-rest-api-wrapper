import time

from sonos import mySonos


class test:
    def __init__ (self):
        self.a = "f"

    def passable (self, path, data):
        print(path)


if __name__ == '__main__':
    b = test()
    d = mySonos.Firebase_callback('/', b.passable)
    print(b.a)
    time.sleep(5)
    print("done sleeping ")
    d.close()


