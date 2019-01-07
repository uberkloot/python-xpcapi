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

from ._xpcapi import (
    _xpcapi, XpcError, decode, dirStruct, diskinfo,
    MAX_ERR_MSG_LENGTH, MAX_SCOPES, MAX_SIGNALS,
    COMMTYP, SCTYPE, TRIGMD, TRIGSLOPE, SCMODE, SCST, LGMOD
    )
    
import ctypes
import os
import string
import sys
import datetime
from collections import namedtuple
import itertools

def sanitizeName(name):
    """Replace all non-alphanumeric characters in name to alpha-numeric characters"""
    return ''.join(c if c.isalnum() else '_' for c in name)
    

class XpcParam:
    """Represents a parameter of an XpcBlock"""
    def __init__(self, model, path, index):
        self._xpc = model._xpc
        self._model = model
        self._path = path
        self._index = index
        
    def __call__(self, value = None):
        if value is None: # Read
            return self._xpc.getParam(self._index)
        else: # Write
            self._xpc.setParam(self._index, value)
    
    def __repr__(self):
        return '<XpcParam %d (%s) = %s>' % (self._index, self._path, self())
        
        
class XpcSignal:
    """Represents a signal of an XpcBlock"""
    def __init__(self, xpc, path, index):
        self._xpc = xpc
        self._path = path
        self._index = index
        
    def __call__(self):
        return self._xpc.getSignal(self._index)
        
    def __repr__(self):
        return '<XpcSignal %d (%s) = %s>' % (self._index, self._path, self())
        
    def __int__(self):
        return self._index


class XpcBlock:
    """Represents a (sub-)block of an xpc model"""
    
    
    def __init__(self, model, path):
        # These first assignments go via __dict__ to prevent calling __setattr__
        self.__dict__['_params_'] = {}
        self.__dict__['_signals_'] = {}
        self.__dict__['_blocks_'] = {}
        self.__dict__['_model_'] = model
        self.__dict__['_path_'] = path

        
    def _getBlock(self, path):
        """Get an XpcBlock which is located underneath this XpcBloc, specified
        by the path (which is /-separated)
        
        If the current block is A/B , the block A/B/C/D can be reached by calling
        '_getBlock('C/D')
        
        As a side effect, blocks and subblocks that are not known yet are added.
        This is used during the building of the model.
        
        This function should not be used directly. Instead, use attribute access
        (e.g. thisBlock.C.D) to access sub-blocks
        
        """
        if path == '':
            return self
            
        first, _, rest = path.partition('/')
        saneFirst = sanitizeName(first)
        
        try:
            subblock =  self._blocks_[saneFirst]
        except KeyError:
            if self._path_ == '':
                subpath = first
            else:
                subpath = self._path_ + '/' + first
                
            subblock = self._blocks_[saneFirst] = XpcBlock(self, subpath)
        
        if rest == '':
            return subblock
        else:
            return subblock._getBlock(rest)
            
    def tree(self, indent = ''):
        ret = indent + (self._path_ or 'model root')
        
        for subblock in self._blocks_.values():
            ret += '\n' + subblock.tree(indent + '  ')
        
        return ret
    
    def __dir__(self):
        return list(
            set(object.__dir__(self)) |
            set(self._blocks_.keys()) |
            set(self._signals_.keys()) |
            set(self._params_.keys())
            )

        
    def __getattr__(self, attr):
        if attr in self._blocks_:
            return self._blocks_[attr]
        if attr in self._signals_:
            return self._signals_[attr]
        if attr in self._params_:
            return self._params_[attr]
        raise AttributeError
    
    def __setattr__(self, attr, value):
        raise AttributeError
            
    def __repr__(self):
        return '<xpcblock %s>' % self._path_
            
            
    
                   

class XpcModel(XpcBlock):
    def __init__(self, xpc):
        XpcBlock.__init__(self, self, '')
        
        self.__dict__['_xpc'] = xpc
        for i in range(xpc.getNumSignals()):
            block, _, signal = xpc.getSignalName(i).rpartition('/')
            label = xpc.getSignalLabel(i)
            if not label:
                label = signal
                
            self._getBlock(block)._signals_[sanitizeName(label)] = XpcSignal(self._xpc, block + '/' + signal, i)
            
        for i in range(xpc.getNumParams()):
            block, param = xpc.getParamName(i)
            self._getBlock(block)._params_[sanitizeName(param)] = XpcParam(self, block + '/' + param, i)
            
    def __repr__(self):
        return '<xpcmodel>'
        

def defaultDllPath():
    if getattr(sys,'frozen', False):
        # Frozen, try from the executable dir
        return os.path.join(os.path.dirname(sys.executable), 'xpcapi.dll')
    
    else:
        # Try from the module dir
        return os.path.join(os.path.dirname(__file__), 'xpcapi.dll')    


