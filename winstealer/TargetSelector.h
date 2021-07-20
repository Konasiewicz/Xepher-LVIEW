#pragma once
#include "MemSnapshot.h"
#include "Utils.h"
#include "PyGame.h"

class TargetSelector {

public:
	TargetSelector() {}

	PyGame* game;

// I don't have a time for this make ur self!
public:
	GameObject* GetBestTarget(const UnitTag& unittype, float range) {
		GameObject* champion;
		float lastHealth = FLT_MAX;
		if (!range || range == 0)
			range = game->localChampion->atkRange + game->localChampion->GetGameplayRadius();
		for (auto& champ : (unittype == Unit_Champion ? game->ms->champions : unittype == Unit_Minion_Lane ? game->ms->minions : unittype == Unit_Monster ? game->ms->jungle : game->ms->champions)) {
			if (champ->HasUnitTags(Unit_Champion_Clone))
				continue;
			if (champ->isAlive && champ->isVisible && champ->isTargetable && champ->IsEnemyTo(*game->localChampion) && lastHealth >= champ->health && game->Distance(champ.get(), game->localChampion) <= range) {
				lastHealth = champ->health;
				champion = champ.get();
			}
		};
		return champion;
	}
};