#!/usr/bin/env python
import os
from time import time
import pygame as pg
import asyncio as aio
from boilerplate import (
    load_image, ClipDrawSprite, ClipDrawGroup,
    TileMapSprite, GameState,
    )

key_config = {
    'U': pg.K_UP,
    'D': pg.K_DOWN,
    'L': pg.K_LEFT,
    'R': pg.K_RIGHT,
    }

class PlayerSprite(ClipDrawSprite):
    """The player character."""

    instance = None
    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, pos):
        self.size = (20, 36)
        super().__init__(
            load_image('sprites.png', colorkey=0xFF00FF),
            pg.Rect((0, 0), self.size),
            pg.Rect((0, 0), self.size),
            )
        self.collrect = pg.Rect(0, 0, 24, 8)
        self.rect.midbottom = self.collrect.midbottom = pos
        self.vel = [0, 0]
        self.facing = 0
        self.frame = 0

    def set_motion(self, axis, mdir, press):
        if axis == 0:
            if self.vel[1] * mdir > 0:
                self.vel[1] = 0
            elif press:
                self.vel[1] = 2 * mdir
        else:
            if self.vel[0] * mdir > 0:
                self.vel[0] = 0
            elif press:
                self.vel[0] = 2 * mdir
        if press:
            self.facing = ((mdir < 0) << 1) + axis
            self.vel[axis] = 0 # prevent diagonal movement

    def update(self, tilemap):
        # Store old position: if collision occurs, reset position.
        oldpos = self.rect.midbottom
        self.rect.centerx += self.vel[0]
        self.rect.bottom += self.vel[1]
        self.collrect.midbottom = self.rect.midbottom
        if self.collrect.collidelist(tilemap.collmap) >= 0:
            self.rect.midbottom = self.collrect.midbottom = oldpos
        # Update facing angle.
        self.clip.x = self.size[0] * (self.facing * 3 + (0, 1, 0, 2)[self.frame // 10])
        if self.vel[0] or self.vel[1]:
            self.frame = (self.frame + 1) % 40
        else:
            self.frame = 0


class Walkaround(GameState):
    def __init__(self, handler):
        super().__init__(handler)
        self.tilemap = TileMapSprite('testmap.map')
        self.tilemap.rect.center = self.handler.rect.center
        self.player = PlayerSprite(self.tilemap.tilerect.center)

    async def eval_logic(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.handler.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == key_config['U']:
                    self.player.set_motion(0, -1, True)
                elif event.key == key_config['D']:
                    self.player.set_motion(0, +1, True)
                elif event.key == key_config['L']:
                    self.player.set_motion(1, -1, True)
                elif event.key == key_config['R']:
                    self.player.set_motion(1, +1, True)
            elif event.type == pg.KEYUP:
                if event.key == key_config['U']:
                    self.player.set_motion(0, -1, False)
                elif event.key == key_config['D']:
                    self.player.set_motion(0, +1, False)
                elif event.key == key_config['L']:
                    self.player.set_motion(1, -1, False)
                elif event.key == key_config['R']:
                    self.player.set_motion(1, +1, False)
        self.player.update(self.tilemap)

    async def draw_frame(self):
        window = self.handler.window
        window.fill(0x000000)
        self.tilemap.reset()
        self.player.draw(self.tilemap.image)
        self.tilemap.draw(window)
        pg.display.flip()


class GameApplication(object):
    """Handles the game, self-explanatory."""

    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self):
        self.window = pg.display.get_surface()
        self.rect = self.window.get_rect()
        self.state = Walkaround(self)
        self.running = True

    async def run(self, fps):
        frame = aio.ensure_future(self.state.draw_frame())
        frate = 0.9875 / fps
        ptime = time()
        while self.running:
            await self.state.eval_logic()
            await aio.sleep(max(0, frate - (time() - ptime)))
            ptime = time()
            if frame.done():
                frame = aio.ensure_future(self.state.draw_frame())


def main():
    pg.init()
    pg.display.set_caption('HSD Walkaround')
    pg.display.set_icon(pg.image.load(os.path.join('assets', 'textures', 'icon.png')))
    pg.display.set_mode((1024, 768), pg.HWSURFACE | pg.DOUBLEBUF)
    aio.run(GameApplication().run(60))
    pg.quit()

if __name__ == '__main__':
    main()
