#!/usr/bin/python3

import drm

def main():
    for fmt in drm.Format:
        print(fmt)

        if not fmt.components:
            continue

        pixel = fmt.pixel(1.0, 0.0, 0.0, 1.0)
        print('  red:', pixel)

        pixel = fmt.pixel(0.0, 1.0, 0.0, 1.0)
        print('  green:', pixel)

        pixel = fmt.pixel(0.0, 0.0, 1.0, 1.0)
        print('  blue:', pixel)

if __name__ == '__main__':
    main()
