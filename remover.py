import argparse
import sys
from pathlib import Path

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

if __name__ == '__main__':
    png_files = parse_args()
    print(f"Processing {len(png_files)} PNG files:")
    for file in png_files:
        print(f"- {file}")
