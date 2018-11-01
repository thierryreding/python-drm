#!/usr/bin/python3

import ctypes, errno
import drm, drm.tegra

def syncpt_wait():
    for node in drm.devices():
        if isinstance(node, drm.RenderNode):
            device = node.open()
            v = device.version()

            if v.name == 'tegra':
                tegra = drm.tegra.Device(device)

                print('device: %s' % device.path)
                print('  name: %s' % v.name)

                syncpt = tegra.allocate_syncpoint()
                print('syncpoint: %x' % syncpt.id)

                bo = tegra.create_gem(65536, 0)

                channel = tegra.open_channel(drm.tegra.Channel.Class.VIC, 0)
                print('  VIC:')
                print('    context: %x' % channel.context)
                print('    version: %s' % channel.version)

                mapping = channel.map(bo, drm.tegra.Mapping.Flags.READ | drm.tegra.Mapping.Flags.WRITE);

                job = channel.create_job()
                job.push_begin()
                job.push_sync_cond(syncpt, syncpt.COND_IMMEDIATE)
                job.push_end()
                job.submit()
                job.wait(250000000)

                mapping.unmap()

                channel.close()
                bo.close()
                syncpt.free()
                tegra.close()

def vic_clear(device, verbose = False):
    tegra = drm.tegra.Device(device)

    color = drm.tegra.VIC.Color(drm.tegra.VIC.PixelFormat.A8R8G8B8,
                                1.0, 0.0, 0.0, 1.0)

    try:
        vic = drm.tegra.VIC.create(tegra)
    except OSError as e:
        if e.errno == errno.ENODEV:
            tegra.close()
            return

    output = vic.image(4, 4, color.format, drm.tegra.VIC.BlockKind.PITCH)
    output.clear(0xff)

    vic.clear(output, color.red, color.green, color.blue, color.alpha)
    vic.execute(output)

    try:
        output.validate_color_and_fill(color, 0xff)
    except:
        if verbose:
            output.dump()

    output.free()
    vic.close()
    tegra.close()

def main():
    for node in drm.devices():
        if isinstance(node, drm.RenderNode):
            device = node.open()
            v = device.version()

            if v.name == 'tegra':
                vic_clear(device)

            device.close()

if __name__ == '__main__':
    main()
