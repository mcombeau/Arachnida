import argparse
import os
import pathlib
import stat
import time
import typing
from PIL import Image, ExifTags
import humanize

HEADER = '''
███████  ██████  ██████  ██████  ██████  ██  ██████  ███    ██ 
██      ██      ██    ██ ██   ██ ██   ██ ██ ██    ██ ████   ██ 
███████ ██      ██    ██ ██████  ██████  ██ ██    ██ ██ ██  ██ 
     ██ ██      ██    ██ ██   ██ ██      ██ ██    ██ ██  ██ ██ 
███████  ██████  ██████  ██   ██ ██      ██  ██████  ██   ████ 
                                                               
'''
SEPARATOR = '------------------------'
EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

Args = argparse.Namespace
Parser = argparse.ArgumentParser
Path = pathlib.PosixPath
Any = typing.Any

# ---------------------------
# Prettify
# ---------------------------
class color:
    HEADER = '\033[36m'
    INFO = '\033[96m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'

def print_header() -> None:
    for line in HEADER.splitlines():
        print(color.HEADER + '{:^70}'.format(line) + color.RESET)

def print_image_header(args: Args, image_number: int, image: Path) -> None:
    print('{:-^80}'.format(''))
    print(f'[{color.INFO}{image_number}{color.RESET}/{len(args.image)}] Metadata for image: {color.INFO}{image}{color.RESET}')
    print('{:-^80}'.format(''))

def print_image_metadata(metadata: dict[str, Any], verbose: bool = False) -> None:
    for key, value in metadata.items():
        try:
            if type(value) is bytes:
                value: str = value.decode()
            print(f'{key:30}: {value}')
        except Exception as e:
            if verbose:
                value: str = f'{color.WARNING}{e}{color.RESET}: ' + str(value)
                print(f'{key:30}: {value}')
            continue

# ---------------------------
# Argument parsing
# ---------------------------
def parse_args() -> Args:
    parser: Parser = Parser(description = 'An image metadata viewer')
    parser.add_argument('image', type = pathlib.Path, nargs = '+', help = f'image to view EXIF data for. Supported types: {EXTENSIONS}')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'Enable verbose mode')
    args: Args = parser.parse_args()
    return args

# ---------------------------
# Execution
# ---------------------------
def display_image_metadata(args: Args, image_path: Path) -> None:
    metadata: dict[str, Any] = {}
    metadata['Filename'] = os.path.basename(image_path)
    metadata['Directory'] = os.path.dirname(image_path.resolve())
    metadata['File Size'] = humanize.naturalsize(os.path.getsize(image_path), binary=True)
    metadata['Creation Date'] = time.ctime(os.path.getctime(image_path))
    metadata['Modification Date'] = time.ctime(os.path.getmtime(image_path))
    metadata['File Permissions'] = stat.filemode(os.stat(image_path).st_mode)
    try:
        with Image.open(image_path) as image:
            metadata['Format'] = image.format
            metadata['Mode'] = image.mode
            metadata['Image Width'] = image.width
            metadata['Image Height'] = image.height
            metadata[SEPARATOR] = SEPARATOR
            exifdata: Any = image.getexif()
            for tag_id, value in exifdata.items():
                tag: str = ExifTags.TAGS.get(tag_id, tag_id)
                metadata[tag] = value
        print_image_metadata(metadata, args.verbose)
    except Exception as e:
        metadata[SEPARATOR] = SEPARATOR
        print_image_metadata(metadata, args.verbose)
        print(f'{color.WARNING}Skipping image: {e}{color.RESET}')

def display_all_metadata(args: Args) -> None:
    for i, image in enumerate(args.image):
        print_image_header(args, i + 1, image)
        display_image_metadata(args, image)

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    print_header()
    args: Args = parse_args()
    display_all_metadata(args)
    print('{:-^80}'.format(''))

if __name__ == '__main__':
    main()
