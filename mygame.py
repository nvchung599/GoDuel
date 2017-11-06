from objects import *


class MyGame(object):

    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.FPS = 60 # TODO figure out time scale
        self.clock = pygame.time.Clock()
        self.bg_color = (0, 0, 0)

        # TODO automate player placement in duel box
        self.players = []
        self.players.append(Player(1, [0, 0]))
        self.players.append(Player(2, [self.width/2, -self.height/2]))

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

                # TODO center screen on player 1
                # TODO create grid underlay
                # TODO downsize warbird png, sync hitbox with image, alpha image

                draw_centered(player.transform_image(), self.screen, player.transform_position())

            pygame.display.update()
            self.clock.tick(self.FPS)
            # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

    def keymap(self, keys, alliance): #add input for player 1 or 2

        if alliance == 1:
            left_bool = keys[pygame.K_LEFT]
            right_bool = keys[pygame.K_RIGHT]
            up_bool = keys[pygame.K_UP]
            down_bool = keys[pygame.K_DOWN]
            # AFTERBURN
            # TRIGGER
        elif alliance == 2:
            left_bool = keys[pygame.K_j]
            right_bool = keys[pygame.K_l]
            up_bool = keys[pygame.K_i]
            down_bool = keys[pygame.K_k]
            # AFTERBURN
            # TRIGGER
        else:
            left_bool = False
            right_bool = False
            up_bool = False
            down_bool = False
            # AFTERBURN
            # TRIGGER

        turn = 0
        throttle = 0

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

        actions = {'turn': turn, 'throttle': throttle}

        return actions




