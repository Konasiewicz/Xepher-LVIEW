from winstealer import *
from commons.ByLib import *
from commons.utils import *
import math, itertools, time, json, requests
from . import items
from enum import Enum
from . import utils
from re import search
from commons.damage_calculator import DamageSpecification, DamageType
from API.summoner import *

damageCalc = DamageSpecification()
damageType = DamageType(1)

Version = "sdfjsdkfsd"
MissileToSpell = {}
SpellsToEvade = {}
Spells = {}
ChampionSpells = {}


def VectorPointProjectionOnLineSegment(v1, v2, v):
    cx, cy, ax, ay, bx, by = v.x, v.z, v1.x, v1.z, v2.x, v2.z
    rL = ((cx - ax) * (bx - ax) + (cy - ay) * (by - ay)) / (
        math.pow((bx - ax), 2) + math.pow((by - ay), 2)
    )
    pointLine = Vec3(ax + rL * (bx - ax), 0, ay + rL * (by - ay))
    rS = rL < 0 and 0 or (rL > 1 and 1 or rL)
    isOnSegment = rS == rL
    pointSegment = (
        isOnSegment and pointLine or Vec3(ax + rS * (bx - ax), 0, ay + rS * (by - ay))
    )
    return pointSegment, pointLine, isOnSegment


class HitChance(Enum):
    Immobile = 8
    Dashing = 7
    VeryHigh = 6
    High = 5
    Medium = 4
    Low = 3
    Impossible = 2
    OutOfRange = 1
    Collision = 0


_HitChance = HitChance.Impossible


class SFlag:
    Targeted = 1
    Line = 2
    Cone = 4
    Area = 8

    CollideWindwall = 16
    CollideChampion = 32
    CollideMob = 64

    CollideGeneric = CollideMob | CollideChampion | CollideWindwall
    SkillshotLine = CollideGeneric | Line


class DangerLevels:
    Easy = 1
    Fastes = 2
    UseSpell = 3
    VeryDangerous = 4


class Spell:
    def __init__(
        self, name, missile_names, flags, delay=0.0, danger=DangerLevels.Fastes
    ):
        global MissileToSpell, Spells

        self.flags = flags
        self.name = name
        self.missiles = missile_names
        self.delay = delay
        self.danger = danger
        Spells[name] = self
        for missile in missile_names:
            if len(missile) < 1:
                MissileToSpell[name] = self
            MissileToSpell[missile] = self

    delay = 0.0
    danger = DangerLevels.Fastes
    flags = 0
    name = "?"
    missiles = []
    skills = []


