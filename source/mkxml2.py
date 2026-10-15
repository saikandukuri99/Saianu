import subprocess
R='<rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate>'
def n(f): return int(subprocess.check_output(['ffprobe','-v','error','-count_packets','-select_streams','v','-show_entries','stream=nb_read_packets','-of','csv=p=0','out/fm/'+f]).strip())
cid=[0]
def track(files):
    out='';t=0
    for nm in files:
        d=n(nm);cid[0]+=1;i=cid[0]
        out+=f"""<clipitem id="c{i}"><name>{nm}</name><duration>{d}</duration>{R}<start>{t}</start><end>{t+d}</end><in>0</in><out>{d}</out>
<file id="f{i}"><name>{nm}</name><pathurl>{nm}</pathurl>{R}<duration>{d}</duration><media><video><samplecharacteristics><width>3840</width><height>2160</height></samplecharacteristics></video></media></file></clipitem>"""
        t+=d
    return '<track>'+out+'</track>'
x=f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4"><sequence id="seq1"><name>SOLIXCloud ECS - Keep the Proof - 4K</name><duration>1800</duration>{R}
<media><video><format><samplecharacteristics><width>3840</width><height>2160</height><pixelaspectratio>square</pixelaspectratio>{R}</samplecharacteristics></format>
<track></track>
{track(['ECS_GFX_4K_FILL_part0.mp4','ECS_GFX_4K_FILL_part1.mp4'])}
{track(['ECS_GFX_4K_MATTE.mp4'])}
{track(['ECS_Captions_4K_FILL.mp4'])}
{track(['ECS_Captions_4K_MATTE.mp4'])}
</video><audio><track><clipitem id="vo"><name>ECS_KeepTheProof_VO_48k24.wav</name><duration>1800</duration>{R}<start>0</start><end>1800</end><in>0</in><out>1800</out>
<file id="fvo"><name>ECS_KeepTheProof_VO_48k24.wav</name><pathurl>ECS_KeepTheProof_VO_48k24.wav</pathurl>{R}<duration>1800</duration><media><audio><samplecharacteristics><depth>24</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>1</channelcount></audio></media></file></clipitem></track></audio></media></sequence></xmeml>"""
open('out/fm/ECS_KeepTheProof_Premiere.xml','w').write(x)
