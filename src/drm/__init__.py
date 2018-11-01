#!/usr/bin/python3

import ctypes, enum, fcntl, mmap, os, os.path, time

IOC_NONE = 0
IOC_WRITE = 1
IOC_READ = 2

IOC_DIR_SHIFT = 30
IOC_SIZE_SHIFT = 16
IOC_TYPE_SHIFT = 8
IOC_NR_SHIFT = 0

def set_bits(x, num_bits):
    for bit in range(0, num_bits):
        if x & (1 << bit):
            yield bit

def _IOC(dir, type, nr, size):
    return dir << IOC_DIR_SHIFT | size << IOC_SIZE_SHIFT | type << IOC_TYPE_SHIFT | nr << IOC_NR_SHIFT

def _IO(type, nr):
    return _IOC(IOC_NONE, type, nr, 0)

def _IOW(type, nr, size):
    return _IOC(IOC_WRITE, type, nr, size)

def _IOR(type, nr, size):
    return _IOC(IOC_READ, type, nr, size)

def _IOWR(type, nr, size):
    return _IOC(IOC_READ | IOC_WRITE, type, nr, size)

class Error(Exception):
    pass

class DeprecatedError(Error):
    pass

class version(ctypes.Structure):
    _fields_ = [
        ('version_major', ctypes.c_int),
        ('version_minor', ctypes.c_int),
        ('version_patchlevel', ctypes.c_int),
        ('name_len', ctypes.c_ulong),
        ('name', ctypes.c_char_p),
        ('date_len', ctypes.c_ulong),
        ('date', ctypes.c_char_p),
        ('desc_len', ctypes.c_ulong),
        ('desc', ctypes.c_char_p)
    ]

class gem_close(ctypes.Structure):
    _fields_ = [
            ('handle', ctypes.c_uint32),
            ('pad', ctypes.c_uint32)
        ]

MODE_FLAG_PHSYNC = 1 << 0
MODE_FLAG_NHSYNC = 1 << 1
MODE_FLAG_PVSYNC = 1 << 2
MODE_FLAG_NVSYNC = 1 << 3
MODE_FLAG_INTERLACE = 1 << 4
MODE_FLAG_DBLSCAN = 1 << 5
MODE_FLAG_CSYNC = 1 << 6
MODE_FLAG_PCSYNC = 1 << 7
MODE_FLAG_NCSYNC = 1 << 8
MODE_FLAG_HSKEW = 1 << 9
MODE_FLAG_BCAST = 1 << 10
MODE_FLAG_PIXMUX = 1 << 11
MODE_FLAG_DBLCLK = 1 << 12
MODE_FLAG_CLKDIV2 = 1 << 13

MODE_TYPE_BUILTIN = 1 << 0
MODE_TYPE_CLOCK_C = 1 << 1 | MODE_TYPE_BUILTIN
MODE_TYPE_CRTC_C = 1 << 2 | MODE_TYPE_BUILTIN
MODE_TYPE_PREFERRED = 1 << 3
MODE_TYPE_DEFAULT = 1 << 4
MODE_TYPE_USERDEF = 1 << 5
MODE_TYPE_DRIVER = 1 << 6

