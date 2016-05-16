# vim: noet shiftwidth=4 tabstop=4

# Copyright (c) 2016 Alexander Böhm <alxndr.boehm@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random, serial
from time import sleep

class BusPirate:
	def __init__(self, device, baud, timeout=0.1):
		self.device = device
		self.baud = baud
		self.serial = serial.Serial(self.device, self.baud)
		self.timeout = timeout
		self.debugMode = False

	def debug(self, msg):
		if self.debugMode:
			print(msg)

	def setDebugMode(self, enable=True):
		self.debugMode = enable

	def command(self, command):
		self.debug('bus pirate: %s' % (command))
		self.serial.write(b'%s\r' % (command))
		sleep(self.timeout)

	def init(self):
		pass

	def setProtocol(self, protocol):
		self.command(b'm')
		self.command(b'%i' % (protocol));

	def enablePowerSupply(self):
		self.command(b'W')

	def enablePullupResistors(self):
		self.command(b'P')

class BusPirateI2C(BusPirate):
	def __init__(self, device, baud, i2c_addr, i2c_freq=1, i2c_timeout=0.01):
		BusPirate.__init__(self, device=device, baud=baud)
		self.i2c_address = i2c_addr
		self.i2c_frequency = i2c_freq
		self.i2c_timeout = i2c_timeout

	def init(self):
		self.setProtocol(4)
		self.command(b'%i' % (self.i2c_frequency))
		self.enablePowerSupply()
		self.enablePullupResistors()

	def i2c_write(self, data, timeout=None):
		d = b'[ 0x%2.2X ' % (self.i2c_address)
		for i in data:
			if type(i) == int:
				d += b'0x%2.2X ' % (i)
			else:
				d += bytes(i, 'utf-8')
		d += b']'

		self.debug('i2c write: %s' % (d))
		self.serial.write(d+b'\r')
		if timeout == None:
			sleep(self.timeout)
		else:
			sleep(timeout)


