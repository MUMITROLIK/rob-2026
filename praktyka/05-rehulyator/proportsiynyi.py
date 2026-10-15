from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor.virtual import GPSSensor
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)
color = ColorSensor(INPUT_1)
gps = GPSSensor(INPUT_4)
time.sleep(0.5)

PORIH = 50      # між білим (~100) і чорним (~1)
BAZA = 20       # швидкість прямо, %
Kp = 1.0        # підібране значення (див. zvit.md)


def obmezhyty(v):
    return max(-100, min(100, v))


pochatok = time.time()
while time.time() - pochatok < 120 and gps.y < 85:   # gps.y - тільки секундомір
    v = color.reflected_light_intensity
    e = PORIH - v
    korekciya = Kp * e
    tank.on(SpeedPercent(obmezhyty(BAZA - korekciya)),
            SpeedPercent(obmezhyty(BAZA + korekciya)))

tank.off()
print("час до кінця траси: %.1f с" % (time.time() - pochatok))
