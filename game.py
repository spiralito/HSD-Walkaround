#!/usr/bin/env python
import os
from time import time
import pygame as pg
import asyncio as aio
from boilerplate import (
    load_image, ClipDrawSprite, ClipDrawGroup,
    InteractibleSprite, TileMapSprite, GameState,
    )

key_config = {
    'U': pg.K_UP,
    'D': pg.K_DOWN,
    'L': pg.K_LEFT,
    'R': pg.K_RIGHT,
    'A': pg.K_z,
    }

class ChestSprite(InteractibleSprite):
    """Contains stuff."""

    def __init__(self, pos, *args):
        super().__init__(
            pg.Rect(0, 0, 68, 44),
            pg.Rect(0, 52, 68, 44),
            pg.Rect(0, 0, 60, 44),
            pg.Rect(0, 0, 50, 44)
            )
        self.rect.bottomright = pos
        self.ibox.bottomright = pos
        self.hitbox.bottomright = (pos[0] - 4, pos[1])
        self.size = (68, 44)
        self.opened = False

    def trigger(self):
        if not self.opened:
            print('You got nothing!')
            self.opened = True
            self.clip.x += self.size[0]

    def update(self):
        pass


class PlayerSprite(ClipDrawSprite):
    """The player character."""

    instance = None
    def __new__(cls, *args):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, pos, *args):
        self.size = (40, 72)
        super().__init__(
            load_image('sprites.png', colorkey=0xFF00FF),
            pg.Rect((0, 0), self.size),
            pg.Rect((0, 0), self.size),
            )
        self.hitbox = pg.Rect(0, 0, 36, 12)
        self.ibox = pg.Rect(0, 0, 4, 72)
        self.rect.midbottom = self.hitbox.midbottom = pos
        # Movement attributes.
        self.dirs = []
        self.vel = [0, 0]
        # Animation attributes.
        self.facing = 0
        self.frame = 0

    def set_motion(self, vdir, press):
        if not press:
            self.dirs.remove(vdir)
            if not self.dirs:
                self.vel = [0, 0]
                return
            vdir = self.dirs[-1]
        else:
            self.dirs.append(vdir)
        self.facing = vdir
        self.vel[~vdir & 1] = 3 * (1, -1)[vdir >> 1]
        self.vel[vdir & 1] = 0

    def interact(self, obj_list):
        index = self.ibox.collidelist([obj.ibox for obj in obj_list[1:]])
        if index >= 0:
            obj_list[index + 1].trigger()

    def update(self, tilemap):
        # Store old position: if collision occurs, reset position.
        oldpos = self.rect.midbottom
        self.hitbox.move_ip(*self.vel)
        if self.hitbox.collidelist(tilemap.collmap) >= 0:
            self.hitbox.midbottom = oldpos
        else:
            self.rect.midbottom = self.hitbox.midbottom
        # Update interaction hitbox.
        self.ibox.size = ((4, 72), (72, 4))[self.facing & 1]
        setattr(
            self.ibox,
            ('midtop', 'midleft', 'midbottom', 'midright')[self.facing],
            self.rect.midbottom
            )
        # Update animation state.
        self.clip.x = self.size[0] * (self.facing * 3 + (1, 0, 2, 0)[self.frame // 10])
        self.frame = (self.frame + 1) % 40 if any(self.vel) else 39


TileMapSprite.sprites = (PlayerSprite, ChestSprite)


class Walkaround(GameState):
    def __init__(self, handler):
        super().__init__(handler)
        self.tilemap = TileMapSprite('testmap.dat')
        self.tilemap.rect.center = self.handler.rect.center
        self.player = self.tilemap.objs[0]

    async def eval_logic(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.handler.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == key_config['U']:
                    self.player.set_motion(2, True)
                elif event.key == key_config['D']:
                    self.player.set_motion(0, True)
                elif event.key == key_config['L']:
                    self.player.set_motion(3, True)
                elif event.key == key_config['R']:
                    self.player.set_motion(1, True)
                elif event.key == key_config['A']:
                    self.player.interact(self.tilemap.objs)
            elif event.type == pg.KEYUP:
                if event.key == key_config['U']:
                    self.player.set_motion(2, False)
                elif event.key == key_config['D']:
                    self.player.set_motion(0, False)
                elif event.key == key_config['L']:
                    self.player.set_motion(3, False)
                elif event.key == key_config['R']:
                    self.player.set_motion(1, False)
        self.player.update(self.tilemap)

    async def draw_frame(self):
        self.window.fill(0x000000)
        self.tilemap.draw(self.window)
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
    InteractibleSprite.sheet = load_image('objects.png', colorkey=0xFF00FF)
    TileMapSprite.tiles = load_image('tiles.png', colorkey=0xFF00FF)
    aio.run(GameApplication().run(60))
    pg.quit()

if __name__ == '__main__':
    main()
