import time

import Pyro4

from support import detect_pi

if detect_pi():
    from sense_hat import SenseHat

X = [255, 255, 255]
O = [0, 0, 0]

up = [
    O, O, O, X, X, O, O, O,
    O, O, X, X, X, X, O, O,
    O, X, X, X, X, X, X, O,
    X, X, O, X, X, O, X, X,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O
]

down = [
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    X, X, O, X, X, O, X, X,
    O, X, X, X, X, X, X, O,
    O, O, X, X, X, X, O, O,
    O, O, O, X, X, O, O, O
]

left = [
    O, O, O, X, O, O, O, O,
    O, O, X, X, O, O, O, O,
    O, X, X, O, O, O, O, O,
    X, X, X, X, X, X, X, X,
    X, X, X, X, X, X, X, X,
    O, X, X, O, O, O, O, O,
    O, O, X, X, O, O, O, O,
    O, O, O, X, O, O, O, O
]

right = [
    O, O, O, O, X, O, O, O,
    O, O, O, O, X, X, O, O,
    O, O, O, O, O, X, X, O,
    X, X, X, X, X, X, X, X,
    X, X, X, X, X, X, X, X,
    O, O, O, O, O, X, X, O,
    O, O, O, O, X, X, O, O,
    O, O, O, O, X, O, O, O
]


def start_sense_hat():
    sense = SenseHat()
    with Pyro4.Proxy("PYRONAME:KeyManager") as keys:
        while True:
            print('sense' + str(keys.variable()))
            if keys.state('up arrow'):
                sense.set_pixels(up)
            elif keys.state('down arrow'):
                sense.set_pixels(down)
            elif keys.state('right arrow'):
                sense.set_pixels(right)
            elif keys.state('left arrow'):
                sense.set_pixels(left)
            else:
                sense.clear()
            time.sleep(1)


if __name__ == '__main__':
    start_sense_hat()
