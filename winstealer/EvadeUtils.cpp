#pragma once
#include "PyGame.h"
#include "Vector.h"
#include "Utils.h"

class EvadeUtils {
	Vector3 GetBestEvadePos(GameObject* player, GameObject& missile, float bounding) {

		Vector3 direction = missile.endPos - missile.startPos;

		Vector3 rightPos = missile.endPos + Vector3(-direction.z, direction.y, direction.x * 1.f);
		Vector3 leftPos = missile.endPos + Vector3(direction.z * 1.f, direction.y, -direction.x);

		/*Vector3 rightDirection = rightPos - leftPos;
		Vector3 rightDirection = PyGame().clamp_norm_2d(rightDirection, player->GetGameplayRadius());
		Vector3 leftDirection = Vector3();
		leftDirection.x = -rightDirection.x;
		leftDirection.y = -rightDirection.y;
		leftDirection.z = -rightDirection.z;*/
	}
};