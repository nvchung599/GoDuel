from general import *

# GameObject
# Player, Wall, Bullet      Bullet trail


class GameObject(object):

    def __init__(self, object_image, object_position, object_screen_coord_sys):
        self.image = load_image_convert_alpha(object_image) # the image's forward position should point up/north

        self.screen_coord_sys = object_screen_coord_sys

        self.position = object_position
        self.velocity = [0, 0]
        self.angle = 0

        self.transformed_position = None
        self.transformed_velocity = None
        self.transformed_angle = None

        self.alliance = -1
        # -1: aesthetic object
        # 0: neutral object w/ hit box
        # 1: team 1
        # 2: team 2



    def calc_speed(self):
        return math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

    def predraw_transform(self):
        self.transformed_position = [self.position[0], -self.position[1] + self.screen_coord_sys[1]]
        self.transformed_velocity = [self.velocity[0], self.velocity[1]*-1]
        self.transformed_angle = -self.angle


    # TODO remove this function from repeated execution, store image variable as transformed version
    def transform_object_image(self):
        return rotate_center(self.image, self.angle - 90)

    def transform_position(self):
        return [self.position[0], -self.position[1]]


class Player(GameObject):

    def __init__(self, alliance, position, object_screen_coord_sys):
        super().__init__('player_image.png', position, object_screen_coord_sys)
        self.angle = 90  # should coincide with image file
        self.discreet_angle = 90

        # graphics
        self.image_small_exhaust = load_image_convert_alpha('small_exhaust.png')
        self.image_medium_exhaust = load_image_convert_alpha('medium_exhaust.png')
        self.image_large_exhaust = load_image_convert_alpha('large_exhaust.png')

        # maneuverability
        self.throttle_acceleration = 1000 # units/s^2
        self.throttle_afterburn_acceleration = 2000
        self.turn_speed = 350 # degrees/s
        self.max_speed = 500  # units/s
        self.max_afterburn_speed = 700
        self.current_action = {'throttle': 0, 'turn': 0, 'trigger': 0, 'afterburn':0}

        # game settings
        self.radius = 32
        self.alliance = alliance
        self.shots = []
        self.gun_cool_down_frames = 0

    def predraw_transform(self):
        self.transformed_position = [self.position[0], -self.position[1] + self.screen_coord_sys[1]]
        self.transformed_velocity = [self.velocity[0], self.velocity[1]*-1]
        self.transformed_angle = -self.discreet_angle

    def maneuver(self, time_between_frames):

        # input for either maneuver should be: -1, 0, 1

        if self.current_action['afterburn']:
            instantaneous_max_speed = self.max_afterburn_speed
            instantaneous_accleration = self.throttle_afterburn_acceleration
        else:
            instantaneous_max_speed = self.max_speed
            instantaneous_accleration = self.throttle_acceleration



        self.velocity[0] += math.cos(math.radians(self.discreet_angle))*instantaneous_accleration*time_between_frames*self.current_action['throttle']
        self.velocity[1] += math.sin(math.radians(self.discreet_angle))*instantaneous_accleration*time_between_frames*self.current_action['throttle']

        # max speed check and adjustment



        instantaneous_speed = self.calc_speed()

        if instantaneous_speed > instantaneous_max_speed:
            speed_reduction = instantaneous_max_speed/instantaneous_speed
            self.velocity[0] *= speed_reduction
            self.velocity[1] *= speed_reduction

        self.position[0] += self.velocity[0]*time_between_frames
        self.position[1] += self.velocity[1]*time_between_frames

        self.angle += self.turn_speed*time_between_frames*self.current_action['turn']
        self.discreet_angle = round(self.angle/9)*9


        for shot in self.shots:
            shot.move(time_between_frames)

        # have current pos and vel
        # take input from mygame
        #     decision branch to apply what maneuver
        # apply maneuver, get new pos and vel
        # modify this objects position
        # modify this objects velocity
        # detect collision (call class method)
        #     return collision code
        #     recalculate if wall collision
        #         detect collision again for corner case

    def shoot(self, screen):

        if self.current_action['trigger'] == 1 and self.gun_cool_down_frames == 0:
            self.shots.append(Shot(self.position, self.velocity, self.discreet_angle, self.screen_coord_sys, screen))
            self.gun_cool_down_frames = 20

        elif self.gun_cool_down_frames > 0:
            self.gun_cool_down_frames -= 1



    def draw(self, screen):

        self.predraw_transform()

        draw_centered(self.transform_object_image(), screen, self.transformed_position)
        #draw centered 64x64 image on position coordinates, which are corrected for -Y,

        if self.current_action['throttle'] == 1:
            if self.current_action['afterburn'] == 1:
                rear_exhaust_image = rotate_center(self.image_large_exhaust, self.discreet_angle - 90)
            else:
                rear_exhaust_image = rotate_center(self.image_medium_exhaust, self.discreet_angle - 90)
            rear_exhaust_position = [self.transformed_position[0]+self.radius*math.cos(math.radians(self.transformed_angle + 180)),
                                     self.transformed_position[1]+self.radius*math.sin(math.radians(self.transformed_angle + 180))]
            draw_centered(rear_exhaust_image, screen, rear_exhaust_position)

        elif self.current_action['throttle'] == -1:
            if self.current_action['afterburn'] == 1:
                front_exhaust_image_1 = rotate_center(self.image_medium_exhaust, self.discreet_angle + 70)
                front_exhaust_image_2 = rotate_center(self.image_medium_exhaust, self.discreet_angle + 110)
            else:
                front_exhaust_image_1 = rotate_center(self.image_small_exhaust, self.discreet_angle + 70)
                front_exhaust_image_2 = rotate_center(self.image_small_exhaust, self.discreet_angle + 110)

            front_exhaust_position_1 = [self.transformed_position[0]+self.radius*0.5*math.cos(math.radians(self.transformed_angle + 90)),
                                        self.transformed_position[1]+self.radius*0.5*math.sin(math.radians(self.transformed_angle + 90))]
            front_exhaust_position_2 = [self.transformed_position[0]+self.radius*0.5*math.cos(math.radians(self.transformed_angle - 90)),
                                        self.transformed_position[1]+self.radius*0.5*math.sin(math.radians(self.transformed_angle - 90))]
            draw_centered(front_exhaust_image_1, screen, front_exhaust_position_1)
            draw_centered(front_exhaust_image_2, screen, front_exhaust_position_2)

            # todo counter thrust graphic when turn is terminated
        if self.current_action['turn'] != 0:
            right_exhaust_image = rotate_center(self.image_small_exhaust, self.discreet_angle - 90 * self.current_action['turn'])
            left_exhaust_image = rotate_center(self.image_small_exhaust, self.discreet_angle + 90 * self.current_action['turn'])

            right_exhaust_position = [self.transformed_position[0] + self.radius * math.cos(math.radians(self.transformed_angle + 90)),
                                      self.transformed_position[1] + self.radius * math.sin(math.radians(self.transformed_angle + 90))]
            left_exhaust_position = [self.transformed_position[0] + self.radius * math.cos(math.radians(self.transformed_angle - 90)),
                                     self.transformed_position[1] + self.radius * math.sin(math.radians(self.transformed_angle - 90))]

            draw_centered(right_exhaust_image, screen, right_exhaust_position)
            draw_centered(left_exhaust_image, screen, left_exhaust_position)

        for shot in self.shots:
            shot.draw()

        # given throttle and turn states, also draw exhaust under player image

