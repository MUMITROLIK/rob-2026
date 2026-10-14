"""
Робота 10 — слідування за лінією в Webots. Заготовка.

Що вже є: мотори в режимі швидкості, три датчики підлоги, помилка й пам'ять
про бік, де лінію бачили востаннє, підсумок прогону.
Що робите ви: PORIH (крок 3) і регулятор у позначеному місці (крок 4).
Вивід — у консолі Webots, унизу вікна.
"""
from controller import Robot

TIMESTEP = 32     # мс, крок світу
BAZA = 1.3        # рад/с — базова швидкість; максимум e-puck 6.28
KP = 0.0          # ← крок 4: підібрати
PORIH = 500       # ← крок 3: свій поріг; менше — під датчиком чорне
CHAS = 60         # с модельного часу на один прогін
MAX = 6.28        # рад/с — більше мотор e-puck не дасть
R = 0.0205        # м — радіус колеса e-puck

robot = Robot()

livyi = robot.getDevice("left wheel motor")
pravyi = robot.getDevice("right wheel motor")
for m in (livyi, pravyi):
    m.setPosition(float("inf"))   # режим швидкості, а не кута
    m.setVelocity(0.0)
enk = [robot.getDevice("left wheel sensor"), robot.getDevice("right wheel sensor")]
for e in enk:
    e.enable(TIMESTEP)            # енкодери коліс: на скільки радіан повернулось колесо

gs = []
for imya in ("gs0", "gs1", "gs2"):        # лівий, центральний, правий
    s = robot.getDevice(imya)
    s.enable(TIMESTEP)                     # без enable датчик мовчить
    gs.append(s)

print("BAZA = %.2f рад/с, KP = %.4f, PORIH = %d" % (BAZA, KP, PORIH))
krokiv = 0
bez_linii = 0
ostannya = 0.0

while robot.step(TIMESTEP) != -1:
    krokiv += 1
    livo, centr, pravo = [s.getValue() for s in gs]

    if krokiv % 16 == 0 and robot.getTime() <= 10:      # перші 10 с, кожні ≈0,5 с
        print("t = %4.1f с   gs0 %4.0f   gs1 %4.0f   gs2 %4.0f" % (robot.getTime(), livo, centr, pravo))

    if min(livo, centr, pravo) < PORIH:      # хоч один датчик бачить лінію
        pomylka = livo - pravo               # > 0 — лінія праворуч
        ostannya = pomylka
    else:                                    # лінію загублено:
        bez_linii += 1                       # крутимося туди, де бачили її востаннє
        pomylka = 600.0 if ostannya >= 0 else -600.0

    # ─── крок 4: ваш регулятор — дві швидкості з BAZA, KP і pomylka ───
    v_l = BAZA
    v_p = BAZA
    # ──────────────────────────────────────────────────────────────────

    v_l = max(-MAX, min(MAX, v_l))
    v_p = max(-MAX, min(MAX, v_p))
    livyi.setVelocity(v_l)
    pravyi.setVelocity(v_p)

    if robot.getTime() >= CHAS:
        livyi.setVelocity(0)
        pravyi.setVelocity(0)
        shlyakh = (enk[0].getValue() + enk[1].getValue()) / 2 * R    # s = кут · r
        print("ПІДСУМОК: KP = %.4f, BAZA = %.2f — без лінії %.1f %% кроків, шлях %.2f м"
              % (KP, BAZA, bez_linii * 100.0 / krokiv, shlyakh))
        break
