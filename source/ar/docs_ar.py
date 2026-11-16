# 3D product documents for the Access beat: Solix Search, the purchase-to-pay record
# (PO -> goods receipt -> invoice -> payment) and a standard report, drawn as textures and
# placed in 3D with true perspective (homography), soft shadows and a light sheen.
# All names and numbers are fictional demo data.
import math, os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/opentype/inter/"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
INK = (24, 22, 48); MUTE = (118, 116, 140); PAPER = (251, 251, 253)
INDIGO = (48, 38, 123); BLUE = (0, 136, 207); RED = (238, 36, 36); TINT = (240, 241, 248)

@lru_cache(None)
def F(name, size): return ImageFont.truetype(FD + name, size)
@lru_cache(None)
def icon(h):
    im = Image.open(f"{ASSETS}/icon.png").convert("RGBA")
    return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)

def tracked(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += font.getlength(ch) + track

VENDOR = "Halden Industrial Supply"
ITEMS = [("Hydraulic pump assembly", "4", "$28,400.00"), ("Valve kit, stainless", "12", "$9,600.00"), ("Freight", "1", "$1,250.00")]
TOTAL = "$39,250.00"

def paper(w, h, head, title, number):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w-1, h-1), 30, fill=PAPER + (255,))
    d.rounded_rectangle((0, 0, w-1, 170), 30, fill=head + (255,)); d.rectangle((0, 120, w-1, 170), fill=head + (255,))
    tracked(d, (52, 52), title, F("Inter-SemiBold.otf", 34), (255, 255, 255), 6)
    d.text((52, 98), "Archived in SOLIXCloud", font=F("Inter-Medium.otf", 24), fill=(220, 222, 245))
    d.text((52, 200), number, font=F("InterDisplay-Bold.otf", 66), fill=INK)
    return im, d

def field(d, x, y, label, value, vs=34):
    d.text((x, y), label.upper(), font=F("Inter-SemiBold.otf", 20), fill=MUTE)
    d.text((x, y + 30), value, font=F("InterDisplay-SemiBold.otf", vs), fill=INK)

def items(d, x, y, w, mode="amount"):
    for i, (name, q, amt) in enumerate(ITEMS):
        yy = y + i*62
        if i % 2 == 0: d.rounded_rectangle((x-16, yy-12, x+w+16, yy+46), 12, fill=TINT)
        d.text((x, yy), name, font=F("Inter-Medium.otf", 28), fill=INK)
        if mode == "amount":
            d.text((x + w - 300, yy), f"×{q}", font=F("Inter-Medium.otf", 28), fill=MUTE)
            d.text((x + w, yy), amt, font=F("Inter-SemiBold.otf", 28), fill=INK, anchor="ra")
        else:
            d.text((x + w, yy), f"{q} of {q}  ✓", font=F("Inter-SemiBold.otf", 28), fill=BLUE, anchor="ra")

def pill(d, x, y, text, col):
    f = F("Inter-SemiBold.otf", 26); tw = f.getlength(text)
    d.rounded_rectangle((x, y, x + tw + 44, y + 50), 25, fill=tuple(int(c*.12 + 255*.88) for c in col))
    d.text((x + 22, y + 10), text, font=f, fill=col)

