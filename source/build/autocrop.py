import sys, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
def bbox(path):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int)
    bright=(a.mean(axis=2)>150)
    H,W=bright.shape
    cols=bright.mean(0); rows=bright.mean(1)
    def rng(v,th):
        idx=np.where(v>th)[0]
        # longest contiguous run
        best=(0,0);s=idx[0];p=idx[0]
        for i in list(idx[1:])+[10**9]:
            if i!=p+1:
                if p-s>best[1]-best[0]: best=(s,p)
                s=i
            p=i
        return best
    x0,x1=rng(cols,0.25); 
    sub=bright[:,x0:x1+1].mean(1); y0,y1=rng(sub,0.5)
    return x0,y0,x1,y1
if __name__=="__main__":
    out=sys.argv[1]
    for p in sys.argv[2:]:
        x0,y0,x1,y1=bbox(p); m=2
        im=Image.open(p).convert('RGB').crop((x0+m,y0+m,x1-m,y1-m))
        w,h=im.size; sc=2.0
        im=im.resize((int(w*sc),int(h*sc)),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2,80,2))
        n=p.split('/')[-1]; im.save(f"{out}/{n}"); print(n,(x0,y0,x1,y1),im.size)
