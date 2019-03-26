#!/usr/bin/env python
import os
import struct
import numpy as np

def write_map(fname, collarr, tilearr, objarr):
    if collarr.shape != tilearr.shape[1:] or len(collarr.shape) != 2:
        raise TypeError('array shapes do not match 2d mapping')
    print(f'Writing mapfile {fname}')
    with open(os.path.join('assets', 'mapdata', fname), 'wb') as mapfile:
        mapfile.write('TLMP'.encode())
        mapfile.write(struct.pack('>II', *collarr.shape))
        print('Writing collision table data...')
        for cell in collarr.flatten():
            mapfile.write(struct.pack('>?', cell))
        print('Writing tilemap table data...')
        for layer1, layer2 in zip(tilearr[0].flatten(), tilearr[1].flatten()):
            mapfile.write(struct.pack('>HH', layer1, layer2))
        print('Writing object data...')
        mapfile.write('OBJS'.encode())
        for obj in objarr:
            mapfile.write(struct.pack(f'>{len(obj)}Hcc', *obj, b'\x00', b'\x00'))

    print('Done!')

if __name__ == '__main__':
    write_map(
        'testmap.dat',
        np.array([
            [0] * 16,
            [1] * 16,
            *([1, *([0] * 14), 1] for _ in range(14)),
            [1] * 16,
            ]),
        np.array([[
            [0] * 16,
            [2, *([3] * 14), 4],
            [1, *([8] * 14), 5],
            *([1, *([8] * 14), 5] for _ in range(12)),
            [1, *([9] * 14), 5],
            [6, *([0] * 14), 7]
            ], [
            *([0] * 16 for _ in range(8)),
            [*([0] * 7), 36, 38, *([0] * 7)],
            [*([0] * 7), 36, 38, *([0] * 7)],
            *([0] * 16 for _ in range(7))
            ]]),
        np.array([
            [0, 256, 256, 2],
            [1, 280, 128],
            ]),
        )
