#!/usr/bin/env python
import os
import struct
import numpy as np

def write_map(fname: str, collarr: np.array, tilearr: np.array) -> None:
    if collarr.shape != tilearr.shape or len(collarr.shape) != 2:
        raise TypeError('array shapes do not match 2d mapping')
    with open(os.path.join('assets', 'mapdata', fname), 'wb') as mapfile:
        mapfile.write('TLMP'.encode())
        mapfile.write(struct.pack('>II', *collarr.shape))
        mapfile.write(struct.pack('>' + '?'*collarr.size, *collarr.flatten()))
        mapfile.write(struct.pack('>' + 'I'*tilearr.size, *tilearr.flatten()))

if __name__ == '__main__':
    write_map(
        'testmap.map',
        np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]),
        np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]),
        )
