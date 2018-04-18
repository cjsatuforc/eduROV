import argparse
import os

import Pyro4
import RPi.GPIO as GPIO

from edurov import WebMethod


class Motor(object):
    pwm_frequency = 490

    def __init__(self, a_pin, b_pin, reverse=False, pwm=False):
        self.reverse = reverse
        self.pwm = pwm
        if not reverse:
            self.a_pin = a_pin
            self.b_pin = b_pin
        else:
            self.a_pin = b_pin
            self.b_pin = a_pin
        for pin in [a_pin, b_pin]:
            GPIO.setup(pin, GPIO.OUT)

        if self.pwm:
            self.a_pwm = GPIO.PWM(self.a_pin, self.pwm_frequency)
            self.b_pwm = GPIO.PWM(self.b_pin, self.pwm_frequency)
            self.a_pwm.start(0)
            self.b_pwm.start(0)
        else:
            for pin in [a_pin, b_pin]:
                GPIO.output(pin, GPIO.LOW)

    def speed(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        if speed > 0:
            self.forward(speed)
        elif speed < 0:
            self.backward(speed * -1)
        else:
            self.stop()

    def forward(self, speed=100.0):
        if self.pwm:
            self.a_pwm.ChangeDutyCycle(speed)
            self.b_pwm.ChangeDutyCycle(0)
        else:
            GPIO.output(self.a_pin, GPIO.HIGH)
            GPIO.output(self.b_pin, GPIO.LOW)

    def backward(self, speed=100.0):
        if self.pwm:
            self.a_pwm.ChangeDutyCycle(0)
            self.b_pwm.ChangeDutyCycle(speed)
        else:
            GPIO.output(self.a_pin, GPIO.LOW)
            GPIO.output(self.b_pin, GPIO.HIGH)

    def stop(self):
        if self.pwm:
            self.a_pwm.ChangeDutyCycle(0)
            self.b_pwm.ChangeDutyCycle(0)
        else:
            GPIO.output(self.a_pin, GPIO.LOW)
            GPIO.output(self.b_pin, GPIO.LOW)

    def close(self):
        if self.pwm:
            self.a_pwm.stop()
            self.b_pwm.stop()


def control_motors():
    GPIO.setmode(GPIO.BCM)
    m1 = Motor(4, 18, pwm=True)
    m2 = Motor(12, 19, pwm=True)
    normal = 50
    turn = 30

    with Pyro4.Proxy("PYRONAME:KeyManager") as keys:
        with Pyro4.Proxy("PYRONAME:ROVSyncer") as rov:
            while rov.run:
                keys_dict = keys.arrow_dict
                motor1_speed = 0
                motor2_speed = 0
                if keys_dict['up arrow']:
                    motor1_speed += normal
                    motor2_speed += normal
                elif keys_dict['down arrow']:
                    motor1_speed -= normal
                    motor2_speed -= normal
                if keys_dict['left arrow']:
                    motor1_speed += turn
                    motor2_speed -= turn
                elif keys_dict['right arrow']:
                    motor1_speed -= turn
                    motor2_speed += turn
                m1.speed(motor1_speed)
                m2.speed(motor2_speed)
    m1.close()
    m2.close()
    GPIO.cleanup()


def main(video_resolution='1024x768', fps=30, server_port=8000, debug=False):
    web_method = WebMethod(
        video_resolution=video_resolution,
        fps=fps,
        server_port=server_port,
        debug=debug,
        runtime_functions=control_motors,
        index_file=os.path.join(os.path.dirname(__file__), 'index.html', )
    )
    web_method.serve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Start a streaming video server on raspberry pi')
    parser.add_argument(
        '-r',
        metavar='RESOLUTION',
        type=str,
        default='1024x768',
        help='''resolution, use format WIDTHxHEIGHT or an integer''')
    parser.add_argument(
        '-fps',
        metavar='FRAMERATE',
        type=int,
        default=30,
        help='framerate for the camera (default 30)')
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='set to print debug information')

    args = parser.parse_args()

    main(
        video_resolution=args.r,
        fps=args.fps,
        server_port=8000,
        debug=args.debug
    )