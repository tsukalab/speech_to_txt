# https://future-chem.com/matplotlib-plot-type/

import matplotlib.pyplot as plt
import numpy as np


data = [10, 15, 45, 30, 4]
label = ['A', 'B', 'C', 'D', 'E']

# 1つめ
plt.pie(data, labels=label)
plt.show()

def pct_abs(pct, raw_data):
    absolute = int(np.sum(raw_data)*(pct/100.))
    return '{:d}\n({:.0f}%)'.format(absolute, pct) if pct > 5 else ''

# 2つめ
plt.pie(data, counterclock=False, startangle=90, autopct=lambda p: pct_abs(p, data),
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'}, textprops={'color': 'white', 'weight': 'bold'})
plt.axis('equal')
plt.legend(label)
plt.show()

# 3つめ
plt.pie(data, counterclock=False, startangle=90, autopct=lambda p: pct_abs(p, data), pctdistance=0.75,
       textprops={'color': 'white', 'weight':'bold'})
plt.pie([100], colors='white', radius=0.5)
plt.axis('equal')
plt.show()