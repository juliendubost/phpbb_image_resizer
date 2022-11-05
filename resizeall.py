import os
import sys
import re
import glob
import argparse
import magic
from PIL import Image
from resizeimage import resizeimage


CONTAIN_WIDTH = 1024
CONTAIN_HEIGHT = 768


def fetch_image_files(rootpath, filter_extension=True):

    extension_regexp = "(?i)(jpe?g|png|gif|bmp)"
    image_full_paths = []

    for dirpath, dirs, filenames in os.walk(rootpath):
        for filename in filenames:
            if filter_extension:
                search = re.search(extension_regexp, filename)
                if search is not None:
                    image_full_paths.append(os.path.join(dirpath, filename))
            else:
                image_full_paths.append(os.path.join(dirpath, filename))

    return image_full_paths


def resize_and_replace(filepath):

    fd_img = open(filepath, "r+b")
    sys.stdout.write(f"{filepath}\r")
    try:
        img = Image.open(fd_img)
    except Image.UnidentifiedImageError:
        return

    width, height = img.size
    if width > CONTAIN_WIDTH and height > CONTAIN_HEIGHT:
        img = resizeimage.resize_thumbnail(img, (CONTAIN_WIDTH, CONTAIN_HEIGHT))
        if not img.format:
            img.format = magic.from_file(filepath, mime=True).split("/")[-1].upper()
        img.save(filepath, format=img.format)
        sys.stdout.write(f"{filepath} -> resized\n")
        sys.stdout.flush()
        fd_img.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="resize all images files found in a given folder"
    )
    parser.add_argument(
        "path", help="image file path or folder path containing images to resize"
    )
    parser.add_argument(
        "--ignore-ext",
        action="store_true",
        help="ignore file extensions, in this case, try to open all files and ignore if an exception occurs (phpbb file names does not include extensions)",
    )
    args = parser.parse_args()
    if os.path.isdir(args.path):
        filepaths = fetch_image_files(args.path, not args.ignore_ext)
    else:
        filepaths = [args.path]
    for filepath in filepaths:
        resize_and_replace(filepath)
