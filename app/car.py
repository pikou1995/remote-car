import asyncio
import RPi.GPIO as GPIO
import time

PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24


class Car:
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

    def stop(self):
        self.L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, False)

        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2, False)
        GPIO.output(BIN1, False)

    async def forward(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, True)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, False)
        GPIO.output(BIN1, True)
        if t_time:
            await asyncio.sleep(t_time)
        self.stop()

    async def backword(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, True)
        GPIO.output(AIN1, False)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, True)
        GPIO.output(BIN1, False)
        if t_time:
            await asyncio.sleep(t_time)
        self.stop()

    async def left(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, True)
        GPIO.output(AIN1, False)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, False)
        GPIO.output(BIN1, True)
        if t_time:
            await asyncio.sleep(t_time)
        self.stop()

    async def right(self, speed, t_time):
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2, False)
        GPIO.output(AIN1, True)

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2, True)
        GPIO.output(BIN1, False)
        if t_time:
            await asyncio.sleep(t_time)
        self.stop()


car = Car()
