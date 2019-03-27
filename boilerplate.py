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
            self.size = struct.unpack('>HH', mapfile.read(4))
            self.collmap = [
                pg.Rect(col * 32, row * 32, 32, 32)
                for row in range(self.size[0])
                for col, byte in enumerate(mapfile.read(self.size[1]))
                if byte & 1
                ]
            self.tilemap = pg.Surface((self.size[1] * 32, self.size[0] * 32))
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
                    self.objs[-1] = self.sprites[self.objs[-1][0]](*self.objs[-1][1:])
                    self.objs.append([])
                buff = mapfile.read(2)
            self.objs.pop()
            self.collmap.extend(obj.hitbox for obj in self.objs[1:])
        self.tilerect = self.tilemap.get_rect()
        self.rect = self.tilemap.get_rect()
        self.image = self.tilemap.copy()
        self.player, *self.objs = self.objs
        self.bounds = pg.display.get_surface().get_rect()
        if self.rect.w < self.bounds.w:
            self.rect.centerx = self.bounds.centerx
        else:
            self.rect.x = self.bounds.centerx - self.player.rect.centerx
        if self.rect.h < self.bounds.h:
            self.rect.centery = self.bounds.centery
        else:
            self.rect.y = self.bounds.centery - self.player.rect.bottom
        self.scrollpad = 164
        self.bounds.w -= self.scrollpad * 2
        self.bounds.h -= self.scrollpad * 2
        self.bounds.topleft = (self.scrollpad, self.scrollpad)

    def update(self):
        self.player.update(self)
        for obj in self.objs:
            obj.update()
        # Auto-scrolling.
        posx, posy = self.player.rect.midbottom
        if not self.bounds.collidepoint(posx + self.rect.x, posy + self.rect.y):
            if posx + self.rect.x < self.bounds.left:
                self.rect.x = self.bounds.left + 1 - posx
            else:
                self.rect.x = self.bounds.right - 1 - posx
            if posy + self.rect.y < self.bounds.top:
                self.rect.y = self.bounds.top + 1 - posy
            else:
                self.rect.y = self.bounds.bottom - 1 - posy

    def draw(self, window):
        # Layer split.
        back = []; frnt = []
        for obj in self.objs:
            if obj.rect.bottom <= self.player.rect.bottom:
                back.append(obj)
            else:
                frnt.append(obj)
        # Actual drawing of the layers.
        self.image.blit(self.tilemap, (0, 0))
        for obj in back:
            obj.draw(self.image)
        self.player.draw(self.image)
        for obj in frnt:
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
