#define BOOST_DEBUG_PYTHON 
#define USE_IMPORT_EXPORT
#define USE_WINDOWS_DLL_SEMANTICS
#define STB_IMAGE_IMPLEMENTATION

#include "PyStructs.h"

#include <iostream>
#include "windows.h"
#include "Utils.h"
#include "Structs.h"
#include "LeagueMemoryReader.h"
#include "Offsets.h"
#include "AntiCrack.h"
#include "MapObject.h"
#include "GameData.h"
#include "imgui.h"
#include "ConsoleColor.h"
#include <chrono>
#include "Overlay.h"
#include <map>
#include <list>
#include <conio.h>
#include <thread>
#include <strsafe.h>
#include <iostream>
#include <Wininet.h>
#include <string>
#include <urlmon.h>
#include <tchar.h>
#pragma comment(lib, "urlmon.lib")
#pragma comment(lib, "wininet.lib")

using namespace std::this_thread;

using namespace std::chrono;
std::string version = "1.0.0.2";
inline bool exists_test3(const std::string& name) {
	struct stat buffer;
	return (stat(name.c_str(), &buffer) == 0);
}
size_t write_data(void* ptr, size_t size, size_t nmemb, FILE* stream) {
	size_t written = fwrite(ptr, size, nmemb, stream);
	return written;
}
void MainLoop(Overlay& overlay, LeagueMemoryReader& reader);

std::string replaceAll(std::string subject, const std::string& search,
	const std::string& replace) {
	size_t pos = 0;
	while ((pos = subject.find(search, pos)) != std::string::npos) {
		subject.replace(pos, search.length(), replace);
		pos += replace.length();
	}
	return subject;
}
std::string GetExePath()
{
	char szFilePath[MAX_PATH + 1] = { 0 };
	GetModuleFileNameA(NULL, szFilePath, MAX_PATH);
	/*
	strrchr: function function: find the position of the last occurrence of a character c in another string str (that is, find the position of the first occurrence of the character c from the right side of str),
	 And return the address of this location. If the specified character cannot be found, the function returns NULL.
	 Use this address to return the string from the last character c to the end of str.
	*/
	(strrchr(szFilePath, '\\'))[0] = 0; // Delete the file name, only get the path string //
	std::string path = szFilePath;
	return path;
}



template< class ExecutionPolicy, class ForwardIt, class UnaryPredicate >
ForwardIt remove_if(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last,
	UnaryPredicate p);
std::string DownloadString(std::string URL) {
	HINTERNET interwebs = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, NULL);
	HINTERNET urlFile;
	std::string rtn;
	if (interwebs) {
		urlFile = InternetOpenUrlA(interwebs, URL.c_str(), NULL, NULL, NULL, NULL);
		if (urlFile) {
			char buffer[2000];
			DWORD bytesRead;
			do {
				InternetReadFile(urlFile, buffer, 2000, &bytesRead);
				rtn.append(buffer, bytesRead);
				memset(buffer, 0, 2000);
			} while (bytesRead);
			InternetCloseHandle(interwebs);
			InternetCloseHandle(urlFile);
			std::string p = replaceAll(rtn, "|n", "\r\n");
			return p;
		}
	}
	InternetCloseHandle(interwebs);
	std::string p = replaceAll(rtn, "|n", "\r\n");
	return p;
}

std::wstring getComputerName() {
	wchar_t buffer[MAX_COMPUTERNAME_LENGTH + 1] = { 0 };
	DWORD cchBufferSize = sizeof(buffer) / sizeof(buffer[0]);
	if (!GetComputerNameW(buffer, &cchBufferSize))
		throw std::runtime_error("GetComputerName() failed.");
	return std::wstring(&buffer[0]);
}

int main()
{
	printf(
		"                _    _                _                                 \n"
		"               ( )  ( )              ( )                                \n"
		"               `\\`\\/'/'   __   _ _   | |__     __   _ __                \n"
		"                 >  <   /'__`\\( '_`\ |  _ `\\ /'__`\\( '__)               \n"
		"                /'/\\`\\ (  ___/| (_) )| | | |(  ___/| |                  \n"
		"               (_)  (_)`\\____)| ,__/'(_) (_)`\\____)(_)                  \n"
		" ______  ______               | |                        ______  ______ \n"
		"(______)(______)              (_)                       (______)(______)\n"
	);
	std::cout << yellow << "Version: " << version << white <<std::endl;
	Overlay overlay = Overlay();
	LeagueMemoryReader reader = LeagueMemoryReader();

	try {
		Sleep(1000);
		std::cout << green << "[+] Removed his shitty version check." << white << std::endl;

		std::cout << yellow << "[+] Initializing PyModule" << std::endl;
		PyImport_AppendInittab("winstealer", &PyInit_winstealer);
		Py_Initialize();
		printf("[+] Initialising imgui and directx UI\n");
		overlay.Init();
		printf("[+] Loading static map data\n");
		MapObject::Get(MapType::SUMMONERS_RIFT)->Load("data/height_map_sru.bin");
		MapObject::Get(MapType::HOWLING_ABYSS)->Load("data/height_map_ha.bin");
		printf("[+] Loading unit data\n");
		std::string dataPath("data");
		GameData::Load(dataPath);

		MainLoop(overlay, reader);

		Py_Finalize();

	}
	catch (std::runtime_error exception) {
		std::cout << exception.what() << std::endl;
	}

	printf("Press any key to exit...");
	getch();
}

void MainLoop(Overlay& overlay, LeagueMemoryReader& reader) {

	MemSnapshot memSnapshot;
	bool rehook = true;
	bool firstIter = true;

	printf("[i] Waiting for league process...\n");
	while (true) {

		bool isLeagueWindowActive = reader.IsLeagueWindowActive();
		if (overlay.IsVisible()) {
			if (Input::WasKeyPressed(HKey::F8)) {
				overlay.ToggleTransparent();
			}
			if (!isLeagueWindowActive) {
				overlay.Hide();
			}
		}
		else if (isLeagueWindowActive) {
			overlay.Show();
		}
		try {
			overlay.StartFrame();
			if (rehook) {
				reader.HookToProcess();
				rehook = false;
				firstIter = true;
				memSnapshot = MemSnapshot();
				printf("[i] Found league process. The UI will appear when the game stars.\n");
			}
			else {

				if (!reader.IsHookedToProcess()) {
					rehook = true;
					printf("[i] League process is dead.\n");
					printf("[i] Waiting for league process...\n");
				}

				reader.MakeSnapshot(memSnapshot);
				if (memSnapshot.gameTime > 2.f) {
					if (firstIter) {

						overlay.GameStart(memSnapshot);
						firstIter = false;
					}
					overlay.Update(memSnapshot);
				}
			}
			overlay.RenderFrame();
		}
		catch (WinApiException exception) {
			rehook = true;
		}
		catch (std::runtime_error exception) {
			printf("[!] Unexpected error occured: \n [!] %s \n", exception.what());
			break;
		}
	}
}
