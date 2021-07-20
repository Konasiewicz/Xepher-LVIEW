#pragma once
#include <Windows.h>

class Utils {
public:

protected:
	Utils();
	~Utils();

	NTSTATUS ZwRWVM(HANDLE hProcess, void* lpBaseAddress, void* lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesRead);
};