#!/usr/bin/python3

import ctypes, drm

def main():
    for node in drm.devices():
        if isinstance(node, drm.CardDevice):
            device = node.open()
            v = device.version()

            print('version: %u.%u.%u' % (v.major, v.minor, v.patch))
            print('name:', v.name)
            print('date:', v.date)
            print('description:', v.desc)

            print('capabilities:')
            print('  dumb buffers:', device.get_capability(drm.Capability.DUMB_BUFFER))
            print('  VBLANK high CRTC:', device.get_capability(drm.Capability.VBLANK_HIGH_CRTC))
            print('  preferred depth:', device.get_capability(drm.Capability.DUMB_PREFERRED_DEPTH))
            print('  prefer shadow:', device.get_capability(drm.Capability.DUMB_PREFER_SHADOW))

            prime = device.get_capability(drm.Capability.PRIME)
            flags = []

            if prime & drm.Prime.IMPORT:
                flags.append('import')

            if prime & drm.Prime.EXPORT:
                flags.append('export')

            print('  PRIME:', ', '.join(flags))
            #print('  PRIME:', drm.Prime(prime))
            print('  timestamp monotonic:', device.get_capability(drm.Capability.TIMESTAMP_MONOTONIC))
            print('  async page flip:', device.get_capability(drm.Capability.ASYNC_PAGE_FLIP))

            width = device.get_capability(drm.Capability.CURSOR_WIDTH)
            height = device.get_capability(drm.Capability.CURSOR_HEIGHT)
            print('  cursor: %ux%u' % (width, height))

            print('  framebuffer modifiers:', device.get_capability(drm.Capability.ADDFB2_MODIFIERS))
            print('  page flip target:', device.get_capability(drm.Capability.PAGE_FLIP_TARGET))
            print('  CRTC in VBLANK event:', device.get_capability(drm.Capability.CRTC_IN_VBLANK_EVENT))
            print('  Sync objects:', device.get_capability(drm.Capability.SYNCOBJ))

            device.set_capability(drm.ClientCapability.UNIVERSAL_PLANES, True)
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

                    print('    properties:')

                    for prop in connector.properties:
                        if isinstance(prop, drm.PropertyEnum):
                            print('      %u: %s' % (prop.id, prop.name))

                            for enum in prop.type:
                                if enum is prop.value:
                                    print('      * %u: %s' % (enum.value, enum.name))
                                else:
                                    print('        %u: %s' % (enum.value, enum.name))
                        else:
                            print('      %s' % prop)

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
                    print('  %s' % plane)
                    print('    CRTCs:')

                    for crtc in plane.crtcs:
                        if crtc == plane.crtc:
                            print('    * %s' % crtc)
                        else:
                            print('      %s' % crtc)

                    count = len(plane.formats)

                    print('    %u format%s:' % (count, 's' if count > 1 else ''))

                    for fmt in plane.formats:
                        print('      %s' % fmt)

                        if isinstance(plane.formats, dict):
                            for modifier in plane.formats[fmt]:
                                print('        %s' % modifier)

                    count = len(plane.properties)

                    print('    %u propert%s:' % (count, 'y' if count == 1 else 'ies'))

                    for prop in plane.properties:
                        if isinstance(prop, drm.PropertyEnum):
                            print('      %u: %s' % (prop.id, prop.name))

                            for enum in prop.type:
                                if enum is prop.value:
                                    print('      * %u: %s' % (enum.value, enum.name))
                                else:
                                    print('        %u: %s' % (enum.value, enum.name))
                        else:
                            print('      %s' % prop)

if __name__ == '__main__':
    main()
