from objects import *


"""
TRANSFORMING IMAGES

DRAWING WITH PYGAME PERFORMS THE FOLLOWING TRANSFORM:

U     1  0
V  *  0 -1

WE MUST COMPENSATE WITH A PRE-TRANSFORM TO END UP WITH A CORRECT IMAGE IN THE VIEWABLE WINDOW

U     1  0     0
V  *  0 -1  -  WIDTH

UPDATE THIS EVERY TICK

"""


class MyGame(object):

    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 1200
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.FPS = 100 # TODO figure out time scale
        self.clock = pygame.time.Clock()
        self.bg_color = (0, 0, 0)

        # TODO automate player placement in duel box
        self.players = []
        self.players.append(Player(1, [100, 100], [self.width, self.height]))
        #self.players.append(Player(2, [self.width/2, -self.height/2]))

        self.bricks = []
        self.boundaries = {'east':0, 'north':0, 'west':0, 'south':0} # should be 4 integer limits, with cardinal direction identity, for boundary in boundaries.items()
        self.generate_duelbox()

    def run(self):

        running = True

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # KEYSTROKES & CONTROLS

            keys = pygame.key.get_pressed()

            self.screen.fill(self.bg_color)

            for player in self.players:

                player.current_action = self.keymap(keys, player.alliance)
                player.maneuver(1/self.FPS)
                player.shoot(self.screen)

                # TODO center screen on player 1
                # TODO create grid underlay
                # TODO downsize warbird png, sync hitbox with image, alpha image

                # draw_centered(player.transform_image(), self.screen, player.transform_position())
                player.draw(self.screen) # draws this player on the screen

            if self.detect_collision():
                self.detect_collision()

            for brick in self.bricks:
                brick.draw(self.screen)

            pygame.display.update()
            self.clock.tick(self.FPS)
            # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

    def generate_duelbox(self):

        graphic_width = 32

        width_index = int(self.width/graphic_width)
        height_index = int(self.height/graphic_width) # assumes wall graphic is 32 pixels wide

        for w in range(1, width_index, 1):
            for h in range(1, height_index, 1):
                if w == 1 or h == 1 or w == width_index-1 or h == height_index-1:
                    self.bricks.append(Brick([w * graphic_width, h * graphic_width], [self.width, self.height]))

        # for self.boundaries.items():

        self.boundaries['east'] = (width_index - 2.5) * graphic_width
        self.boundaries['north'] = (height_index - 2.5) * graphic_width
        self.boundaries['west'] = 2.5 * graphic_width
        self.boundaries['south'] = 2.5 * graphic_width

    def detect_collision(self):

        damping_coefficient = 0.5

        for player in self.players:

            if player.position[0] < self.boundaries['west']: #left wall collision

                delta_x = self.boundaries['west'] - player.position[0]
                velocity_slope = player.velocity[1]/player.velocity[0]
                delta_y = delta_x * velocity_slope
                collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]


                collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2)/player.calc_speed()

                new_velocity = [-player.velocity[0]*damping_coefficient, player.velocity[1]*damping_coefficient]

                new_position = [collision_coordinate[0]+new_velocity[0]*collision_penetration_ratio,
                                collision_coordinate[1]+new_velocity[1]*collision_penetration_ratio]

                player.velocity = new_velocity
                player.position = new_position

            elif player.position[0] > self.boundaries['east']:  # left wall collision

                delta_x = self.boundaries['east'] - player.position[0]
                velocity_slope = player.velocity[1] / player.velocity[0]
                delta_y = delta_x * velocity_slope
                collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

                collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

                new_velocity = [-player.velocity[0] * damping_coefficient, player.velocity[1] * damping_coefficient]

                new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                                collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

                player.velocity = new_velocity
                player.position = new_position

            elif player.position[1] > self.boundaries['north']:  # left wall collision

                delta_y = self.boundaries['north'] - player.position[1]
                inv_velocity_slope = player.velocity[0] / player.velocity[1]
                delta_x = delta_y * inv_velocity_slope
                collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

                collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

                new_velocity = [player.velocity[0] * damping_coefficient, -player.velocity[1] * damping_coefficient]

                new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                                collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

                player.velocity = new_velocity
                player.position = new_position

            elif player.position[1] < self.boundaries['south']:  # left wall collision

                delta_y = self.boundaries['south'] - player.position[1]
                inv_velocity_slope = player.velocity[0] / player.velocity[1]
                delta_x = delta_y * inv_velocity_slope
                collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

                collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

                new_velocity = [player.velocity[0] * damping_coefficient, -player.velocity[1] * damping_coefficient]

                new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                                collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

                player.velocity = new_velocity
                player.position = new_position


            # elif player.position[1] < self.boundaries['south']:  # left wall collision
            #
            #     delta_x = self.boundaries['south'] - player.position[0]
            #     velocity_slope = player.velocity[1] / player.velocity[0]
            #     delta_y = delta_x * velocity_slope
            #     collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]
            #
            #     collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()
            #
            #     new_velocity = [-player.velocity[0] * damping_coefficient, player.velocity[1] * damping_coefficient]
            #
            #     new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
            #                     collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]
            #
            #     player.velocity = new_velocity
            #     player.position = new_position




                # for item in self.boundaries.items():
        #     print(item[1])

            else:
                return False

        return True


    def keymap(self, keys, alliance): #add input for player 1 or 2

        if alliance == 1:
            left_bool = keys[pygame.K_LEFT]
            right_bool = keys[pygame.K_RIGHT]
            up_bool = keys[pygame.K_UP]
            down_bool = keys[pygame.K_DOWN]
            afterburn_bool = keys[pygame.K_LSHIFT]
            trigger_bool = keys[pygame.K_LCTRL]
        elif alliance == 2:
            left_bool = keys[pygame.K_j]
            right_bool = keys[pygame.K_l]
            up_bool = keys[pygame.K_i]
            down_bool = keys[pygame.K_k]
            afterburn_bool = keys[pygame.K_g]
            trigger_bool = keys[pygame.K_b]
        else:
            left_bool = False
            right_bool = False
            up_bool = False
            down_bool = False
            afterburn_bool = False
            trigger_bool = False

        turn = 0
        throttle = 0
        afterburn = 0
        trigger = 0

        if not left_bool and not right_bool:
            turn = 0
        elif left_bool and right_bool:
            turn = 0
        elif left_bool:
            turn = 1
        elif right_bool:
            turn = -1

        if not down_bool and not up_bool:
            throttle = 0
        elif down_bool and up_bool:
            throttle = 0
        elif down_bool:
            throttle = -1
        elif up_bool:
            throttle = 1

        if afterburn_bool:
            afterburn = 1

        if trigger_bool:
            trigger = 1

        actions = {'turn': turn, 'throttle': throttle, 'afterburn': afterburn, 'trigger': trigger}

        return actions




