# JustSomeSkills
Just some skills For Claude,  made as needed, freely shared.

## codegen-images

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



## svd-interpreter
This is for reading System View Description files.
It includes a compressed svd file describing the hardware of the RP2350 chip

## vanilla-artifact-builder
This lets you develop a page as separate HTML, CSS, JS and image files, then bundles them into one self-contained HTML file. That suits environments that can only show a single HTML file, such as claude.ai artifacts, or anyone who just wants one file.

```
project/
├── src/              ← Everything here gets bundled
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── images/
│       └── logo.png
├── project.html      ← Generated bundle (or in $VANILLA_ARTIFACT_OUTPUT_DIR)
├── dist/             ← Build output (temporary)
├── node_modules/     ← Dependencies (temporary)
```
The bundle ends with a comment holding the compressed source files and a link back to this repo, so the bundle can be turned back into individual files. Set `VANILLA_ARTIFACT_OUTPUT_DIR` to wherever your environment picks up output files. Run `scripts/check-environment.sh` to check that an environment has what the skill needs.

## terminal-images
Lets the agent show images inline in a terminal that supports the kitty graphics protocol (Ghostty, kitty, WezTerm). Claude Code captures shell output and strips escape codes, so `termimg` writes the image straight to the terminal device of the agent's own UI. Images float over the conversation; type `/hideimg` (the companion `hideimg` skill) to hide them. When `termimg check` finds no image support, the skill stays out of the way.
