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
'''
Helper script to generate _xpcapi.py from xpcapi.h definition

'''


from pycparser import parse_file, c_ast
import re


p=parse_file('xpcapi.h', use_cpp = True, cpp_args=['-DXPCAPIFUNC(type, fun)=type fun', '-DHMODULE=void * module'])


def ctypes_type(node):
    if isinstance(node, c_ast.IdentifierType):
        return '_'.join(node.names)
    elif isinstance(node, (c_ast.TypeDecl, c_ast.Decl, c_ast.Typename)):
        return ctypes_type(node.type)
    elif isinstance(node, c_ast.PtrDecl):
        return 'POINTER(%s)' % ctypes_type(node.type)
    else:
        raise Exception


initcode = ''
classcode = ''



for f in p.ext:
    typ = f.type
    if isinstance(typ, c_ast.FuncDecl):
        if not f.name.startswith('xPC'):
            continue
            
        parameters = [(param.name, ctypes_type(param.type)) for param in f.type.args.params]
        if parameters == [(None, 'void')]:
            parameters = []

        # Convert all char pointers in the arguments to c_str, which will do unicode -> bytes conversion for Python 3
        paramtypes = ['c_str' if p[1] == 'POINTER(char)' else p[1] for p in parameters]
        paramnames = [p[0] for p in parameters]
        
        restype = ctypes_type(f.type.type)
        
        
            
        
        initcode += '        self._define_function("%s", [%s], %s)\n' % (f.name, ','.join(paramtypes), restype)
        
        methodparams = paramnames
        libparams = paramnames
        
        if paramnames and paramnames[0] == 'port':
            methodparams = methodparams[1:]
            libparams[0] = 'self._port'
        
        methodname = f.name[3].lower() + f.name[4:]
        
        classcode += '    def %s(self, %s):\n        retval = self._lib.%s(%s)\n        self._checkerror()\n        return retval\n' % (methodname, ','.join(methodparams), f.name, ','.join(libparams))
        

## xpciapconst constants
xpcapiconst = open('xpcapiconst.h').read()
constants = ''
enums = {}
for name, value in re.findall('^#define\s+(\w+)\s+(\d+)\w*$', xpcapiconst, re.MULTILINE):
    if name.startswith('MAX_'):
        constants += '%s=%s\n' % (name, value)
    else:
        enum, sep, item = name.partition('_')
        enums.setdefault(enum, []).append((item, value))

for enum, items in enums.items():
    constants += '\nclass %s(IntEnum):\n' % enum
    for item in items:
        constants += '    %s=%s\n' % item

##
        

of = open ('../xpcapi/_xpcapi.py', 'w')
of.write( """\
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

%s

class XpcError(IOError):
    pass

class _xpcapi:
    def __init__(self, lib):
        self._lib = lib
        self._port = -1
%s
%s
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
""" % (constants, initcode, classcode))



of.close()
