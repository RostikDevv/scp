from utils.reader import Reader
import argparse
import os


def info(text):
	print(f"[INFO] {text}")


class ScPacks(Reader):
	def __init__(self, filename):
		super().__init__(open(filename, "rb").read(), 'little')
		self.filename = filename

	def parse_info(self):
		for x in range(self.files_count):
			self.read_int16()  # length hash maybe
			self.read_int16()
			
			file_size = self.read_int64()
			file_offset = self.read_int64()
			self.read_int64()  # file_size
			
			file_hash = self.read(32)
			filename = self.read_string_little()
			
			current_offset = self.i
			
			self.setOffset(file_offset)
			file_data = self.read(file_size)
			self.setOffset(current_offset)
			
			open(f"{self.filename.split('.scp')[0]}/{filename}", "wb").write(file_data)
			
			info(f"Save as... Filename: {filename}, hash file: {file_hash.hex()}, size file: {file_size}")

	def parse(self):
		sectionName = self.read(3)
		self.read(1)

		version = self.read_int32()
		self.read_int32()
		self.files_count = self.read_int32()
		info_offset = self.read_int32()

		self.read(52)
		self.read(32) # md5 hash ???
		self.read(1) # unk

		self.setOffset(info_offset)

		self.parse_info()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-f', "--file", help='.scp convert to files', nargs='+')
	args = parser.parse_args()
	if args.file:
		filename = args.file[0]
		if os.path.isfile(filename):
			try: os.mkdir(filename.split(".scp")[0])
			except: pass
			decoder = ScPacks(filename)
			decoder.parse()
		else:
			print("File not found.")
	else:
		print("The -f element is required.")

#ScPacks("tutorial.scp")
