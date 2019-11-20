from __future__ import print_function
import odrive
from odrive.enums import *


def set_motor_characteristics(mot):
    """These are physical characteristics of the motor, i.e. number of magnets
    and pole pairs, encoder counts per revolution, etc.
    """

    mot.motor.config.pole_pairs = 7
    mot.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
    mot.encoder.config.cpr = 8192
    mot.motor.config.current_lim = 40
    mot.controller.config.vel_limit = 10000.0

def calibrate(tt):
    tt.config.startup_motor_calibration = True
    tt.config.startup_encoder_offset_calibration = True
    tt.config.startup_closed_loop_control = True

    # full calibration
    print("start full calibration")
    tt.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    while(tt.encoder.is_ready != True):
        print('.', end = '')
    print("finished full calibration sequence")

def anti_cog(mot):
    '''For anti-cogging (this worked with platter attached)'''

    mot.controller.config.pos_gain = 100
    mot.controller.config.vel_gain =.003
    mot.controller.config.vel_integrator_gain = 0.015
    mot.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
    mot.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    mot.controller.start_anticogging_calibration()


def init():
    """Initialize odrive, return first one"""

    print("finding an odrive...")
    my_drive = odrive.find_any()
    print("found odrive")

    return(my_drive)

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


