import argparse
import os
import pathlib
import stat
import time
import typing
from PIL import Image, ExifTags
import humanize

# TODO: Check this out: https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-python/
# For exif modification and deletion

HEADER = '''
███████  ██████  ██████  ██████  ██████  ██  ██████  ███    ██ 
██      ██      ██    ██ ██   ██ ██   ██ ██ ██    ██ ████   ██ 
███████ ██      ██    ██ ██████  ██████  ██ ██    ██ ██ ██  ██ 
     ██ ██      ██    ██ ██   ██ ██      ██ ██    ██ ██  ██ ██ 
███████  ██████  ██████  ██   ██ ██      ██  ██████  ██   ████ 
                                                               
'''
SEPARATOR = '{:^30}'.format('---')
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

def print_image_metadata_header(args: Args, image_number: int, image: Path) -> None:
    print('{:-^80}'.format(''))
    print(f'[{color.INFO}{image_number}{color.RESET}/{len(args.image)}] Metadata for image: {color.INFO}{image}{color.RESET}')
    print('{:-^80}'.format(''))

def print_deleting_metadata_header() -> None:
    print('{:-^80}'.format(''))
    print(f'Deleting metadata')
    print('{:-^80}'.format(''))

def print_deleting_image_metadata(args: Args, image_number: int, image: Path, save: str) -> None:
    print(f'[{color.INFO}{image_number}{color.RESET}/{len(args.image)}] Deleting metadata for image: {color.INFO}{image}{color.RESET}')
    print(f'Saving stripped image to: {color.INFO}{save}{color.RESET}')

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
    parser.add_argument('-d', '--delete', action = 'store_true', default = False, help = 'delete all exif data from image(s)')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'Enable verbose mode')
    args: Args = parser.parse_args()
    return args

# ---------------------------
# Metadata extraction
# ---------------------------
def extract_basic_file_info(image_path: Path, metadata: dict[str, Any]) -> None:
    metadata['Filename'] = os.path.basename(image_path)
    metadata['Directory'] = os.path.dirname(image_path.resolve())
    metadata['File Size'] = humanize.naturalsize(os.path.getsize(image_path), binary=True)
    metadata['Creation Date'] = time.ctime(os.path.getctime(image_path))
    metadata['Modification Date'] = time.ctime(os.path.getmtime(image_path))
    metadata['File Permissions'] = stat.filemode(os.stat(image_path).st_mode)

def extract_basic_image_info(image: Any, metadata: dict[str, Any]) -> None:
    metadata['Format'] = image.format
    metadata['Mode'] = image.mode
    metadata['Image Width'] = image.width
    metadata['Image Height'] = image.height

def add_separator(metadata: dict[str, Any]) -> None:
    metadata[SEPARATOR] = SEPARATOR

def extract_image_exif(image: Any, metadata: dict[str, Any]) -> None:
    exifdata: Any = image.getexif()
    for tag_id, value in exifdata.items():
        tag: str = ExifTags.TAGS.get(tag_id, tag_id)
        metadata[tag] = value

def display_image_metadata(args: Args, image_path: Path, index: int) -> None:
    print_image_metadata_header(args, index, image_path)
    metadata: dict[str, Any] = {}
    try:
        extract_basic_file_info(image_path, metadata)
        with Image.open(image_path) as image:
            extract_basic_image_info(image, metadata)
            add_separator(metadata)
            extract_image_exif(image, metadata)
        print_image_metadata(metadata, args.verbose)
    except Exception as e:
        add_separator(metadata)
        print_image_metadata(metadata, args.verbose)
        print(f'{color.WARNING}Skipping image: {e}{color.RESET}')

# ---------------------------
# Metadata deletion
# ---------------------------
def build_stripped_file_name(image_path: Path) -> str:
    dir: str = os.path.dirname(image_path.resolve())
    ext: str = os.path.splitext(image_path)[-1]
    name: str = os.path.splitext(image_path)[-2] + '.stripped'
    return dir + '/' + name + ext

def strip_image_metadata(args: Args, image_path: Path, index: int) -> None:
    try:
        with Image.open(image_path) as original:
            data: list = list(original.getdata())
            stripped: Any = Image.new(original.mode, original.size)
            stripped.putdata(data)
            save_name: str = build_stripped_file_name(image_path)
            stripped.save(save_name)
            print_deleting_image_metadata(args, index, image_path, save_name)
    except Exception as e:
        print(f'{color.WARNING}Skipping image: {e}{color.RESET}')

# ---------------------------
# Main
# ---------------------------
def process_metadata(args: Args) -> None:
    for i, image in enumerate(args.image):
        if args.delete:
            print_deleting_metadata_header()
            strip_image_metadata(args, image, i + 1)
        else:
            display_image_metadata(args, image, i + 1)

def main() -> None:
    print_header()
    args: Args = parse_args()
    process_metadata(args)
    print('{:-^80}'.format(''))

if __name__ == '__main__':
    main()
