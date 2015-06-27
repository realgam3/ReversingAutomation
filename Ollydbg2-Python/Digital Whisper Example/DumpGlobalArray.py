import struct
from ctypes import *
from ollyapi import *


class App(Structure):
    _fields_ = [
        ("id", c_int32),
        ("name", c_void_p),
        ("callback", c_void_p),
    ]


def bswap(val):
    return struct.unpack("<I", struct.pack(">I", val))[0]

def get_section(section_name):
    sections = GetPESections()
    for section in sections:
        if section.sectname == section_name:
            return section.base

def get_string(ea, max_length=1024):
    byte_array = bytearray()
    for offset in xrange(max_length + 1):
        read_chr = ReadMemory(1, ea + offset)
        if read_chr == '\0':
            break
        byte_array.append(read_chr)

    return byte_array.decode("ascii")


if __name__ == '__main__':
    Test1_address = FindHexInPage("Test1".encode('hex'), get_section('.rdata'))
    Test1_pointer = FindHexInPage("%08X" % bswap(Test1_address), get_section('.data'))
    app_array_address = Test1_pointer - sizeof(c_int32)

    app_size = sizeof(App)
    app_offset = 0
    while True:
        app = App.from_buffer_copy(ReadMemory(app_size, app_array_address + app_offset))
        if not app.name:
            break

        print 'App Id: %d' % app.id
        print 'App Name: %s' % get_string(app.name)
        print 'App Callback Address: 0x%08X\n' % app.callback

        app_offset += app_size
