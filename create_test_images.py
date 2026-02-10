#!/usr/bin/env python3
"""
Create test images for multi-image upload testing.
Generates 6 different room images using PIL.
"""

from PIL import Image, ImageDraw
import os

def create_kitchen_image():
    """Create a kitchen-like image with counters and appliances."""
    img = Image.new('RGB', (400, 300), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Countertops
    draw.rectangle([0, 200, 400, 220], fill='#8B4513')  # Brown counters
    
    # Cabinets
    draw.rectangle([0, 150, 400, 200], fill='#D2B48C')  # Light brown cabinets
    
    # Appliances (simple rectangles)
    draw.rectangle([50, 160, 90, 190], fill='#C0C0C0')  # Silver appliance
    draw.rectangle([150, 160, 190, 190], fill='#C0C0C0')  # Silver appliance
    draw.rectangle([250, 160, 290, 190], fill='#C0C0C0')  # Silver appliance
    
    # Floor
    draw.rectangle([0, 220, 400, 300], fill='#DEB887')  # Tan floor
    
    return img

def create_bedroom_image():
    """Create a bedroom-like image with bed and furniture."""
    img = Image.new('RGB', (400, 300), color='#E6E6FA')
    draw = ImageDraw.Draw(img)
    
    # Bed (simple rectangle)
    draw.rectangle([100, 100, 300, 180], fill='#4B0082')  # Dark purple bed
    draw.rectangle([120, 80, 280, 100], fill='#4B0082')  # Headboard
    
    # Nightstands
    draw.rectangle([60, 120, 90, 160], fill='#8B4513')  # Brown nightstand
    draw.rectangle([310, 120, 340, 160], fill='#8B4513')  # Brown nightstand
    
    # Floor
    draw.rectangle([0, 200, 400, 300], fill='#DEB887')  # Tan floor
    
    return img

def create_bathroom_image():
    """Create a bathroom-like image with fixtures."""
    img = Image.new('RGB', (400, 300), color='#F0F8FF')
    draw = ImageDraw.Draw(img)
    
    # Bathtub/shower area
    draw.rectangle([50, 50, 150, 120], fill='#B0C4DE')  # Light steel blue
    
    # Vanity
    draw.rectangle([200, 80, 350, 110], fill='#8B4513')  # Brown vanity
    draw.rectangle([250, 60, 280, 80], fill='#FFFFFF')  # White sink
    
    # Toilet
    draw.rectangle([300, 130, 370, 170], fill='#FFFFFF')  # White toilet
    
    # Tile floor
    draw.rectangle([0, 180, 400, 300], fill='#D3D3D3')  # Gray tile
    
    return img

def create_living_room_image():
    """Create a living room-like image with furniture."""
    img = Image.new('RGB', (400, 300), color='#FFF8DC')
    draw = ImageDraw.Draw(img)
    
    # Sofa
    draw.rectangle([80, 120, 320, 160], fill='#8B4513')  # Brown sofa
    draw.rectangle([70, 100, 330, 130], fill='#8B4513')  # Sofa back
    
    # Coffee table
    draw.rectangle([150, 170, 250, 190], fill='#654321')  # Dark brown table
    
    # Fireplace (simple representation)
    draw.rectangle([300, 80, 380, 180], fill='#696969')  # Gray fireplace
    draw.rectangle([310, 90, 370, 140], fill='#000000')  # Black firebox
    
    # Floor
    draw.rectangle([0, 200, 400, 300], fill='#DEB887')  # Tan floor
    
    return img

def create_hallway_image():
    """Create a hallway-like image."""
    img = Image.new('RGB', (500, 200), color='#F5F5F5')
    draw = ImageDraw.Draw(img)
    
    # Long hallway perspective (simple representation)
    # Walls
    draw.rectangle([0, 0, 50, 200], fill='#FFFFFF')   # Left wall
    draw.rectangle([450, 0, 500, 200], fill='#FFFFFF')  # Right wall
    
    # Floor
    draw.rectangle([50, 150, 450, 200], fill='#DEB887')  # Tan floor
    
    # Doors along hallway
    draw.rectangle([100, 20, 130, 70], fill='#8B4513')  # Door 1
    draw.rectangle([200, 20, 230, 70], fill='#8B4513')  # Door 2
    draw.rectangle([300, 20, 330, 70], fill='#8B4513')  # Door 3
    
    return img

def create_exterior_image():
    """Create an exterior house-like image."""
    img = Image.new('RGB', (600, 400), color='#87CEEB')
    draw = ImageDraw.Draw(img)
    
    # House structure
    draw.rectangle([100, 100, 500, 350], fill='#D2B48C')  # House body
    
    # Roof
    points = [(80, 100), (300, 50), (520, 100)]
    draw.polygon(points, fill='#8B4513')  # Brown roof
    
    # Door
    draw.rectangle([270, 200, 330, 350], fill='#8B4513')  # Brown door
    
    # Windows
    draw.rectangle([150, 150, 200, 200], fill='#87CEEB')  # Window
    draw.rectangle([400, 150, 450, 200], fill='#87CEEB')  # Window
    
    # Yard
    draw.rectangle([0, 350, 600, 400], fill='#90EE90')  # Green grass
    
    return img

def main():
    """Create all test images and save them."""
    output_dir = "frontend/tests/fixtures"
    os.makedirs(output_dir, exist_ok=True)
    
    images = {
        "kitchen.jpg": create_kitchen_image,
        "bedroom.jpg": create_bedroom_image,
        "bathroom.jpg": create_bathroom_image,
        "living_room.jpg": create_living_room_image,
        "hallway.jpg": create_hallway_image,
        "exterior.jpg": create_exterior_image,
    }
    
    for filename, create_func in images.items():
        print(f"Creating {filename}...")
        img = create_func()
        img.save(f"{output_dir}/{filename}", "JPEG", quality=85)
    
    print(f"Created {len(images)} test images in {output_dir}")

if __name__ == "__main__":
    main()