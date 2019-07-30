
from livewires import games, color
import math
import random

games.init(screen_width=640, screen_height=480, fps=50)


class Wrapper(games.Sprite):
    """ Огибатель. Спрайт, который, двигаясь, огибает графический экран. """
    def update(self):
        """ Переносит спрайт на противоположную сторону окна. """
        if self.top > games.screen.height:
            self.bottom = 0
        if self.bottom < 0:
            self.top = games.screen.height
        if self.left > games.screen.width:
            self.right = 0
        if self.right < 0:
            self.left = games.screen.width

    def die(self):
        """ Разрушает объект. """
        self.destroy()


class Collider(Wrapper):
    """ Погибатель. Спрайт, который, двигаясь, огибает графический экран и при столкновении гибнет. """
    def update(self):
        """ Проверяет, нет ли спрайтов, визуально перекрывающихся с данным. """
        super(Collider, self).update()
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()

    def die(self):
        """ Разрушает объект со взрывом. """
        new_explosion = Explosion(x=self.x, y=self.y)
        games.screen.add(new_explosion)
        self.destroy()


class Ship(Collider):
    """ Корабль игрока. """
    image = games.load_image("ship.bmp")
    ROTATION_STEP = 3
    VALIOCITY_STEP = .03
    VALIOCITY_MAX = 3
    MISSILE_DELAY = 25
    sound = games.load_sound("thrust.wav")

    def __init__(self, game, x, y):
        """ Инициализирует спрайт с изображением космического корабля. """
        self.game = game
        super(Ship, self).__init__(image=Ship.image, x=x, y=y)
        self.missile_wait = 0

    def update(self):
        """ Вращает корабль при нажатии клавиш со стрелками. """
        super(Ship, self).update()
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_UP):
            Ship.sound.play()
            # изменение горизонтальной и верикальной скорости корабля с учетом угла поворота
            angle = self.angle * math.pi / 180  # преобразование в радианы
            self.dx += Ship.VALIOCITY_STEP * math.sin(angle)
            self.dy += Ship.VALIOCITY_STEP * -math.cos(angle)

        # если нажат пробел выпустить ракету
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)
            self.missile_wait = Ship.MISSILE_DELAY

        # если запуск ракеты пока еще не разрешен, вычесть 1 из длины оставшегося интервала ожидания
        if self.missile_wait > 0:
            self.missile_wait -= 1

        # ограничение горизонтальной и вертикальной скорости
        self.dx = min(max(self.dx, -Ship.VALIOCITY_MAX), Ship.VALIOCITY_MAX)
        self.dy = min(max(self.dy, -Ship.VALIOCITY_MAX), Ship.VALIOCITY_MAX)

    def die(self):
        """ Разрушает корабль и завершает игру. """
        self.game.end()
        super(Ship, self).die()


class Missile(Collider):
    """ Ракета, которую может выпустить корабль игрока """
    image = games.load_image("missile.bmp")
    sound = games.load_sound("missile.wav")
    BUFFER = 40
    VELIOCITY_FACTOR = 7
    LIFETIME = 40

    def __init__(self, ship_x, ship_y, ship_angle):
        """ Инициализирует спрайт с изображением ракеты """
        Missile.sound.play()
        # преобразование в радианы
        angle = ship_angle * math.pi / 180
        # вычисление начальной позиции ракеты
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y
        # вычисление горизонтальной и вертикальной скорости ракеты
        dx = Missile.VELIOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELIOCITY_FACTOR * -math.cos(angle)
        # вызываю конструктор Sprite
        super(Missile, self).__init__(image=Missile.image,
                                      x=x,
                                      y=y,
                                      dx=dx,
                                      dy=dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        """ Перемещаем ракету. """
        super(Missile, self).update()
        # если "срок годности" ракеты истек, она уничтожается
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Explosion(games.Animation):
    """ Анимированный взрыв. """
    sound = games.load_sound("explosion.wav")
    images = ["explosion1.bmp",
              "explosion2.bmp",
              "explosion3.bmp",
              "explosion4.bmp",
              "explosion5.bmp",
              "explosion6.bmp",
              "explosion7.bmp",
              "explosion8.bmp",
              "explosion9.bmp"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images=Explosion.images,
                                        x=x, y=y,
                                        repeat_interval=4, n_repeats=1,
                                        is_collideable=False)
        Explosion.sound.play()


class Asteroid(Wrapper):
    """ Астероид, прямолинейно движущийся по экрану """

    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    POINTS = 30
    images = {SMALL: games.load_image("asteroid_small.bmp"),
              MEDIUM: games.load_image("asteroid_med.bmp"),
              LARGE: games.load_image("asteroid_big.bmp")}
    SPEED = 2
    SPAWN = 2
    total = 0

    def __init__(self, game, x, y, size):
        """ Инициализирует спрайт с изображением астероида """
        Asteroid.total += 1
        self.game = game
        super(Asteroid, self).__init__(
            image=Asteroid.images[size],
            x=x,
            y=y,
            dx=random.choice([1, -1]) * Asteroid.SPEED * random.random()/size,
            dy=random.choice([1, -1]) * Asteroid.SPEED * random.random() / size,
        )
        self.size = size

    def die(self):
        """ Разрушает астероид. """
        Asteroid.total -= 1
        # если размеры астероида крупные или средние, разделить его на два более мелких
        self.game.score.value += int(Asteroid.POINTS / self.size)
        self.game.score.right = games.screen.width - 10
        if self.size != Asteroid.SMALL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game=self.game, x=self.x, y=self.y, size=self.size-1)
                games.screen.add(new_asteroid)
        super(Asteroid, self).die()
        # если больше астероидов не осталось, переходим на следующий уровень
        if Asteroid.total == 0:
            self.game.advance()


