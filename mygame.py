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
        pygame.font.init()
        self.width = 600
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.timescale = 1
        self.FPS = 60 * self.timescale # FPS and timescale should scale together
        self.playtime = 0
        self.clock = pygame.time.Clock()
        self.bg_color = (0, 0, 0)

        # TODO initiate based off object parameters

        # TODO automate player placement in duel box
        self.players = []
        self.players.append(Player(1, [self.width/2, 100], [self.width, self.height]))
        self.players.append(Player(2, [self.width/2, self.height/2], [self.width, self.height]))

        self.players[0].angle = 45
        
        reference_brick = Brick([0, 0], [0, 0])
        self.brick_graphic_width = reference_brick.width
        self.player_graphic_width = self.players[0].radius * 2

        self.bricks = []
        self.player_boundaries = {'east': 0, 'north': 0, 'west': 0, 'south': 0} # should be 4 integer limits, with cardinal direction identity, for boundary in boundaries.items()
        self.bullet_boundaries = {'east': 0, 'north': 0, 'west': 0, 'south': 0}
        self.generate_duelbox()

    def run(self):

        running = True

        while running:

            milliseconds = self.clock.tick(self.FPS)  # milliseconds passed since last frame
            delta_t = (milliseconds / 1000.0) * self.timescale  # seconds passed since last frame (float)
            self.playtime += delta_t

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # KEYSTROKES & CONTROLS

            keys = pygame.key.get_pressed()

            self.screen.fill(self.bg_color)

            for player in self.players:

                player.current_action = self.keymap(keys, player.alliance)
                player.maneuver(delta_t)
                player.shoot(self.screen, delta_t)
                for shot in player.shots:
                    shot.move(delta_t)

                # TODO center screen on player 1
                # TODO create grid underlay

                if self.detect_collision_player(player):
                    self.detect_collision_player(player)

                player.recharge_energy(delta_t)
                player.draw(self.screen) # draws this player on the screen

            self.check_match_status()

            self.detect_collision_bullet(delta_t)

            for brick in self.bricks:
                brick.draw(self.screen)

            pygame.display.update()

            pygame.display.set_caption(" FPS: {}     TIME: {}".format(self.clock.get_fps(), self.playtime))

    def generate_duelbox(self):

        width_index = int(self.width/self.brick_graphic_width)
        height_index = int(self.height/self.brick_graphic_width) # assumes wall graphic is 32 pixels wide

        for w in range(1, width_index, 1):
            for h in range(1, height_index, 1):
                if w == 1 or h == 1 or w == width_index - 1 or h == height_index - 1:
                    transformed_position = [w * self.brick_graphic_width, -h * self.brick_graphic_width + self.height]
                    self.bricks.append(Brick(transformed_position, [self.width, self.height]))

        # for self.boundaries.items():

        self.player_boundaries['east'] = (width_index - 2.5) * self.brick_graphic_width
        self.player_boundaries['north'] = (height_index - 2.5) * self.brick_graphic_width
        self.player_boundaries['west'] = 2.5 * self.brick_graphic_width
        self.player_boundaries['south'] = 2.5 * self.brick_graphic_width

        self.bullet_boundaries['east'] = (width_index - 1.5) * self.brick_graphic_width
        self.bullet_boundaries['north'] = (height_index - 1.5) * self.brick_graphic_width
        self.bullet_boundaries['west'] = 1.5 * self.brick_graphic_width
        self.bullet_boundaries['south'] = 1.5 * self.brick_graphic_width

    def detect_collision_player(self, player):

        damping_coefficient = 0.5

        if player.position[0] < self.player_boundaries['west']: #left wall collision

            delta_x = self.player_boundaries['west'] - player.position[0]
            velocity_slope = player.velocity[1]/player.velocity[0]
            delta_y = delta_x * velocity_slope
            collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]


            collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2)/player.calc_speed()

            new_velocity = [-player.velocity[0]*damping_coefficient, player.velocity[1]*damping_coefficient]

            new_position = [collision_coordinate[0]+new_velocity[0]*collision_penetration_ratio,
                            collision_coordinate[1]+new_velocity[1]*collision_penetration_ratio]

            player.velocity = new_velocity
            player.position = new_position

            return True

        elif player.position[0] > self.player_boundaries['east']:  # left wall collision

            delta_x = self.player_boundaries['east'] - player.position[0]
            velocity_slope = player.velocity[1] / player.velocity[0]
            delta_y = delta_x * velocity_slope
            collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

            collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

            new_velocity = [-player.velocity[0] * damping_coefficient, player.velocity[1] * damping_coefficient]

            new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                            collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

            player.velocity = new_velocity
            player.position = new_position

            return True

        elif player.position[1] > self.player_boundaries['north']:  # left wall collision

            delta_y = self.player_boundaries['north'] - player.position[1]
            inv_velocity_slope = player.velocity[0] / player.velocity[1]
            delta_x = delta_y * inv_velocity_slope
            collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

            collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

            new_velocity = [player.velocity[0] * damping_coefficient, -player.velocity[1] * damping_coefficient]

            new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                            collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

            player.velocity = new_velocity
            player.position = new_position

            return True

        elif player.position[1] < self.player_boundaries['south']:  # left wall collision

            delta_y = self.player_boundaries['south'] - player.position[1]
            inv_velocity_slope = player.velocity[0] / player.velocity[1]
            delta_x = delta_y * inv_velocity_slope
            collision_coordinate = [player.position[0] + delta_x, player.position[1] + delta_y]

            collision_penetration_ratio = math.sqrt(delta_x ** 2 + delta_y ** 2) / player.calc_speed()

            new_velocity = [player.velocity[0] * damping_coefficient, -player.velocity[1] * damping_coefficient]

            new_position = [collision_coordinate[0] + new_velocity[0] * collision_penetration_ratio,
                            collision_coordinate[1] + new_velocity[1] * collision_penetration_ratio]

            player.velocity = new_velocity
            player.position = new_position

            return True

        else:
            return False

    def detect_collision_bullet(self, delta_t):
        """
        sense player hit
            apply damage
            vanish
        sense wall hit
            vanish
        :return:
        """

        for player in self.players:

            refreshed_shots = []

            for shot in player.shots:

                refreshed_bullets = []

                player_hit_bool = False

                for bullet in shot.bullets:

                    wall_hit_bool = False

                    for other_player in self.players:
                        if other_player != player:
                            if distance(bullet.position, other_player.position) < self.player_graphic_width/2 and player_hit_bool == False:
                                player_hit_bool = True
                                other_player.get_hit()

                    if bullet.position[0] < self.bullet_boundaries['west']            \
                        or bullet.position[0] > self.bullet_boundaries['east']        \
                        or bullet.position[1] < self.bullet_boundaries['south']       \
                        or bullet.position[1] > self.bullet_boundaries['north']:

                        wall_hit_bool = True

                    if wall_hit_bool == False:
                        refreshed_bullets.append(bullet)

                shot.bullets = refreshed_bullets

                if player_hit_bool == False and len(shot.bullets) != 0 and shot.bullet_lifetime > 0:
                    shot.bullet_lifetime -= delta_t
                    refreshed_shots.append(shot)
                else:
                    shot.hit()

            player.shots = refreshed_shots

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

    def check_match_status(self):
        living_players = 0
        lingering_shots = 0
        for player in self.players:
            if player.alive:
                living_players += 1
            else:
                lingering_shots = len(player.shots)

        if living_players < 2 and lingering_shots == 0:

            winning_alliance = 0

            for player in self.players:
                if player.alive:
                    player.record += 1
                    winning_alliance = player.alliance

            if winning_alliance == 0:
                print('MATCH TIE')
            else:
                print('PLAYER %d WINS' % winning_alliance)

            #print('match is over')
            #reward living player (if any) with point
            #announce winner
            #countdown to new match