W_, H_ = 760, 900
@lru_cache(None)
def doc(kind, stamp=0):
    if kind == "po":
        im, d = paper(W_, H_, INDIGO, "PURCHASE ORDER", "PO-118204")
        field(d, 52, 300, "Vendor", VENDOR); field(d, 52, 400, "Ordered", "28 Mar 2019"); field(d, 420, 400, "Buyer", "Plant 3")
        items(d, 52, 530, W_-104)
        field(d, 52, 760, "Order total", TOTAL, 52); pill(d, 470, 790, "Approved", BLUE)
    elif kind == "gr":
        im, d = paper(W_, H_, INDIGO, "GOODS RECEIPT", "GR-55031")
        field(d, 52, 300, "Against", "PO-118204"); field(d, 420, 300, "Received", "08 Apr 2019")
        field(d, 52, 400, "Location", "Warehouse 3, Dock B")
        items(d, 52, 530, W_-104, mode="qty")
        field(d, 52, 760, "Status", "Received in full", 44)
    elif kind == "inv":
        im, d = paper(W_, H_, BLUE, "INVOICE", "INV-2019-04417")
        field(d, 52, 300, "Vendor", VENDOR); field(d, 52, 400, "Invoice date", "12 Apr 2019"); field(d, 420, 400, "PO", "PO-118204")
        items(d, 52, 530, W_-104)
        field(d, 52, 760, "Amount due", TOTAL, 52); pill(d, 400, 790, "3-way matched", BLUE)
    elif kind == "pay":
        im, d = paper(W_, H_, BLUE, "PAYMENT", "PMT-90876")
        field(d, 52, 300, "Paid to", VENDOR); field(d, 52, 400, "Paid on", "10 May 2019"); field(d, 420, 400, "Method", "ACH")
        field(d, 52, 510, "For invoice", "INV-2019-04417")
        d.text((52, 640), "AMOUNT PAID", font=F("Inter-SemiBold.otf", 20), fill=MUTE)
        d.text((52, 672), TOTAL, font=F("InterDisplay-Bold.otf", 92), fill=INK)
        if stamp:
            st = Image.new("RGBA", (420, 190), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((8, 8, 412, 182), 26, outline=RED + (235,), width=12)
            sd.text((210, 95), "PAID", font=F("InterDisplay-Bold.otf", 112), fill=RED + (235,), anchor="mm")
            st = st.rotate(-14, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(st, (W_ - st.width - 16, 560))
    elif kind == "report":
        w, h = 1180, 820
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w-1, h-1), 30, fill=PAPER + (255,))
        d.rounded_rectangle((0, 0, w-1, 150), 30, fill=INDIGO + (255,)); d.rectangle((0, 110, w-1, 150), fill=INDIGO + (255,))
        tracked(d, (56, 44), "STANDARD REPORT", F("Inter-SemiBold.otf", 32), (255, 255, 255), 6)
        d.text((56, 90), "Opened from the archive. No legacy application needed.", font=F("Inter-Medium.otf", 24), fill=(220, 222, 245))
        d.text((56, 185), "Invoices by vendor · FY2019", font=F("InterDisplay-Bold.otf", 56), fill=INK)
        d.text((56, 258), VENDOR, font=F("InterDisplay-Medium.otf", 32), fill=MUTE)
        rows = [("INV-2019-04417", "12 Apr 2019", "$39,250.00", "Paid"), ("INV-2019-05102", "03 May 2019", "$12,980.00", "Paid"),
                ("INV-2019-07736", "18 Jul 2019", "$31,440.00", "Paid"), ("INV-2019-08120", "02 Aug 2019", "$7,615.00", "Paid")]
        hf = F("Inter-SemiBold.otf", 20)
        for x, lab in ((56, "INVOICE"), (420, "DATE"), (700, "AMOUNT"), (960, "STATUS")): d.text((x, 340), lab, font=hf, fill=MUTE)
        for i, r in enumerate(rows):
            y = 390 + i*70
            if i == 0: d.rounded_rectangle((36, y-16, w-36, y+50), 14, fill=(225, 240, 250))
            elif i % 2 == 0: d.rounded_rectangle((36, y-16, w-36, y+50), 14, fill=TINT)
            f = F("Inter-SemiBold.otf" if i == 0 else "Inter-Medium.otf", 30)
            d.text((56, y), r[0], font=f, fill=INK); d.text((420, y), r[1], font=f, fill=INK)
            d.text((870, y), r[2], font=f, fill=INK, anchor="ra"); d.text((960, y), r[3], font=f, fill=BLUE)
        d.text((56, 700), "Total", font=F("Inter-SemiBold.otf", 30), fill=MUTE)
        d.text((870, 690), "$91,285.00", font=F("InterDisplay-Bold.otf", 44), fill=INK, anchor="ra")
    return im

@lru_cache(None)
def search(nchars, rows, hl):
    w, h = 1280, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w-1, h-1), 34, fill=PAPER + (255,))
    im.alpha_composite(icon(56), (48, 40))
    d.text((122, 46), "Solix Search", font=F("InterDisplay-SemiBold.otf", 40), fill=INK)
    d.text((w-48, 56), "Application Retirement", font=F("Inter-Medium.otf", 26), fill=MUTE, anchor="ra")
    d.rounded_rectangle((48, 130, w-48, 226), 48, fill=TINT, outline=BLUE + (255,) if nchars else None, width=3)
    d.ellipse((86, 160, 116, 190), outline=MUTE, width=5); d.line((112, 186, 126, 200), fill=MUTE, width=6)
    q = VENDOR[:nchars]
    d.text((150, 152), q if q else "Search archived records", font=F("Inter-Medium.otf", 40), fill=INK if q else MUTE)
    if 0 < nchars < len(VENDOR):
        x = 150 + F("Inter-Medium.otf", 40).getlength(q) + 4; d.rectangle((x, 156, x + 4, 202), fill=BLUE)
    res = [(VENDOR, "Vendor · 1,284 archived records"), ("INV-2019-04417", "Invoice · $39,250.00 · Paid"),
           ("PO-118204", "Purchase order · Approved"), ("GR-55031", "Goods receipt · Received in full")]
    for i in range(rows):
        y = 262 + i*118
        if hl and i == 0: d.rounded_rectangle((48, y, w-48, y+102), 22, fill=(225, 240, 250), outline=BLUE + (255,), width=3)
        d.text((86, y + 14), res[i][0], font=F("InterDisplay-SemiBold.otf", 38), fill=INK)
        d.text((86, y + 60), res[i][1], font=F("Inter-Medium.otf", 26), fill=BLUE if (hl and i == 0) else MUTE)
    return im