class XpcFile:
    def __init__(self, xpc, filename, mode):
        self._xpc = xpc
        self._handle = xpc.fSOpenFile(filename, mode)
        self._pos = 0
        self._size = xpc.fSGetFileSize(self._handle)
        
    def read(self, nbytes = None):
        if self._handle is None:
            raise RuntimeError('read on closed file')
            
        if nbytes is None:
            nbytes = self._size - self._pos
        else:
            nbytes = min(nbytes, self._size - self._pos)
        
        if nbytes == 0:
            return b''
            
        buffer = ctypes.create_string_buffer(nbytes)
        
        self._xpc.fSReadFile(self._handle, self._pos, nbytes,
                             ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte )))
        
        self._pos += nbytes
        
        return buffer.raw
    
    def close(self):
        if self._handle is not None:
            self._xpc.fSCloseFile(self._handle)
        self._handle = None
    
    def __del__(self):
        self.close()
        

class XpcScope:
    # Scope related enums
    SCTYPE, TRIGMD, TRIGSLOPE, SCMODE, SCST = SCTYPE, TRIGMD, TRIGSLOPE, SCMODE, SCST
    def __init__(self, xpc, id):
        self._xpc = xpc
        self._id = id
    def __int__(self):
        return self._id
    
    def __eq__(self, other):
        return isinstance(other, XpcScope) and other._id == self._id    
    
    def start(self):
        self._xpc.scStart(self._id)
        
    def stop(self):
        self._xpc.scStop(self._id)

    def isFinished(self):
        return self._xpc.isScFinished(self._id)
    
    def getStartTime(self):
        return self._xpc.scGetStartTime(self._id)

    def getAutoRestart(self):
        return bool(self._xpc.scGetAutoRestart(self._id))
        
    def setAutoRestart(self, autoRestart):
        self._xpc.scSetAutoRestart(self._id, autoRestart)

    def getDecimation(self):
        return self._xpc.scGetDecimation(self._id)
    
    def setDecimation(self, decimation):
        self._xpc.scSetDecimation(self._id, decimation)
        
    def getNumSamples(self):
        return self._xpc.scGetNumSamples(self._id)
    
    def setNumSamples(self, numSamples):
        self._xpc.scSetNumSamples(self._id, numSamples)
    
    def getSignals(self):
        '''
        Get a list of XpcSignals for this scope
        '''
        # TODO: use scGetSignals instead
        scdata = self._xpc.getScope(self._id)
        sigIds = itertools.takewhile(lambda x: x>=0, scdata.signals)
        
        return [XpcSignal(self._xpc, self._xpc.getSignalName(id), id) for id in sigIds]
    
    def addSignal(self, signal):
        '''
        Add a signal to a scope, can be either a signal index or an XpcSignal
        '''
        self._xpc.scAddSignal(self._id, int(signal))   
    
    def removeSignal(self, signal):
        '''
        Remove a signal from a scope, can be either a signal index or an XpcSignal
        '''
        self._xpc.scRemSignal(self._id, int(signal))
            
    def getType(self):
        return SCTYPE(self._xpc.scGetType(self._id))
        
    def getState(self):
        return SCST(self._xpc.scGetState(self._id))
    
    def getTriggerMode(self):
        return TRIGMD(self._xpc.scGetTriggerMode(self._id))
    
    def setTriggerMode(self, mode):
        '''Set trigger mode (a TRIGMD value)'''
        self._xpc.scSetTriggerMode(self._id, mode)

    def getTriggerScope(self):
        '''
        Returns the triggering scope (trigger source) for this scope
        Note that a new XpcScope object is returned
        '''
        return XpcScope(self, self._xpc.scGetTriggerScope(self._id))
    
    def setTriggerScope(self, scope):
        self._xpc.scSetTriggerScope(self._id, int(scope))

    def getTriggerScopeSample(self):
        return self._xpc.scGetTriggerScopeSample(self._id)
    
    def setTriggerScopeSample(self, triggerScopeSample):
        self._xpc.scSetTriggerScopeSample(self._id, triggerScopeSample)

    def getTriggerSignal(self):
        id = self._xpc.scGetTriggerSignal(self._id)
        if id == -1:
            return None
        else:
            return XpcSignal(self._xpc, self._xpc.getSignalName(id), id)
    
    def setTriggerSignal(self, signal):
        self._xpc.scSetTriggerSignal(self._id, int(signal))

    def getTriggerSlope(self):
        return TRIGSLOPE(self._xpc.scGetTriggerSlope(self._id))
    
    def setTriggerSlope(self, slope):
        '''Set trigger slope (a TRIGSLOPE value)'''
        self._xpc.scSetTriggerSlope(self._id, slope)
        
    def getTriggerLevel(self):
        return self._xpc.scGetTriggerLevel(self._id)
    
    def setTriggerLevel(self, level):
        self._xpc.scSetTriggerLevel(self._id, level)
    
    def softwareTrigger(self):
        self._xpc.scSoftwareTrigger(self._id)
        
    def getNumPrePostSamples(self):
        return self._xpc.scGetNumPrePostSamples(self._id)

    def setNumPrePostSamples(self, numSamples):
        self._xpc.scSetNumPrePostSamples(self._id, numSamples)

    # File scope specific
    def setFilename(self, filename):
        self._xpc.fSScSetFilename(self._id, filename)
        
    def getFilename(self):
        buffer = ctypes.create_string_buffer(256)
        self._xpc.fSScGetFilename(self._id, buffer)
        
        return decode(buffer.value)
        
    # Target scope specific
    def setMode(self, mode):
        self._xpc.tgScSetMode(self._id, mode)
    
    def getMode(self):
        return SCMODE(self._xpc.tgScGetMode(self._id))


