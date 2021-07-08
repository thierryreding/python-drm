#!/usr/bin/python3

import drm, time

if __name__ == '__main__':
    use_cairo = True

    for node in drm.devices():
        if isinstance(node, drm.CardDevice):
            device = node.open()

            device.set_capability(drm.DRM_CLIENT_CAP_UNIVERSAL_PLANES, True)
            device.get_resources()

            if device.connectors:
                for connector in device.connectors:
                    if connector.status == drm.Connector.Status.CONNECTED:
                        mode = connector.modes[0]
                        width = mode.hdisplay
                        height = mode.vdisplay
                        fmt = drm.Format.XRGB8888
                        #fmt = drm.Format.RGB565
                        #fmt = drm.Format.XRGB1555

                        dumb = device.create_dumb(width, height, fmt.cpp[0] * 8, 0)

                        fb = device.add_framebuffer(width, height, fmt, 0, [dumb], [dumb.pitch], [0], [0])

                        for plane in device.planes:
                            if plane.crtc == connector.encoder.crtc:
                                plane.set(plane.crtc, fb, 0, 0, 0, width, height, 0, 0, width, height)


                        if use_cairo:
                            import cairo

                            data = dumb.map()

                            surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, width, height, width * 4)
                            cr = cairo.Context(surface)

                            cr.scale(width, height)
                            cr.rectangle(0, 0, 1, 1)
                            cr.set_source_rgba(1, 1, 1, 1)
                            cr.fill()

                            time.sleep(1)

                            cr.rectangle(0, 0, 1, 1)
                            cr.set_source_rgba(1, 0, 0, 1)
                            cr.fill()

                            time.sleep(1)
                        else:
                            white = fmt.pixel(1.0, 1.0, 1.0, 1.0)
                            red = fmt.pixel(1.0, 0.0, 0.0, 1.0)

                            for y in range(0, height):
                                for x in range(0, width):
                                    dumb[x, y] = white

                            time.sleep(1)

                            for y in range(0, height):
                                for x in range(0, width):
                                    dumb[x, y] = red

                            time.sleep(1)
