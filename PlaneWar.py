import pygame
from pygame.locals import *
# import sys
import random
# import time


def key_control(hero):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("exit")
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_a or event.key == K_LEFT:
                hero.key_down(K_LEFT)
            elif event.key == K_d or event.key == K_RIGHT:
                hero.key_down(K_RIGHT)
            elif event.key == K_w or event.key == K_UP:
                hero.key_down(K_UP)
            elif event.key == K_s or event.key == K_DOWN:
                hero.key_down(K_DOWN)
            elif event.key == K_SPACE:
                hero.fire()
            elif event.key == K_b:
                print(enemy_bullet_list)
                hero.bomb()
        # 检测按键弹开
        elif event.type == pygame.KEYUP:
            # 是否为left
            if event.key == K_LEFT or event.key == K_a:
                hero.key_up(K_LEFT)
            # 检测按键是否是right
            elif event.key == K_RIGHT or event.key == K_d:
                hero.key_up(K_RIGHT)
            # 检测按键是否是up
            elif event.key == K_UP or event.key == K_w:
                hero.key_up(K_UP)
            # 检测按键是否是down
            elif event.key == K_DOWN or event.key == K_s:
                hero.key_up(K_DOWN)


class Base(object):
    def __init__(self, screen_temp, x, y, image_name, picture_num, hp):
        self.x = x
        self.y = y
        self.screen = screen_temp
        self.image = pygame.image.load(image_name)
        self.hp = hp

        self.hit = False  # 是否被击
        self.normal_picture_list = []  # 序列动画保存
        self.reverse_picture_list = []  # 反向动画保存
        self.boom_picture_num = picture_num  # 有几帧
        self.image_num = 0  # 动画播放间隔
        self.image_index = 0  # 当前动画帧
        self.key_down_list = []  # 按键保存
        self.Rect_parameter = ()

    def create_rect(self):
        """
        创建碰撞矩形
        :return:
        """
        rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        return rect

    def draw_rect(self):
        """
        画出碰撞矩形
        """
        pygame.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.image.get_width(), self.image.get_height()), 1)

    def collision(self, collider, collider_tick):
        """
        碰撞判断
        :param collider: 碰撞单位
        :param collider_tick: 碰撞次数
        """
        # 直接调用矩形碰撞检测，碰撞单位.hp 减去 损伤
        if self.create_rect().colliderect(collider.create_rect()):
            # print("???")
            collider.hit = True
            self.hit = True
            collider.hp -= self.damage
            self.hp -= collider.damage
            self.collider_tick -= 1
            print('???',self.collider_tick)

    # 预加载动画，正反两套（内存开销巨大）
    def create_image(self, boom_image_name):
        for i in range(1, self.boom_picture_num + 1):
            self.normal_picture_list.append(
                pygame.image.load(r'C:\Users\22684\Desktop\\' + boom_image_name + '\\' + str(i) + '.png'))
        for image in self.normal_picture_list:
            self.reverse_picture_list.append(pygame.transform.flip(image, True, False))


class PlaneBase(Base):
    def __init__(self, screen_temp, x, y, image_name, picture_num, hp):
        Base.__init__(self, screen_temp, x, y, image_name, picture_num, hp)
        self.direction = 1
        self.score_get = hp
        self.damage = 0
        global bullet_list
        global hero_bullet_list
        global enemy_bullet_list

    def display(self):
        """
        播放动画还是显示原图，可以扩展一下做动画包
        """
        global score
        # 如果hp<0就播放动画
        if self.hp <= 0:

            # 通过方向播放对应方向的动画
            if self.direction == 1:
                self.screen.blit(self.normal_picture_list[self.image_index], (self.x, self.y))
            else:
                self.screen.blit(self.reverse_picture_list[self.image_index], (self.x, self.y))

            # 调整 image_num 来控制动画播放间隔
            self.image_num += 1
            if self.image_num > 2:
                self.image_index += 1
                self.image_num = 0

            # 播放完成后将index归0，删除飞机，获取得分
            if self.image_index > self.boom_picture_num - 1:
                self.image_index = 0

                self.del_plane()
                score += self.score_get
        # 否则显示原图
        else:
            self.screen.blit(self.image, (self.x, self.y))

    def remove_bullet(self, self_bullet_list):
        """
        移除子弹，同时进行碰撞判断
        :param self_bullet_list:是谁的子弹组
        """
        bullet_list_out = []
        # 子弹组中子弹一系列操作
        for bullet in self_bullet_list:
            bullet.move()
            bullet.display()
            bullet.draw_rect()
            bullet.create_rect()

            # 遍历enemy列表进行碰撞判断
            for enemy in enemy_list:
                print(bullet.collider_tick)
                # 碰撞次数
                if bullet.collider_tick != 0:
                    # 对enemy进行碰撞判断
                    bullet.collision(enemy, bullet.collider_tick)

                # 如果敌人列表不为空，则对其子弹进行碰撞检测

                    if enemy.hp != 0:
                        for enemy_bullet in enemy.bullet_list:
                            # 敌方子弹碰撞次数不为0
                            if bullet.collider_tick != 0:
                                # 对我方子弹进行碰撞检测
                                bullet.collision(enemy_bullet, bullet.collider_tick)



            # 遍历enemy1列表
            for enemy1 in enemy1_list:
                bullet.collision(enemy1, bullet.collider_tick)
                if not enemy1.hit:
                    for enemy_bullet in enemy1.bullet_list:
                        enemy_bullet.collision(bullet, enemy_bullet.collider_tick)
            # self.collision()

            # 子弹销毁判断，加入out列表，从list移除
            if bullet.judge():
                bullet_list_out.append(bullet)

        for bullet_out in bullet_list_out:
            self_bullet_list.remove(bullet_out)

    def del_plane(self):
        """
        删除死亡飞机
        """
        global enemy_list
        global hero
        if self in enemy_list:
            # if not self.bullet_list:        #困难模式，子弹不消失击败则飞机变幽灵
            enemy_list.remove(self)

        if self in enemy1_list:
            enemy1_list.remove(self)

        if self == hero:
            # sys.exit()
            # print("hit!!")
            pass


