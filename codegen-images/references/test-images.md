# Raytraced Test Images

Generate placeholder/test images with a compact raytracer. Returns `ImageData`.

```javascript
// Minified raytracer - spheres on checkerboard plane with reflections
// W=width, H=height, S=scene, C=camera, L=lookAt, P=planeTexture
function makeTestImage(W=256,H=W,S,C,L,P=(([x,,y])=>8*x&1^8*y&1)){let I=new ImageData(W,H),D=I.data,M=Math,A=M.abs,U=M.max,m=e=>U(0,M.min(1,e)),O=a=>Array.from(a[0],b=>b.charCodeAt()/25-3),p=e=>(t,l)=>t.map((t,a)=>e(t,l[a])),i=(e,t)=>e+t,u=p(i),R=p((e,t)=>e-t),o=p((e,t)=>e*t),c=(e,t)=>e.map(e=>e*t),b=(e,t)=>o(e,t).reduce(i),g=e=>c(e,1/(M.hypot(...e)||1)),h=([e,t,l])=>[t,l,e],d=(e,t)=>R(e,c(t,2*b(e,t))),w=g(R(L||O`KU5`,C||=O`KY~`)),x=(e,t)=>h(R(o(e,h(t)),o(h(e),t))),y=g(x(w,O`KdK`)),G=g(x(y,w)),V=g(O`?bQ`),j=e=>{let t=m(.5*(1-b(e,V)));return[m(1-2*t*t),m(1-2*t),m(1-t/2)]},v=(e,m)=>{let p,s,t=1e9,k=-1,n=O`KdK`;if(A(m[1])>1e-6){let a=-e[1]/m[1];a>1e-4&&(t=a,k=0,p=u(e,c(m,a)))}for(let [r,i,o,h,d,...B] of S){let q=R(e,B),w=b(q,m),x=w*w-(b(q,q)-r*r);if(x>0){let l=M.sqrt(x),b=-w-l;b<1e-4&&(b=-w+l),b>1e-4&&b<t&&(t=b,k=1,p=u(e,c(m,b)),n=g(R(p,B)),s={c:[i,o,h],f:d})}}return k<0?0:{t,k,p,n,s}},z=(e,t)=>{let a=O`KKK`,r=O`ddd`;for(let _ of r){let Q=v(e,t);if(!Q){let e=j(t);return u(a,o(r,e))}let i,h,Z=Q.p,q=Q.n;if(0==Q.k){i=P(Z)?O`^_a`:O`MNO`,h=.1+.38*m(1-A(t[1]))}else i=Q.s.c,h=Q.s.f;let x=v(u(Z,c(q,1e-4)),V)?.t<20?.18:1,y=(x?1:0)*U(0,b(q,g(R(V,t))))**(Q.k?120:70),G=u(c(i,x*(.1+.9*U(0,b(q,V)))*(.65+.35*q[1])),c(O`ddd`,y*(Q.k?.55:.35)+.18*U(0,1+b(t,q))**2));if(a=u(a,o(r,G)),h<.001)break;r=c(r,h),e=u(Z,c(q,1e-4)),t=g(d(t,q))}return a};S||=[O`UdPN^9U=`,O`SM]d\\QS.`,O`WbbdbbWD`,O`Pd\`NXHPM`];for(let l=0;l<H;l++){let a=.4*(1-2*(l+.5)/H);for(let f=0;f<W;f++){let n=z(C,g(u(u(c(y,.4*(2*(f+.5)/W-1)*(W/H)),c(G,a)),w))).map((e=>(e/(1+e))**(1/2.2)));n=(e=>n.map((t=>m(1.6875*t-.4375*e-.125))))(b(n,[.2126,.7152,.0722]));let p=(f+.5)/W-.5,i=(l+.5)/H-.5,k=m(1-.85*(p*p+i*i));n=c(n,k);let o=4*(l*W+f);D.set(c(n,255),o),D[o+3]=255}}return I}
```

**Parameters:**
- `W`, `H` — width/height in pixels (default: 256×256)
- `S` — scene array of spheres: `[[radius, r, g, b, reflectivity, x, y, z], ...]`
- `C` — camera position `[x, y, z]` (default: `[0, 1.4, 4]`)
- `L` — look-at target `[x, y, z]` (default: `[0, 0.8, -2]`)
- `P` — plane texture function `([x,y,z]) => 0|1` (default: checkerboard)

**Encoding spheres:** The default scene uses encoded strings. To create custom scenes, use arrays directly:

```javascript
// [radius, r, g, b, reflectivity, x, y, z]
const customScene = [
  [0.8, 1, 0.2, 0.2, 0.3, 0, 0.8, 0],    // red sphere
  [0.5, 0.2, 1, 0.2, 0.5, -1.5, 0.5, 1], // green sphere, more reflective
  [1.2, 1, 1, 1, 0.9, 2, 1.2, -1],       // large white mirror sphere
];
const img = makeTestImage(512, 512, customScene);
```

**Preset scenes:**

```javascript
const SCENES = {
  // Classic 4-sphere demo
  DEFAULT: [
    [0.6, 0.9, 0.2, 0.3, 0.3, -1.0, 0.6, 0],      // red-pink left
    [0.5, 0.2, 0.8, 0.9, 0.4, 0.8, 0.5, 0.5],     // cyan right-front
    [0.8, 0.95, 0.95, 1.0, 0.85, 0.3, 0.8, -0.8], // white mirror
    [0.4, 1.0, 0.9, 0.3, 0.2, -0.3, 0.4, 0.8],    // yellow front
  ],
  
  // Single large mirror sphere
  MIRROR: [[1.2, 0.98, 0.98, 1.0, 0.95, 0, 1.2, 0]],
  
  // RGB spheres in a row
  RGB: [
    [0.55, 1.0, 0.15, 0.15, 0.25, -1.1, 0.55, 0],
    [0.55, 0.15, 1.0, 0.15, 0.25, 0, 0.55, 0],
    [0.55, 0.15, 0.15, 1.0, 0.25, 1.1, 0.55, 0],
  ],
  
  // Metallic gold and silver
  METALLIC: [
    [0.7, 0.9, 0.8, 0.3, 0.7, -0.8, 0.7, 0],
    [0.7, 0.8, 0.8, 0.85, 0.8, 0.8, 0.7, 0],
  ],
};

