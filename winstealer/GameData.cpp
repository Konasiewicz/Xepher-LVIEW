#include "GameData.h"
#include <boost/json.hpp>
#include <fstream>
#include <filesystem>
#include "Utils.h"
#include "Overlay.h"

using namespace std;

UnitInfo*                         GameData::UnknownUnit  = new UnitInfo();
SpellInfo*                        GameData::UnknownSpell = new SpellInfo();
ItemInfo*                         GameData::UnknownItem  = new ItemInfo();
std::map<std::string, UnitInfo*>  GameData::Units        = {};
std::map<std::string, SpellInfo*> GameData::Spells       = {};
std::map<std::string, Texture2D*> GameData::Images       = {};
std::map<int, ItemInfo*>          GameData::Items        = {};

void GameData::Load(std::string& dataFolder)
{
	std::string unitData         = dataFolder + "/UnitData.json";
	std::string spellData        = dataFolder + "/SpellData.json";
	std::string spellDataCustom  = dataFolder + "/SpellDataCustom.json";
	std::string itemData         = dataFolder + "/ItemData.json";
	std::string spellIcons       = dataFolder + "/icons_spells";
	std::string champIcons       = dataFolder + "/icons_champs";
	std::string extraIcons       = dataFolder + "/icons_extra";

	LoadItemData(itemData);

	LoadUnitData(unitData);

	LoadSpellData(spellData);
	LoadSpellData(spellDataCustom);

	LoadIcons(spellIcons);
	LoadIcons(champIcons);
	LoadIcons(extraIcons);

	printf("\r	Load complete please wait                             \n");
}

UnitInfo * GameData::GetUnitInfoByName(std::string& name)
{
	auto it = Units.find(name);
	if (it != Units.end())
		return it->second;
	return UnknownUnit;
}

SpellInfo * GameData::GetSpellInfoByName(std::string& name)
{
	auto it = Spells.find(name);
	if (it != Spells.end())
		return it->second;
	return UnknownSpell;
}

ItemInfo * GameData::GetItemInfoById(int id)
{
	auto it = Items.find(id);
	if (it != Items.end())
		return it->second;
	return UnknownItem;
}

boost::json::value parse_json_file(std::string& path) {
	std::ifstream inputData;
	inputData.open(path);

	if (!inputData.is_open())
		throw std::runtime_error("Can't open unit data file");

	boost::json::stream_parser p;
	boost::json::error_code ec;
	do {
		char buf[4096];
		inputData.read(buf, sizeof(buf));
		p.write(buf, inputData.gcount(), ec);
	} while (!inputData.eof());
	if (ec)
		throw std::runtime_error("Failed to parse JSON file");
	p.finish(ec);
	if (ec)
		throw std::runtime_error("Failed to parse JSON file");

	boost::json::value jv = p.release();
	return jv;
}

double json_to_double(boost::json::value val) {
	if (val.is_int64())
		return val.as_int64();
	else
		return val.as_double();
}

void GameData::LoadUnitData(std::string&  path)
{
	boost::json::value jv = parse_json_file(path);
	auto& units = jv.get_array();
	for (auto& unit : units) {
		auto& unitObj = unit.get_object();

		UnitInfo* unit = new UnitInfo();
		unit->acquisitionRange         = (double)json_to_double(unitObj["acquisitionRange"]);
		unit->attackSpeedRatio         = (double)json_to_double(unitObj["attackSpeedRatio"]);
		unit->baseAttackRange          = (double)json_to_double(unitObj["attackRange"]);
		unit->baseAttackSpeed          = (double)json_to_double(unitObj["attackSpeed"]);
		unit->baseMovementSpeed        = (double)json_to_double(unitObj["baseMoveSpeed"]);
		unit->basicAttackMissileSpeed  = (double)json_to_double(unitObj["basicAtkMissileSpeed"]);
		unit->basicAttackWindup        = (double)json_to_double(unitObj["basicAtkWindup"]);
		unit->gameplayRadius           = (double)json_to_double(unitObj["gameplayRadius"]);
		unit->healthBarHeight          = (double)json_to_double(unitObj["healthBarHeight"]);
		unit->name                     = Character::ToLower(std::string(unitObj["name"].as_string().c_str()));
		unit->pathRadius               = (double)json_to_double(unitObj["pathingRadius"]);
		unit->selectionRadius          = (double)json_to_double(unitObj["selectionRadius"]);

		auto& tags = unitObj["tags"].as_array();
		for (auto& tag : tags)
			unit->SetTag(tag.as_string().c_str());

		Units[unit->name] = unit;
	}
}

