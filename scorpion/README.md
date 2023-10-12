# Scorpion

Scorpion is a small image metadata viewing script in Python. It can display and delete the exif data of the specified image(s).

## Requirements

- Python3
- Pillow

## Usage

Clone this repository and `cd` into `Arachnida/scorpion`.

To run the program, use:

```bash
python3 scorpion.py [-d/--delete][-v/--verbose] image [image...]
```

The options are as follows:

- `image` (one required): Path to an image (or several space-separated images) for which to view/delete metadata.
- `-d` (optional): Enable deletion mode: a copy of the image will be created, stripped of all of its exif data.
- `-h`: Display the help page.
- `-v`: Enable verbose mode.

---

Made by mcombeau: mcombeau@student.42.fr | LinkedIn: [mcombeau](https://www.linkedin.com/in/mia-combeau-86653420b/) | Website: [codequoi.com](https://www.codequoi.com)
