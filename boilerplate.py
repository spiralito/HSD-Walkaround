import os
import struct
import itertools
import numpy as np
import pygame as pg
import asyncio as aio

def load_image(name, *, alpha=None, colorkey=None):
    """Load an image file into memory."""
    try:
        image = pg.image.load(os.path.join('assets', 'textures', name))
    except pg.error:
        print('Image loading failed: ')
        raise
    if alpha is None:
        image = image.convert()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image
    return image.convert_alpha()


class TileMapSprite(pg.sprite.Sprite):
    """The tiled background that all the other sprites walk on."""

    tiles = None
    def __init__(self, mapname):
        if self.__class__.tiles is None:
            self.__class__.tiles = load_image('tiles.png', colorkey=0xFF00FF)
        with open(os.path.join('assets', 'mapdata', mapname), 'rb') as mapfile:
            if mapfile.read(4) != b'TLMP':
                raise IOError('Mapfile of incorrect format')
            self.size = struct.unpack('>II', mapfile.read(8))
            self.collmap = np.array([
                [byte for byte in mapfile.read(self.size[1])]
                for _ in range(self.size[0])
                ]
                , dtype=bool)
            self.tilemap = pg.Surface((self.size[0] * 32, self.size[1] * 32))
            for row, col in itertools.product(*map(range, self.size)):
                tileid = struct.unpack('>I', mapfile.read(4))[0]
                self.tilemap.blit(
                    self.tiles,
                    (col * 32, row * 32, 32, 32),
                    (tileid % 8 * 32, tileid // 8 * 32, 32, 32)
                    )
        self.tilerect = self.tilemap.get_rect()
        self.rect = self.tilemap.get_rect()
        self.image = self.tilemap.copy()

    def reset(self):
        self.image.blit(self.tilemap, (0, 0))

    def draw(self, window):
        window.blit(self.image, self.rect)


class ClipDrawSprite(pg.sprite.Sprite):
    """Sprites that use a clip rectangle to designate its tile in an atlas."""

    def __init__(self, image=None, rect=None, clip=None):
        super().__init__()
        self.image = image
        if image is not None and rect is None:
            self.rect = self.image.get_rect()
        else:
            self.rect = rect
        if self.rect is not None and clip is None:
            self.clip = self.rect.copy()
            self.clip.topleft = (0, 0)
        else:
            self.clip = clip

    def draw(self, surf):
        surf.blit(self.image, self.rect, self.clip)


class ClipDrawGroup(pg.sprite.OrderedUpdates):
    """Group that accomodates atlas based sprites."""

    def draw(self, surf):
        blitfunc = surf.blit
        for sprite in self.sprites():
            blitfunc(sprite.image, sprite.rect, sprite.clip)


class GameState(object):
    instance = None
    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, handler):
        self.handler = handler

    async def eval_logic(self):
        raise NotImplementedError

    async def draw_frame(self):
        raise NotImplementedError