class HeroPlane(PlaneBase):
    def __init__(self, screen_temp):
        self.x = 200
        self.y = 400
        self.image = r"C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\刀魂之卡赞\0.png"
        self.direction = 1
        self.hp = 100
        PlaneBase.__init__(self, screen_temp, self.x, self.y, self.image, 7, self.hp)
        PlaneBase.create_image(self, "刀魂之卡赞")

    def press_move(self):
        """
        按键判断，控制飞机移动
        """
        if len(self.key_down_list) != 0:
            if self.key_down_list[-1] == K_LEFT:
                self.move_left()
            elif self.key_down_list[-1] == K_RIGHT:
                self.move_right()
            elif self.key_down_list[-1] == K_UP:
                self.move_up()
            elif self.key_down_list[-1] == K_DOWN:
                self.move_down()

    def move_limit(self):
        """
        飞机范围控制
        """
        if self.x < 0:
            self.x = 2
        elif self.x + 50 > 480:
            self.x = 386

    # 键盘按下向列表添加按键
    def key_down(self, key):
        self.key_down_list.append(key)

    # 键盘松开向列表删除按键
    def key_up(self, key):
        if len(self.key_down_list) != 0:  # 判断是否为空
            self.key_down_list.remove(key)

    # 自爆
    def bomb(self):
        self.hit = not self.hit

# 上下左右移动，左右图片转向

    def move_left(self):
        self.x -= 5
        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = -1

    def move_right(self):
        self.x += 5
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 1

    def move_up(self):
        self.y -= 5

    def move_down(self):
        self.y += 5

    # 开火
    def fire(self):
        hero_bullet_list.append(Bullet(self.screen, self.x, self.y))


class EnemyPlane(PlaneBase):

    def __init__(self, screen_temp):
        self.x = random.randint(0, 480)
        self.y = 0
        self.hp = 5
        self.image = r"C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\冰霜之萨亚\0.png"
        PlaneBase.__init__(self, screen_temp, self.x, self.y, self.image, 7, self.hp)
        self.direction = 1  # 飞机默认移动方向
        self.reverse = False    # 飞机贴图控制
        self.bullet_list = []
        PlaneBase.create_image(self, "冰霜之萨亚")

    def move(self):
        """
        飞机移动，左右转向，超出屏幕则删除
        """
        self.y += 0

        # 根据方向转换贴图
        if self.direction == 1:
            self.x += 5
            if self.reverse:
                self.image = pygame.transform.flip(self.image, True, False)
                self.reverse = False
        elif self.direction == -1:
            self.x -= 5
            if not self.reverse:
                self.image = pygame.transform.flip(self.image, True, False)
                self.reverse = True

        # 移动转向
        if self.x > 430:
            self.direction = -1
        elif self.x < 0:
            self.direction = 1

        # 非出屏幕删除
        if self.y > 600:
            self.del_plane()

    def fire(self, max_bullet):
        random_num = random.randint(1, 100)  # 随机的发射子弹
        if (random_num == 8 or random_num == 20) and len(self.bullet_list) < max_bullet:
            self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, 0, 1, 1))

    def remove_bullet(self):
        """
        重构方法，子弹基本属性，只对英雄飞机做碰撞判断
        """
        bullet_list_out = []

        for bullet in self.bullet_list:
            bullet.move()
            bullet.display()
            bullet.draw_rect()
            bullet.create_rect()
            bullet.collision(hero, bullet.collider_tick)


            if bullet.judge():
                bullet_list_out.append(bullet)

        for bullet_out in bullet_list_out:
            self.bullet_list.remove(bullet_out)


