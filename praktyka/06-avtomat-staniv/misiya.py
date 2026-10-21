from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_2, INPUT_3, INPUT_6
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from ev3dev2.sensor.virtual import CameraSensor
import time

tank = MoveTank(OUTPUT_A, OUTPUT_B)
ultra = UltrasonicSensor(INPUT_2)
gyro = GyroSensor(INPUT_3)
cam = CameraSensor(INPUT_6)         # камера: порт 6 (додана в конфігурації робота)
time.sleep(0.5)

# Місія № 2: знайти ЧЕРВОНИЙ маяк і зупинитись біля нього. Ускладнення № 4:
# стартова позиція невідома, тому GPS у керуванні не використовуємо.
TAIMAUT = 30          # с: найдовше в одному стані
STOP = 12             # см: поріг зупинки (запас до межі 15 см)
BLYZKO_PX = 250       # пікселів: стільки червоного видно з ≈ 12-20 см (під кутом менше)
MALO_PX = 150         # менше пікселів і вже близько - перед нами не маяк, а перешкода
RED_A = [0, 12, 60, 100, 35, 100]       # відтінок червоного: 0-12 ...
RED_B = [348, 360, 60, 100, 35, 100]    # ... і 348-360 (червоне "перетинає" 0)
PEREPYNKA = 25        # стільки кадрів без червоного ще терпимо при наведенні
VTRATA = 150          # стільки кадрів без червоного терпимо по дорозі до маяка (≈ 15 с)
MINPX = 2             # найменша пляма, яку вважаємо маяком (далекий маяк займає 3-4 пікселі)
PERESHKODA = 22       # см: ближче цього не червоне = перешкода
OBLYK = 45            # см: ближче - вже перешкода, не їдемо далі при переїзді
KRUK = 18             # швидкість обертання при пошуку

stan = "poshuk"
vkhid = time.time()   # коли увійшли в поточний стан
poterya = 0           # скільки кадрів поспіль червоного не видно
ostannii = 0          # куди була зміщена пляма востаннє: -1 ліворуч, 1 праворуч
skan = []             # (кут, відстань) за час оберту: де найбільше вільного місця
cil = 360             # кут, до якого довертаємо під час переїзду
kurs = 0              # курс (кут гіроскопа) на маяк: тримаємо його, коли далекий маяк мигає


def chervonyi():
    """Найбільша червона пляма на знімку: [пікселів, cx, cy, ...] або None."""
    cam.capture_image()
    plyamy = cam.find_blobs(RED_A, MINPX) + cam.find_blobs(RED_B, MINPX)
    naikrashcha = None
    for p in plyamy:
        if naikrashcha is None or p[0] > naikrashcha[0]:
            naikrashcha = p
    return naikrashcha


def perekhid(novyi):
    """Єдине місце, де змінюється стан: друк і дії при вході."""
    global stan, vkhid, poterya, skan, kurs
    print("%s -> %s" % (stan, novyi))
    stan = novyi
    vkhid = time.time()
    poterya = 0
    if novyi == "pidhid":
        kurs = gyro.angle             # курс на маяк, який тримаємо, поки далекий маяк мигає
    if novyi == "poshuk":
        gyro.reset()                  # кут повороту рахуємо від початку оберту
        skan = []


while stan != "gotovo":
    d = ultra.distance_centimeters
    b = chervonyi()
    if b is None:
        poterya += 1
    else:
        poterya = 0
        ostannii = 1 if b[1] > 50 else -1
        if stan == "pidhid" and abs(b[1] - 50) <= 10:
            kurs = gyro.angle         # маяк по центру: запамʼятовуємо курс на нього

    if stan == "poshuk":              # крутимось на місці й шукаємо червоне
        tank.on(SpeedPercent(KRUK), SpeedPercent(-KRUK))
        skan.append((abs(gyro.angle), d))
        if b:
            tank.off()
            perekhid("navedennya")
        elif abs(gyro.angle) >= 360:  # повний оберт - червоного не видно
            tank.off()
            naikr = max(skan, key=lambda s: s[1])
            cil = 360 + naikr[0]      # довертаємо туди, де було найбільше вільного місця
            perekhid("pereizd")

    elif stan == "navedennya":        # ставимо червону пляму посередині кадру (cx = 50)
        if b is None:
            tank.on(SpeedPercent(6 * ostannii), SpeedPercent(-6 * ostannii))   # далі в той самий бік
            if poterya > PEREPYNKA:
                tank.off()
                perekhid("poshuk")
        elif abs(b[1] - 50) <= 6:
            tank.off()
            perekhid("pidhid")
        elif b[1] > 50:
            tank.on(SpeedPercent(8), SpeedPercent(-8))
        else:
            tank.on(SpeedPercent(-8), SpeedPercent(8))

    elif stan == "pidhid":            # їдемо до червоного, підправляючи курс по кадру
        if b is None:                 # далекий маяк мигає: їдемо далі за гіроскопом, а якщо довго нема чи перешкода - шукаємо
            v = 40 if d > 80 else (25 if d > 40 else 10)
            pomylka = max(-20, min(20, gyro.angle - kurs))
            tank.on(SpeedPercent(v - 0.8 * pomylka), SpeedPercent(v + 0.8 * pomylka))
            if d < PERESHKODA:
                tank.off()
                perekhid("pereizd")
            elif poterya > VTRATA:
                tank.off()
                perekhid("poshuk")
        elif d < STOP and b[0] >= BLYZKO_PX:      # поруч і це справді червоне
            tank.off()
            time.sleep(0.3)
            print("зупинка: показ %.1f см, фактично %.1f см" % (d, ultra.distance_centimeters))
            perekhid("gotovo")
        elif d < PERESHKODA and b[0] < MALO_PX:    # щось не червоне заважає
            tank.off()
            perekhid("pereizd")
        else:
            e = b[1] - 50
            shvydko = 40 if d > 80 else (25 if d > 40 else 10)
            tank.on(SpeedPercent(shvydko + 0.2 * e), SpeedPercent(shvydko - 0.2 * e))

    elif stan == "pereizd":           # довернути до вільного напрямку, проїхати й дивитись знову
        if b and d > OBLYK and abs(gyro.angle) >= cil and time.time() - vkhid > 5:
            tank.off()                # відʼїхали вбік достатньо й бачимо червоне - наводимось знову
            perekhid("navedennya")
        elif abs(gyro.angle) < cil:
            tank.on(SpeedPercent(KRUK), SpeedPercent(-KRUK))
        elif d > OBLYK and time.time() - vkhid < 12:
            tank.on(SpeedPercent(25), SpeedPercent(25))
        else:
            tank.off()
            perekhid("poshuk")

    if stan != "gotovo" and time.time() - vkhid > TAIMAUT:
        print("таймаут у стані", stan)
        tank.off()
        break
