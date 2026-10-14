# Робота 3: 10 поворотів "на час" і 10 поворотів "по гіроскопу".
# Середовище: Gears, світ Grid, швидкість 20 %, поворот праворуч.

from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_3
from ev3dev2.sensor.lego import GyroSensor
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)   # A - ліве колесо, B - праве
gyro = GyroSensor(INPUT_3)            # у Gears порт обовязковий
time.sleep(0.5)

print("гіроскоп:", gyro.angle)

# Крок 2: 10 поворотів "на час" (1 с, 20 %)
porednii = gyro.angle
for i in range(1, 11):
    tank.on_for_seconds(SpeedPercent(20), SpeedPercent(-20), 1.0)
    time.sleep(0.5)
    teper = gyro.angle
    print("T", i, teper - porednii)
    porednii = teper

# Крок 4: 10 поворотів "по гіроскопу" до 90 градусів
for i in range(1, 11):
    gyro.reset()
    tank.on(SpeedPercent(20), SpeedPercent(-20))
    while gyro.angle < 90:
        pass
    tank.off()
    time.sleep(0.5)
    print("G", i, gyro.angle)