ChampionSpells = {
    "aatrox": [
        Spell("aatroxw", ["aatroxw"], SFlag.SkillshotLine),
        Spell("aatroxq", ["aatroxq1"], SFlag.SkillshotLine),
        Spell("aatroxq2", ["aatroxq2"], SFlag.SkillshotLine),
        Spell("aatroxq3", ["aatroxq3"], SFlag.SkillshotLine),
    ],
    "rell": [Spell("rellq", ["rellq_vfxmis"], SFlag.SkillshotLine)],
    "twistedfate": [Spell("wildcards", ["sealfatemissile"], SFlag.SkillshotLine)],
    "zoe": [
        Spell("zoeqmissile", ["zoeqmissile"], SFlag.SkillshotLine),
        Spell("zoeqmis2", ["zoeqmis2"], SFlag.SkillshotLine),
        Spell("zoee", ["zoeemis"], SFlag.SkillshotLine),
        Spell("zoeebubble", ["zoeec"], SFlag.Area),
    ],
    "ornn": [
        Spell("ornnq", ["ornnqmissile", "ornnq"], SFlag.SkillshotLine),
        Spell("ornnrwave2", ["ornnrwave2"], SFlag.Line),
        Spell("ornnrwave", ["ornnrwave"], SFlag.Line),
    ],
    "kassadin": [
        Spell("riftwalk", ["riftwalk"], SFlag.Area),
        Spell("forcepulse", [], SFlag.Cone),
    ],
    "katarina": [
        Spell("katarinaw", ["katarinadaggerarc"], SFlag.Area),
    ],
    "quinn": [Spell("quinnq", ["quinnq"], SFlag.CollideGeneric)],
    "aurelionsol": [
        Spell("aurelionsolq", ["aurelionsolqmissile"], SFlag.SkillshotLine),
        Spell("aurelionsolr", ["aurelionsolrbeammissile"], SFlag.SkillshotLine),
    ],
    "ahri": [
        Spell("ahriorbofdeception", ["ahriorbmissile"], SFlag.SkillshotLine),
        Spell("ahriseduce", ["ahriseducemissile"], SFlag.SkillshotLine),
    ],
    "ashe": [
        Spell(
            "enchantedcrystalarrow",
            ["enchantedcrystalarrow"],
            SFlag.SkillshotLine,
        ),
        Spell("volleyrank1", [], SFlag.SkillshotLine),
        Spell("volleyrank2", [], SFlag.SkillshotLine),
        Spell("volleyrank3", [], SFlag.SkillshotLine),
        Spell("volleyrank4", [], SFlag.SkillshotLine),
        Spell("volleyrank5", [], SFlag.SkillshotLine),
    ],
    "shen": [Spell("shene", ["shene"], SFlag.Line)],
    "elise": [Spell("elisehumane", ["elisehumane"], SFlag.SkillshotLine)],
    "sylas": [
        Spell("sylase2", ["sylase2"], SFlag.SkillshotLine),
        Spell("sylasq", [], SFlag.Area),
        Spell("sylasqline", [], SFlag.Line),
    ],
    "camille": [Spell("camillee", ["camilleemissile"], SFlag.SkillshotLine)],
    "kennen": [
        Spell(
            "kennenshurikenhurlmissile1",
            ["kennenshurikenhurlmissile1"],
            SFlag.SkillshotLine,
        )
    ],
    "darius": [
        Spell("dariuscleave", [], SFlag.Area),
        Spell("dariusaxegrabcone", ["dariusaxegrabcone"], SFlag.Cone),
    ],
    "brand": [
        Spell("brandq", ["brandqmissile"], SFlag.SkillshotLine),
    ],
    "pyke": [
        Spell("pykeqrange", ["pykeqrange", "pykeq"], SFlag.Line),
        Spell("pykee", ["pykeemissile"], SFlag.Line)
    ],
    "amumu": [
        Spell(
            "bandagetoss", ["sadmummybandagetoss"], SFlag.Line | SFlag.CollideWindwall
        )
    ],
    "caitlyn": [
        Spell(
            "caitlynpiltoverpeacemaker",
            ["caitlynpiltoverpeacemaker", "caitlynpiltoverpeacemaker2"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("caitlynyordletrap", [], SFlag.Area),
        Spell("caitlynentrapment", ["caitlynentrapmentmissile"], SFlag.SkillshotLine),
    ],
    "chogath": [
        Spell("rupture", ["rupture"], SFlag.Area),
        Spell("feralscream", ["feralscream"], SFlag.Cone | SFlag.CollideWindwall),
    ],
    "drmundo": [
        Spell(
            "infectedcleavermissilecast",
            ["infectedcleavermissile"],
            SFlag.SkillshotLine,
        )
    ],
    "bard": [
        Spell("bardq", ["bardqmissile"], SFlag.SkillshotLine),
        Spell("bardr", ["bardrmissile"], SFlag.Area),
    ],
    "diana": [
        Spell(
            "dianaq",
            ["dianaqinnermissile", "dianaqoutermissile", "dianaq"],
            SFlag.Cone | SFlag.Area,
        ),
        Spell("dianaarcarc", ["dianaarcarc"], SFlag.Cone | SFlag.Area),
    ],
    "qiyana": [
        Spell(
            "qiyanaq_rock",
            ["qiyanaq_rock"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell(
            "qiyanaq_grass",
            ["qiyanaq_grass"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell(
            "qiyanaq_water",
            ["qiyanaq_water"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell("qiyanar", ["qiyanarmis"], SFlag.Cone, 0.25, DangerLevels.UseSpell),
        Spell(
            "dianaarcarc",
            ["dianaarcarc"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
    ],
    "ekko": [
        Spell("ekkoq", ["ekkoqmis"], SFlag.Line | SFlag.Area, 0.0, DangerLevels.Easy),
        Spell("ekkow", ["ekkowmis"], SFlag.Area, 0.0, DangerLevels.Fastes),
        Spell("ekkor", ["ekkor"], SFlag.Area, 0.0, DangerLevels.UseSpell),
    ],
    "kogmaw": [
        Spell("kogmawq", ["kogmawq"], SFlag.SkillshotLine),
        Spell("kogmawvoidooze", ["kogmawvoidoozemissile"], SFlag.SkillshotLine),
        Spell("kogmawlivingartillery", ["kogmawlivingartillery"], SFlag.Area),
    ],
    "fizz": [
        Spell(
            "fizzr", ["fizzrmissile"], SFlag.SkillshotLine, 0.0, DangerLevels.UseSpell
        )
    ],
    "vi": [
        Spell("vi-q", ["viqmissile"], SFlag.Line),
        Spell("viq", ["viqmissile"], SFlag.Line),
    ],
    "viktor": [
        Spell("viktorgravitonfield", ["viktordeathraymissile"], SFlag.SkillshotLine)
    ],
    "irelia": [
        Spell("ireliaeparticle", ["ireliaeparticlemissile"], SFlag.Line),
        Spell("ireliaw2", ["ireliaw2"], SFlag.SkillshotLine),
        Spell("ireliar", ["ireliar"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell),
    ],
    "katarina": [Spell("katarinae", [], SFlag.Targeted)],
    "illaoi": [
        Spell("illaoiq", [], SFlag.Line),
        Spell("illaoie", ["illaoiemis"], SFlag.SkillshotLine),
    ],
    "heimerdinger": [
        Spell(
            "heimerdingerwm",
            ["heimerdingerwattack2", "heimerdingerwattack2ult"],
            SFlag.SkillshotLine,
        ),
        Spell("heimerdingere", ["heimerdingerespell"], SFlag.Area),
    ],
    "jarvaniv": [
        Spell("jarvanivdemacianstandard", [], SFlag.Area),
        Spell("jarvanivdragonstrike", [], SFlag.SkillshotLine),
        Spell(
            "jarvanivqe", [], SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall
        ),
    ],
    "janna": [
        Spell("jannaq", ["howlinggalespell"], SFlag.SkillshotLine),
        Spell("howlinggalespell", ["howlinggalespell"], SFlag.SkillshotLine),
    ],
    "jayce": [
        Spell("jayceshockblast", ["jayceshockblastmis"], SFlag.SkillshotLine),
        Spell("jayceqaccel", ["jayceshockblastwallmis"], SFlag.SkillshotLine),
    ],
    "khazix": [
        Spell("khazixw", ["khazixwmissile"], SFlag.SkillshotLine),
        Spell("khazixwlong", ["khazixwmissile"], SFlag.SkillshotLine),
        Spell("khazixe", ["khazixe"], SFlag.Area),
    ],
    "ezreal": [
        Spell("ezrealq", ["ezrealq"], SFlag.SkillshotLine),
        Spell("ezrealw", ["ezrealw"], SFlag.SkillshotLine),
        Spell("ezrealr", ["ezrealr"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell),
    ],
    "kalista": [
        Spell(
            "kalistamysticshot",
            ["kalistamysticshotmis", "kalistamysticshotmistrue"],
            SFlag.SkillshotLine,
        ),
    ],
    "alistar": [
        Spell("pulverize", ["koco_missile"], SFlag.Area),
    ],
    "lissandra": [
        Spell("lissandraq", ["lissandraqmissile"], SFlag.SkillshotLine),
        Spell("lissandraqshards", ["lissandraqshards"], SFlag.SkillshotLine),
        Spell("lissandrae", ["lissandraemissile"], SFlag.SkillshotLine),
    ],
    "galio": [
        Spell("galioq", ["galioqmissile"], SFlag.Area),
        Spell("galioe", [], SFlag.SkillshotLine),
    ],
    "evelynn": [
        Spell("evelynnq", ["evelynnq"], SFlag.SkillshotLine),
        Spell("evelynnr", ["evelynnr"], SFlag.Cone),
    ],
    "graves": [
        Spell(
            "gravesqlinespell",
            ["gravesqlinemis", "gravesqreturn"],
            SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall,
        ),
        Spell(
            "gravessmokegrenade",
            ["gravessmokegrenadeboom"],
            SFlag.Area | SFlag.CollideWindwall,
        ),
        Spell(
            "graveschargeshot",
            ["graveschargeshotshot"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("graveschargeshotfxmissile2", ["graveschargeshotfxmissile2"], SFlag.Cone),
    ],
    "leesin": [Spell("blindmonkqone", ["blindmonkqone"], SFlag.SkillshotLine)],
    "leona": [
        Spell(
            "leonazenithblade",
            ["leonazenithblademissile"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell("leonasolarflare", ["leonasolarflare"], SFlag.Area),
    ],
    "leblanc": [
        Spell("leblancslide", ["leblancslide"], SFlag.Area),
        Spell("leblancr", ["leblancslidem"], SFlag.Area),
        Spell("leblance", ["leblancemissile"], SFlag.SkillshotLine),
        Spell("leblancre", ["leblancremissile"], SFlag.SkillshotLine),
        Spell("leblancsoulshacklem", ["leblancsoulshacklem"], SFlag.SkillshotLine),
    ],
    "lucian": [
        Spell("lucianq", ["lucianqmis"], SFlag.SkillshotLine, 0.4, DangerLevels.Fastes),
        Spell("lucianw", ["lucianwmissile"], SFlag.SkillshotLine),
        Spell("lucianrmis", ["lucianrmissile", "lucianrmissileoffhand"], SFlag.SkillshotLine),
    ],
    "gragas": [
        Spell("gragasq", ["gragasqmissile"], SFlag.Area),
        Spell("gragasr", ["gragasrboom"], SFlag.Area, 0, DangerLevels.UseSpell),
    ],
    "kled": [
        Spell("kledq", ["kledqmissile"], SFlag.Line),
        Spell("kledriderq", ["kledriderqmissile"], SFlag.Cone),
    ],
    "tristana": [Spell("tristanaw", ["rocketjump"], SFlag.Area)],
    "rengar": [
        Spell("rengare", ["rengaremis"], SFlag.SkillshotLine),
        Spell("rengareemp", ["rengareempmis"], SFlag.SkillshotLine),
    ],
    "ryze": [Spell("ryzeq", ["ryzeq"], SFlag.SkillshotLine)],
    "blitzcrank": [
        Spell(
            "rocketgrab",
            ["rocketgrabmissile"],
            SFlag.SkillshotLine,
            0.0,
            DangerLevels.Fastes,
        ),
    ],
    "corki": [
        Spell("phosphorusbomb", ["phosphorusbombmissile"], SFlag.Area),
        Spell("missilebarrage", ["missilebarragemissile"], SFlag.SkillshotLine),
        Spell("missilebarrage2", ["missilebarragemissile2"], SFlag.SkillshotLine),
    ],
    "varus": [
        Spell("varusq", ["varusqmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("varuse", ["varusemissile"], SFlag.Area),
        Spell("varusr", ["varusrmissile"], SFlag.Line, 0, DangerLevels.UseSpell),
    ],
    "tryndamere": [Spell("slashcast", ["slashcast"], SFlag.SkillshotLine)],
    "twitch": [
        Spell("twitchvenomcask", ["twitchvenomcaskmissile"], SFlag.Area),
        Spell("twitchsprayandprayattack", ["twitchsprayandprayattack"], SFlag.Line)
    ],
    "nocturne": [Spell("nocturneduskbringer", ["nocturneduskbringer"], SFlag.Line)],
    "velkoz": [
        Spell("velkozqmissilesplit", ["velkozqmissilesplit"], SFlag.SkillshotLine),
        Spell("velkozq", ["velkozqmissile"], SFlag.SkillshotLine),
        Spell(
            "velkozqsplitactivate",
            ["velkozqmissilesplit"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("velkozw", ["velkozwmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("velkoze", ["velkozemissile"], SFlag.Area),
    ],
    "lux": [
        Spell(
            "luxlightbinding",
            ["luxlightbindingmis", "luxlightbindingdummy"],
            SFlag.SkillshotLine,
        ),
        Spell("luxlightstrikekugel", ["luxlightstrikekugel"], SFlag.Area),
        Spell("luxmalicecannon", ["luxmalicecannon"], SFlag.Line),
    ],
    "nautilus": [
        Spell(
            "nautilusanchordragmissile",
            ["nautilusanchordragmissile"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes | DangerLevels.UseSpell,
        )
    ],
    "malzahar": [Spell("malzaharq", ["malzaharq"], SFlag.SkillshotLine)],
    "skarner": [
        Spell("skarnerfracturemissile", ["skarnerfracturemissile"], SFlag.SkillshotLine)
    ],
    "karthus": [Spell("karthuslaywastea1", [], SFlag.Area)],
    "sejuani": [Spell("sejuanir", ["sejuanirmissile"], SFlag.SkillshotLine)],
    "talon": [
        Spell("talonw", ["talonwmissileone"], SFlag.Line),
        Spell("talonwtwo", ["talonwmissiletwo"], SFlag.Line),
        Spell("talonrakereturn", ["talonwmissiletwo"], SFlag.Line),
    ],
    "ziggs": [
        Spell("ziggsq", ["ziggsqspell", "ziggsqspell2", "ziggsqspell3"], SFlag.Area),
        Spell("ziggsw", ["ziggsw"], SFlag.Area),
        Spell("ziggse", ["ziggse2"], SFlag.Area),
        Spell(
            "ziggsr",
            ["ziggsrboom", "ziggsrboommedium", "ziggsrboomlong", "ziggsrboomextralong"],
            SFlag.Area,
        ),
    ],
    "jhin": [
        Spell("jhinw", ["jhinwmissile"], SFlag.Line),
        Spell("jhine", ["jhinetrap"], SFlag.Area),
        Spell("jhinrshot", ["jhinrshotmis4", "jhinrshotmis"], SFlag.SkillshotLine),
    ],
    "swain": [
        Spell("swainw", ["swainw"], SFlag.Area | SFlag.CollideWindwall),
        Spell(
            "swainshadowgrasp", ["swainshadowgrasp"], SFlag.Area | SFlag.CollideWindwall
        ),
        Spell("swaine", ["swaine"], SFlag.SkillshotLine),
        Spell("swainereturn", ["swainereturnmissile"], SFlag.SkillshotLine),
    ],
    "nasus": [Spell("nasuse", [], SFlag.Area)],
    "nami": [
        Spell("namiq", ["namiqmissile"], SFlag.Area),
        Spell("namir", ["namirmissile"], SFlag.Line | SFlag.CollideWindwall),
    ],
    "nidalee": [
        Spell("javelintoss", ["javelintoss"], SFlag.SkillshotLine),
        Spell("bushwhack", [], SFlag.Area),
    ],
    "malphite": [Spell("ufslash", ["ufslash"], SFlag.SkillshotLine)],
    "reksai": [Spell("reksaiqburrowed", ["reksaiqburrowedmis"], SFlag.SkillshotLine)],
    "thresh": [
        Spell("threshq", ["threshqmissile"], SFlag.SkillshotLine),
        Spell("thresheflay", ["threshemissile1"], SFlag.SkillshotLine),
    ],
    "morgana": [
        Spell("morganaq", ["morganaq"], SFlag.SkillshotLine),
        Spell("morganaw", [], SFlag.Area),
    ],
    "mordekaiser": [
        Spell("mordekaiserq", [], SFlag.SkillshotLine),
        Spell("mordekaisere", ["mordekaiseremissile"], SFlag.SkillshotLine),
    ],
    "samira": [
        Spell("samiraqgun", ["samiraqgun"], SFlag.SkillshotLine),
    ],
    "pantheon": [
        Spell("pantheonq", ["pantheonqmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("pantheonr", ["pantheonrmissile"], SFlag.Line),
    ],
    "annie": [
        Spell("anniew", [], SFlag.Cone | SFlag.CollideWindwall),
        Spell("annier", [], SFlag.Area),
    ],
    "hecarim": [
        Spell(
            "hecarimult",
            ["hecarimultmissile"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
        Spell("hecarimrcircle", [], SFlag.Area),
    ],
    "olaf": [
        Spell("olafaxethrowcast", ["olafaxethrow"], SFlag.Line | SFlag.CollideWindwall)
    ],
    "anivia": [
        Spell("flashfrost", ["flashfrostspell"], SFlag.Line | SFlag.CollideWindwall)
    ],
    "zed": [
        Spell("zedq", ["zedqmissile"], SFlag.Line),
        Spell("zedw", ["zedwmissile"], SFlag.Area),
    ],
    "xerath": [
        Spell("xeratharcanopulse", ["xeratharcanopulse"], SFlag.Area),
        Spell("xeratharcanopulsechargup", ["xeratharcanopulsechargup"], SFlag.Area),
        Spell("xeratharcanebarrage2", ["xeratharcanebarrage2"], SFlag.Area),
        Spell(
            "xerathmagespear",
            ["xerathmagespearmissile"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("xerathr", ["xerathlocuspulse"], SFlag.Area),
    ],
    "urgot": [
        Spell("urgotq", ["urgotqmissile"], SFlag.Area),
        Spell("urgotr", ["urgotr"], SFlag.Line),
    ],
    "poppy": [
        Spell("poppyq", ["poppyq"], SFlag.SkillshotLine | SFlag.CollideWindwall),
        Spell(
            "poppyrspell",
            ["poppyrmissile"],
            SFlag.SkillshotLine | SFlag.CollideWindwall,
            0,
            DangerLevels.VeryDangerous,
        ),
        Spell(
            "poppyrlong",
            ["poppyrmissile"],
            SFlag.SkillshotLine | SFlag.CollideWindwall,
            0,
            DangerLevels.VeryDangerous,
        ),
    ],
    "gnar": [
        Spell("gnarq", ["gnarqmissile"], SFlag.SkillshotLine),
        Spell("gnarqreturn", ["gnarqmissilereturn"], SFlag.SkillshotLine),
        Spell("gnarbigq", ["gnarbigqmissile"], SFlag.SkillshotLine),
        Spell("gnarbigw", ["gnarbigw"], SFlag.SkillshotLine),
        Spell("gnare", ["gnare"], SFlag.Area),
        Spell("gnarbige", ["gnarbige"], SFlag.Area),
        Spell("gnarr", ["gnarr"], SFlag.Area),
    ],
    "senna": [
        Spell("sennaqcast", ["sennaqcast"], SFlag.SkillshotLine),
        Spell("sennaw", ["sennaw"], SFlag.SkillshotLine),
        Spell("sennar", ["sennarwarningmis"], SFlag.Line),
    ],
    "shyvana": [
        Spell("shyvanafireball", ["shyvanafireballmissile"], SFlag.SkillshotLine),
        Spell(
            "shyvanafireballdragon2",
            ["shyvanafireballdragonmissile"],
            SFlag.SkillshotLine,
        ),
    ],
    "singed": [Spell("megaadhesive", ["singedwparticlemissile"], SFlag.Area)],
    "fiora": [Spell("fioraw", ["fiorawmissile"], SFlag.SkillshotLine)],
    "sivir": [
        Spell("sivirq", ["sivirqmissile"], SFlag.SkillshotLine),
        Spell("sivirqreturn", ["sivirqmissilereturn"], SFlag.SkillshotLine)
    ],
    "kaisa": [Spell("kaisaw", ["kaisaw"], SFlag.Line | SFlag.CollideWindwall)],
    "karma": [
        Spell(
            "karmaq",
            ["karmaqmissile", "karmaqmissilemantra"],
            SFlag.SkillshotLine | SFlag.Area,
        ),
        Spell("karmaqmantracircle", [], SFlag.SkillshotLine | SFlag.Area),
    ],
    "braum": [
        Spell("braumq", ["braumqmissile"], SFlag.SkillshotLine),
        Spell(
            "braumrwrapper",
            ["braumrmissile"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
    ],
    "soraka": [
        Spell("sorakaq", ["sorakaqmissile"], SFlag.Area),
        Spell("sorakae", ["sorakaemissile"], SFlag.Area),
    ],
    "rakan": [
        Spell("rakanq", ["rakanqmis"], SFlag.SkillshotLine),
        Spell("rakanw", [], SFlag.Area, delay=0.5),
    ],
    "xayah": [
        Spell(
            "xayahq",
            ["xayahq", "xayahqmissile1", "xayahqmissile2"],
            SFlag.Line,
        ),
        Spell(
            "xayahq1",
            ["xayahqmissile1"],
            SFlag.Line,
        ),
        Spell(
            "xayahq2",
            ["xayahqmissile2"],
            SFlag.Line,
        ),
        Spell(
            "xayahe",
            ["xayahemissile"],
            SFlag.Line,
        ),
        Spell(
            "xayahr",
            ["xayahrmissile"],
            SFlag.Line,
        )
    ],
    "sona": [Spell("sonar", ["sonar"], SFlag.Line | SFlag.CollideWindwall)],
    "akali": [Spell("akalie", ["akaliemis"], SFlag.Line | SFlag.CollideWindwall)],
    "kayle": [Spell("kayleq", ["kayleqmis"], SFlag.SkillshotLine)],
    "taliyah": [
        Spell("taliyahqmis", ["taliyahqmis"], SFlag.SkillshotLine),
        Spell("taliyahr", ["taliyahrmis"], SFlag.SkillshotLine),
    ],
    "yasuo": [
        Spell("yasuoq1wrapper", [], SFlag.SkillshotLine),
        Spell("yasuoq2wrapper", [], SFlag.SkillshotLine),
        Spell("yasuoq3wrapper", ["yasuoq3mis"], SFlag.SkillshotLine),
        Spell("yasuoq3", ["yasuoq3mis"], SFlag.SkillshotLine),
    ],
    "yone": [
        Spell("yoneq3", ["yoneq3missile"], SFlag.SkillshotLine),
    ],
    "yuumi": [Spell("yuumiq", [], SFlag.Cone)],
    "zac": [
        Spell("zacq", ["zacqmissile"], SFlag.SkillshotLine),
        Spell("zace", [], SFlag.Area),
    ],
    "zyra": [
        Spell("zyraq", ["zyraq"], SFlag.Cone),
        Spell("zyraw", ["zyraw"], SFlag.Area),
        Spell("zyrae", ["zyrae"], SFlag.SkillshotLine),
        Spell(
            "zyrapassivedeathmanager", ["zyrapassivedeathmanager"], SFlag.SkillshotLine
        ),
    ],
    "zilean": [
        Spell("zileanq", ["zileanqmissile"], SFlag.Area | SFlag.CollideWindwall)
    ],
    "veigar": [Spell("veigarbalefulstrike", ["veigarbalefulstrikemis"], SFlag.Line)],
    "maokai": [Spell("maokaiq", ["maokaiqmissile"], SFlag.SkillshotLine)],
    "orianna": [
        Spell(
            "orianaizunacommand",
            ["orianaizuna"],
            SFlag.Line | SFlag.Area | SFlag.CollideWindwall,
        )
    ],
    "warwick": [
        Spell("warwickr", [], SFlag.Area | SFlag.CollideChampion),
        Spell("warwickrchannel", [], SFlag.Area | SFlag.CollideChampion),
    ],
    "taric": [Spell("tarice", ["tarice"], SFlag.SkillshotLine)],
    "cassiopeia": [
        Spell("cassiopeiar", ["cassiopeiar"], SFlag.Cone),
        Spell("cassiopeiaq", ["cassiopeiaq"], SFlag.Area),
    ],
    "viego": [
        Spell("viegoq", [], SFlag.Line | SFlag.CollideWindwall),
        Spell("viegowcast", ["viegowmis"], SFlag.Line | SFlag.CollideWindwall),
        Spell("viegorr", [], SFlag.Area),
    ],
    "syndra": [
        Spell("syndraqspell", ["syndraqspell"], SFlag.Area),
        Spell("syndraespheremissile", ["syndraespheremissile"], SFlag.Line),
    ],
    "draven": [
        Spell("dravendoubleshot", ["dravendoubleshotmissile"], SFlag.SkillshotLine),
        Spell("dravenrcast", ["dravenr"], SFlag.SkillshotLine),
    ],
    "sion": [
        Spell("sione", ["sionemissile"], SFlag.SkillshotLine),
    ],
    "kayn": [
        Spell("kaynq", [], SFlag.CollideWindwall),
        Spell("kaynw", ["kaynw_1234"], SFlag.SkillshotLine),
        Spell("kaynassw", [], SFlag.SkillshotLine),
    ],
    "jinx": [
        Spell("jinxw", [], SFlag.SkillshotLine),
        Spell("jinxwmissile", ["jinxwmissile"], SFlag.SkillshotLine),
        Spell("jinxe", ["jinxehit"], SFlag.Line),
        Spell("jinxr", ["jinxr"], SFlag.SkillshotLine),
    ],
    "seraphine": [
        Spell("seraphineqcast", ["seraphineqinitialmissile"], SFlag.Area),
        Spell("seraphineecast", ["seraphineemissile"], SFlag.SkillshotLine),
        Spell("seraphiner", ["seraphiner"], SFlag.SkillshotLine),
    ],
    "lulu": [
        Spell("luluq", ["luluqmissile"], SFlag.SkillshotLine),
        Spell("luluqpix", ["luluqmissiletwo"], SFlag.SkillshotLine),
    ],
    "rumble": [
        Spell("rumblegrenade", ["rumblegrenademissile"], SFlag.SkillshotLine),
    ],
    "aphelios": [
        Spell("aphelioscalibrumq", ["aphelioscalibrumq"], SFlag.SkillshotLine),
        Spell(
            "apheliosr", ["apheliosrmis"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell
        ),
    ],
    "neeko": [
        Spell("neekoq", ["neekoq"], SFlag.Area),
        Spell("neekoe", ["neekoe"], SFlag.Line | SFlag.CollideWindwall),
    ],
    "allchampions": [
        Spell(
            "arcanecomet",
            ["perks_arcanecomet_mis", "perks_arcanecomet_mis_arc"],
            SFlag.Area,
        )
    ],
    "lillia": [
        Spell("lilliaw", [], SFlag.Area | SFlag.CollideWindwall),
        Spell("lilliae", ["lilliae"], SFlag.SkillshotLine),
        Spell("lilliae2", ["lilliaerollingmissile"], SFlag.SkillshotLine),
    ],
    "tahmkench": [Spell("tahmkenchq", ["tahmkenchqmissile"], SFlag.SkillshotLine)],
    "sett": [
        Spell("settw", ["settw"], SFlag.Cone),
        Spell("sette", [], SFlag.SkillshotLine),
    ],
    "azir": [
        Spell("azirsoldier", ["azirsoldiermissile"], SFlag.Line),
    ],
    "riven": [
        Spell("rivenizunablade", ["rivenwindslashmissileleft", "rivenwindslashmissileright", "rivenwindslashmissilecenter"], SFlag.Line),
    ],
    "yuumi": [
        Spell("yuumiq", ["yuumiqskillshot"], SFlag.Line),
        Spell("yuumiqcast", ["yuumiqcast"], SFlag.Line),
    ],
}


def to_lower(dictionary):
    def try_iterate(k):
        return lower_by_level(k) if isinstance(k, dict) else k

    def try_lower(k):
        return k.lower() if isinstance(k, str) else k

    def lower_by_level(data):
        return dict((try_lower(k), try_iterate(v)) for k, v in data.items())

    return lower_by_level(dictionary)


def get_range(game, skill_name, slot):
    spelldb_range = 0
    with open("SpellDB.json", "r") as read_file:
        champ = json.loads(read_file.read())
        convertedSkillShot = {
            k.lower()
            if isinstance(k, str)
            else k: v.lower()
            if isinstance(v, str)
            else v
            for k, v in champ[game.player.name.capitalize()][slot].items()
        }
        if convertedSkillShot["name"] == skill_name:
            spelldb_range = convertedSkillShot["rangeburn"]

    return spelldb_range


def get_skillshot_range(game, skill_name, slot):
    global Spells

    if skill_name not in Spells:
        raise Exception("Not a skillshot")

    skillshot = Spells[skill_name]
    if len(skillshot.missiles) > 0:
        return game.get_spell_info(skillshot.missiles[0]).cast_range

    info = game.get_spell_info(skill_name)
    return info.cast_range * 2.0 if is_skillshot_cone(skill_name) else info.cast_range


def is_skillshot(skill_name):
    global Spells, MissileToSpell
    return skill_name in Spells or skill_name in MissileToSpell


def get_missile_parent_spell(missile_name):
    global MissileToSpell, Spells
    return MissileToSpell.get(missile_name, None)


def is_champ_supported(champ):
    global ChampionSpells
    return champ.name in ChampionSpells


def is_skillshot_cone(skill_name):
    if skill_name not in Spells:
        return False
    return Spells[skill_name].flags & SFlag.Cone

def is_last_hitable(game, player, enemy):
    missile_speed = player.basic_missile_speed + 1

    damageCalc.damage_type = damageType
    damageCalc.base_damage = 0

    hit_dmg = (
        damageCalc.calculate_damage(game, player, enemy)
        + items.get_onhit_physical(player, enemy)
        + items.get_onhit_magical(player, enemy)
    )

    hp = enemy.health + enemy.armour + (enemy.health_regen)
    t_until_basic_hits = (
        game.distance(player, enemy) / missile_speed
    )

    for missile in game.missiles:
        if missile.dest_id == enemy.id:
            src = game.get_obj_by_id(missile.src_id)
            if src:
                t_until_missile_hits = game.distance(missile, enemy) / (
                    missile.speed + 1
                )

                if t_until_missile_hits < t_until_basic_hits:
                    hp -= src.base_atk

    return hp - hit_dmg <= 0


def castpoint_for_collision(game, spell, caster, target):
    global Spells

    if spell.name not in Spells:
        return target.pos

    if not target.isMoving:
        return target.pos

    spell_extra = Spells[spell.name]
    if len(spell_extra.missiles) > 0 and spell_extra:
        missile = game.get_spell_info(spell_extra.missiles[0])
    else:
        missile = spell

    t_delay = spell.delay  # + (0.50 / 0.2) + 0.007
    if missile.travel_time > 0.0:
        t_missile = missile.travel_time
    else:
        t_missile = (
            (missile.cast_range / missile.delay + missile.speed)
            if spell_extra and len(spell_extra.missiles) > 0 and missile.speed > 0.0
            else 100.0
        )

    target_dir = target.pos.sub(target.prev_pos).normalize()
    if math.isnan(target_dir.x):
        target_dir.x = 0.0
    if math.isnan(target_dir.y):
        target_dir.y = 0.0
    if math.isnan(target_dir.z):
        target_dir.z = 0.0

    if spell_extra.flags & SFlag.Line:

        iterations = int(missile.cast_range / 30.0)
        step = t_missile / iterations

        last_dist = 999999999
        last_target_pos = None
        for i in range(iterations):
            t = i * step
            target_future_pos = target.pos.add(
                target_dir.scale((t_delay + t) * target.movement_speed)
            )
            spell_dir = (
                target_future_pos.sub(caster.pos).normalize().scale(t * missile.speed)
            )
            spell_future_pos = caster.pos.add(spell_dir)
            dist = target_future_pos.distance(spell_future_pos)
            if dist < missile.width / 2.0:
                return target_future_pos
            elif dist > last_dist:
                return last_target_pos
            else:
                last_dist = dist
                last_target_pos = target_future_pos

    elif spell_extra.flags & SFlag.Area:
        return target.pos.add(target_dir.scale(t_delay * target.movement_speed))
    else:
        return target.pos


def GetSpellHitTime(game, missile, spell, pos):
    spellPos = game.world_to_screen(missile.pos)
    if spell.flags & SFlag.Line:
        if missile.speed == 0:
            return max(0, spellPos.distance(pos))
        return 1000 * spellPos.distance(pos) / missile.speed
    if spell.flags & SFlag.Area:
        return max(0, spellPos.distance(pos))
    return float("inf")


def CanHeroEvade(game, missile, spell, evadePos):
    self = game.player

    heroPos = game.world_to_screen(self.pos)
    projection = game.world_to_screen(evadePos)

    evadeTime = 0
    spellHitTime = 0
    speed = self.movement_speed
    delay = 0.0

    if spell.flags & SFlag.Line:
        evadeTime = (
            missile.cast_radius
            - heroPos.distance(projection)
            + self.gameplay_radius
            + 10
        ) / (missile.pos.distance(self.pos) or speed)
        spellHitTime = GetSpellHitTime(game, missile, spell, projection)
    if spell.flags & SFlag.Area:
        evadeTime = (missile.cast_radius - self.pos.distance(missile.end_pos)) / (
            missile.pos.distance(self.pos) or speed
        )
        spellHitTime = GetSpellHitTime(game, missile, spell, projection)
    if spell.flags & SFlag.Cone:
        evadeTime = (heroPos.distance(projection) + self.gameplay_radius) / (
            missile.pos.distance(self.pos) or speed
        )
        spellHitTime = GetSpellHitTime(game, missile, spell, projection)
    return spellHitTime - delay > evadeTime


def IsCollisioned(game, target, oType="minion"):
    self = game.player

    if oType == "minion":
        for minion in game.minions:
            if minion.is_enemy_to(game.player) and minion.is_alive:
                if game.point_on_line(
                    game.world_to_screen(self.pos),
                    game.world_to_screen(target.pos),
                    game.world_to_screen(minion.pos),
                    target.gameplay_radius * 1,
                ):
                    return True
    if oType == "champ":
        for champ in game.champs:
            if (
                champ.is_enemy_to(game.player)
                and champ.is_alive
                and not champ.name == target.name
            ):
                if game.point_on_line(
                    game.world_to_screen(self.pos),
                    game.world_to_screen(target.pos),
                    game.world_to_screen(champ.pos),
                    target.gameplay_radius * 1,
                ):
                    return True
    return False


def GetDistanceSqr(a, b):
    if a.z != None and b.z != None:
        x = a.x - b.x
        z = a.z - b.z
        return x * x + z * z
    else:
        x = a.x - b.x
        y = a.y - b.y
        return x * x + y * y


def InSkillShot(game, pos, missile, spell, radius):
    pointSegment, pointLine, isOnSegment = VectorPointProjectionOnLineSegment(
        missile.start_pos, missile.end_pos, pos
    )
    if spell.flags & SFlag.Line or spell.flags & SFlag.SkillshotLine:
        return isOnSegment and pointSegment.distance(pos) <= game.player.gameplay_radius * 2
    if spell.flags & SFlag.Area:
        return game.point_on_line(
            game.world_to_screen(missile.start_pos),
            game.world_to_screen(missile.end_pos),
            game.world_to_screen(pos),
            radius,
        )
    return (
        isOnSegment
        and pointSegment.distance(pos)
        <= (missile.width or missile.cast_radius) + radius + game.player.gameplay_radius
    )


def IsDanger(game, point):
    for missile in game.missiles:
        if not game.player.is_alive or missile.is_ally_to(game.player):
            continue
        if not is_skillshot(missile.name):
            continue
        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue
        if InSkillShot(game, point, missile, spell, game.player.gameplay_radius):
            return True
        else:
            return False


def RotateAroundPoint(v1, v2, angle):
    cos, sin = math.cos(angle), math.sin(angle)
    x = ((v1.x - v2.x) * cos) - ((v2.z - v1.z) * sin) + v2.x
    z = ((v2.z - v1.z) * cos) + ((v1.x - v2.x) * sin) + v2.z
    return Vec3(x, v1.y, z or 0)


def getEvadePos(game, current, br, missile, spell):
    self = game.player

    direction = missile.end_pos.sub(missile.start_pos)

    pos3 = missile.end_pos.add(Vec3(-direction.z, direction.y, direction.x * 1.0))
    pos4 = missile.end_pos.add(Vec3(direction.z * 1.0, direction.y, -direction.x))

    direction2 = pos3.sub(pos4)
    direction2 = game.clamp2d(direction2, br)

    direction3 = Vec3(0, 0, 0)
    direction3.x = -direction2.x
    direction3.y = -direction2.y
    direction3.z = -direction2.z

    points = list()

    for k in range(-8, 8, 2):
        if game.is_left(
            game.world_to_screen(missile.start_pos),
            game.world_to_screen(missile.end_pos),
            game.world_to_screen(self.pos),
        ):
            test_pos = current.add(
                direction3.add(direction.normalize().scale(k * 40).add(Vec3(40, 0, 40)))
            )
            if not SRinWall(game, test_pos) and not IsDanger(game, test_pos):
                points.append(test_pos)
        else:
            test_pos = current.add(
                direction2.add(direction.normalize().scale(k * 40).add(Vec3(40, 0, 40)))
            )
            if not SRinWall(game, test_pos) and not IsDanger(game, test_pos):
                points.append(test_pos)
    if len(points) > 0:
        points = sorted(points, key=lambda a: self.pos.distance(a))
        return points[0]
    return None