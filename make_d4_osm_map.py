#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D4 map on real OpenStreetMap tiles + route overlay. Tiles © OpenStreetMap contributors."""
import math, requests, io
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

def deg2tile(lon, lat, z):
    n=2**z
    xt=int((lon+180)/360*n)
    import math
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

import math
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

W=(x1-x0+1)*256
H=(y1-y0+1)*256
base=Image.new("RGB",(W,H),(240,240,240))
for (x,y),im in tiles.items():
    base.paste(im, ((x-x0)*256,(y-y0)*256))

ox=x0*256; oy=y0*256
def px(lon,lat):
    gx,gy=lonlat_to_global_px(lon,lat,z)
    return gx-ox, gy-oy

# upscale 2x for readability
scale=2
base_large=base.resize((W*scale,H*scale), Image.LANCZOS)

def px2(lon,lat):
    x,y=px(lon,lat)
    return x*scale, y*scale

draw=ImageDraw.Draw(base_large)
# route: S->1 (bus), 1->2->3->4 walk, 4->5 bus, 5->6 walk
route_order=[0,1,2,3,4,5,6]
pts=[px2(spots[i]["lon"],spots[i]["lat"]) for i in route_order]
# draw thick white casing then gold line
draw.line(pts, fill="white", width=10, joint="curve")
draw.line(pts, fill="#C5A059", width=6, joint="curve")
# dashed effect? PIL no dash, keep solid

# try font
try:
    font_bold=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 22)
    font_reg=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 20)
    font_small=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18)
except:
    try:
        font_bold=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTC-Bold.otf", 22)
        font_reg=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTC-Regular.otf", 20)
        font_small=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTC-Regular.otf", 18)
    except:
        font_bold=ImageFont.load_default()
        font_reg=font_bold
        font_small=font_bold

for s in spots:
    x,y=px2(s["lon"],s["lat"])
    r=18
    # shadow
    draw.ellipse([x-r-2,y-r-2,x+r+2,y+r+2], fill="white")
    draw.ellipse([x-r,y-r,x+r,y+r], fill=s["color"])
    # id text centered
    draw.text((x,y), s["id"], fill="white", font=font_bold, anchor="mm")
    # label box
    label=f'{s["name"]}\n{s["sub"]}'
    # offset to avoid overlap - v2 spread layout
    off={"S":(-210,-110),"1":(170,-110),"2":(-180,-110),"3":(190,80),"4":(-190,90),"5":(190,-110),"6":(190,80)}
    dx,dy=off.get(s["id"],(90,-50))
    tx,ty=x+dx,y+dy
    # measure
    bbox=draw.multiline_textbbox((0,0), label, font=font_small, spacing=2)
    tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
    pad=8
    draw.rounded_rectangle([tx-tw/2-pad,ty-th/2-pad,tx+tw/2+pad,ty+th/2+pad], radius=10, fill="white", outline=s["color"], width=3)
    draw.multiline_text((tx,ty), label, fill="#222222", font=font_small, anchor="mm", align="center", spacing=2)
    # connector
    draw.line([(x,y),(tx,ty)], fill=s["color"], width=2)

# title bar
# crop a bit to bbox
x1p,y1p=px(lon_min,lat_max); x2p,y2p=px(lon_max,lat_min)
x1p*=scale; y1p*=scale; x2p*=scale; y2p*=scale
crop=base_large.crop((int(x1p),int(y1p),int(x2p),int(y2p)))
# add header/footer
header_h=110; footer_h=90
out_w, out_h=crop.size
final=Image.new("RGB",(out_w,out_h+header_h+footer_h),"#FAF8F5")
fd=ImageDraw.Draw(final)
fd.text((out_w//2,38),"D4 1/23(六) 兼六園→金澤城→21世紀美術館→金澤站", fill="#1C1D21", font=font_bold, anchor="mm")
fd.text((out_w//2,72),"OpenStreetMap底圖・08:15桂坂口進・11:30先吃・12:30美術館早場・16:30回車站", fill="#666666", font=font_small, anchor="mm")
final.paste(crop,(0,header_h))
fd.text((out_w//2,out_h+header_h+30),"巴士去・石川橋步行5分・巴士回車站15分・輝壽司候補もりもり/壽司玉", fill="#555555", font=font_small, anchor="mm")
fd.text((out_w-10,out_h+header_h+footer_h-8),"© OpenStreetMap contributors", fill="#888888", font=font_small, anchor="rm")
final.save("travel-kanazawa-2027/d4_osm_map.png")
print("saved", final.size)
