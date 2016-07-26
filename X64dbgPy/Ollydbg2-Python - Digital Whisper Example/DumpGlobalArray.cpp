#include <stdio.h>
#include <windows.h>

int Test1();
int Test2();
int Test3();
int Test4();

typedef struct App {
    int id;
    char *name;
	int (*callback)();
} App;

App appArr[] = {
	{0, "Test1", Test1},
	{1, "Test2", Test2},
	{2, "Test3", Test3},
	{3, "Test4", Test4}
};

int main(int argc, const char* argv[]) {
	int i, callbackResult;

	for (i=0; i<ARRAYSIZE(appArr); i++) {
		printf("App Id: %d\n", appArr[i].id);
		printf("App Name: %s\n", appArr[i].name);
		printf("Callback Output: \n");
		callbackResult = appArr[i].callback();
		printf("Callback Result: %d\n", callbackResult);
		printf("\n");
	}
	
	printf("Struct Size: 0x%02X\n", sizeof(App));
	printf("Array Size: 0x%02x\n", sizeof(appArr));
    return 0;
}

int Test1() {
    printf("Test1 Callback\n");
	return 1;
}

	int Test2() {
		printf("Test2 Callback\n");
		return 2;
	}

	int Test3() {
    printf("Test3 Callback\n");
	return 3;
}

int Test4() {
    printf("Test4 Callback\n");
	return 4;
}
