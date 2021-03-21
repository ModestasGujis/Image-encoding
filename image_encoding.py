#!/usr/local/bin/python3
from PIL import Image
import sys, getopt

USAGE = 'USAGE:\n./image_encoding.py -d <image_file> # for decoding\n./image_encoding.py -e <text_file> <image_file> # for encoding'
ENCODING_BIT_COUNT = 2 # number of the least significant bits that will be used to encode the message
BIT_COUNT = 8 # number of bits in a pixel
ENCODING = 'utf-8'

def string2bits(s):
	bits = list(s.encode(ENCODING))
	ret = ''.join([bin(x)[2:].zfill(BIT_COUNT) for x in bits])

	return ret

def bits2string(binary_string):
	bits = [int(binary_string[i - BIT_COUNT:i], 2) for i in range(BIT_COUNT, len(binary_string), BIT_COUNT)]
		
	bits = bits[:bits.index((1 << BIT_COUNT) - 1)]
	return bytes(bits).decode(ENCODING)

def encode8(pixel, binary_string):
	# remove the least significant encoding bits
	pixel = pixel >> ENCODING_BIT_COUNT
	pixel = pixel << ENCODING_BIT_COUNT

	return pixel | int(binary_string[:ENCODING_BIT_COUNT], 2)

def decode8(pixel):
	b = ENCODING_BIT_COUNT
	return (bin(pixel)[2:])[-b:].zfill(b)

def encode3x8(pixel, binary_string):
	pixel_list = list(pixel)

	e = ENCODING_BIT_COUNT
	for i in range(3):
		if len(binary_string) >= ENCODING_BIT_COUNT:
			pixel_list[i] = encode8(pixel_list[i], binary_string)
			binary_string = binary_string[ENCODING_BIT_COUNT:]

	return tuple(pixel_list)

def decode3x8(pixel):
	pixel_list = list(pixel)
	b = ENCODING_BIT_COUNT

	return ''.join([str((bin(px)[2:])[-b:].zfill(b)) for px in pixel_list])

def decode(image_file):
	im = Image.open(image_file)

	(w, h) = im.size

	decodePixel = 'temp'

	if im.mode == 'L':
		decodePixel = decode8
	elif im.mode == 'RGB':
		decodePixel = decode3x8
	else:
		print('only L and RGB modes are supported (for now) ;(')
		sys.exit()

	px = im.load()
	binary_string = ''
	for i in range(w):
		for j in range(h):
			binary_string += decodePixel(px[i,j])

	text = bits2string(binary_string)
	print(text)

def encode(text_file, image_file):
	file = open(text_file, mode='r')
	all_text = file.read()
	file.close()
	binary_string = string2bits(all_text)
	binary_string += '1' * BIT_COUNT # add one invalid byte for termination

	im = Image.open(image_file)
	(w, h) = im.size

	encoded_bits_per_pixel = 0
	encodePixel = 3

	if im.mode == 'L':
		encodePixel = encode8
		encoded_bits_per_pixel = ENCODING_BIT_COUNT
	elif im.mode == 'RGB':
		encodePixel = encode3x8
		encoded_bits_per_pixel = 3 * ENCODING_BIT_COUNT
	else:
		im = im.convert('RGB')
		encodePixel = encode3x8
		encoded_bits_per_pixel = 3 * ENCODING_BIT_COUNT


	have_bits = w*h*encoded_bits_per_pixel
	need_bits = len(binary_string)

	# for easier implementation we pad the binary string
	need_bits = ((need_bits + ENCODING_BIT_COUNT - 1)//ENCODING_BIT_COUNT)*ENCODING_BIT_COUNT
	binary_string += '0'*(need_bits - len(binary_string))

	if have_bits < need_bits:
		print('not enough space on the image ;(')
		sys.exit()

	px = im.load()

	for i in range(w):
		for j in range(h):
			if len(binary_string) <= 0:
				break
			px[i,j] = encodePixel(px[i,j], binary_string)
			binary_string = binary_string[encoded_bits_per_pixel:]

	# save as png to preserve pixels and avoid compression
	new_file_name = 'encoded_' + image_file.rsplit(".", 1)[0] + '.png'

	print(new_file_name, 'has been generated')
	im.save(new_file_name)

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hde", ["--help"])
	except getopt.GetoptError:
		print (USAGE)
		sys.exit(2)

	if len(args) == 0:
		print(USAGE)
		sys.exit()

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