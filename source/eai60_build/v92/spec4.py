import spec3
W=dict(spec3.W)
for k in ['L08','L09','L10','L11','L12a','L12b','L13']:
    a,b=W[k];W[k]=(round(a+4.0,2),round(b+4.0,2))
W['L06']=(22.6,31.3);W['L06b']=(31.85,35.45);W['L07']=(35.75,43.63)
TXT0=dict(spec3.TXT)
TXT={}
for k,v in TXT0.items():
    if k=='L06':
        TXT['L06']=[(12,"For structured data, Data Sense maps your ERPs and cloud platforms, so AI understands what your data means.")]
        TXT['L06b']=[(None,"For unstructured data, it builds a semantic content library.")]
    elif k=='L07':
        TXT['L07']=[(13,"The Cross-Application Knowledge Graph connects it all across your business applications, so AI understands the full picture.")]
    else: TXT[k]=v
GAP=dict(spec3.GAP)