class Bullet(GameObject):

    def __init__(self, position, velocity, object_screen_coord_sys):
        super().__init__('bullet.png', position, object_screen_coord_sys)
        self.velocity = velocity

    def move(self, time_between_frames):
        self.position = [self.position[0] + self.velocity[0] * time_between_frames,
                         self.position[1] + self.velocity[1] * time_between_frames]

    def hit(self):
        """
        display graphic
        :return:
        """
        None

    def draw(self, screen):
        self.predraw_transform()
        draw_centered(self.transform_object_image(), screen, self.transformed_position)

class Brick(GameObject):
    def __init__(self, position, object_screen_coord_sys):
        super().__init__('wall.png', position, object_screen_coord_sys)
        self.width = 32 # half of player model

    def draw(self, screen):
        self.predraw_transform()
        draw_centered(self.image, screen, self.position)


class Shot(object):
    def __init__(self, position, velocity, angle, object_screen_coord_sys, screen):

        self.screen = screen

        bullet_speed = 500

        #right and left bullets
        bullet_1_position = [position[0] + 25 * math.cos(math.radians(angle - 90)),
                             position[1] + 25 * math.sin(math.radians(angle - 90))]
        bullet_2_position = [position[0] + 25 * math.cos(math.radians(angle + 90)),
                             position[1] + 25 * math.sin(math.radians(angle + 90))]

        bullet_velocity = [bullet_speed * math.cos(math.radians(angle)) + velocity[0],
                           bullet_speed * math.sin(math.radians(angle)) + velocity[1]]

        self.bullet_1 = Bullet(bullet_1_position, bullet_velocity, object_screen_coord_sys)
        self.bullet_2 = Bullet(bullet_2_position, bullet_velocity, object_screen_coord_sys)

    def move(self, time_between_frames):
        self.bullet_1.move(time_between_frames)
        self.bullet_2.move(time_between_frames)
        print(self.bullet_1.velocity)

    def hit(self):
        self.bullet_1.hit()
        self.bullet_2.hit()

    def draw(self):
        self.bullet_1.draw(self.screen)
        self.bullet_2.draw(self.screen)

