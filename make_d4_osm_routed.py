#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D4 OSM routed version: lines follow streets via OSMDE (car for bus legs, foot for walks)."""
import io, math, requests
from PIL import Image, ImageDraw, ImageFont

spots = [
    {"id":"S", "name":"S Neon Hotel","sub":"07:30出發 金澤站旁","lon":136.6475, "lat":36.5779, "color":"#333333"},
    {"id":"1", "name":"1 兼六園 桂坂口","sub":"08:15進園 雪吊/燈籠","lon":136.6622, "lat":36.5618, "color":"#1B7F5A"},
    {"id":"2", "name":"2 金澤城公園","sub":"09:30 石川橋步行5分","lon":136.6588, "lat":36.5659, "color":"#9E2A2B"},
    {"id":"3", "name":"3 午餐 11:30","sub":"兼六園周邊 熱食暖身","lon":136.6605, "lat":36.5628, "color":"#B7791F"},
    {"id":"4", "name":"4 21世紀美術館","sub":"12:30早場 泳池要預約","lon":136.6577, "lat":36.5611, "color":"#6A3FB5"},
    {"id":"5", "name":"5 百番街 Anto","sub":"16:30登記+伴手禮","lon":136.6480, "lat":36.5782, "color":"#C97A17"},
    {"id":"6", "name":"6 輝壽司","sub":"17:00前開吃","lon":136.6488, "lat":36.5776, "color":"#C0392B"},
]
idx={s["id"]:s for s in spots}
legs=[("S","1","car"),("1","2","foot"),("2","3","foot"),("3","4","foot"),("4","5","car"),("5","6","foot")]

def fetch(a,b,mode):
    lon1,lat1=idx[a]["lon"],idx[a]["lat"]
    lon2,lat2=idx[b]["lon"],idx[b]["lat"]
    base="https://routing.openstreetmap.de/routed-car" if mode=="car" else "https://routing.openstreetmap.de/routed-foot"
    url=f"{base}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson&steps=false"
    r=requests.get(url, headers={"User-Agent":"kanazawa-trip-demo/1.0"}, timeout=25)
    r.raise_for_status()
    j=r.json()
    coords=j["routes"][0]["geometry"]["coordinates"]  # lon,lat
    dist=j["routes"][0]["distance"]; dur=j["routes"][0]["duration"]
    print(f"{a}->{b} {mode} {dist:.0f}m {dur/60:.1f}min pts={len(coords)}")
    return coords, dist, dur

routes=[]
for a,b,m in legs:
    c,d,du=fetch(a,b,m)
    routes.append({"from":a,"to":b,"mode":m,"coords":c,"dist":d,"dur":du})

# --- tiles ---
def deg2tile(lon, lat, z):
    n=2**z
    xt=int((lon+180)/360*n)
    lat_r=math.radians(lat)
    yt=int((1.0-math.log(math.tan(lat_r)+1/math.cos(lat_r))/math.pi)/2.0*n)
    return xt, yt
def lonlat_to_global_px(lon,lat,z):
    n=2**z
    x=(lon+180)/360*n*256
    lat_r=math.radians(lat)
    y=(1.0-math.log(math.tan(lat_r)+1/math.cos(lat_r))/math.pi)/2.0*n*256
    return x,y

z=15
lon_min, lon_max = 136.640, 136.673
lat_min, lat_max = 36.556, 36.584
x0,y0 = deg2tile(lon_min, lat_max, z)
x1,y1 = deg2tile(lon_max, lat_min, z)
print(f"z={z} x {x0}-{x1} y {y0}-{y1}")
tiles={}
for x in range(x0, x1+1):
    for y in range(y0, y1+1):
        url=f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        r=requests.get(url, headers={"User-Agent":"kanazawa-trip-demo/1.0"}, timeout=20)
        print(x,y,r.status_code)
        if r.status_code==200:
            tiles[(x,y)]=Image.open(io.BytesIO(r.content)).convert("RGB")
W=(x1-x0+1)*256; H=(y1-y0+1)*256
base=Image.new("RGB",(W,H),(240,240,240))
for (x,y),im in tiles.items():
    base.paste(im, ((x-x0)*256,(y-y0)*256))
ox=x0*256; oy=y0*256
scale=2
base_large=base.resize((W*scale,H*scale), Image.LANCZOS)
def px2(lon,lat):
    gx,gy=lonlat_to_global_px(lon,lat,z)
    return (gx-ox)*scale, (gy-oy)*scale

draw=ImageDraw.Draw(base_large)

def draw_solid(pts, color, width):
    draw.line(pts, fill="white", width=width+4, joint="curve")
    draw.line(pts, fill=color, width=width, joint="curve")

def draw_dashed(pts, color, width, dash=14, gap=10):
    # white casing solid first
    draw.line(pts, fill="white", width=width+4, joint="curve")
    # dashed color: walk along segments
    for i in range(len(pts)-1):
        x1,y1=pts[i]; x2,y2=pts[i+1]
        seg_len=math.hypot(x2-x1,y2-y1)
        if seg_len==0: continue
        # subdivide
        n=int(seg_len/4)+1
        # we track distance along whole polyline for dash pattern continuity (simplified per-segment)
        t=0
        while t<seg_len:
            t0=t; t1=min(t+dash, seg_len)
            f0=t0/seg_len; f1=t1/seg_len
            sx1=x1+(x2-x1)*f0; sy1=y1+(y2-y1)*f0
            sx2=x1+(x2-x1)*f1; sy2=y1+(y2-y1)*f1
            draw.line([(sx1,sy1),(sx2,sy2)], fill=color, width=width)
            t+=dash+gap