// Custom plane textures
const PLANE_TEXTURES = {
  checker: ([x,,z]) => (8*x & 1) ^ (8*z & 1),
  stripes: ([x,,z]) => (4*z & 1),
  dots: ([x,,z]) => (Math.hypot(x % 1 - 0.5, z % 1 - 0.5) < 0.3) ? 1 : 0,
};
```

**Usage with output converters:**

```javascript
// Generate and display
const imageData = makeTestImage(512, 512);
const canvas = document.createElement('canvas');
canvas.width = imageData.width;
canvas.height = imageData.height;
canvas.getContext('2d').putImageData(imageData, 0, 0);
document.body.appendChild(canvas);

// As data URL
const dataUrl = canvas.toDataURL('image/png');

// As ImageBitmap
const bitmap = await createImageBitmap(imageData);
```

## Rendering to PNG (Node.js)

Generate raytraced PNG test images using `<skill-dir>/scripts/render_scene.js` (needs the canvas setup in SKILL.md):

```bash
# Render default scene
node <skill-dir>/scripts/render_scene.js --size 512 --out test.png

# Use a preset scene
node <skill-dir>/scripts/render_scene.js --scene rgb --size 256 --out rgb.png

# Custom camera position
node <skill-dir>/scripts/render_scene.js --scene mirror --camera 0,2,6 --out mirror.png

# List available scenes
node <skill-dir>/scripts/render_scene.js --list-scenes
```

Available scenes: `default`, `mirror`, `rgb`, `single`, `metallic`
