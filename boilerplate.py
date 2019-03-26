import os
import struct
import itertools
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


class ClipDrawSprite(pg.sprite.Sprite):
    """Sprites that use a clip rectangle to designate its tile in an atlas."""

    def __init__(self, image=None, rect=None, clip=None):
        super().__init__()
        self.image = image
        if image is not None and rect is None:
            self.rect = self.image.get_rect()
        else:
            self.rect = pg.Rect(rect)
        if self.rect is not None and clip is None:
            self.clip = self.rect.copy()
            self.clip.topleft = (0, 0)
        else:
            self.clip = pg.Rect(clip)

    def draw(self, surf):
        surf.blit(self.image, self.rect, self.clip)


class ClipDrawGroup(pg.sprite.OrderedUpdates):
    """Group that accomodates atlas based sprites."""

    def draw(self, surf):
        blitfunc = surf.blit
        for sprite in self.sprites():
            blitfunc(sprite.image, sprite.rect, sprite.clip)


class InteractibleSprite(ClipDrawSprite):
    """Interactibles."""

    sheet = None
    def __init__(self, rect, clip, interact=None, hitbox=None):
        super().__init__(self.sheet, rect, clip)
        self.ibox = pg.Rect(interact) if interact else self.rect
        self.hitbox = pg.Rect(hitbox) if hitbox else self.ibox

    def trigger(self, player):
        pass

    def update(self):
        pass


class TileMapSprite(pg.sprite.Sprite):
    """The tiled background that all the other sprites walk on."""

    tiles = None
    sprites = None
    def __init__(self, mapname):
        with open(os.path.join('assets', 'mapdata', mapname), 'rb') as mapfile:
            if mapfile.read(4) != b'TLMP':
                raise IOError('Mapfile of incorrect format')
            self.size = struct.unpack('>II', mapfile.read(8))
            self.collmap = [
                pg.Rect(col * 32, row * 32, 32, 32)
                for row in range(self.size[0])
                for col, byte in enumerate(mapfile.read(self.size[1]))
                if byte & 1
                ]
            self.tilemap = pg.Surface((self.size[0] * 32, self.size[1] * 32))
            for row, col in itertools.product(*map(range, self.size)):
                for tileid in struct.unpack('>HH', mapfile.read(4)):
                    self.tilemap.blit(
                        self.tiles,
                        (col * 32, row * 32, 32, 32),
                        (tileid % 8 * 32, tileid // 8 * 32, 32, 32)
                        )
            if mapfile.read(4) != b'OBJS':
                raise IOError('Mpafile object data has incorrect format')
            self.objs = [[]]
            buff = mapfile.read(2)
            while buff:
                if len(self.objs[-1]) < 3 or buff != b'\x00\x00':
                    self.objs[-1].append(struct.unpack('>H', buff)[0])
                else:
                    self.objs[-1] = self.sprites[self.objs[-1][0]](self.objs[-1][1:3], *self.objs[-1][3:])
                    self.objs.append([])
                buff = mapfile.read(2)
            self.objs.pop()
            self.collmap.extend(obj.hitbox for obj in self.objs[1:])
        self.tilerect = self.tilemap.get_rect()
        self.rect = self.tilemap.get_rect()
        self.image = self.tilemap.copy()

    def update(self):
        obj_iter = iter(self.objs)
        next(obj_iter).update(self)
        for obj in obj_iter:
            obj.update()

    def draw(self, window):
        self.image.blit(self.tilemap, (0, 0))
        for obj in reversed(self.objs):
            obj.draw(self.image)
        window.blit(self.image, self.rect)


class GameState(object):
    instance = None
    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, handler):
        self.handler = handler
        self.window = pg.display.get_surface()

    async def eval_logic(self):
        raise NotImplementedError

    async def draw_frame(self):
        raise NotImplementedError