void GameData::LoadSpellData(std::string& path)
{
	boost::json::value jv = parse_json_file(path);
	auto& spells = jv.as_array();

	for (auto& spell : spells) {
		auto& spellObj = spell.as_object();

		SpellInfo* info = new SpellInfo();
		info->flags      = (SpellFlags)spellObj["flags"].as_int64();
		info->delay      = (double)json_to_double(spellObj["delay"]);
		info->height     = (double)json_to_double(spellObj["height"]);
		info->icon       = Character::ToLower(std::string(spellObj["icon"].as_string().c_str()));
		info->name       = Character::ToLower(std::string(spellObj["name"].as_string().c_str()));
		info->width      = (double)json_to_double(spellObj["width"]);
		info->castRange  = (double)json_to_double(spellObj["castRange"]);
		info->castRadius = (double)json_to_double(spellObj["castRadius"]);
		info->speed      = (double)json_to_double(spellObj["speed"]);
		info->travelTime = (double)json_to_double(spellObj["travelTime"]);
		info->flags      = (SpellFlags) (info->flags | (spellObj["projectDestination"].as_bool() ? ProjectedDestination : 0));

		Spells[info->name] = info;
	}
}

void GameData::LoadIcons(std::string& path)
{
	std::string folder(path);
	WIN32_FIND_DATAA findData;
	HANDLE hFind;

	
	int nrFiles = std::distance(filesystem::directory_iterator(path), filesystem::directory_iterator());
	int nrFile = 0;
	hFind = FindFirstFileA((folder + "\\*.png").c_str(), &findData);
	do {
		if (hFind != INVALID_HANDLE_VALUE) {
			if(nrFile % 100 == 0)
				printf("\r	Library loading %d/%d      ", nrFile, nrFiles);

			std::string filePath = folder + "/" + findData.cFileName;
			Texture2D* image = Texture2D::LoadFromFile(Overlay::GetDxDevice(), filePath);
			if (image == nullptr)
				printf("	Failed to load: %s\n", filePath.c_str());
			else {
				std::string fileName(findData.cFileName);
				fileName.erase(fileName.find(".png"), 4);
				Images[Character::ToLower(fileName)] = image;
			}
		}
		nrFile++;
	} while (FindNextFileA(hFind, &findData));
}

void GameData::LoadItemData(std::string & path)
{
	boost::json::value jv = parse_json_file(path);
	auto& items = jv.as_array();
	for (auto& itemObj : items) {
		auto& item = itemObj.as_object();
		ItemInfo* info = new ItemInfo();

		info->movementSpeed        = (double)json_to_double(item["movementSpeed"]);
		info->health               = (double)json_to_double(item["health"]);
		info->crit                 = (double)json_to_double(item["crit"]);
		info->abilityPower         = (double)json_to_double(item["abilityPower"]);
		info->mana                 = (double)json_to_double(item["mana"]);
		info->armour               = (double)json_to_double(item["armour"]);
		info->magicResist          = (double)json_to_double(item["magicResist"]);
		info->physicalDamage       = (double)json_to_double(item["physicalDamage"]);
		info->attackSpeed          = (double)json_to_double(item["attackSpeed"]);
		info->lifeSteal            = (double)json_to_double(item["lifeSteal"]);
		info->hpRegen              = (double)json_to_double(item["hpRegen"]);
		info->movementSpeedPercent = (double)json_to_double(item["movementSpeedPercent"]);
		info->cost                 = (double)json_to_double(item["cost"]);
		info->id                   = item["id"].as_int64();

		Items[info->id] = info;
	}
}
