from servo import Servo
import asyncio
import RPi.GPIO as GPIO

PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24


class Car:
    delay_stop_handler = None
    action = 'stop'
    speed = 0
    servo: Servo

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(PWMA, GPIO.OUT)

        GPIO.setup(BIN1, GPIO.OUT)
        GPIO.setup(BIN2, GPIO.OUT)
        GPIO.setup(PWMB, GPIO.OUT)

        self.L_Motor = GPIO.PWM(PWMA, 100)
        self.L_Motor.start(0)

        self.R_Motor = GPIO.PWM(PWMB, 100)
        self.R_Motor.start(0)

        self.servo = Servo()

    def set_speed(self, action: str):
        if self.action != action:
            self.action = action
            self.speed = 60
        elif self.speed == 60:
            self.speed = 100

        if action == 'stop':
            self.speed = 0
        print(self.speed, action)

        self.L_Motor.ChangeDutyCycle(self.speed)
        self.R_Motor.ChangeDutyCycle(self.speed)

    def stop(self):
        self.delay_stop_handler = None
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, False)

        GPIO.output(BIN2, False)
        GPIO.output(BIN1, False)
        self.set_speed('stop')

    def forward(self):
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, True)

        GPIO.output(BIN2, False)
        GPIO.output(BIN1, True)
        self.set_speed('forward')

    def backward(self):
        GPIO.output(AIN2, True)
        GPIO.output(AIN1, False)

        GPIO.output(BIN2, True)
        GPIO.output(BIN1, False)
        self.set_speed('backward')

    def left(self):
        GPIO.output(AIN2, True)
        GPIO.output(AIN1, False)

        GPIO.output(BIN2, False)
        GPIO.output(BIN1, True)
        self.set_speed('left')

    def right(self):
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, True)

        GPIO.output(BIN2, True)
        GPIO.output(BIN1, False)
        self.set_speed('right')

    def delay_stop(self, delay: float):
        if self.delay_stop_handler:
            self.delay_stop_handler.cancel()
        loop = asyncio.get_event_loop()
        self.delay_stop_handler = loop.call_later(delay, self.stop)


car = Car()
