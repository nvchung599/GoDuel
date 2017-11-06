from general import *

# GameObject
# TangibleGameObject        AestheticGameObject
# Player, Wall, Bullet      Exhaust, Bullet trail


class GameObject(object):

    def __init__(self, object_image, object_position):
        self.image = load_image_convert_alpha(object_image)
        self.position = object_position
        self.velocity = [0, 0]
        self.angle = 0
        self.alliance = -1
        # -1: aesthetic object
        # 0: neutral object w/ hit box
        # 1: team 1
        # 2: team 2

    def transform_image(self):
        return rotate_center(self.image, self.angle - 90)

    def transform_position(self):
        return [self.position[0], -self.position[1]]


class Player(GameObject):

    def __init__(self, alliance, position):
        super().__init__('player_image.png', position)
        self.angle = 90  # should coincide with image file

        # maneuverability
        self.throttle_acceleration = 1000 # units/s^2
        self.turn_speed = 270 # degrees/s
        self.max_speed = 750  # units/s
        self.current_action = {'throttle': 0, 'turn': 0, 'trigger': 0}

        # game settings
        self.alliance = alliance

    def maneuver(self, time_between_frames):

        # input for either maneuver should be: -1, 0, 1

        self.velocity[0] += math.cos(math.radians(self.angle))*self.throttle_acceleration*time_between_frames*self.current_action['throttle']
        self.velocity[1] += math.sin(math.radians(self.angle))*self.throttle_acceleration*time_between_frames*self.current_action['throttle']

        # max speed check and adjustment

        instantaneous_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if instantaneous_speed > self.max_speed:
            speed_reduction = self.max_speed/instantaneous_speed
            self.velocity[0] *= speed_reduction
            self.velocity[1] *= speed_reduction

        self.position[0] += self.velocity[0]*time_between_frames
        self.position[1] += self.velocity[1]*time_between_frames

        self.angle += self.turn_speed*time_between_frames*self.current_action['turn']

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

class Exhaust(GameObject):
    def __init__(self, position, angle):
        super().__init__('exhaust.png', position)
        self.alliance = -1
