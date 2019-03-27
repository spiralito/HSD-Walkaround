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
        mapfile.write(struct.pack('>HH', *collarr.shape))
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
        'floor2.dat',
        np.array([
            [0] * 24,
            [1] * 24,
            *([1, *([0] * 22), 1] for _ in range(17)),
            [1] * 24,
            ]),
        np.array([[
            [52] * 24,
            [52, *([12, 13] * 11), 52],
            *([52, *([24] * 22), 52] for _ in range(3)),
            *([52, 24, 24, 24, *([25] * 16), 24, 24, 24, 52] for _ in range(11)),
            *([52, *([24] * 22), 52] for _ in range(3)),
            [52] * 24,
            ], [
            [0] * 24 for _ in range(20)
            ]]),
        np.array([
            [0, 384, 356, 1],
            [1, 128, 356],
            [1, 700, 356],
            ]),
        )
