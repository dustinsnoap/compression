#0-9 represents a color
#a-z represents 4 bits
#A-Z represents 8 bits
#|a-z represents 16 bits
#|A-Z represents 32 bits
#The letter combination represents how far to go back

import cv2, numpy, math
image = cv2.imread('./test_data/test.png', -1)
image = numpy.array(image).tolist()

# print(uncompressed)
#general helpers
def getDigitsPerNumber(bitmap):
    max = 0
    for row in uncompressed:
        for tile in row:
            for tile_row in tile:
                for tile_col in tile_row:
                    max = tile_col if tile_col > max else max
    return len(str(max))

def getHex(color):
    r = str(hex(color[2]).split('x')[-1])
    if len(r) == 1: r = '0'+r
    g = str(hex(color[1]).split('x')[-1])
    if len(g) == 1: g = '0'+g
    b = str(hex(color[0]).split('x')[-1])
    if len(b) == 1: b = '0'+b
    return r+g+b  

def isTransparent(color):
    if len(color) == 3: return False
    if len(color) == 4 and color[3] == 255: return False
    return True

def convertImageToHex(image):
    hex_image = list()
    for row in image:
        hex_row = list()
        for col in row:
            if isTransparent(col): hex_row.append(0)
            else: hex_row.append(getHex(col))
        hex_image.append(hex_row)
    return hex_image

def convertImageToColorMap(image, colors):
    converted = list()
    for row in image:
        new_row = list()
        for col in row:
            if col in colors: new_row.append(colors[col])
            else: new_row.append(0)
        converted.append(new_row)
    return converted

def convertImageToString(image, colors):
    digits = len(str(len(colors)))
    converted = str()
    for row in image:
        for col in row:
            col = '0'*(digits-len(str(col)))+str(col)
            converted += col
    return converted

def getString(distance, chunk_size):
    if chunk_size%2 == 1 or chunk_size > 64:
        print('!!!INVALID CHUNK SIZE!!!')
        return -1
    digits_needed = math.ceil(math.log(distance+1, 26))
    base = 26
    chars = str()
    string = chr(int(chunk_size/2 + 31))
    for d in range(digits_needed):
        num = (distance//(base**d))%base
        chars = chr(num+97) + chars
    # print('s1', chars)
    for c in chars:
        if chunk_size == 8 or chunk_size == 32: c = c.upper()
        string += c
    return string

#worker helper functions
def createColorDict(image):
    color_dict = dict()
    counter = 1
    for row in image:
        for col in row:
            if col != 0 and col not in color_dict:
                color_dict[col] = counter
                counter += 1
    return color_dict

def compressString(string):
    new_string = str()
    # string = string[:36]
    maxi = len(string)
    block_size = 32
    i = 0
    while i < len(string):
        remaining = maxi - i
        index = int()
        char = string[i]
        if i >= block_size and remaining >= block_size:
            searchable_string = string[:i]
            search_string = string[i:i+block_size]
            index = searchable_string.rfind(search_string)
            if i != index and index != -1:
                distance = i - index
                char = getString(distance, block_size)
                i += block_size-1
        i += 1
        new_string += char
    print('old string:')
    print(string)
    print('new string:')
    print(new_string)
    ratio = math.floor(1000*(1-len(new_string)/len(string)))/10
    print(f'block size: {block_size} --- size: {len(string)} => {len(new_string)} --- compression ratio: {ratio}%')
    return new_string

def compressImage(image):
    image_height = len(image)
    image_width = len(image[0])
    image = convertImageToHex(image)
    colors = createColorDict(image)
    image = convertImageToColorMap(image, colors)
    string = convertImageToString(image, colors)
    # print(string[0:36])
    compressString(string)
    return {
        'height': image_height,
        'width': image_width,
        'colors': colors
    }

compressImage(image)