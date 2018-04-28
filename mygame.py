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

    def __init__(self, demo_toggle):
        pygame.init()
        pygame.font.init()
        self.width = 1000
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.timescale = 1
        self.FPS = 60 * self.timescale # FPS and timescale should scale together
        self.playtime = 0
        self.clock = pygame.time.Clock()
        self.bg_color = (0, 0, 0)

        # TODO initiate based off object parameters

        # TODO automate player placement in duel box
        self.players = []
        self.players.append(Player(1, [self.width/2, self.height/2], [self.width, self.height]))
        self.players.append(Player(2, [self.width/2, self.height/2], [self.width, self.height]))

        self.players[0].angle = 0
        self.players[1].angle = 0

        reference_brick = Brick([0, 0], [0, 0])
        self.brick_graphic_width = reference_brick.width
        self.player_graphic_width = self.players[0].radius * 2

        self.bricks = []
        self.player_boundaries = {'east': 0, 'north': 0, 'west': 0, 'south': 0} # should be 4 integer limits, with cardinal direction identity, for boundary in boundaries.items()
        self.bullet_boundaries = {'east': 0, 'north': 0, 'west': 0, 'south': 0}
        self.generate_duelbox()
        self.myfont = pygame.font.SysFont('Calibri', 15)
        self.match_active = True
        self.match_counter = 1
        self.restart_timer = 0

        self.duelbox_line_1 = None
        self.duelbox_line_2 = None
        self.duelbox_line_3 = None

        self.error_total = 0
        self.error_prev = 0

        self.error_angle_prev = 0

        self.pwm_pulse_index = 0
        self.pwm_pulse_width = 10 # frames
        self.pwm_pulse_array = [0] * self.pwm_pulse_width
        self.frame_count = 0

        self.viscosity_coefficient = 0.000

        self.distance_prev = 0

        self.demo_toggle = demo_toggle

    def run(self):

        running = True

        while running:

            self.frame_count += 1
            milliseconds = self.clock.tick(self.FPS)  # milliseconds passed since last frame
            delta_t = (milliseconds / 1000.0) * self.timescale  # seconds passed since last frame (float)
            self.playtime += delta_t

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # KEYSTROKES & CONTROLS

            keys = pygame.key.get_pressed()

            self.screen.fill(self.bg_color)

            for brick in self.bricks:
                brick.draw(self.screen)

            for player in self.players:

                if player.alliance == 1:
                    player.current_action = self.keymap(keys, player.alliance)
                else:

                    if self.demo_toggle == 1:
                        player.current_action = self.keymap_auto_1d(delta_t, self.players[0].position[0], self.players[1].position[0])
                    elif self.demo_toggle == 2:
                        player.current_action = self.keymap_auto_2d(delta_t,
                                                                    self.players[0].position[0],
                                                                    self.players[0].position[1],
                                                                    self.players[1].position[0],
                                                                    self.players[1].position[1])
                    elif self.demo_toggle == 3:
                        player.current_action = self.keymap_auto_2d_combat(delta_t,
                                                                    self.players[0].position[0],
                                                                    self.players[0].position[1],
                                                                    self.players[1].position[0],
                                                                    self.players[1].position[1])
                    else:
                        print("ERROR: demo toggle input must be 1, 2, or 3")
                        exit()



                player.damp(self.viscosity_coefficient)
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

            self.check_match_status(delta_t)

            self.detect_collision_bullet(delta_t)

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

    def keymap(self, keys, alliance):

        """
        :param keys: key strokes
        :param alliance: identifies player 1 or 2
        :return: a dictionary mapping specific actions to -1, 0, or 1
        """

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

    def keymap_auto_1d(self, delta_t, x_target, x_agent):

        """
        :param x_target: other player's x coordinate
        :param x_agent: this player's x coordinate
        :param keys: key strokes
        :return: a dictionary mapping specific actions to -1, 0, or 1
        """

        error = x_agent - x_target
        self.error_total += error * delta_t
        error_rate = (error - self.error_prev) / delta_t
        self.error_prev = error

        # TODO tune gains
        kp = 15
        ki = 1
        kd = 50

        instant_pid_sum = (kp * error) + (ki * self.error_total) + (kd * error_rate)

        if self.frame_count % self.pwm_pulse_width == 0:
            # TODO replace 100 with some variable normalizer, tune viscosity coefficient
            throttle_dutycycle = instant_pid_sum/10000

            self.generate_pwm_pulse(throttle_dutycycle)
            self.pwm_pulse_index = 0

            # print(self.players[1].calc_speed() / self.players[1].max_speed)
            # print(viscous_dutycycle)


        # print(error, "   ", self.error_total, "   ", error_rate)
        # print(instant_pid_sum)

        turn = 0
        throttle = self.pwm_pulse_array[self.pwm_pulse_index]
        afterburn = 0
        trigger = 0

        self.pwm_pulse_index += 1

        actions = {'turn': turn, 'throttle': throttle, 'afterburn': afterburn, 'trigger': trigger}

        return actions

    def keymap_auto_2d(self, delta_t, x_target, y_target, x_agent, y_agent):

        """
        :param x_target: other player's x coordinate
        :param x_agent: this player's x coordinate
        :param keys: key strokes
        :return: a dictionary mapping specific actions to -1, 0, or 1
        """

        f_offset = 50 # future frames
        x_target += (self.players[0].velocity[0] - self.players[1].velocity[0]) * delta_t * f_offset
        y_target += (self.players[0].velocity[1] - self.players[1].velocity[1]) * delta_t * f_offset

        distance_magnitude = distance([x_target, y_target], [x_agent, y_agent])

        # agent to target unit vector
        if distance_magnitude != 0:
            target_unit_vector = [(x_target - x_agent) / distance_magnitude, (y_target - y_agent) / distance_magnitude]
        else:
            target_unit_vector = [0, 0]

        # agent direction unit vector
        agent_unit_vector = [math.cos(math.radians(self.players[1].angle)), math.sin(math.radians(self.players[1].angle))]
        # error angle between two direction vectors
        dot_product = target_unit_vector[0] * agent_unit_vector[0] + target_unit_vector[1] * agent_unit_vector[1]
        error_angle = math.degrees(math.acos(dot_product))

        # increment agent angle and sample recalculated error angle -- identifies whether to turn left or right
        pos_inc_agent_unit_vector = [math.cos(math.radians(self.players[1].angle + 0.1)), math.sin(math.radians(self.players[1].angle + 0.1))]
        pos_inc_dot_product = target_unit_vector[0] * pos_inc_agent_unit_vector[0] + target_unit_vector[1] * pos_inc_agent_unit_vector[1]
        pos_inc_error_angle = math.degrees(math.acos(pos_inc_dot_product))
        positive_turn_bool = pos_inc_error_angle < error_angle

        error_angle_rate = (error_angle - self.error_angle_prev) / delta_t
        self.error_angle_prev = error_angle

        kp_angle = 1
        kd_angle = 0.05

        angle_pid_sum = (kp_angle * error_angle) + (kd_angle * error_angle_rate)


        error = - distance_magnitude
        self.error_total += error * delta_t
        error_rate = (error - self.error_prev) / delta_t
        self.error_prev = error


        # error = x_agent - x_target
        # self.error_total += error * delta_t
        # error_rate = (error - self.error_prev) / delta_t
        # self.error_prev = error

        kp = 30
        ki = 30
        kd = 20

        distance_pid_sum = (kp * error) + (ki * self.error_total) + (kd * error_rate)

        if self.frame_count % self.pwm_pulse_width == 0:

            throttle_dutycycle = distance_pid_sum/10000

            self.generate_pwm_pulse(throttle_dutycycle)
            self.pwm_pulse_index = 0


        if positive_turn_bool and angle_pid_sum > 0 and error_angle > 5:
            turn = 1
        elif positive_turn_bool and angle_pid_sum < 0 and error_angle > 5:
            turn = -1
        elif not positive_turn_bool and angle_pid_sum > 0 and error_angle > 5:
            turn = -1
        elif not positive_turn_bool and angle_pid_sum < 0 and error_angle > 5:
            turn = 1
        else:
            turn = 0

        # if positive_turn_bool:
        #     turn = 1
        # elif not positive_turn_bool:
        #     turn = -1
        # else:
        #     turn = 0

        if angle_pid_sum < 50:
            throttle = self.pwm_pulse_array[self.pwm_pulse_index]
        else:
            throttle = 0


        # TODO toggles
        # turn = 0
        # throttle = 0
        trigger = 0
        afterburn = 0

        self.pwm_pulse_index += 1

        actions = {'turn': turn, 'throttle': throttle, 'afterburn': afterburn, 'trigger': trigger}

        return actions

    def keymap_auto_2d_combat(self, delta_t, x_target, y_target, x_agent, y_agent):

        """
        delta_t == seconds per frame
        """

        distance_magnitude = distance([x_target, y_target], [x_agent, y_agent])
        distance_rate = (distance_magnitude - self.distance_prev) / delta_t # error is negative, [pixels per second]
        self.distance_prev = distance_magnitude

        if distance_rate != 0:
            t_future = distance_magnitude / (500 - distance_rate)
        else:
            t_future = 0

        x_target += (self.players[0].velocity[0] - self.players[1].velocity[0]) * t_future
        y_target += (self.players[0].velocity[1] - self.players[1].velocity[1]) * t_future


        # num_future_frames = 40 # future frames
        # x_target += (self.players[0].velocity[0] - self.players[1].velocity[0]) * delta_t * num_future_frames
        # y_target += (self.players[0].velocity[1] - self.players[1].velocity[1]) * delta_t * num_future_frames


        distance_magnitude = distance([x_target, y_target], [x_agent, y_agent])

        # agent to target unit vector
        if distance_magnitude != 0:
            target_unit_vector = [(x_target - x_agent) / distance_magnitude, (y_target - y_agent) / distance_magnitude]
        else:
            target_unit_vector = [0, 0]

        # agent direction unit vector
        agent_unit_vector = [math.cos(math.radians(self.players[1].angle)), math.sin(math.radians(self.players[1].angle))]
        # error angle between two direction vectors
        dot_product = target_unit_vector[0] * agent_unit_vector[0] + target_unit_vector[1] * agent_unit_vector[1]
        error_angle = math.degrees(math.acos(dot_product))

        # increment agent angle and sample recalculated error angle -- identifies whether to turn left or right
        pos_inc_agent_unit_vector = [math.cos(math.radians(self.players[1].angle + 0.1)), math.sin(math.radians(self.players[1].angle + 0.1))]
        pos_inc_dot_product = target_unit_vector[0] * pos_inc_agent_unit_vector[0] + target_unit_vector[1] * pos_inc_agent_unit_vector[1]
        pos_inc_error_angle = math.degrees(math.acos(pos_inc_dot_product))
        positive_turn_bool = pos_inc_error_angle < error_angle

        error_angle_rate = (error_angle - self.error_angle_prev) / delta_t
        self.error_angle_prev = error_angle

        kp_angle = 1
        kd_angle = 0

        angle_pid_sum = (kp_angle * error_angle) + (kd_angle * error_angle_rate)


        error = -distance_magnitude
        self.error_total += error * delta_t
        error_rate = (error - self.error_prev) / delta_t
        self.error_prev = error

        kp = 30
        ki = 1
        kd = 50

        distance_pid_sum = 5000 + (kp * error) + (ki * self.error_total) + (kd * error_rate)

        if self.frame_count % self.pwm_pulse_width == 0:

            throttle_dutycycle = distance_pid_sum/10000

            self.generate_pwm_pulse(throttle_dutycycle)
            self.pwm_pulse_index = 0


        if positive_turn_bool and angle_pid_sum > 0 and error_angle > 1:
            turn = 1
        elif positive_turn_bool and angle_pid_sum < 0 and error_angle > 1:
            turn = -1
        elif not positive_turn_bool and angle_pid_sum > 0 and error_angle > 1:
            turn = -1
        elif not positive_turn_bool and angle_pid_sum < 0 and error_angle > 1:
            turn = 1
        else:
            turn = 0

        # if positive_turn_bool:
        #     turn = 1
        # elif not positive_turn_bool:
        #     turn = -1
        # else:
        #     turn = 0

        if angle_pid_sum < 50:
            throttle = self.pwm_pulse_array[self.pwm_pulse_index]
        else:
            throttle = 0

        if error_angle < 1:
            trigger = 1
        else:
            trigger = 0

        # TODO toggles
        # turn = 0
        # throttle = 0
        # trigger = 0

        afterburn = 0



        self.pwm_pulse_index += 1

        actions = {'turn': turn, 'throttle': throttle, 'afterburn': afterburn, 'trigger': trigger}

        return actions

    def generate_pwm_pulse(self, throttle_dutycycle):

        """ prepares the next pulse, summing throttle and viscous forces """

        throttle_frames = round(throttle_dutycycle*self.pwm_pulse_width)

        if throttle_frames > self.pwm_pulse_width:
            throttle_frames = self.pwm_pulse_width
        elif throttle_frames < -self.pwm_pulse_width:
            throttle_frames = -self.pwm_pulse_width

        for i in range(self.pwm_pulse_width):
            self.pwm_pulse_array[i] = 0

        if throttle_frames > 0:
            for i in range(throttle_frames):
                self.pwm_pulse_array[i] += -1
        else:
            for i in range(-throttle_frames):
                self.pwm_pulse_array[i] += 1


    def check_match_status(self, delta_t):

        if self.match_active:

            self.duelbox_line_2 = self.myfont.render('MATCH ' + str(self.match_counter) + ' IN PROGRESS', False, (255, 255, 255))

            living_players = 0
            lingering_shots = 0
            for player in self.players:
                if player.alive:
                    living_players += 1
                else:
                    lingering_shots = len(player.shots)

            if living_players < 2 and lingering_shots == 0:

                self.match_active = False

                self.restart_timer = 3

                winning_alliance = 0

                for player in self.players:
                    if player.alive:
                        player.record += 1
                        winning_alliance = player.alliance

                if winning_alliance == 0:
                    self.duelbox_line_2 = self.myfont.render('MATCH TIE', False, (255, 255, 255))
                else:
                    self.duelbox_line_2 = self.myfont.render('PLAYER ' + str(winning_alliance) + ' WINS', False, (255, 255, 255))

                self.match_counter += 1
        else:
            self.duelbox_line_3 = self.myfont.render('NEXT ROUND IN ' + str(int(self.restart_timer)), False, (255, 255, 255))
            self.restart_timer -= delta_t
            draw_centered(self.duelbox_line_3, self.screen, [self.width / 2, 140])

        self.duelbox_line_1 = self.myfont.render(
            'PLAYER 1:' + str(self.players[0].record) + '      PLAYER 2:' + str(self.players[1].record), False,
            (255, 255, 255))
        draw_centered(self.duelbox_line_1, self.screen, [self.width / 2, 100])

        draw_centered(self.duelbox_line_2, self.screen, [self.width / 2, 120])

        if self.restart_timer < 0:
            self.restart_timer = 0
            self.restart()

    def restart(self):
        self.match_active = True
        for player in self.players:
            player.revive()

        self.players[0].position = [100,100]
        self.players[0].angle = 225

        self.players[1].position = [self.width - 150, self.height - 150]
        self.players[1].angle = 45


            #print('match is over')
            #reward living player (if any) with point
            #announce winner
            #countdown to new match




