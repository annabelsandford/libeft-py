# LibEFT Python

This is a Python implementation of the LibEFT library, originally written in C by @FuzzyQuills. The Python version is based on the C implementation and aims to provide similar functionality for working with EFT (Emergency File Texture) image files.

## Features

- Parsing EFT files and extracting RGBA image data
- Converting EFT tile's S3TC texture data to RGBA format
- Writing RGBA blocks from an EFT's tilemap to an RGBA buffer
- Saving the RGBA buffer as a TGA image file

## Requirements
This implementation requires Python 3.8.5 or above.
The required PIL (Python Imaging Library) or Pillow package is automatically checked and installed if not found.

## Usage

To use LibEFT Python, follow these steps:

1. Ensure you have the Python interpreter installed on your system.
2. Save the EFT file you want to process in the same directory as the Python script.
3. Place a `"example.eft"` in the same directory as eft.py
4. Run the Python script (eft.py)
5. The script will automatically check if the PIL (Pillow) package is installed. If not found, it will be downloaded and installed.
6. The EFT file will be parsed, and the RGBA image data will be extracted.
7. An RGBA image with the extracted data will be created using the Pillow library.
8. The image will be saved as a TGA file named "output.tga" in the same directory as the Python script.

Ensure that the PIL (Pillow) package is successfully installed and imported in the script. If you encounter any issues, please refer to the installation steps in the Requirements section or consult the PIL/Pillow documentation for further assistance.

## Acknowledgements

- Original C implementation: [@FuzzyQuills](https://github.com/FuzzyQuills/libeft)
- Python implementation: @annabelsandford

## License

This project is licensed under the MIT License.