class mode_info(ctypes.Structure):
    _fields_ = [
        ('clock', ctypes.c_uint32),
        ('hdisplay', ctypes.c_uint16),
        ('hsync_start', ctypes.c_uint16),
        ('hsync_end', ctypes.c_uint16),
        ('htotal', ctypes.c_uint16),
        ('hskew', ctypes.c_uint16),
        ('vdisplay', ctypes.c_uint16),
        ('vsync_start', ctypes.c_uint16),
        ('vsync_end', ctypes.c_uint16),
        ('vtotal', ctypes.c_uint16),
        ('vscan', ctypes.c_uint16),
        ('vrefresh', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('type', ctypes.c_uint32),
        ('name', (32 * ctypes.c_char))
    ]

    def __eq__(self, other):
        for field in self._fields:
            if getattr(self, field[0]) != getattr(other, field[0]):
                return False

        return True

    def __str__(self):
        return '%ux%u-%u' % (self.hdisplay, self.vdisplay, self.vrefresh)

    def get_flags(self):
        flags = []

        if self.flags & MODE_FLAG_PHSYNC:
            flags.append('phsync')

        if self.flags & MODE_FLAG_NHSYNC:
            flags.append('nhsync')

        if self.flags & MODE_FLAG_PVSYNC:
            flags.append('pvsync')

        if self.flags & MODE_FLAG_NVSYNC:
            flags.append('nvsync')

        if self.flags & MODE_FLAG_INTERLACE:
            flags.append('interlace')

        if self.flags & MODE_FLAG_DBLSCAN:
            flags.append('dblscan')

        if self.flags & MODE_FLAG_CSYNC:
            flags.append('csync')

        if self.flags & MODE_FLAG_PCSYNC:
            flags.append('pcsync')

        if self.flags & MODE_FLAG_NCSYNC:
            flags.append('ncsync')

        if self.flags & MODE_FLAG_HSKEW:
            flags.append('hskew')

        if self.flags & MODE_FLAG_BCAST:
            flags.append('bcast')

        if self.flags & MODE_FLAG_PIXMUX:
            flags.append('pixmux')

        if self.flags & MODE_FLAG_DBLCLK:
            flags.append('dblclk')

        if self.flags & MODE_FLAG_CLKDIV2:
            flags.append('clkdiv2')

        return flags

    def get_types(self):
        types = []

        if self.type & MODE_TYPE_BUILTIN:
            types.append('builtin')

        if self.type & MODE_TYPE_CLOCK_C:
            types.append('clock-c')

        if self.type & MODE_TYPE_CRTC_C:
            types.append('crtc-c')

        if self.type & MODE_TYPE_PREFERRED:
            types.append('preferred')

        if self.type & MODE_TYPE_DEFAULT:
            types.append('default')

        if self.type & MODE_TYPE_USERDEF:
            types.append('userdef')

        if self.type & MODE_TYPE_DRIVER:
            types.append('driver')

        return types

class Capability(enum.IntEnum):
    DUMB_BUFFER = 0x1
    VBLANK_HIGH_CRTC = 0x2
    DUMB_PREFERRED_DEPTH = 0x3
    DUMB_PREFER_SHADOW = 0x4
    PRIME = 0x05
    PRIME_IMPORT = 0x01
    PRIME_EXPORT = 0x02
    TIMESTAMP_MONOTONIC = 0x6
    ASYNC_PAGE_FLIP = 0x7
    CURSOR_WIDTH = 0x8
    CURSOR_HEIGHT = 0x9
    ADDFB2_MODIFIERS = 0x10
    PAGE_FLIP_TARGET = 0x11
    CRTC_IN_VBLANK_EVENT = 0x12
    SYNCOBJ = 0x13

class Prime(enum.IntFlag):
    IMPORT = 0x1
    EXPORT = 0x2

class ClientCapability(enum.IntEnum):
    STEREO_3D = 0x01
    UNIVERSAL_PLANES = 0x02
    ATOMIC = 0x03
    ASPECT_RATIO = 0x04
    WRITEBACK_CONNECTORS = 0x05

class capability(ctypes.Structure):
    _fields_ = [
        ('capability', ctypes.c_uint64),
        ('value', ctypes.c_uint64),
    ]

class prime_handle(ctypes.Structure):
    _fields_ = [
        ('handle', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('fd', ctypes.c_int32)
    ]

class mode_resources(ctypes.Structure):
    _fields_ = [
        ('fb_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('crtc_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('connector_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('encoder_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_fbs', ctypes.c_uint32),
        ('count_crtcs', ctypes.c_uint32),
        ('count_connectors', ctypes.c_uint32),
        ('count_encoders', ctypes.c_uint32),
        ('min_width', ctypes.c_uint32),
        ('max_width', ctypes.c_uint32),
        ('min_height', ctypes.c_uint32),
        ('max_height', ctypes.c_uint32)
    ]

class mode_get_encoder(ctypes.Structure):
    _fields_ = [
        ('encoder_id', ctypes.c_uint32),
        ('encoder_type', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('possible_crtcs', ctypes.c_uint32),
        ('possible_clones', ctypes.c_uint32)
    ]

MODE_CONNECTOR_Unknown = 0
MODE_CONNECTOR_VGA = 1
MODE_CONNECTOR_DVII = 2
MODE_CONNECTOR_DVID = 3
MODE_CONNECTOR_DVIA = 4
MODE_CONNECTOR_Composite = 5
MODE_CONNECTOR_SVIDEO = 6
MODE_CONNECTOR_LVDS = 7
MODE_CONNECTOR_Component = 8
MODE_CONNECTOR_9PinDIN = 9
MODE_CONNECTOR_DisplayPort = 10
MODE_CONNECTOR_HDMIA = 11
MODE_CONNECTOR_HDMIB = 12
MODE_CONNECTOR_TV = 13
MODE_CONNECTOR_eDP = 14
MODE_CONNECTOR_VIRTUAL = 15
MODE_CONNECTOR_DSI = 16
MODE_CONNECTOR_DPI = 17
MODE_CONNECTOR_WRITEBACK = 18

class mode_get_connector(ctypes.Structure):
    _fields_ = [
        ('encoders_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('modes_ptr', ctypes.POINTER(mode_info)),
        ('props_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('prop_values_ptr', ctypes.POINTER(ctypes.c_uint64)),
        ('count_modes', ctypes.c_uint32),
        ('count_props', ctypes.c_uint32),
        ('count_encoders', ctypes.c_uint32),
        ('encoder_id', ctypes.c_uint32),
        ('connector_id', ctypes.c_uint32),
        ('connector_type', ctypes.c_uint32),
        ('connector_type_id', ctypes.c_uint32),
        ('connection', ctypes.c_uint32),
        ('mm_width', ctypes.c_uint32),
        ('mm_height', ctypes.c_uint32),
        ('subpixel', ctypes.c_uint32),
        ('pad', ctypes.c_uint32),
    ]

class mode_create_dumb(ctypes.Structure):
    _fields_ = [
            ('height', ctypes.c_uint32),
            ('width', ctypes.c_uint32),
            ('bpp', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('handle', ctypes.c_uint32),
            ('pitch', ctypes.c_uint32),
            ('size', ctypes.c_uint64)
        ]

class mode_map_dumb(ctypes.Structure):
    _fields_ = [
            ('handle', ctypes.c_uint32),
            ('pad', ctypes.c_uint32),
            ('offset', ctypes.c_uint64)
        ]

class mode_destroy_dumb(ctypes.Structure):
    _fields_ = [
            ('handle', ctypes.c_uint32)
        ]

class mode_plane_resources(ctypes.Structure):
    _fields_ = [
        ('plane_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_planes', ctypes.c_uint32)
    ]

class mode_set_plane(ctypes.Structure):
    _fields_ = [
            ('plane_id', ctypes.c_uint32),
            ('crtc_id', ctypes.c_uint32),
            ('fb_id', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('crtc_x', ctypes.c_int32),
            ('crtc_y', ctypes.c_int32),
            ('crtc_w', ctypes.c_uint32),
            ('crtc_h', ctypes.c_uint32),
            ('src_x', ctypes.c_uint32),
            ('src_y', ctypes.c_uint32),
            ('src_h', ctypes.c_uint32),
            ('src_w', ctypes.c_uint32)
        ]

class mode_get_plane(ctypes.Structure):
    _fields_ = [
        ('plane_id', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('fb_id', ctypes.c_uint32),
        ('possible_crtcs', ctypes.c_uint32),
        ('gamma_size', ctypes.c_uint32),
        ('count_format_types', ctypes.c_uint32),
        ('format_type_ptr', ctypes.POINTER(ctypes.c_uint32))
    ]

class mode_fb_cmd2(ctypes.Structure):
    _fields_ = [
            ('fb_id', ctypes.c_uint32),
            ('width', ctypes.c_uint32),
            ('height', ctypes.c_uint32),
            ('pixel_format', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('handles', ctypes.c_uint32 * 4),
            ('pitches', ctypes.c_uint32 * 4),
            ('offsets', ctypes.c_uint32 * 4),
            ('modifier', ctypes.c_uint32 * 4)
        ]

class mode_property_enum(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_uint64),
        ('name', (32 * ctypes.c_char))
    ]

    def __str__(self):
        return '%u: %s' % (self.value, self.name.decode('utf-8'))

class mode_get_property(ctypes.Structure):
    _fields_ = [
        ('values_ptr', ctypes.c_uint64),
        ('enum_blob_ptr', ctypes.c_uint64),
        ('prop_id', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('name', (32 * ctypes.c_char)),
        ('count_values', ctypes.c_uint32),
        ('count_enum_blobs', ctypes.c_uint32)
    ]

MODE_OBJECT_CRTC = 0xcccccccc
MODE_OBJECT_CONNECTOR = 0xc0c0c0c0
MODE_OBJECT_ENCODER = 0xe0e0e0e0
MODE_OBJECT_MODE = 0xdededede
MODE_OBJECT_PROPERTY = 0xb0b0b0b0
MODE_OBJECT_FB = 0xfbfbfbfb
MODE_OBJECT_BLOB = 0xbbbbbbbb
MODE_OBJECT_PLANE = 0xeeeeeeee
MODE_OBJECT_ANY = 0x00000000

class mode_obj_get_properties(ctypes.Structure):
    _fields_ = [
        ('props_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('prop_values_ptr', ctypes.POINTER(ctypes.c_uint64)),
        ('count_props', ctypes.c_uint32),
        ('obj_id', ctypes.c_uint32),
        ('obj_type', ctypes.c_uint32)
    ]

class mode_get_blob(ctypes.Structure):
    _fields_ = [
        ('blob_id', ctypes.c_uint32),
        ('length', ctypes.c_uint32),
        ('data', ctypes.POINTER(ctypes.c_byte))
    ]

class mode_crtc(ctypes.Structure):
    _fields_ = [
        ('set_connectors_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_connectors', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('fb_id', ctypes.c_uint32),
        ('x', ctypes.c_uint32),
        ('y', ctypes.c_uint32),
        ('gamma_size', ctypes.c_uint32),
        ('mode_valid', ctypes.c_uint32),
        ('mode', mode_info)
    ]

IOCTL_BASE = ord('d')
COMMAND_BASE = 0x40

def IO(nr):
    return _IO(IOCTL_BASE, nr)

def IOWR(nr, type):
    return _IOWR(IOCTL_BASE, nr, ctypes.sizeof(type))

def IOW(nr, type):
    return _IOW(IOCTL_BASE, nr, ctypes.sizeof(type))

IOCTL_VERSION = IOWR(0x00, version)
IOCTL_GEM_CLOSE = IOW(0x09, gem_close)
IOCTL_GET_CAP = IOWR(0x0c, capability)
IOCTL_SET_CLIENT_CAP = IOW(0x0d, capability)
IOCTL_SET_MASTER = IO(0x1e)
IOCTL_DROP_MASTER = IO(0x1f)
IOCTL_PRIME_HANDLE_TO_FD = IOWR(0x2d, prime_handle)
IOCTL_PRIME_FD_TO_HANDLE = IOWR(0x2e, prime_handle)
IOCTL_MODE_GETRESOURCES = IOWR(0xa0, mode_resources)
IOCTL_MODE_GETCRTC = IOWR(0xa1, mode_crtc)
IOCTL_MODE_GETENCODER = IOWR(0xa6, mode_get_encoder)
IOCTL_MODE_GETCONNECTOR = IOWR(0xa7, mode_get_connector)
IOCTL_MODE_GETPROPERTY = IOWR(0xaa, mode_get_property)
IOCTL_MODE_GETPROPBLOB = IOWR(0xac, mode_get_blob)
IOCTL_MODE_CREATE_DUMB = IOWR(0xb2, mode_create_dumb)
IOCTL_MODE_MAP_DUMB = IOWR(0xb3, mode_map_dumb)
IOCTL_MODE_DESTROY_DUMB = IOWR(0xb4, mode_destroy_dumb)
IOCTL_MODE_GETPLANERESOURCES = IOWR(0xb5, mode_plane_resources)
IOCTL_MODE_GETPLANE = IOWR(0xb6, mode_get_plane)
IOCTL_MODE_SETPLANE = IOWR(0xb7, mode_set_plane)
IOCTL_MODE_ADDFB2 = IOWR(0xb8, mode_fb_cmd2)
IOCTL_MODE_OBJ_GETPROPERTIES = IOWR(0xb9, mode_obj_get_properties)

def get_flags(value):
    flags = []

    if value & MODE_PROP_PENDING:
        flags.append('pending')

    if value & MODE_PROP_RANGE:
        flags.append('range')

    if value & MODE_PROP_IMMUTABLE:
        flags.append('immutable')

    if value & MODE_PROP_ENUM:
        flags.append('enum')

    if value & MODE_PROP_BLOB:
        flags.append('blob')

    if value & MODE_PROP_BITMASK:
        flags.append('bitmask')

    return flags

class Version:
    def __init__(self, version):
        self.major = version.version_major
        self.minor = version.version_minor
        self.patch = version.version_patchlevel
        self.name = version.name.decode()
        self.date = version.date.decode()
        self.desc = version.desc.decode()

class Component:
    def __init__(self, shift, width):
        self.shift = shift
        self.width = width

class RGBA:
    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

class Format(enum.IntEnum):
    def __new__(cls, a, b, c, d, num_planes, cpp, hsub, vsub, components = None):
        value = (ord(d) << 24) | (ord(c) << 16) | (ord(b) << 8) | ord(a)
        fourcc = a + b + c + d

        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.fourcc = fourcc.strip()
        obj.num_planes = num_planes
        obj.cpp = cpp
        obj.hsub = hsub
        obj.vsub = vsub
        obj.components = components

        return obj

    #def __repr__(self):
    #    return '<%s: %#08x>' % (self.name, self.value)

    #def __str__(self):
    #    return '%s' % self.fourcc

    @classmethod
    def _missing_(cls, value):
        d = chr((value >> 24) & 0xff)
        c = chr((value >> 16) & 0xff)
        b = chr((value >>  8) & 0xff)
        a = chr((value >>  0) & 0xff)

        print('missing format %c%c%c%c' % (a, b, c, d))

        return None

    def pixel(self, red, green, blue, alpha):
        if isinstance(self.components, RGBA):
            r = self.components.red
            g = self.components.green
            b = self.components.blue
            a = self.components.alpha

            value = 0

            for c, v in zip([r, g, b, a], [red, green, blue, alpha]):
                mask = (1 << c.width) - 1
                value |= int(v * mask) << c.shift

            return value.to_bytes(self.cpp[0], byteorder = 'little')

        raise Exception()

    C8       = ('C', '8', ' ', ' ', 1, [1, 0, 0], 1, 1)
    ABGR4444 = ('A', 'B', '1', '2', 1, [2, 0, 0], 1, 1, RGBA(Component( 0, 4), Component(4, 4), Component( 8, 4), Component(12, 4)))
    XRGB1555 = ('X', 'R', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component(10, 5), Component(5, 5), Component( 0, 5), Component(15, 1)))
    XBGR1555 = ('X', 'B', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component( 0, 5), Component(5, 5), Component(10, 5), Component(15, 1)))
    RGBX5551 = ('R', 'X', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component(11, 5), Component(6, 5), Component( 1, 5), Component( 0, 1)))
    BGRX5551 = ('B', 'X', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component( 1, 5), Component(6, 5), Component(11, 5), Component( 0, 1)))
    ARGB1555 = ('A', 'R', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component(10, 5), Component(5, 5), Component( 0, 5), Component(15, 1)))
    ABGR1555 = ('A', 'B', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component( 0, 5), Component(5, 5), Component(10, 5), Component(15, 1)))
    RGBA5551 = ('R', 'A', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component(11, 5), Component(6, 5), Component( 1, 5), Component( 0, 1)))
    BGRA5551 = ('B', 'A', '1', '5', 1, [2, 0, 0], 1, 1, RGBA(Component( 1, 5), Component(6, 5), Component(11, 5), Component( 0, 1)))
    RGB565   = ('R', 'G', '1', '6', 1, [2, 0, 0], 1, 1, RGBA(Component(11, 5), Component(5, 6), Component( 0, 5), Component( 0, 0)))
    BGR565   = ('B', 'G', '1', '6', 1, [2, 0, 0], 1, 1, RGBA(Component( 0, 5), Component(5, 6), Component(11, 5), Component( 0, 0)))
    XRGB8888 = ('X', 'R', '2', '4', 1, [4, 0, 0], 1, 1, RGBA(Component(16, 8), Component(8, 8), Component( 0, 8), Component(24, 8)))
    XBGR8888 = ('X', 'B', '2', '4', 1, [4, 0, 0], 1, 1, RGBA(Component( 0, 8), Component(8, 8), Component(16, 8), Component(24, 8)))
    ARGB8888 = ('A', 'R', '2', '4', 1, [4, 0, 0], 1, 1, RGBA(Component(16, 8), Component(8, 8), Component( 0, 8), Component(24, 8)))
    ABGR8888 = ('A', 'B', '2', '4', 1, [4, 0, 0], 1, 1, RGBA(Component( 0, 8), Component(8, 8), Component(16, 8), Component(24, 8)))
    YUYV     = ('Y', 'U', 'Y', 'V', 3, [1, 1, 1], 2, 2)
    UYVY     = ('U', 'Y', 'V', 'Y', 3, [1, 1, 1], 2, 2)
    YUV420   = ('Y', 'U', '1', '2', 3, [1, 1, 1], 2, 2)
    YUV422   = ('Y', 'U', '1', '6', 3, [1, 1, 1], 2, 1)

class Vendor(enum.IntEnum):
    NONE = 0
    INTEL = 1
    AMD = 2
    NVIDIA = 3
    SAMSUNG = 4
    QCOM = 5
    VIVANTE = 6
    BROADCOM = 7
    ARM = 8

class Modifier(enum.IntEnum):
    def __new__(cls, vendor, code):
        value = ((vendor & 0xff) << 56) | (code & 0xffffffffffffff)
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    INVALID = (Vendor.NONE, 0xffffffffffffff)
    LINEAR = (Vendor.NONE, 0)

class Mode:
    def __init__(self, mode):
        self.name = mode.name.encode('UTF-8')

MODE_PROP_PENDING = 1 << 0
MODE_PROP_RANGE = 1 << 1
MODE_PROP_IMMUTABLE = 1 << 2
MODE_PROP_ENUM = 1 << 3
MODE_PROP_BLOB = 1 << 4
MODE_PROP_BITMASK = 1 << 5

MODE_PROP_EXTENDED_TYPE = 0x0000ffc0

def MODE_PROP_TYPE(prop_type):
    return prop_type << 6

MODE_PROP_OBJECT = MODE_PROP_TYPE(1)
MODE_PROP_SIGNED_RANGE = MODE_PROP_TYPE(2)

MODE_PROP_ATOMIC = 0x80000000

class Blob:
    def __init__(self, blob_id, data):
        self.id = blob_id
        self.data = data

    def __str__(self):
        return '%u, %u bytes' % (self.id, len(self.data))

class Property:
    def __init__(self, prop_id, name, flags):
        self.id = prop_id
        self.name = name
        self.flags = flags

    @property
    def immutable(self):
        return 'immutable' in self.flags

class PropertyPending(Property):
    def __init__(self, prop_id, name, flags):
        super().__init__(prop_id, name, flags)

class PropertyRange(Property):
    def __init__(self, prop_id, name, flags, minimum, maximum, value):
        super().__init__(prop_id, name, flags)

        self.min = minimum
        self.max = maximum
        self.value = value

    def __str__(self):
        return '%u: %s (range: %d < %d < %d)' % (self.id, self.name, self.min, self.value, self.max)

class PropertyEnum(Property):
    def __init__(self, prop_id, name, flags, enums, value):
        super().__init__(prop_id, name, flags)

        self.type = enum.Enum(name, enums)
        self.value = self.type(value)

    def __str__(self):
        return '%u: %s (enum: %s)' % (self.id, self.name, self.type)

class PropertyBlob(Property):
    def __init__(self, prop_id, name, flags, blob):
        super().__init__(prop_id, name, flags)

        self.blob = blob

    def __str__(self):
        return '%u: %s (blob: %s)' % (self.id, self.name, self.blob)

class PropertyBitmask(Property):
    pass

class PropertyObject(Property):
    pass

    def __init__(self, device, prop_id, value):
        self.device = device
        self.id = prop_id
        self.value = value
        self.blob = None

        self.name = args.name.decode('utf-8')

    def __str__(self):
        return '%u: %s -> %u' % (self.id, self.name, self.value)

MODE_CONNECTED = 1
MODE_DISCONNECTED = 2
MODE_UNKNOWNCONNECTION = 3

class Framebuffer:
    def __init__(self, device, id):
        self.device = device
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class CRTC:
    def __init__(self, device, index, crtc_id):
        self.device = device
        self.index = index
        self.id = crtc_id

        args = mode_crtc()
        args.crtc_id = self.id

        device.ioctl(IOCTL_MODE_GETCRTC, args)

        if args.mode_valid:
            self.mode = args.mode
        else:
            self.mode = None

    def __repr__(self):
        return '%u' % self.id

class Connector:
    class Status(enum.IntEnum):
        CONNECTED = 1
        DISCONNECTED = 2
        UNKNOWN = 3

    class Type(enum.IntEnum):
        def __new__(cls, value, name):
            obj = int.__new__(cls, value)
            obj._value_ = value
            obj._name_ = name
            return obj

        UNKNOWN = (0, 'unknown')
        VGA = (1, 'VGA')
        DVII = (2, 'DVI-I')
        DVID = (3, 'DVI-D')
        DVIA = (4, 'DVI-A')
        COMPOSITE = (5, 'composite')
        SVIDEO = (6, 's-video')
        LVDS = (7, 'LVDS')
        COMPONENT = (8, 'component')
        DIN_9PIN = (9, '9-pin DIN')
        DISPLAYPORT = (10, 'DP')
        HDMIA = (11, 'HDMI-A')
        HDMIB = (12, 'HDMI-B')
        TV = (13, 'TV')
        eDP = (14, 'eDP')
        VIRTUAL = (15, 'Virtual')
        DSI = (16, 'DSI')
        DPI = (17, 'DPI')
        WRITEBACK = (18, 'Writeback')
        SPI = (19, 'SPI')
        USB = (20, 'USB')

    def __init__(self, device, connector_id):
        self.device = device
        self.id = connector_id
        self.encoder = None

        self.encoders = []
        self.modes = []
        self.properties = []

        args = mode_get_connector()
        args.connector_id = self.id

        device.ioctl(IOCTL_MODE_GETCONNECTOR, args)

        if args.count_encoders > 0:
            encoders = (ctypes.c_uint32 * args.count_encoders)()
            args.encoders_ptr = encoders

        if args.count_modes > 0:
            modes = (mode_info * args.count_modes)()
            args.modes_ptr = modes

        if args.count_props > 0:
            props = (ctypes.c_uint32 * args.count_props)()
            prop_values = (ctypes.c_uint64 * args.count_props)()

            args.props_ptr = props
            args.prop_values_ptr = prop_values

        device.ioctl(IOCTL_MODE_GETCONNECTOR, args)

        self.name = '%s-%u' % (Connector.Type(args.connector_type),
                               args.connector_type_id)
        self.status = Connector.Status(args.connection)
        self.width = args.mm_width
        self.height = args.mm_height

        if args.count_encoders > 0:
            for encoder_id in encoders:
                for encoder in device.encoders:
                    if encoder.id == encoder_id:
                        self.encoders.append(encoder)
                        break
                else:
                    raise NotFound('no encoder with ID %u' % encoder_id)

        for encoder in self.encoders:
            if encoder.id == args.encoder_id:
                self.encoder = encoder

        if args.count_modes > 0:
            for mode in modes:
                self.modes.append(mode)

        if args.count_props > 0:
            for prop_id, value in zip(props, prop_values):
                prop = device.get_property(prop_id, value)
                self.properties.append(prop)

    def __str__(self):
        return '%u: %s (%ux%u mm, %s)' % (self.id, self.name, self.width,
                                       self.height, self.status)

    def __repr__(self):
        return '%u' % self.id

MODE_ENCODER_NONE = 0
MODE_ENCODER_DAC = 1
MODE_ENCODER_TMDS = 2
MODE_ENCODER_LVDS = 3
MODE_ENCODER_TVDAC = 4
MODE_ENCODER_VIRTUAL = 5
MODE_ENCODER_DSI = 6
MODE_ENCODER_DPMST = 7
MODE_ENCODER_DPI = 8

class Encoder:
    types = {
        MODE_ENCODER_NONE: 'NONE',
        MODE_ENCODER_DAC: 'DAC',
        MODE_ENCODER_TMDS: 'TMDS',
        MODE_ENCODER_LVDS: 'LVDS',
        MODE_ENCODER_TVDAC: 'TVDAC',
        MODE_ENCODER_VIRTUAL: 'VIRTUAL',
        MODE_ENCODER_DSI: 'DSI',
        MODE_ENCODER_DPMST: 'DPMST',
        MODE_ENCODER_DPI: 'DPI',
    }

    def __init__(self, device, index, id):
        self.device = device
        self.index = index
        self.id = id

        args = mode_get_encoder()
        args.encoder_id = id

        device.ioctl(IOCTL_MODE_GETENCODER, args)

        self.type = args.encoder_type
        self.possible_crtcs = []
        # need to resolve these later
        self.possible_clones = args.possible_clones

        for crtc in device.crtcs:
            if crtc.id == args.crtc_id:
                self.crtc = crtc
                break
        else:
            self.crtc = None

        for bit in set_bits(args.possible_crtcs, 32):
            for crtc in device.crtcs:
                if crtc.index == bit:
                    self.possible_crtcs.append(crtc)

        if args.encoder_type in Encoder.types:
            self.name = '%s' % Encoder.types[self.type]
        else:
            self.name = 'UNKNOWN'

    def __str__(self):
        return '%u: %s' % (self.id, self.name)

    def __repr__(self):
        return '%u' % self.id

class Plane:
    def __init__(self, device, id):
        self.device = device
        self.id = id
        self.crtcs = []
        self.formats = []
        self.properties = []

        args = mode_get_plane()
        args.plane_id = id

        device.ioctl(IOCTL_MODE_GETPLANE, args)

        if args.count_format_types > 0:
            formats = (ctypes.c_uint32 * args.count_format_types)()
            args.format_type_ptr = formats

        device.ioctl(IOCTL_MODE_GETPLANE, args)

        for bit in set_bits(args.possible_crtcs, 32):
            for crtc in device.crtcs:
                if crtc.index == bit:
                    self.crtcs.append(crtc)

        for crtc in self.crtcs:
            if crtc.id == args.crtc_id:
                self.crtc = crtc
                break
        else:
            self.crtc = None

        for fmt in formats:
            fmt = Format(fmt)
            self.formats.append(fmt)

        args = mode_obj_get_properties()
        args.obj_type = MODE_OBJECT_PLANE
        args.obj_id = id

        device.ioctl(IOCTL_MODE_OBJ_GETPROPERTIES, args)

        if args.count_props > 0:
            props = (ctypes.c_uint32 * args.count_props)()
            args.props_ptr = props

            values = (ctypes.c_uint64 * args.count_props)()
            args.prop_values_ptr = values

        device.ioctl(IOCTL_MODE_OBJ_GETPROPERTIES, args)

        if args.count_props > 0:
            for prop, value in zip(props, values):
                prop = device.get_property(prop, value)
                self.properties.append(prop)

    def __repr__(self):
        return '%u' % self.id

    def set(self, crtc, fb, flags, crtc_x, crtc_y, crtc_w, crtc_h, src_x, src_y, src_w, src_h):
        args = mode_set_plane()
        args.plane_id = self.id
        args.crtc_id = crtc.id
        args.fb_id = fb.id
        args.flags = flags

        args.crtc_x = crtc_x
        args.crtc_y = crtc_y
        args.crtc_w = crtc_w
        args.crtc_h = crtc_h

        args.src_x = src_x << 16
        args.src_y = src_y << 16
        args.src_h = src_h << 16
        args.src_w = src_w << 16

        self.device.ioctl(IOCTL_MODE_SETPLANE, args)

class GEM:
    def __init__(self, device, handle, size):
        self.device = device
        self.handle = handle
        self.size = size

class DumbBuffer(GEM):
    def __init__(self, device, width, height, handle, pitch, size):
        super().__init__(device, handle, size)
        self.width = width
        self.height = height
        self.pitch = pitch
        self.mmap = None

    def map(self):
        if not self.mmap:
            args = mode_map_dumb()
            args.handle = self.handle

            self.device.ioctl(IOCTL_MODE_MAP_DUMB, args)

            self.mmap = self.device.mmap(args.offset, self.size)

        return self.mmap

    def __del__(self):
        if self.mmap:
            self.mmap.close()

        args = mode_destroy_dumb()
        args.handle = self.handle

        self.device.ioctl(IOCTL_MODE_DESTROY_DUMB, args)

    def __setitem__(self, key, value):
        mmap = self.map()

        x, y = key

        offset = y * self.pitch + x * len(value)
        mmap[offset:offset + len(value)] = value

class Resolution:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Device:
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR)
        self.path = path

    def close(self):
        os.close(self.fd)

    def ioctl(self, nr, args):
        return fcntl.ioctl(self.fd, nr, args)

    def mmap(self, offset, length, flags = mmap.MAP_SHARED, prot = mmap.PROT_WRITE | mmap.PROT_READ, access = mmap.ACCESS_DEFAULT):
        return mmap.mmap(self.fd, length, flags, prot, access, offset)

    def version(self):
        v = version()

        self.ioctl(IOCTL_VERSION, v)

        name = bytes(v.name_len)
        date = bytes(v.date_len)
        desc = bytes(v.desc_len)

        v.name = ctypes.c_char_p(name)
        v.date = ctypes.c_char_p(date)
        v.desc = ctypes.c_char_p(desc)

        self.ioctl(IOCTL_VERSION, v)

        return Version(v)

    def get_capability(self, cap):
        args = capability()
        args.capability = cap

        self.ioctl(IOCTL_GET_CAP, args)

        if cap == Capability.DUMB_BUFFER or \
           cap == Capability.VBLANK_HIGH_CRTC or \
           cap == Capability.DUMB_PREFER_SHADOW or \
           cap == Capability.TIMESTAMP_MONOTONIC or \
           cap == Capability.ASYNC_PAGE_FLIP or \
           cap == Capability.ADDFB2_MODIFIERS or \
           cap == Capability.PAGE_FLIP_TARGET or \
           cap == Capability.CRTC_IN_VBLANK_EVENT or \
           cap == Capability.SYNCOBJ:
            return args.value != 0

        return args.value

    def set_capability(self, cap, value):
        args = capability()
        args.capability = cap
        args.value = value

        self.ioctl(IOCTL_SET_CLIENT_CAP, args)

    def set_master(self):
        self.ioctl(IOCTL_SET_MASTER, 0)

    def drop_master(self):
        self.ioctl(IOCTL_DROP_MASTER, 0)

    def prime_handle_to_fd(self, handle, flags):
        args = prime_handle()
        args.fd = -1
        args.handle = handle
        args.flags = flags

        self.ioctl(IOCTL_PRIME_HANDLE_TO_FD, args)

        return args.fd

    def prime_fd_to_handle(self, fd):
        args = prime_handle()
        args.fd = fd

        self.ioctl(IOCTL_PRIME_FD_TO_HANDLE, args)

        return args.handle

    def get_property(self, prop_id, value):
        args = mode_get_property()
        args.prop_id = prop_id

        self.ioctl(IOCTL_MODE_GETPROPERTY, args)

        name = args.name.decode('utf-8')
        flags = get_flags(args.flags)
        prop = None

        if args.count_values > 0:
            values = (ctypes.c_uint64 * args.count_values)()
            args.values_ptr = ctypes.addressof(values)

        if args.count_enum_blobs > 0:
            if args.flags & (MODE_PROP_ENUM | MODE_PROP_BITMASK):
                blobs = (mode_property_enum * args.count_enum_blobs)()
                args.enum_blob_ptr = ctypes.addressof(blobs)

            if args.flags & MODE_PROP_BLOB:
                blobs = (ctypes.c_uint32 * args.count_enum_blobs)()
                args.enum_blob_ptr = ctypes.addressof(blobs)

                values = (ctypes.c_uint32 * args.count_enum_blobs)()
                args.values_ptr = ctypes.addressof(values)

        self.ioctl(IOCTL_MODE_GETPROPERTY, args)

        if 0:
            print('property: value %s' % value)
            print('  values_ptr:', args.values_ptr)
            print('  enum_blob_ptr:', args.enum_blob_ptr)
            print('  prop_id:', args.prop_id)
            print('  flags:', args.flags)
            print('  name:', args.name)
            print('  count_values:', args.count_values)
            print('  count_enum_blobs:', args.count_enum_blobs)

        if args.flags & MODE_PROP_PENDING:
            raise NotImplemented('unable to parse pending properties')

        if args.flags & MODE_PROP_RANGE:
            return PropertyRange(prop_id, name, flags, values[0], values[1], value)

        if args.flags & MODE_PROP_ENUM:
            enums = {}

            for blob in blobs:
                enum = blob.name.decode('utf-8')
                enums[enum] = blob.value

            return PropertyEnum(prop_id, name, flags, enums, value)

        if args.flags & MODE_PROP_BLOB:
            if args.count_enum_blobs > 0:
                raise NotImplemented('unable to parse %u enum blobs' %
                                        args.count_enum_blobs)
            else:
                if value > 0:
                    blob = self.get_blob(value)
                else:
                    blob = None

            return PropertyBlob(prop_id, name, flags, blob)

        if args.flags & MODE_PROP_BITMASK:
            raise NotImplemented('unable to parse bitmask properties')

        prop_type = args.flags & MODE_PROP_EXTENDED_TYPE

        if prop_type == MODE_PROP_OBJECT:
            raise NotImplemented('unable to parse object properties')

        if prop_type == MODE_PROP_SIGNED_RANGE:
            raise NotImplemented('unable to parse signed range properties')

        if not prop:
            if args.count_values > 0:
                print('  values: %u' % args.count_values)

                for value in values:
                    print('    %u' % value)

            if args.count_enum_blobs > 0:
                print('  enum blobs: %u' % args.count_enum_blobs)

                for blob in blobs:
                    print('    %s' % blob)

            if args.flags & MODE_PROP_ENUM:
                self.values = {}

                if args.count_enum_blobs > 0:
                    for blob in blobs:
                        self.values[blob.name] = blob.value

        return prop

    def get_blob(self, blob_id):
        args = mode_get_blob()
        args.blob_id = blob_id
        data = None

        self.ioctl(IOCTL_MODE_GETPROPBLOB, args)

        #print('  blob: %u' % blob_id)
        #print('    length: %u bytes' % args.length)

        if args.length > 0:
            data = (ctypes.c_byte * args.length)()
            args.data = data

            self.ioctl(IOCTL_MODE_GETPROPBLOB, args)

            data = bytes(data)

        #print('    data:\n     ', end = '')
        #count = 0

        #for byte in self.data:
        #    if count >= 16:
        #        print('\n     ', end = '')
        #        count = 0

        #    print(' %02x' % byte, end = '')
        #    count += 1

        #print()

        return Blob(blob_id, data)

    def get_resources(self):
        args = mode_resources()

        self.ioctl(IOCTL_MODE_GETRESOURCES, args)

        self.minimum_resolution = Resolution(args.min_width, args.min_height)
        self.maximum_resolution = Resolution(args.max_width, args.max_height)

        if args.count_fbs > 0:
            fbs = (ctypes.c_uint32 * args.count_fbs)()
            args.fb_id_ptr = fbs

        if args.count_crtcs > 0:
            crtcs = (ctypes.c_uint32 * args.count_crtcs)()
            args.crtc_id_ptr = crtcs

        if args.count_connectors > 0:
            connectors = (ctypes.c_uint32 * args.count_connectors)()
            args.connector_id_ptr = connectors

        if args.count_encoders > 0:
            encoders = (ctypes.c_uint32 * args.count_encoders)()
            args.encoder_id_ptr = encoders

        self.ioctl(IOCTL_MODE_GETRESOURCES, args)

        self.framebuffers = []
        self.crtcs = []
        self.connectors = []
        self.encoders = []
        self.planes = []

        if args.count_fbs > 0:
            for fb in fbs:
                fb = Framebuffer(self, fb)
                self.framebuffers.append(fb)

        if args.count_crtcs > 0:
            index = 0

            for crtc in crtcs:
                crtc = CRTC(self, index, crtc)
                self.crtcs.append(crtc)
                index = index + 1

        if args.count_encoders > 0:
            index = 0

            for encoder in encoders:
                encoder = Encoder(self, index, encoder)
                self.encoders.append(encoder)
                index = index + 1

            # resolve possible clones
            for encoder in self.encoders:
                possible_clones = []

                for bit in set_bits(encoder.possible_clones, 32):
                    for clone in self.encoders:
                        if clone.index == bit:
                            possible_clones.append(clone)

                encoder.possible_clones = possible_clones

        if args.count_connectors > 0:
            for connector in connectors:
                connector = Connector(self, connector)
                self.connectors.append(connector)

        # retrieve plane information
        args = mode_plane_resources()

        self.ioctl(IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            planes = (ctypes.c_uint32 * args.count_planes)()
            args.plane_id_ptr = planes

        self.ioctl(IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            for plane in planes:
                plane = Plane(self, plane)
                self.planes.append(plane)

    def create_dumb(self, width, height, bpp, flags):
        args = mode_create_dumb()
        args.width = width
        args.height = height
        args.bpp = bpp
        args.flags = flags

        self.ioctl(IOCTL_MODE_CREATE_DUMB, args)

        return DumbBuffer(self, width, height, args.handle, args.pitch, args.size)

    def add_framebuffer(self, width, height, pixel_format, flags, objects,
                        pitches, offsets, modifiers):
        args = mode_fb_cmd2()
        args.width = width
        args.height = height
        args.pixel_format = pixel_format
        args.flags = flags

        if not isinstance(objects, list):
            objects = [ objects ]

        if not isinstance(pitches, list):
            pitches = [ pitches ]

        if not isinstance(offsets, list):
            offsets = [ offsets ]

        if not isinstance(modifiers, list):
            modifiers = [ modifiers ]

        elements = zip(objects, pitches, offsets, modifiers)

        for i, (bo, pitch, offset, modifier) in enumerate(elements):
            args.handles[i] = bo.handle
            args.pitches[i] = pitch
            args.offsets[i] = offset
            args.modifier[i] = modifier

        self.ioctl(IOCTL_MODE_ADDFB2, args)

        return Framebuffer(self, args.fb_id)

class DeviceNode:
    def __init__(self, path):
        self.path = path
        self.fd = None

    def __del__(self):
        if self.fd:
            os.close(self.fd)

        self.fd = None

    def open(self):
        return Device(self.path)

class CardDevice(DeviceNode):
    def __init__(self, path):
        super().__init__(path)

class RenderNode(DeviceNode):
    def __init__(self, path):
        super().__init__(path)

def devices():
    directory = os.path.join(os.path.sep, 'dev', 'dri')
    result = []

    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        device = None

        if name.startswith('card'):
            device = CardDevice(path)

        if name.startswith('render'):
            device = RenderNode(path)

        if device:
            result.append(device)

    return result
