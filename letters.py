import sys
from PIL import Image


def dotting(path):
    img = Image.open(path)
    dots = img.convert('L')
    letter_matrix = {'dots': []}
    for x in range(20):
        for y in range(15):
            if (g_scale_value := dots.getpixel((x,y))) == 0:
                letter_matrix['dots'].append((x,y))

    letter_matrix['size'] = dots.size
    return letter_matrix

def get_coords(char):
    if char in ['O']:
        return dotting(char)

if __name__ == '__main__':
    print(dotting(sys.argv[1]))
