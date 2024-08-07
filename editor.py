import sys

import pygame

from instance import Instance
from scripts.assets import AssetTile
from scripts.tile import Tile
from scripts.utils import Key, Mouse, Vec2


class Editor(Instance):
    def __init__(self):
        super().__init__(title='editor', res_base=(320, 180), res_scale=3.0)

        self.binds = (
            Key((pygame.K_a, pygame.K_LEFT), lambda: self.dir.toggle_left(), lambda: self.dir.toggle_left()),
            Key((pygame.K_d, pygame.K_RIGHT), lambda: self.dir.toggle_right(), lambda: self.dir.toggle_right()),
            Key((pygame.K_w, pygame.K_UP), lambda: self.dir.toggle_up(), lambda: self.dir.toggle_up()),
            Key((pygame.K_s, pygame.K_DOWN), lambda: self.dir.toggle_down(), lambda: self.dir.toggle_down()),
            Key(pygame.K_g, lambda: self.toggle_ongrid()),
            Key(pygame.K_t, lambda: self.tilemap.automap()),
            Key(pygame.K_o, lambda: self.tilemap.save('map.json')),
            Key(pygame.K_TAB, lambda: self.scroll_tile_type(1)),
            Mouse(1, lambda: self.toggle_click(), lambda: self.toggle_click()),
            Mouse(3, lambda: self.toggle_r_click(), lambda: self.toggle_r_click()),
            Mouse(4, lambda: self.scroll_tile_var(1)),
            Mouse(5, lambda: self.scroll_tile_var(-1))
        )

        self.tile_group = 0
        self.tile_type = tuple(AssetTile)[self.tile_group]
        self.tile_var = 0
        self.tile_pos = Vec2((0, 0))

        self.mpos = Vec2((0, 0))
        self.click = False
        self.r_click = False
        self.ongrid = True
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

    def toggle_click(self):
        self.click = not self.click
        # This prevents accidental placement of multiple instances.
        if self.click and not self.ongrid:
            self.tilemap.offgrid.append(Tile(self.tile_type, self.tile_var, self.mpos.add(self.scroll)))

    def toggle_r_click(self):
        self.r_click = not self.r_click

    def toggle_ongrid(self):
        self.ongrid = not self.ongrid

    def scroll_tile_type(self, amount):
        self.tile_group = (self.tile_group + amount) % len(AssetTile)
        self.tile_type = tuple(AssetTile)[self.tile_group]
        self.tile_var = 0

    def scroll_tile_var(self, amount):
        self.tile_var = ((self.tile_var + amount) % len(self.assets.get_tiles(self.tile_type)))

    def run(self):
        while True:
            # Order is important here!
            self.clear()
            self.handle_scroll()
            self.handle_tilemap()
            self.handle_positions()
            self.handle_tile_preview()
            self.handle_tile_placement()
            self.handle_tile_removal()
            self.handle_events()
            self.render()

    def handle_scroll(self):
        self.scroll = self.scroll.add(((self.dir.right - self.dir.left) * 5, (self.dir.down - self.dir.up) * 5))
        self.render_scroll = self.scroll.int()

    def handle_tilemap(self):
        self.tilemap.render()

    def handle_positions(self):
        self.mpos = Vec2(pygame.mouse.get_pos()).div(self.RES_SCALE)
        self.tile_pos = (self.mpos.add(self.scroll).div_f(self.tilemap.size).int())

    def handle_tile_preview(self):
        current_tile_img = self.assets.get_tiles(self.tile_type, self.tile_var).copy()
        current_tile_img.set_alpha(155)

        if self.ongrid:
            self.fore_d.blit(current_tile_img, self.tile_pos.mult(self.tilemap.size).sub(self.scroll).tuple())
        else:
            self.fore_d.blit(current_tile_img, self.mpos.tuple())

        self.fore_d.blit(current_tile_img, (5, 5))

    def handle_tile_placement(self):
        if self.click and self.ongrid:
            self.tilemap.tilemap[self.tile_pos.json()] = Tile(self.tile_type, self.tile_var, self.tile_pos)

    def handle_tile_removal(self):
        if self.r_click:
            tile_loc = self.tile_pos.json()

            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]

            for tile in self.tilemap.offgrid.copy():
                tile_img = self.assets.get_tiles(tile.type, tile.var)
                tile_r = pygame.Rect(*tile.pos.sub(self.scroll), *tile_img.get_size())

                if tile_r.collidepoint(self.mpos.tuple()):
                    self.tilemap.offgrid.remove(tile)

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_window(event)

            for bind in self.binds:
                bind.check(event)

    def handle_window(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


Editor().run()
