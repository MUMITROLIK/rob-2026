from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_2, INPUT_3, INPUT_6
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from ev3dev2.sensor.virtual import CameraSensor
import random
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)
ultra = UltrasonicSensor(INPUT_2)
gyro = GyroSensor(INPUT_3)
cam = CameraSensor(INPUT_6)         # камера: порт 6 (додана в конфігурації робота)
time.sleep(0.5)

# Фрагмент місії № 2: знайти ЧЕРВОНИЙ маяк серед інших і зупинитись біля нього
TAIMAUT = 30          # с: найдовше в одному стані
STOP = 12             # см: поріг зупинки (15 см мінус шум 3 см)
BLYZKO_PX = 400       # пікселів: стільки червоного видно з ≈ 15-20 см
RED_A = [0, 12, 60, 100, 35, 100]       # відтінок червоного: 0-12 ...
RED_B = [348, 360, 60, 100, 35, 100]    # ... і 348-360 (червоне "перетинає" 0)

stan = "poshuk"
vkhid = time.time()   # коли увійшли в поточний стан
poterya = 0           # скільки кадрів поспіль червоного не видно
PEREPYNKA = 8         # стільки кадрів без червоного ще терпимо
PERESHKODA = 22       # см: ближче цього не червоне = перешкода


def vidstan():
    """Відстань із шумом ±3 см - ускладнення з картки."""
    return ultra.distance_centimeters + random.randint(-30, 30) / 10


def chervonyi():
    """Найбільша червона пляма на знімку: [пікселів, cx, cy, ...] або None."""
    cam.capture_image()
    plyamy = cam.find_blobs(RED_A, 3) + cam.find_blobs(RED_B, 3)
    naikrashcha = None
    for p in plyamy:
        if naikrashcha is None or p[0] > naikrashcha[0]:
            naikrashcha = p
    return naikrashcha


def perekhid(novyi):
    """Єдине місце, де змінюється стан: друк і дії при вході."""
    global stan, vkhid, poterya
    print("%s -> %s" % (stan, novyi))
    stan = novyi
    vkhid = time.time()
    poterya = 0
    if novyi == "poshuk" or novyi == "pereizd":
        gyro.reset()                  # кут повороту рахуємо від входу в стан


while stan != "gotovo":
    d = vidstan()
    b = chervonyi()
    if b is None:
        poterya += 1
    else:
        poterya = 0

    if stan == "poshuk":              # крутимось на місці й шукаємо червоне
        tank.on(SpeedPercent(15), SpeedPercent(-15))
        if b:
            tank.off()
            perekhid("navedennya")
        elif abs(gyro.angle) >= 360:  # повний оберт - червоного не видно
            tank.off()
            perekhid("pereizd")

    elif stan == "navedennya":        # ставимо червону пляму посередині кадру (cx = 50)
        if b is None:
            tank.off()
            if poterya > PEREPYNKA:
                perekhid("poshuk")
        elif abs(b[1] - 50) <= 4:
            tank.off()
            perekhid("pidhid")
        elif b[1] > 50:
            tank.on(SpeedPercent(8), SpeedPercent(-8))
        else:
            tank.on(SpeedPercent(-8), SpeedPercent(8))

    elif stan == "pidhid":            # їдемо до червоного, підправляючи курс по кадру
        if b is None:                 # кадр без червоного: їдемо далі, а за кілька - шукаємо знову
            tank.on(SpeedPercent(10), SpeedPercent(10))
            if poterya > PEREPYNKA:
                tank.off()
                perekhid("poshuk")
        elif d < STOP and b[0] >= BLYZKO_PX:      # поруч і це справді червоне
            tank.off()
            time.sleep(0.3)
            print("зупинка: показ із шумом %.1f см, фактично %.1f см" % (d, ultra.distance_centimeters))
            perekhid("gotovo")
        elif d < PERESHKODA and b[0] < BLYZKO_PX:  # щось не червоне заважає
            tank.off()
            perekhid("pereizd")
        else:
            e = b[1] - 50
            shvydko = 25 if d > 40 else 10
            tank.on(SpeedPercent(shvydko + 0.2 * e), SpeedPercent(shvydko - 0.2 * e))

    elif stan == "pereizd":           # відʼїхати вбік і дивитись знову з іншої точки
        if abs(gyro.angle) < 90:
            tank.on(SpeedPercent(15), SpeedPercent(-15))
        elif d > 35 and time.time() - vkhid < 8:
            tank.on(SpeedPercent(25), SpeedPercent(25))
        else:
            tank.off()
            perekhid("poshuk")

    if stan != "gotovo" and time.time() - vkhid > TAIMAUT:
        print("таймаут у стані", stan)
        tank.off()
        break
