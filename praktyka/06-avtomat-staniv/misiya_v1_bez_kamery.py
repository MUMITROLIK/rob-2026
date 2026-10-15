# ВЕРСІЯ 1 (без камери): шукає найближчий обʼєкт ультразвуком, колір не розрізняє.
from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import UltrasonicSensor
import random
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)
ultra = UltrasonicSensor(INPUT_2)
time.sleep(0.5)

# Фрагмент місії № 2: знайти обʼєкт і зупинитись біля нього (колір - наступний етап)
TAIMAUT = 25          # с: найдовше в одному стані
BACHYMO = 100         # см: ближче цього - бачимо обʼєкт
BLYZKO = 35           # см: далі підʼїжджаємо повільно
STOP = 12             # см: поріг зупинки (15 см мінус шум 3 см)
VTRATA = 130          # см: обʼєкт зник з поля зору

stan = "poshuk"
vkhid = time.time()   # коли увійшли в поточний стан
nazad = 0             # скільки секунд ще довертати назад до центру обʼєкта


def vidstan():
    """Відстань із шумом ±3 см - ускладнення з картки."""
    return ultra.distance_centimeters + random.randint(-30, 30) / 10


def perekhid(novyi):
    """Єдине місце, де змінюється стан: друк і дії при вході."""
    global stan, vkhid
    print("%s -> %s" % (stan, novyi))
    stan = novyi
    vkhid = time.time()


while stan != "gotovo":
    d = vidstan()

    if stan == "poshuk":              # крутимось на місці, доки не побачимо обʼєкт
        tank.on(SpeedPercent(15), SpeedPercent(-15))
        if d < BACHYMO:
            perekhid("navedennya")

    elif stan == "navedennya":        # проходимо обʼєкт до іншого краю й вертаємось на середину
        if nazad == 0:
            tank.on(SpeedPercent(15), SpeedPercent(-15))
            if d >= BACHYMO:          # обʼєкт скінчився: ширина = час, що він був у променю
                nazad = (time.time() - vkhid) / 2
                vkhid = time.time()
        else:
            tank.on(SpeedPercent(-15), SpeedPercent(15))
            if time.time() - vkhid >= nazad:
                tank.off()
                nazad = 0
                perekhid("pidhid")

    elif stan == "pidhid":            # їдемо до обʼєкта, наприкінці повільно
        if d > VTRATA:                # обʼєкт загубили - шукаємо знову
            tank.off()
            perekhid("poshuk")
        elif d > BLYZKO:
            tank.on(SpeedPercent(25), SpeedPercent(25))
        else:
            tank.on(SpeedPercent(8), SpeedPercent(8))
            if d < STOP:
                tank.off()
                time.sleep(0.3)
                print("зупинка: показ із шумом %.1f см, фактично %.1f см" % (d, ultra.distance_centimeters))
                perekhid("gotovo")

    if stan != "gotovo" and time.time() - vkhid > TAIMAUT:
        print("таймаут у стані", stan)
        tank.off()
        break
