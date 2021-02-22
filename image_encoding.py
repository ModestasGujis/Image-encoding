#!/usr/bin/python3
from PIL import Image
import sys
import binascii

import sys, getopt
USAGE = 'USAGE:\n./image_encoding.py -d <image_file> # for decoding\n./image_encoding.py -e <text_file> <image_file> # for encoding'
ENCODING_BIT_COUNT = 2 # number of the least significant bits that will be used to encode the message
BIT_COUNT = 8 # number of bits in a pixel

def string2bits(s=''):
	return ''.join([bin(ord(x))[2:].zfill(8) for x in s])

def encode8bit(pixel, binary_string): # encode 8bit integer pixels
	# remove the least significant encoding bits
	pixel = pixel >> ENCODING_BIT_COUNT
	pixel = pixel << ENCODING_BIT_COUNT

	return pixel | int(binary_string[:ENCODING_BIT_COUNT], 2)

def decode(image_file):
	im = Image.open(image_file)

	(w, h) = im.size

	if im.mode != "L":
		print('only mode L is supported (for now) ;(')
		sys.exit()

	px = im.load()
	binary_string = ''
	for i in range(w):
		for j in range(h):
			b = ENCODING_BIT_COUNT
			binary_string += (bin(px[i,j])[2:])[-b:].zfill(b)

	text = ''
	for i in range(0, len(binary_string), BIT_COUNT):
		text += chr(int(binary_string[i:i + BIT_COUNT], 2))

	print(text)

def encode(text_file, image_file):
	file = open(text_file, mode='r')
	all_text = file.read()
	file.close()
	binary_string = string2bits(all_text)

	im = Image.open(image_file)
	(w, h) = im.size

	have_bits = w*h*ENCODING_BIT_COUNT
	need_bits = len(binary_string)

	# for easier implementation we pad the binary string
	need_bits = ((need_bits + ENCODING_BIT_COUNT - 1)//ENCODING_BIT_COUNT)*ENCODING_BIT_COUNT
	binary_string += '0'*(need_bits - len(binary_string))

	if have_bits < need_bits:
		print('not enough space on the image ;(')
		sys.exit()

	# TODO implement other mode encodings
	if im.mode != "L":
		im = im.convert("L")

	px = im.load()

	for i in range(w):
		for j in range(h):
			if len(binary_string) <= 0:
				break
			px[i,j] = encode8bit(px[i,j], binary_string)
			binary_string = binary_string[ENCODING_BIT_COUNT:]

	im.save('encoded_' + image_file)

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hde", ["--help"])
	except getopt.GetoptError:
		print (USAGE)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print (USAGE)
			sys.exit()
		elif opt == "-d":
			if len(args) < 1:
				print (USAGE)
				sys.exit(2)
			decode(args[0])
		elif opt == "-e":
			if len(args) < 2:
				print (USAGE)
				sys.exit(2)
			encode(args[0], args[1])


if __name__ == "__main__":
   main(sys.argv[1:])