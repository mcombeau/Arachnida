import sys
import argparse
import pathlib

# ---------------------------
# Argument parsing
# ---------------------------
def parse_args():
    parser = argparse.ArgumentParser(description = 'An image scrapper')
    parser.add_argument('-r', '--recursive', action = 'store_true', help = 'download images recursively (to depth level 5 by default)')
    parser.add_argument('-l', '--level', dest = 'depth', type = int, help = 'depth level of recursive image search')
    parser.add_argument('-p', '--path', type = pathlib.Path, help = 'path to save downloaded images')
    parser.add_argument('URL', help = 'URL to crawl')
    args = parser.parse_args()
    if args.recursive and (args.depth is None):
        args.depth = 5
    if args.depth and (args.recursive is False):
        parser.error("argument -l/--level: expected -r/--recursive argument.")
    print(args)
    return args


# ---------------------------
# Execution
# ---------------------------
def crawl(options: dict):
    print("Ready to crawl")

# ---------------------------
# Prettify
# ---------------------------
def print_header():
    print('')
    print('\t███████ ██████  ██ ██████  ███████ ██████')
    print('\t██      ██   ██ ██ ██   ██ ██      ██   ██')
    print('\t███████ ██████  ██ ██   ██ █████   ██████')
    print('\t     ██ ██      ██ ██   ██ ██      ██   ██')
    print('\t███████ ██      ██ ██████  ███████ ██   ██')
    print('')
                                           

def print_crawling_options(options: dict):
    print(f"Crawling {options['url']}", end="")
    if options['recursive']:
        print(f" recusively to depth {options['depth']}", end="")
    print(f". Saving images to {options['path']}")

# ---------------------------
# Main
# ---------------------------
def main():
    print_header()
    args = parse_args()
    print(args)

if __name__ == '__main__':
    main()
