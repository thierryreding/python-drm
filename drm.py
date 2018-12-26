#!/usr/bin/python3

import ctypes, fcntl, os, os.path

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

def IOC(dir, type, nr, size):
    return dir << IOC_DIR_SHIFT | size << IOC_SIZE_SHIFT | type << IOC_TYPE_SHIFT | nr << IOC_NR_SHIFT

def IO(type, nr):
    return IOC(IOC_NONE, type, nr, 0)

def IOW(type, nr, size):
    return IOC(IOC_WRITE, type, nr, size)

def IOR(type, nr, size):
    return IOC(IOC_READ, type, nr, size)

def IOWR(type, nr, size):
    return IOC(IOC_READ | IOC_WRITE, type, nr, size)

class Error(Exception):
    pass

class DeprecatedError(Error):
    pass

class drm_version(ctypes.Structure):
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

DRM_MODE_FLAG_PHSYNC = 1 << 0
DRM_MODE_FLAG_NHSYNC = 1 << 1
DRM_MODE_FLAG_PVSYNC = 1 << 2
DRM_MODE_FLAG_NVSYNC = 1 << 3
DRM_MODE_FLAG_INTERLACE = 1 << 4
DRM_MODE_FLAG_DBLSCAN = 1 << 5
DRM_MODE_FLAG_CSYNC = 1 << 6
DRM_MODE_FLAG_PCSYNC = 1 << 7
DRM_MODE_FLAG_NCSYNC = 1 << 8
DRM_MODE_FLAG_HSKEW = 1 << 9
DRM_MODE_FLAG_BCAST = 1 << 10
DRM_MODE_FLAG_PIXMUX = 1 << 11
DRM_MODE_FLAG_DBLCLK = 1 << 12
DRM_MODE_FLAG_CLKDIV2 = 1 << 13

DRM_MODE_TYPE_BUILTIN = 1 << 0
DRM_MODE_TYPE_CLOCK_C = 1 << 1 | DRM_MODE_TYPE_BUILTIN
DRM_MODE_TYPE_CRTC_C = 1 << 2 | DRM_MODE_TYPE_BUILTIN
DRM_MODE_TYPE_PREFERRED = 1 << 3
DRM_MODE_TYPE_DEFAULT = 1 << 4
DRM_MODE_TYPE_USERDEF = 1 << 5
DRM_MODE_TYPE_DRIVER = 1 << 6

class drm_mode_info(ctypes.Structure):
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

        if self.flags & DRM_MODE_FLAG_PHSYNC:
            flags.append('phsync')

        if self.flags & DRM_MODE_FLAG_NHSYNC:
            flags.append('nhsync')

        if self.flags & DRM_MODE_FLAG_PVSYNC:
            flags.append('pvsync')

        if self.flags & DRM_MODE_FLAG_NVSYNC:
            flags.append('nvsync')

        if self.flags & DRM_MODE_FLAG_INTERLACE:
            flags.append('interlace')

        if self.flags & DRM_MODE_FLAG_DBLSCAN:
            flags.append('dblscan')

        if self.flags & DRM_MODE_FLAG_CSYNC:
            flags.append('csync')

        if self.flags & DRM_MODE_FLAG_PCSYNC:
            flags.append('pcsync')

        if self.flags & DRM_MODE_FLAG_NCSYNC:
            flags.append('ncsync')

        if self.flags & DRM_MODE_FLAG_HSKEW:
            flags.append('hskew')

        if self.flags & DRM_MODE_FLAG_BCAST:
            flags.append('bcast')

        if self.flags & DRM_MODE_FLAG_PIXMUX:
            flags.append('pixmux')

        if self.flags & DRM_MODE_FLAG_DBLCLK:
            flags.append('dblclk')

        if self.flags & DRM_MODE_FLAG_CLKDIV2:
            flags.append('clkdiv2')

        return flags

    def get_types(self):
        types = []

        if self.type & DRM_MODE_TYPE_BUILTIN:
            types.append('builtin')

        if self.type & DRM_MODE_TYPE_CLOCK_C:
            types.append('clock-c')

        if self.type & DRM_MODE_TYPE_CRTC_C:
            types.append('crtc-c')

        if self.type & DRM_MODE_TYPE_PREFERRED:
            types.append('preferred')

        if self.type & DRM_MODE_TYPE_DEFAULT:
            types.append('default')

        if self.type & DRM_MODE_TYPE_USERDEF:
            types.append('userdef')

        if self.type & DRM_MODE_TYPE_DRIVER:
            types.append('driver')

        return types

