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
            [1] * 8,
            *([1, 0, 0, 0, 0, 0, 0, 1] for _ in range(6)),
            [1] * 8]
            ),
        np.array([
            [1] * 8,
            *([1, 0, 0, 0, 0, 0, 0, 1] for _ in range(6)),
            [1] * 8]
            ),
        )
