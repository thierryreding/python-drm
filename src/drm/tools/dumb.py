#!/usr/bin/python3

import argparse, enum, sys, time
import drm, utils

class Backend(enum.Enum):
    CAIRO = 'cairo'
    PLAIN = 'plain'

    def __str__(self):
        return self._value_

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', metavar = 'BACKEND', type = Backend, default = Backend.CAIRO,
                        action = utils.StoreEnumAction)
    parser.add_argument('--format', metavar = 'FORMAT', type = drm.Format,
                        default = drm.Format.ARGB8888,
                        action = utils.StoreEnumAction)
    args = parser.parse_args(sys.argv[1:])

    for node in drm.devices():
        if isinstance(node, drm.CardDevice):
            device = node.open()

            device.set_capability(drm.ClientCapability.UNIVERSAL_PLANES, True)
            device.get_resources()

            if device.connectors:
                for connector in device.connectors:
                    if connector.status == drm.Connector.Status.CONNECTED:
                        mode = connector.modes[0]
                        width = mode.hdisplay
                        height = mode.vdisplay

                        #fmt = drm.Format.ARGB8888
                        #fmt = drm.Format.XRGB8888
                        #fmt = drm.Format.RGB565
                        fmt = args.format

                        dumb = device.create_dumb(width, height, fmt.cpp[0] * 8, 0)

                        fb = device.add_framebuffer(width, height, fmt, 0,
                                                    dumb, dumb.pitch, 0, 0)

                        for plane in device.planes:
                            if plane.crtc == connector.encoder.crtc:
                                plane.set(plane.crtc, fb, 0, 0, 0, width, height, 0, 0, width, height)

                        if args.backend == Backend.CAIRO:
                            import cairo

                            data = dumb.map()

                            if fmt == drm.Format.ARGB8888:
                                crfmt = cairo.FORMAT_ARGB32
                            elif fmt == drm.Format.XRGB8888:
                                crfmt = cairo.FORMAT_RGB24
                            elif fmt == drm.Format.RGB565:
                                crfmt = cairo.FORMAT_RGB16_565
                            else:
                                raise Exception('format %s not supported in cairo backend' % fmt)

                            pitch = crfmt.stride_for_width(width)
                            surface = cairo.ImageSurface.create_for_data(data, crfmt, width,
                                                                         height, pitch)
                            cr = cairo.Context(surface)
                            cr.scale(width, height)

                            white = (1.0, 1.0, 1.0, 1.0)
                            red = (1.0, 0.0, 0.0, 1.0)
                            green = (0.0, 1, 0.0, 1.0)
                            blue = (0.0, 0.0, 1.0, 1.0)

                            for color in [ white, red, green, blue ]:
                                cr.rectangle(0, 0, 1, 1)
                                cr.set_source_rgba(*color)
                                cr.fill()

                                time.sleep(1)

                            del cr, surface
                        else:
                            white = fmt.pixel(1.0, 1.0, 1.0, 1.0)
                            red = fmt.pixel(1.0, 0.0, 0.0, 1.0)
                            green = fmt.pixel(0.0, 1.0, 0.0, 1.0)
                            blue = fmt.pixel(0.0, 0.0, 1.0, 1.0)

                            for pixel in [ white, red, green, blue ]:
                                for y in range(0, height):
                                    for x in range(0, width):
                                        dumb[x, y] = pixel

                                time.sleep(1)

if __name__ == '__main__':
    main()
