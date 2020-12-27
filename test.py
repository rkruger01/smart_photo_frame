import logging
import os

from draw import image_draw

debug = True


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG" if debug else "INFO"))
    img = image_draw(800, 480)
    img.show()
    return 0


if __name__ == "__main__":
    main()
