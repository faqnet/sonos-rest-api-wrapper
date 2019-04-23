from mySonos import Firebase_callback


class test:
    def __init__(self):
        self.a = "f"

    def passable(self, path, data):
        print(path)

if __name__ == '__main__':
    b = test()
    Firebase_callback('/', b.passable)