#!/usr/bin/python3

import ctypes, fcntl, os, os.path

IOC_NONE = 0
IOC_WRITE = 1
IOC_READ = 2

IOC_DIR_SHIFT = 30
IOC_SIZE_SHIFT = 16
IOC_TYPE_SHIFT = 8
IOC_NR_SHIFT = 0

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

    def __str__(self):
        return '%ux%u-%u' % (self.hdisplay, self.vdisplay, self.vrefresh)

CAP_DUMB_BUFFER = 0x1
CAP_VBLANK_HIGH_CRTC = 0x2
CAP_DUMB_PREFERRED_DEPTH = 0x3
CAP_DUMB_PREFER_SHADOW = 0x4
CAP_PRIME = 0x05
CAP_PRIME_IMPORT = 0x01
CAP_PRIME_EXPORT = 0x02
CAP_TIMESTAMP_MONOTONIC = 0x6
CAP_ASYNC_PAGE_FLIP = 0x7
CAP_CURSOR_WIDTH = 0x8
CAP_CURSOR_HEIGHT = 0x9
CAP_ADDFB2_MODIFIERS = 0x10
CAP_PAGE_FLIP_TARGET = 0x11
CAP_CRTC_IN_VBLANK_EVENT = 0x12
CAP_SYNCOBJ = 0x13

CLIENT_CAP_STEREO_3D = 0x01
CLIENT_CAP_UNIVERSAL_PLANES = 0x02
CLIENT_CAP_ATOMIC = 0x03
CLIENT_CAP_ASPECT_RATIO = 0x04
CLIENT_CAP_WRITEBACK_CONNECTORS = 0x05

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

class Framebuffer:
    def __init__(self, device, id):
        self.device = device
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class CRTC:
    def __init__(self, device, id):
        self.device = device
        self.id = id

        args = drm_mode_crtc()
        args.crtc_id = id

        device.ioctl(DRM_IOCTL_MODE_GETCRTC, args)

        print('count_connectors:', args.count_connectors)
        print('crtc_id:', args.crtc_id)
        print('fb_id:', args.fb_id)
        print('x: %u y: %u' % (args.x, args.y))
        print('gamma size: %u' % args.gamma_size)
        print('mode valid:', args.mode_valid)

        if args.mode_valid:
            print('mode:', args.mode)
            print('  clock:', args.mode.clock)
            print('  hdisplay:', args.mode.hdisplay)
            print('  hsync_start:', args.mode.hsync_start)
            print('  hsync_end:', args.mode.hsync_end)
            print('  htotal:', args.mode.htotal)
            print('  hskew:', args.mode.hskew)
            print('  vdisplay:', args.mode.vdisplay)
            print('  vsync_start:', args.mode.vsync_start)
            print('  vsync_end:', args.mode.vsync_end)
            print('  vtotal:', args.mode.vtotal)
            print('  vscan:', args.mode.vscan)
            print('  vrefresh:', args.mode.vrefresh)
            print('  flags:', args.mode.flags)
            print('  type:', args.mode.type)
            print('  name:', args.mode.name)

    def __repr__(self):
        return '%u' % self.id

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
    def __init__(self, device, blob_id):
        args = drm_mode_get_blob()
        args.blob_id = blob_id

        device.ioctl(DRM_IOCTL_MODE_GETPROPBLOB, args)

        print('  blob: %u' % blob_id)
        print('    length: %u bytes' % args.length)

        if args.length > 0:
            data = (ctypes.c_byte * args.length)()
            args.data = data

            device.ioctl(DRM_IOCTL_MODE_GETPROPBLOB, args)

            self.data = bytes(data)

        print('    data:\n     ', end = '')
        count = 0

        for byte in self.data:
            if count >= 16:
                print('\n     ', end = '')
                count = 0

            print(' %02x' % byte, end = '')
            count += 1

        print()

class Property:
    def __init__(self, device, prop_id, value):
        self.device = device
        self.id = prop_id
        self.value = value
        self.blob = None

        self.name = args.name.decode('utf-8')

    def __str__(self):
        return '%u: %s -> %u' % (self.id, self.name, self.value)

class Connector:
    def __init__(self, device, id):
        self.device = device
        self.id = id

        self.encoders = []

        args = drm_mode_get_connector()
        args.connector_id = id

        device.ioctl(DRM_IOCTL_MODE_GETCONNECTOR, args)

        print('connector:', id)
        print('  encoders:', args.count_encoders)
        print('  properties:', args.count_props)
        print('  modes:', args.count_modes)

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

        if args.count_encoders > 0:
            print('  encoders: %u' % args.count_encoders)

            for encoder_id in encoders:
                for encoder in device.encoders:
                    if encoder.id == encoder_id:
                        self.encoders.append(encoder)
                        print('    %s' % encoder)
                        break
                else:
                    print('    %u: unknown' % encoder_id)

        if args.count_modes > 0:
            print('  modes: %u' % args.count_modes)

            for mode in modes:
                print('    %s' % mode)

        if args.count_props > 0:
            print('  properties: %u' % args.count_props)

            for prop_id, value in zip(props, prop_values):
                prop = Property(device, prop_id, value)
                print('    %s' % prop)

    def __repr__(self):
        return '%u' % self.id

