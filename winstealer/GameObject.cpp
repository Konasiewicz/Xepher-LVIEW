#include "GameObject.h"
#include "Utils.h"
#include "Offsets.h"
#include "Spell.h"
#include "GameData.h"
#include "PyGame.h"
#include "thread"

using namespace std::this_thread;

BYTE  GameObject::buff[GameObject::sizeBuff]         = {};
BYTE  GameObject::buffDeep[GameObject::sizeBuffDeep] = {};

bool GameObject::HasUnitTags(const UnitTag& type1) const {
	return unitInfo->tags.test(type1);
}

bool GameObject::IsEqualTo(const GameObject& other) const {
	return this->objectIndex == other.objectIndex;
}

bool GameObject::IsNotEqualTo(const GameObject& other) const {
	return this->objectIndex != other.objectIndex;
}

float GameObject::GetAcquisitionRadius() const
{
	return unitInfo->acquisitionRange;
}

float GameObject::GetSelectionRadius() const
{
	return unitInfo->selectionRadius;
}

float GameObject::GetPathingRadius() const
{
	return unitInfo->pathRadius;
}

float GameObject::GetGameplayRadius() const
{
	return unitInfo->gameplayRadius;
}

float GameObject::GetBasicAttackMissileSpeed() const
{
	return unitInfo->basicAttackMissileSpeed;
}

float GameObject::GetBasicAttackWindup() const
{
	return unitInfo->basicAttackWindup;
}

float GameObject::GetAttackSpeedRatio() const
{
	return unitInfo->attackSpeedRatio;
}

float GameObject::GetBaseMovementSpeed() const
{
	return unitInfo->baseMovementSpeed;
}

float GameObject::GetBaseAttackSpeed() const
{
	return unitInfo->baseAttackSpeed;
}

float GameObject::GetBaseAttackRange() const
{
	return unitInfo->baseAttackRange;
}

float GameObject::GetAttackRange()  const {
	return GetBaseAttackRange() + GetGameplayRadius();
}

float GameObject::GetHpBarHeight() const
{
	return unitInfo->healthBarHeight;
}

bool GameObject::IsEnemyTo(const GameObject& other) const {
	return this->team != other.team;
}

bool GameObject::IsAllyTo(const GameObject& other) const {
	return this->team == other.team;
}

void GameObject::LoadFromMem(DWORD base, HANDLE hProcess, bool deepLoad) {

	address = base;
	Mem::Read(hProcess, base, buff, sizeBuff);

	std::chrono::duration<float, std::milli> timeDuration = high_resolution_clock::now() - timeSinceLastPreviousPosition;
	if (timeDuration.count() > 25) {
		previousPosition = position.clone();
		timeSinceLastPreviousPosition = high_resolution_clock::now();
	}

	memcpy(&team,          &buff[Offsets::ObjTeam],          sizeof(short));
	memcpy(&position,      &buff[Offsets::ObjPos],           sizeof(Vector3));
	memcpy(&health,        &buff[Offsets::ObjHealth],        sizeof(float));
	memcpy(&maxHealth,     &buff[Offsets::ObjMaxHealth],     sizeof(float));
	memcpy(&mana,		   &buff[Offsets::ObjMana],			 sizeof(float));
	memcpy(&maxMana,	   &buff[Offsets::ObjMaxMana], sizeof(float));
	memcpy(&baseAttack,    &buff[Offsets::ObjBaseAtk],       sizeof(float));
	memcpy(&bonusAttack,   &buff[Offsets::ObjBonusAtk],      sizeof(float));
	memcpy(&armour,        &buff[Offsets::ObjArmor],         sizeof(float));
	memcpy(&magicResist,   &buff[Offsets::ObjMagicRes],      sizeof(float));
	memcpy(&duration,      &buff[Offsets::ObjExpiry],        sizeof(float));
	memcpy(&isVisible,     &buff[Offsets::ObjVisibility],    sizeof(bool));
	memcpy(&objectIndex,   &buff[Offsets::ObjIndex],         sizeof(short));
	memcpy(&crit,          &buff[Offsets::ObjCrit],          sizeof(float));
	memcpy(&critMulti,     &buff[Offsets::ObjCritMulti],     sizeof(float));
	memcpy(&abilityPower,  &buff[Offsets::ObjAbilityPower],  sizeof(float));
	memcpy(&isMoving,	   &buff[Offsets::ObjIsMoving], sizeof(bool));
	memcpy(&atkSpeedMulti, &buff[Offsets::ObjAtkSpeedMulti], sizeof(float));
	memcpy(&movementSpeed, &buff[Offsets::ObjMoveSpeed],     sizeof(float));
	memcpy(&networkId,     &buff[Offsets::ObjNetworkID],     sizeof(DWORD));
	memcpy(&isTargetable,  &buff[Offsets::ObjTargetable],	 sizeof(bool));
	memcpy(&isInvulnerable,&buff[Offsets::ObjInvulnerable],  sizeof(bool));
	memcpy(&isDirection,   &buff[Offsets::ObjDirection], 	 sizeof(bool));
	memcpy(&isMoving,	   &buff[Offsets::ObjIsMoving], 	 sizeof(bool));
	memcpy(&atkRange,      &buff[Offsets::ObjAtkRange],		 sizeof(float));
	memcpy(&manaRegen, &buff[Offsets::ObjManaRegen], sizeof(float));
	memcpy(&healthRegen, &buff[Offsets::ObjHealthRegen], sizeof(float));
	memcpy(&isRecalling,   &buff[Offsets::ObjRecallState], sizeof(int));

	/* 
		AIManager removed! Make ur self.
	*/

	// Check if alive
	DWORD spawnCount;
	memcpy(&spawnCount, &buff[Offsets::ObjSpawnCount], sizeof(int));
	isAlive = (spawnCount % 2 == 0);

	if (deepLoad) {
		char nameBuff[50];
		Mem::Read(hProcess, Mem::ReadDWORDFromBuffer(buff, Offsets::ObjName), nameBuff, 50);

		if (Character::ContainsOnlyASCII(nameBuff, 50))
			name = Character::ToLower(std::string(nameBuff));
		else
			name = std::string("");
		unitInfo = GameData::GetUnitInfoByName(name);
	}
	// Don't use buffmanager for minions making lag idk ?
	if (HasUnitTags(Unit_Champion)) {
		LoadChampionFromMem(base, hProcess, deepLoad);
		LoadBuffFromMem(base, hProcess, deepLoad);
	}
	else if (unitInfo == GameData::UnknownUnit) {
		LoadMissileFromMem(base, hProcess, deepLoad);
	}
	else if (HasUnitTags(Unit_Monster)) {
		LoadBuffFromMem(base, hProcess, deepLoad);
	}
		/*else if (HasUnitTags(Unit_Minion_Lane)) {
			LoadBuffFromMem(base, hProcess, deepLoad);
		}*/
}

