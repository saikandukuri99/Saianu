// Core of the 3D engine: renderer, lights, shader background, camera rig, post-processing, transitions, captions.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export const V = {};                 // visual registry: V.name = ctx => update(lt)
export const W = 1920, H = 1080;
export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (lt, a, b) => clamp((lt - a) / (b - a));
export const E = {
  lin: t => t, out2: t => 1 - (1 - t) ** 2, out3: t => 1 - (1 - t) ** 3, out5: t => 1 - (1 - t) ** 5, in2: t => t * t, in3: t => t * t * t,
  inOut: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  backBig: t => { const c1 = 2.8, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  elastic: t => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1,
};
export const bob = (lt, amp = .1, f = 1, ph = 0) => Math.sin(lt * f * Math.PI * 2 + ph) * amp;
export function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

// ------------------------------------------------------------------ renderer
export const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
export const RW = 1600, RH = 900;
renderer.setPixelRatio(1); renderer.setSize(RW, RH);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NoToneMapping;           // tone mapping happens inside the final FX pass
document.getElementById('gl').appendChild(renderer.domElement);

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(32, W / H, .1, 200);
camera.setViewOffset(W, H, 0, 30, W, H);                // content sits a little higher, captions get the bottom

// image based lighting from a procedural studio (soft boxes), used for glossy reflections
{
  const env = new THREE.Scene();
  env.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.MeshBasicMaterial({ side: THREE.BackSide, color: 0x1b2050 })));
  const box = (c, i, p, s) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(s[0], s[1]), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(i), side: THREE.DoubleSide })); m.position.set(...p); m.lookAt(0, 0, 0); env.add(m); };
  box(0xffffff, 6, [-14, 18, 14], [26, 14]); box(0xffd9a0, 4, [20, 8, 10], [10, 22]); box(0x6aa8ff, 3.5, [0, -12, -22], [40, 8]); box(0xff7ad9, 2.5, [-22, 2, -10], [8, 26]);
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(env, .02).texture; pm.dispose();
}

// ------------------------------------------------------------------ lights
export const hemi = new THREE.HemisphereLight(0x8ea2ff, 0x2a1a44, .55); scene.add(hemi);
export const key = new THREE.DirectionalLight(0xfff1dc, 1.7);
key.position.set(5, 9, 8); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -.0012; key.shadow.normalBias = .08;
Object.assign(key.shadow.camera, { left: -9, right: 9, top: 7, bottom: -7, near: 1, far: 40 }); scene.add(key);
export const rim = new THREE.DirectionalLight(0xffc857, 2.4); rim.position.set(-7, 5, -9); scene.add(rim);
export const fill = new THREE.PointLight(0x7aa2ff, 14, 40, 2); fill.position.set(-6, 1.5, 7); scene.add(fill);
export const glint = new THREE.PointLight(0xffffff, 7, 30, 2); glint.position.set(3, 3, 9); scene.add(glint);

