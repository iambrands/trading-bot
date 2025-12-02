#!/bin/bash
# Create simple icon files using ImageMagick or base64

# Create a simple 192x192 blue square with white TB text using ImageMagick if available
if command -v convert &> /dev/null; then
    convert -size 192x192 xc:"#2563eb" -gravity center -pointsize 60 -fill white -font Arial-Bold -annotate +0+0 "TB" icon-192.png 2>/dev/null
    convert -size 512x512 xc:"#2563eb" -gravity center -pointsize 150 -fill white -font Arial-Bold -annotate +0+0 "TB" icon-512.png 2>/dev/null
    echo "✅ Created icons with ImageMagick"
elif command -v python3 &> /dev/null; then
    python3 << 'PYTHON'
from PIL import Image, ImageDraw, ImageFont
try:
    img = Image.new('RGB', (192, 192), '#2563eb')
    draw = ImageDraw.Draw(img)
    draw.text((96, 96), 'TB', fill='white', anchor='mm')
    img.save('icon-192.png')
    img = Image.new('RGB', (512, 512), '#2563eb')
    draw = ImageDraw.Draw(img)
    draw.text((256, 256), 'TB', fill='white', anchor='mm')
    img.save('icon-512.png')
    print("✅ Created icons with PIL")
except:
    print("⚠️  Could not create icons")
PYTHON
else
    echo "⚠️  ImageMagick and PIL not available - icons will be 404 (non-critical)"
fi
