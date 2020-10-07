import struct
from ctypes import *
from x64dbgpy import *


class App(Structure):
    _fields_ = [
        ("id", c_int32),
        ("name", c_void_p),
        ("callback", c_void_p),
    ]


def bswap(val):
    return struct.unpack("<I", struct.pack(">I", val))[0]

def get_section(section_name, module=pluginsdk.GetMainModuleInfo()):
    for i in xrange(module.sectionCount):
        section = pluginsdk.SectionFromAddr(module.base, i)
        if section.name == section_name:
            return section

def get_string(ea, max_length=1024):
    byte_array = bytearray()
    for offset in xrange(max_length + 1):
        read_byte = pluginsdk.ReadByte(ea + offset)
        if read_byte == 0:
            break
        byte_array.append(read_byte)

    return str(byte_array)


if __name__ == '__main__':
    rdata_section = get_section('.rdata')
    Test1_address = pluginsdk.FindMem(rdata_section.addr, rdata_section.size, "Test1".encode('hex'))
    data_section = get_section('.data')
    Test1_pointer = pluginsdk.FindMem(data_section.addr, data_section.size, "%08X" % bswap(Test1_address))
    app_array_address = Test1_pointer - sizeof(c_int32)

    app_size = sizeof(App)
    app_offset = 0
    while True:
        app = App.from_buffer_copy(pluginsdk.Read(app_array_address + app_offset, app_size))
        if not app.name:
            break

        print 'App Id: %d' % app.id
        print 'App Name: %s' % get_string(app.name)
        print 'App Callback Address: 0x%08X\n' % app.callback

        app_offset += app_size
