#!/bin/bash
# Create a starter project at PROJECT_DIR (any path; its name becomes the bundle name).
#
# Usage: init-vanilla-artifact.sh <PROJECT_DIR>
set -e

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: init-vanilla-artifact.sh <PROJECT_DIR>"
  [ -z "$1" ] && exit 1 || exit 0
fi
if [ -e "$1/src" ]; then
  echo "Error: $1/src already exists." >&2
  exit 1
fi

mkdir -p "$1/src/images"
cd "$1"

# Create index.html in src/
cat > src/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Artifact</title>
    <link rel="stylesheet" href="./styles.css">
</head>
<body>
    <div class="container">
        <h1>Hello, World!</h1>
        <p>Edit this artifact to build something amazing.</p>
        <button id="myButton" class="btn">Click Me</button>
        <div id="output"></div>
    </div>
    <script src="./script.js"></script>
</body>
</html>
EOF

# Create styles.css in src/
cat > src/styles.css << 'EOF'
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

.container {
    background: white;
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    width: 100%;
}

h1 {
    color: #333;
    margin-bottom: 1rem;
}

p {
    color: #666;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.btn {
    padding: 0.75rem 2rem;
    font-size: 1rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 600;
    color: white;
    background: #667eea;
}

.btn:hover {
    background: #5568d3;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn:active {
    transform: translateY(0);
}

#output {
    margin-top: 2rem;
    padding: 1rem;
    border-radius: 8px;
    background: #f3f4f6;
    color: #333;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}
EOF

# Create script.js in src/
cat > src/script.js << 'EOF'
// Get DOM elements
const button = document.getElementById('myButton');
const output = document.getElementById('output');

// State
let clickCount = 0;

// Event handler
function handleClick() {
    clickCount++;
    output.textContent = `Button clicked ${clickCount} time${clickCount !== 1 ? 's' : ''}!`;
}

// Add event listener
button.addEventListener('click', handleClick);

console.log('Artifact initialized successfully!');
EOF

# Create .gitignore for the project
cat > .gitignore << 'EOF'
# Build outputs (temporary)
dist/
.parcel-cache/

# Dependencies (temporary)
node_modules/

# Build configs (generated)
package.json
package-lock.json
.parcelrc
EOF

echo "Created $(pwd)/src (index.html, styles.css, script.js, images/)"
