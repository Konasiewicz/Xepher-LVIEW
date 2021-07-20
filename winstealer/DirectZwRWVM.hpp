#pragma once
#include <Windows.h>

class DirectZwRWVM {
public:

protected:
	DirectZwRWVM();
	~DirectZwRWVM();

	NTSTATUS ZwRWVM(HANDLE hProcess, void* lpBaseAddress, void* lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesRead);
};