class Game(object):
    """ Собственно игра. """
    def __init__(self):
        """ Инициализирует объект Game. """
        # выбор начального игрового уровня
        self.level = 0
        # загрузка звука, сопровождающего переход на новый уровень
        self.sound = games.load_sound("level.wav")
        # создание объекта, в котором будет храниться текущий счет
        self.score = games.Text(value=0,
                                size=30,
                                color=color.white,
                                top=5,
                                right=games.screen.width - 10,
                                is_collideable=False)
        games.screen.add(self.score)
        # создание корабля, которым будет управлять игрок
        self.ship = Ship(game=self,
                         x=games.screen.width/2,
                         y=games.screen.height/2)
        games.screen.add(self.ship)

    def advance(self):
        """ Переводит игру на очередной уровень. """
        self.level += 1
        # зарезервированное пространство вокруг корабля
        BUFFER = 150
        # создание новых астероидов
        for i in range(self.level):
            # вычислим x и y, чтобы от корабля они отстояли минимум на BUFFER пикселов
            # сначала выберем минимельные отступы по горизонтали и вертикали
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min
            # исходя из этих минимумов, сгенерируем расстояния от корабля по горизонтали и вертикали
            x_distance = random.randrange(x_min, games.screen.width - x_min)
            y_distance = random.randrange(y_min, games.screen.height - y_min)
            # исходя из этих расстояний вычислим экранные координаты
            x = self.ship.x + x_distance
            y = self.ship.y + y_distance
            # если необходимо, вернем объект внутрь окна
            x %= games.screen.width
            y %= games.screen.height
            # создадим астероид
            new_asteroid = Asteroid(game=self, x=x, y=y, size=Asteroid.LARGE)
            games.screen.add(new_asteroid)
        # отображение номера уровня
        level_message = games.Message(value="Уровень " + str(self.level),
                                      size=40,
                                      color=color.yellow,
                                      x=games.screen.width/2,
                                      y=games.screen.width/10,
                                      lifetime=3 * games.screen.fps,
                                      is_collideable=False)
        games.screen.add(level_message)
        # звуковой эффект перехода (кроме 1-го уровня)
        if self.level > 1:
            self.sound.play()

    def end(self):
        """ Завершает игру. """
        # 5-секундное отображение 'Game Over'
        end_message = games.Message(value="Game Over",
                                    size=90,
                                    color=color.red,
                                    x=games.screen.width/2,
                                    y=games.screen.width/3,
                                    lifetime=5 * games.screen.fps,
                                    after_death=games.screen.quit,
                                    is_collideable=False)
        games.screen.add(end_message)

    def play(self):
        """ Начинает игру. """
        # запуск музыкальной темы
        games.music.load("theme.mid")
        games.music.play(-1)
        # загрузка и назначение фоновой картинки
        nebula_image = games.load_image("nebula.jpg")
        games.screen.background = nebula_image
        # переход к уровню 1
        self.advance()
        # начало игры
        games.screen.mainloop()


def main():
    astrocrash = Game()
    astrocrash.play()


if __name__ == '__main__':
    main()