DRM_CAP_DUMB_BUFFER = 0x1
DRM_CAP_VBLANK_HIGH_CRTC = 0x2
DRM_CAP_DUMB_PREFERRED_DEPTH = 0x3
DRM_CAP_DUMB_PREFER_SHADOW = 0x4
DRM_CAP_PRIME = 0x05
DRM_CAP_PRIME_IMPORT = 0x01
DRM_CAP_PRIME_EXPORT = 0x02
DRM_CAP_TIMESTAMP_MONOTONIC = 0x6
DRM_CAP_ASYNC_PAGE_FLIP = 0x7
DRM_CAP_CURSOR_WIDTH = 0x8
DRM_CAP_CURSOR_HEIGHT = 0x9
DRM_CAP_ADDFB2_MODIFIERS = 0x10
DRM_CAP_PAGE_FLIP_TARGET = 0x11
DRM_CAP_CRTC_IN_VBLANK_EVENT = 0x12
DRM_CAP_SYNCOBJ = 0x13

DRM_CLIENT_CAP_STEREO_3D = 0x01
DRM_CLIENT_CAP_UNIVERSAL_PLANES = 0x02
DRM_CLIENT_CAP_ATOMIC = 0x03
DRM_CLIENT_CAP_ASPECT_RATIO = 0x04
DRM_CLIENT_CAP_WRITEBACK_CONNECTORS = 0x05

class drm_capability(ctypes.Structure):
    _fields_ = [
        ('capability', ctypes.c_uint64),
        ('value', ctypes.c_uint64),
    ]

