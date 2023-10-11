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

def print_image_metadata(metadata: dict[str, Any]) -> None:
    for key, value in metadata.items():
        if type(value) is bytes:
            try:
                value = value.decode()
            except Exception as e:
                value = f'{color.WARNING}{e}{color.RESET}: ' + str(value)
        print(f'{key:30}: {value}')

# ---------------------------
# Argument parsing
# ---------------------------
def parse_args() -> Args:
    parser: Parser = Parser(description = 'An image metadata viewer')
    parser.add_argument('image', type = pathlib.Path, nargs = '+', help = f'image to view EXIF data for. Supported types: {EXTENSIONS}')
    args: Args = parser.parse_args()
    return args

# ---------------------------
# Execution
# ---------------------------
def get_image_metadata(image_path: Path) -> dict[str, Any]:
    metadata: dict[str, str] = {}
    print(image_path.resolve())
    try:
        with Image.open(image_path) as image:
            metadata['Filename'] = os.path.basename(image.filename)
            metadata['Directory'] = os.path.dirname(image.filename)
            metadata['File Size'] = humanize.naturalsize(os.path.getsize(image_path), binary=True)
            metadata['Creation Date'] = time.ctime(os.path.getctime(image_path))
            metadata['Modification Date'] = time.ctime(os.path.getmtime(image_path))
            metadata['File Permissions'] = stat.filemode(os.stat(image_path).st_mode)
            metadata['Format'] = image.format
            metadata['Mode'] = image.mode
            metadata['Image Width'] = image.width
            metadata['Image Height'] = image.height
            exifdata: Any = image.getexif()
            for tag_id, value in exifdata.items():
                tag: str = ExifTags.TAGS.get(tag_id, tag_id)
                metadata[tag] = value
        return metadata
    except Exception as e:
        print(f'{color.WARNING}Skipping image: {e}{color.RESET}')
        return metadata

def display_all_metadata(args: Args) -> None:
    i: int = 1
    for image in args.image:
        print_image_header(args, i, image)
        metadata: dict[str, Any] = get_image_metadata(image)
        print_image_metadata(metadata)
        i += 1

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    print_header()
    args: Args = parse_args()
    display_all_metadata(args)

if __name__ == '__main__':
    main()
