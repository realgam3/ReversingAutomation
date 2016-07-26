isDebuggerPresent = pluginsdk.RemoteGetProcAddress('kernel32', 'IsDebuggerPresent')
isDebuggerPresentRet = None

def is_debugger_present_return_callback():
    global isDebuggerPresentRet
    print "isDebuggerPresentRet: 0x%08x" % isDebuggerPresentRet
    Register.EAX = 0
    Breakpoint.remove(isDebuggerPresentRet)
    isDebuggerPresentRet = None
    
def is_debugger_present_callback():
    global isDebuggerPresentRet
    print "isDebuggerPresent: 0x%08x" % isDebuggerPresent
    isDebuggerPresentRet = pluginsdk.Peek()
    print isDebuggerPresentRet
    Breakpoint.add(isDebuggerPresentRet, is_debugger_present_return_callback)
    
Breakpoint.add(isDebuggerPresent, is_debugger_present_callback)
