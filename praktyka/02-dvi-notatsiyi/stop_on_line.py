#!/usr/bin/env python3
# Робота 2, програма 2: їхати вперед і зупинитись, коли датчик кольору
# бачить темну лінію (reflected_light_intensity нижче порогу).
# Середовище: Gears (Ev3dev-режим), датчик кольору на порту 1,
# світ: Line Following Challenges -> Simple Curves.

import time
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.sensor.virtual import *

tank = MoveTank(OUTPUT_A, OUTPUT_B)
color = ColorSensor(INPUT_1)
THRESHOLD = 30

# підготовка: розвертаємось убік, відʼїжджаємо на світле покриття
# і розвертаємось назад до лінії (на старті робот стоїть просто на лінії)
tank.on_for_rotations(30, -30, 0.7)
tank.on_for_rotations(30, 30, 1.2)
tank.on_for_rotations(30, -30, 1.4)
time.sleep(1)
print('white', color.reflected_light_intensity)

# головна програма: їдемо вперед, поки датчик бачить світле покриття
tank.on(20, 20)
while color.reflected_light_intensity > THRESHOLD:
    time.sleep(0.01)
tank.off()
time.sleep(1)
print('line', color.reflected_light_intensity)
