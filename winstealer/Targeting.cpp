#include "Targeting.h"
#include "PyGame.h"

void Targeting::GetBestTarget(float range) {
	PyGame game = PyGame();
	if (!range) {
		range = 500;
		game.GetLocalChampion().attr();
	}
}