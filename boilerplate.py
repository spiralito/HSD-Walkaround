import os
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
