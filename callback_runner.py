import time

from mySonos import Firebase_callback


class test:
    def __init__ (self):
        self.a = "f"

    def passable (self, path, data):
        print(path)


if __name__ == '__main__':
    b = test()
    d = Firebase_callback('/', b.passable)
    print(b.a)
    time.sleep(5)
    print("done sleeping ")
    d.close()