class BusPirateSSD1306(BusPirateI2C):
	# Documentation of SSD1306 https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf#page=37&zoom=auto,0,842
		
	MEM_ADDR_MODE_PAGE = 0x10
	MEM_ADDR_MODE_HORZ = 0x00
	MEM_ADDR_MODE_VERT = 0x01

	# Font by Benedikt K. (2006) http://www.mikrocontroller.net/topic/54860#423255
	ASCII_TABLE_VERTICAL = [
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x00
		[0x7E,0x81,0xA5,0x81,0xBD,0x99,0x81,0x7E],	# 0x01
		[0x7E,0xFF,0xDB,0xFF,0xC3,0xE7,0xFF,0x7E],	# 0x02
		[0x36,0x7F,0x7F,0x7F,0x3E,0x1C,0x08,0x00],	# 0x03
		[0x08,0x1C,0x3E,0x7F,0x3E,0x1C,0x08,0x00],	# 0x04
		[0x1C,0x3E,0x1C,0x7F,0x7F,0x6B,0x08,0x1C],	# 0x05
		[0x08,0x08,0x1C,0x3E,0x7F,0x3E,0x08,0x1C],	# 0x06
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x07
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x08
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x09
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x0A
		[0xF0,0xE0,0xF0,0xBE,0x33,0x33,0x33,0x1E],	# 0x0B
		[0x3C,0x66,0x66,0x66,0x3C,0x18,0x7E,0x18],	# 0x0C
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x0D
		[0xFE,0xC6,0xFE,0xC6,0xC6,0xE6,0x67,0x03],	# 0x0E
		[0x99,0x5A,0x3C,0xE7,0xE7,0x3C,0x5A,0x99],	# 0x0F
		[0x01,0x07,0x1F,0x7F,0x1F,0x07,0x01,0x00],	# 0x10
		[0x40,0x70,0x7C,0x7F,0x7C,0x70,0x40,0x00],	# 0x11
		[0x18,0x3C,0x7E,0x18,0x18,0x7E,0x3C,0x18],	# 0x12
		[0x66,0x66,0x66,0x66,0x66,0x00,0x66,0x00],	# 0x13
		[0xFE,0xDB,0xDB,0xDE,0xD8,0xD8,0xD8,0x00],	# 0x14
		[0x7E,0xC3,0x1E,0x33,0x33,0x1E,0x31,0x1F],	# 0x15
		[0x00,0x00,0x00,0x00,0x7E,0x7E,0x7E,0x00],	# 0x16
		[0x18,0x3C,0x7E,0x18,0x7E,0x3C,0x18,0xFF],	# 0x17
		[0x18,0x3C,0x7E,0x18,0x18,0x18,0x18,0x00],	# 0x18
		[0x18,0x18,0x18,0x18,0x7E,0x3C,0x18,0x00],	# 0x19
		[0x00,0x18,0x30,0x7F,0x30,0x18,0x00,0x00],	# 0x1A
		[0x00,0x0C,0x06,0x7F,0x06,0x0C,0x00,0x00],	# 0x1B
		[0x00,0x00,0x03,0x03,0x03,0x7F,0x00,0x00],	# 0x1C
		[0x00,0x24,0x66,0xFF,0x66,0x24,0x00,0x00],	# 0x1D
		[0x00,0x18,0x3C,0x7E,0xFF,0xFF,0x00,0x00],	# 0x1E
		[0x00,0xFF,0xFF,0x7E,0x3C,0x18,0x00,0x00],	# 0x1F
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x20
		[0x0C,0x1E,0x1E,0x0C,0x0C,0x00,0x0C,0x00],	# 0x21
		[0x36,0x36,0x36,0x00,0x00,0x00,0x00,0x00],	# 0x22
		[0x36,0x36,0x7F,0x36,0x7F,0x36,0x36,0x00],	# 0x23
		[0x0C,0x3E,0x03,0x1E,0x30,0x1F,0x0C,0x00],	# 0x24
		[0x00,0x63,0x33,0x18,0x0C,0x66,0x63,0x00],	# 0x25
		[0x1C,0x36,0x1C,0x6E,0x3B,0x33,0x6E,0x00],	# 0x26
		[0x06,0x06,0x03,0x00,0x00,0x00,0x00,0x00],	# 0x27
		[0x18,0x0C,0x06,0x06,0x06,0x0C,0x18,0x00],	# 0x28
		[0x06,0x0C,0x18,0x18,0x18,0x0C,0x06,0x00],	# 0x29
		[0x00,0x66,0x3C,0xFF,0x3C,0x66,0x00,0x00],	# 0x2A
		[0x00,0x0C,0x0C,0x3F,0x0C,0x0C,0x00,0x00],	# 0x2B
		[0x00,0x00,0x00,0x00,0x00,0x0E,0x0C,0x06],	# 0x2C
		[0x00,0x00,0x00,0x3F,0x00,0x00,0x00,0x00],	# 0x2D
		[0x00,0x00,0x00,0x00,0x00,0x0C,0x0C,0x00],	# 0x2E
		[0x60,0x30,0x18,0x0C,0x06,0x03,0x01,0x00],	# 0x2F
		[0x1E,0x33,0x3B,0x3F,0x37,0x33,0x1E,0x00],	# 0x30
		[0x0C,0x0F,0x0C,0x0C,0x0C,0x0C,0x3F,0x00],	# 0x31
		[0x1E,0x33,0x30,0x1C,0x06,0x33,0x3F,0x00],	# 0x32
		[0x1E,0x33,0x30,0x1C,0x30,0x33,0x1E,0x00],	# 0x33
		[0x38,0x3C,0x36,0x33,0x7F,0x30,0x30,0x00],	# 0x34
		[0x3F,0x03,0x1F,0x30,0x30,0x33,0x1E,0x00],	# 0x35
		[0x1C,0x06,0x03,0x1F,0x33,0x33,0x1E,0x00],	# 0x36
		[0x3F,0x33,0x30,0x18,0x0C,0x06,0x06,0x00],	# 0x37
		[0x1E,0x33,0x33,0x1E,0x33,0x33,0x1E,0x00],	# 0x38
		[0x1E,0x33,0x33,0x3E,0x30,0x18,0x0E,0x00],	# 0x39
		[0x00,0x00,0x0C,0x0C,0x00,0x0C,0x0C,0x00],	# 0x3A
		[0x00,0x00,0x0C,0x0C,0x00,0x0E,0x0C,0x06],	# 0x3B
		[0x18,0x0C,0x06,0x03,0x06,0x0C,0x18,0x00],	# 0x3C
		[0x00,0x00,0x3F,0x00,0x3F,0x00,0x00,0x00],	# 0x3D
		[0x06,0x0C,0x18,0x30,0x18,0x0C,0x06,0x00],	# 0x3E
		[0x1E,0x33,0x30,0x18,0x0C,0x00,0x0C,0x00],	# 0x3F
		[0x3E,0x63,0x7B,0x7B,0x7B,0x03,0x1E,0x00],	# 0x40
		[0x0C,0x1E,0x33,0x33,0x3F,0x33,0x33,0x00],	# 0x41
		[0x3F,0x66,0x66,0x3E,0x66,0x66,0x3F,0x00],	# 0x42
		[0x3C,0x66,0x03,0x03,0x03,0x66,0x3C,0x00],	# 0x43
		[0x3F,0x36,0x66,0x66,0x66,0x36,0x3F,0x00],	# 0x44
		[0x7F,0x46,0x16,0x1E,0x16,0x46,0x7F,0x00],	# 0x45
		[0x7F,0x46,0x16,0x1E,0x16,0x06,0x0F,0x00],	# 0x46
		[0x3C,0x66,0x03,0x03,0x73,0x66,0x7C,0x00],	# 0x47
		[0x33,0x33,0x33,0x3F,0x33,0x33,0x33,0x00],	# 0x48
		[0x1E,0x0C,0x0C,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x49
		[0x78,0x30,0x30,0x30,0x33,0x33,0x1E,0x00],	# 0x4A
		[0x67,0x66,0x36,0x1E,0x36,0x66,0x67,0x00],	# 0x4B
		[0x0F,0x06,0x06,0x06,0x46,0x66,0x7F,0x00],	# 0x4C
		[0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],	# 0x4D
		[0x63,0x67,0x6F,0x7B,0x73,0x63,0x63,0x00],	# 0x4E
		[0x1C,0x36,0x63,0x63,0x63,0x36,0x1C,0x00],	# 0x4F
		[0x3F,0x66,0x66,0x3E,0x06,0x06,0x0F,0x00],	# 0x50
		[0x1E,0x33,0x33,0x33,0x3B,0x1E,0x38,0x00],	# 0x51
		[0x3F,0x66,0x66,0x3E,0x1E,0x36,0x67,0x00],	# 0x52
		[0x1E,0x33,0x07,0x1C,0x38,0x33,0x1E,0x00],	# 0x53
		[0x3F,0x2D,0x0C,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x54
		[0x33,0x33,0x33,0x33,0x33,0x33,0x3F,0x00],	# 0x55
		[0x33,0x33,0x33,0x33,0x33,0x1E,0x0C,0x00],	# 0x56
		[0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],	# 0x57
		[0x63,0x63,0x36,0x1C,0x36,0x63,0x63,0x00],	# 0x58
		[0x33,0x33,0x33,0x1E,0x0C,0x0C,0x1E,0x00],	# 0x59
		[0x7F,0x33,0x19,0x0C,0x46,0x63,0x7F,0x00],	# 0x5A
		[0x1E,0x06,0x06,0x06,0x06,0x06,0x1E,0x00],	# 0x5B
		[0x03,0x06,0x0C,0x18,0x30,0x60,0x40,0x00],	# 0x5C
		[0x1E,0x18,0x18,0x18,0x18,0x18,0x1E,0x00],	# 0x5D
		[0x08,0x1C,0x36,0x63,0x00,0x00,0x00,0x00],	# 0x5E
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF],	# 0x5F
		[0x0C,0x0C,0x18,0x00,0x00,0x00,0x00,0x00],	# 0x60
		[0x00,0x00,0x1E,0x30,0x3E,0x33,0x6E,0x00],	# 0x61
		[0x07,0x06,0x3E,0x66,0x66,0x66,0x3D,0x00],	# 0x62
		[0x00,0x00,0x1E,0x33,0x03,0x33,0x1E,0x00],	# 0x63
		[0x38,0x30,0x30,0x3E,0x33,0x33,0x6E,0x00],	# 0x64
		[0x00,0x00,0x1E,0x33,0x3F,0x03,0x1E,0x00],	# 0x65
		[0x1C,0x36,0x06,0x0F,0x06,0x06,0x0F,0x00],	# 0x66
		[0x00,0x00,0x6E,0x33,0x33,0x3E,0x30,0x1F],	# 0x67
		[0x07,0x06,0x36,0x6E,0x66,0x66,0x67,0x00],	# 0x68
		[0x0C,0x00,0x0E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x69
		[0x18,0x00,0x1E,0x18,0x18,0x18,0x1B,0x0E],	# 0x6A
		[0x07,0x06,0x66,0x36,0x1E,0x36,0x67,0x00],	# 0x6B
		[0x0E,0x0C,0x0C,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x6C
		[0x00,0x00,0x37,0x7F,0x6B,0x63,0x63,0x00],	# 0x6D
		[0x00,0x00,0x1F,0x33,0x33,0x33,0x33,0x00],	# 0x6E
		[0x00,0x00,0x1E,0x33,0x33,0x33,0x1E,0x00],	# 0x6F
		[0x00,0x00,0x3B,0x66,0x66,0x3E,0x06,0x0F],	# 0x70
		[0x00,0x00,0x6E,0x33,0x33,0x3E,0x30,0x78],	# 0x71
		[0x00,0x00,0x1B,0x36,0x36,0x06,0x0F,0x00],	# 0x72
		[0x00,0x00,0x3E,0x03,0x1E,0x30,0x1F,0x00],	# 0x73
		[0x08,0x0C,0x3E,0x0C,0x0C,0x2C,0x18,0x00],	# 0x74
		[0x00,0x00,0x33,0x33,0x33,0x33,0x6E,0x00],	# 0x75
		[0x00,0x00,0x33,0x33,0x33,0x1E,0x0C,0x00],	# 0x76
		[0x00,0x00,0x63,0x63,0x6B,0x7F,0x36,0x00],	# 0x77
		[0x00,0x00,0x63,0x36,0x1C,0x36,0x63,0x00],	# 0x78
		[0x00,0x00,0x33,0x33,0x33,0x3E,0x30,0x1F],	# 0x79
		[0x00,0x00,0x3F,0x19,0x0C,0x26,0x3F,0x00],	# 0x7A
		[0x38,0x0C,0x0C,0x07,0x0C,0x0C,0x38,0x00],	# 0x7B
		[0x18,0x18,0x18,0x00,0x18,0x18,0x18,0x00],	# 0x7C
		[0x07,0x0C,0x0C,0x38,0x0C,0x0C,0x07,0x00],	# 0x7D
		[0x6E,0x3B,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x7E
		[0x08,0x1C,0x36,0x63,0x63,0x63,0x7F,0x00],	# 0x7F
		[0x1E,0x33,0x03,0x03,0x33,0x1E,0x0C,0x06],	# 0x80
		[0x00,0x33,0x00,0x33,0x33,0x33,0x7E,0x00],	# 0x81
		[0x18,0x0C,0x1E,0x33,0x3F,0x03,0x1E,0x00],	# 0x82
		[0x7E,0xC3,0x3C,0x60,0x7C,0x66,0xFC,0x00],	# 0x83
		[0x33,0x00,0x1E,0x30,0x3E,0x33,0x7E,0x00],	# 0x84
		[0x06,0x0C,0x1E,0x30,0x3E,0x33,0x7E,0x00],	# 0x85
		[0x3C,0x66,0x3C,0x60,0x7C,0x66,0xFC,0x00],	# 0x86
		[0x00,0x1E,0x33,0x03,0x33,0x1E,0x0C,0x06],	# 0x87
		[0x7E,0xC3,0x3C,0x66,0x7E,0x06,0x3C,0x00],	# 0x88
		[0x33,0x00,0x1E,0x33,0x3F,0x03,0x1E,0x00],	# 0x89
		[0x06,0x0C,0x1E,0x33,0x3F,0x03,0x1E,0x00],	# 0x8A
		[0x33,0x00,0x0E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x8B
		[0x3E,0x63,0x1C,0x18,0x18,0x18,0x3C,0x00],	# 0x8C
		[0x06,0x0C,0x0E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0x8D
		[0x33,0x0C,0x1E,0x33,0x33,0x3F,0x33,0x00],	# 0x8E
		[0x0C,0x12,0x0C,0x1E,0x33,0x3F,0x33,0x00],	# 0x8F
		[0x18,0x0C,0x3F,0x06,0x1E,0x06,0x3F,0x00],	# 0x90
		[0x00,0x00,0xFE,0x30,0xFE,0x33,0xFE,0x00],	# 0x91
		[0x7C,0x36,0x33,0x7F,0x33,0x33,0x73,0x00],	# 0x92
		[0x1E,0x33,0x00,0x1E,0x33,0x33,0x1E,0x00],	# 0x93
		[0x00,0x33,0x00,0x1E,0x33,0x33,0x1E,0x00],	# 0x94
		[0x06,0x0C,0x00,0x1E,0x33,0x33,0x1E,0x00],	# 0x95
		[0x1E,0x33,0x00,0x33,0x33,0x33,0x7E,0x00],	# 0x96
		[0x06,0x0C,0x00,0x33,0x33,0x33,0x7E,0x00],	# 0x97
		[0x00,0x33,0x00,0x33,0x33,0x3F,0x30,0x1F],	# 0x98
		[0x63,0x00,0x3E,0x63,0x63,0x63,0x3E,0x00],	# 0x99
		[0x33,0x00,0x33,0x33,0x33,0x33,0x1E,0x00],	# 0x9A
		[0x00,0x00,0x3E,0x73,0x6B,0x67,0x3E,0x00],	# 0x9B
		[0x1C,0x36,0x26,0x0F,0x06,0x67,0x3F,0x00],	# 0x9C
		[0x5C,0x36,0x73,0x6B,0x67,0x36,0x1D,0x00],	# 0x9D
		[0x00,0x00,0x33,0x1E,0x0C,0x1E,0x33,0x00],	# 0x9E
		[0x70,0xD8,0x18,0x7E,0x18,0x18,0x1B,0x0E],	# 0x9F
		[0x18,0x0C,0x1E,0x30,0x3E,0x33,0x7E,0x00],	# 0xA0
		[0x18,0x0C,0x0E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0xA1
		[0x30,0x18,0x00,0x1E,0x33,0x33,0x1E,0x00],	# 0xA2
		[0x30,0x18,0x00,0x33,0x33,0x33,0x7E,0x00],	# 0xA3
		[0x6E,0x3B,0x00,0x1F,0x33,0x33,0x33,0x00],	# 0xA4
		[0x6E,0x3B,0x00,0x37,0x3F,0x3B,0x33,0x00],	# 0xA5
		[0x3C,0x36,0x36,0x7C,0x00,0x7E,0x00,0x00],	# 0xA6
		[0x3C,0x66,0x66,0x3C,0x00,0x7E,0x00,0x00],	# 0xA7
		[0x0C,0x00,0x0C,0x06,0x03,0x33,0x1E,0x00],	# 0xA8
		[0x3C,0x5A,0xA5,0x9D,0x95,0x66,0x3C,0x00],	# 0xA9
		[0x00,0x00,0x00,0x3F,0x30,0x30,0x00,0x00],	# 0xAA
		[0x67,0x36,0x1E,0x7E,0xC6,0x73,0x19,0xF8],	# 0xAB
		[0x67,0x36,0x1E,0xCE,0xE6,0xB3,0xF9,0xC0],	# 0xAC
		[0x00,0x18,0x00,0x18,0x18,0x3C,0x3C,0x18],	# 0xAD
		[0x00,0xCC,0x66,0x33,0x66,0xCC,0x00,0x00],	# 0xAE
		[0x00,0x33,0x66,0xCC,0x66,0x33,0x00,0x00],	# 0xAF
		[0x44,0x11,0x44,0x11,0x44,0x11,0x44,0x11],	# 0xB0
		[0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55],	# 0xB1
		[0xBB,0xEE,0xBB,0xEE,0xBB,0xEE,0xBB,0xEE],	# 0xB2
		[0x18,0x18,0x18,0x18,0x18,0x18,0x18,0x18],	# 0xB3
		[0x18,0x18,0x18,0x18,0x1F,0x18,0x18,0x18],	# 0xB4
		[0x30,0x18,0x0C,0x1E,0x33,0x3F,0x33,0x00],	# 0xB5
		[0x1E,0x21,0x0C,0x1E,0x33,0x3F,0x33,0x00],	# 0xB6
		[0x03,0x06,0x0C,0x1E,0x33,0x3F,0x33,0x00],	# 0xB7
		[0x3C,0x42,0x9D,0x85,0x9D,0x42,0x3C,0x00],	# 0xB8
		[0x6C,0x6C,0x6F,0x60,0x6F,0x6C,0x6C,0x6C],	# 0xB9
		[0x6C,0x6C,0x6C,0x6C,0x6C,0x6C,0x6C,0x6C],	# 0xBA
		[0x00,0x00,0x7F,0x60,0x6F,0x6C,0x6C,0x6C],	# 0xBB
		[0x6C,0x6C,0x6F,0x60,0x7F,0x00,0x00,0x00],	# 0xBC
		[0x18,0x18,0x7E,0x03,0x03,0x7E,0x18,0x18],	# 0xBD
		[0x33,0x33,0x1E,0x3F,0x0C,0x3F,0x0C,0x0C],	# 0xBE
		[0x00,0x00,0x00,0x00,0x1F,0x18,0x18,0x18],	# 0xBF
		[0x18,0x18,0x18,0x18,0xF8,0x00,0x00,0x00],	# 0xC0
		[0x18,0x18,0x18,0x18,0xFF,0x00,0x00,0x00],	# 0xC1
		[0x00,0x00,0x00,0x00,0xFF,0x18,0x18,0x18],	# 0xC2
		[0x18,0x18,0x18,0x18,0xF8,0x18,0x18,0x18],	# 0xC3
		[0x00,0x00,0x00,0x00,0xFF,0x00,0x00,0x00],	# 0xC4
		[0x18,0x18,0x18,0x18,0xFF,0x18,0x18,0x18],	# 0xC5
		[0x6E,0x3B,0x1E,0x30,0x3E,0x33,0x7E,0x00],	# 0xC6
		[0x6E,0x3B,0x0C,0x1E,0x33,0x3F,0x33,0x00],	# 0xC7
		[0x6C,0x6C,0xEC,0x0C,0xFC,0x00,0x00,0x00],	# 0xC8
		[0x00,0x00,0xFC,0x0C,0xEC,0x6C,0x6C,0x6C],	# 0xC9
		[0x6C,0x6C,0xEF,0x00,0xFF,0x00,0x00,0x00],	# 0xCA
		[0x00,0x00,0xFF,0x00,0xEF,0x6C,0x6C,0x6C],	# 0xCB
		[0x6C,0x6C,0xEC,0x0C,0xEC,0x6C,0x6C,0x6C],	# 0xCC
		[0x00,0x00,0xFF,0x00,0xFF,0x00,0x00,0x00],	# 0xCD
		[0x6C,0x6C,0xEF,0x00,0xEF,0x6C,0x6C,0x6C],	# 0xCE
		[0x00,0x41,0x7F,0x36,0x36,0x7F,0x41,0x00],	# 0xCF
		[0x1B,0x0E,0x1B,0x30,0x3C,0x36,0x1C,0x00],	# 0xD0
		[0x3F,0x36,0x66,0x6F,0x66,0x36,0x3F,0x00],	# 0xD1
		[0x1E,0x21,0x3F,0x06,0x1E,0x06,0x3F,0x00],	# 0xD2
		[0x33,0x00,0x3F,0x06,0x1E,0x06,0x3F,0x00],	# 0xD3
		[0x06,0x0C,0x3F,0x06,0x1E,0x06,0x3F,0x00],	# 0xD4
		[0x00,0x03,0x02,0x07,0x00,0x00,0x00,0x00],	# 0xD5
		[0x18,0x0C,0x1E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0xD6
		[0x1E,0x21,0x1E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0xD7
		[0x33,0x00,0x1E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0xD8
		[0x18,0x18,0x18,0x18,0x1F,0x00,0x00,0x00],	# 0xD9
		[0x00,0x00,0x00,0x00,0xF8,0x18,0x18,0x18],	# 0xDA
		[0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF],	# 0xDB
		[0x00,0x00,0x00,0x00,0xFF,0xFF,0xFF,0xFF],	# 0xDC
		[0x18,0x18,0x18,0x00,0x18,0x18,0x18,0x00],	# 0xDD
		[0x06,0x0C,0x1E,0x0C,0x0C,0x0C,0x1E,0x00],	# 0xDE
		[0xFF,0xFF,0xFF,0xFF,0x00,0x00,0x00,0x00],	# 0xDF
		[0x18,0x0C,0x3E,0x63,0x63,0x63,0x3E,0x00],	# 0xE0
		[0x00,0x1E,0x33,0x1F,0x33,0x1F,0x03,0x03],	# 0xE1
		[0x3E,0x41,0x3E,0x63,0x63,0x63,0x3E,0x00],	# 0xE2
		[0x0C,0x18,0x3E,0x63,0x63,0x63,0x3E,0x00],	# 0xE3
		[0x6E,0x3B,0x00,0x1E,0x33,0x33,0x1E,0x00],	# 0xE4
		[0x6E,0x3B,0x3E,0x63,0x63,0x63,0x3E,0x00],	# 0xE5
		[0x00,0x66,0x66,0x66,0x66,0x3E,0x06,0x03],	# 0xE6
		[0x00,0x07,0x1E,0x36,0x1E,0x06,0x0F,0x00],	# 0xE7
		[0x0F,0x06,0x3E,0x66,0x3E,0x06,0x0F,0x00],	# 0xE8
		[0x18,0x0C,0x33,0x33,0x33,0x33,0x1E,0x00],	# 0xE9
		[0x1E,0x21,0x00,0x33,0x33,0x33,0x1E,0x00],	# 0xEA
		[0x06,0x0C,0x33,0x33,0x33,0x33,0x1E,0x00],	# 0xEB
		[0x18,0x0C,0x00,0x33,0x33,0x3F,0x30,0x1F],	# 0xEC
		[0x18,0x0C,0x33,0x33,0x1E,0x0C,0x1E,0x00],	# 0xED
		[0x00,0x3F,0x00,0x00,0x00,0x00,0x00,0x00],	# 0xEE
		[0x18,0x0C,0x00,0x00,0x00,0x00,0x00,0x00],	# 0xEF
		[0x00,0x00,0x00,0x00,0x3F,0x00,0x00,0x00],	# 0xF0
		[0x0C,0x0C,0x3F,0x0C,0x0C,0x00,0x3F,0x00],	# 0xF1
		[0x00,0x00,0x00,0x3F,0x00,0x3F,0x00,0x00],	# 0xF2
		[0x67,0x34,0x1E,0xCC,0xE7,0xB3,0xF9,0xC0],	# 0xF3
		[0xFE,0xDB,0xDB,0xDE,0xD8,0xD8,0xD8,0x00],	# 0xF4
		[0x7E,0xC3,0x1E,0x33,0x33,0x1E,0x31,0x1F],	# 0xF5
		[0x0C,0x0C,0x00,0x3F,0x00,0x0C,0x0C,0x00],	# 0xF6
		[0x00,0x00,0x00,0x00,0x00,0x00,0x0C,0x06],	# 0xF7
		[0x1C,0x36,0x36,0x1C,0x00,0x00,0x00,0x00],	# 0xF8
		[0x00,0x33,0x00,0x00,0x00,0x00,0x00,0x00],	# 0xF9
		[0x00,0x00,0x00,0x00,0x18,0x00,0x00,0x00],	# 0xFA
		[0x1C,0x1E,0x18,0x18,0x7E,0x00,0x00,0x00],	# 0xFB
		[0x3E,0x70,0x3C,0x70,0x3E,0x00,0x00,0x00],	# 0xFC
		[0x1E,0x30,0x1C,0x06,0x3E,0x00,0x00,0x00],	# 0xFD
		[0x00,0x00,0x3C,0x3C,0x3C,0x3C,0x00,0x00],	# 0xFE
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]	# 0xFF
	];

	ASCII_TABLE_HORIZONTAL = [
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x00
		[0x7E,0x81,0x95,0xB1,0xB1,0x95,0x81,0x7E],	# 0x01
		[0x7E,0xFF,0xEB,0xCF,0xCF,0xEB,0xFF,0x7E],	# 0x02
		[0x0E,0x1F,0x3F,0x7E,0x3F,0x1F,0x0E,0x00],	# 0x03
		[0x08,0x1C,0x3E,0x7F,0x3E,0x1C,0x08,0x00],	# 0x04
		[0x38,0x3A,0x9F,0xFF,0x9F,0x3A,0x38,0x00],	# 0x05
		[0x10,0x38,0xBC,0xFF,0xBC,0x38,0x10,0x00],	# 0x06
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x07
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x08
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x09
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x0A
		[0x70,0xF8,0x88,0x88,0xFD,0x7F,0x07,0x0F],	# 0x0B
		[0x00,0x4E,0x5F,0xF1,0xF1,0x5F,0x4E,0x00],	# 0x0C
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x0D
		[0xC0,0xFF,0x7F,0x05,0x05,0x65,0x7F,0x3F],	# 0x0E
		[0x99,0x5A,0x3C,0xE7,0xE7,0x3C,0x5A,0x99],	# 0x0F
		[0x7F,0x3E,0x3E,0x1C,0x1C,0x08,0x08,0x00],	# 0x10
		[0x08,0x08,0x1C,0x1C,0x3E,0x3E,0x7F,0x00],	# 0x11
		[0x00,0x24,0x66,0xFF,0xFF,0x66,0x24,0x00],	# 0x12
		[0x00,0x5F,0x5F,0x00,0x00,0x5F,0x5F,0x00],	# 0x13
		[0x06,0x0F,0x09,0x7F,0x7F,0x01,0x7F,0x7F],	# 0x14
		[0xDA,0xBF,0xA5,0xA5,0xFD,0x59,0x03,0x02],	# 0x15
		[0x00,0x70,0x70,0x70,0x70,0x70,0x70,0x00],	# 0x16
		[0x80,0x94,0xB6,0xFF,0xFF,0xB6,0x94,0x80],	# 0x17
		[0x00,0x04,0x06,0x7F,0x7F,0x06,0x04,0x00],	# 0x18
		[0x00,0x10,0x30,0x7F,0x7F,0x30,0x10,0x00],	# 0x19
		[0x08,0x08,0x08,0x2A,0x3E,0x1C,0x08,0x00],	# 0x1A
		[0x08,0x1C,0x3E,0x2A,0x08,0x08,0x08,0x00],	# 0x1B
		[0x3C,0x3C,0x20,0x20,0x20,0x20,0x20,0x00],	# 0x1C
		[0x08,0x1C,0x3E,0x08,0x08,0x3E,0x1C,0x08],	# 0x1D
		[0x30,0x38,0x3C,0x3E,0x3E,0x3C,0x38,0x30],	# 0x1E
		[0x06,0x0E,0x1E,0x3E,0x3E,0x1E,0x0E,0x06],	# 0x1F
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],	# 0x20
		[0x00,0x06,0x5F,0x5F,0x06,0x00,0x00,0x00],	# 0x21
		[0x00,0x07,0x07,0x00,0x07,0x07,0x00,0x00],	# 0x22
		[0x14,0x7F,0x7F,0x14,0x7F,0x7F,0x14,0x00],	# 0x23
		[0x24,0x2E,0x6B,0x6B,0x3A,0x12,0x00,0x00],	# 0x24
		[0x46,0x66,0x30,0x18,0x0C,0x66,0x62,0x00],	# 0x25
		[0x30,0x7A,0x4F,0x5D,0x37,0x7A,0x48,0x00],	# 0x26
		[0x04,0x07,0x03,0x00,0x00,0x00,0x00,0x00],	# 0x27
		[0x00,0x1C,0x3E,0x63,0x41,0x00,0x00,0x00],	# 0x28
		[0x00,0x41,0x63,0x3E,0x1C,0x00,0x00,0x00],	# 0x29
		[0x08,0x2A,0x3E,0x1C,0x1C,0x3E,0x2A,0x08],	# 0x2A
		[0x08,0x08,0x3E,0x3E,0x08,0x08,0x00,0x00],	# 0x2B
		[0x00,0xA0,0xE0,0x60,0x00,0x00,0x00,0x00],	# 0x2C
		[0x08,0x08,0x08,0x08,0x08,0x08,0x00,0x00],	# 0x2D
		[0x00,0x00,0x60,0x60,0x00,0x00,0x00,0x00],	# 0x2E
		[0x60,0x30,0x18,0x0C,0x06,0x03,0x01,0x00],	# 0x2F
		[0x3E,0x7F,0x59,0x4D,0x7F,0x3E,0x00,0x00],	# 0x30
		[0x42,0x42,0x7F,0x7F,0x40,0x40,0x00,0x00],	# 0x31
		[0x62,0x73,0x59,0x49,0x6F,0x66,0x00,0x00],	# 0x32
		[0x22,0x63,0x49,0x49,0x7F,0x36,0x00,0x00],	# 0x33
		[0x18,0x1C,0x16,0x13,0x7F,0x7F,0x10,0x00],	# 0x34
		[0x27,0x67,0x45,0x45,0x7D,0x39,0x00,0x00],	# 0x35
		[0x3C,0x7E,0x4B,0x49,0x79,0x30,0x00,0x00],	# 0x36
		[0x03,0x63,0x71,0x19,0x0F,0x07,0x00,0x00],	# 0x37
		[0x36,0x7F,0x49,0x49,0x7F,0x36,0x00,0x00],	# 0x38
		[0x06,0x4F,0x49,0x69,0x3F,0x1E,0x00,0x00],	# 0x39
		[0x00,0x00,0x6C,0x6C,0x00,0x00,0x00,0x00],	# 0x3A
		[0x00,0xA0,0xEC,0x6C,0x00,0x00,0x00,0x00],	# 0x3B
		[0x08,0x1C,0x36,0x63,0x41,0x00,0x00,0x00],	# 0x3C
		[0x14,0x14,0x14,0x14,0x14,0x14,0x00,0x00],	# 0x3D
		[0x00,0x41,0x63,0x36,0x1C,0x08,0x00,0x00],	# 0x3E
		[0x02,0x03,0x51,0x59,0x0F,0x06,0x00,0x00],	# 0x3F
		[0x3E,0x7F,0x41,0x5D,0x5D,0x1F,0x1E,0x00],	# 0x40
		[0x7C,0x7E,0x13,0x13,0x7E,0x7C,0x00,0x00],	# 0x41
		[0x41,0x7F,0x7F,0x49,0x49,0x7F,0x36,0x00],	# 0x42
		[0x1C,0x3E,0x63,0x41,0x41,0x63,0x22,0x00],	# 0x43
		[0x41,0x7F,0x7F,0x41,0x63,0x7F,0x1C,0x00],	# 0x44
		[0x41,0x7F,0x7F,0x49,0x5D,0x41,0x63,0x00],	# 0x45
		[0x41,0x7F,0x7F,0x49,0x1D,0x01,0x03,0x00],	# 0x46
		[0x1C,0x3E,0x63,0x41,0x51,0x73,0x72,0x00],	# 0x47
		[0x7F,0x7F,0x08,0x08,0x7F,0x7F,0x00,0x00],	# 0x48
		[0x00,0x41,0x7F,0x7F,0x41,0x00,0x00,0x00],	# 0x49
		[0x30,0x70,0x40,0x41,0x7F,0x3F,0x01,0x00],	# 0x4A
		[0x41,0x7F,0x7F,0x08,0x1C,0x77,0x63,0x00],	# 0x4B
		[0x41,0x7F,0x7F,0x41,0x40,0x60,0x70,0x00],	# 0x4C
		[0x7F,0x7F,0x06,0x0C,0x06,0x7F,0x7F,0x00],	# 0x4D
		[0x7F,0x7F,0x06,0x0C,0x18,0x7F,0x7F,0x00],	# 0x4E
		[0x1C,0x3E,0x63,0x41,0x63,0x3E,0x1C,0x00],	# 0x4F
		[0x41,0x7F,0x7F,0x49,0x09,0x0F,0x06,0x00],	# 0x50
		[0x1E,0x3F,0x21,0x71,0x7F,0x5E,0x00,0x00],	# 0x51
		[0x41,0x7F,0x7F,0x19,0x39,0x6F,0x46,0x00],	# 0x52
		[0x26,0x67,0x4D,0x59,0x7B,0x32,0x00,0x00],	# 0x53
		[0x03,0x41,0x7F,0x7F,0x41,0x03,0x00,0x00],	# 0x54
		[0x7F,0x7F,0x40,0x40,0x7F,0x7F,0x00,0x00],	# 0x55
		[0x1F,0x3F,0x60,0x60,0x3F,0x1F,0x00,0x00],	# 0x56
		[0x7F,0x7F,0x30,0x18,0x30,0x7F,0x7F,0x00],	# 0x57
		[0x63,0x77,0x1C,0x08,0x1C,0x77,0x63,0x00],	# 0x58
		[0x07,0x4F,0x78,0x78,0x4F,0x07,0x00,0x00],	# 0x59
		[0x67,0x73,0x59,0x4D,0x47,0x63,0x71,0x00],	# 0x5A
		[0x00,0x7F,0x7F,0x41,0x41,0x00,0x00,0x00],	# 0x5B
		[0x01,0x03,0x06,0x0C,0x18,0x30,0x60,0x00],	# 0x5C
		[0x00,0x41,0x41,0x7F,0x7F,0x00,0x00,0x00],	# 0x5D
		[0x08,0x0C,0x06,0x03,0x06,0x0C,0x08,0x00],	# 0x5E
		[0x80,0x80,0x80,0x80,0x80,0x80,0x80,0x80],	# 0x5F
		[0x00,0x00,0x03,0x07,0x04,0x00,0x00,0x00],	# 0x60
		[0x20,0x74,0x54,0x54,0x3C,0x78,0x40,0x00],	# 0x61
		[0x41,0x3F,0x7F,0x44,0x44,0x7C,0x38,0x00],	# 0x62
		[0x38,0x7C,0x44,0x44,0x6C,0x28,0x00,0x00],	# 0x63
		[0x30,0x78,0x48,0x49,0x3F,0x7F,0x40,0x00],	# 0x64
		[0x38,0x7C,0x54,0x54,0x5C,0x18,0x00,0x00],	# 0x65
		[0x48,0x7E,0x7F,0x49,0x03,0x02,0x00,0x00],	# 0x66
		[0x98,0xBC,0xA4,0xA4,0xF8,0x7C,0x04,0x00],	# 0x67
		[0x41,0x7F,0x7F,0x08,0x04,0x7C,0x78,0x00],	# 0x68
		[0x00,0x44,0x7D,0x7D,0x40,0x00,0x00,0x00],	# 0x69
		[0x40,0xC4,0x84,0xFD,0x7D,0x00,0x00,0x00],	# 0x6A
		[0x41,0x7F,0x7F,0x10,0x38,0x6C,0x44,0x00],	# 0x6B
		[0x00,0x41,0x7F,0x7F,0x40,0x00,0x00,0x00],	# 0x6C
		[0x7C,0x7C,0x0C,0x18,0x0C,0x7C,0x78,0x00],	# 0x6D
		[0x7C,0x7C,0x04,0x04,0x7C,0x78,0x00,0x00],	# 0x6E
		[0x38,0x7C,0x44,0x44,0x7C,0x38,0x00,0x00],	# 0x6F
		[0x84,0xFC,0xF8,0xA4,0x24,0x3C,0x18,0x00],	# 0x70
		[0x18,0x3C,0x24,0xA4,0xF8,0xFC,0x84,0x00],	# 0x71
		[0x44,0x7C,0x78,0x44,0x1C,0x18,0x00,0x00],	# 0x72
		[0x48,0x5C,0x54,0x54,0x74,0x24,0x00,0x00],	# 0x73
		[0x00,0x04,0x3E,0x7F,0x44,0x24,0x00,0x00],	# 0x74
		[0x3C,0x7C,0x40,0x40,0x3C,0x7C,0x40,0x00],	# 0x75
		[0x1C,0x3C,0x60,0x60,0x3C,0x1C,0x00,0x00],	# 0x76
		[0x3C,0x7C,0x60,0x30,0x60,0x7C,0x3C,0x00],	# 0x77
		[0x44,0x6C,0x38,0x10,0x38,0x6C,0x44,0x00],	# 0x78
		[0x9C,0xBC,0xA0,0xA0,0xFC,0x7C,0x00,0x00],	# 0x79
		[0x4C,0x64,0x74,0x5C,0x4C,0x64,0x00,0x00],	# 0x7A
		[0x08,0x08,0x3E,0x77,0x41,0x41,0x00,0x00],	# 0x7B
		[0x00,0x00,0x00,0x77,0x77,0x00,0x00,0x00],	# 0x7C
		[0x41,0x41,0x77,0x3E,0x08,0x08,0x00,0x00],	# 0x7D
		[0x02,0x03,0x01,0x03,0x02,0x03,0x01,0x00],	# 0x7E
		[0x78,0x7C,0x46,0x43,0x46,0x7C,0x78,0x00],	# 0x7F
		[0x1E,0xBF,0xE1,0x61,0x33,0x12,0x00,0x00],	# 0x80
		[0x3A,0x7A,0x40,0x40,0x7A,0x7A,0x40,0x00],	# 0x81
		[0x38,0x7C,0x56,0x57,0x5D,0x18,0x00,0x00],	# 0x82
		[0x02,0x23,0x75,0x55,0x55,0x7D,0x7B,0x42],	# 0x83
		[0x21,0x75,0x54,0x54,0x7D,0x79,0x40,0x00],	# 0x84
		[0x20,0x75,0x57,0x56,0x7C,0x78,0x40,0x00],	# 0x85
		[0x00,0x22,0x77,0x55,0x55,0x7F,0x7A,0x40],	# 0x86
		[0x1C,0xBE,0xE2,0x62,0x36,0x14,0x00,0x00],	# 0x87
		[0x02,0x3B,0x7D,0x55,0x55,0x5D,0x1B,0x02],	# 0x88
		[0x39,0x7D,0x54,0x54,0x5D,0x19,0x00,0x00],	# 0x89
		[0x38,0x7D,0x57,0x56,0x5C,0x18,0x00,0x00],	# 0x8A
		[0x01,0x45,0x7C,0x7C,0x41,0x01,0x00,0x00],	# 0x8B
		[0x02,0x03,0x45,0x7D,0x7D,0x43,0x02,0x00],	# 0x8C
		[0x00,0x45,0x7F,0x7E,0x40,0x00,0x00,0x00],	# 0x8D
		[0x79,0x7D,0x26,0x26,0x7D,0x79,0x00,0x00],	# 0x8E
		[0x70,0x7A,0x2D,0x2D,0x7A,0x70,0x00,0x00],	# 0x8F
		[0x44,0x7C,0x7E,0x57,0x55,0x44,0x00,0x00],	# 0x90
		[0x20,0x74,0x54,0x54,0x7C,0x7C,0x54,0x54],	# 0x91
		[0x7C,0x7E,0x0B,0x09,0x7F,0x7F,0x49,0x00],	# 0x92
		[0x32,0x7B,0x49,0x49,0x7B,0x32,0x00,0x00],	# 0x93
		[0x32,0x7A,0x48,0x48,0x7A,0x32,0x00,0x00],	# 0x94
		[0x30,0x79,0x4B,0x4A,0x78,0x30,0x00,0x00],	# 0x95
		[0x3A,0x7B,0x41,0x41,0x7B,0x7A,0x40,0x00],	# 0x96
		[0x38,0x79,0x43,0x42,0x78,0x78,0x40,0x00],	# 0x97
		[0xBA,0xBA,0xA0,0xA0,0xFA,0x7A,0x00,0x00],	# 0x98
		[0x39,0x7D,0x44,0x44,0x44,0x7D,0x39,0x00],	# 0x99
		[0x3D,0x7D,0x40,0x40,0x7D,0x3D,0x00,0x00],	# 0x9A
		[0x38,0x7C,0x64,0x54,0x4C,0x7C,0x38,0x00],	# 0x9B
		[0x68,0x7E,0x7F,0x49,0x43,0x66,0x20,0x00],	# 0x9C
		[0x5C,0x3E,0x73,0x49,0x67,0x3E,0x1D,0x00],	# 0x9D
		[0x44,0x6C,0x38,0x38,0x6C,0x44,0x00,0x00],	# 0x9E
		[0x40,0xC8,0x88,0xFE,0x7F,0x09,0x0B,0x02],	# 0x9F
		[0x20,0x74,0x56,0x57,0x7D,0x78,0x40,0x00],	# 0xA0
		[0x00,0x44,0x7E,0x7F,0x41,0x00,0x00,0x00],	# 0xA1
		[0x30,0x78,0x48,0x4A,0x7B,0x31,0x00,0x00],	# 0xA2
		[0x38,0x78,0x40,0x42,0x7B,0x79,0x40,0x00],	# 0xA3
		[0x7A,0x7B,0x09,0x0B,0x7A,0x73,0x01,0x00],	# 0xA4
		[0x7A,0x7B,0x19,0x33,0x7A,0x7B,0x01,0x00],	# 0xA5
		[0x00,0x26,0x2F,0x29,0x2F,0x2F,0x28,0x00],	# 0xA6
		[0x00,0x26,0x2F,0x29,0x29,0x2F,0x26,0x00],	# 0xA7
		[0x30,0x78,0x4D,0x45,0x60,0x20,0x00,0x00],	# 0xA8
		[0x1C,0x22,0x7D,0x4B,0x5B,0x65,0x22,0x1C],	# 0xA9
		[0x08,0x08,0x08,0x08,0x38,0x38,0x00,0x00],	# 0xAA
		[0x61,0x3F,0x1F,0xCC,0xEE,0xAB,0xB9,0x90],	# 0xAB
		[0x61,0x3F,0x1F,0x4C,0x66,0x73,0xD9,0xF8],	# 0xAC
		[0x00,0x00,0x60,0xFA,0xFA,0x60,0x00,0x00],	# 0xAD
		[0x08,0x1C,0x36,0x22,0x08,0x1C,0x36,0x22],	# 0xAE
		[0x22,0x36,0x1C,0x08,0x22,0x36,0x1C,0x08],	# 0xAF
		[0xAA,0x00,0x55,0x00,0xAA,0x00,0x55,0x00],	# 0xB0
		[0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55],	# 0xB1
		[0x55,0xFF,0xAA,0xFF,0x55,0xFF,0xAA,0xFF],	# 0xB2
		[0x00,0x00,0x00,0xFF,0xFF,0x00,0x00,0x00],	# 0xB3
		[0x10,0x10,0x10,0xFF,0xFF,0x00,0x00,0x00],	# 0xB4
		[0x70,0x78,0x2C,0x2E,0x7B,0x71,0x00,0x00],	# 0xB5
		[0x72,0x79,0x2D,0x2D,0x79,0x72,0x00,0x00],	# 0xB6
		[0x71,0x7B,0x2E,0x2C,0x78,0x70,0x00,0x00],	# 0xB7
		[0x1C,0x22,0x5D,0x55,0x55,0x41,0x22,0x1C],	# 0xB8
		[0x14,0x14,0xF7,0xF7,0x00,0xFF,0xFF,0x00],	# 0xB9
		[0x00,0x00,0xFF,0xFF,0x00,0xFF,0xFF,0x00],	# 0xBA
		[0x14,0x14,0xF4,0xF4,0x04,0xFC,0xFC,0x00],	# 0xBB
		[0x14,0x14,0x17,0x17,0x10,0x1F,0x1F,0x00],	# 0xBC
		[0x18,0x3C,0x24,0xE7,0xE7,0x24,0x24,0x00],	# 0xBD
		[0x2B,0x2F,0xFC,0xFC,0x2F,0x2B,0x00,0x00],	# 0xBE
		[0x10,0x10,0x10,0xF0,0xF0,0x00,0x00,0x00],	# 0xBF
		[0x00,0x00,0x00,0x1F,0x1F,0x10,0x10,0x10],	# 0xC0
		[0x10,0x10,0x10,0x1F,0x1F,0x10,0x10,0x10],	# 0xC1
		[0x10,0x10,0x10,0xF0,0xF0,0x10,0x10,0x10],	# 0xC2
		[0x00,0x00,0x00,0xFF,0xFF,0x10,0x10,0x10],	# 0xC3
		[0x10,0x10,0x10,0x10,0x10,0x10,0x10,0x10],	# 0xC4
		[0x10,0x10,0x10,0xFF,0xFF,0x10,0x10,0x10],	# 0xC5
		[0x22,0x77,0x55,0x57,0x7E,0x7B,0x41,0x00],	# 0xC6
		[0x72,0x7B,0x2D,0x2F,0x7A,0x73,0x01,0x00],	# 0xC7
		[0x00,0x00,0x1F,0x1F,0x10,0x17,0x17,0x14],	# 0xC8
		[0x00,0x00,0xFC,0xFC,0x04,0xF4,0xF4,0x14],	# 0xC9
		[0x14,0x14,0x17,0x17,0x10,0x17,0x17,0x14],	# 0xCA
		[0x14,0x14,0xF4,0xF4,0x04,0xF4,0xF4,0x14],	# 0xCB
		[0x00,0x00,0xFF,0xFF,0x00,0xF7,0xF7,0x14],	# 0xCC
		[0x14,0x14,0x14,0x14,0x14,0x14,0x14,0x14],	# 0xCD
		[0x14,0x14,0xF7,0xF7,0x00,0xF7,0xF7,0x14],	# 0xCE
		[0x66,0x3C,0x3C,0x24,0x3C,0x3C,0x66,0x00],	# 0xCF
		[0x05,0x27,0x72,0x57,0x7D,0x38,0x00,0x00],	# 0xD0
		[0x49,0x7F,0x7F,0x49,0x63,0x7F,0x1C,0x00],	# 0xD1
		[0x46,0x7D,0x7D,0x55,0x55,0x46,0x00,0x00],	# 0xD2
		[0x45,0x7D,0x7C,0x54,0x55,0x45,0x00,0x00],	# 0xD3
		[0x44,0x7D,0x7F,0x56,0x54,0x44,0x00,0x00],	# 0xD4
		[0x0A,0x0E,0x08,0x00,0x00,0x00,0x00,0x00],	# 0xD5
		[0x00,0x44,0x7E,0x7F,0x45,0x00,0x00,0x00],	# 0xD6
		[0x02,0x45,0x7D,0x7D,0x45,0x02,0x00,0x00],	# 0xD7
		[0x01,0x45,0x7C,0x7C,0x45,0x01,0x00,0x00],	# 0xD8
		[0x10,0x10,0x10,0x1F,0x1F,0x00,0x00,0x00],	# 0xD9
		[0x00,0x00,0x00,0xF0,0xF0,0x10,0x10,0x10],	# 0xDA
		[0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF],	# 0xDB
		[0xF0,0xF0,0xF0,0xF0,0xF0,0xF0,0xF0,0xF0],	# 0xDC
		[0x00,0x00,0x00,0x77,0x77,0x00,0x00,0x00],	# 0xDD
		[0x00,0x45,0x7F,0x7E,0x44,0x00,0x00,0x00],	# 0xDE
		[0x0F,0x0F,0x0F,0x0F,0x0F,0x0F,0x0F,0x0F],	# 0xDF
		[0x38,0x7C,0x46,0x47,0x45,0x7C,0x38,0x00],	# 0xE0
		[0xFC,0xFE,0x2A,0x2A,0x3E,0x14,0x00,0x00],	# 0xE1
		[0x3A,0x7D,0x45,0x45,0x45,0x7D,0x3A,0x00],	# 0xE2
		[0x38,0x7C,0x45,0x47,0x46,0x7C,0x38,0x00],	# 0xE3
		[0x32,0x7B,0x49,0x4B,0x7A,0x33,0x01,0x00],	# 0xE4
		[0x3A,0x7F,0x45,0x47,0x46,0x7F,0x39,0x00],	# 0xE5
		[0x80,0xFE,0x7E,0x20,0x20,0x3E,0x1E,0x00],	# 0xE6
		[0x42,0x7E,0x7E,0x54,0x1C,0x08,0x00,0x00],	# 0xE7
		[0x41,0x7F,0x7F,0x55,0x14,0x1C,0x08,0x00],	# 0xE8
		[0x3C,0x7C,0x42,0x43,0x7D,0x3C,0x00,0x00],	# 0xE9
		[0x3A,0x79,0x41,0x41,0x79,0x3A,0x00,0x00],	# 0xEA
		[0x3C,0x7D,0x43,0x42,0x7C,0x3C,0x00,0x00],	# 0xEB
		[0xB8,0xB8,0xA2,0xA3,0xF9,0x78,0x00,0x00],	# 0xEC
		[0x0C,0x5C,0x72,0x73,0x5D,0x0C,0x00,0x00],	# 0xED
		[0x02,0x02,0x02,0x02,0x02,0x02,0x00,0x00],	# 0xEE
		[0x00,0x00,0x02,0x03,0x01,0x00,0x00,0x00],	# 0xEF
		[0x10,0x10,0x10,0x10,0x10,0x10,0x00,0x00],	# 0xF0
		[0x44,0x44,0x5F,0x5F,0x44,0x44,0x00,0x00],	# 0xF1
		[0x28,0x28,0x28,0x28,0x28,0x28,0x00,0x00],	# 0xF2
		[0x71,0x35,0x1F,0x4C,0x66,0x73,0xD9,0xF8],	# 0xF3
		[0x06,0x0F,0x09,0x7F,0x7F,0x01,0x7F,0x7F],	# 0xF4
		[0xDA,0xBF,0xA5,0xA5,0xFD,0x59,0x03,0x02],	# 0xF5
		[0x08,0x08,0x6B,0x6B,0x08,0x08,0x00,0x00],	# 0xF6
		[0x00,0x80,0xC0,0x40,0x00,0x00,0x00,0x00],	# 0xF7
		[0x00,0x06,0x0F,0x09,0x0F,0x06,0x00,0x00],	# 0xF8
		[0x02,0x02,0x00,0x00,0x02,0x02,0x00,0x00],	# 0xF9
		[0x00,0x00,0x00,0x10,0x10,0x00,0x00,0x00],	# 0xFA
		[0x00,0x12,0x13,0x1F,0x1F,0x10,0x10,0x00],	# 0xFB
		[0x00,0x11,0x15,0x15,0x1F,0x1F,0x0A,0x00],	# 0xFC
		[0x00,0x19,0x1D,0x15,0x17,0x12,0x00,0x00],	# 0xFD
		[0x00,0x00,0x3C,0x3C,0x3C,0x3C,0x00,0x00],	# 0xFE
		[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]	# 0xFF
	];

	def __init__(self, device, baud, i2c_addr=0x78, i2c_freq=4, width=128, height=64):
		BusPirateI2C.__init__(self, device=device, baud=baud, i2c_addr=i2c_addr, i2c_freq=i2c_freq)
		self.width = width
		self.height = height

		self.cursor_column = 0
		self.columns = int(self.width/8)
		self.cursor_row = 0
		self.rows = int(self.height/8)

	def setClockDiv(self, div):
		self.ssd1306_cmd(0xd5)
		self.ssd1306_cmd(div)

	def setMultiplexRatio(self, ratio):
		self.ssd1306_cmd(0xa8)
		self.ssd1306_cmd(ratio)

	def setDisplayOffset(self, offset):
		self.ssd1306_cmd(0xd3)
		self.ssd1306_cmd(offset)

	def setMemoryAddressingMode(self, mode):
		self.ssd1306_cmd(0x20)
		self.ssd1306_cmd(mode)

	def setContrast(self, contrast=0x7F):
		self.ssd1306_cmd(0x81)
		self.ssd1306_cmd(contrast)

	def setPrechargePeriod(self, period):
		self.ssd1306_cmd(0xd9)
		self.ssd1306_cmd(period)

	def setVCOMHDeselectLevel(self, level):
		self.ssd1306_cmd(0xdb)
		self.ssd1306_cmd(level)

	def setInverse(self, one_means_on=False):
		if one_means_on == True:
			self.ssd1306_cmd(0xA6)
		else:
			self.ssd1306_cmd(0xA7)

	def setEnableRamOutput(self, ignoreram=False):
		self.ssd1306_cmd(0xA4 + (ignoreram == True)*0x01)

	def setColumnStartAddress(self, start):
		l = start & 0x0F
		h = (start & 0xF0) >> 4
		self.ssd1306_cmd(0x00 | l)
		self.ssd1306_cmd(0x10 | h)

	def setColumnStartEnd(self, start=0x00, end=0x7F):
		self.ssd1306_cmd(0x21)
		self.ssd1306_cmd(start & 0x7F)
		self.ssd1306_cmd(end & 0x7F)

	def setPageStartEnd(self, start=0x00, end=0x07):
		self.ssd1306_cmd(0x22)
		self.ssd1306_cmd(start & 0x07)
		self.ssd1306_cmd(end & 0x07)

	def setPageStartAddress(self, start):
		self.debug('New page start address %i' % start)
		self.ssd1306_cmd(0xb0|  (start & 0x07))
	
	def setDisplayStartLine(self, line):
		d = (line & 0x1F) | 0x40
		self.ssd1306_cmd(d)

	def setDisplayOffset(self, offset):
		self.ssd1306_cmd(0xd3)
		self.ssd1306_cmd(offset & 0x3F)

	def setScroll(self, activate=True):
		self.ssd1306_cmd(0x2E + (activate == True)*1)

	def setChargePump(self, enabled):
		self.ssd1306_cmd(0x8D)
		self.ssd1306_cmd(0x10 + (enabled == True)*0x04)

	def setCOMPinConfiguration(self, sequential, leftrightremap):
		d  = 0x02
		d |= (sequential == True)*0x10
		d |= (leftrightremap == True)*0x20
		self.ssd1306_cmd(0xda)
		self.ssd1306_cmd(d)

	def setSegmentRemap(self, lefttoright):
		self.ssd1306_cmd(0xA0 + (lefttoright == True)*0x01)

	def setCOMOutputScanDirection(self, normal):
		self.ssd1306_cmd(0xC0 + (normal == False)*0x08)

	def setDisplayPower(self, on):
		self.ssd1306_cmd(0xAE + (on == True)*1)

	def setCursorPosition(self, x, y):
		self.cursor_column = x % self.columns
		self.cursor_row = y % self.rows

	def getCursorPosition(self):
		return (self.cursor_column, self.cursor_row)

	def print(self, msg, vertical=False):
		self.setColumnStartEnd(0, self.width-1)
		self.setPageStartEnd(0, self.rows-1)
		self.setColumnStartAddress(self.cursor_column*8)
		self.setPageStartAddress(self.cursor_row)

		for char in msg:
			if vertical == False:
				self.ssd1306_ctrl(BusPirateSSD1306.ASCII_TABLE_HORIZONTAL[ord(char)])
			else:
				self.ssd1306_ctrl(BusPirateSSD1306.ASCII_TABLE_VERTICAL[ord(char)])

			self.cursor_column += 1
			if self.cursor_column >= self.columns:
				self.cursor_column = 0
				self.cursor_row += 1
		
		self.cursor_column %= self.columns
		self.cursor_row %= self.rows

		return self.getCursorPosition()
		
	def println(self, msg, vertical=False):
		self.print(msg, vertical)
		self.cursor_column = 0
		self.cursor_row = (self.cursor_row+1) % self.rows
		return self.getCursorPosition()

	def init(self):
		BusPirateI2C.init(self)
		self.setDisplayPower(False)
		self.setClockDiv(0x80)
		self.setMultiplexRatio(0x3f)
		self.setChargePump(True)
		self.setContrast(0x00)
		self.setPrechargePeriod(0xf1)
		self.setVCOMHDeselectLevel(0x40)
		self.setInverse(True)

		self.setMemoryAddressingMode(BusPirateSSD1306.MEM_ADDR_MODE_PAGE)
		self.setSegmentRemap(True)
		self.setCOMOutputScanDirection(False)
		self.setCOMPinConfiguration(True, False)
		self.setDisplayOffset(0x00)
		self.setDisplayStartLine(0x00)
		self.setColumnStartEnd(0, self.width-1)
		self.setPageStartEnd(0, int(self.height/8)-1)

		self.setEnableRamOutput()
		self.setDisplayPower(True)

	def clear(self):
		self.ssd1306_ctrl('0x00:1024')
		sleep(0.5)
	
	def fill(self):
		self.ssd1306_ctrl('0xFF:1024')
		sleep(0.5)

	def ssd1306_cmd(self, command):
		self.i2c_write([0x00, command])

	def ssd1306_ctrl(self, control):
		if type(control) == list:
			self.i2c_write([0x40] + control)
		else:
			self.i2c_write([0x40, control])

class BusPirateSSD1306Buffered(BusPirateSSD1306):
	def __init__(self, device, baud, i2c_addr=0x78, width=128, height=64):
		BusPirateSSD1306.__init__(self, device=device, baud=baud, i2c_addr=i2c_addr, i2c_freq=4, width=width, height=height)
		self.buffer = [0x00]*self.width*int(self.height/8)

	def init(self):
		BusPirateSSD1306.init(self)

	def setPixel(self, x, y, value=0x01):
		ox = int(x) % self.width
		oy = int(y/8) % self.height
		off = oy*self.width+ox

		cv = (int(y) % 8)

		if value == 0x00:
			self.buffer[off] &= (0xff ^ (0x01 << cv))
		else:
			self.buffer[off] |= (0x01 << cv)

	def clear(self):
		self.buffer = [0x00]*self.width*int(self.height/8)
		BusPirateSSD1306.clear(self)

	def fill(self):
		self.buffer = [0xff]*self.width*int(self.height/8)
		self.sync()
		#BusPirateSSD1306Buffered.fill(self)

	def sync(self, block=16):
		self.setColumnStartEnd(0x00, 0x7f)
		self.setPageStartEnd(0x00, 0x07)

		idx = 0
		while idx < self.width*self.height/8:
			d = []
			for j in range(0, block):
				d += [self.buffer[idx]]
				idx += 1

			self.i2c_write([0x40] + d)


if __name__ == "buspirate_SSD1306":
	import psutil, sys
	from datetime import datetime
	d = BusPirateSSD1306(device=sys.argv[1], baud=115200)
	d.init()
	d.clear()
	
	d.setCursorPosition(0, 2)
	d.println('CPU:')
	d.println('MEM:')

	d.setCursorPosition(0, 5)
	d.println('Net stats in MB')
	d.println('Snt:')
	d.println('Rcv:')

	while True:
		d.setCursorPosition(0, 0)
		d.println(datetime.now().strftime('%Y/%m/%d'))
		d.println(datetime.now().strftime('%H:%M:%S'))

		d.setCursorPosition(5, 2)
		d.print('%3.1f  ' % (psutil.cpu_percent()))
		d.setCursorPosition(5, 3)
		d.print('%3.1f  ' % (psutil.virtual_memory().percent))

		d.setCursorPosition(5, 6)
		d.print('%i  ' % (psutil.net_io_counters().bytes_sent/1048576))
		d.setCursorPosition(5, 7)
		d.print('%i  ' % (psutil.net_io_counters().bytes_recv/1048576))


