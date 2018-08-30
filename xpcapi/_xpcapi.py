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

from enum import IntEnum
from ctypes import *
from .xpcapitypes import *

int = c_int
void = None
double = c_double
char = c_char

unsigned_char = c_ubyte
unsigned_int = c_uint




if str == bytes:
    # Python 2: no unicode conversions
    c_str = c_char_p

    def decode(s):
        return s
else:
    # Python 3: convert from/to unicode transparently via ascii encoding
    class c_str(c_char_p):
        '''
        Helper class to convert strings to bytes under python 3 for C function calls
        '''
        @staticmethod
        def from_param(s):
            if isinstance(s,str):
                s = s.encode('latin-1')
            return c_char_p.from_param(s)

                
    def decode(s):
        return s.decode('latin-1')

MAX_ERR_MSG_LENGTH=50
MAX_SCOPES=30
MAX_SIGNALS=10

class COMMTYP(IntEnum):
    RS232=1
    TCPIP=2

class SCTYPE(IntEnum):
    NONE=0
    HOST=1
    TARGET=2
    FILE=3
    HIDDEN=4

class TRIGMD(IntEnum):
    FREERUN=0
    SOFTWARE=1
    SIGNAL=2
    SCOPE=3
    SCEND=4

class TRIGSLOPE(IntEnum):
    EITHER=0
    RISING=1
    FALLING=2

class SCMODE(IntEnum):
    NUMERICAL=0
    REDRAW=1
    SLIDING=2
    ROLLING=3

class SCST(IntEnum):
    WAITTOSTART=0
    WAITFORTRIG=1
    ACQUIRING=2
    FINISHED=3
    INTERRUPTED=4
    PREACQUIRING=5

class LGMOD(IntEnum):
    TIME=0
    VALUE=1


class XpcError(IOError):
    pass

