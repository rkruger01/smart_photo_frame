from PIL import ImageDraw, Image


def main():
    height = 480
    width = 800
    Himage = Image.new('1', (height, width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, 0), 'hello world', fill=0)
    draw.text((10, 20), '7.5inch e-Paper', fill=0)
    draw.line((20, 50, 70, 100), fill=0)
    draw.line((70, 50, 20, 100), fill=0)
    draw.rectangle((20, 50, 70, 100), outline=0)
    draw.line((165, 50, 165, 100), fill=0)
    draw.line((140, 75, 190, 75), fill=0)
    draw.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw.rectangle((80, 50, 130, 100), fill=0)
    draw.chord((200, 50, 250, 100), 0, 360, fill=0)
    draw.line((0, 0) + (width, height), fill=0)
    Himage.show()


if __name__ == '__main__':
    main()