DWORD GameObject::spellSlotPointerBuffer[7] = {};
BYTE  GameObject::itemListBuffer[0x100] = {};

void GameObject::LoadChampionFromMem(DWORD base, HANDLE hProcess, bool deepLoad) {

	memcpy(&spellSlotPointerBuffer, &buff[Offsets::ObjSpellBook], sizeof(DWORD) * 6);

	Q.LoadFromMem(spellSlotPointerBuffer[0], hProcess);
	W.LoadFromMem(spellSlotPointerBuffer[1], hProcess);
	E.LoadFromMem(spellSlotPointerBuffer[2], hProcess);
	R.LoadFromMem(spellSlotPointerBuffer[3], hProcess);

	D.LoadFromMem(spellSlotPointerBuffer[4], hProcess);
	F.LoadFromMem(spellSlotPointerBuffer[5], hProcess);

	DWORD ptrList = Mem::ReadDWORD(hProcess, address + Offsets::ObjItemList);
	Mem::Read(hProcess, ptrList, itemListBuffer, 0x100);

	for (int i = 0; i < 7; ++i) {
		itemSlots[i].isEmpty = true;
		itemSlots[i].slot = i;

		DWORD itemPtr = 0, itemInfoPtr = 0;
		memcpy(&itemPtr, itemListBuffer + i * 0x10 + Offsets::ItemListItem, sizeof(DWORD));
		if (itemPtr == 0)
			continue;

		itemInfoPtr = Mem::ReadDWORD(hProcess, itemPtr + Offsets::ItemInfo);
		if (itemInfoPtr == 0)
			continue;
		
		int id = Mem::ReadDWORD(hProcess, itemInfoPtr + Offsets::ItemInfoId);
		itemSlots[i].isEmpty = false;
		itemSlots[i].stats = GameData::GetItemInfoById(id);
	}

	level = Mem::ReadDWORD(hProcess, base + Offsets::ObjLvl);
}