class _xpcapi:
    def __init__(self, lib):
        self._lib = lib
        self._port = -1
        self._define_function("xPCReOpenPort", [int], int)
        self._define_function("xPCOpenSerialPort", [int,int], int)
        self._define_function("xPCClosePort", [int], void)
        self._define_function("xPCGetLastError", [], int)
        self._define_function("xPCSetLastError", [int], void)
        self._define_function("xPCGetExecTime", [int], double)
        self._define_function("xPCSetStopTime", [int,double], void)
        self._define_function("xPCGetStopTime", [int], double)
        self._define_function("xPCSetSampleTime", [int,double], void)
        self._define_function("xPCGetSampleTime", [int], double)
        self._define_function("xPCSetEcho", [int,int], void)
        self._define_function("xPCGetEcho", [int], int)
        self._define_function("xPCSetHiddenScopeEcho", [int,int], void)
        self._define_function("xPCGetHiddenScopeEcho", [int], int)
        self._define_function("xPCAverageTET", [int], double)
        self._define_function("xPCGetNumParams", [int], int)
        self._define_function("xPCGetNumSignals", [int], int)
        self._define_function("xPCGetAppName", [int,c_str], POINTER(char))
        self._define_function("xPCUnloadApp", [int], void)
        self._define_function("xPCStartApp", [int], void)
        self._define_function("xPCStopApp", [int], void)
        self._define_function("xPCIsAppRunning", [int], int)
        self._define_function("xPCIsOverloaded", [int], int)
        self._define_function("xPCGetNumOutputs", [int], int)
        self._define_function("xPCGetNumStates", [int], int)
        self._define_function("xPCGetParam", [int,int,POINTER(double)], void)
        self._define_function("xPCSetLogMode", [int,lgmode], void)
        self._define_function("xPCSetParam", [int,int,POINTER(double)], void)
        self._define_function("xPCGetLogMode", [int], lgmode)
        self._define_function("xPCNumLogSamples", [int], int)
        self._define_function("xPCMaxLogSamples", [int], int)
        self._define_function("xPCNumLogWraps", [int], int)
        self._define_function("xPCReboot", [int], void)
        self._define_function("xPCGetOutputLog", [int,int,int,int,int,POINTER(double)], void)
        self._define_function("xPCGetStateLog", [int,int,int,int,int,POINTER(double)], void)
        self._define_function("xPCGetTimeLog", [int,int,int,int,POINTER(double)], void)
        self._define_function("xPCGetTETLog", [int,int,int,int,POINTER(double)], void)
        self._define_function("xPCScGetData", [int,int,int,int,int,int,POINTER(double)], void)
        self._define_function("xPCMinimumTET", [int,POINTER(double)], void)
        self._define_function("xPCMaximumTET", [int,POINTER(double)], void)
        self._define_function("xPCGetSignals", [int,int,POINTER(int),POINTER(double)], int)
        self._define_function("xPCGetSignal", [int,int], double)
        self._define_function("xPCAddScope", [int,int,int], void)
        self._define_function("xPCRemScope", [int,int], void)
        self._define_function("xPCScAddSignal", [int,int,int], void)
        self._define_function("xPCScRemSignal", [int,int,int], void)
        self._define_function("xPCScSetAutoRestart", [int,int,int], void)
        self._define_function("xPCScGetAutoRestart", [int,int], int)
        self._define_function("xPCGetScopes", [int,POINTER(int)], void)
        self._define_function("xPCGetHiddenScopes", [int,POINTER(int)], void)
        self._define_function("xPCScGetSignals", [int,int,POINTER(int)], void)
        self._define_function("xPCScSetDecimation", [int,int,int], void)
        self._define_function("xPCScGetNumSignals", [int,int], int)
        self._define_function("xPCScGetDecimation", [int,int], int)
        self._define_function("xPCScSetNumSamples", [int,int,int], void)
        self._define_function("xPCScGetNumSamples", [int,int], int)
        self._define_function("xPCScGetStartTime", [int,int], double)
        self._define_function("xPCScGetState", [int,int], int)
        self._define_function("xPCScSetTriggerLevel", [int,int,double], void)
        self._define_function("xPCScGetTriggerLevel", [int,int], double)
        self._define_function("xPCScSetTriggerMode", [int,int,int], void)
        self._define_function("xPCScGetTriggerMode", [int,int], int)
        self._define_function("xPCScSetTriggerScope", [int,int,int], void)
        self._define_function("xPCScGetTriggerScope", [int,int], int)
        self._define_function("xPCScSetTriggerScopeSample", [int,int,int], void)
        self._define_function("xPCScGetTriggerScopeSample", [int,int], int)
        self._define_function("xPCScSetTriggerSignal", [int,int,int], void)
        self._define_function("xPCScGetTriggerSignal", [int,int], int)
        self._define_function("xPCScSetTriggerSlope", [int,int,int], void)
        self._define_function("xPCScGetTriggerSlope", [int,int], int)
        self._define_function("xPCScSoftwareTrigger", [int,int], void)
        self._define_function("xPCScStart", [int,int], void)
        self._define_function("xPCScStop", [int,int], void)
        self._define_function("xPCIsScFinished", [int,int], int)
        self._define_function("xPCScGetNumPrePostSamples", [int,int], int)
        self._define_function("xPCScSetNumPrePostSamples", [int,int,int], void)
        self._define_function("xPCGetScope", [int,int], scopedata)
        self._define_function("xPCSetScope", [int,scopedata], void)
        self._define_function("xPCLoadApp", [int,c_str,c_str], void)
        self._define_function("xPCGetParamDims", [int,int,POINTER(int)], void)
        self._define_function("xPCGetParamDimsSize", [int,int], int)
        self._define_function("xPCGetSignalWidth", [int,int], int)
        self._define_function("xPCGetSignalIdx", [int,c_str], int)
        self._define_function("xPCGetSigLabelWidth", [int,c_str], int)
        self._define_function("xPCGetSigIdxfromLabel", [int,c_str,POINTER(int)], int)
        self._define_function("xPCGetSignalLabel", [int,int,c_str], POINTER(char))
        self._define_function("xPCGetParamIdx", [int,c_str,c_str], int)
        self._define_function("xPCGetParamName", [int,int,c_str,c_str], void)
        self._define_function("xPCGetParamType", [int,int,c_str], void)
        self._define_function("xPCGetSignalName", [int,int,c_str], POINTER(char))
        self._define_function("xPCTgScGetGrid", [int,int], int)
        self._define_function("xPCTgScGetMode", [int,int], int)
        self._define_function("xPCTgScGetViewMode", [int], int)
        self._define_function("xPCTgScGetYLimits", [int,int,POINTER(double)], void)
        self._define_function("xPCTgScSetGrid", [int,int,int], void)
        self._define_function("xPCTgScSetMode", [int,int,int], void)
        self._define_function("xPCTgScSetViewMode", [int,int], void)
        self._define_function("xPCTgScSetYLimits", [int,int,POINTER(double)], void)
        self._define_function("xPCTgScSetSignalFormat", [int,int,int,c_str], void)
        self._define_function("xPCTgScGetSignalFormat", [int,int,int,c_str], POINTER(char))
        self._define_function("xPCSetLoadTimeOut", [int,int], void)
        self._define_function("xPCErrorMsg", [int,c_str], POINTER(char))
        self._define_function("xPCScGetType", [int,int], int)
        self._define_function("xPCGetLoadTimeOut", [int], int)
        self._define_function("xPCOpenTcpIpPort", [c_str,c_str], int)
        self._define_function("xPCOpenConnection", [int], void)
        self._define_function("xPCCloseConnection", [int], void)
        self._define_function("xPCRegisterTarget", [int,c_str,c_str,int,int], int)
        self._define_function("xPCDeRegisterTarget", [int], void)
        self._define_function("xPCGetAPIVersion", [], POINTER(char))
        self._define_function("xPCGetTargetVersion", [int,c_str], void)
        self._define_function("xPCTargetPing", [int], int)
        self._define_function("xPCFSReadFile", [int,int,int,int,POINTER(unsigned_char)], void)
        self._define_function("xPCFSRead", [int,int,int,int,POINTER(unsigned_char)], int)
        self._define_function("xPCFSWriteFile", [int,int,int,POINTER(unsigned_char)], void)
        self._define_function("xPCFSBufferInfo", [int,c_str], void)
        self._define_function("xPCFSGetFileSize", [int,int], int)
        self._define_function("xPCFSOpenFile", [int,c_str,c_str], int)
        self._define_function("xPCFSCloseFile", [int,int], void)
        self._define_function("xPCFSGetPWD", [int,c_str], void)
        self._define_function("xPCFTPGet", [int,int,int,c_str], void)
        self._define_function("xPCFTPPut", [int,int,c_str], void)
        self._define_function("xPCFSRemoveFile", [int,c_str], void)
        self._define_function("xPCFSCD", [int,c_str], void)
        self._define_function("xPCFSMKDIR", [int,c_str], void)
        self._define_function("xPCFSRMDIR", [int,c_str], void)
        self._define_function("xPCFSDir", [int,c_str,c_str,int], void)
        self._define_function("xPCFSDirSize", [int,c_str], int)
        self._define_function("xPCFSGetError", [int,unsigned_int,POINTER(unsigned_char)], void)
        self._define_function("xPCSaveParamSet", [int,c_str], void)
        self._define_function("xPCLoadParamSet", [int,c_str], void)
        self._define_function("xPCFSScSetFilename", [int,int,c_str], void)
        self._define_function("xPCFSScGetFilename", [int,int,c_str], POINTER(char))
        self._define_function("xPCFSScSetWriteMode", [int,int,int], void)
        self._define_function("xPCFSScGetWriteMode", [int,int], int)
        self._define_function("xPCFSScSetWriteSize", [int,int,unsigned_int], void)
        self._define_function("xPCFSScGetWriteSize", [int,int], unsigned_int)
        self._define_function("xPCReadXML", [int,int,POINTER(unsigned_char)], void)
        self._define_function("xPCFSDiskInfo", [int,c_str], diskinfo)
        self._define_function("xPCFSFileTable", [int,c_str], POINTER(char))
        self._define_function("xPCFSDirItems", [int,c_str,POINTER(dirStruct),int], void)
        self._define_function("xPCFSDirStructSize", [int,c_str], int)
        self._define_function("xPCGetNumScopes", [int], int)
        self._define_function("xPCGetNumHiddenScopes", [int], int)
        self._define_function("xPCGetScopeList", [int,POINTER(int)], void)
        self._define_function("xPCGetHiddenList", [int,POINTER(int)], void)
        self._define_function("xPCScGetSignalList", [int,int,POINTER(int)], void)
        self._define_function("xPCGetSimMode", [int], int)
        self._define_function("xPCGetPCIInfo", [int,c_str], void)
        self._define_function("xPCGetSessionTime", [int], double)
        self._define_function("xPCGetLogStatus", [int,POINTER(int)], void)
        self._define_function("xPCFSFileInfo", [int,int], fileinfo)
        self._define_function("xPCSetDefaultStopTime", [int], void)
        self._define_function("xPCGetXMLSize", [int], int)
        self._define_function("xPCIsTargetScope", [int], int)
        self._define_function("xPCSetTargetScopeUpdate", [int,int], void)
        self._define_function("xPCFSReNameFile", [int,c_str,c_str], void)
        self._define_function("xPCFSScSetDynamicMode", [int,int,int], void)
        self._define_function("xPCFSScGetDynamicMode", [int,int], int)
        self._define_function("xPCFSScSetMaxWriteFileSize", [int,int,unsigned_int], void)
        self._define_function("xPCFSScGetMaxWriteFileSize", [int,int], unsigned_int)
        self._define_function("xPCInitAPI", [], int)
        self._define_function("xPCFreeAPI", [], void)
        self._define_function("xPCResolveAPI", [POINTER(void)], int)

    def reOpenPort(self, ):
        retval = self._lib.xPCReOpenPort(self._port)
        self._checkerror()
        return retval
    def openSerialPort(self, comport,baudRate):
        retval = self._lib.xPCOpenSerialPort(comport,baudRate)
        self._checkerror()
        return retval
    def closePort(self, ):
        retval = self._lib.xPCClosePort(self._port)
        self._checkerror()
        return retval
    def getLastError(self, ):
        retval = self._lib.xPCGetLastError()
        self._checkerror()
        return retval
    def setLastError(self, error):
        retval = self._lib.xPCSetLastError(error)
        self._checkerror()
        return retval
    def getExecTime(self, ):
        retval = self._lib.xPCGetExecTime(self._port)
        self._checkerror()
        return retval
    def setStopTime(self, tfinal):
        retval = self._lib.xPCSetStopTime(self._port,tfinal)
        self._checkerror()
        return retval
    def getStopTime(self, ):
        retval = self._lib.xPCGetStopTime(self._port)
        self._checkerror()
        return retval
    def setSampleTime(self, ts):
        retval = self._lib.xPCSetSampleTime(self._port,ts)
        self._checkerror()
        return retval
    def getSampleTime(self, ):
        retval = self._lib.xPCGetSampleTime(self._port)
        self._checkerror()
        return retval
    def setEcho(self, mode):
        retval = self._lib.xPCSetEcho(self._port,mode)
        self._checkerror()
        return retval
    def getEcho(self, ):
        retval = self._lib.xPCGetEcho(self._port)
        self._checkerror()
        return retval
    def setHiddenScopeEcho(self, mode):
        retval = self._lib.xPCSetHiddenScopeEcho(self._port,mode)
        self._checkerror()
        return retval
    def getHiddenScopeEcho(self, ):
        retval = self._lib.xPCGetHiddenScopeEcho(self._port)
        self._checkerror()
        return retval
    def averageTET(self, ):
        retval = self._lib.xPCAverageTET(self._port)
        self._checkerror()
        return retval
    def getNumParams(self, ):
        retval = self._lib.xPCGetNumParams(self._port)
        self._checkerror()
        return retval
    def getNumSignals(self, ):
        retval = self._lib.xPCGetNumSignals(self._port)
        self._checkerror()
        return retval
    def getAppName(self, modelname):
        retval = self._lib.xPCGetAppName(self._port,modelname)
        self._checkerror()
        return retval
    def unloadApp(self, ):
        retval = self._lib.xPCUnloadApp(self._port)
        self._checkerror()
        return retval
    def startApp(self, ):
        retval = self._lib.xPCStartApp(self._port)
        self._checkerror()
        return retval
    def stopApp(self, ):
        retval = self._lib.xPCStopApp(self._port)
        self._checkerror()
        return retval
    def isAppRunning(self, ):
        retval = self._lib.xPCIsAppRunning(self._port)
        self._checkerror()
        return retval
    def isOverloaded(self, ):
        retval = self._lib.xPCIsOverloaded(self._port)
        self._checkerror()
        return retval
    def getNumOutputs(self, ):
        retval = self._lib.xPCGetNumOutputs(self._port)
        self._checkerror()
        return retval
    def getNumStates(self, ):
        retval = self._lib.xPCGetNumStates(self._port)
        self._checkerror()
        return retval
    def getParam(self, parIdx,paramValue):
        retval = self._lib.xPCGetParam(self._port,parIdx,paramValue)
        self._checkerror()
        return retval
    def setLogMode(self, lgdata):
        retval = self._lib.xPCSetLogMode(self._port,lgdata)
        self._checkerror()
        return retval
    def setParam(self, parIdx,paramValue):
        retval = self._lib.xPCSetParam(self._port,parIdx,paramValue)
        self._checkerror()
        return retval
    def getLogMode(self, ):
        retval = self._lib.xPCGetLogMode(self._port)
        self._checkerror()
        return retval
    def numLogSamples(self, ):
        retval = self._lib.xPCNumLogSamples(self._port)
        self._checkerror()
        return retval
    def maxLogSamples(self, ):
        retval = self._lib.xPCMaxLogSamples(self._port)
        self._checkerror()
        return retval
    def numLogWraps(self, ):
        retval = self._lib.xPCNumLogWraps(self._port)
        self._checkerror()
        return retval
    def reboot(self, ):
        retval = self._lib.xPCReboot(self._port)
        self._checkerror()
        return retval
    def getOutputLog(self, start,numsamples,decimation,output_id,data):
        retval = self._lib.xPCGetOutputLog(self._port,start,numsamples,decimation,output_id,data)
        self._checkerror()
        return retval
    def getStateLog(self, start,numsamples,decimation,state_id,data):
        retval = self._lib.xPCGetStateLog(self._port,start,numsamples,decimation,state_id,data)
        self._checkerror()
        return retval
    def getTimeLog(self, start,numsamples,decimation,data):
        retval = self._lib.xPCGetTimeLog(self._port,start,numsamples,decimation,data)
        self._checkerror()
        return retval
    def getTETLog(self, start,numsamples,decimation,data):
        retval = self._lib.xPCGetTETLog(self._port,start,numsamples,decimation,data)
        self._checkerror()
        return retval
    def scGetData(self, scNum,signal_id,start,numsamples,decimation,data):
        retval = self._lib.xPCScGetData(self._port,scNum,signal_id,start,numsamples,decimation,data)
        self._checkerror()
        return retval
    def minimumTET(self, data):
        retval = self._lib.xPCMinimumTET(self._port,data)
        self._checkerror()
        return retval
    def maximumTET(self, data):
        retval = self._lib.xPCMaximumTET(self._port,data)
        self._checkerror()
        return retval
    def getSignals(self, numSignals,signals,values):
        retval = self._lib.xPCGetSignals(self._port,numSignals,signals,values)
        self._checkerror()
        return retval
    def getSignal(self, sigNum):
        retval = self._lib.xPCGetSignal(self._port,sigNum)
        self._checkerror()
        return retval
    def addScope(self, type,scNum):
        retval = self._lib.xPCAddScope(self._port,type,scNum)
        self._checkerror()
        return retval
    def remScope(self, scNum):
        retval = self._lib.xPCRemScope(self._port,scNum)
        self._checkerror()
        return retval
    def scAddSignal(self, scNum,sigNum):
        retval = self._lib.xPCScAddSignal(self._port,scNum,sigNum)
        self._checkerror()
        return retval
    def scRemSignal(self, scNum,sigNum):
        retval = self._lib.xPCScRemSignal(self._port,scNum,sigNum)
        self._checkerror()
        return retval
    def scSetAutoRestart(self, scNum,autorestart):
        retval = self._lib.xPCScSetAutoRestart(self._port,scNum,autorestart)
        self._checkerror()
        return retval
    def scGetAutoRestart(self, scNum):
        retval = self._lib.xPCScGetAutoRestart(self._port,scNum)
        self._checkerror()
        return retval
    def getScopes(self, data):
        retval = self._lib.xPCGetScopes(self._port,data)
        self._checkerror()
        return retval
    def getHiddenScopes(self, data):
        retval = self._lib.xPCGetHiddenScopes(self._port,data)
        self._checkerror()
        return retval
    def scGetSignals(self, scNum,data):
        retval = self._lib.xPCScGetSignals(self._port,scNum,data)
        self._checkerror()
        return retval
    def scSetDecimation(self, scNum,decimation):
        retval = self._lib.xPCScSetDecimation(self._port,scNum,decimation)
        self._checkerror()
        return retval
    def scGetNumSignals(self, scNum):
        retval = self._lib.xPCScGetNumSignals(self._port,scNum)
        self._checkerror()
        return retval
    def scGetDecimation(self, scNum):
        retval = self._lib.xPCScGetDecimation(self._port,scNum)
        self._checkerror()
        return retval
    def scSetNumSamples(self, scNum,samples):
        retval = self._lib.xPCScSetNumSamples(self._port,scNum,samples)
        self._checkerror()
        return retval
    def scGetNumSamples(self, scNum):
        retval = self._lib.xPCScGetNumSamples(self._port,scNum)
        self._checkerror()
        return retval
    def scGetStartTime(self, scNum):
        retval = self._lib.xPCScGetStartTime(self._port,scNum)
        self._checkerror()
        return retval
    def scGetState(self, scNum):
        retval = self._lib.xPCScGetState(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerLevel(self, scNum,level):
        retval = self._lib.xPCScSetTriggerLevel(self._port,scNum,level)
        self._checkerror()
        return retval
    def scGetTriggerLevel(self, scNum):
        retval = self._lib.xPCScGetTriggerLevel(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerMode(self, scNum,mode):
        retval = self._lib.xPCScSetTriggerMode(self._port,scNum,mode)
        self._checkerror()
        return retval
    def scGetTriggerMode(self, scNum):
        retval = self._lib.xPCScGetTriggerMode(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerScope(self, scNum,trigMode):
        retval = self._lib.xPCScSetTriggerScope(self._port,scNum,trigMode)
        self._checkerror()
        return retval
    def scGetTriggerScope(self, scNum):
        retval = self._lib.xPCScGetTriggerScope(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerScopeSample(self, scNum,trigScSamp):
        retval = self._lib.xPCScSetTriggerScopeSample(self._port,scNum,trigScSamp)
        self._checkerror()
        return retval
    def scGetTriggerScopeSample(self, scNum):
        retval = self._lib.xPCScGetTriggerScopeSample(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerSignal(self, scNum,trigSig):
        retval = self._lib.xPCScSetTriggerSignal(self._port,scNum,trigSig)
        self._checkerror()
        return retval
    def scGetTriggerSignal(self, scNum):
        retval = self._lib.xPCScGetTriggerSignal(self._port,scNum)
        self._checkerror()
        return retval
    def scSetTriggerSlope(self, scNum,trigSlope):
        retval = self._lib.xPCScSetTriggerSlope(self._port,scNum,trigSlope)
        self._checkerror()
        return retval
    def scGetTriggerSlope(self, scNum):
        retval = self._lib.xPCScGetTriggerSlope(self._port,scNum)
        self._checkerror()
        return retval
    def scSoftwareTrigger(self, scNum):
        retval = self._lib.xPCScSoftwareTrigger(self._port,scNum)
        self._checkerror()
        return retval
    def scStart(self, scNum):
        retval = self._lib.xPCScStart(self._port,scNum)
        self._checkerror()
        return retval
    def scStop(self, scNum):
        retval = self._lib.xPCScStop(self._port,scNum)
        self._checkerror()
        return retval
    def isScFinished(self, scNum):
        retval = self._lib.xPCIsScFinished(self._port,scNum)
        self._checkerror()
        return retval
    def scGetNumPrePostSamples(self, scNum):
        retval = self._lib.xPCScGetNumPrePostSamples(self._port,scNum)
        self._checkerror()
        return retval
    def scSetNumPrePostSamples(self, scNum,prepost):
        retval = self._lib.xPCScSetNumPrePostSamples(self._port,scNum,prepost)
        self._checkerror()
        return retval
    def getScope(self, scNum):
        retval = self._lib.xPCGetScope(self._port,scNum)
        self._checkerror()
        return retval
    def setScope(self, state):
        retval = self._lib.xPCSetScope(self._port,state)
        self._checkerror()
        return retval
    def loadApp(self, pathstr,filename):
        retval = self._lib.xPCLoadApp(self._port,pathstr,filename)
        self._checkerror()
        return retval
    def getParamDims(self, parIdx,dims):
        retval = self._lib.xPCGetParamDims(self._port,parIdx,dims)
        self._checkerror()
        return retval
    def getParamDimsSize(self, parIdx):
        retval = self._lib.xPCGetParamDimsSize(self._port,parIdx)
        self._checkerror()
        return retval
    def getSignalWidth(self, sigIdx):
        retval = self._lib.xPCGetSignalWidth(self._port,sigIdx)
        self._checkerror()
        return retval
    def getSignalIdx(self, sigName):
        retval = self._lib.xPCGetSignalIdx(self._port,sigName)
        self._checkerror()
        return retval
    def getSigLabelWidth(self, sigName):
        retval = self._lib.xPCGetSigLabelWidth(self._port,sigName)
        self._checkerror()
        return retval
    def getSigIdxfromLabel(self, sigName,sigIds):
        retval = self._lib.xPCGetSigIdxfromLabel(self._port,sigName,sigIds)
        self._checkerror()
        return retval
    def getSignalLabel(self, sigIdx,sigLabel):
        retval = self._lib.xPCGetSignalLabel(self._port,sigIdx,sigLabel)
        self._checkerror()
        return retval
    def getParamIdx(self, block,parameter):
        retval = self._lib.xPCGetParamIdx(self._port,block,parameter)
        self._checkerror()
        return retval
    def getParamName(self, parIdx,block,param):
        retval = self._lib.xPCGetParamName(self._port,parIdx,block,param)
        self._checkerror()
        return retval
    def getParamType(self, parIdx,paramType):
        retval = self._lib.xPCGetParamType(self._port,parIdx,paramType)
        self._checkerror()
        return retval
    def getSignalName(self, sigIdx,sigName):
        retval = self._lib.xPCGetSignalName(self._port,sigIdx,sigName)
        self._checkerror()
        return retval
    def tgScGetGrid(self, scNum):
        retval = self._lib.xPCTgScGetGrid(self._port,scNum)
        self._checkerror()
        return retval
    def tgScGetMode(self, scNum):
        retval = self._lib.xPCTgScGetMode(self._port,scNum)
        self._checkerror()
        return retval
    def tgScGetViewMode(self, ):
        retval = self._lib.xPCTgScGetViewMode(self._port)
        self._checkerror()
        return retval
    def tgScGetYLimits(self, scNum,limits):
        retval = self._lib.xPCTgScGetYLimits(self._port,scNum,limits)
        self._checkerror()
        return retval
    def tgScSetGrid(self, scNum,flag):
        retval = self._lib.xPCTgScSetGrid(self._port,scNum,flag)
        self._checkerror()
        return retval
    def tgScSetMode(self, scNum,flag):
        retval = self._lib.xPCTgScSetMode(self._port,scNum,flag)
        self._checkerror()
        return retval
    def tgScSetViewMode(self, scNum):
        retval = self._lib.xPCTgScSetViewMode(self._port,scNum)
        self._checkerror()
        return retval
    def tgScSetYLimits(self, scNum,limits):
        retval = self._lib.xPCTgScSetYLimits(self._port,scNum,limits)
        self._checkerror()
        return retval
    def tgScSetSignalFormat(self, scNum,signalNo,signalFormat):
        retval = self._lib.xPCTgScSetSignalFormat(self._port,scNum,signalNo,signalFormat)
        self._checkerror()
        return retval
    def tgScGetSignalFormat(self, scNum,signalNo,signalFormat):
        retval = self._lib.xPCTgScGetSignalFormat(self._port,scNum,signalNo,signalFormat)
        self._checkerror()
        return retval
    def setLoadTimeOut(self, timeOut):
        retval = self._lib.xPCSetLoadTimeOut(self._port,timeOut)
        self._checkerror()
        return retval
    def errorMsg(self, errorno,errmsg):
        retval = self._lib.xPCErrorMsg(errorno,errmsg)
        self._checkerror()
        return retval
    def scGetType(self, scNum):
        retval = self._lib.xPCScGetType(self._port,scNum)
        self._checkerror()
        return retval
    def getLoadTimeOut(self, ):
        retval = self._lib.xPCGetLoadTimeOut(self._port)
        self._checkerror()
        return retval
    def openTcpIpPort(self, address,port):
        retval = self._lib.xPCOpenTcpIpPort(address,port)
        self._checkerror()
        return retval
    def openConnection(self, ):
        retval = self._lib.xPCOpenConnection(self._port)
        self._checkerror()
        return retval
    def closeConnection(self, ):
        retval = self._lib.xPCCloseConnection(self._port)
        self._checkerror()
        return retval
    def registerTarget(self, commType,ipAddress,ipPort,comPort,baudRate):
        retval = self._lib.xPCRegisterTarget(commType,ipAddress,ipPort,comPort,baudRate)
        self._checkerror()
        return retval
    def deRegisterTarget(self, ):
        retval = self._lib.xPCDeRegisterTarget(self._port)
        self._checkerror()
        return retval
    def getAPIVersion(self, ):
        retval = self._lib.xPCGetAPIVersion()
        self._checkerror()
        return retval
    def getTargetVersion(self, ver):
        retval = self._lib.xPCGetTargetVersion(self._port,ver)
        self._checkerror()
        return retval
    def targetPing(self, ):
        retval = self._lib.xPCTargetPing(self._port)
        self._checkerror()
        return retval
    def fSReadFile(self, fileHandle,start,numsamples,data):
        retval = self._lib.xPCFSReadFile(self._port,fileHandle,start,numsamples,data)
        self._checkerror()
        return retval
    def fSRead(self, fileHandle,start,numsamples,data):
        retval = self._lib.xPCFSRead(self._port,fileHandle,start,numsamples,data)
        self._checkerror()
        return retval
    def fSWriteFile(self, fileHandle,numbytes,data):
        retval = self._lib.xPCFSWriteFile(self._port,fileHandle,numbytes,data)
        self._checkerror()
        return retval
    def fSBufferInfo(self, data):
        retval = self._lib.xPCFSBufferInfo(self._port,data)
        self._checkerror()
        return retval
    def fSGetFileSize(self, fileHandle):
        retval = self._lib.xPCFSGetFileSize(self._port,fileHandle)
        self._checkerror()
        return retval
    def fSOpenFile(self, filename,attrib):
        retval = self._lib.xPCFSOpenFile(self._port,filename,attrib)
        self._checkerror()
        return retval
    def fSCloseFile(self, fileHandle):
        retval = self._lib.xPCFSCloseFile(self._port,fileHandle)
        self._checkerror()
        return retval
    def fSGetPWD(self, data):
        retval = self._lib.xPCFSGetPWD(self._port,data)
        self._checkerror()
        return retval
    def fTPGet(self, fileHandle,numbytes,filename):
        retval = self._lib.xPCFTPGet(self._port,fileHandle,numbytes,filename)
        self._checkerror()
        return retval
    def fTPPut(self, fileHandle,filename):
        retval = self._lib.xPCFTPPut(self._port,fileHandle,filename)
        self._checkerror()
        return retval
    def fSRemoveFile(self, filename):
        retval = self._lib.xPCFSRemoveFile(self._port,filename)
        self._checkerror()
        return retval
    def fSCD(self, filename):
        retval = self._lib.xPCFSCD(self._port,filename)
        self._checkerror()
        return retval
    def fSMKDIR(self, dirname):
        retval = self._lib.xPCFSMKDIR(self._port,dirname)
        self._checkerror()
        return retval
    def fSRMDIR(self, dirname):
        retval = self._lib.xPCFSRMDIR(self._port,dirname)
        self._checkerror()
        return retval
    def fSDir(self, path,listing,numbytes):
        retval = self._lib.xPCFSDir(self._port,path,listing,numbytes)
        self._checkerror()
        return retval
    def fSDirSize(self, path):
        retval = self._lib.xPCFSDirSize(self._port,path)
        self._checkerror()
        return retval
    def fSGetError(self, errCode,message):
        retval = self._lib.xPCFSGetError(self._port,errCode,message)
        self._checkerror()
        return retval
    def saveParamSet(self, filename):
        retval = self._lib.xPCSaveParamSet(self._port,filename)
        self._checkerror()
        return retval
    def loadParamSet(self, filename):
        retval = self._lib.xPCLoadParamSet(self._port,filename)
        self._checkerror()
        return retval
    def fSScSetFilename(self, scopeId,filename):
        retval = self._lib.xPCFSScSetFilename(self._port,scopeId,filename)
        self._checkerror()
        return retval
    def fSScGetFilename(self, scopeId,filename):
        retval = self._lib.xPCFSScGetFilename(self._port,scopeId,filename)
        self._checkerror()
        return retval
    def fSScSetWriteMode(self, scopeId,writeMode):
        retval = self._lib.xPCFSScSetWriteMode(self._port,scopeId,writeMode)
        self._checkerror()
        return retval
    def fSScGetWriteMode(self, scopeId):
        retval = self._lib.xPCFSScGetWriteMode(self._port,scopeId)
        self._checkerror()
        return retval
    def fSScSetWriteSize(self, scopeId,writeSize):
        retval = self._lib.xPCFSScSetWriteSize(self._port,scopeId,writeSize)
        self._checkerror()
        return retval
    def fSScGetWriteSize(self, scopeId):
        retval = self._lib.xPCFSScGetWriteSize(self._port,scopeId)
        self._checkerror()
        return retval
    def readXML(self, numbytes,data):
        retval = self._lib.xPCReadXML(self._port,numbytes,data)
        self._checkerror()
        return retval
    def fSDiskInfo(self, driveLetter):
        retval = self._lib.xPCFSDiskInfo(self._port,driveLetter)
        self._checkerror()
        return retval
    def fSFileTable(self, tableBuffer):
        retval = self._lib.xPCFSFileTable(self._port,tableBuffer)
        self._checkerror()
        return retval
    def fSDirItems(self, path,dirs,numDirItems):
        retval = self._lib.xPCFSDirItems(self._port,path,dirs,numDirItems)
        self._checkerror()
        return retval
    def fSDirStructSize(self, path):
        retval = self._lib.xPCFSDirStructSize(self._port,path)
        self._checkerror()
        return retval
    def getNumScopes(self, ):
        retval = self._lib.xPCGetNumScopes(self._port)
        self._checkerror()
        return retval
    def getNumHiddenScopes(self, ):
        retval = self._lib.xPCGetNumHiddenScopes(self._port)
        self._checkerror()
        return retval
    def getScopeList(self, data):
        retval = self._lib.xPCGetScopeList(self._port,data)
        self._checkerror()
        return retval
    def getHiddenList(self, data):
        retval = self._lib.xPCGetHiddenList(self._port,data)
        self._checkerror()
        return retval
    def scGetSignalList(self, scNum,data):
        retval = self._lib.xPCScGetSignalList(self._port,scNum,data)
        self._checkerror()
        return retval
    def getSimMode(self, ):
        retval = self._lib.xPCGetSimMode(self._port)
        self._checkerror()
        return retval
    def getPCIInfo(self, buf):
        retval = self._lib.xPCGetPCIInfo(self._port,buf)
        self._checkerror()
        return retval
    def getSessionTime(self, ):
        retval = self._lib.xPCGetSessionTime(self._port)
        self._checkerror()
        return retval
    def getLogStatus(self, logArray):
        retval = self._lib.xPCGetLogStatus(self._port,logArray)
        self._checkerror()
        return retval
    def fSFileInfo(self, fileHandle):
        retval = self._lib.xPCFSFileInfo(self._port,fileHandle)
        self._checkerror()
        return retval
    def setDefaultStopTime(self, ):
        retval = self._lib.xPCSetDefaultStopTime(self._port)
        self._checkerror()
        return retval
    def getXMLSize(self, ):
        retval = self._lib.xPCGetXMLSize(self._port)
        self._checkerror()
        return retval
    def isTargetScope(self, ):
        retval = self._lib.xPCIsTargetScope(self._port)
        self._checkerror()
        return retval
    def setTargetScopeUpdate(self, value):
        retval = self._lib.xPCSetTargetScopeUpdate(self._port,value)
        self._checkerror()
        return retval
    def fSReNameFile(self, fsName,newName):
        retval = self._lib.xPCFSReNameFile(self._port,fsName,newName)
        self._checkerror()
        return retval
    def fSScSetDynamicMode(self, scopeId,onoff):
        retval = self._lib.xPCFSScSetDynamicMode(self._port,scopeId,onoff)
        self._checkerror()
        return retval
    def fSScGetDynamicMode(self, scopeId):
        retval = self._lib.xPCFSScGetDynamicMode(self._port,scopeId)
        self._checkerror()
        return retval
    def fSScSetMaxWriteFileSize(self, scopeId,maxWriteFileSize):
        retval = self._lib.xPCFSScSetMaxWriteFileSize(self._port,scopeId,maxWriteFileSize)
        self._checkerror()
        return retval
    def fSScGetMaxWriteFileSize(self, scopeId):
        retval = self._lib.xPCFSScGetMaxWriteFileSize(self._port,scopeId)
        self._checkerror()
        return retval
    def initAPI(self, ):
        retval = self._lib.xPCInitAPI()
        self._checkerror()
        return retval
    def freeAPI(self, ):
        retval = self._lib.xPCFreeAPI()
        self._checkerror()
        return retval
    def resolveAPI(self, module):
        retval = self._lib.xPCResolveAPI(module)
        self._checkerror()
        return retval

    def _checkerror(self):
        err = self._lib.xPCGetLastError()
        if err == 0:
            return
        msg = create_string_buffer(256)
        self._lib.xPCErrorMsg(err, msg)
        raise XpcError(decode(msg.value))
    def _define_function(self, name, argtypes, restype):
        try:
            libfunction = getattr(self._lib, name)
        except AttributeError:
            return
        libfunction.argtypes = argtypes
        libfunction.restype = restype

if __name__=='__main__':
    lib = windll.LoadLibrary('xpcapi.dll')
    x = xpcapi(lib)
