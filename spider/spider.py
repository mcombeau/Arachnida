import argparse
import os
import pathlib
import re
import requests
from bs4 import BeautifulSoup, ResultSet
from urllib.parse import ParseResult, urljoin, urlparse

HEADER = '''
███████ ██████  ██ ██████  ███████ ██████
██      ██   ██ ██ ██   ██ ██      ██   ██
███████ ██████  ██ ██   ██ █████   ██████
     ██ ██      ██ ██   ██ ██      ██   ██
███████ ██      ██ ██████  ███████ ██   ██

'''
DEFAULT_DEPTH = 5
DEFAULT_PATH = './data'
EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

Args = argparse.Namespace
Parser = argparse.ArgumentParser
Res = requests.Response

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

def print_args(args: Args) -> None:
    print('{:-^80}'.format(''))
    print(f'[+] URL to scrape: {color.INFO}{args.URL}{color.RESET}')
    if args.recursive:
        print(f'[+] Scraping recursively to depth level: {color.INFO}{args.depth}{color.RESET}')
    print(f'[+] Saving images to directory: {color.INFO}{args.path}{color.RESET}')
    print('{:-^80}'.format(''))

def print_depth_header(depth: int) -> None:
    print('{:=^80}'.format(''))
    print('{:^80}'.format(f'Depth {depth}'))
    print('{:=^80}'.format(''))

def print_downloading_header(url: str, depth: int) -> None:
    print('{:-^80}'.format(''))
    print(f'[Depth: {depth}] Downloading images from: {url}')
    print('{:-^80}'.format(''))

def print_total_downloaded(args: Args, download_count: int) -> None:
    print('')
    print('{:-^80}'.format(''))
    print(f'TOTAL: {download_count} images downloaded from {args.URL}')
    print('{:-^80}'.format(''))

# ---------------------------
# Argument parsing
# ---------------------------
def check_url(url: str) -> None:
    result: ParseResult = urlparse(url)
    if not result.scheme:
        raise Exception('URL must have a scheme such as http or https')
    elif not result.netloc:
        raise Exception('no network location for URL')
    if (result.scheme != 'https' and result.scheme != 'http'):
        raise Exception('URL scheme must be http or https')

def validate_url(args: Args) -> None:
    try:
        check_url(args.URL)
    except Exception as e:
        if not re.match('^[a-z]*://', args.URL):
            args.URL = 'http://' + args.URL
            validate_url(args)
        else:
            raise Exception(f'{args.URL}: invalid URL: {e}')

def parse_args() -> Args:
    parser: Parser = Parser(description = 'An image scrapper')
    parser.add_argument('-r', '--recursive', action = 'store_true', help = 'download images recursively (to depth level 5 by default)')
    parser.add_argument('-l', '--level', dest = 'depth', type = int, help = 'depth level of recursive image search')
    parser.add_argument('-p', '--path', type = pathlib.Path, help = 'path to save downloaded images')
    parser.add_argument('URL', help = 'URL to download images from')
    args: Args = parser.parse_args()
    if args.depth is None:
        if args.recursive:
            args.depth = DEFAULT_DEPTH
        else:
            args.depth = 1
    elif args.depth and (args.recursive is False):
        parser.error("argument -l/--level: expected -r/--recursive argument.")
    if args.path is None:
        args.path = pathlib.Path(DEFAULT_PATH)
    args.current_depth = 0
    return args

# ---------------------------
# Execution
# ---------------------------
def check_url_connection(args: Args) -> None:
    validate_url(args)
    r: Res = requests.get(args.URL, headers={"User-Agent":"Mozilla/5.0"}, timeout = 1)
    r.raise_for_status()
    if r.status_code != 200:
        print(f'spider.py: error: cannot access URL (HTTP response {r.status_code})')

def create_save_directory(args: Args) -> None:
    if not os.path.exists(args.path):
        print(f'Creating directory: {args.path.resolve()}')
        os.makedirs(args.path)
    elif not os.path.isdir(args.path):
        raise Exception(args.path.name + ': not a directory.')
    elif not os.access(args.path, os.W_OK) or not os.access(args.path, os.X_OK):
        raise Exception(args.path.name + ': Permission denied.')

def download_image(args: Args, image_url: str, save_dir: str) -> int:
    image_name: str = os.path.basename(image_url)
    save_path: str = os.path.join(save_dir, image_name)
    if os.path.exists(save_path):
        print(f'{color.WARNING}Skipping: {image_name}: image already exists in {save_dir} directory.{color.RESET}')
        return 0
    print(f'Downloading: {image_url}...')
    try:
        r: Res = requests.get(image_url)
        with open(save_path, 'wb') as f:
            f.write(r.content)
            print(f'{color.SUCCESS}Saved image to: {save_path}{color.RESET}')
            return 1
    except Exception as e:
        print(f'{color.WARNING}Skipping: {image_name}: {e}.{color.RESET}')
        return 0

def download_images_from_url(args: Args, url: str, soup: BeautifulSoup, current_depth: int) -> int:
    print_downloading_header(url, current_depth)
    count: int = 0
    download_count: int = 0
    image_tags: ResultSet = soup.find_all('img')
    for image_tag in image_tags:
        image_path: str = image_tag.get('src')
        image_ext: str = os.path.splitext(image_path)[-1]
        if image_ext.lower() not in EXTENSIONS:
            continue
        count += 1
        image_url: str = os.path.dirname(url) + image_path
        download_count += download_image(args, image_url, args.path)
    print(f'Downloaded {download_count} of {count} images from {url}')
    return download_count

def get_links_from_url(url: str, soup: BeautifulSoup) -> set[str]:
    urls: set[str] = set()
    links: ResultSet = soup.find_all('a')
    for link in links:
        href: str = link.get('href')
        if not href:
            continue
        if not href.startswith('http://') or not href.startswith('https://'):
            href: str = urljoin(url, href)
        if href.startswith(url):
            parse: ParseResult = urlparse(href)
            final_url: str = parse.scheme + '://' + parse.netloc + parse.path
            if final_url not in urls and final_url != url:
                urls.add(final_url)
    return urls

def download_images_recusively(args: Args, url: str, visited_urls: set = set(), current_depth: int = 0, download_count: int = 0) -> int:
    if current_depth >= args.depth:
        return download_count
    if url in visited_urls:
        return download_count
    visited_urls.add(url)
    r: Res = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(r.content, 'html.parser')
    download_count += download_images_from_url(args, url, soup, current_depth)
    links: set[str] = get_links_from_url(url, soup)
    print(f'Found {len(links)} links in URL')
    for link in links:
        download_images_recusively(args, link, visited_urls, current_depth + 1, download_count)
    return download_count

# TODO: check robots.txt to see if we are allowed to crawl this URL
def scrape(args: Args) -> None:
    try:
        check_url_connection(args)
        print(f'{color.SUCCESS}URL OK: {args.URL}{color.RESET}')
        create_save_directory(args)
        print(f'{color.SUCCESS}Save directory OK: {args.path.resolve()}{color.RESET}')
        count: int = download_images_recusively(args, args.URL)
        print_total_downloaded(args, count)
    except Exception as e:
        print(f'{color.ERROR}spider.py: error: {e}{color.RESET}')

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    print_header()
    args : Args = parse_args()
    print_args(args)
    scrape(args)

if __name__ == '__main__':
    main()
