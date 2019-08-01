import ugame
import stage
import random
import time


class Ship(stage.Sprite):
    def __init__(self):
        super().__init__(tiles, 4, 56, 102)
        self.dx = 0
        self.x = 56
        self.tick = 0
        self.dead = False

    def update(self):
        super().update()
        self.tick = not self.tick

        keys = ugame.buttons.get_pressed()
        self.set_frame(4, 0 if self.tick else 4)
        if keys & ugame.K_RIGHT:
            self.dx = min(self.dx + 1, 4)
            self.set_frame(5, 0)
        elif keys & ugame.K_LEFT:
            self.dx = max(self.dx - 1, -4)
            self.set_frame(5, 4)
        else:
            self.dx = self.dx // 2
        if keys & ugame.K_X:
            if missile.y <= -16:
                missile.move(self.x, self.y)
                sound.play(pew_sound)
            elif missile1.y <= 16:
                missile1.move(self.x, self.y)
                sound.play(pew_sound)
            elif missile2.y <= 16:
                missile2.move(self.x, self.y)
                sound.play(pew_sound)
        if keys & ugame.K_O:
            pause(" Pause...")
        self.x = max(min(self.x + self.dx, 112), 0)
        self.move(self.x, self.y)


class Saucer(stage.Sprite):
    def __init__(self):
        super().__init__(tiles, 9, 0, 0)
        self.tick = 0
        self.dx = 4

    def update(self):
        super().update()
        self.tick = (self.tick + 1) % 6
        self.layer.frame(9, 0 if self.tick >= 3 else 4)
        if self.x >= 128 or self.x <= -16:
            self.dx = -self.dx
        self.move(self.x + self.dx, self.y)
        if abs(self.x - ship.x) < 4 and bomb.y >= 128:
            bomb.move(self.x, self.y)


class Bomb(stage.Sprite):
    def __init__(self):
        super().__init__(tiles, 6, 0, 128)
        self.boom = 0

    def update(self):
        super().update()
        if self.y >= 128:
            return
        if self.boom:
            if self.boom == 1:
                sound.play(boom_sound)
            self.set_frame(12 + self.boom, 0)
            self.boom += 1
            if self.boom > 4:
                self.boom = 0
                ship.dead = True
                self.move(self.x, 128)
            return
        self.move(self.x, self.y + 8)
        self.set_frame(6, 0 if self.y % 16 else 4)
        if stage.collide(self.x + 4, self.y + 4, self.x + 12, self.y + 12,
                         ship.x + 4, ship.y + 4, ship.x + 12, ship.y + 12):
            self.boom = 1


class Missile(stage.Sprite):
    def __init__(self, power):
        super().__init__(tiles, 12, 0, -32)
        self.boom = 0
        self.power = power

    def update(self):
        super().update()
        if self.boom:
            if self.boom == 1:
                sound.play(boom_sound)
            self.set_frame(12 + self.boom)
            self.boom += 1
            if self.boom > 4:
                self.boom = 0
                self.kill()
                aliens.tile(self.ax, self.ay, 0)
                aliens.dirty = True
            return

        if self.y <= -32:
            return
        self.move(self.x, self.y - 8)
        self.set_frame(12 - self.power, 0 if self.y % 16 == 6 else 4)
        self.ax = (self.x + 8 - aliens.x) // 16
        self.ay = (self.y + 4 - aliens.y) // 16
        if aliens.tile(self.ax, self.ay) and (self.x + 10 - aliens.x) % 16 > 4:
            aliens.tile(self.ax, self.ay, 7)
            self.move(self.x, self.y - 4)
            self.boom = 1

    def kill(self):
        self.move(self.x, -32)
        self.set_frame(12 - self.power)


class Aliens(stage.Grid):
    def __init__(self):
        super().__init__(tiles, 7, 3)
        for y in range(3):
            for x in range(7):
                self.tile(x, y, 8)
        self.tick = self.left = self.right = self.descend = 0
        self.dx = 2
        self.dirty = False

    def update(self):
        self.tick = (self.tick + 1) % 4
        self.layer.frame(0, 0 if self.tick >= 2 else 4)
        if self.tick in (0, 2):
            if self.x >= 14 + self.right or self.x <= 2 - self.left:
                self.y += 1
                self.descend += 1
                if self.descend >= 4:
                    self.descend = 0
                    self.dx = -self.dx
                    self.x += self.dx
            else:
                self.x += self.dx
            self.move(self.x, self.y)

    def reform(self):
        self.left = 16 * 6
        self.right = 16 * 6
        for x in range(7):
            for y in range(3):
                if self.tile(x, y):
                    self.left = min(16 * x, self.left)
                    self.right = min(96 - 16 * x, self.right)
        self.dirty = False


def pause(info):
    while ugame.buttons.get_pressed() & ugame.K_O:
        time.sleep(0.25)
    text.cursor(0, 0)
    text.text(info)
    game.render_block()
    while not ugame.buttons.get_pressed() & ugame.K_O:
        time.sleep(0.25)
    text.clear()
    game.render_block()
    while ugame.buttons.get_pressed() & ugame.K_O:
        time.sleep(0.25)


tiles = stage.Bank.from_bmp16("tiles.bmp")
while True:
    space = stage.Grid(tiles)
    aliens = Aliens()
    game = stage.Stage(ugame.display, 12)
    for y in range(8):
        for x in range(8):
            space.tile(x, y, 1)
    for i in range(8):
        space.tile(random.randint(0, 7), random.randint(0, 7),
                   random.randint(2, 3))
    aliens.move(8, 17)
    saucer = Saucer()
    bomb = Bomb()
    ship = Ship()
    missile = Missile(0)
    missile1 = Missile(1)
    missile2 = Missile(2)
    text = stage.Text(9, 1)
    text.move(28, 60)
    sprites = [saucer, bomb, ship, missile, missile1, missile2]
    game.layers = [text] + sprites + [aliens, space]
    game.render_block()
    pew_sound = open("pew.wav", 'rb')
    boom_sound = open("boom.wav", 'rb')
    sound = ugame.audio
    sound.mute(False)

    while aliens.left + aliens.right < 112 and aliens.y < 80 and not ship.dead:
        for sprite in sprites:
            sprite.update()
        aliens.update()
        game.render_sprites(sprites)
        game.render_block(aliens.x + aliens.left - 1, aliens.y - 1,
                          aliens.x + 113 - aliens.right, aliens.y + 48)
        if aliens.dirty:
            aliens.reform()
        game.tick()

    if ship.dead or aliens.y >= 80:
        pause("Game Over")
    else:
        pause("You won!")