# ---------------------------------------------------------------- 3D placement
def rot(P, yaw, pitch, roll):
    cr, sr = math.cos(roll), math.sin(roll); cp, sp = math.cos(pitch), math.sin(pitch); cy, sy = math.cos(yaw), math.sin(yaw)
    x, y, z = P[:, 0]*cr - P[:, 1]*sr, P[:, 0]*sr + P[:, 1]*cr, P[:, 2]
    y, z = y*cp - z*sp, y*sp + z*cp
    x, z = x*cy + z*sy, -x*sy + z*cy
    return np.stack([x, y, z], 1)

class Cam:
    def __init__(self, cx, cy, f, D, yaw=0.0, pitch=0.0):
        self.cx, self.cy, self.f, self.D, self.yaw, self.pitch = cx, cy, f, D, yaw, pitch
    def proj(self, P):
        P = rot(P, self.yaw, self.pitch, 0.0)
        z = P[:, 2] + self.D
        s = self.f/np.maximum(z, .2)
        return np.stack([self.cx + P[:, 0]*s, self.cy - P[:, 1]*s], 1), z

def quad(cam, center, w, h, yaw=0.0, pitch=0.0, roll=0.0):
    C = np.array([[-w/2, h/2, 0], [w/2, h/2, 0], [w/2, -h/2, 0], [-w/2, -h/2, 0]], float)
    Pw = rot(C, yaw, pitch, roll) + np.asarray(center, float)
    q, z = cam.proj(Pw)
    n = rot(np.array([[0, 0, -1.0]]), yaw, pitch, roll)
    n = rot(n, cam.yaw, cam.pitch, 0)[0]
    return q, n, z.mean()

def _coeffs(dst, src):
    A = []; b = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float))

def draw(frame, tex, q, n, alpha=1.0, sheen=None, shadow=.5, W=1920, H=1080):
    """Composite a texture onto the 4-point screen quad q (TL, TR, BR, BL) with perspective."""
    if alpha <= .003: return
    x0, y0 = np.floor(q.min(0)).astype(int) - 2; x1, y1 = np.ceil(q.max(0)).astype(int) + 2
    if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H or x1 - x0 > 4000 or y1 - y0 > 4000: return
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1); bw, bh = x1 - x0, y1 - y0
    tw, th = tex.size
    co = _coeffs(q - [x0, y0], [(0, 0), (tw, 0), (tw, th), (0, th)])
    img = tex.transform((bw, bh), Image.PERSPECTIVE, tuple(co), Image.BICUBIC)
    a = np.asarray(img, np.float32)/255
    al = a[..., 3:]*alpha
    facing = max(0.0, -n[2]) if n[2] < 0 else 0.0
    rgb = a[..., :3]*(.72 + .28*facing)
    if sheen is not None:
        yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
        u = (xx + yy*.6)/(bw + bh*.6)
        rgb = rgb + .45*np.exp(-((u - sheen)/.06)**2)[..., None]*(1 - rgb*.5)
    # clip to frame
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    sl = (slice(fy0-y0, fy1-y0), slice(fx0-x0, fx1-x0))
    if shadow:
        sh = Image.fromarray((a[..., 3]*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(float(max(6, bw*.05))))
        sa = np.asarray(sh, np.float32)[..., None]/255*shadow*alpha
        oy = int(bh*.06); ox = int(bw*.03)
        sx0, sy0, sx1, sy1 = max(0, x0+ox), max(0, y0+oy), min(W, x1+ox), min(H, y1+oy)
        if sx1 > sx0 and sy1 > sy0:
            ss = sa[sy0-y0-oy:sy1-y0-oy, sx0-x0-ox:sx1-x0-ox]
            reg = frame[sy0:sy1, sx0:sx1]; reg[:] = reg*(1 - ss) + np.array([.03, .01, .08], np.float32)*ss
    reg = frame[fy0:fy1, fx0:fx1]
    aa = al[sl]; reg[:] = reg*(1 - aa) + rgb[sl]*aa

def to_pil(im): return im
