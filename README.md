# GoDuel

GoDuel is a top-down shooter minigame modelled off of certain gameplay segments found in
[Subspace Continuum](https://store.steampowered.com/app/352700/Subspace_Continuum/).
It is intended to serve as a controlled development environment for a
1 vs. 1 competitive AI.

![follow](https://github.com/nvchung599/GoDuel/blob/master/follow.gif)

Currently, this bot's tracking and targeting algorithms are based on a
manually tuned PID controller.

Future implementation of a neural network should allow this bot to dodge
bullets and play more strategically.


## Getting Started

Install pygame

Run main.py

There are three gameplay modes to choose from.

The game never terminates -- close the window when done.

Controls:

* Arrow keys for movement
* Left ctrl for gun
* Left shift for afterburn


## Random Notes

* The players here move through a non-viscous medium (space). This lack of
natural motion damping was a notable challenge in the controller
design. Early versions of the follower bot would get caught in orbit
around the player and fail to converge on the target position. This was
solved by fixing the frame of reference on the bot and accounting for
relative velocities/projected positions.
* The output of the distance-keeping PID controller is a normalized
term with the range [-1, 1]. This is used as the duty cycle for
generating a PWM signal for the thrusters. Pulse width is set at 10 frames.
This games operates at 60 FPS.
* Increasing the integral gain __ki__ in mygame.keymap_auto_2d_combat
is an easy way to make the bot more "aggressive"
* The code is a pile of underdocumented patchwork, and will be restructured in preparation
for a neural network/reinforcement learning implementation.


## Acknowledgments

* All the folks from [SSCE Hyperspace](http://sshyperspace.com/) and
[SSCU Death Star Battle](http://www.deathstarbattle.com/) for over a
decade of fun.
* [The bot developers of Hyperspace](http://sshyperspace.com/dev/index.php#bot)
from whose work I draw inspiration and amusement.

