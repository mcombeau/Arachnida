# Spider

Spider is a small image-scraping script in Python.

This bot respects `robots.txt`. Please do not use this program for malicious purposes.

## Usage

Clone this repository and `cd` into `Arachnida/spider`.

To run the program, use:

```bash
python3 spider.py URL [-r/--recursive][-l/--level N][-p/--path path]
```

The options are as follows:

- `URL` (required): The URL from which to scrape images.
- `-r` (optional): Enable recursive mode: the spider will follow the links it finds in the URL and download the images there as well. Default depth level is 5.
- `-l N` (optional): The depth level for recursive mode. Requires `-r` option.
- `-p path` (optional): The directory in which to save the downloaded images. By default, this path is `./data`.
- `-h`: Display the help page.
- `-v`: Enable verbose mode.

---

Made by mcombeau: mcombeau@student.42.fr | LinkedIn: [mcombeau](https://www.linkedin.com/in/mia-combeau-86653420b/) | Website: [codequoi.com](https://www.codequoi.com)