void GameObject::LoadBuffFromMem(DWORD base, HANDLE hProcess, bool deepLoad) {
	DWORD buffArrayBgn = Mem::ReadDWORD(hProcess, address + Offsets::ObjBuffManager + Offsets::BuffManagerEntriesArray);
	DWORD buffArrayEnd = Mem::ReadDWORD(hProcess, address + Offsets::ObjBuffManager + 0x14);
	int i = 0;
	buffVector.clear();
	buffVector.reserve(i);
	for (DWORD pBuffPtr = buffArrayBgn; pBuffPtr != buffArrayEnd; pBuffPtr += 0x8)
	{
		i++;
		DWORD buffInstance = Mem::ReadDWORD(hProcess, pBuffPtr);

		Mem::Read(hProcess, buffInstance, buff, sizeBuff);

		DWORD buffInfo = Mem::ReadDWORDFromBuffer(buff, 0x8);

		if (buffInfo == NULL || (DWORD)buffInfo <= 0x1000)
			continue;

		char buffnamebuffer[240];
		Mem::Read(hProcess, buffInfo + Offsets::BuffName, buffnamebuffer, 240);
		if (buffnamebuffer == NULL)
			continue;

		bool isAlive = false;
		float buffStartTime;
		float buffEndTime;
		int buffCount;
		int buffCountAlt;
		int buffCountAlt2;
		int bufftype;

		memcpy(&buffStartTime, &buff[Offsets::BuffEntryBuffStartTime], sizeof(float));
		memcpy(&buffEndTime, &buff[Offsets::BuffEntryBuffEndTime], sizeof(float));
		memcpy(&buffCount, &buff[Offsets::BuffEntryBuffCount], sizeof(int));
		memcpy(&buffCountAlt, &buff[Offsets::BuffEntryBuffCountAlt], sizeof(int));
		memcpy(&buffCountAlt2, &buff[Offsets::BuffEntryBuffCountAlt2], sizeof(int));
		memcpy(&bufftype, &buff[Offsets::BuffType], sizeof(int));

		buffCountAlt = buffCountAlt - buffCountAlt2 >> 3;

		if (buffCountAlt > 0)
			isAlive = true;
		buffVector.push_back(BuffInstance(buffnamebuffer, isAlive, buffCount, buffCountAlt, bufftype, buffStartTime, buffEndTime));
	}
}

float GameObject::GetBasicAttackDamage() {
	return baseAttack + bonusAttack;
}

Spell* GameObject::GetSummonerSpell(SummonerSpellType type) {
	if (D.summonerSpellType == type)
		return &D;
	if (F.summonerSpellType == type)
		return &F;
	return nullptr;
}

bool GameObject::IsRanged() {
	return GetBaseAttackRange() >= 300.f;
}

list GameObject::ItemsToPyList() {
	list l;
	for (int i = 0; i < 7; ++i){
		if (!itemSlots[i].isEmpty)
			l.append(boost::ref(itemSlots[i]));
	}
	return l;
}

list GameObject::BuffsToPyList() {
	list buffList;
	for (auto& buffs : buffVector)
	{
		if (buffs.isAlive)
			buffList.append(boost::ref(buffs));
	}
	return buffList;
}

// Missile stuff
void GameObject::LoadMissileFromMem(DWORD base, HANDLE hProcess, bool deepLoad) {

	if (!deepLoad)
		return;

	DWORD spellInfoPtr = Mem::ReadDWORDFromBuffer(buff, Offsets::MissileSpellInfo);
	if (spellInfoPtr == 0)
		return;

	DWORD spellDataPtr = Mem::ReadDWORD(hProcess, spellInfoPtr + Offsets::SpellInfoSpellData);
	if (spellDataPtr == 0)
		return;

	memcpy(&srcIndex,  buff + Offsets::MissileSrcIdx,   sizeof(short));
	memcpy(&destIndex, buff + Offsets::MissileDestIdx,  sizeof(short));
	memcpy(&startPos,  buff + Offsets::MissileStartPos, sizeof(Vector3));
	memcpy(&endPos,    buff + Offsets::MissileEndPos,   sizeof(Vector3));

	Mem::Read(hProcess, spellDataPtr, buff, 0x500);

	// Read name
	char nameBuff[50];
	Mem::Read(hProcess, Mem::ReadDWORD(hProcess, spellDataPtr + Offsets::SpellDataMissileName), nameBuff, 50);
	if (Character::ContainsOnlyASCII(nameBuff, 50))
		name = Character::ToLower(std::string(nameBuff));
	else
		name = std::string("");

	// Find static data
	spellInfo = GameData::GetSpellInfoByName(name);

	// Some spells require their end position to be projected using the range of the spell
	if (spellInfo != GameData::UnknownSpell && HasSpellFlags(ProjectedDestination)) {

		startPos.y += spellInfo->height;

		// Calculate direction vector and normalize
		endPos = Vector3(endPos.x - startPos.x, 0, endPos.z - startPos.z);
		endPos = endPos.normalize();

		// Update endposition using the height of the current position
		endPos.x = endPos.x*spellInfo->castRange + startPos.x;
		endPos.y = startPos.y;
		endPos.z = endPos.z*spellInfo->castRange + startPos.z;
	}
}

bool GameObject::EqualSpellFlags(SpellFlags flags) const
{
	return spellInfo->flags == flags;
}

bool GameObject::HasSpellFlags(SpellFlags flags) const
{
	return (spellInfo->flags & flags) == flags;
}

float GameObject::GetSpeed() const
{
	return spellInfo->speed;
}

float GameObject::GetCastRange() const
{
	return spellInfo->castRange;
}

float GameObject::GetWidth() const
{
	return spellInfo->width;
}

float GameObject::GetCastRadius() const
{
	return spellInfo->castRadius;
}

float GameObject::GetDelay() const
{
	return spellInfo->delay;
}

float GameObject::GetHeight() const
{
	return spellInfo->height;
}

float GameObject::GetTravelTime() const
{
	return spellInfo->travelTime;
}

std::string GameObject::GetIcon() const
{
	return spellInfo->icon;
}
