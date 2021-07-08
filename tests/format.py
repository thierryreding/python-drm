#!/usr/bin/python3

import drm

fmt = drm.Format.RGB565
pixel = fmt.pixel(1.0, 0.0, 0.0, 1.0)

print('format:', fmt)
print('pixel:', pixel)

fmt = drm.Format.XRGB8888
pixel = fmt.pixel(1.0, 0.0, 0.0, 1.0)

print('format:', fmt)
print('pixel:', pixel)
