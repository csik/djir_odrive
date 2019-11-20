import odrive
from odrive.enums import *
import time
import math
import sys
from speeds import *
from utils import *

ENCODER_CPR = 8192
S_33 = 100.0/3 / 60 * ENCODER_CPR
S_45 = 45 / 60 * ENCODER_CPR

# Import PYO and start server
from pyo import *
pyo = Server().boot()
pyo.start()
oscreceiver = OscReceive(port=1234, address=['/pitch',
                                             '/amp',
                                             '/clock',
                                             '/in0',
                                             '/in1',
                                             '/in2',
                                             '/in3'
                                             '/other'])

# Find a connected ODrive (this will block until you connect one)
print("finding an odrive...")
my_drive = odrive.find_any()
tt0 = my_drive.axis0
home = tt0.encoder.pos_estimate

set_motor_characteristics(tt0)
# perhaps have a board-level init?
my_drive.config.brake_resistance = 2

tt0.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL

class Turntable:
    def __init__(self, OdriveMotor):
        self.tt = OdriveMotor
        self.home = self.tt.encoder.pos_estimate
        self.trajvel_limit = 8000
        self.trajaccel_limit = 40000
        self.trajdecel_limit = 40000
        self.trajA_per_css = 0

    def calibrate(self):
        self.tt.config.startup_motor_calibration = True
        self.tt.config.startup_encoder_offset_calibration = True
        self.tt.config.startup_closed_loop_control = True

        # full calibration
        print("start full calibration")
        spinner = spinning_cursor()
        self.tt.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        time.sleep(1)
        while(self.tt.motor.armed_state != 0):
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
        print("finished full calibration sequence")

    def anticogitate(self):
        self.tt.config.startup_closed_loop_control = True
        startpoint = self.tt.encoder.pos_estimate
        print("starting anti-cogging, may take some time")
        anti_cog(self.tt)
        time.sleep(1)
        spinner = spinning_cursor()
        while(abs(self.tt.encoder.pos_estimate - startpoint) > 100):
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
        print("finished anti-cogging")


    def settrajparams(self, mode):
        print(type(trajparams))
        i = trajparams.get(mode)
        print(i)
        print(type(i))
        self.tt.trap_traj.config.vel_limit = i.get('trajvel_limit')
        self.tt.trap_traj.config.accel_limit = i.get('trajaccel_limit')
        self.tt.trap_traj.config.decel_limit = i.get('trajdecel_limit')
        self.tt.trap_traj.config.A_per_css = i.get('trajA_per_css')

    def restart(self):
        self.tt.error=0
        self.tt.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    def relax(self):
        self.tt.requested_state = AXIS_STATE_IDLE

    def on(self):
        self.tt.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL


    def sethome(self):
        self.home = self.tt.encoder.pos_estimate
        self.tt.encoder.pos_estimate = self.home

    def gohome(self):
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.tt.controller.move_to_pos(self.home)

    def govel(self, speed):
        self.tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        self.tt.controller.vel_setpoint = speed

    def reset_pos(self):
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.tt.controller.move_to_pos(self.tt.encoder.pos_estimate)

    def move_to_pos(self, position):
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.tt.controller.move_to_pos(position)

    def move_incremental(self, distance, absolute=True):
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.tt.controller.move_incremental(distance, absolute)

    def forth(self, velocity):
        tt = self.tt
        tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        tt.controller.vel_setpoint = velocity

    def back(self, velocity):
        self.tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        self.tt.controller.vel_setpoint = -1*velocity

    def backnforth(self, loops, distance):
        self.on()
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        for i in range(0,loops):
            self.tt.controller.move_to_pos(distance)
            while (self.tt.controller.vel_setpoint != 0):
                pass
            self.tt.controller.move_to_pos(-1*distance)
            while (self.tt.controller.vel_setpoint != 0):
                pass

    def bnf(self, loops, distance):
        self.on()
        self.tt.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.reset_pos()
        for i in range(0,loops):
            self.tt.controller.move_incremental(distance, 0)
            while (self.tt.controller.vel_setpoint != 0):
                pass
            self.tt.controller.move_incremental(-1*distance, 0)
            while (self.tt.controller.vel_setpoint != 0):
                pass

    def receive_vel(self, offset=20):
        self.on()
        pitchvel =  oscreceiver['/in0']*S_33*2
        offet = oscreceiver['/in1']*10
        self.tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        while(1):
            self.govel(pitchvel.stream.getValue()*offset)

    def receive_sine(self):
        self.on()
        pitchrel = (oscreceiver['/in0']-oscreceiver['/in1'])*S_33*2
        self.tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        while(1):
            self.govel(pitchrel.stream.getValue())

    def somebeats(self):
        self.on()
        t = CosTable([(0,0), (100,1), (500,.3), (8191,0)])
        clock = Metro(time=.125, poly=4).play()
        beat = Beat(time=.125, taps=16, w1=[90,60], w2=[50, 80], w3=35, poly=1).play()
        trmid = TrigXnoiseMidi(beat, dist=12, mrange=(60, 96))
        trhz = TrigChoice(clock, choice=[-8192,
                                         8192,
                                         -4092,
                                         4092,
                                         16384,
                                         -4092*4/3,
                                         4092*4/3,
                                         -4092*3/2,
                                         4092*3/2]
                          )
        self.tt.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        while(1):
            self.govel(trhz.get())

    def delayed(self):
        time.sleep(15)
        self.on()
        self.bnf(8,150)