CAR="#E67E22"; FOOT="#1B7F5A"
for rt in routes:
    pts=[px2(lon,lat) for lon,lat in rt["coords"]]
    if rt["mode"]=="car":
        draw_solid(pts, CAR, 6)
    else:
        draw_dashed(pts, FOOT, 6)

try:
    font_bold=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 22)
    font_small=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18)
    font_reg=font_small
except:
    try:
        font_bold=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTC-Bold.otf", 22)
        font_small=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTC-Regular.otf", 18)
        font_reg=font_small
    except:
        font_bold=ImageFont.load_default(); font_reg=font_bold; font_small=font_bold

for s in spots:
    x,y=px2(s["lon"],s["lat"])
    r=18
    draw.ellipse([x-r-2,y-r-2,x+r+2,y+r+2], fill="white")
    draw.ellipse([x-r,y-r,x+r,y+r], fill=s["color"])
    draw.text((x,y), s["id"], fill="white", font=font_bold, anchor="mm")
    label=f'{s["name"]}\n{s["sub"]}'
    off={"S":(-210,-110),"1":(170,-110),"2":(-180,-110),"3":(190,80),"4":(-190,90),"5":(190,-110),"6":(190,80)}
    dx,dy=off.get(s["id"],(90,-50))
    tx,ty=x+dx,y+dy
    bbox=draw.multiline_textbbox((0,0), label, font=font_small, spacing=2)
    tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
    pad=8
    draw.rounded_rectangle([tx-tw/2-pad,ty-th/2-pad,tx+tw/2+pad,ty+th/2+pad], radius=10, fill="white", outline=s["color"], width=3)
    draw.multiline_text((tx,ty), label, fill="#222222", font=font_small, anchor="mm", align="center", spacing=2)
    draw.line([(x,y),(tx,ty)], fill=s["color"], width=2)

# legend box top-left inside map
# crop first
def px_raw(lon,lat):
    gx,gy=lonlat_to_global_px(lon,lat,z)
    return gx-ox, gy-oy
x1p,y1p=px_raw(lon_min,lat_max); x2p,y2p=px_raw(lon_max,lat_min)
x1p*=scale; y1p*=scale; x2p*=scale; y2p*=scale
crop=base_large.crop((int(x1p),int(y1p),int(x2p),int(y2p)))
header_h=110; footer_h=110
out_w, out_h=crop.size
final=Image.new("RGB",(out_w,out_h+header_h+footer_h),"#FAF8F5")
fd=ImageDraw.Draw(final)
fd.text((out_w//2,38),"D4 1/23(六) 兼六園→金澤城→21世紀美術館→金澤站 (街道版)", fill="#1C1D21", font=font_bold, anchor="mm")
fd.text((out_w//2,72),"橘實線=巴士/車行・綠虛線=步行・OSM街道繞行", fill="#666666", font=font_small, anchor="mm")
final.paste(crop,(0,header_h))
# legend
fd.text((out_w//2,out_h+header_h+22),"S→1巴士3.2km・1→2→3→4步行共2km・4→5巴士3.1km・5→6步行0.3km", fill="#555555", font=font_small, anchor="mm")
fd.text((out_w//2,out_h+header_h+50),"巴士去・石川橋步行5分・巴士回車站15分・輝壽司候補もりもり/壽司玉", fill="#555555", font=font_small, anchor="mm")
fd.text((out_w-10,out_h+header_h+footer_h-8),"© OpenStreetMap contributors・routing: OSMDE", fill="#888888", font=font_small, anchor="rm")
final.save("travel-kanazawa-2027/d4_osm_map.png")
print("saved", final.size)

# --- HTML ---
import json
html_routes=[]
for rt in routes:
    # leaflet wants [lat,lon]
    ll=[[lat,lon] for lon,lat in rt["coords"]]
    html_routes.append({"from":rt["from"],"to":rt["to"],"mode":rt["mode"],"ll":ll})
html=f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>D4 1/23 街道版 OpenStreetMap互動版</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>body{{margin:0;font-family:sans-serif}}#map{{height:92vh}}.bar{{padding:10px;background:#FAF8F5}}</style>
</head>
<body>
<div class="bar"><b>D4 1/23(六) 街道版：橘=車/巴士 綠虛=步行</b>・底圖 © OpenStreetMap contributors・繞行 routing.openstreetmap.de</div>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map=L.map('map').setView([36.569,136.655],13);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19,attribution:'© OpenStreetMap contributors'}}).addTo(map);
var routes={json.dumps(html_routes)};
var labels={{"S":"S Neon Hotel 07:30出發","1":"1 兼六園桂坂口 08:15雪吊","2":"2 金澤城 09:30石川橋5分","3":"3 午餐11:30熱食","4":"4 美術館12:30泳池預約","5":"5 百番街16:30伴手禮","6":"6 輝壽司17:00"}};
var pts={{ "S":[36.5779,136.6475],"1":[36.5618,136.6622],"2":[36.5659,136.6588],"3":[36.5628,136.6605],"4":[36.5611,136.6577],"5":[36.5782,136.6480],"6":[36.5776,136.6488] }};
Object.keys(pts).forEach(k=>{{ L.marker(pts[k]).addTo(map).bindPopup(labels[k]); }});
routes.forEach(r=>{{
  if(r.mode==='car') L.polyline(r.ll,{{color:'#E67E22',weight:5}}).addTo(map);
  else L.polyline(r.ll,{{color:'#1B7F5A',weight:5,dashArray:'10 8'}}).addTo(map);
}});
var all=[]; routes.forEach(r=>{{ all=all.concat(r.ll); }});
map.fitBounds(all,{{padding:[30,30]}});
</script>
</body>
</html>"""
open("travel-kanazawa-2027/d4_osm_map.html","w",encoding="utf-8").write(html)
print("html saved")
