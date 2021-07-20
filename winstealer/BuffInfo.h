#pragma once
#include <map>
#include <string>

struct ItemInfo {

public:
	std::string name;
	int count;
	int countAlt;
	int type;
	float startTime;
	float endTime;
	bool isAlive;
};
