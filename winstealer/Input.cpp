#include "Input.h"
#include "windows.h"
#include <thread>
#include <chrono>
#include "Vector.h"
#include "PyGame.h"
#include <ctime>
#include "LeagueMemoryReader.h"
using namespace std::chrono;
using namespace std::this_thread;
using namespace std::chrono_literals;
LeagueMemoryReader reader = LeagueMemoryReader();
void Input::PressKey(HKey key) {
	INPUT input;
	input.type = INPUT_KEYBOARD;
	input.ki.wScan = key;
	input.ki.time = 0;
	input.ki.dwExtraInfo = 0;
	input.ki.wVk = 0;
	input.ki.dwFlags = KEYEVENTF_SCANCODE;
	SendInput(1, &input, sizeof(INPUT));

	Sleep(8);
	input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
	SendInput(1, &input, sizeof(INPUT));
}

void Input::KeyUp(HKey key) {
	INPUT input;
	input.type = INPUT_KEYBOARD;
	input.ki.wScan = key;
	input.ki.time = 0;
	input.ki.dwExtraInfo = 0;
	input.ki.wVk = 0;
	input.ki.dwFlags = KEYEVENTF_KEYUP;
	SendInput(1, &input, sizeof(INPUT));
}

void Input::KeyDown(HKey key) {
	INPUT input;
	input.type = INPUT_KEYBOARD;
	input.ki.wScan = key;
	input.ki.time = 0;
	input.ki.dwExtraInfo = 0;
	input.ki.wVk = 0;
	input.ki.dwFlags = KEYEVENTF_SCANCODE;
	SendInput(1, &input, sizeof(INPUT));
}

bool Input::WasKeyPressed(HKey key) {

	static high_resolution_clock::time_point nowTime;
	static high_resolution_clock::time_point lastTimePressed[300] = {high_resolution_clock::now()};
	static bool pressed[300] = { 0 };

	static duration<float, std::milli> timeDiff;

	int virtualKey = MapVirtualKeyA(key, MAPVK_VSC_TO_VK);
	if (virtualKey == 0)
		return false;

	nowTime = high_resolution_clock::now();
	timeDiff = nowTime - lastTimePressed[virtualKey];
	if (pressed[virtualKey]) {

		if (timeDiff.count() > 200)
			pressed[virtualKey] = false;
		return false;
	}
		
	bool keyDown = GetAsyncKeyState(virtualKey) & 0x8000;
	if (keyDown) {
		lastTimePressed[virtualKey] = high_resolution_clock::now();
		pressed[virtualKey] = true;
		return true;
	}

	return false;
}

bool Input::IsKeyDown(HKey key) {
	int virtualKey = MapVirtualKeyA(key, MAPVK_VSC_TO_VK);
	if (virtualKey == 0)
		return false;

	return GetAsyncKeyState(virtualKey);
}

Vector2 Input::GetCursorPosition()
{
	POINT pos;
	GetCursorPos(&pos);
	//std::cout << "GET_CURSOR_POSITION" << std::endl;
	//std::cout << "POS X: " <<pos.x << "POS Y: "<<pos.y << std::endl;

	return { (float)pos.x, (float)pos.y };
}

void Input::PressLeftClick()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
	SendInput(1, &input, sizeof(INPUT));

	Sleep(8);

	input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
	SendInput(1, &input, sizeof(INPUT));
}

void Input::PressRightClick()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN;
	SendInput(1, &input, sizeof(INPUT));

	Sleep(8);

	input.mi.dwFlags = MOUSEEVENTF_RIGHTUP;
	SendInput(1, &input, sizeof(INPUT));
}

void Input::Move(int x, int y)
{
	SetCursorPos(x, y);
	//DWORD nx = 65535 / GetSystemMetrics(SM_CXSCREEN) * x -1;
	//DWORD ny = 65535 / GetSystemMetrics(SM_CYSCREEN) * y -1;
	//mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0);

	POINT mouse_pos;
	GetCursorPos(&mouse_pos);
	//std::cout << "INPUT_MOVE" << std::endl;
	//std::cout << "MOUSE POS X: " << mouse_pos.x << "MOUSE POS Y: " << mouse_pos.y << std::endl;
	

	if (mouse_pos.x != x || mouse_pos.y != y)
		SetCursorPos(x, y);
}

void Input::ClipMouse(float x, float y) {
	RECT rect = RECT();
	rect.bottom = y;
	rect.top = y;
	rect.right = x;
	rect.left = x;
	ClipCursor(&rect);
}

void Input::ClickAt(bool leftClick, float x, float y)
{
	static float fScreenWidth = (float)::GetSystemMetrics(SM_CXSCREEN) - 1;
	static float fScreenHeight = (float)::GetSystemMetrics(SM_CYSCREEN) - 1;

	POINT oldPos;
	GetCursorPos(&oldPos);
	
	//std::cout << "Old Pos X: "<<oldPos.x << std::endl;
	//std::cout << "Old Pos Y: "<<oldPos.y << std::endl;
	//std::cout << "New Pos X: " << x << std::endl;
	//std::cout << "New Pos Y: " << y << std::endl;

	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE;
	input.mi.dx = (LONG)(x * (65535.0f / fScreenWidth));
	input.mi.dy = (LONG)(y * (65535.0f / fScreenHeight));
	SendInput(1, &input, sizeof(INPUT));

	input.mi.dwFlags = (leftClick ? MOUSEEVENTF_LEFTDOWN : MOUSEEVENTF_RIGHTDOWN);
	SendInput(1, &input, sizeof(INPUT));

	Sleep(8);

	input.mi.dwFlags = (leftClick ? MOUSEEVENTF_LEFTUP : MOUSEEVENTF_RIGHTUP);
	SendInput(1, &input, sizeof(INPUT));

	input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE;
	input.mi.dx = (LONG)(oldPos.x * (65535.0f / fScreenWidth));
	input.mi.dy = (LONG)(oldPos.y * (65535.0f / fScreenHeight));
	SendInput(1, &input, sizeof(INPUT));
	SendInput(1, &input, sizeof(INPUT));
}

void Input::MouseRightDown()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_ABSOLUTE;
	SendInput(1, &input, sizeof(INPUT));
	ZeroMemory(&input, sizeof(INPUT));
}

void Input::MouseRightUp()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_RIGHTUP | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_ABSOLUTE;
	SendInput(1, &input, sizeof(INPUT));
	ZeroMemory(&input, sizeof(INPUT));
}

void Input::MouseLeftDown()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
	SendInput(1, &input, sizeof(INPUT));
	ZeroMemory(&input, sizeof(INPUT));
}

void Input::MouseLeftUp()
{
	INPUT input = { 0 };
	input.type = INPUT_MOUSE;
	input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
	SendInput(1, &input, sizeof(INPUT));
	ZeroMemory(&input, sizeof(INPUT));
}

void Input::MoveAndPress(HKey key, float x, float y)
{
	BlockInput(true);
	POINT oldPos;
	GetCursorPos(&oldPos);
	Move(x, y);
	PressLeftClick();
	PressKey(key);
	Move(oldPos.x, oldPos.y);
	BlockInput(false);
}