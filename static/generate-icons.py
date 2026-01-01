#!/usr/bin/env python3
"""
Generate placeholder PWA icons for VICTUS
Requires Pillow: pip install Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Install with: pip install Pillow")
    exit(1)

import os

# Icon sizes needed
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Create icons directory
os.makedirs('icons', exist_ok=True)

# Colors
primary_color = (102, 126, 234)  # #667eea
secondary_color = (118, 75, 162)  # #764ba2

for size in sizes:
    # Create image with gradient background
    img = Image.new('RGB', (size, size), primary_color)
    draw = ImageDraw.Draw(img)
    
    # Draw gradient effect (simplified)
    for i in range(size):
        ratio = i / size
        r = int(primary_color[0] * (1 - ratio) + secondary_color[0] * ratio)
        g = int(primary_color[1] * (1 - ratio) + secondary_color[1] * ratio)
        b = int(primary_color[2] * (1 - ratio) + secondary_color[2] * ratio)
        draw.rectangle([(0, i), (size, i + 1)], fill=(r, g, b))
    
    # Draw "V" letter in center
    try:
        # Try to use a nice font
        font_size = int(size * 0.5)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position (centered)
    text = "V"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2)
    
    # Draw white "V"
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Save icon
    filename = f'icons/icon-{size}x{size}.png'
    img.save(filename, 'PNG')
    print(f'Created {filename}')

print('\nAll icons generated successfully!')
print('Place them in /static/icons/ directory.')

