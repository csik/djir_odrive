import odrive
from odrive.enums import *
import time
import math
from utils import *
# Find a connected ODrive (this will block until you connect one)
print("finding an odrive...")
my_drive = odrive.find_any()

tt0 = my_drive.axis0
home = tt0.encoder.pos_estimate

set_motor_characteristics(tt0)
# perhaps have a board-level init?
my_drive.config.brake_resistance = 2

tt0.config.startup_motor_calibration = True
tt0.config.startup_encoder_offset_calibration = True
tt0.config.startup_closed_loop_control = True

# basic startup (beep)
#print("attempting to enter startup sequence")
#tt0.requested_state = AXIS_STATE_STARTUP_SEQUENCE
#time.sleep(20)
#while tt0.current_state == AXIS_STATE_STARTUP_SEQUENCE:
#    time.sleep(0.1)
#print("finished axis startup")

# full calibration
print("start full calibration")
tt0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
time.sleep(20)
while(tt0.encoder.is_ready != True):
    print('.', end = '')
print("finished full calibration sequence")

print("starting anti-cogging, may take some time")
anti_cog(tt0)
print("finished anti-cogging")

tt0.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL


def backnforth(loops):
    for i in range(0,loops):
        my_drive.axis0.controller.pos_setpoint = 8192
        time.sleep(.5)
        my_drive.axis0.controller.pos_setpoint = -8192
        time.sleep(.5)


def gohome():
    tt0.controller.pos_setpoint = home

def govel(speed, dir):
    tt0.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
    my_drive.axis0.controller.vel_setpoint = speed




