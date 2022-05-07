# i2c interface functions
#
# This file is part of sis3316 python package.
#
# Copyright 2014 Sergey Ryzhikov <sergey-inform@ya.ru>
# IHEP @ Protvino, Russia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from .common import *

SI5325_WRITE    = 1<<14
SI5325_READ     = 1<<15
SI5325_BUSY     = 1<<31
SI5325_CAL_BUSY = 1<<6
SI5325_MAX_POLL = 10 # [ms] max time waiting for busy signal to clear

class Sis3316(object):
    
    class clkMultiplier_comm(object):
        '''Communication with the SI5325 Clock Multiplier
        Refer to the SI5325 manual for register details'''
        
        def __init__(self, container, register):
            self.container = container
            self.reg = register
        
        
        def write(self, addr, data):
            self.container.write(self.reg, addr & 0xff) # write register addr
            self.wait_busy()
            self.container.write(self.reg, SI5325_WRITE + (data & 0xff)) # write data
            self.wait_busy()
                
        def read(self, addr):
            self.container.write(self.reg, addr & 0xff)
            self.wait_busy()
            self.container.write(self.reg, SI5325_READ)
            return self.wait_busy()

        def wait_busy(self):
            """ Return the register value. """
            count = 0
            while True:
                data = self.container.read(self.reg)
                if not data & SI5325_BUSY:
                    return data
                    
                count += 1
                if count >= SI5325_MAX_POLL:
                    raise self._clkMultiplierHangExcept("Clk Multiplier busy flag is set more than %d ms." % count)
                msleep(1)
        
        def internalCalibration(self):
            self.write(136, 0x40) # ICAL to start internal callibration seq

            # poll until calibration is ready
            count = 0
            while True:
                self.container.write(self.reg, SI5325_READ) # read data
                data = self.wait_busy()
                if not data & SI5325_CAL_BUSY:
                    return data
                
                count += 1
                if count >= 1200: # According to SI5325 manual, typical = 35 ms. max = 1200 ms
                    raise self._clkMultiplierHangExcept("Clk Multiplier internal callibration busy flag is set more than %d ms." % count)
                msleep(1)


        def stop(self, clk):
            '''Turns off clock'''
            if clk not in [1,2]:
                raise ValueError("clkMultiplier_comm.bypass() powers down either clk1 or clk2")
            self.write(11, clk)

        def setup(self, ckin1, bw_sel, n1_hs, n1_clkx, n2, n3):
            """Configures clock multiplier. See DSPLLsimm from SI labs for valid settings"""
            if not (10 <= ckin1 <= 250):
                raise ValueError('CKIN1 must be in the range [10 MHz, 250 MHz]')
            if bw_sel > 15:
                raise ValueError('See DSPLLsimm for valid BW_SEL settings')
            if not (4 <= n1_hs <= 11):
                raise ValueError('N1_HS must be in the range [4,11]')
            if not (0 < n1_clkx <= 0x100000) or ( (n1_clkx & 0x1)==1 and n1_clkx != 1):
                raise ValueError('N1_CLKX must be an even int or 1 in the range [1, 2^20]')
            if not (32 <= n2 <= 512) or (n2 & 0x1)==1:
                raise ValueError('N2 must be an even int in the range [32,512]')
            if not (0 < n3 <= 0x80000):
                raise ValueError('N3 must be in the range [0, 2^19]')
            
            self.write( 0, 0x0) # No Bypass
            self.write(11, 0x02) # Power down clk2
            
            n3_val = n3 - 1 # See pg 38 of the SI5325 register manual
            self.write(43, ((n3_val >> 16) & 0x7) ) # n3 bits 18:16
            self.write(44, ((n3_val >> 8) & 0xff) ) # n3 bits 15:8
            self.write(45, (n3_val & 0xff) )        # n3 bits 7:0

            self.write(40, 0x00)                    # n2_ls bits 19:16
            self.write(41, ((n2 >> 8) & 0xff))      # n2_ls bits 15:8
            self.write(42, (n2 & 0xff))             # n2_ls bits 7:0

            n1_hs_val = n1_hs - 4 # pg 33
            self.write(25, n1_hs_val << 5)

            n1_val = n1_clkx - 1 # pg 33
            self.write(31, ((n1_val >> 16) & 0xf) ) # nc1_ls bits 19:16
            self.write(32, ((n1_val >> 8) & 0xff) ) # nc1_ls bits 15:8
            self.write(33, (n1_val & 0xff) )        # nc1_ls bits 7:0
            self.write(34, ((n1_val >> 16) & 0xf) ) # nc2_ls bits 19:16
            self.write(35, ((n1_val >> 8) & 0xff) ) # nc2_ls bits 15:8
            self.write(36, (n1_val & 0xff) )        # nc2_ls bits 7:0

            self.write( 2, bw_sel << 5 ) # BWSEL_REG
            self.internalCalibration()

    class _clkMultiplierHangExcept(Sis3316Except):
        """ Clock multiplier Errors """