// ------------------------------------------------------------------ shader background (sky dome + tech floor + particles)
export const THEMES = {
  night:   { a: '#070a26', b: '#2b1d78', c: '#5a3bd1', acc: '#FFC857', key: '#fff1dc', rim: '#ffc857', fill: '#6f8cff' },
  dusk:    { a: '#160c2b', b: '#6a2f76', c: '#c04d8a', acc: '#FFB36B', key: '#ffe6d2', rim: '#ff9a5c', fill: '#d06bff' },
  sepia:   { a: '#120c06', b: '#5b4228', c: '#a97c44', acc: '#E9C58B', key: '#ffe2b8', rim: '#e5a95a', fill: '#b08455' },
  sunrise: { a: '#13205a', b: '#e2674a', c: '#ffb36b', acc: '#FFE08A', key: '#fff0d8', rim: '#ffd27a', fill: '#ff7a8a' },
  day:     { a: '#0b2f5e', b: '#27a9c4', c: '#7be0e8', acc: '#FFE08A', key: '#f4fbff', rim: '#bff3ff', fill: '#5ab8ff' },
  royal:   { a: '#150c40', b: '#6b2fb3', c: '#c05cff', acc: '#FFD66B', key: '#fff1ff', rim: '#ffd66b', fill: '#9a6bff' },
  green:   { a: '#04201f', b: '#12766b', c: '#3fe0b0', acc: '#FFE08A', key: '#f0fff8', rim: '#a8ffe0', fill: '#3dd9c0' },
  crimson: { a: '#1d0710', b: '#8a2145', c: '#ff5a7a', acc: '#FFC857', key: '#ffe8ee', rim: '#ff8aa0', fill: '#ff4d7a' },
};
const C3 = h => new THREE.Color(h);
const skyUniforms = { uA: { value: C3('#000') }, uB: { value: C3('#000') }, uC: { value: C3('#000') }, uT: { value: 0 } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(90, 48, 24), new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, uniforms: skyUniforms,
  vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: `varying vec3 vP; uniform vec3 uA,uB,uC; uniform float uT;
    float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
    float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
    void main(){
      float y = vP.y*.5+.5;
      vec3 col = mix(uA, uB, smoothstep(0.,.75,y));
      float a = vP.x*2.2 + vP.z*1.3;
      float s = n(vec2(a*2.+uT*.05, y*5.-uT*.03))*.6 + n(vec2(a*5.-uT*.04, y*9.))*.4;
      col = mix(col, uC, smoothstep(.35,.9,s)*.28*(1.-abs(y-.5)*1.6));
      col += uC*.35*exp(-pow((y-.42)*5.,2.))*(.6+.4*sin(uT*.2+a*3.));
      float st = step(.9965, h(floor(vP.xz*220.)+floor(vP.y*220.)));
      col += st*.7*smoothstep(.45,.8,y);
      gl_FragColor = vec4(col,1.);
    }`,
}));
scene.add(sky);

const floorU = { uAcc: { value: C3('#FFC857') }, uT: { value: 0 } };
const floor = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, uniforms: floorU,
  vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.); vW=w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }',
  fragmentShader: `varying vec3 vW; uniform vec3 uAcc; uniform float uT;
    void main(){
      vec2 g = vW.xz; float d = length(g-vec2(0.,-2.));
      vec2 q = abs(fract(g*.5-.5)-.5)/fwidth(g*.5);
      float line = 1.-min(min(q.x,q.y),1.);
      float fade = exp(-d*.045);
      float pulse = .5+.5*sin(d*.5-uT*1.3);
      float a = line*fade*(.12+.12*pulse);
      a += .05*fade;
      gl_FragColor = vec4(uAcc*(.8+.6*line), a);
    }`,
}));
floor.rotation.x = -Math.PI / 2; floor.position.y = -2.2; floor.renderOrder = -2; scene.add(floor);
export const shadowFloor = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.ShadowMaterial({ opacity: .38 }));
shadowFloor.rotation.x = -Math.PI / 2; shadowFloor.position.y = -2.195; shadowFloor.receiveShadow = true; scene.add(shadowFloor);
export const FLOOR_Y = -2.2;

// glowing dust + big soft bokeh discs at several depths
const dust = (() => {
  const n = 340, r = rng(5), pos = new Float32Array(n * 3), prm = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { pos.set([(r() - .5) * 46, r() * 20 - 4, -r() * 44 + 12], i * 3); prm.set([.6 + r() * 2.2, r() * 6.28, .1 + r() * .5], i * 3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('prm', new THREE.BufferAttribute(prm, 3));
  const u = { uT: { value: 0 }, uCol: { value: C3('#ffffff') } };
  const p = new THREE.Points(g, new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: u,
    vertexShader: `attribute vec3 prm; uniform float uT; varying float vA;
      void main(){ vec3 p = position; p.y += mod(uT*prm.z*.6 + prm.y*3., 22.) - 4.; p.y = mod(p.y+4., 24.)-4.; p.x += sin(uT*.3+prm.y)*.6;
        vec4 mv = modelViewMatrix*vec4(p,1.); gl_Position = projectionMatrix*mv; float depth = -mv.z;
        gl_PointSize = prm.x*(260./depth)*(1.+step(1.8,prm.x)*2.2); vA = (.25+.35*sin(uT*1.2+prm.y)) * (prm.x>1.8 ? .35 : 1.); }`,
    fragmentShader: 'varying float vA; uniform vec3 uCol; void main(){ vec2 c = gl_PointCoord-.5; float d = length(c); float a = smoothstep(.5,.0,d)*vA; gl_FragColor = vec4(uCol, a); }',
  }));
  p.frustumCulled = false; p.renderOrder = -1; scene.add(p); return { p, u };
})();

