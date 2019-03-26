#!/usr/bin/env python
import os
import struct
import numpy as np

def write_map(fname, collarr, tilearr, objarr):
    if collarr.shape != tilearr.shape[1:] or len(collarr.shape) != 2:
        raise TypeError(f'array shapes {collarr.shape} cannot be broadcast to {tilearr.shape}')
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
            [0] * 36,
            [1] * 36,
            *([1, *([0] * 34), 1] for _ in range(14)),
            [*([1] * 15), *([0] * 6), *([1] * 15)],
            *([*([0] * 14), 1, *([0] * 6), 1, *([1] * 14)] for _ in range(7)),
            [*([0] * 14), *([1] * 8), *([0] * 14)],
            ]),
        np.array([[
            [0] * 36,
            [2, *([3] * 34), 4],
            *([1, *([8] * 34), 5] for _ in range(14)),
            *([*([0] * 14), 1, *([9] * 6), 5, *([0] * 14)] for _ in range(8)),
            [*([0] * 14), 6, *([0] * 6), 7, *([0] * 14)],
            ], [
            *([0] * 36 for _ in range(8)),
            [*([0] * 16), 36, 37, 37, 38, *([0] * 16)],
            [*([0] * 16), 36, 37, 37, 38, *([0] * 16)],
            *([0] * 36 for _ in range(15))
            ]]),
        np.array([
            [0, 576, 292, 1],
            [1, 144, 310],
            [1, 732, 310],
            [1, 1116, 310],
            [1, 600, 732],
            ]),
        )