FileInfo = namedtuple('FileInfo', 'name, size, isdir, datetime')        
        
class XpcApi(_xpcapi):

    def __init__(self, dllpath = None):
        
        if dllpath is None:
            dllpath = defaultDllPath()

        lib = ctypes.windll.LoadLibrary(dllpath)
        
        
        super().__init__(lib)
        self._port = None
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = XpcModel(self)
        return self._model
        
        
    def openTcpIpPort(self, address,port):
        self._port = _xpcapi.openTcpIpPort(self, address,port)
    def loadApp(self, file):
   
        absfile = os.path.abspath(file)
        if not os.path.exists(absfile):
            raise IOError('file %s does not exist' % absfile)
        
        root, ext = os.path.splitext(absfile)
        
        if not ext.lower() == '.dlm':
            raise IOError('app filename should have .dlm extension')     
        
        head, tail = os.path.split(root)
        
        super().loadApp(head, tail)
        self._model = None
    
    def closePort(self):
        super().closePort()
        self._port = None
        self._model = None
    
    def getAPIVersion(self):
        return decode(ctypes.cast(super().getAPIVersion(), ctypes.c_char_p).value)
    
    def getAppName(self):
        name = ctypes.create_string_buffer(256)
        super().getAppName(name)
        return decode(name.value)
    
    def setParam(self, parIdx, value):
        ny, nx = self.getParamDims(parIdx)
        
        if nx!=1 or ny!=1:
            raise NotImplementedError
        values = (ctypes.c_double * 1)(value)
        
        super().setParam(parIdx, values)
        
    def getParam(self, parIdx):
        ny, nx = self.getParamDims(parIdx)
        
        if nx!=1 or ny!=1:
            raise NotImplementedError
        values = (ctypes.c_double * 1)()
        
        super().getParam(parIdx, values)
        
        return values[0]
        
    def getSignals(self, sigIdxs):
        numSignals = len(sigIdxs)
        indices = (ctypes.c_int * numSignals)(*sigIdxs)
        values = (ctypes.c_double * numSignals)()
        
        super().getSignals(numSignals, indices, values)
        return values
    def getSignal(self, sigIdx):
        return self.getSignals((sigIdx,))[0]
        
    
    def getParamName(self, parIdx):
        block = ctypes.create_string_buffer(256)
        param = ctypes.create_string_buffer(256)
        super().getParamName(parIdx, block, param)
        return decode(block.value), decode(param.value)
        
    def getSignalName(self, sigIdx):
        sigName = ctypes.create_string_buffer(256)
        super().getSignalName(sigIdx, sigName)
        return decode(sigName.value)
        
    def getSignalLabel(self, sigIdx):
        sigLabel = ctypes.create_string_buffer(256)
        super().getSignalLabel(sigIdx, sigLabel)
        return decode(sigLabel.value)
    
    def getSigIdxfromLabel(self, label):
        width = self.getSigLabelWidth(label)
        indices = (ctypes.c_int * width)()
        super().getSigIdxfromLabel(label, indices)
        return indices
        
    def getParamDims(self, parIdx):
        dims = (ctypes.c_int *2)()
        super().getParamDims(parIdx, dims)
        return list(dims)
        
    def openFile(self, filename, mode):
        if mode != 'r':
            raise NotImplementedError('Only file mode "r" is implemented')
        return XpcFile(self, filename, mode)
        
    def listDir(self, path):
        numItems = self.fSDirStructSize(path)
        items = (dirStruct * numItems)()
        
        self.fSDirItems(path, items, numItems)
        
        dirlist = []
        
        for item in items:
            name = decode(item.name).strip()
            ext = decode(item.ext).strip()
            
            filename = name + ('.' if ext else '') + ext
            fdatetime = datetime.datetime(item.year, item.month, item.day, item.hour, item.min)
            dirlist.append(FileInfo(filename, item.size, bool(item.isDir), fdatetime))

        return dirlist
       
    
    def getScopes(self):
        scopes = (ctypes.c_int * (MAX_SCOPES+1))()
        super().getScopes(scopes)
        
        # Scopes is a -1 terminated list, return an XpcScope object for each scope
        return {
                id: XpcScope(self, id) for id in 
                    itertools.takewhile(lambda x: x>=0, scopes)
                }
    
    def addScope(self, type, id = None):
        if id is None:
            id = max(self.getScopes().keys(), default = 0) + 1
        
        super().addScope(type, id)
        
        return XpcScope(self, id)
        
    def getDiskInfo(self,driveLetter):
        return self.fSDiskInfo(driveLetter)

    
