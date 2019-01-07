# BSD 3-Clause License
# 
# Copyright (c) 2018, DEMCON advanced mechatronics
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
from ctypes import *

# Extend ctypes Structure with some convenience methods
class Structure(Structure):
    def __iter__(self):
        for field, dtype in self._fields_:
            yield field, getattr(self, field)
    
    def __repr__(self):
        return repr(dict(self))

class scopedata(Structure):
    _fields_ = [
        ('number', c_int),
        ('type', c_int),
        ('state', c_int),
        ('signals', c_int*20),
        ('numsamples', c_int),
        ('decimation', c_int),
        ('triggermode', c_int),
        ('numprepostsamples', c_int),
        ('triggersignal', c_int),
        ('triggerscope', c_int),
        ('triggerscopesample', c_int),
        ('triggerlevel', c_double),
        ('triggerslope', c_int)
        ]

class dirStruct(Structure):
    _fields_ = [
        ('name', c_char * 8),
        ('ext', c_char * 3),
        ('day', c_int),
        ('month', c_int),
        ('year', c_int),
        ('hour', c_int),
        ('min', c_int),
        ('isDir', c_int),
        ('size', c_ulong),
    
        ]

class diskinfo(Structure):
    _fields_ = [
        ('DriveLetter',c_char),
        ('Label',c_char*3),
        ('Reserved',c_char*0),
        ('SerialNumber',c_int),
        ('FirstPhysicalSector',c_char),
        ('FATType',c_double), 
        ('FATCount',c_char),
        ('MaxDirEntries',c_char),
        ('BytesPerSector',c_char),
        ('SectorsPerCluster',c_char),
        ('TotalClusters',c_char),
        ('BadClusters',c_char),
        ('FreeClusters',c_char),
        ('Files',c_char),
        ('FileChains',c_char),
        ('FreeChains',c_char),
        ('LargestFreeChain',c_int),
#        ('DriveType',char*11),
        ]
        

# To be implemented
lgmode = c_int
fileinfo = c_int

__all__ = ['scopedata', 'lgmode', 'diskinfo', 'dirStruct', 'fileinfo']