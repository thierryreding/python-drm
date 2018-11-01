#!/usr/bin/python3

import cairo, drm, time

class Pattern:
    def draw(self, cr, width, height):
        pass

class SMPTE(Pattern):
    def draw(self, cr, width, height):
        class Column:
            def __init__(self, width, color):
                self.width = width
                self.color = color

        class Row:
            def __init__(self, height, columns):
                self.height = height
                self.columns = columns

        rows = [
            Row(6, [
                    Column(1, (0.75, 0.75, 0.75, 1.0)), # grey
                    Column(1, (0.75, 0.75, 0.00, 1.0)), # yellow
                    Column(1, (0.00, 0.75, 0.75, 1.0)), # cyan
                    Column(1, (0.00, 0.75, 0.00, 1.0)), # green
                    Column(1, (0.75, 0.00, 0.75, 1.0)), # magenta
                    Column(1, (0.75, 0.00, 0.00, 1.0)), # red
                    Column(1, (0.00, 0.00, 0.75, 1.0)), # blue
                ]),
            Row(1, [
                    Column(1, (0.00, 0.00, 0.75, 0.5)), # blue
                    Column(1, (0.07, 0.07, 0.07, 0.5)), # black
                    Column(1, (0.75, 0.00, 0.75, 0.5)), # magenta
                    Column(1, (0.07, 0.07, 0.07, 0.5)), # black
                    Column(1, (0.00, 0.75, 0.75, 0.5)), # cyan
                    Column(1, (0.07, 0.07, 0.07, 0.5)), # black
                    Column(1, (0.75, 0.75, 0.75, 0.5)), # grey
                ]),
            Row(2, [
                    Column(3, (0.00, 0.12, 0.29, 1.0)), # in-phase
                    Column(3, (1.00, 1.00, 1.00, 1.0)), # super white
                    Column(3, (0.19, 0.00, 0.41, 1.0)), # quadrature
                    Column(3, (0.07, 0.07, 0.07, 1.0)), # black
                    Column(1, (0.03, 0.03, 0.03, 1.0)), # 3.5%
                    Column(1, (0.07, 0.07, 0.07, 1.0)), # 7.5%
                    Column(1, (0.11, 0.11, 0.11, 1.0)), # 11.5%
                    Column(3, (0.07, 0.07, 0.07, 1.0)), # black
                ])
        ]

        total_height = 0
        y = 0

        for row in rows:
            total_height += row.height

        for row in rows:
            total_width = 0
            x = 0

            for column in row.columns:
                total_width += column.width

            columns = len(row.columns)

            cr.identity_matrix()
            cr.scale(width / total_width, height / total_height)

            for column in row.columns:
                cr.rectangle(x, y, column.width, row.height)
                cr.set_source_rgba(*column.color)
                cr.fill()

                x = x + column.width

            y = y + row.height

def main():
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
                        fmt = drm.Format.XRGB8888
                        crfmt = cairo.FORMAT_RGB24

                        dumb = device.create_dumb(width, height, fmt.cpp[0] * 8, 0)

                        fb = device.add_framebuffer(width, height, fmt, 0,
                                                    dumb, dumb.pitch, 0, 0)

                        for plane in device.planes:
                            if plane.crtc == connector.encoder.crtc:
                                plane.set(plane.crtc, fb, 0, 0, 0, width, height,
                                          0, 0, width, height)


                        data = dumb.map()

                        surface = cairo.ImageSurface.create_for_data(data, crfmt, width, height,
                                                                     crfmt.stride_for_width(width))
                        cr = cairo.Context(surface)

                        pattern = SMPTE()
                        pattern.draw(cr, width, height)
                        time.sleep(2)

                        del cr, surface

if __name__ == '__main__':
    main()
