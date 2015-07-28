isDebuggerPresent = pluginsdk.RemoteGetProcAddress('kernel32', 'IsDebuggerPresent')
isDebuggerPresentRet = None

# Temporary Hacks (Better solution will be in the official api)
def SetInt3Breakpoint(addr):
    pluginsdk.x64dbg.DbgCmdExecDirect("bp %08x" % addr)

def RemoveInt3Breakpoint(addr):
    pluginsdk.x64dbg.DbgCmdExecDirect("bpc %08x" % addr)

def breakpoint_callback(**info):
    if info['addr'] == isDebuggerPresent:
        print "isDebuggerPresent: 0x%08x" % isDebuggerPresent
        global isDebuggerPresentRet
        isDebuggerPresentRet = pluginsdk.Peek()
        SetInt3Breakpoint(isDebuggerPresentRet)
    elif info['addr'] == isDebuggerPresentRet:
        print "isDebuggerPresentRet: 0x%08x" % isDebuggerPresentRet
        Register.EAX = 0
        RemoveInt3Breakpoint(isDebuggerPresentRet)
        isDebuggerPresentRet = None

SetInt3Breakpoint(isDebuggerPresent)
Event.listen('breakpoint', breakpoint_callback);
