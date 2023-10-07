import argparse
import pathlib

DEFAULT_DEPTH = 5
DEFAULT_PATH = './data'

Args = argparse.Namespace
Parser = argparse.ArgumentParser

# ---------------------------
# Argument parsing
# ---------------------------
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
def crawl() -> None:
    print("Ready to crawl")

# ---------------------------
# Prettify
# ---------------------------
def print_header() -> None:
    print('')
    print('\t███████ ██████  ██ ██████  ███████ ██████')
    print('\t██      ██   ██ ██ ██   ██ ██      ██   ██')
    print('\t███████ ██████  ██ ██   ██ █████   ██████')
    print('\t     ██ ██      ██ ██   ██ ██      ██   ██')
    print('\t███████ ██      ██ ██████  ███████ ██   ██')
    print('')

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    print_header()
    args : Args = parse_args()
    print(args)

if __name__ == '__main__':
    main()
