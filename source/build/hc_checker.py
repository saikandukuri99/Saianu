"""Remove a baked-in transparency checkerboard from artwork (fragmented-data PNG).

The checker (two tones, ~11 px squares) is rebuilt as a separable soft XOR from a
clean row and column, then every pixel is unmixed against it (minimum alpha),
leaving straight RGBA. Grey translucent squares, which show the checker through
them, are flattened to their mean colour.

usage: python3 hc_checker.py IN.webp OUT_rgba.png
"""
import sys
import numpy as np, cv2
img=cv2.imread(sys.argv[1])[:,:,::-1].astype(np.float32)
h,w=img.shape[:2]
g=img.mean(2)
HI=np.median(img[0:140][g[0:140]>245],0); LO=np.median(img[0:140][(g[0:140]<228)&(g[0:140]>212)],0)
print('HI',HI,'LO',LO)
hm,lm=HI.mean(),LO.mean()
y0=60
u=np.clip((g[y0-3:y0+4].mean(0)*0+g[y0]-lm)/(hm-lm),0,1)
sx=lambda a,b:a+b-2*a*b
def tone_row(y): return np.clip((g[y]-lm)/(hm-lm),0,1)
u=tone_row(y0); v=np.clip((g[:,3]-lm)/(hm-lm),0,1); c0=v[y0]
T=sx(sx(u[None,:],v[:,None]),c0)
B=LO[None,None]+(HI-LO)[None,None]*T[...,None]
err=np.abs(img-B).max(2)
print('bg err top', np.percentile(err[0:140],[50,90,99]), 'bottom', np.percentile(err[880:],[50,90,99]))
# unmix against B (min alpha): c = a*F + (1-a)*B
up=np.clip((img-B)/np.maximum(255-B,1),0,1).max(2)
dn=np.clip((B-img)/np.maximum(B,1),0,1).max(2)
a=np.maximum(up,dn)
a=np.where(a<0.035,0,a)  # residual checker noise
F=np.where(a[...,None]>0,(img-(1-a[...,None])*B)/np.maximum(a[...,None],1e-3),0)
F=np.clip(F,0,255)
chroma=F.max(2)-F.min(2)
lumF=F.mean(2)
a2=a.copy()
a2[(a<0.16)&(chroma<30)]=0
# grey translucent squares: flatten (checker shows through them)
C0=F*a[...,None]+255*(1-a[...,None]); cc=C0.max(2)-C0.min(2); cl=C0.mean(2)
grey=((cc<48)&(cl>110)&(cl<225)&(C0[...,2]>=C0[...,0])).astype(np.uint8)
grey=cv2.morphologyEx(grey,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(grey)
F2=F.copy()
for i in range(1,n):
    x,y,ww,hh,ar=st[i]
    if x>600 and 14<=ww<=60 and 14<=hh<=60 and 0.7<ww/hh<1.4 and ar>0.55*ww*hh:
        m=(lab[y:y+hh,x:x+ww]==i)
        col=np.median(C0[y:y+hh,x:x+ww][m],0); al=1.0
        box=np.zeros((h,w),np.float32); cv2.rectangle(box,(x+1,y+1),(x+ww-2,y+hh-2),1,-1)
        box=cv2.GaussianBlur(box,(0,0),0.8)
        sel=box>0.01
        a2[sel]=np.maximum(a2[sel]*(1-box[sel]), al*box[sel])
        F2[sel]=F2[sel]*(1-box[sel,None])+col*box[sel,None]
        print('sq',x,y,ww,hh,col,al)
rgba=np.dstack([F2,a2*255]).astype(np.uint8)
cv2.imwrite(sys.argv[2],cv2.cvtColor(rgba,cv2.COLOR_RGBA2BGRA))
