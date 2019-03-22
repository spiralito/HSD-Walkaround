#!/usr/bin/env python
import os
import struct
import numpy as np

def write_map(fname: str, collarr: np.array, tilearr: np.array) -> None:
    if collarr.shape != tilearr.shape or len(collarr.shape) != 2:
        raise TypeError('array shapes do not match 2d mapping')
    print(f'Writing mapfile {fname}')
    with open(os.path.join('assets', 'mapdata', fname), 'wb') as mapfile:
        mapfile.write('TLMP'.encode())
        mapfile.write(struct.pack('>II', *collarr.shape))
        print('Writing collision table data...')
        for cell in collarr.flatten():
            mapfile.write(struct.pack('>?', cell))
        print('Writing tilemap table data...')
        for cell in tilearr.flatten():
            mapfile.write(struct.pack('>I', cell))
    print('Done!')

if __name__ == '__main__':
    write_map(
        'testmap.map',
        np.array([
            [1] * 16,
            *([1, *([0] * 14), 1] for _ in range(14)),
            [1] * 16
            ]),
        np.array([
            [2, *([3] * 14), 4],
            [1, *([8] * 14), 5],
            *([1, *([8] * 14), 5] for _ in range(12)),
            [1, *([8] * 14), 5],
            [6, *([0] * 14), 7]
            ]),
        )
