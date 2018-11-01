import ctypes, enum, sys, time
import drm, drm.tegra

def align(value, align):
    return (value + align - 1) & ~(align - 1)

class drm_tegra_gem_create(ctypes.Structure):
    _fields_ = [
            ('size', ctypes.c_uint64),
            ('flags', ctypes.c_uint32),
            ('handle', ctypes.c_uint32)
        ]

class drm_tegra_gem_mmap(ctypes.Structure):
    _fields_ = [
            ('handle', ctypes.c_uint32),
            ('pad', ctypes.c_uint32),
            ('offset', ctypes.c_uint64)
        ]

class drm_tegra_channel_open(ctypes.Structure):
    _fields_ = [
            ('client', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('context', ctypes.c_uint32),
            ('version', ctypes.c_uint32),
            ('capabilities', ctypes.c_uint32)
        ]

class drm_tegra_channel_close(ctypes.Structure):
    _fields_ = [
            ('context', ctypes.c_uint32),
            ('padding', ctypes.c_uint32)
        ]

class drm_tegra_channel_map(ctypes.Structure):
    _fields_ = [
            ('context', ctypes.c_uint32),
            ('handle', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('mapping', ctypes.c_uint32)
        ]

class drm_tegra_channel_unmap(ctypes.Structure):
    _fields_ = [
            ('context', ctypes.c_uint32),
            ('mapping', ctypes.c_uint32)
        ]

class drm_tegra_submit_reloc(ctypes.Structure):
    _fields_ = [
            ('target_offset', ctypes.c_uint64),
            ('gather_offset_words', ctypes.c_uint32),
            ('shift', ctypes.c_uint32)
        ]

class drm_tegra_submit_buffer(ctypes.Structure):
    _fields_ = [
            ('mapping', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('reloc', drm_tegra_submit_reloc)
        ]

class drm_tegra_submit_syncpt(ctypes.Structure):
    _fields_ = [
            ('id', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('increments', ctypes.c_uint32),
            ('value', ctypes.c_uint32)
        ]

class drm_tegra_submit_gather_uptr(ctypes.Structure):
    _fields_ = [
            ('words', ctypes.c_uint32),
            ('reserved', 3 * ctypes.c_uint32)
        ]

class drm_tegra_submit_wait_syncpt(ctypes.Structure):
    _fields_ = [
            ('id', ctypes.c_uint32),
            ('value', ctypes.c_uint32),
            ('reserved', 2 * ctypes.c_uint32)
        ]

class drm_tegra_submit_command_data(ctypes.Union):
    _fields_ = [
            ('gather_uptr', drm_tegra_submit_gather_uptr),
            ('wait_syncpt', drm_tegra_submit_wait_syncpt),
            ('reserved', 4 * ctypes.c_uint32)
        ]

class drm_tegra_submit_command_type(enum.IntEnum):
    SUBMIT_COMMAND_GATHER_UPTR = 0x0
    SUBMIT_COMMAND_WAIT_SYNCPT = 0x1

class drm_tegra_submit_command(ctypes.Structure):
    _fields_ = [
            ('type', ctypes.c_uint32),
            ('flags', ctypes.c_uint32),
            ('data', drm_tegra_submit_command_data)
        ]

class drm_tegra_channel_submit(ctypes.Structure):
    _fields_ = [
            ('context', ctypes.c_uint32),
            ('num_bufs', ctypes.c_uint32),
            ('num_cmds', ctypes.c_uint32),
            ('gather_data_words', ctypes.c_uint32),
            ('bufs_ptr', ctypes.c_uint64),
            ('cmds_ptr', ctypes.c_uint64),
            ('gather_data_ptr', ctypes.c_uint64),
            ('syncobj_in', ctypes.c_uint32),
            ('syncobj_out', ctypes.c_uint32),
            ('syncpt', drm_tegra_submit_syncpt)
        ]

class drm_tegra_syncpoint_allocate(ctypes.Structure):
    _fields_ = [
            ('id', ctypes.c_uint32),
            ('padding', ctypes.c_uint32)
        ]

class drm_tegra_syncpoint_free(ctypes.Structure):
    _fields_ = [
            ('id', ctypes.c_uint32),
            ('padding', ctypes.c_uint32)
        ]

class drm_tegra_syncpoint_wait(ctypes.Structure):
    _fields_ = [
            ('timeout_ns', ctypes.c_int64),
            ('id', ctypes.c_uint32),
            ('threshold', ctypes.c_uint32),
            ('value', ctypes.c_uint32),
            ('padding', ctypes.c_uint32)
        ]

DRM_IOCTL_TEGRA_GEM_CREATE = drm.IOWR(drm.COMMAND_BASE + 0x00, drm_tegra_gem_create)
DRM_IOCTL_TEGRA_GEM_MMAP = drm.IOWR(drm.COMMAND_BASE + 0x01, drm_tegra_gem_mmap)
DRM_IOCTL_TEGRA_CHANNEL_OPEN = drm.IOWR(drm.COMMAND_BASE + 0x10, drm_tegra_channel_open)
DRM_IOCTL_TEGRA_CHANNEL_CLOSE = drm.IOWR(drm.COMMAND_BASE + 0x11, drm_tegra_channel_close)
DRM_IOCTL_TEGRA_CHANNEL_MAP = drm.IOWR(drm.COMMAND_BASE + 0x12, drm_tegra_channel_map)
DRM_IOCTL_TEGRA_CHANNEL_UNMAP = drm.IOWR(drm.COMMAND_BASE + 0x13, drm_tegra_channel_unmap)
DRM_IOCTL_TEGRA_CHANNEL_SUBMIT = drm.IOWR(drm.COMMAND_BASE + 0x14, drm_tegra_channel_submit)
DRM_IOCTL_TEGRA_SYNCPOINT_ALLOCATE = drm.IOWR(drm.COMMAND_BASE + 0x20, drm_tegra_syncpoint_allocate)
DRM_IOCTL_TEGRA_SYNCPOINT_FREE = drm.IOWR(drm.COMMAND_BASE + 0x21, drm_tegra_syncpoint_free)
DRM_IOCTL_TEGRA_SYNCPOINT_WAIT = drm.IOWR(drm.COMMAND_BASE + 0x22, drm_tegra_syncpoint_wait)

def HOST1X_OPCODE_INCR(offset, count):
    return (0x1 << 28) | (offset & 0xfff) << 16 | (count & 0xffff)

def HOST1X_OPCODE_NONINCR(offset, count):
    return (0x2 << 28) | (offset & 0xfff) << 16 | (count & 0xffff)

class BufferObject:
    def __init__(self, parent, size, flags):
        self.parent = parent

        args = drm_tegra_gem_create()
        args.size = size
        args.flags = flags

        parent.device.ioctl(DRM_IOCTL_TEGRA_GEM_CREATE, args)

        self.handle = args.handle
        self.size = args.size

    def __del__(self):
        self.close()

    def close(self):
        if self.handle is not None:
            args = drm.gem_close()
            args.handle = self.handle

            self.parent.device.ioctl(drm.IOCTL_GEM_CLOSE, args)

        self.handle = None

    def map(self):
        args = drm_tegra_gem_mmap()
        args.handle = self.handle

        self.parent.device.ioctl(DRM_IOCTL_TEGRA_GEM_MMAP, args)
        self.mmap = self.parent.device.mmap(args.offset, self.size)

        return self.mmap

    def unmap(self):
        self.mmap.close()

class Syncpoint:
    COND_IMMEDIATE = 0
    COND_OP_DONE = 1
    COND_RD_DONE = 2
    COND_WR_SAFE = 3

    def __init__(self, parent):
        self.parent = parent

        args = drm_tegra_syncpoint_allocate()
        self.ioctl(DRM_IOCTL_TEGRA_SYNCPOINT_ALLOCATE, args)

        self.id = args.id

    def free(self):
        args = drm_tegra_syncpoint_free()
        args.id = self.id

        self.ioctl(DRM_IOCTL_TEGRA_SYNCPOINT_FREE, args)

    def ioctl(self, nr, args):
        return self.parent.device.ioctl(nr, args)

class Mapping:
    class Flags(enum.IntFlag):
        READ = 1 << 0
        WRITE = 1 << 1
        READ_WRITE = (1 << 1) | (1 << 0)

    def __init__(self, channel, bo, flags):
        self.channel = channel
        self.handle = bo.handle
        self.flags = flags

        args = drm_tegra_channel_map()
        args.context = channel.context
        args.handle = bo.handle
        args.flags = flags

        self.channel.parent.device.ioctl(DRM_IOCTL_TEGRA_CHANNEL_MAP, args)

        self.id = args.mapping

    def unmap(self):
        args = drm_tegra_channel_unmap()
        args.context = self.channel.context
        args.mapping = self.id

        self.channel.parent.device.ioctl(DRM_IOCTL_TEGRA_CHANNEL_UNMAP, args)

class Job:
    class Syncpoint:
        def __init__(self, id):
            self.id = id
            self.increments = 0

        def increment(self, count):
            self.increments += count

    class PushBuffer:
        def __init__(self, job):
            self.job = job
            self.buffer = []
            self.ptr = 0

        def begin(self):
            self.ptr = len(self.buffer)

        def end(self):
            return len(self.buffer) - self.ptr

        def push(self, word):
            self.buffer.append(word)

        def length(self):
            return len(self.buffer)

        def get_data(self):
            return (ctypes.c_uint32 * len(self.buffer))(*self.buffer)

    def __init__(self, channel):
        self.channel = channel
        self.pushbuf = Job.PushBuffer(self)
        self.commands = []
        self.buffers = []
        self.syncpt = None

        if channel.version == Channel.Version.TEGRA20 or \
           channel.version == Channel.Version.TEGRA30 or \
           channel.version == Channel.Version.TEGRA114 or \
           channel.version == Channel.Version.TEGRA124 or \
           channel.version == Channel.Version.TEGRA210:
            self.cond_shift = 8
        elif channel.version == Channel.Version.TEGRA186 or \
             channel.version == Channel.Version.TEGRA194:
            self.cond_shift = 10
        else:
            raise Exception('unknown channel version: %s' % channel.version)

    def ioctl(self, nr, args):
        return self.channel.parent.device.ioctl(nr, args)

    def push_begin(self):
        self.pushbuf.begin()

    def push_end(self):
        words = self.pushbuf.end()

        command = drm_tegra_submit_command()
        command.type = drm_tegra_submit_command_type.SUBMIT_COMMAND_GATHER_UPTR
        command.flags = 0
        command.data.gather_uptr.words = words

        self.commands.append(command)

    def push_wait(self, syncpt, value):
        command = drm_tegra_submit_command()
        command.type = drm_tegra_submit_command_type.SUBMIT_COMMAND_WAIT_SYNCPT
        command.flags = 0
        command.data.wait_syncpt.id = syncpt.id
        command.data.wait_syncpt.value = value

        self.commands.append(command)

    def push(self, word):
        self.pushbuf.push(word)

    def push_buffer(self, target, offset, shift, flags):
        buffer = drm_tegra_submit_buffer()
        buffer.mapping = target.id
        buffer.flags = flags
        buffer.reloc.target_offset = offset
        buffer.reloc.gather_offset_words = self.pushbuf.length()
        buffer.reloc.shift = shift
        self.buffers.append(buffer)

        self.pushbuf.push(0xdeadbeef)

    def push_sync(self, syncpt, count):
        if self.syncpt is None:
            self.syncpt = Job.Syncpoint(syncpt.id)

        if syncpt.id != self.syncpt.id:
            raise Exception('job already uses syncpoint %u' % self.syncpt.id)

        self.syncpt.increment(count)

    def push_sync_cond(self, syncpt, cond):
        self.push(HOST1X_OPCODE_NONINCR(0x0, 0x1))
        self.push(cond << self.cond_shift | syncpt.id)
        self.push_sync(syncpt, 1)

    def submit(self):
        gather_data = self.pushbuf.get_data()

        args = drm_tegra_channel_submit()
        args.context = self.channel.context
        args.gather_data_words = self.pushbuf.length()
        args.gather_data_ptr = ctypes.addressof(gather_data)
        args.syncobj_in = 0
        args.syncobj_out = 0

        if self.buffers:
            buffers = (drm_tegra_submit_buffer * len(self.buffers))(*self.buffers)
            args.num_bufs = len(self.buffers)
            args.bufs_ptr = ctypes.addressof(buffers)

        if self.commands:
            commands = (drm_tegra_submit_command * len(self.commands))(*self.commands)
            args.num_cmds = len(self.commands)
            args.cmds_ptr = ctypes.addressof(commands)

        if self.syncpt is not None:
            args.syncpt.id = self.syncpt.id
            args.syncpt.increments = self.syncpt.increments
            args.syncpt.flags = 0

        self.ioctl(DRM_IOCTL_TEGRA_CHANNEL_SUBMIT, args)

        self.fence = args.syncpt.value

    def wait(self, timeout):
        now = time.clock_gettime_ns(time.CLOCK_MONOTONIC)

        args = drm_tegra_syncpoint_wait()
        args.timeout_ns = now + timeout
        args.id = self.syncpt.id
        args.threshold = self.fence

        self.ioctl(DRM_IOCTL_TEGRA_SYNCPOINT_WAIT, args)

class Channel:
    class Class(enum.IntEnum):
        HOST1X = 0x01
        GR2D = 0x51
        GR2D_SB = 0x52
        VIC = 0x5d
        GR3D = 0x60
        NVDEC = 0xf0

    class Capabilities(enum.IntFlag):
        CACHE_COHERENT = 1 << 0

    class Version(enum.IntEnum):
        TEGRA20  = 0x20
        TEGRA30  = 0x30
        TEGRA114 = 0x35
        TEGRA124 = 0x40
        TEGRA210 = 0x21
        TEGRA186 = 0x18
        TEGRA194 = 0x19
        TEGRA234 = 0x23

    def __init__(self, parent, client, flags):
        self.parent = parent
        self.client = client
        self.context = None
        self.flags = flags

        args = drm_tegra_channel_open()
        args.client = client
        args.flags = flags

        try:
            self.parent.device.ioctl(DRM_IOCTL_TEGRA_CHANNEL_OPEN, args)
        except OSError as e:
            raise e

        self.context = args.context
        self.version = Channel.Version(args.version)
        self.capabilities = Channel.Capabilities(args.capabilities)

    def __del__(self):
        self.close()

    def close(self):
        if self.context is not None:
            args = drm_tegra_channel_close()
            args.context = self.context

            self.ioctl(DRM_IOCTL_TEGRA_CHANNEL_CLOSE, args)

        self.context = None
        self.version = None
        self.capabilities = None

    def ioctl(self, nr, args):
        return self.parent.device.ioctl(nr, args)

    def map(self, bo, flags):
        return Mapping(self, bo, flags)

    def create_job(self):
        return Job(self)

class Device:
    def __init__(self, device):
        self.device = device
        self.fd = device.fd

    def close(self):
        pass

    def create_gem(self, size, flags):
        return BufferObject(self, size, flags)

    def open_channel(self, client, flags):
        return Channel(self, client, flags)

    def allocate_syncpoint(self):
        return Syncpoint(self)

class VIC:
    class Color:
        def __init__(self, format, red, green, blue, alpha):
            self.format = format
            self.red = red
            self.green = green
            self.blue = blue
            self.alpha = alpha

            if self.format == VIC.PixelFormat.A8R8G8B8:
                self.value = int(alpha * 255) << 24 | int(red * 255) << 16 | \
                             int(green * 255) << 8 | int(blue) * 255
            elif self.format == VIC.PixelFormat.R8G8B8A8:
                self.value = int(red * 255) << 24 | int(green * 255) << 16 | \
                             int(blue * 255) << 8 | int(alpha) * 255
            else:
                raise Exception('unsupported pixel format %s' % self.format)

        def __str__(self):
            return '%s: <%.3f %.3f %.3f %.3f>' % (self.format, self.red, self.green,
                                                  self.blue, self.alpha)

    class Command(enum.IntEnum):
        INCR_SYNCPT = 0x00
        METHOD_OFFSET = 0x10
        METHOD_DATA = 0x11

    class AlphaFillMode(enum.IntEnum):
        OPAQUE = 0
        BACKGROUND = 1
        DESTINATION = 2
        COMPOSITED = 4
        SOURCE_ALPHA = 5

    class PixelFormat(enum.IntEnum):
        A8 = 0
        L8 = 1
        A4L4 = 2
        L4A4 = 3
        R8 = 4
        A8L8 = 5
        L8A8 = 6
        R8G8 = 7
        G8R8 = 8
        B5G6R5 = 9
        R5G6B5 = 10
        B6G5R5 = 11
        R5G5B6 = 12
        A1B5G5R5 = 13
        A1R5G5B5 = 14
        B5G5B5A1 = 15
        R5G5B5A1 = 16
        A5B5G5R1 = 17
        A5R1G5B5 = 18
        B5G5R1A5 = 19
        R1G5B5A5 = 20
        X1B5G5R5 = 21
        X1R5G5B5 = 22
        B5G5R5X1 = 23
        R5G5B5X1 = 24
        A4B4G4R4 = 25
        A4R4G4B4 = 26
        B4G4R4A4 = 27
        R4G4B4A4 = 28
        B8_G8_R8 = 29
        R8_G8_B8 = 30
        A8B8G8R8 = 31
        A8R8G8B8 = 32
        B8G8R8A8 = 33
        R8G8B8A8 = 34
        X8G8B8R8 = 35
        X8R8G8B8 = 36
        B8G8R8X8 = 37
        R8G8B8X8 = 38
        A2B10G10R10 = 39
        A2R10G10B10 = 40
        B10G10R10A2 = 41
        R10G10B10A2 = 42
        A4P4 = 43
        P4A4 = 44
        P8A8 = 45
        A8P8 = 46
        P8 = 47
        P1 = 48
        U8V8 = 49
        V8U8 = 50
        A8Y8U8V8 = 51
        V8U8Y8A8 = 52
        Y8_U8_V8 = 53
        Y8_V8_U8 = 54
        U8_V8_Y8 = 55
        V8_U8_Y8 = 56
        Y8_U8__Y8_V8 = 57
        Y8_V8__Y8_U8 = 58
        U8_Y8__V8_Y8 = 59
        V8_Y8__U8_Y8 = 60
        Y8___U8V8_N444 = 61
        Y8___V8U8_N444 = 62
        Y8___U8V8_N422 = 63
        Y8___V8U8_N422 = 64
        Y8___U8V8_N422R = 65
        Y8___V8U8_N422R = 66
        Y8___U8V8_N420 = 67
        Y8___V8U8_N420 = 68
        Y8___U8___V8_N444 = 69
        Y8___U8___V8_N422 = 70
        Y8___U8___V8_N422R = 71
        Y8___U8___V8_N420 = 72
        U8 = 73
        V8 = 74
        Y10___U10V10_N444 = 75
        Y10___V10U10_N444 = 76
        Y10___U10V10_N422 = 77
        Y10___V10U10_N422 = 78
        Y10___U10V10_N422R = 79
        Y10___V10U10_N422R = 80
        Y10___U10V10_N420 = 81
        Y10___V10U10_N420 = 82
        Y10___U10___V10_N444 = 83
        Y10___U10___V10_N422 = 84
        Y10___U10___V10_N422R = 85
        Y10___U10___V10_N420 = 86
        U10 = 87
        V10 = 88
        L10 = 89
        U10V10 = 90
        V10U10 = 91
        Y12___U12V12_N444 = 92
        Y12___V12U12_N444 = 93
        Y12___U12V12_N422 = 94
        Y12___V12U12_N422 = 95
        Y12___U12V12_N422R = 96
        Y12___V12U12_N422R = 97
        Y12___U12V12_N420 = 98
        Y12___V12U12_N420 = 99
        Y12___U12___V12_N444 = 100
        Y12___U12___V12_N422 = 101
        Y12___U12___V12_N422R = 102
        Y12___U12___V12_N420 = 103
        U12 = 104
        V12 = 105
        L12 = 106
        U12V12 = 107
        V12U12 = 108
        L16 = 109
        A16B16G16R16 = 110
        A16Y16U16V16 = 111
        R16 = 112
        Y16___V8U8_N444 = 113
        Y16___V8U8_N422 = 114
        Y16___V8U8_N420 = 115
        Y16___V16U16_N444 = 116
        Y16___V16U16_N422 = 117
        Y16___V16U16_N420 = 118
        U16V16 = 119
        V16U16 = 120

    class BlockKind(enum.IntEnum):
        PITCH = 0
        GENERIC_16Bx2 = 1
        BL_NAIVE = 2
        BL_KEPLER_XBAR_RAW = 3
        VP2_TILED = 15

    class GammaMode(enum.IntEnum):
        NONE = 0
        SRGB = 1
        REC709 = 2
        REC2020 = 3

    class BlendSourceFactorC(enum.IntEnum):
        K1 = 0
        K1_TIMES_DST = 1
        NEG_K1_TIMES_DST = 2
        K1_TIMES_SRC = 3
        ZERO = 4

    class BlendDestinationFactorC(enum.IntEnum):
        K1 = 0
        K2 = 1
        K1_TIMES_DST = 2
        NEG_K1_TIMES_DST = 3
        NEG_K1_TIMES_SRC = 4
        ZERO = 5
        ONE = 6

    class BlendSourceFactorA(enum.IntEnum):
        K1 = 0
        K2 = 1
        NEG_K1_TIMES_DST = 2
        ZERO = 3

    class BlendDestinationFactorA(enum.IntEnum):
        K2 = 0
        NEG_K1_TIMES_SRC = 1
        ZERO = 2
        ONE = 3

    class CacheWidth(enum.IntEnum):
        _16Bx16 = 0
        _32Bx8 = 1
        _64Bx4 = 2
        _128Bx2 = 3
        _256Bx1 = 4

    class Image:
        def __init__(self, parent, width, height, format, kind):
            self.parent = parent
            self.width = width
            self.height = height
            self.format = format
            self.kind = kind

            if format == VIC.PixelFormat.A8R8G8B8:
                self.bpp = 4
            else:
                raise Exception('unsupported format:', format)

            if kind == VIC.BlockKind.PITCH:
                # operates on 8x8 pixel macroblocks
                self.align = 8
            else:
                # XXX needs change for block-linear?
                self.align = 8

            self.stride = align(self.width, self.align)
            self.pitch = self.stride * self.bpp
            self.size = self.pitch * self.height

            device = parent.channel.parent
            self.buffer = drm.tegra.BufferObject(device, self.size, 0)

        def __del__(self):
            self.free()

        def free(self):
            self.buffer.close()

        def clear(self, value):
            mapping = self.buffer.map()

            size = self.buffer.size
            byte = ctypes.c_byte.from_buffer(mapping)
            address = ctypes.addressof(byte)
            ctypes.memset(address, value, size)

            del byte
            mapping.close()

        """
        This function checks whether the image was filled with a given color pixel
        and that the non-visible areas of the image are filled with the expected fill
        value.
        """
        def validate_color_and_fill(self, color, fill = None):
            mapping = self.buffer.map()

            for j in range(0, self.height):
                for i in range(0, self.width):
                    if self.bpp == 4 or self.bpp == 3:
                        cls = ctypes.c_uint32
                    elif self.bpp == 2:
                        cls = ctypes.c_uint16
                    else:
                        raise Exception('unsupported bytes/pixel: %u' % self.bpp)

                    pixel = cls.from_buffer(mapping, j * self.pitch + i * self.bpp)
                    if pixel.value != color.value:
                        raise Exception('unexpected pixel %x at <%u, %u>' % (pixel.value, i, j))

                    del pixel

                if fill is not None:
                    offset = j * self.pitch + (i + 1) * self.bpp
                    mapping.seek(offset)

                    length = self.pitch - self.width * self.bpp
                    for pos, byte in enumerate(mapping.read(length)):
                        if byte != fill:
                            raise Exception('unexpected fill byte %x on line %u, byte %u' % (byte, j, pos))

            mapping.close()

        def dump(self, file = sys.stdout):
            print('image:', self, file = file)
            print('  resolution: %ux%u' % (self.width, self.height), file = file)
            print('  stride: %u pitch: %u' % (self.stride, self.pitch), file = file)
            print('  data:', file = file)

            mapping = self.buffer.map()

            for j in range(0, self.height):
                print('   ', end = '', file = file)

                for i in range(0, self.width):
                    if self.bpp == 4 or self.bpp == 3:
                        cls = ctypes.c_uint32
                        width = 8
                    elif self.bpp == 2:
                        cls = ctypes.c_uint16
                        width = 4
                    else:
                        raise Exception('unsupported bytes per pixel: %u' % self.bpp)

                    pixel = cls.from_buffer(mapping, j * self.pitch + i * self.bpp)
                    print(' %0*x' % (width, pixel.value), end = '', file = file)
                    del pixel

                print(file = file)

            mapping.close()

    @classmethod
    def create(cls, tegra):
        #from drm.tegra import vic30
        #from drm.tegra import vic40
        #from drm.tegra import vic41
        from drm.tegra import vic42

        channel = tegra.open_channel(drm.tegra.Channel.Class.VIC, 0)

        #if channel.version == Channel.Version.TEGRA124:
        #    return vic30.VIC(channel)

        #if channel.version == Channel.Version.TEGRA210:
        #    return vic40.VIC(channel)

        #if channel.version == Channel.Version.TEGRA186:
        #    return vic41.VIC(channel)

        if channel.version == Channel.Version.TEGRA194:
            return vic42.VIC(channel)

        channel.close()
        raise Exception('unknown VIC version')

    def __init__(self, channel):
        self.syncpt = drm.tegra.Syncpoint(channel.parent)
        self.channel = channel
        self.mappings = {}

        self.config = drm.tegra.BufferObject(channel.parent, 16 * 1024, 0)
        self.filter = drm.tegra.BufferObject(channel.parent, 16 * 1024, 0)
        self.histogram = drm.tegra.BufferObject(channel.parent, 4 * 1024, 0)

        self.map(self.config, drm.tegra.Mapping.Flags.READ)
        self.map(self.filter, drm.tegra.Mapping.Flags.READ)
        self.map(self.histogram, drm.tegra.Mapping.Flags.READ_WRITE)

    def close(self):
        for buffer, mapping in self.mappings.items():
            mapping.unmap()

        self.mappings = {}

        self.histogram.close()
        self.filter.close()
        self.config.close()
        self.syncpt.free()

        self.channel.close()

    def map(self, buffer, flags):
        if buffer in self.mappings:
            print('buffer %s already mapped to VIC' % buffer)
            return

        self.mappings[buffer] = self.channel.map(buffer, flags)

    def unmap(self, buffer):
        if buffer not in self.mappings:
            print('buffer %s is not mapped to VIC' % buffer)
            return

        self.mappings[buffer].unmap()
        del self.mappings[buffer]

    def image(self, width, height, fmt, kind):
        return VIC.Image(self, width, height, fmt, kind)

    def push_method(self, job, method, value):
        job.push(HOST1X_OPCODE_INCR(VIC.Command.METHOD_OFFSET, 2))
        job.push(method >> 2)
        job.push(value)

    def push_buffer(self, job, method, mapping, offset, flags):
        job.push(HOST1X_OPCODE_INCR(VIC.Command.METHOD_OFFSET, 2))
        job.push(method >> 2)
        job.push_buffer(mapping, offset, 8, flags)