class drm_prime_handle(ctypes.Structure):
    _fields_ = [
        ('handle', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('fd', ctypes.c_int32)
    ]

class drm_mode_resources(ctypes.Structure):
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

class drm_mode_get_encoder(ctypes.Structure):
    _fields_ = [
        ('encoder_id', ctypes.c_uint32),
        ('encoder_type', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('possible_crtcs', ctypes.c_uint32),
        ('possible_clones', ctypes.c_uint32)
    ]

DRM_MODE_CONNECTOR_Unknown = 0
DRM_MODE_CONNECTOR_VGA = 1
DRM_MODE_CONNECTOR_DVII = 2
DRM_MODE_CONNECTOR_DVID = 3
DRM_MODE_CONNECTOR_DVIA = 4
DRM_MODE_CONNECTOR_Composite = 5
DRM_MODE_CONNECTOR_SVIDEO = 6
DRM_MODE_CONNECTOR_LVDS = 7
DRM_MODE_CONNECTOR_Component = 8
DRM_MODE_CONNECTOR_9PinDIN = 9
DRM_MODE_CONNECTOR_DisplayPort = 10
DRM_MODE_CONNECTOR_HDMIA = 11
DRM_MODE_CONNECTOR_HDMIB = 12
DRM_MODE_CONNECTOR_TV = 13
DRM_MODE_CONNECTOR_eDP = 14
DRM_MODE_CONNECTOR_VIRTUAL = 15
DRM_MODE_CONNECTOR_DSI = 16
DRM_MODE_CONNECTOR_DPI = 17
DRM_MODE_CONNECTOR_WRITEBACK = 18

class drm_mode_get_connector(ctypes.Structure):
    _fields_ = [
        ('encoders_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('modes_ptr', ctypes.POINTER(drm_mode_info)),
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

class drm_mode_plane_resources(ctypes.Structure):
    _fields_ = [
        ('plane_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_planes', ctypes.c_uint32)
    ]

class drm_mode_get_plane(ctypes.Structure):
    _fields_ = [
        ('plane_id', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('fb_id', ctypes.c_uint32),
        ('possible_crtcs', ctypes.c_uint32),
        ('gamma_size', ctypes.c_uint32),
        ('count_format_types', ctypes.c_uint32),
        ('format_type_ptr', ctypes.POINTER(ctypes.c_uint32))
    ]

class drm_mode_property_enum(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_uint64),
        ('name', (32 * ctypes.c_char))
    ]

    def __str__(self):
        return '%u: %s' % (self.value, self.name.decode('utf-8'))

class drm_mode_get_property(ctypes.Structure):
    _fields_ = [
        ('values_ptr', ctypes.c_uint64),
        ('enum_blob_ptr', ctypes.c_uint64),
        ('prop_id', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('name', (32 * ctypes.c_char)),
        ('count_values', ctypes.c_uint32),
        ('count_enum_blobs', ctypes.c_uint32)
    ]

class drm_mode_get_blob(ctypes.Structure):
    _fields_ = [
        ('blob_id', ctypes.c_uint32),
        ('length', ctypes.c_uint32),
        ('data', ctypes.POINTER(ctypes.c_byte))
    ]

class drm_mode_crtc(ctypes.Structure):
    _fields_ = [
        ('set_connectors_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_connectors', ctypes.c_uint32),
        ('crtc_id', ctypes.c_uint32),
        ('fb_id', ctypes.c_uint32),
        ('x', ctypes.c_uint32),
        ('y', ctypes.c_uint32),
        ('gamma_size', ctypes.c_uint32),
        ('mode_valid', ctypes.c_uint32),
        ('mode', drm_mode_info)
    ]

DRM_IOCTL_BASE = ord('d')

def DRM_IO(nr):
    return IO(DRM_IOCTL_BASE, nr)

def DRM_IOWR(nr, type):
    return IOWR(DRM_IOCTL_BASE, nr, ctypes.sizeof(type))

def DRM_IOW(nr, type):
    return IOW(DRM_IOCTL_BASE, nr, ctypes.sizeof(type))

DRM_IOCTL_VERSION = DRM_IOWR(0x00, drm_version)
DRM_IOCTL_GET_CAP = DRM_IOWR(0x0c, drm_capability)
DRM_IOCTL_SET_CLIENT_CAP = DRM_IOW(0x0d, drm_capability)
DRM_IOCTL_SET_MASTER = DRM_IO(0x1e)
DRM_IOCTL_DROP_MASTER = DRM_IO(0x1f)
DRM_IOCTL_PRIME_HANDLE_TO_FD = DRM_IOWR(0x2d, drm_prime_handle)
DRM_IOCTL_PRIME_FD_TO_HANDLE = DRM_IOWR(0x2e, drm_prime_handle)
DRM_IOCTL_MODE_GETRESOURCES = DRM_IOWR(0xa0, drm_mode_resources)
DRM_IOCTL_MODE_GETCRTC = DRM_IOWR(0xa1, drm_mode_crtc)
DRM_IOCTL_MODE_GETENCODER = DRM_IOWR(0xa6, drm_mode_get_encoder)
DRM_IOCTL_MODE_GETCONNECTOR = DRM_IOWR(0xa7, drm_mode_get_connector)
DRM_IOCTL_MODE_GETPROPERTY = DRM_IOWR(0xaa, drm_mode_get_property)
DRM_IOCTL_MODE_GETPROPBLOB = DRM_IOWR(0xac, drm_mode_get_blob)
DRM_IOCTL_MODE_GETPLANERESOURCES = DRM_IOWR(0xb5, drm_mode_plane_resources)
DRM_IOCTL_MODE_GETPLANE = DRM_IOWR(0xb6, drm_mode_get_plane)

def get_flags(value):
    flags = []

    if value & DRM_MODE_PROP_PENDING:
        flags.append('pending')

    if value & DRM_MODE_PROP_RANGE:
        flags.append('range')

    if value & DRM_MODE_PROP_IMMUTABLE:
        flags.append('immutable')

    if value & DRM_MODE_PROP_ENUM:
        flags.append('enum')

    if value & DRM_MODE_PROP_BLOB:
        flags.append('blob')

    if value & DRM_MODE_PROP_BITMASK:
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

class Format:
    def __init__(self, fmt):
        self.fmt = fmt
        self.name = ''

        while True:
            if fmt & 0xff == 0:
                break

            self.name += chr(fmt & 0xff)
            fmt >>= 8

    def __repr__(self):
        return '%u' % self.fmt

    def __str__(self):
        return '%s' % self.name

class Mode:
    def __init__(self, mode):
        self.name = mode.name.encode('UTF-8')

DRM_MODE_PROP_PENDING = 1 << 0
DRM_MODE_PROP_RANGE = 1 << 1
DRM_MODE_PROP_IMMUTABLE = 1 << 2
DRM_MODE_PROP_ENUM = 1 << 3
DRM_MODE_PROP_BLOB = 1 << 4
DRM_MODE_PROP_BITMASK = 1 << 5

DRM_MODE_PROP_EXTENDED_TYPE = 0x0000ffc0

def DRM_MODE_PROP_TYPE(prop_type):
    return prop_type << 6

DRM_MODE_PROP_OBJECT = DRM_MODE_PROP_TYPE(1)
DRM_MODE_PROP_SIGNED_RANGE = DRM_MODE_PROP_TYPE(2)

DRM_MODE_PROP_ATOMIC = 0x80000000

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
    def __init__(self, prop_id, name, flags, minimum, maximum):
        super().__init__(prop_id, name, flags)

        self.min = minimum
        self.max = maximum

    def __str__(self):
        return '%u: %s (range: %d-%d)' % (self.id, self.name, self.min, self.max)

class PropertyEnum(Property):
    def __init__(self, prop_id, name, flags, enums):
        super().__init__(prop_id, name, flags)

        self.enums = enums

    def __str__(self):
        return '%u: %s (enum: %s)' % (self.id, self.name, self.enums)

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

DRM_MODE_CONNECTED = 1
DRM_MODE_DISCONNECTED = 2
DRM_MODE_UNKNOWNCONNECTION = 3

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

        args = drm_mode_crtc()
        args.crtc_id = self.id

        device.ioctl(DRM_IOCTL_MODE_GETCRTC, args)

        if args.mode_valid:
            self.mode = args.mode
        else:
            self.mode = None

    def __repr__(self):
        return '%u' % self.id

class Connector:
    status = {
        DRM_MODE_CONNECTED: 'connected',
        DRM_MODE_DISCONNECTED: 'disconnected',
        DRM_MODE_UNKNOWNCONNECTION: 'unknown',
    }

    types = {
        DRM_MODE_CONNECTOR_Unknown: 'unknown',
        DRM_MODE_CONNECTOR_VGA: 'VGA',
        DRM_MODE_CONNECTOR_DVII: 'DVI-I',
        DRM_MODE_CONNECTOR_DVID: 'DVI-D',
        DRM_MODE_CONNECTOR_DVIA: 'DVI-A',
        DRM_MODE_CONNECTOR_Composite: 'composite',
        DRM_MODE_CONNECTOR_SVIDEO: 's-video',
        DRM_MODE_CONNECTOR_LVDS: 'LVDS',
        DRM_MODE_CONNECTOR_Component: 'component',
        DRM_MODE_CONNECTOR_9PinDIN: '9-pin DIN',
        DRM_MODE_CONNECTOR_DisplayPort: 'DP',
        DRM_MODE_CONNECTOR_HDMIA: 'HDMI-A',
        DRM_MODE_CONNECTOR_HDMIB: 'HDMI-B',
        DRM_MODE_CONNECTOR_TV: 'TV',
        DRM_MODE_CONNECTOR_eDP: 'eDP',
        DRM_MODE_CONNECTOR_VIRTUAL: 'Virtual',
        DRM_MODE_CONNECTOR_DSI: 'DSI',
        DRM_MODE_CONNECTOR_DPI: 'DPI',
        DRM_MODE_CONNECTOR_WRITEBACK: 'WRITEBACK',
    }

    def __init__(self, device, connector_id):
        self.device = device
        self.id = connector_id
        self.encoder = None

        self.encoders = []
        self.modes = []
        self.properties = []

        args = drm_mode_get_connector()
        args.connector_id = self.id

        device.ioctl(DRM_IOCTL_MODE_GETCONNECTOR, args)

        if args.count_encoders > 0:
            encoders = (ctypes.c_uint32 * args.count_encoders)()
            args.encoders_ptr = encoders

        if args.count_modes > 0:
            modes = (drm_mode_info * args.count_modes)()
            args.modes_ptr = modes

        if args.count_props > 0:
            props = (ctypes.c_uint32 * args.count_props)()
            prop_values = (ctypes.c_uint64 * args.count_props)()

            args.props_ptr = props
            args.prop_values_ptr = prop_values

        device.ioctl(DRM_IOCTL_MODE_GETCONNECTOR, args)

        self.name = '%s-%u' % (Connector.types[args.connector_type],
                               args.connector_type_id)
        self.status = Connector.status[args.connection]
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

DRM_MODE_ENCODER_NONE = 0
DRM_MODE_ENCODER_DAC = 1
DRM_MODE_ENCODER_TMDS = 2
DRM_MODE_ENCODER_LVDS = 3
DRM_MODE_ENCODER_TVDAC = 4
DRM_MODE_ENCODER_VIRTUAL = 5
DRM_MODE_ENCODER_DSI = 6
DRM_MODE_ENCODER_DPMST = 7
DRM_MODE_ENCODER_DPI = 8

class Encoder:
    types = {
        DRM_MODE_ENCODER_NONE: 'NONE',
        DRM_MODE_ENCODER_DAC: 'DAC',
        DRM_MODE_ENCODER_TMDS: 'TMDS',
        DRM_MODE_ENCODER_LVDS: 'LVDS',
        DRM_MODE_ENCODER_TVDAC: 'TVDAC',
        DRM_MODE_ENCODER_VIRTUAL: 'VIRTUAL',
        DRM_MODE_ENCODER_DSI: 'DSI',
        DRM_MODE_ENCODER_DPMST: 'DPMST',
        DRM_MODE_ENCODER_DPI: 'DPI',
    }

    def __init__(self, device, index, id):
        self.device = device
        self.index = index
        self.id = id

        args = drm_mode_get_encoder()
        args.encoder_id = id

        device.ioctl(DRM_IOCTL_MODE_GETENCODER, args)

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
        self.formats = []

        args = drm_mode_get_plane()
        args.plane_id = id

        device.ioctl(DRM_IOCTL_MODE_GETPLANE, args)

        self.crtc = args.crtc_id
        self.fb = args.fb_id
        self.possible_crtcs = args.possible_crtcs
        self.gamma_size = args.gamma_size

        if args.count_format_types > 0:
            formats = (ctypes.c_uint32 * args.count_format_types)()
            args.format_type_ptr = formats

        device.ioctl(DRM_IOCTL_MODE_GETPLANE, args)

        for fmt in formats:
            fmt = Format(fmt)
            self.formats.append(fmt)

    def __repr__(self):
        return '%u' % self.id

class Resolution:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Device:
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR)
        self.path = path

    def ioctl(self, nr, args):
        fcntl.ioctl(self.fd, nr, args)

    def version(self):
        v = drm_version()

        self.ioctl(DRM_IOCTL_VERSION, v)

        name = bytes(v.name_len)
        date = bytes(v.date_len)
        desc = bytes(v.desc_len)

        v.name = ctypes.c_char_p(name)
        v.date = ctypes.c_char_p(date)
        v.desc = ctypes.c_char_p(desc)

        self.ioctl(DRM_IOCTL_VERSION, v)

        return Version(v)

    def get_capability(self, cap):
        args = drm_capability()
        args.capability = cap

        self.ioctl(DRM_IOCTL_GET_CAP, args)

        if cap == DRM_CAP_DUMB_BUFFER or \
           cap == DRM_CAP_VBLANK_HIGH_CRTC or \
           cap == DRM_CAP_DUMB_PREFER_SHADOW or \
           cap == DRM_CAP_TIMESTAMP_MONOTONIC or \
           cap == DRM_CAP_ASYNC_PAGE_FLIP or \
           cap == DRM_CAP_ADDFB2_MODIFIERS or \
           cap == DRM_CAP_PAGE_FLIP_TARGET or \
           cap == DRM_CAP_CRTC_IN_VBLANK_EVENT or \
           cap == DRM_CAP_SYNCOBJ:
            return args.value != 0

        return args.value

    def set_capability(self, cap, value):
        args = drm_capability()
        args.capability = cap
        args.value = value

        self.ioctl(DRM_IOCTL_SET_CLIENT_CAP, args)

    def set_master(self):
        self.ioctl(DRM_IOCTL_SET_MASTER, 0)

    def drop_master(self):
        self.ioctl(DRM_IOCTL_DROP_MASTER, 0)

    def prime_handle_to_fd(self, handle, flags):
        args = drm_prime_handle()
        args.fd = -1
        args.handle = handle
        args.flags = flags

        self.ioctl(DRM_IOCTL_PRIME_HANDLE_TO_FD, args)

        return args.fd

    def prime_fd_to_handle(self, fd):
        args = drm_prime_handle()
        args.fd = fd

        self.ioctl(DRM_IOCTL_PRIME_FD_TO_HANDLE, args)

        return args.handle

    def get_property(self, prop_id, value):
        args = drm_mode_get_property()
        args.prop_id = prop_id

        self.ioctl(DRM_IOCTL_MODE_GETPROPERTY, args)

        name = args.name.decode('utf-8')
        flags = get_flags(args.flags)
        prop = None

        if args.count_values > 0:
            values = (ctypes.c_uint64 * args.count_values)()
            args.values_ptr = ctypes.addressof(values)

        if args.count_enum_blobs > 0:
            if args.flags & (DRM_MODE_PROP_ENUM | DRM_MODE_PROP_BITMASK):
                blobs = (drm_mode_property_enum * args.count_enum_blobs)()
                args.enum_blob_ptr = ctypes.addressof(blobs)

            if args.flags & DRM_MODE_PROP_BLOB:
                blobs = (ctypes.c_uint32 * args.count_enum_blobs)()
                args.enum_blob_ptr = ctypes.addressof(blobs)

                values = (ctypes.c_uint32 * args.count_enum_blobs)()
                args.values_ptr = ctypes.addressof(values)

        device.ioctl(DRM_IOCTL_MODE_GETPROPERTY, args)

        if args.flags & DRM_MODE_PROP_PENDING:
            raise NotImplemented('unable to parse pending properties')

        if args.flags & DRM_MODE_PROP_RANGE:
            return PropertyRange(prop_id, name, flags, values[0], values[1])

        if args.flags & DRM_MODE_PROP_ENUM:
            enums = {}

            for blob in blobs:
                enum = blob.name.decode('utf-8')
                enums[enum] = blob.value

            return PropertyEnum(prop_id, name, flags, enums)

        if args.flags & DRM_MODE_PROP_BLOB:
            if args.count_enum_blobs > 0:
                raise NotImplemented('unable to parse %u enum blobs' %
                                        args.count_enum_blobs)
            else:
                if value > 0:
                    blob = device.get_blob(value)
                else:
                    blob = None

            return PropertyBlob(prop_id, name, flags, blob)

        if args.flags & DRM_MODE_PROP_BITMASK:
            raise NotImplemented('unable to parse bitmask properties')

        prop_type = args.flags & DRM_MODE_PROP_EXTENDED_TYPE

        if prop_type == DRM_MODE_PROP_OBJECT:
            raise NotImplemented('unable to parse object properties')

        if prop_type == DRM_MODE_PROP_SIGNED_RANGE:
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

            if args.flags & DRM_MODE_PROP_ENUM:
                self.values = {}

                if args.count_enum_blobs > 0:
                    for blob in blobs:
                        self.values[blob.name] = blob.value

        return prop

    def get_blob(self, blob_id):
        args = drm_mode_get_blob()
        args.blob_id = blob_id
        data = None

        device.ioctl(DRM_IOCTL_MODE_GETPROPBLOB, args)

        #print('  blob: %u' % blob_id)
        #print('    length: %u bytes' % args.length)

        if args.length > 0:
            data = (ctypes.c_byte * args.length)()
            args.data = data

            device.ioctl(DRM_IOCTL_MODE_GETPROPBLOB, args)

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
        args = drm_mode_resources()

        self.ioctl(DRM_IOCTL_MODE_GETRESOURCES, args)

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

        self.ioctl(DRM_IOCTL_MODE_GETRESOURCES, args)

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
        args = drm_mode_plane_resources()

        self.ioctl(DRM_IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            planes = (ctypes.c_uint32 * args.count_planes)()
            args.plane_id_ptr = planes

        self.ioctl(DRM_IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            for plane in planes:
                plane = Plane(self, plane)
                self.planes.append(plane)

class DeviceNode:
    def open(self):
        return Device(self.path)

    def __del__(self):
        if self.fd:
            os.close(self.fd)

        self.fd = None

class CardDevice(DeviceNode):
    def __init__(self, path):
        self.path = path
        self.fd = None

class RenderNode(DeviceNode):
    def __init__(self, path):
        self.path = path
        self.fd = None

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

if __name__ == '__main__':
    for node in devices():
        if isinstance(node, CardDevice):
            device = node.open()
            v = device.version()

            print('version: %u.%u.%u' % (v.major, v.minor, v.patch))
            print('name:', v.name)
            print('date:', v.date)
            print('description:', v.desc)

            print('capabilities:')
            print('  dumb buffers:', device.get_capability(DRM_CAP_DUMB_BUFFER))
            print('  VBLANK high CRTC:', device.get_capability(DRM_CAP_VBLANK_HIGH_CRTC))
            print('  preferred depth:', device.get_capability(DRM_CAP_DUMB_PREFERRED_DEPTH))
            print('  prefer shadow:', device.get_capability(DRM_CAP_DUMB_PREFER_SHADOW))

            prime = device.get_capability(DRM_CAP_PRIME)
            flags = []

            if prime & DRM_CAP_PRIME_IMPORT:
                flags.append('import')

            if prime & DRM_CAP_PRIME_EXPORT:
                flags.append('export')

            print('  PRIME:', ', '.join(flags))
            print('  timestamp monotonic:', device.get_capability(DRM_CAP_TIMESTAMP_MONOTONIC))
            print('  async page flip:', device.get_capability(DRM_CAP_ASYNC_PAGE_FLIP))

            width = device.get_capability(DRM_CAP_CURSOR_WIDTH)
            height = device.get_capability(DRM_CAP_CURSOR_HEIGHT)
            print('  cursor: %ux%u' % (width, height))

            print('  framebuffer modifiers:', device.get_capability(DRM_CAP_ADDFB2_MODIFIERS))
            print('  page flip target:', device.get_capability(DRM_CAP_PAGE_FLIP_TARGET))
            print('  CRTC in VBLANK event:', device.get_capability(DRM_CAP_CRTC_IN_VBLANK_EVENT))
            print('  Sync objects:', device.get_capability(DRM_CAP_SYNCOBJ))

            device.set_capability(DRM_CLIENT_CAP_UNIVERSAL_PLANES, True)
            device.get_resources()

            if device.connectors:
                print('connectors:')

                for connector in device.connectors:
                    print('  %s' % connector)

                    if connector.modes:
                        print('    modes:')

                        for mode in connector.modes:
                            flags = ', '.join(mode.get_flags())
                            types = ', '.join(mode.get_types())

                            if flags:
                                flags = ' flags: %s' % flags

                            if types:
                                types = ' type: %s' % types

                            print('      %s%s%s' % (mode, flags, types))

                    print('    encoders:')

                    for encoder in connector.encoders:
                        if encoder == connector.encoder:
                            print('    * %s' % encoder)
                        else:
                            print('      %s' % encoder)

            if device.encoders:
                print('encoders:')

                for encoder in device.encoders:
                    print('  %s' % encoder)
                    print('    CRTCs:')

                    for crtc in encoder.possible_crtcs:
                        if crtc == encoder.crtc:
                            print('    * %s' % crtc)
                        else:
                            print('      %s' % crtc)

                    print('    Clones:')

                    for clone in encoder.possible_clones:
                        print('      %s' % clone)

            if device.crtcs:
                print('CRTCs:')

                for crtc in device.crtcs:
                    print('  %s' % crtc)

            if device.framebuffers:
                print('Framebuffers:')

                for fb in device.framebuffers:
                    print(' ', fb)

            if device.planes:
                print('Planes:')

                for plane in device.planes:
                    print('    CRTC: %u (possible: %x)' % (plane.crtc, plane.possible_crtcs))
                    print('    FB:', plane.fb)
                    print('    gamma size:', plane.gamma_size)

                    count = len(plane.formats)

                    print(' ', plane)
                    print('    %u format%s:' % (count, 's' if count > 1 else ''))

                    for fmt in plane.formats:
                        print('     ', fmt)
