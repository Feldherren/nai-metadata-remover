import argparse
import configparser
import sys
from pathlib import Path
from PIL import Image
import numpy as np
import io

# TODO:
# optionally take a switch that makes it save files in place, without metadata?
# maybe have an external config file for the default behaviour - keeping/removing name, keeping/removing metadata, saving a copy/saving over the original?

def get_config():
    config = configparser.ConfigParser()
    config_path = Path('config.ini')
    if not config_path.exists():
        config['DEFAULT'] = {'export_path': 'scrubbed',
                             'display_metadata': 'false', 
                             'change_filename': 'true', 
                             'remove_metadata': 'true', 
                             'prevent_overwrite': 'true'}
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    config.read('config.ini')
    return config

def parse_args():
    parser = argparse.ArgumentParser(description='Process PNG files.')
    parser.add_argument('files', nargs='+', type=str, help='One or more PNG files to process')
    args = parser.parse_args()
    
    # Validate files and collect valid PNG files
    png_files = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: File '{file_path}' does not exist", file=sys.stderr)
            continue
        if path.suffix.lower() != '.png':
            print(f"Warning: '{file_path}' is not a PNG file and will be skipped", file=sys.stderr)
            continue
        png_files.append(str(path))
    
    if not png_files:
        print("Error: No valid PNG files were provided", file=sys.stderr)
        sys.exit(1)
    
    return png_files

def display_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"\nMetadata for {image_path}:")
            print("-" * 50)
            print(f"Format: {img.format}")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size}")
            print(f"Width: {img.width}")
            print(f"Height: {img.height}")
            
            # Display all available metadata
            if img.info:
                print("\nAdditional metadata:")
                for key, value in img.info.items():
                    print(f"{key}: {value}")
            else:
                print("\nNo additional metadata found")
    except Exception as e:
        print(f"Error reading metadata for {image_path}: {str(e)}", file=sys.stderr)

def remove_metadata(image_path, index, config):
    try:
        # Create scrubbed directory if it doesn't exist
        scrubbed_dir = Path(config['DEFAULT']['export_path'])
        scrubbed_dir.mkdir(exist_ok=True)
        
        if config['DEFAULT']['change_filename'] == 'true':
            # Create new filename with sequential number
            filename = f"Image{index}.png"
        else:
            # Use the original filename
            filename = image_path.name

        new_path = scrubbed_dir / filename

        if config['DEFAULT']['prevent_overwrite'] == 'true':
            if new_path.exists():
                print(f"Warning: {new_path} already exists, skipping")
                return
        
        # Open the image and convert to RGBA
        with Image.open(image_path) as img:
            # Convert to RGBA to ensure we have a consistent format
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Get the raw pixel data as a numpy array
            img_array = np.array(img)
            
            # Create a new image with the same dimensions
            new_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # Convert the array back to an image
            temp_img = Image.fromarray(img_array, 'RGBA')
            
            # Paste the pixel data into the new image
            new_img.paste(temp_img, (0, 0))
            
            # Save to a bytes buffer first
            buffer = io.BytesIO()
            new_img.save(buffer, format='BMP')  # Save as BMP first to strip metadata
            buffer.seek(0)
            
            # Load from buffer and save as PNG
            clean_img = Image.open(buffer)
            clean_img.save(new_path, "PNG", 
                         optimize=True,
                         pnginfo=None,  # Don't include any PNG info
                         compress_level=9)  # Maximum compression
            
            print(f"Created scrubbed copy: {new_path}")
            
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}", file=sys.stderr)

# NovelAI additional metadata keys:
# Software, Source, Generation_time, Comment, Title, Description

if __name__ == '__main__':
    config = get_config()
    export_path = config['DEFAULT']['export_path']
    print(f"Exporting to {export_path}")

    png_files = parse_args()
    print(f"Processing {len(png_files)} PNG files:")
    for index, file in enumerate(png_files, start=1):
        if config['DEFAULT']['display_metadata'] == 'true':
            display_metadata(file)
        if config['DEFAULT']['remove_metadata'] == 'true':
            remove_metadata(file, index, config)