class EnemyPlane1(EnemyPlane):
    def __init__(self, screen_temp):
        self.x = 0
        self.y = 50
        self.image = r'C:\Users\22684\Desktop\天四\0.png'     # 图片改变
        PlaneBase.__init__(self, screen_temp, self.x, self.y, self.image, 240)
        self.direction = -1
        self.reverse = False
        PlaneBase.create_image(self, '天四')                  # 动画贴图位置
        self.bullet_list = []

    def fire(self, max_bullet):
        random_num = random.randint(1, 200)  # 随机的发射子弹
        if (random_num == 8 or random_num == 20) and len(self.bullet_list) < max_bullet:
            # 主要是子弹贴图改变,伤害改变，生命值改变
            self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, 1, 5, 2))


class BulletBase(Base):
    def __init__(self, screen_temp, x, y, image_name, hp):
        Base.__init__(self, screen_temp, x, y, image_name, 7, hp)
        self.collider_tick = 1

    def display(self):
        self.screen.blit(self.image, (self.x, self.y))


class Bullet(BulletBase):
    def __init__(self, screen_temp, x, y):
        self.x = x + 30
        self.y = y - 20
        self.hp = 1
        self.image = r"C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\cbmid01.img\ricu_frozentree.img\7.png"
        BulletBase.__init__(self, screen_temp, self.x, self.y, self.image, self.hp)
        self.damage = 1

    def move(self):
        self.y -= 10

    def judge(self):
        if self.y < 0 or self.hp <= 0:
            return True
        else:
            return False
    # def remove_bullet(self):


class EnemyBullet(BulletBase):
    def __init__(self, screen_temp, x, y, mode, damage, hp):
        self.x = x + 25
        self.y = y + 40
        self.damage = damage
        self.hp = hp
        image = [r"C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\cbmid01.img\iceflower.img\3.png",
                 r'C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\cbmid01.img\ricu_tree.img\5.png']
        self.image = image[mode]
        BulletBase.__init__(self, screen_temp, self.x, self.y, self.image, self.hp)

    def move(self):
        self.y += 5

    def judge(self):
        if self.y > 600 or self.hp <= 0:
            return True
        else:
            return False


class Support(BulletBase):
    def __init__(self, screen_temp, x, y, type, speed_temp, type_image, hp_temp):
        self.image = r'C:\Users\22684\Desktop\冥炎之卡洛\\'+str(type_image)+'.png'
        BulletBase.__init__(self, screen_temp, x, y, self.image, hp_temp)
        self.type = type
        self.speed = speed_temp

    def move(self):
        self.y += self.speed

    def judge(self):
        if self.y > 600:
            return True
        else:
            return False


def main():
    global enemy_list
    global max_enemy_number
    global hero
    global socre
    pygame.font.init()
    font = pygame.font.SysFont(None, 50)
    size = (480, 600)
    fps = 30
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size, 0, 32)

    background = pygame.image.load(r"C:\Users\22684\Desktop\dfq\贴图\鬼泣鬼神\cbmid01.img\cbtile.img\1.png")
    background2 = pygame.transform.scale(background, size)

    hero = HeroPlane(screen)
    # enemy = EnemyPlane(screen)
    # enemy.hit = True

    while True:
        clock.tick(fps)
        screen.blit(background2, (0, 0))

        hero.display()
        hero.create_rect()
        hero.draw_rect()
        hero.press_move()
        hero.move_limit()
        hero.remove_bullet(hero_bullet_list)

        screen.blit(font.render('score:' + str(score), -1, (55, 25, 255)), (0, 0))

        random_int = random.randint(1, 100)
        if (random_int == 29 or random_int == 50) and len(enemy_list) < max_enemy_number:
            enemy_list.append(EnemyPlane(screen))

        if (random_int == 36 or random_int == 60) and len(enemy1_list) < max_enemy1_number:
            enemy1_list.append(EnemyPlane1(screen))

        if not support_list:
            random_supply = random.randint(1, 240)
            if random_supply % 239 == 0:
                random_x = random.randint(0, 480-50)
                random_y = random.randint(0, 200)
                random_speed = random.randint(1,5)
                random_hp = random.randint(10,20)
                support_list.append(Support(screen, random_x, random_y, None, random_speed, 6, random_hp))
        if enemy_list:

            for enemy in enemy_list:
                enemy.move()
                enemy.fire(2)
                enemy.display()
                enemy.create_rect()
                enemy.draw_rect()
                enemy.remove_bullet()

        if enemy1_list:
            for enemy1 in enemy1_list:
                enemy1.move()
                enemy1.fire(3)
                enemy1.display()
                enemy1.create_rect()
                enemy1.draw_rect()
                enemy1.remove_bullet()

        if support_list:
            for support in support_list:
                support.move()
                support.judge()
                support.display()
                support.create_rect()
                support.draw_rect()

        key_control(hero)
        pygame.display.update()


if __name__ == '__main__':
    enemy_list = []
    enemy1_list = []
    hero_bullet_list = []
    enemy_bullet_list = []
    bullet_list = []
    support_list = []

    max_enemy_number = 1
    max_enemy1_number = 0
    score = 0
    main()
