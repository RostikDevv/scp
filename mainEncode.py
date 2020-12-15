from utils.writer import Writer
import argparse
import os
import hashlib

def info(text):
	print(f"[INFO] {text}")

class ScPacksEncode(Writer):
	def __init__(self, files):
		super().__init__()
		self.files = files
		self.filesOut = {}
		self.write_info()

	def write_files(self):
		for file in self.files:
			self.write(open(file, "rb").read())

			self.filesOut[file] = len(self.buffer)

			info(f"File add! size: {len(open(file, 'rb').read())}, name: {file}")

	def write_info(self):
		self.write(b"SCP!")

		self.write_int32(1) # version
		self.write_int32(16)

		self.write_int32(len(self.files))

		lenBlockInfo = 0
		offSetAll = len(self.buffer) + 56 + 32 + 1

		for file in self.files:
			lenBlockInfo += 60 + len(file.encode()) + 1
			offSetAll += len(open(file, "rb").read())

		offSetAll_ = offSetAll + lenBlockInfo

		self.write_int64(offSetAll) # offset_info

		offsetInfo = self.write_int64(offSetAll_ - offSetAll) # offset info the end
		offsetInfo_ = self.write_int64(offSetAll_ - offSetAll) # offset info the end

		self.write_int64(0)
		self.write_int64(0)
		self.write_int64(0)
		self.write_int64(0)

		self.write(b'\x01' * 32) # md5 hash

		self.writeByte(0)

		self.write_files()

		infoOffsetInt = len(self.buffer)

		info(f"Header create! offset_info: {len(self.buffer)}")

		for file in self.files:
			self.write_int16(16) # length hash maybe
			self.write_int16(0)

			file_data = open(file, "rb").read()

			self.write_int64(len(file_data)) # file_size
			self.write_int64(self.filesOut[file]) # offset_file
			self.write_int64(len(file_data)) # file_size

			m = hashlib.sha256()
			m.update(file_data)
			self.write(m.digest()) # data_hash

			self.write(file.encode() + b'\x00')
			info(f"File Info add! finame: {file}, hash: {m.digest().hex()}, size: {len(file_data)}, offset: {self.filesOut[file]}")

		m = hashlib.sha256()
		m.update(self.buffer[infoOffsetInt:len(self.buffer)])

		self.buffer = self.buffer.replace(b'\x01' * 32, m.digest()) # info_block hash

		open("encodeScp.scp", "wb").write(self.buffer)

		info(f"Save as... filename: encodeScp.scp, size: {len(self.buffer)}")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-f', "--files", help='.scp convert to files', nargs='+')
	args = parser.parse_args()
	array_files = []
	if args.files:
		for filename in args.files:
			if os.path.isfile(filename):
				array_files.append(filename)
			else:
				print(f"File {filename} not found.")
		ScPacksEncode(array_files)
	else:
		print("The -f element is required.")
