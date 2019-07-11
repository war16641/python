from GoodToolPython.lol.snapscreen import *
import time
import numpy as np
from PIL import ImageGrab
# import pytesseract
from PIL import Image
import random
if __name__ == '__main__':
    # im=snap_screen(bbox='full')
    # im.show()
    im=Image.open("e:/d2.bmp")
    # im1=im.convert("L")
    # im1.show()
    im2=do_with_image2(im)
    im2.show()
    im3=im2.resize((7,12))
    im3.show()
    im3.save("e:/d2_py.bmp")