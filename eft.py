# LibEFT Python 3.8.5 implementation
# May 28, 2023
# Written by @annabelsandford
# Based on the C implementation by @FuzzyQuills
# https://github.com/FuzzyQuills/libeft
# --------------------------------------------------

# from depression import painkillers cause imaboutta kill myself
import importlib.util
import subprocess
import urllib.request

# Check if PIL is installed
spec = importlib.util.find_spec("PIL")
if spec is None:
    # PIL is not installed, download and install it
    print("PIL is not installed. Downloading and installing...")
    urllib.request.urlretrieve("https://bootstrap.pypa.io/pip/2.7/get-pip.py", "get-pip.py")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/python-pillow/Pillow/master/requirements.txt", "requirements.txt")
    
    # Install pip
    subprocess.run(["python", "get-pip.py"])
    
    # Install Pillow requirements
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    print("PIL installation complete.")

# Import PIL
from PIL import Image
import struct

# EFT magic number
EFT_MAGIC_NUM = 1103806595072

# Dimensions table entry
class EftDimensionsTableEntry:
    def __init__(self, code, actual_size):
        self.code = code
        self.actual_size = actual_size

# Dimensions table
image_size_table = [
    EftDimensionsTableEntry(0x1, 512),
    EftDimensionsTableEntry(0x2, 1024),
    EftDimensionsTableEntry(0x3, 1536),
    EftDimensionsTableEntry(0x4, 2048),
    EftDimensionsTableEntry(0x5, 2560),
    EftDimensionsTableEntry(0x6, 3072),
    EftDimensionsTableEntry(0x7, 3584),
    EftDimensionsTableEntry(0x8, 4096),
    EftDimensionsTableEntry(0x9, 4608),
    EftDimensionsTableEntry(0xA, 5120),
    EftDimensionsTableEntry(0xB, 5632),
    EftDimensionsTableEntry(0xC, 6144),
    EftDimensionsTableEntry(0xD, 6656),
    EftDimensionsTableEntry(0xE, 7168),
    EftDimensionsTableEntry(0xF, 7680),
    EftDimensionsTableEntry(0x10, 8192)
]

# EFT file structure
class EftFile:
    def __init__(self):
        self.magic = 0
        self.height = 0
        self.width = 0
        self.garbage = None
        self.data = None

# Color structure
class Color:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 0

# Writes a single RGBA block from an EFT's tilemap into the RGBA buffer
def write_eft_tiles(input, tileindexes, tilecount, width, height, use_bgra, swap_wh):
    output = [Color() for _ in range(width * height)]

    blocknum = 0
    height_stride = width if swap_wh else height
    width_stride = height if swap_wh else width

    for y in range(height_stride // 512):
        for x in range(width_stride // 512):
            for y_512 in range(512):
                for x_512 in range(512):
                    x_offset_512 = (x_512 + 8) & 511
                    y_offset_512 = (y_512 + 4) & 511 if x_512 > 503 else y_512

                    tile_address = blocknum  # Experimental tile data load (unused, some EFTs have strange tile data)

                    if use_bgra:
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].b = input[tile_address][(y_offset_512 * 512) + x_offset_512].b  # r
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].g = input[tile_address][(y_offset_512 * 512) + x_offset_512].g  # g
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].r = input[tile_address][(y_offset_512 * 512) + x_offset_512].r  # b
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].a = input[tile_address][(y_offset_512 * 512) + x_offset_512].a  # a
                    else:
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].r = input[tile_address][(y_offset_512 * 512) + x_offset_512].r  # r
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].g = input[tile_address][(y_offset_512 * 512) + x_offset_512].g  # g
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].b = input[tile_address][(y_offset_512 * 512) + x_offset_512].b  # b
                        output[(y_512 + y * 512) * width_stride + x * 512 + x_512].a = input[tile_address][(y_offset_512 * 512) + x_offset_512].a  # a

            blocknum += 1

    return output

