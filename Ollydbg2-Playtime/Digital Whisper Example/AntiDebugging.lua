isDebuggerPresent = GPA("kernel32", "IsDebuggerPresent")
isDebuggerPresentRet = nil

Event.Listen("Int3Breakpoint", function(info)
	if info.Address == isDebuggerPresent then
		if isDebuggerPresentRet == nil then
			isDebuggerPresentRet = Pop()
			Push(isDebuggerPresentRet)
			SetInt3Breakpoint(isDebuggerPresentRet)
		end
	elseif info.Address == isDebuggerPresentRet then
		EAX = 0
		RemoveInt3Breakpoint(isDebuggerPresentRet)
		isDebuggerPresentRet = nil
	end
end)

SetInt3Breakpoint(isDebuggerPresent)