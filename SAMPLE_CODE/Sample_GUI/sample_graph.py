import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
xs = []
ys = []

for i in range(100):
    ax.cla()  # Axes をクリアする。

    xs.append(i)
    if ys:
        ys.append(ys[-1] + np.random.choice([-1, 1]))  # ランダムに -1 or +1 移動
    else:
        ys.append(0)  # 初期値

    ax.set_xlim(0, 100)
    ax.set_ylim(-20, 20)
    ax.plot(xs, ys)

    plt.draw()  # 描画する。
    plt.pause(0.3)  # 0.3 秒ストップする。