# JustSomeSkills
Skills For Claude.


#codegen-images

codegen-images generates images in javascript for situations where you want some imagery, but cannot fetch media files.  It can provide simple user interface elements from SVG d path strings. 


The skill also includes instructions for a compact encoder and decoder to further shrink the path string data.    

If you have a group of user interface icons rendered in this manner the decoder at roughly 200 characters can be useful.  
```javascript
function Q([e]){let c,t,n,d="",l=0,o=c=>e.charCodeAt(l++)-33;for(;l<e.length;d+=t<20?(c=1&t?100:10,"MmLlHhVvCcSsQqTtAaZz"[t]):t<71?t-45+" ":71==t?(n=o(),e.slice(l,l+=n)):(94*(t-72)+o()-1033)/c+" ")t=o();return d}
```

It also includes a very basic raytracer to generate placeholder images.   Think of it as a image lorem ipsen. 

This link shows a sampler of images that it knows how to create.  The entire sampler page is only 14k, including the decoder, raytracer, path renderer, scene data, and path data.

https://htmlpreview.github.io/?https://github.com/Lerc/JustSomeSkills/blob/main/codegen-images/sampler.html

In this encoding one of the larger icons is the Gear symbol which is stored in code as 

```javascript
GEAR: Q`!L6#P6R<X>^:a=]D_JfLfP\`R^Xb^_aX]R_PfLfJ\`D^>b;_?X=R6P6L<J>D:>=;D?J=3!NF1VVNONNVVVNONNF`
```

![SimpleUser Interface Images](https://github.com/Lerc/JustSomeSkills/blob/main/ui_images.png?raw=true)



#svd-interpreter
This is for reading System View Description files.
It includes a compressed svd file describing the hardware of the RP2350 chip

#vanilla-artifact-builder
This assists in making artifacts in multiple files and then combining them into the html file that may be viewed as an artifact.

Internally it uses

```project/
├── src/              ← Everything here gets bundled
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── images/       
│       └── logo.png
├── bundle.html       ← Generated artifact
├── dist/             ← Build output (temporary)
├── node_modules/     ← Dependencies (temporary)
```
It can  handle multiple js files, and appends instructions to the end of the HTML telling claude how to deconstruct the bundled html file back into individual files.



