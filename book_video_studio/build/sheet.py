import sys, glob, os
from PIL import Image, ImageDraw
d=sys.argv[1]; out=sys.argv[2]; cols=int(sys.argv[3]) if len(sys.argv)>3 else 2
files=sorted(glob.glob(d+'/snap_*.*'), key=lambda f: float(os.path.basename(f)[5:-4]))
if len(sys.argv)>4: files=[f for f in files if float(os.path.basename(f)[5:-4]) in {float(x) for x in sys.argv[4:]}]
w,h=(1920//cols, 1080//cols); rows=(len(files)+cols-1)//cols
sheet=Image.new('RGB',(w*cols,h*rows))
for i,f in enumerate(files):
    im=Image.open(f).convert('RGB').resize((w,h), Image.LANCZOS)
    ImageDraw.Draw(im).text((10,8), os.path.basename(f)[5:-4]+'s', fill=(255,255,0))
    sheet.paste(im,((i%cols)*w,(i//cols)*h))
sheet.save(out)
