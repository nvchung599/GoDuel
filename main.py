from mygame import *

print("___DEMO SELECTION___\n"
      "\n"
      "  1  -  X FOLLOW\n"
      "  2  -  XY FOLLOW\n"
      "  3  -  COMBAT\n"
      "\n"
      "INPUT: ")

my_input = input()
this_game = MyGame(int(my_input))
this_game.run()
