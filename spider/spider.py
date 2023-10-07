import argparse
import pathlib
import requests
from urllib.parse import ParseResult, urlparse
import re

HEADER = '''
███████ ██████  ██ ██████  ███████ ██████
██      ██   ██ ██ ██   ██ ██      ██   ██
███████ ██████  ██ ██   ██ █████   ██████
     ██ ██      ██ ██   ██ ██      ██   ██
███████ ██      ██ ██████  ███████ ██   ██

'''.format(0, 1, 2, 3, 4, 5, 6)
DEFAULT_DEPTH = 5
DEFAULT_PATH = './data'

Args = argparse.Namespace
Parser = argparse.ArgumentParser

# ---------------------------
# Argument parsing
# ---------------------------
def check_url(url: str) -> None:
    print(url)
    result: ParseResult = urlparse(url)
    if not result.scheme or not result.netloc:
        raise Exception()
    if result.scheme != 'http':
        raise Exception()

def validate_url(args: Args) -> None:
    try:
        check_url(args.URL)
    except Exception:
        if not re.match('^[a-z]*://', args.URL):
            args.URL = 'http://' + args.URL
            validate_url(args)
        else:
            raise Exception(f'{args.URL}: invalid URL')

def parse_args() -> Args:
    parser: Parser = Parser(description = 'An image scrapper')
    parser.add_argument('-r', '--recursive', action = 'store_true', help = 'download images recursively (to depth level 5 by default)')
    parser.add_argument('-l', '--level', dest = 'depth', type = int, help = 'depth level of recursive image search')
    parser.add_argument('-p', '--path', type = pathlib.Path, help = 'path to save downloaded images')
    parser.add_argument('URL', help = 'URL to download images from')
    args: Args = parser.parse_args()
    if args.recursive and (args.depth is None):
        args.depth = DEFAULT_DEPTH
    if args.depth and (args.recursive is False):
        parser.error("argument -l/--level: expected -r/--recursive argument.")
    if args.path is None:
        args.path = pathlib.Path(DEFAULT_PATH)
    return args

# ---------------------------
# Execution
# ---------------------------
def crawl(args: Args) -> None:
    try:
        validate_url(args)
        res = requests.get(args.URL, headers={"User-Agent":"Mozilla/5.0"}, timeout = 1)
        print(type(res))
        print(res.status_code)
        res.raise_for_status()
        if res.status_code != 200:
            print(f'spider.py: error: cannot access URL (HTTP response {res.status_code})')
        print("Ready to crawl")
    except requests.exceptions.HTTPError as e:
        print(f'spider.py: HTTP error: {e}')
    except requests.exceptions.ConnectionError as e:
        print(f'spider.py: Connection error: {e}')
    except requests.exceptions.Timeout as e:
        print(f'spider.py: Timeout error: {e}')
    except requests.exceptions.RequestException as e:
        print(f'spider.py: Fatal error: {e}')
    except Exception as e:
        print(f'spider.py: error: {e}')

# ---------------------------
# Prettify
# ---------------------------
def print_header() -> None:
    for line in HEADER.splitlines():
        print('{:^70}'.format(line))

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    print_header()
    args : Args = parse_args()
    print(args)
    crawl(args)

if __name__ == '__main__':
    main()
