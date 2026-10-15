from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor.virtual import GPSSensor
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)
color = ColorSensor(INPUT_1)
gps = GPSSensor(INPUT_4)
time.sleep(0.5)

PORIH = 50

pochatok = time.time()
while time.time() - pochatok < 150 and gps.y < 85:   # gps.y - тільки секундомір
    v = color.reflected_light_intensity
    if v < PORIH:
        tank.on(SpeedPercent(10), SpeedPercent(0))   # темно - праве колесо стоїть
    else:
        tank.on(SpeedPercent(0), SpeedPercent(10))   # світло - стоїть ліве

tank.off()
print("час до кінця траси: %.1f с" % (time.time() - pochatok))
