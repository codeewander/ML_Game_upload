"""The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import pickle
import numpy as np
import os.path as path



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
    # 2. Inform the game process that ml process is ready before start the loop.
    filename = 'model.sav'
    model = pickle.load(open(filename,'rb'))
    comm.ml_ready()
    last_x=0
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        direction = 1 if scene_info.ball[0] > last_x else -1

        inp_temp = np.array([scene_info.ball[0], scene_info.ball[1], scene_info.platform[0],direction])
        input=inp_temp[np.newaxis, :]

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
                scene_info.status == GameStatus.GAME_PASS:
            comm.ml_ready()

            scene_info = comm.get_scene_info()
            # Do some stuff if needed

        # 3.3. Put the code here to handle the scene information
        move  = model.predict(input)
        # motion direction of ball
        # compute the location of falling
        print(move)
        # 3.4. Send the instruction for this frame to the game process
        if move > 0:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
        elif move < 0:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
        else:
            comm.send_instruction(scene_info.frame, PlatformAction.NONE)