# Converts an EFT tile's S3TC texture data to RGBA format
def eft2rgba(input, tileindex, use_bgra):
    color0 = 0  # color 0
    color1 = 0  # color 1
    codes = 0  # code stream to decode 4x4 block

    rgba_buf = [Color() for _ in range(512 * 512)]

    height_in_blocks = 512 // 4
    width_in_blocks = 512 // 4

    for y in range(height_in_blocks):
        for x in range(width_in_blocks):
            # First, copy the needed values from the input
            color0 = struct.unpack("<H", input[(131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) : (131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) + 2])[0]
            color1 = struct.unpack("<H", input[(131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) + 2 : (131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) + 4])[0]

            #print(f"Tile {tileindex}, Block ({x}, {y}), Color0: {color0}, Color1: {color1}")

            codes = struct.unpack("<I", input[(131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) + 4 : (131072 * tileindex) + (y * 8 * width_in_blocks) + (x * 8) + 8])[0]

            reversed_codes = int.from_bytes(codes.to_bytes(4, "little"), "little")

            color0_rgb = [
                ((color0 >> 11) & 0x1F) * 527 + 23 >> 6,
                ((color0 >> 5) & 0x3F) * 259 + 33 >> 6,
                (color0 & 0x1F) * 527 + 23 >> 6,
            ]

            color1_rgb = [
                ((color1 >> 11) & 0x1F) * 527 + 23 >> 6,
                ((color1 >> 5) & 0x3F) * 259 + 33 >> 6,
                (color1 & 0x1F) * 527 + 23 >> 6,
            ]

            for yb in range(4):
                for xb in range(4):
                    bitshift_amount_x = xb * 2
                    bitshift_amount_y = yb * 4 * 2

                    if color0 > color1:
                        code = (reversed_codes >> (bitshift_amount_x + bitshift_amount_y)) & 0x3
                        if code == 0x0:
                            rgb_row = color0_rgb
                        elif code == 0x1:
                            rgb_row = color1_rgb
                        elif code == 0x2:
                            rgb_row = [
                                (2 * color0_rgb[0] + color1_rgb[0]) // 3,
                                (2 * color0_rgb[1] + color1_rgb[1]) // 3,
                                (2 * color0_rgb[2] + color1_rgb[2]) // 3,
                            ]
                        elif code == 0x3:
                            rgb_row = [
                                (color0_rgb[0] + 2 * color1_rgb[0]) // 3,
                                (color0_rgb[1] + 2 * color1_rgb[1]) // 3,
                                (color0_rgb[2] + 2 * color1_rgb[2]) // 3,
                            ]
                    elif color0 <= color1:
                        code = (reversed_codes >> (bitshift_amount_x + bitshift_amount_y)) & 0x3
                        if code == 0x0:
                            rgb_row = color0_rgb
                        elif code == 0x1:
                            rgb_row = color1_rgb
                        elif code == 0x2:
                            rgb_row = [
                                (color0_rgb[0] + color1_rgb[0]) // 2,
                                (color0_rgb[1] + color1_rgb[1]) // 2,
                                (color0_rgb[2] + color1_rgb[2]) // 2,
                            ]
                        elif code == 0x3:
                            rgb_row = [0, 0, 0]

                    if use_bgra:
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].b = rgb_row[0]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].g = rgb_row[1]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].r = rgb_row[2]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].a = 255
                    else:
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].r = rgb_row[0]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].g = rgb_row[1]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].b = rgb_row[2]
                        rgba_buf[(yb + y * 4) * 512 + (4 * x) + xb].a = 255

    return rgba_buf

def get_garbage_data(data, header_offset, tile_count, tile_entry_size):
    garbage_start = header_offset + tile_count * tile_entry_size
    garbage_data = data[garbage_start:]
    return garbage_data

HEADER_SIZE = 1024
TILE_ENTRY_SIZE = 131072

# Parses an EFT file and returns the RGBA buffer
def parse_eft_file(filename, use_bgra=False, swap_wh=False):
    with open(filename, "rb") as f:
        eft_data = f.read()

    eft_file = EftFile()

    eft_file.magic = struct.unpack("<Q", eft_data[:8])[0]
    dimensions_table_code = struct.unpack("<H", eft_data[8:10])[0]
    eft_file.height = next(entry.actual_size for entry in image_size_table if entry.code == dimensions_table_code)
    eft_file.width = eft_file.height  # Set width equal to height for square tiles
    eft_file.garbage = eft_data[12:16]
    eft_file.data = eft_data[16:]

    if eft_file.magic != EFT_MAGIC_NUM:
        raise ValueError("Invalid EFT file")

    tile_count = len(eft_file.data) // TILE_ENTRY_SIZE

    header_offset = HEADER_SIZE
    garbage_data = get_garbage_data(eft_file.data, header_offset, tile_count, TILE_ENTRY_SIZE)

    rgba_buffer = [
        eft2rgba(eft_file.data, i, use_bgra) for i in range(tile_count)
    ]

    output_width = eft_file.width #* 512
    output_height = eft_file.height #* 512

    print(f"EFT file width: {eft_file.width}")
    print(f"EFT file height: {eft_file.height}")
    print(f"Tile count: {tile_count}")
    print(f"Output width: {output_width}")
    print(f"Output height: {output_height}")

    return rgba_buffer, output_width, output_height

rgba_buffer, output_width, output_height = parse_eft_file("example.eft")

image = Image.new('RGBA', (output_width, output_height))
pixels = image.load()
for tile_y in range(output_height // 512):
    for tile_x in range(output_width // 512):
        for y in range(512):
            for x in range(512):
                color = rgba_buffer[(tile_y * (output_width // 512) + tile_x)][(y * 512) + x]
                image_x = tile_x * 512 + x
                image_y = tile_y * 512 + y
                pixels[image_x, image_y] = (color.r, color.g, color.b, color.a)

image.save("output.tga")
