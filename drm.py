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

class drm_mode_plane_resources(ctypes.Structure):
    _fields_ = [
        ('plane_id_ptr', ctypes.POINTER(ctypes.c_uint32)),
        ('count_planes', ctypes.c_uint32)
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
DRM_IOCTL_MODE_GETPLANERESOURCES = DRM_IOWR(0xb5, drm_mode_plane_resources)

class Version:
    def __init__(self, version):
        self.major = version.version_major
        self.minor = version.version_minor
        self.patch = version.version_patchlevel
        self.name = version.name.decode()
        self.date = version.date.decode()
        self.desc = version.desc.decode()

class Framebuffer:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class CRTC:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class Connector:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class Encoder:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '%u' % self.id

class Plane:
    def __init__(self, id):
        self.id = id

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

    def version(self):
        v = drm_version()

        fcntl.ioctl(self.fd, DRM_IOCTL_VERSION, v)

        name = bytes(v.name_len)
        date = bytes(v.date_len)
        desc = bytes(v.desc_len)

        v.name = ctypes.c_char_p(name)
        v.date = ctypes.c_char_p(date)
        v.desc = ctypes.c_char_p(desc)

        fcntl.ioctl(self.fd, DRM_IOCTL_VERSION, v)

        return Version(v)

    def get_capability(self, cap):
        args = drm_capability()
        args.capability = cap

        fcntl.ioctl(self.fd, DRM_IOCTL_GET_CAP, args)

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

        fcntl.ioctl(self.fd, DRM_IOCTL_SET_CLIENT_CAP, args)

    def set_master(self):
        fcntl.ioctl(self.fd, DRM_IOCTL_SET_MASTER, 0)

    def drop_master(self):
        fcntl.ioctl(self.fd, DRM_IOCTL_DROP_MASTER, 0)

    def prime_handle_to_fd(self, handle, flags):
        args = drm_prime_handle()
        args.fd = -1
        args.handle = handle
        args.flags = flags

        fcntl.ioctl(self.fd, DRM_IOCTL_PRIME_HANDLE_TO_FD, args)

        return args.fd

    def prime_fd_to_handle(self, fd):
        args = drm_prime_handle()
        args.fd = fd

        fcntl.ioctl(self.fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, args)

        return args.handle

    def get_resources(self):
        args = drm_mode_resources()

        fcntl.ioctl(self.fd, DRM_IOCTL_MODE_GETRESOURCES, args)

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

        fcntl.ioctl(self.fd, DRM_IOCTL_MODE_GETRESOURCES, args)

        self.framebuffers = []
        self.crtcs = []
        self.connectors = []
        self.encoders = []
        self.planes = []

        if args.count_fbs > 0:
            for fb in fbs:
                fb = Framebuffer(fb)
                self.framebuffers.append(fb)

        if args.count_crtcs > 0:
            for crtc in crtcs:
                crtc = CRTC(crtc)
                self.crtcs.append(crtc)

        if args.count_connectors > 0:
            for connector in connectors:
                connector = Connector(connector)
                self.connectors.append(connector)

        if args.count_encoders > 0:
            for encoder in encoders:
                encoder = Encoder(encoder)
                self.encoders.append(encoder)

        args = drm_mode_plane_resources()

        fcntl.ioctl(self.fd, DRM_IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            planes = (ctypes.c_uint32 * args.count_planes)()
            args.plane_id_ptr = planes

        fcntl.ioctl(self.fd, DRM_IOCTL_MODE_GETPLANERESOURCES, args)

        if args.count_planes > 0:
            for plane in planes:
                plane = Plane(plane)
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

            if device.framebuffers:
                print('Framebuffers:')

                for fb in device.framebuffers:
                    print(' ', fb)

            if device.crtcs:
                print('CRTCs:')

                for crtc in device.crtcs:
                    print(' ', crtc)

            if device.connectors:
                print('Connectors:')

                for connector in device.connectors:
                    print(' ', connector)

            if device.encoders:
                print('Encoders:')

                for encoder in device.encoders:
                    print(' ', encoder)

            if device.planes:
                print('Planes:')

                for plane in device.planes:
                    print(' ', plane)
