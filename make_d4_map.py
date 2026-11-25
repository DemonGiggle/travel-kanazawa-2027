#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.family'] = ['Noto Sans CJK TC', 'Noto Sans CJK JP', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(12, 9), dpi=200)
ax.set_facecolor('#FAF8F5')
fig.patch.set_facecolor('#FAF8F5')

# lon/lat approx
spots = [
    {"id": "S", "name": "起點\nNeon Hotel\n金澤站附近", "sub": "07:30 出發", "lon": 136.6475, "lat": 36.5775, "color": "#333333"},
    {"id": "1", "name": "1 兼六園 桂坂口", "sub": "08:15 進園 先拍空景\n唐崎松雪吊・徽軫燈籠", "lon": 136.6622, "lat": 36.5618, "color": "#1B7F5A"},
    {"id": "2", "name": "2 金澤城公園", "sub": "09:30 石川橋步行5分\n菱櫓・五十間長屋", "lon": 136.6588, "lat": 36.5659, "color": "#9E2A2B"},
    {"id": "3", "name": "3 午餐 11:30", "sub": "兼六園周邊先吃\n避12:00人潮・熱食暖身", "lon": 136.6605, "lat": 36.5628, "color": "#D Thượng"},
    {"id": "4", "name": "4 21世紀美術館", "sub": "12:30-15:00 早場\n《泳池》地下區要預約", "lon": 136.6577, "lat": 36.5611, "color": "#6A3FB5"},
    {"id": "5", "name": "5 百番街 Anto", "sub": "16:30 登記+買伴手禮\n烏雞庵・落雁", "lon": 136.6486, "lat": 36.5780, "color": "#B7791F"},
    {"id": "6", "name": "6 晚餐 輝壽司", "sub": "17:00前開吃\n候補:もりもり/壽司玉", "lon": 136.6490, "lat": 36.5772, "color": "#C0392B"},
    {"id": "7", "name": "7 FORUS → 回飯店", "sub": "重物最後買\n直接回Neon Hotel", "lon": 136.6495, "lat": 36.5785, "color": "#1B4965"},
]

# fix color typo
for s in spots:
    if s["color"].startswith("#D"):
        s["color"] = "#D67E00"

# background park boxes
ax.add_patch(patches.Rectangle((136.656, 36.560), 0.009, 0.009, facecolor='#D9EDD3', edgecolor='#A9CBA3', linewidth=1.2, zorder=1))
ax.text(136.661, 36.5645, '兼六園\nKenrokuen', ha='center', va='center', fontsize=10, color='#2E6B3A', weight='bold', alpha=0.9, zorder=2)
ax.add_patch(patches.Rectangle((136.6565, 36.5645), 0.006, 0.006, facecolor='#E8DDD0', edgecolor='#C5A059', linewidth=1.2, zorder=1))
ax.text(136.6595, 36.5675, '金澤城', ha='center', va='center', fontsize=9, color='#7A5A2E', weight='bold', zorder=2)
ax.add_patch(patches.Circle((136.6577, 36.5611), 0.0015, facecolor='#E6D9FF', edgecolor='#6A3FB5', linewidth=1.2, zorder=2))

# station area box
ax.add_patch(patches.Rectangle((136.646, 36.576), 0.006, 0.0045, facecolor='#DDEAF5', edgecolor='#1B4965', linewidth=1.2, zorder=1))
ax.text(136.649, 36.5798, '金澤站 Kanazawa St.\n百番街・FORUS・輝壽司', ha='center', va='center', fontsize=9, color='#1B4965', weight='bold', zorder=2)

# draw route lines in order S->1->2->3->4->5(->6->7 very close to station)
order = [spots[0], spots[1], spots[2], spots[3], spots[4], spots[5]]
lons = [p["lon"] for p in order]
lats = [p["lat"] for p in order]

ax.plot(lons, lats, color='#C5A059', linewidth=3.5, linestyle='--', alpha=0.9, zorder=3)

# return leg 4->station (long)
ax.annotate('', xy=(136.6486, 36.5780), xytext=(136.6577, 36.5611),
            arrowprops=dict(arrowstyle='->', color='#C5A059', lw=2.5, ls='--',
                            connectionstyle='arc3,rad=0.15'), zorder=3)
ax.text(136.6525, 36.569, '巴士/計程車\n15分回車站', ha='center', va='center', fontsize=9, color='#7A5A2E',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#C5A059'), zorder=4)

# walking annotation between 1-2
ax.text(136.6605, 36.5642, '石川橋 步行5分', ha='center', fontsize=8.5, color='#9E2A2B',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#9E2A2B'), zorder=5)

# plot points
for s in spots:
    ax.scatter(s["lon"], s["lat"], s=320, c=s["color"], edgecolors='white', linewidths=2, zorder=6)
    ax.text(s["lon"], s["lat"], s["id"], ha='center', va='center', fontsize=11, weight='bold', color='white', zorder=7)
    # label box offset
    # choose offsets to avoid overlap
    offsets = {
        "S": (-0.006, 0.0025),
        "1": (0.0075, 0.0005),
        "2": (-0.007, 0.001),
        "3": (0.007, -0.001),
        "4": (-0.0085, -0.0015),
        "5": (0.007, -0.0005),
        "6": (-0.0075, -0.0018),
        "7": (0.007, 0.001),
    }
    dx, dy = offsets.get(s["id"], (0.006, 0.001))
    ax.text(s["lon"]+dx, s["lat"]+dy, f'{s["name"]}\n{s["sub"]}',
            ha='center', va='center', fontsize=8.5, linespacing=1.4, weight='bold',
            bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=s["color"], lw=1.5),
            zorder=8)

ax.set_xlim(136.642, 136.673)
ax.set_ylim(36.557, 36.582)
ax.set_xlabel('經度 lon → 東', fontsize=9, color='#666')
ax.set_ylabel('緯度 lat → 北', fontsize=9, color='#666')
ax.set_title('D4 1/23(六) 建議路線：兼六園 → 金澤城 → 21世紀美術館 → 金澤站 (避人潮版)', fontsize=14, weight='bold', pad=15, color='#1C1D21')
ax.text(0.5, -0.02,
        '動線不變・只是提早+錯峰：08:15桂坂口進 → 09:30石川橋去金澤城 → 11:30先吃 → 12:30美術館早場 → 16:30回車站登記晚餐',
        transform=ax.transAxes, ha='center', va='top', fontsize=10, color='#555',
        bbox=dict(boxstyle='round,pad=0.4', fc='#FFF8E1', ec='#C5A059'))

ax.grid(True, linestyle=':', alpha=0.4)
plt.tight_layout()
out = 'd4_map.png'
plt.savefig(out, bbox_inches='tight')
print(f'saved {out}')
