
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


def anti_cog(mot):
    '''For anti-cogging (this worked with platter attached)'''

    mot.controller.config.pos_gain = 100
    mot.controller.config.vel_gain =.003
    mot.controller.config.vel_integrator_gain = 0.015
    mot.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
    mot.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    mot.controller.start_anticogging_calibration()

    print("calibration finished")


