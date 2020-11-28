class Reader:
	def __init__(self, buffer: bytes, endian: str = 'little'):
		self.buffer = buffer
		self.endian = endian
		self.bit_shift = 0
		self.i = 0


	def setOffset(self, offset):
		self.i = offset

	def read(self, length: int = 1) -> bytes:
		self.ensure_capacity()
		result = self.buffer[self.i:self.i + length]
		self.i += length

		return result

	def read_string_little(self) -> str:
		bufferString = b""
		while True:
			readByte = self.read()
			if readByte != b"\x00":
				bufferString += readByte
			else:
				break
		return bufferString.decode()

	def read_vint(self, is_rotated: bool = True) -> int:
		shift = 0
		result = 0
		while True:
			byte = self.readByte()
			if is_rotated and shift == 0:
				seventh = (byte & 0x40) >> 6  # save 7th bit
				msb = (byte & 0x80) >> 7  # save msb
				n = byte << 1  # rotate to the left
				n = n & ~0x181  # clear 8th and 1st bit and 9th if any
				byte = n | (msb << 7) | seventh  # insert msb and 6th back in
			result |= (byte & 0x7f) << shift
			shift += 7
			if not (byte & 0x80):
				break
		return (result >> 1) ^ (-(result & 1))

	def read_unsigned_integer(self, length: int = 1) -> int:
		self.ensure_capacity()

		result = 0
		for x in range(length):
			byte = self.buffer[self.i]

			bit_padding = x * 8
			if self.endian == 'big':
				bit_padding = (8 * (length - 1)) - bit_padding

			result |= byte << bit_padding
			self.i += 1

		return result

	def read_integer(self, length: int = 1) -> int:
		integer = self.read_unsigned_integer(length)
		result = integer
		if integer > 2**(length * 8) / 2:
			result -= 2**(length * 8)
		return result

	def read_unsigned_int64(self) -> int:
		return self.read_unsigned_integer(8)

	def read_int64(self) -> int:
		return self.read_integer(8)

	def read_float(self) -> float:
		as_int = self.read_unsigned_int32()
		binary = bin(as_int)
		binary = binary[2:].zfill(32)

		sign = -1 if binary[0] == '1' else 1
		exponent = int(binary[1:9], 2) - 127
		mantissa_base = binary[9:]
		mantissa_bin = '1' + mantissa_base
		mantissa = 0
		val = 1

		if exponent == -127:
			if mantissa_base[1] == -1:
				return 0
			else:
				exponent = -126
				mantissa_bin = '0' + mantissa_base

		for char in mantissa_bin:
			mantissa += val * int(char)
			val = val / 2

		result = sign * 2 ** exponent * mantissa
		return result

	def read_unsigned_int32(self) -> int:
		return self.read_unsigned_integer(4)

	def read_int32(self) -> int:
		return self.read_integer(4)

	def read_normalized_unsigned_int16(self) -> float:
		return self.read_unsigned_int16() / 65535

	def read_unsigned_int16(self) -> int:
		return self.read_unsigned_integer(2)

	def read_normalized_int16(self) -> float:
		return self.read_int16() / 32512

	def read_int16(self) -> int:
		return self.read_integer(2)

	def read_unsigned_int8(self) -> int:
		return self.read_unsigned_integer()

	def read_int8(self) -> int:
		return self.read_integer()

	def read_bool(self) -> bool:
		current_byte = self.buffer[self.i]
		boolean = current_byte & 2**self.bit_shift

		self.bit_shift += 1 & 7
		if self.bit_shift == 0:
			self.i += 1
		if boolean == 1:
			return True
		return False

	readUInt = read_unsigned_integer
	readInt = read_integer

	readUInt64 = readULongLong = read_unsigned_int64
	readInt64 = readLongLong = read_int64

	readUInt32 = readULong = read_unsigned_int32
	readInt32 = readLong = read_int32

	readNUInt16 = readNUShort = read_normalized_unsigned_int16
	readNInt16 = readNShort = read_normalized_int16

	readUInt16 = readUShort = read_unsigned_int16
	readInt16 = readShort = read_int16

	readUInt8 = readUByte = read_unsigned_int8
	readInt8 = readByte = read_int8

	readBool = readBoolean = read_boolean = read_bool
	readVint = read_Vint = read_vint 

	def read_char(self, length: int = 1) -> str:
		return self.read(length).decode('utf-8')

	def read_string(self) -> str:
		length = self.read_int32()
		if length == -1:
			return ''
		else:
			return self.read_char(length)

	def read_string_len2(self) -> str:
		length = self.read_integer(2)
		if length == -1:
			return ''
		else:
			return self.read_char(length)

	def readScID(self):
		tempArray = []

		idSc = self.read_vint()
		tempArray.append(idSc)
		if idSc != 0:
			tempArray.append(self.read_vint())
		return tempArray


	def read_stringReference(self) -> str:
		length = self.read_integer(3)
		if length == -1:
			return ''
		else:
			return self.read_char(length)

	readChar = read_char
	readString = read_string

	def tell(self) -> int:
		return self.i

	def ensure_capacity(self):
		if self.bit_shift > 0:
			self.bit_shift = 0
			self.i += 1
