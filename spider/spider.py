import sys

# ---------------------------
# Argument parsing
# ---------------------------
def check_args(args: list):
    if len(args) == 0 or len(args) > 6:
        print('usage: python3 spider.py [-r][-l depth level][-p path] URL')
        exit(1)
    if ('-h' in args or '--help' in args):
        print('usage: python3 spider.py [-r][-l depth level][-p path] URL')
        print('\t-r: recursively download images from the URL')
        print('\t-l [N]: maximum depth level N of recusive download')
        print('\t-p [path]: path where downloaded files should be saved')
        print('\t-h: display help page')
        exit(1)

def get_url(options: dict, arg: str):
    if options['url'] == '':
        options['url'] = arg
    else:
        print('Error: Only one URL at a time, please!')
        exit (1)

def get_depth(options:dict, arg: str, it_args: iter, args: list):
    if not '-r' in args:
        print('Error: -l option requires accompanying -r option')
        exit (1)
    try:
        arg = next(it_args)
        if arg.isnumeric():
            options['depth'] = int(arg)
        else:
            raise Exception()
    except Exception as e:
        print('Error: -l depth option requires a numeric value')
        exit (1)

def get_path(options: dict, arg: str, it_args:iter):
    try:
        arg = next(it_args)
        options['path'] = arg
    except Exception as e:
        print('Error: -p option requires a path', e)
        exit (1)

def parse_args(options: dict):
    args: list = sys.argv.copy()
    args.pop(0)
    check_args(args)
    it_args = iter(args)
    for arg in it_args:
        if arg == '-r':
            options['recursive'] = True
        elif arg == '-l':
            get_depth(options, arg, it_args, args)
        elif arg == '-p':
            get_path(options, arg, it_args)
        elif arg[0] == '-':
            print(f'Error: {arg}: Unknown option')
            exit (1)
        else:
            get_url(options, arg)

def verify_options(options: dict):
    if options['url'] == '':
        print('Error: Please provide a URL to crawl')
        exit (1)

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
    options: dict = {
        'url': '',
        'recursive': False,
        'depth': 5,
        'path': './data/',
    }
    print_header()
    parse_args(options)
    verify_options(options)
    print_crawling_options(options)
    crawl(options)

if __name__ == '__main__':
    main()
