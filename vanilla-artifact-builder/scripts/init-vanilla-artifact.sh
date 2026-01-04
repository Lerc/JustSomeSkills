#!/bin/bash
set -e

# Check if project name provided
if [ -z "$1" ]; then
  echo "❌ Error: No project name provided"
  echo "Usage: bash init-vanilla-artifact.sh <project-name>"
  exit 1
fi

PROJECT_NAME="$1"

echo "🚀 Initializing vanilla JavaScript artifact: $PROJECT_NAME"

# Create project directory with src subdirectory
mkdir -p "$PROJECT_NAME/src"
mkdir -p "$PROJECT_NAME/src/images"
cd "$PROJECT_NAME"

echo "📝 Creating project files..."

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

# Note: bundle*.html files are NOT ignored
# Keep versioned bundles for comparison and history
EOF

# Create README for the images folder
cat > src/images/README.md << 'EOF'
# Images Directory

Place image files here to include them in your artifact.

Supported formats:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- SVG (.svg)
- WebP (.webp)

Images will be:
- Automatically bundled into the artifact
- Base64-encoded in the bundle metadata
- Accessible via relative paths in your HTML

Example usage in HTML:
```html
<img src="./images/logo.png" alt="Logo">
```

The bundler will handle encoding and including these images.
EOF

echo ""
echo "✅ Project initialized successfully!"
echo "📁 Project structure:"
echo "   $PROJECT_NAME/"
echo "   ├── src/"
echo "   │   ├── index.html"
echo "   │   ├── styles.css"
echo "   │   ├── script.js"
echo "   │   └── images/"
echo "   │       └── README.md (place images here)"
echo "   └── .gitignore"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Edit files in src/ directory"
echo "3. Add images to src/images/ if needed"
echo "4. Run bundle script to create artifact"

