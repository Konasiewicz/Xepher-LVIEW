#pragma once
#include <string>

class BuffInstance
{
public:

	BuffInstance(std::string buffname, bool isAlive, int buffcount, int countalt, int type, float starttime, float endtime) : name(buffname), isAlive(isAlive), count(buffcount), countAlt(countalt), type(type), startTime(starttime), endTime(endtime) {}

	std::string name;
	bool isAlive;
	int count;
	int countAlt;
	int type;
	float startTime;
	float endTime;
};