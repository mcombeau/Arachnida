import argparse
import os
import pathlib
import re
import requests
from bs4 import BeautifulSoup, ResultSet
from urllib.parse import ParseResult, urljoin, urlparse
from urllib import robotparser
from typing import Optional

USER_AGENT = "SpiderBot"
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
RobotParser = robotparser.RobotFileParser

total_downloads: int = 0

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

def print_visiting_header(url: str, depth: int) -> None:
    print('{:-^80}'.format(''))
    print(f'[Depth: {depth}] Visiting URL: {url}')
    print('{:-^80}'.format(''))

def print_total_downloaded(args: Args) -> None:
    global total_downloads
    print('')
    print('{:-^80}'.format(''))
    print('TOTAL:{:>83}'.format(f'{color.INFO}{total_downloads}{color.RESET} images downloaded'))
    print('SAVE DIR:{:>80}'.format(f'{color.INFO}{args.path.resolve()}{color.RESET}'))
    print('{:-^80}'.format(''))

# ---------------------------
# Argument parsing
# ---------------------------
def parse_args() -> Args:
    parser: Parser = Parser(description = 'An image scrapper')
    parser.add_argument('-r', '--recursive', action = 'store_true', help = 'download images recursively (to depth level 5 by default)')
    parser.add_argument('-l', '--level', dest = 'depth', type = int, help = 'depth level of recursive image search')
    parser.add_argument('-p', '--path', type = pathlib.Path, help = 'path to save downloaded images')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'Enable verbose mode')
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

def create_save_directory(args: Args) -> None:
    if not os.path.exists(args.path):
        print(f'Creating directory: {args.path.resolve()}')
        os.makedirs(args.path)
    elif not os.path.isdir(args.path):
        raise Exception(args.path.name + ': not a directory.')
    elif not os.access(args.path, os.W_OK) or not os.access(args.path, os.X_OK):
        raise Exception(args.path.name + ': Permission denied.')
    print(f'{color.SUCCESS}Save directory OK: {args.path.resolve()}{color.RESET}')

# ---------------------------
# URL validation and resolution
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

def check_url_connection(args: Args) -> None:
    validate_url(args)
    check_robots(args.URL, True)
    r: Res = requests.get(args.URL, headers={"User-Agent":USER_AGENT}, timeout = 5)
    r.raise_for_status()
    if r.status_code != 200:
        print(f'spider.py: error: cannot access URL (HTTP response {r.status_code})')
    print(f'{color.SUCCESS}URL OK (200 response): {args.URL}{color.RESET}')

def check_robots(url: str, print_success: bool = False) -> None:
    path_to_check: str = urlparse(url).path
    base_url: str = urlparse(url).scheme + '://' + urlparse(url).netloc
    robots_url: str = base_url + '/robots.txt'
    parser: RobotParser  = robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.read()
    can_fetch: bool = parser.can_fetch(USER_AGENT, path_to_check)
    if can_fetch == False:
        raise Exception(robots_url + ' forbids path: ' + path_to_check)
    if print_success:
        print(f'{color.SUCCESS}URL robots.txt OK: {robots_url}{color.RESET}')

def resolve_full_url(base_url: str, path: str) -> str:
    parse: ParseResult = urlparse(path)
    if not parse.netloc:
        return urljoin(base_url, parse.path)
    elif not parse.scheme:
        return 'http://' + parse.netloc + parse.path
    return parse.scheme + '://' + parse.netloc + parse.path

def get_link_from_href(base_url: str, href: str, urls: set[str]) -> Optional[str]:
    if not href:
        return None
    link: str = resolve_full_url(base_url, href)
    if link in urls or link == base_url:
        return None
    parse_base_url: ParseResult = urlparse(base_url)
    parse_link_url: ParseResult = urlparse(link)
    if parse_base_url.netloc != parse_link_url.netloc:
        return None
    return link

def get_links_from_url(url: str, soup: BeautifulSoup) -> set[str]:
    urls: set[str] = set()
    hrefs: ResultSet = soup.find_all('a')
    for h in hrefs:
        href: str = h.get('href')
        link: str | None = get_link_from_href(url, href, urls)
        if not link or link is None:
            continue
        else:
            urls.add(link)
    return urls

# ---------------------------
# Image download
# ---------------------------
def download_image(image_url: str, save_dir: str) -> int:
    global total_downloads
    image_name: str = os.path.basename(image_url)
    save_path: str = os.path.join(save_dir, image_name)
    if os.path.exists(save_path):
        print(f'{color.WARNING}Skipping: {image_name}: image already exists in {save_dir} directory.{color.RESET}')
        return 0
    try:
        check_robots(image_url)
        r: Res = requests.get(image_url, stream = True, headers={"User-Agent":USER_AGENT}, timeout = 5)
        with open(save_path, 'wb') as f:
            f.write(r.content)
            f.close()
            total_downloads += 1
            print(f'{color.SUCCESS}Downloaded image: {save_path}{color.RESET}')
            return 1
    except Exception as e:
        print(f'{color.WARNING}Skipping: {image_name}: {e}.{color.RESET}')
        return 0

def download_images_from_url(args: Args, url: str, soup: BeautifulSoup) -> None:
    count: int = 0
    download_count: int = 0
    image_tags: ResultSet = soup.find_all('img')
    for image_tag in image_tags:
        image_path: str = image_tag.get('src')
        image_ext: str = os.path.splitext(image_path)[-1]
        if image_ext.lower() not in EXTENSIONS:
            continue
        count += 1
        image_url: str = resolve_full_url(url, image_path)
        if args.verbose:
            print(f'Downloading: {image_url}...')
        download_count += download_image(image_url, args.path)
    print(f'Downloaded {download_count} of {count} images from {url}')

def download_images_recusively(args: Args, url: str, visited_urls: set = set(), current_depth: int = 0, download_count: int = 0) -> None:
    if current_depth >= args.depth:
        return
    if url in visited_urls:
        return
    visited_urls.add(url)
    print_visiting_header(url, current_depth)
    try:
        check_robots(url)
        r: Res = requests.get(url, headers={"User-Agent":USER_AGENT}, timeout = 5)
        soup: BeautifulSoup = BeautifulSoup(r.content, 'html.parser')
        download_images_from_url(args, url, soup)
        if current_depth + 1 < args.depth:
            links: set[str] = get_links_from_url(url, soup)
            print(f'{color.INFO}Discovered {len(links)} links in URL{color.RESET}')
            for link in links:
                download_images_recusively(args, link, visited_urls, current_depth + 1, download_count)
    except Exception as e:
        print(f'{color.ERROR}Skipping URL: {e}{color.RESET}')

# ---------------------------
# Main
# ---------------------------
def scrape(args: Args) -> None:
    try:
        check_url_connection(args)
        create_save_directory(args)
        download_images_recusively(args, args.URL)
        print_total_downloaded(args)
    except Exception as e:
        print(f'{color.ERROR}spider.py: error: {e}{color.RESET}')

def main() -> None:
    print_header()
    args : Args = parse_args()
    print_args(args)
    scrape(args)

if __name__ == '__main__':
    main()
