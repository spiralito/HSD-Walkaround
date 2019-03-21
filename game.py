#!/usr/bin/env python
import os
from time import time
import pygame as pg
import asyncio as aio
from boilerplate import (
    load_image, ClipDrawSprite, ClipDrawGroup,
    GameState,
    )


class Walkaround(GameState):
    def __init__(self, handler):
        super().__init__(handler)
        self.sprite = load_image('sprites.png', colorkey=0xFF00FF)

    async def eval_logic(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.handler.running = False

    async def draw_frame(self):
        self.handler.window.blit(self.sprite, (0, 0, 32, 32))
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