class Encoder:
    def __init__(self, device, id):
        self.device = device
        self.id = id

        args = drm_mode_get_encoder()
        args.encoder_id = id

        device.ioctl(DRM_IOCTL_MODE_GETENCODER, args)

        self.type = args.encoder_type
        self.crtc = args.crtc_id

        DRM_MODE_ENCODER_NONE = 0
        DRM_MODE_ENCODER_DAC = 1
        DRM_MODE_ENCODER_TMDS = 2
        DRM_MODE_ENCODER_LVDS = 3
        DRM_MODE_ENCODER_TVDAC = 4
        DRM_MODE_ENCODER_VIRTUAL = 5
        DRM_MODE_ENCODER_DSI = 6
        DRM_MODE_ENCODER_DPMST = 7
        DRM_MODE_ENCODER_DPI = 8

        encoder_types = {
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

        if args.encoder_type in encoder_types:
            self.name = '%s:%u' % (encoder_types[args.encoder_type], self.id)
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

        if cap == CAP_DUMB_BUFFER or \
           cap == CAP_VBLANK_HIGH_CRTC or \
           cap == CAP_DUMB_PREFER_SHADOW or \
           cap == CAP_TIMESTAMP_MONOTONIC or \
           cap == CAP_ASYNC_PAGE_FLIP or \
           cap == CAP_ADDFB2_MODIFIERS or \
           cap == CAP_PAGE_FLIP_TARGET or \
           cap == CAP_CRTC_IN_VBLANK_EVENT or \
           cap == CAP_SYNCOBJ:
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

    def get_property(self, prop_id):
        args = drm_mode_get_property()
        args.prop_id = prop_id

        self.ioctl(DRM_IOCTL_MODE_GETPROPERTY, args)

        print('property: %u' % args.prop_id)
        print('  name: %s' % args.name.decode('utf-8'))
        print('  flags: %x' % args.flags)
        print('  count_values: %u' % args.count_values)
        print('  count_enum_blobs: %u' % args.count_enum_blobs)

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
            pass

        if args.flags & DRM_MODE_PROP_RANGE:
            pass

        if args.flags & DRM_MODE_PROP_BLOB:
            prop = PropertyBlob()

            if args.count_enum_blobs > 0:
                print('  blobs: %u' % args.count_enum_blobs)

                for blob_id in blobs:
                    print('    %u' % blob_id)

                print('  values: %u' % args.count_enum_blobs)

                for value in values:
                    print('    %u' % value)
            else:
                self.blob = Blob(device, value)

        if args.flags & DRM_MODE_PROP_BITMASK:
            pass

        prop_type = args.flags & DRM_MODE_PROP_EXTENDED_TYPE

        if prop_type == DRM_MODE_PROP_OBJECT:
            pass

        if prop_type == DRM_MODE_PROP_SIGNED_RANGE:
            pass

        if args.flags & DRM_MODE_PROP_EXTENDED_TYPE
        else:
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
            for crtc in crtcs:
                crtc = CRTC(self, crtc)
                self.crtcs.append(crtc)

        if args.count_encoders > 0:
            for encoder in encoders:
                encoder = Encoder(self, encoder)
                self.encoders.append(encoder)

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
            print('  dumb buffers:', device.get_capability(CAP_DUMB_BUFFER))
            print('  VBLANK high CRTC:', device.get_capability(CAP_VBLANK_HIGH_CRTC))
            print('  preferred depth:', device.get_capability(CAP_DUMB_PREFERRED_DEPTH))
            print('  prefer shadow:', device.get_capability(CAP_DUMB_PREFER_SHADOW))

            prime = device.get_capability(CAP_PRIME)
            flags = []

            if prime & CAP_PRIME_IMPORT:
                flags.append('import')

            if prime & CAP_PRIME_EXPORT:
                flags.append('export')

            print('  PRIME:', ', '.join(flags))
            print('  timestamp monotonic:', device.get_capability(CAP_TIMESTAMP_MONOTONIC))
            print('  async page flip:', device.get_capability(CAP_ASYNC_PAGE_FLIP))

            width = device.get_capability(CAP_CURSOR_WIDTH)
            height = device.get_capability(CAP_CURSOR_HEIGHT)
            print('  cursor: %ux%u' % (width, height))

            print('  framebuffer modifiers:', device.get_capability(CAP_ADDFB2_MODIFIERS))
            print('  page flip target:', device.get_capability(CAP_PAGE_FLIP_TARGET))
            print('  CRTC in VBLANK event:', device.get_capability(CAP_CRTC_IN_VBLANK_EVENT))
            print('  Sync objects:', device.get_capability(CAP_SYNCOBJ))

            device.set_capability(CLIENT_CAP_UNIVERSAL_PLANES, True)

            device.get_resources()

#            if device.framebuffers:
#                print('Framebuffers:')
#
#                for fb in device.framebuffers:
#                    print(' ', fb)
#
#            if device.crtcs:
#                print('CRTCs:')
#
#                for crtc in device.crtcs:
#                    print(' ', crtc)
#
#            if device.connectors:
#                print('Connectors:')
#
#                for connector in device.connectors:
#                    print(' ', connector)
#
#            if device.encoders:
#                print('Encoders:')
#
#                for encoder in device.encoders:
#                    print(' ', encoder)
#
#            if device.planes:
#                print('Planes:')
#
#                for plane in device.planes:
#                    print('    CRTC: %u (possible: %x)' % (plane.crtc, plane.possible_crtcs))
#                    print('    FB:', plane.fb)
#                    print('    gamma size:', plane.gamma_size)
#
#                    count = len(plane.formats)
#
#                    print(' ', plane)
#                    print('    %u format%s:' % (count, 's' if count > 1 else ''))
#
#                    for fmt in plane.formats:
#                        print('     ', fmt)
