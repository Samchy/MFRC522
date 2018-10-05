# Code by Simon Monk https://github.com/simonmonk/
# modify by Sam Chen https://

import MFRC522
import RPi.GPIO as GPIO
import argparse
from time import *


class SimpleMFRC522:
	READER = None;

	KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

	def __init__(self):
		self.READER = MFRC522.MFRC522()

	def read(self):
		id, text = self.read_no_block()
		while not id:
			id, text = self.read_no_block()
		return id, text

	def read_id(self):
		id, text = self.read_no_block()
		while not id:
			id, text = self.read_no_block()
		return id

	def read_id_no_block(self):
		id, text = self.read_no_block()
		return id

	def read_no_block(self, sector, addres_range):
		(status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
		if status != self.READER.MI_OK:
			print 'MFRC522_Request not ready'
			return None, None
		(status, uid) = self.READER.MFRC522_Anticoll()
		if status != self.READER.MI_OK:
			print 'MFRC522_Anticoll not ready'
			return None, None
		id = self.uid_to_num(uid)
		self.READER.MFRC522_SelectTag(uid)
		status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, sector, self.KEY, uid)
		data = []
		text_read = ''
		if status == self.READER.MI_OK:
			for block_num in addres_range:
				block = self.READER.MFRC522_Read(block_num)
				if (block_num + 1) % 4 == 0:
					block = self.KEY + block[len(self.KEY):]
				tmp = ''.join('%02x, ' % i for i in block)
				print '%02d:' % block_num, tmp
				if block:
					data += block
			if data:
				text_read = ''.join(chr(i) for i in data)
		self.READER.MFRC522_StopCrypto1()
		return id, text_read

	def write(self, text):
		id, text_in = self.write_no_block(text)
		while not id:
			id, text_in = self.write_no_block(text)
		return id, text_in

	def write_no_block(self, data, sector, addres_range):
		(status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
		if status != self.READER.MI_OK:
			return None, None
		(status, uid) = self.READER.MFRC522_Anticoll()
		if status != self.READER.MI_OK:
			return None, None
		id = self.uid_to_num(uid)
		self.READER.MFRC522_SelectTag(uid)
		status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, sector, self.KEY, uid)
		self.READER.MFRC522_Read(sector)
		if status == self.READER.MI_OK:
			i = 0
			for block_num in addres_range:
				w_list = []
				for tmp in data[(i * 16):(i + 1) * 16]:
					w_list.append(ord(tmp))
				print '%02d' % block_num, (''.join('%02x,' % ord(tmp) for tmp in data[(i * 16):(i + 1) * 16]))
				#print '%02d' % block_num, (w_list.append(ord(tmp)) for tmp in data[(i * 16):(i + 1) * 16])
				self.READER.MFRC522_Write(block_num, w_list)
				#print '%02d' % block_num, w_list
				i += 1
		self.READER.MFRC522_StopCrypto1()

	def uid_to_num(self, uid):
		n = 0
		for i in range(0, 5):
			n = n * 256 + uid[i]
		return n

	def read_dump(self, file, card_type):
		id = ''
		data = ''
		for i in range(16):
			self.READER = MFRC522.MFRC522()
			id, tmp_data = self.read_no_block((i + 1) * 4 - 1, range(i * 4, (i + 1) * 4))
			# print i, id, tmp_data
			data += tmp_data
			GPIO.cleanup()
		# sleep(1)
		print id
		if file != '':
			with open(file, 'wb') as f:
				f.write(data)

	def write_dump(self, file, card_type):
		with open(file, 'rb') as f:
			data = f.read()
		for i in range(1 if card_type == 0 else 0, 16):
			self.READER = MFRC522.MFRC522()
			self.write_no_block(data[i * 4 * 16:(i + 1) * 4 * 16], (i + 1) * 4 - 1, range(i * 4, i * 4 + 3))
			GPIO.cleanup()


# read 8,9,10, then check 11 sector key
# python sam_MFRC522.py r
# python sam_MFRC522.py r -f r.dump
# python sam_MFRC522.py w -t 0 -f r.dump
# python sam_MFRC522.py w -t 1 -f r.dump
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', action='store', help='select input/output file', type=str)
	parser.add_argument('-t', action='store', help='card type. 0:M1 card, 1:UID card', type=int, default=0)
	parser.add_argument('op', action='store', help='action: r:read, w:write', type=str, default=0)
	args = parser.parse_args()

	file = ""
	card_type = 0
	op = 'r'

	if args.f:
		file = args.f

	if args.t:
		card_type = args.t

	if args.op:
		op = args.op

	mfrc = SimpleMFRC522()
	if op == 'w':
		mfrc.write_dump(file, card_type)
	elif op == 'r':
		mfrc.read_dump(file, card_type)
	else:
		print args.help
