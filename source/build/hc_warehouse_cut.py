"""Cut the supplied SOLIX AI Warehouse artwork (baked checker background) out to RGBA.

Background = neutral light pixels; the object is everything coloured or dark, with
interior highlights filled, glass areas de-checkered and the navy title turned white
for the dark template.

usage: python3 hc_warehouse_cut.py IN.webp OUT_rgba.png
"""
import numpy as np, cv2, sys
img=cv2.imread(sys.argv[1])[:,:,::-1].astype(np.float32)
h,w=img.shape[:2]
ch=img.max(2)-img.min(2); L=img.mean(2)
a=np.maximum(np.clip((ch-4)/22,0,1), np.clip((212-L)/40,0,1))
solid=(a>0.5).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(solid,connectivity=8)
keep=np.zeros(n,bool); keep[1:]=st[1:,4]>300
solid=keep[lab].astype(np.uint8)
# fill interior holes (white highlights / light beam inside the object)
clo=cv2.morphologyEx(solid,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
ff=clo.copy(); mask=np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff,mask,(0,0),1)
holes=(ff==0)
filled=(clo>0)|holes
inner=cv2.erode(filled.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32)
inner=cv2.GaussianBlur(inner,(0,0),1.2)
a=np.maximum(a*keep[lab].astype(np.float32)*0+a*cv2.dilate(filled.astype(np.uint8),np.ones((9,9),np.uint8)), inner)
a=np.clip(a,0,1)
Bv=242.0
F=np.clip((img-(1-a[...,None])*Bv)/np.maximum(a[...,None],1e-3),0,255)
F=np.where(a[...,None]>0.98,img,F)
# de-checker light, low-detail glass areas (period ~24 px): replace by local average there
light=((L>185)&(a>0.9)).astype(np.float32)
k=np.ones((23,23),np.float32)
num=cv2.filter2D(img*light[...,None],-1,k); den=cv2.filter2D(light,-1,k)
avg=num/np.maximum(den[...,None],1e-3)
detail=cv2.Laplacian(cv2.GaussianBlur(L,(0,0),1.0),cv2.CV_32F)
flat=(np.abs(cv2.GaussianBlur(detail,(0,0),3))<4)
sel=(light>0)&flat
F=np.where(sel[...,None],avg,F)
# navy title text -> white (for the dark template), keeping anti-aliasing
yy=np.arange(h)[:,None]
xx=np.arange(w)[None,:]
below=((((xx-725)/352.0)**2+((yy-722)/170.0)**2)>1.03)&(yy>760)
txt=np.clip((215-L)/120,0,1)*(img[...,2]>=img[...,0])
F=np.where(below[...,None],255.0,F)
a=np.where(below,txt,a)
cv2.imwrite(sys.argv[2],cv2.cvtColor(np.dstack([F,a*255]).astype(np.uint8),cv2.COLOR_RGBA2BGRA))
for bg,name in [((255,255,255),'w'),((20,26,70),'d')]:
    o=F*a[...,None]+np.float32(bg)*(1-a[...,None]); cv2.imwrite(f'prev_{name}.png',cv2.resize(o[:,:,::-1],None,fx=0.6,fy=0.6).astype(np.uint8))
