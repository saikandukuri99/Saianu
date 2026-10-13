import * as THREE from 'three';
import {RoomEnvironment} from './jsm/environments/RoomEnvironment.js';
export {THREE};
export function stage(canvas,{fov=32,z=9,y=0}={}){
 const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,preserveDrawingBuffer:true});
 renderer.setPixelRatio(1);renderer.setSize(canvas.width,canvas.height,false);renderer.setClearColor(0,0);
 renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.outputColorSpace=THREE.SRGBColorSpace;
 const scene=new THREE.Scene();const pm=new THREE.PMREMGenerator(renderer);scene.environment=pm.fromScene(new RoomEnvironment(),.04).texture;
 const camera=new THREE.PerspectiveCamera(fov,canvas.width/canvas.height,.1,100);camera.position.set(0,y,z);
 const key=new THREE.DirectionalLight(0xffffff,2.2);key.position.set(3,4,5);scene.add(key);
 const rim=new THREE.DirectionalLight(0x0088cf,3);rim.position.set(-4,1,-3);scene.add(rim);
 return {renderer,scene,camera,render:()=>renderer.render(scene,camera)};
}
export function rrect(w,h,r){const s=new THREE.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;}
export function slab(w,h,d,r,color,{metal=.5,rough=.28,emissive=0,ei=0}={}){
 const g=new THREE.ExtrudeGeometry(rrect(w,h,r),{depth:d,bevelEnabled:true,bevelThickness:.03,bevelSize:.03,bevelSegments:4,curveSegments:16});g.translate(0,0,-d/2);
 return new THREE.Mesh(g,new THREE.MeshStandardMaterial({color,metalness:metal,roughness:rough,emissive,emissiveIntensity:ei}));
}
export function textTex(txt,{size=220,color='#fff',w=512,h=512,bg=null,font='800'}={}){
 const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');if(bg){x.fillStyle=bg;x.fillRect(0,0,w,h)}
 x.fillStyle=color;x.font=`${font} ${size}px Inter`;x.textAlign='center';x.textBaseline='middle';x.fillText(txt,w/2,h/2+size*.04);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
export function chip({label='AI'}={}){
 const g=new THREE.Group();
 const base=slab(2.4,2.4,.34,.34,0x141d63,{metal:.7,rough:.3});g.add(base);
 const core=slab(1.7,1.7,.1,.22,0x0a63a8,{metal:.35,rough:.35,emissive:0x0088cf,ei:.22});core.position.z=.2;g.add(core);
 const face=new THREE.Mesh(new THREE.PlaneGeometry(1.5,1.5),new THREE.MeshBasicMaterial({map:textTex(label,{size:300}),transparent:true}));face.position.z=.37;g.add(face);
 const pm=new THREE.MeshStandardMaterial({color:0xcfe3ff,metalness:.9,roughness:.25});
 for(let i=0;i<7;i++){const o=-1.0+i*.333;
  for(const [sx,sy,w,h] of [[o,1.35,.09,.32],[o,-1.35,.09,.32],[1.35,o,.32,.09],[-1.35,o,.32,.09]]){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,.1),pm);m.position.set(sx,sy,0);g.add(m);}}
 return g;
}
export function coin(tex){
 tex.center.set(.5,.5);tex.rotation=Math.PI/2;
 const g=new THREE.Group();
 const side=new THREE.MeshStandardMaterial({color:0xee2424,metalness:.6,roughness:.25});
 const face=new THREE.MeshBasicMaterial({map:tex,toneMapped:false});
 const m=new THREE.Mesh(new THREE.CylinderGeometry(1,1,.2,128),[side,face,face]);m.rotation.x=Math.PI/2;g.add(m);
 const rim=new THREE.Mesh(new THREE.TorusGeometry(1,.055,24,128),new THREE.MeshStandardMaterial({color:0xffffff,metalness:.9,roughness:.2}));rim.position.z=.1;g.add(rim);const rim2=rim.clone();rim2.position.z=-.1;g.add(rim2);
 return g;
}
export function loadTex(url){return new Promise(r=>new THREE.TextureLoader().load(url,t=>{t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;r(t)}));}