// ------------------------------------------------------------------ post processing
const FXShader = {
  uniforms: { tDiffuse: { value: null }, uT: { value: 0 }, uBlur: { value: 0 }, uDir: { value: new THREE.Vector2(1, 0) }, uRadial: { value: 0 }, uCA: { value: .0007 }, uVig: { value: .38 }, uGrain: { value: .018 }, uFlash: { value: 0 }, uTint: { value: new THREE.Color(1, 1, 1) }, uSat: { value: 1.08 }, uPx: { value: new THREE.Vector2(1 / 1600, 1 / 900) } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec2 uPx; uniform float uT,uBlur,uRadial,uCA,uVig,uGrain,uFlash,uSat; uniform vec2 uDir; uniform vec3 uTint; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
    vec3 smp(vec2 uv, float ca){ return vec3(texture2D(tDiffuse,uv+vec2(ca,0.)).r, texture2D(tDiffuse,uv).g, texture2D(tDiffuse,uv-vec2(ca,0.)).b); }
    vec3 aces(vec3 x){ x *= .95; return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.); }
    void main(){
      vec2 uv = vUv, c = uv-.5; float r = length(c);
      float ca = uCA*(.4+r*2.2) + uBlur*.01;
      vec3 col;
      if (uBlur > .002 || uRadial > .002) {
        vec3 acc = vec3(0.); float tot = 0.;
        for (int i=-8;i<=8;i++){ float k = float(i)/8.; float w = 1.-abs(k)*.55;
          vec2 off = uDir*uBlur*.055*k + (-c)*uRadial*.22*k;
          acc += smp(uv+off, ca)*w; tot += w; }
        col = acc/tot;
      } else col = smp(uv, ca);
      col = pow(aces(col), vec3(1./2.2));
      if (uBlur < .002) { // cheap edge anti-aliasing on the tone-mapped image
        vec3 n1 = pow(aces(texture2D(tDiffuse, uv+vec2(0.,uPx.y)).rgb), vec3(1./2.2)), n2 = pow(aces(texture2D(tDiffuse, uv-vec2(0.,uPx.y)).rgb), vec3(1./2.2));
        vec3 e1 = pow(aces(texture2D(tDiffuse, uv+vec2(uPx.x,0.)).rgb), vec3(1./2.2)), e2 = pow(aces(texture2D(tDiffuse, uv-vec2(uPx.x,0.)).rgb), vec3(1./2.2));
        vec3 w = vec3(.299,.587,.114); float l0 = dot(col,w), lx = max(max(dot(n1,w),dot(n2,w)),max(dot(e1,w),dot(e2,w))), ln = min(min(dot(n1,w),dot(n2,w)),min(dot(e1,w),dot(e2,w)));
        float edge = max(lx,l0)-min(ln,l0); float k = smoothstep(.04,.22,edge)*.55;
        col = mix(col, (n1+n2+e1+e2)*.25*.5 + col*.5, k);
      }
      col *= mix(1., smoothstep(1.05,.25,r*1.35), uVig);
      col = mix(vec3(dot(col,vec3(.299,.587,.114))), col, uSat);
      col = (col-.5)*1.06+.5;
      col *= uTint;
      col += uFlash*vec3(1.,.96,.88);
      col += (hash(uv*vec2(1920.,1080.)+fract(uT)*91.7)-.5)*uGrain;
      gl_FragColor = vec4(clamp(col,0.,1.),1.);
    }`,
};
const Q = new URLSearchParams(location.search);
const MS = Q.has('ms') ? +Q.get('ms') : 0, RES = Q.has('res') ? +Q.get('res') : 1;
const rt = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType, samples: MS });
export const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(RES); composer.setSize(RW, RH);
composer.addPass(new RenderPass(scene, camera));
export const bloom = new UnrealBloomPass(new THREE.Vector2(RW / 2, RH / 2), .32, .55, .93);
composer.addPass(bloom);
export const fx = new ShaderPass(FXShader);
composer.addPass(fx);
const MSD = Q.has('ms') ? +Q.get('ms') : 0; if (Q.get('bloom') === '0') bloom.enabled = false; if (Q.get('dust') === '0') dust.p.visible = false; if (Q.get('shadow') === '0') { renderer.shadowMap.enabled = false; key.castShadow = false; } if (Q.get('fx') === '0') fx.enabled = false; if (Q.get('floor') === '0') floor.visible = false; if (Q.get('sky') === '0') sky.visible = false;;

// ------------------------------------------------------------------ theme blending
const tmp = new THREE.Color();
export function applyTheme(A, B, k, t) {
  const a = THEMES[A] || THEMES.night, b = THEMES[B] || THEMES.night;
  const mix = (n) => tmp.set(a[n]).lerp(C3(b[n]), k);
  skyUniforms.uA.value.copy(mix('a')); skyUniforms.uB.value.copy(mix('b')); skyUniforms.uC.value.copy(mix('c')); skyUniforms.uT.value = t;
  floorU.uAcc.value.copy(mix('acc')); floorU.uT.value = t; dust.u.uT.value = t; dust.u.uCol.value.copy(mix('acc')).lerp(new THREE.Color(1, 1, 1), .4);
  key.color.copy(mix('key')); rim.color.copy(mix('rim')); fill.color.copy(mix('fill'));
  hemi.color.copy(mix('c')).lerp(new THREE.Color(1, 1, 1), .35); hemi.groundColor.copy(mix('a')).lerp(new THREE.Color(.1, .05, .2), .4);
}

// ------------------------------------------------------------------ camera rig
// keys: [{t:0..1, p:[x,y,z], l:[x,y,z], f:fov, r:roll}] interpolated with ease-in-out between neighbours
const _p = new THREE.Vector3(), _l = new THREE.Vector3();
export function evalCam(keys, f) {
  let i = 0; while (i < keys.length - 2 && f > keys[i + 1].t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const k = a === b ? 0 : E.inOut(clamp((f - a.t) / Math.max(1e-4, b.t - a.t)));
  const lv = (u, v) => [lerp(u[0], v[0], k), lerp(u[1], v[1], k), lerp(u[2], v[2], k)];
  return { p: lv(a.p, b.p), l: lv(a.l, b.l), f: lerp(a.f || 32, b.f || 32, k), r: lerp(a.r || 0, b.r || 0, k) };
}
const ZOOM = 1.1;
export function setCamera(c, t) {
  c = { p: c.p.map((v, i) => c.l[i] + (v - c.l[i]) * ZOOM), l: c.l, f: c.f, r: c.r };
  // gentle handheld drift
  const dx = Math.sin(t * .7) * .06 + Math.sin(t * 1.9) * .015, dy = Math.cos(t * .55) * .045;
  camera.position.set(c.p[0] + dx, c.p[1] + dy, c.p[2]);
  camera.up.set(Math.sin(c.r * Math.PI / 180), Math.cos(c.r * Math.PI / 180), 0);
  camera.lookAt(c.l[0], c.l[1], c.l[2]);
  if (Math.abs(camera.fov - c.f) > .01) { camera.fov = c.f; camera.updateProjectionMatrix(); }
}
