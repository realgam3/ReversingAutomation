#include <stdio.h>
#include <windows.h>

void debuggerPresentInFunction() {
	if (IsDebuggerPresent()) {
		printf("Debugger Present (2)!!!\n");
	} else {
		printf("Hello User (2)\n");
	}
}

void main() {
	int result;
	if (IsDebuggerPresent()) {
		printf("Debugger Present!!!\n");
	} else {
		printf("Hello User\n");
	}

	debuggerPresentInFunction();
	
	result = IsDebuggerPresent();
	if (result) {
		printf("Debugger Present (3)!!!\n");
	} else {
		printf("Hello User (3)\n");
	}

}