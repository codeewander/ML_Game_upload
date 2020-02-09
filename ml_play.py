"""The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import pickle
import numpy as np
import os.path as path


def compute_x_end(ball, ball_last):
    direction_x = ball[0] - ball_last[0]
    direction_y = ball[1] - ball_last[1]
    ball_x_end = 0
    # y = mx + c
    if direction_y>0:
        m = direction_y / direction_x
        c = ball[1] - m*ball[0]
        ball_x_end = (400 - c )/m
    else:
        ball_x_end = 100
    while ball_x_end < 0 or ball_x_end > 200:
        if ball_x_end<0:
            ball_x_end = -ball_x_end
        elif ball_x_end>200:
            ball_x_end = 400-ball_x_end
    # print(ball_x_end)
    return ball_x_end


def ml_loop():
    """The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_last = [101,101]
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
                scene_info.status == GameStatus.GAME_PASS:
            comm.ml_ready()

            scene_info = comm.get_scene_info()
            # Do some stuff if needed

        # 3.3. Put the code here to handle the scene information

        ball_x_end = compute_x_end(scene_info.ball, ball_last)
        ball_last = scene_info.ball
        move  = (ball_x_end) - (scene_info.platform[0]+20)
        # motion direction of ball
        # compute the location of falling
        print(ball_x_end)
        # 3.4. Send the instruction for this frame to the game process
        if move > 0:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
        elif move < 0:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
        else:
            comm.send_instruction(scene_info.frame, PlatformAction.NONE)
