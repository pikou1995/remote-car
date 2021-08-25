import Adafruit_PCA9685

# 初始化PCA9685和舵机
servo_pwm = Adafruit_PCA9685.PCA9685()  # 实例话舵机云台

VERTICAL = 4  # 倾斜舵机
HORIZONTAL = 5  # 底座舵机

servo_pwm.set_pwm_freq(60)  # 设置频率为60HZ


class Servo():
    speed = 10
    action = ''

    def __init__(self):
        self.v_deg = 360
        self.h_deg = 360
        # 设置舵机初始值，可以根据自己的要求调试
        servo_pwm.set_pwm(VERTICAL, 0, self.v_deg)
        servo_pwm.set_pwm(HORIZONTAL, 0, self.h_deg)

    def cal_deg(self, deg: int):
        if (deg <= 150):
            return 150
        elif (deg >= 570):
            return 570
        else:
            return deg
    
    def update_speed(self, action):
        if self.action != action:
            self.action = action
            self.speed = 10
        elif self.speed == 10:
            self.speed = 30


    def up(self):
        self.update_speed('up')
        self.v_deg = self.cal_deg(self.v_deg - self.speed)
        servo_pwm.set_pwm(VERTICAL, 0, self.v_deg)

    def left(self):
        self.update_speed('left')
        self.h_deg = self.cal_deg(self.h_deg - self.speed)
        servo_pwm.set_pwm(HORIZONTAL, 0, self.h_deg)

    def down(self):
        self.update_speed('down')
        self.v_deg = self.cal_deg(self.v_deg + self.speed)
        servo_pwm.set_pwm(VERTICAL, 0, self.v_deg)

    def right(self):
        self.update_speed('right')
        self.h_deg = self.cal_deg(self.h_deg + self.speed)
        servo_pwm.set_pwm(HORIZONTAL, 0, self.h_deg)
