#!/usr/bin/python3

import argparse, os.path, json, sys, shutil, random

from itemrandomizerweb.Randomizer import Randomizer, RandoSettings, progSpeeds
from itemrandomizerweb.AreaRandomizer import AreaRandomizer
from itemrandomizerweb.PaletteRando import PaletteRando
from graph_locations import locations as graphLocations
from graph_access import vanillaTransitions, vanillaBossesTransitions, GraphUtils
from parameters import Knows, easy, medium, hard, harder, hardcore, mania, text2diff, diff2text
from utils import PresetLoader
from rom_patches import RomPatches
from rom import RomPatcher, FakeROM
from utils import loadRandoPreset
import log, db

speeds = progSpeeds + ['variable']
energyQties = ['sparse', 'medium', 'vanilla' ]
progDiffs = ['easier', 'normal', 'harder']
morphPlacements = ['early', 'late', 'normal', 'classic']
majorsSplits = ['Full', 'Major', 'Chozo']

def dumpErrorMsg(outFileName, msg):
    print("DIAG: " + msg)
    if outFileName is not None:
        with open(outFileName, 'w') as jsonFile:
            json.dump({"errorMsg": msg}, jsonFile)

def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 9.0:
        raise argparse.ArgumentTypeError("%r not in range [1.0, 9.0]"%(x,))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random Metroid Randomizer")
    parser.add_argument('--patchOnly',
                        help="only apply patches, do not perform any randomization", action='store_true',
                        dest='patchOnly', default=False)
    parser.add_argument('--param', '-p', help="the input parameters", nargs='+',
                        default=None, dest='paramsFileName')
    parser.add_argument('--dir',
                        help="output directory for ROM and dot files",
                        dest='directory', nargs='?', default='.')
    parser.add_argument('--dot',
                        help="generate dot file with area graph",
                        action='store_true',dest='dot', default=False)
    parser.add_argument('--area', help="area mode",
                        dest='area', nargs='?', const=True, default=False)
    parser.add_argument('--areaLayoutBase',
                        help="use simple layout patch for area mode", action='store_true',
                        dest='areaLayoutBase', default=False)
    parser.add_argument('--noEscapeRando',
                        help="Do not randomize the escape sequence in area mode", action='store_true',
                        dest='noEscapeRando', default=False)
    parser.add_argument('--noRemoveEscapeEnemies',
                        help="Do not remove enemies during escape sequence in area mode", action='store_true',
                        dest='noRemoveEscapeEnemies', default=False)
    parser.add_argument('--bosses', help="randomize bosses",
                        dest='bosses', nargs='?', const=True, default=False)
    parser.add_argument('--startAP', help="Name of the Access Point to start from",
                        dest='startAP', nargs='?', default="Landing Site",
                        choices=['random'] + GraphUtils.getStartAccessPointNames())
    parser.add_argument('--debug', '-d', help="activate debug logging", dest='debug',
                        action='store_true')
    parser.add_argument('--maxDifficulty', '-t',
                        help="the maximum difficulty generated seed will be for given parameters",
                        dest='maxDifficulty', nargs='?', default=None,
                        choices=['easy', 'medium', 'hard', 'harder', 'hardcore', 'mania', 'random'])
    parser.add_argument('--seed', '-s', help="randomization seed to use", dest='seed',
                        nargs='?', default=0, type=int)
    parser.add_argument('--rom', '-r',
                        help="the vanilla ROM",
                        dest='rom', nargs='?', default=None)
    parser.add_argument('--output',
                        help="to choose the name of the generated json (for the webservice)",
                        dest='output', nargs='?', default=None)
    parser.add_argument('--preset',
                        help="the name of the preset (for the webservice)",
                        dest='preset', nargs='?', default=None)
    parser.add_argument('--patch', '-c',
                        help="optional patches to add",
                        dest='patches', nargs='?', default=[], action='append',
                        choices=['itemsounds.ips', 'elevators_doors_speed.ips',
                                 'spinjumprestart.ips', 'rando_speed.ips', 'No_Music'])
    parser.add_argument('--missileQty', '-m',
                        help="quantity of missiles",
                        dest='missileQty', nargs='?', default=3,
                        type=restricted_float)
    parser.add_argument('--superQty', '-q',
                        help="quantity of super missiles",
                        dest='superQty', nargs='?', default=2,
                        type=restricted_float)
    parser.add_argument('--powerBombQty', '-w',
                        help="quantity of power bombs",
                        dest='powerBombQty', nargs='?', default=1,
                        type=restricted_float)
    parser.add_argument('--minorQty', '-n',
                        help="quantity of minors",
                        dest='minorQty', nargs='?', default=100,
                        choices=[str(i) for i in range(0,101)])
    parser.add_argument('--energyQty', '-g',
                        help="quantity of ETanks/Reserve Tanks",
                        dest='energyQty', nargs='?', default='vanilla',
                        choices=energyQties + ['random'])
    parser.add_argument('--strictMinors',
                        help="minors quantities values will be strictly followed instead of being probabilities",
                        dest='strictMinors', nargs='?', const=True, default=False)
    parser.add_argument('--majorsSplit',
                        help="how to split majors/minors: Full, Major, Chozo",
                        dest='majorsSplit', nargs='?', choices=majorsSplits + ['random'], default='Full')
    parser.add_argument('--suitsRestriction',
                        help="no suits in early game",
                        dest='suitsRestriction', nargs='?', const=True, default=False)
    parser.add_argument('--morphPlacement',
                        help="morph placement",
                        dest='morphPlacement', nargs='?', default='early',
                        choices=morphPlacements + ['random'])
    parser.add_argument('--hideItems', help="Like in dessy's rando hide half of the items",
                        dest="hideItems", nargs='?', const=True, default=False)
    parser.add_argument('--progressionSpeed', '-i',
                        help="progression speed, from " + str(speeds) + ". 'random' picks a random speed from these. Pick a random speed from a subset using comma-separated values, like 'slow,medium,fast'.",
                        dest='progressionSpeed', nargs='?', default='medium')
    parser.add_argument('--progressionDifficulty',
                        help="",
                        dest='progressionDifficulty', nargs='?', default='normal',
                        choices=progDiffs + ['random'])
    parser.add_argument('--superFun',
                        help="randomly remove major items from the pool for maximum enjoyment",
                        dest='superFun', nargs='?', default=[], action='append',
                        choices=['Movement', 'Combat', 'Suits', 'MovementRandom', 'CombatRandom', 'SuitsRandom'])
    parser.add_argument('--animals',
                        help="randomly change the save the animals room",
                        dest='animals', action='store_true', default=False)
    parser.add_argument('--nolayout',
                        help="do not include total randomizer layout patches",
                        dest='noLayout', action='store_true', default=False)
    parser.add_argument('--nogravheatPatch',
                        help="do not include total randomizer suits patches",
                        dest='noGravHeat', action='store_true', default=False)
    parser.add_argument('--progressiveSuits',
                        help="apply progressive suits patch",
                        dest='progressiveSuits', action='store_true', default=False)
    parser.add_argument('--nerfedCharge',
                        help="apply nerfed charge patch",
                        dest='nerfedCharge', action='store_true', default=False)
    parser.add_argument('--novariatweaks',
                        help="do not include VARIA randomizer tweaks",
                        dest='noVariaTweaks', action='store_true', default=False)
    parser.add_argument('--controls',
                        help="specify controls, comma-separated, in that order: Shoot,Jump,Dash,ItemSelect,ItemCancel,AngleUp,AngleDown. Possible values: A,B,X,Y,L,R,Select,None",
                        dest='controls')
    parser.add_argument('--moonwalk',
                        help="Enables moonwalk by default",
                        dest='moonWalk', action='store_true', default=False)
    parser.add_argument('--runtime',
                        help="Maximum runtime limit in seconds. If 0 or negative, no runtime limit. Default is 30.",
                        dest='runtimeLimit_s', nargs='?', default=30, type=int)
    parser.add_argument('--race', help="Race mode magic number, between 1 and 65535", dest='raceMagic',
                        type=int)
    parser.add_argument('--vcr', help="Generate VCR output file", dest='vcr', action='store_true')
    parser.add_argument('--palette', help="Randomize the palettes", dest='palette', action='store_true')
    parser.add_argument('--individual_suit_shift', help="palette param", action='store_true',
                        dest='individual_suit_shift', default=False)
    parser.add_argument('--individual_tileset_shift', help="palette param", action='store_true',
                        dest='individual_tileset_shift', default=False)
    parser.add_argument('--no_match_ship_and_power', help="palette param", action='store_false',
                        dest='match_ship_and_power', default=True)
    parser.add_argument('--seperate_enemy_palette_groups', help="palette param", action='store_true',
                        dest='seperate_enemy_palette_groups', default=False)
    parser.add_argument('--no_match_room_shift_with_boss', help="palette param", action='store_false',
                        dest='match_room_shift_with_boss', default=True)
    parser.add_argument('--no_shift_tileset_palette', help="palette param", action='store_false',
                        dest='shift_tileset_palette', default=True)
    parser.add_argument('--no_shift_boss_palettes', help="palette param", action='store_false',
                        dest='shift_boss_palettes', default=True)
    parser.add_argument('--no_shift_suit_palettes', help="palette param", action='store_false',
                        dest='shift_suit_palettes', default=True)
    parser.add_argument('--no_shift_enemy_palettes', help="palette param", action='store_false',
                        dest='shift_enemy_palettes', default=True)
    parser.add_argument('--no_shift_beam_palettes', help="palette param", action='store_false',
                        dest='shift_beam_palettes', default=True)
    parser.add_argument('--no_shift_ship_palette', help="palette param", action='store_false',
                        dest='shift_ship_palette', default=True)
    parser.add_argument('--min_degree', help="min hue shift", dest='min_degree', nargs='?', default=-180, type=int)
    parser.add_argument('--max_degree', help="max hue shift", dest='max_degree', nargs='?', default=180, type=int)
    parser.add_argument('--no_global_shift', help="", action='store_false', dest='global_shift', default=True)
    parser.add_argument('--invert', help="invert color range", dest='invert', action='store_true', default=False)
    parser.add_argument('--ext_stats', help="dump extended stats SQL", nargs='?', default=None, dest='extStatsFilename')
    parser.add_argument('--randoPreset', help="rando preset file", dest="randoPreset", nargs='?', default=None)
    parser.add_argument('--plandoRando', help="json string with already placed items/locs", dest="plandoRando",
                        nargs='?', default=None)
    parser.add_argument('--sprite', help='use a custom sprite for Samus', dest='sprite', default=None)

    # parse args
    args = parser.parse_args()

    if args.output is None and args.rom is None:
        print("Need --output or --rom parameter")
        sys.exit(-1)
    elif args.output is not None and args.rom is not None:
        print("Can't have both --output and --rom parameters")
        sys.exit(-1)

    if args.plandoRando != None and args.output == None:
        print("plandoRando param requires output param")
        sys.exit(-1)

    log.init(args.debug)
    logger = log.get('Rando')
    # service to force an argument value and notify it
    argDict = vars(args)
    def forceArg(arg, value, msg):
        if argDict[arg] != value:
            argDict[arg] = value
            print(msg)
            return '\n'+msg
        else:
            return ''
    # if rando preset given, load it first
    if args.randoPreset != None:
        loadRandoPreset(args.randoPreset, args)

    # if diff preset given, load it
    if args.paramsFileName is not None:
        PresetLoader.factory(args.paramsFileName[0]).load()
        preset = os.path.splitext(os.path.basename(args.paramsFileName[0]))[0]

        if args.preset is not None:
            preset = args.preset
    else:
        preset = 'default'

    logger.debug("preset: {}".format(preset))

    # if no seed given, choose one
    if args.seed == 0:
        seed = random.randint(0, 9999999)
    else:
        seed = args.seed
    logger.debug("seed: {}".format(seed))

    seed4rand = seed
    if args.raceMagic is not None:
        if args.raceMagic <= 0 or args.raceMagic >= 0x10000:
            print("Invalid magic")
            sys.exit(-1)
        seed4rand = seed ^ args.raceMagic
    random.seed(seed4rand)
    optErrMsg = ""
    # choose on animal patch
    if args.animals == True:
        animalsPatches = ['animal_enemies.ips', 'animals.ips', 'draygonimals.ips', 'escapimals.ips',
                          'gameend.ips', 'grey_door_animals.ips', 'low_timer.ips', 'metalimals.ips',
                          'phantoonimals.ips', 'ridleyimals.ips']
        if args.area == True and args.noEscapeRando == False:
            # these glitch with enemies on
            animalsPatches.remove('phantoonimals.ips') # excessive lag and ridley sound effects
            animalsPatches.remove('ridleyimals.ips') # escape timer tiles tail
            if args.noRemoveEscapeEnemies == False:
                animalsPatches.remove('draygonimals.ips') # glitched room
                animalsPatches.remove('metalimals.ips') # no pirates
        args.patches.append(random.choice(animalsPatches))
    # if no max diff, set it very high
    if args.maxDifficulty:
        if args.maxDifficulty == 'random':
            diffs = ['hard', 'harder', 'very hard', 'hardcore', 'mania']
            maxDifficulty = text2diff[random.choice(diffs)]
        else:
            maxDifficulty = text2diff[args.maxDifficulty]
    else:
        maxDifficulty = float('inf')
    # same as solver, increase max difficulty
    threshold = maxDifficulty
    epsilon = 0.001
    if maxDifficulty <= easy:
        threshold = medium - epsilon
    elif maxDifficulty <= medium:
        threshold = hard - epsilon
    elif maxDifficulty <= hard:
        threshold = harder - epsilon
    elif maxDifficulty <= harder:
        threshold = hardcore - epsilon
    elif maxDifficulty <= hardcore:
        threshold = mania - epsilon
    maxDifficulty = threshold
    logger.debug("maxDifficulty: {}".format(maxDifficulty))

    # if random progression speed, choose one
    progSpeed = str(args.progressionSpeed).lower()
    if progSpeed == "random":
        progSpeed = random.choice(speeds)
    mulSpeeds = progSpeed.split(',')
    progSpeed = random.choice(mulSpeeds)
    if len(mulSpeeds) > 1:
        args.progressionSpeed = 'random'
    if progSpeed not in speeds:
        print('Invalid progression speed : ' + progSpeed)
        sys.exit(-1)
    logger.debug("progression speed: {}".format(progSpeed))

    # if random progression difficulty, choose one
    progDiff = args.progressionDifficulty
    if progDiff == "random":
        progDiff = random.choice(progDiffs)
    logger.debug("progression diff: {}".format(progDiff))

    majorsSplitRandom = False
    if args.majorsSplit == 'random':
        majorsSplitRandom = True
        args.majorsSplit = random.choice(majorsSplits)
    logger.debug("majorsSplit: {}".format(args.majorsSplit))

    areaRandom = False
    if args.area == 'random':
        areaRandom = True
        args.area = bool(random.randint(0, 2))
    logger.debug("area: {}".format(args.area))

    bossesRandom = False
    if args.bosses == 'random':
        bossesRandom = True
        args.bosses = bool(random.randint(0, 2))
    logger.debug("bosses: {}".format(args.bosses))

    if args.suitsRestriction == 'random':
        if args.morphPlacement == 'late' and args.area == True:
            args.suitsRestriction = False
        else:
            args.suitsRestriction = bool(random.randint(0, 2))
    logger.debug("suitsRestriction: {}".format(args.suitsRestriction))

    if args.hideItems == 'random':
        args.hideItems = bool(random.randint(0, 2))

    if args.morphPlacement == 'random':
        if (args.suitsRestriction == True and args.area == True) or args.majorsSplit == 'Chozo':
            morphPlacements.remove('late')
        args.morphPlacement = random.choice(morphPlacements)
    # late + chozo will always stuck
    if args.majorsSplit == 'Chozo' and args.morphPlacement == "late":
        optErrMsg += forceArg('morphPlacement', 'normal', "'Morph Placement' forced to normal")
    logger.debug("morphPlacement: {}".format(args.morphPlacement))

    if args.strictMinors == 'random':
        args.strictMinors = bool(random.randint(0, 2))

    if not GraphUtils.isStandardStart(args.startAP):
        if args.morphPlacement == 'late':
            optErrMsg += forceArg('morphPlacement', 'normal', "'Morph Placement' forced to normal")
        optErrMsg += forceArg('majorsSplit', 'Full', "'Majors Split' forced to Full")
        optErrMsg += forceArg('noVariaTweaks', False, "'VARIA tweaks' forced to on")
        optErrMsg += forceArg('noLayout', False, "'Anti-softlock layout patches' forced to on")
        optErrMsg += forceArg('suitsRestriction', False, "'Suits restriction' forced to off")
        optErrMsg += forceArg('areaLayoutBase', False, "'Additional layout patches for easier navigation' forced to on")
        possibleStartAPs = GraphUtils.getPossibleStartAPs(args.area, maxDifficulty)
        if args.startAP == 'random':
            args.startAP = random.choice(possibleStartAPs)
        elif args.startAP not in possibleStartAPs:
            optErrMsg += '\nInvalid start location: {}'.format(args.startAP)
            optErrMsg += '\nPossible start locations with these settings: {}'.format(possibleStartAPs)
            dumpErrorMsg(args.output, optErrMsg)
            sys.exit(-1)

    print("startAP:{}".format(args.startAP))

    if args.patchOnly == False:
        print("SEED: " + str(seed))

    # fill restrictions dict
    restrictions = { 'Suits' : args.suitsRestriction, 'Morph' : args.morphPlacement }
    restrictions['MajorMinor'] = args.majorsSplit
    seedCode = 'X'
    if majorsSplitRandom == False:
        if restrictions['MajorMinor'] == 'Full':
            seedCode = 'FX'
        elif restrictions['MajorMinor'] == 'Chozo':
            seedCode = 'ZX'
        elif restrictions['MajorMinor'] == 'Major':
            seedCode = 'MX'
    if args.bosses == True and bossesRandom == False:
        seedCode = 'B'+seedCode
    if args.area == True and areaRandom == False:
        seedCode = 'A'+seedCode

    # output ROM name
    if args.patchOnly == False:
        fileName = 'VARIA_Randomizer_' + seedCode + str(seed) + '_' + preset
        if args.progressionSpeed != "random":
            fileName += "_" + args.progressionSpeed
    else:
        fileName = 'VARIA' # TODO : find better way to name the file (argument?)
    seedName = fileName
    if args.directory != '.':
        fileName = args.directory + '/' + fileName
    if args.noLayout == True:
        RomPatches.ActivePatches = RomPatches.TotalBase
    else:
        RomPatches.ActivePatches = RomPatches.Total
    RomPatches.ActivePatches.remove(RomPatches.BlueBrinstarBlueDoor)
    RomPatches.ActivePatches += GraphUtils.getGraphPatches(args.startAP)
    if args.noGravHeat == True or args.progressiveSuits == True:
        RomPatches.ActivePatches.remove(RomPatches.NoGravityEnvProtection)
    if args.progressiveSuits == True:
        RomPatches.ActivePatches.append(RomPatches.ProgressiveSuits)
    if args.nerfedCharge == True:
        RomPatches.ActivePatches.append(RomPatches.NerfedCharge)
    if args.noVariaTweaks == False:
        RomPatches.ActivePatches += RomPatches.VariaTweaks
    missileQty = float(args.missileQty)
    superQty = float(args.superQty)
    powerBombQty = float(args.powerBombQty)
    minorQty = int(args.minorQty)
    energyQty = args.energyQty
    if missileQty < 1:
        missileQty = random.randint(1, 9)
    if superQty < 1:
        superQty = random.randint(1, 9)
    if powerBombQty < 1:
        powerBombQty = random.randint(1, 9)
    if minorQty < 1:
        minorQty = random.randint(25, 100)
    if energyQty == 'random':
        energyQty = random.choice(energyQties)
    qty = {'energy': energyQty,
           'minors': minorQty,
           'ammo': { 'Missile': missileQty,
                     'Super': superQty,
                     'PowerBomb': powerBombQty },
           'strictMinors' : args.strictMinors }
    logger.debug("quantities: {}".format(qty))

    if len(args.superFun) > 0:
        superFun = []
        for fun in args.superFun:
            if fun.find('Random') != -1:
                if bool(random.randint(0, 2)) == True:
                    superFun.append(fun[0:fun.find('Random')])
            else:
                superFun.append(fun)
        args.superFun = superFun
    logger.debug("superFun: {}".format(args.superFun))

    ctrlDict = None
    if args.controls:
        ctrlList = args.controls.split(',')
        if len(ctrlList) != 7:
            raise ValueError("Invalid control list size")
        ctrlKeys = ["Shot", "Jump", "Dash", "ItemSelect", "ItemCancel", "AngleUp", "AngleDown"]
        ctrlDict = {}
        i = 0
        for k in ctrlKeys:
            b = ctrlList[i]
            if b in RomPatcher.buttons:
                ctrlDict[k] = b
                i += 1
            else:
                raise ValueError("Invalid button name : " + str(b))

    if args.plandoRando != None:
        args.plandoRando = json.loads(args.plandoRando)
        RomPatches.ActivePatches = args.plandoRando["patches"]

    randoSettings = RandoSettings(args.startAP,
                                  maxDifficulty, progSpeed, progDiff, qty,
                                  restrictions, args.superFun, args.runtimeLimit_s,
                                  args.vcr,
                                  args.plandoRando["locsItems"] if args.plandoRando != None else None)
    bossTransitions = vanillaBossesTransitions
    if args.bosses == True:
        bossTransitions = GraphUtils.createBossesTransitions()
    if args.area == True:
        if args.dot == True:
            dotDir = args.directory
        else:
            dotDir = None
        RomPatches.ActivePatches += RomPatches.AreaSet
        if args.areaLayoutBase == True:
            RomPatches.ActivePatches.remove(RomPatches.AreaRandoGatesOther)
        try:
            randomizer = AreaRandomizer(graphLocations, randoSettings, seedName, bossTransitions,
                                        dotDir=dotDir,
                                        escape=not args.noEscapeRando,
                                        removeEscapeEnemies=not args.noRemoveEscapeEnemies)
        except RuntimeError:
            msg = "Cannot generate area layout. Retry, and change the super fun settings if the problem happens again."
            dumpErrorMsg(args.output, msg)
            sys.exit(-1)
    else:
        try:
            if args.plandoRando != None:
                transitions = args.plandoRando["transitions"]
            else:
                transitions = vanillaTransitions + bossTransitions
            randomizer = Randomizer(graphLocations, randoSettings, seedName, transitions)
        except RuntimeError:
            msg = "Locations unreachable detected with preset/super fun/max diff. Retry, and change the Super Fun settings and/or Maximum difficulty if the problem happens again."
            dumpErrorMsg(args.output, msg)
            sys.exit(-1)
        except Exception as e:
            msg = str(e)
            dumpErrorMsg(args.output, msg)
            sys.exit(-1)
    if args.patchOnly == False:
        (stuck, itemLocs, progItemLocs) = randomizer.generateItems()
        doors = GraphUtils.getDoorConnections(randomizer.areaGraph,
                                              args.area, args.bosses,
                                              args.area and not args.noEscapeRando)
        escapeTimer = randomizer.areaGraph.EscapeTimer
    else:
        stuck = False
        itemLocs = []
        progItemLocs = None
    if stuck == True:
        dumpErrorMsg(args.output, randomizer.errorMsg)
        print("Can't generate " + fileName + " with the given parameters: {}".format(randomizer.errorMsg))
        # in vcr mode we still want the seed to be generated to analyze it
        if args.vcr == False:
            sys.exit(-1)

    # hide some items like in dessy's
    if args.hideItems == True:
        for itemLoc in itemLocs:
            if (itemLoc['Item']['Type'] not in ['Nothing', 'NoEnergy']
                and itemLoc['Location']['CanHidden'] == True
                and itemLoc['Location']['Visibility'] == 'Visible'):
                if bool(random.randint(0, 2)) == True:
                    itemLoc['Location']['Visibility'] = 'Hidden'

    # transform itemLocs in our usual dict(location, item), for minors keep only the first
    locsItems = {}
    firstMinorsFound = {'Missile': False, 'Super': False, 'PowerBomb': False}
    for itemLoc in itemLocs:
        locName = itemLoc["Location"]["Name"]
        itemType = itemLoc["Item"]["Type"]
        if itemType in firstMinorsFound and firstMinorsFound[itemType] == False:
            locsItems[locName] = itemType
            firstMinorsFound[itemType] = True
        elif itemType not in firstMinorsFound:
            locsItems[locName] = itemType
    if args.debug == True:
        for loc in sorted(locsItems.keys()):
            print('{:>50}: {:>16} '.format(loc, locsItems[loc]))

    if args.plandoRando != None:
        # replace smbool with a dict
        for itemLoc in itemLocs:
            itemLoc["Location"]["difficulty"] = itemLoc["Location"]["difficulty"].json()
            if "Wrapper" in itemLoc["Item"]:
                del itemLoc["Item"]["Wrapper"]

        with open(args.output, 'w') as jsonFile:
            json.dump({"itemLocs": itemLocs, "errorMsg": randomizer.errorMsg}, jsonFile, default=lambda x: x.__dict__)
        sys.exit(0)

    # generate extended stats
    if args.extStatsFilename != None:
        if args.noGravHeat == True:
            gravityBehaviour = 'Vanilla'
        elif args.progressiveSuits == True:
            gravityBehaviour = 'Progressive'
        else:
            gravityBehaviour = 'Balanced'
        if args.maxDifficulty == None:
            args.maxDifficulty = 'no difficulty cap'
        parameters = {'preset': preset, 'area': args.area, 'boss': args.bosses,
                      'majorsSplit': args.majorsSplit,
                      'startAP': args.startAP,
                      'gravityBehaviour': gravityBehaviour,
                      'nerfedCharge': args.nerfedCharge,
                      'maxDifficulty': args.maxDifficulty,
                      'progSpeed': progSpeed, 'morphPlacement': args.morphPlacement,
                      'suitsRestriction': args.suitsRestriction, 'progDiff': progDiff,
                      'superFunMovement': 'Movement' in args.superFun,
                      'superFunCombat': 'Combat' in args.superFun,
                      'superFunSuit': 'Suits' in args.superFun}
        with open(args.extStatsFilename, 'a') as extStatsFile:
            db.DB.dumpExtStatsItems(parameters, locsItems, extStatsFile)

    try:
        # args.rom is not None: generate local rom named filename.sfc with args.rom as source
        # args.output is not None: generate local json named args.output
        if args.rom is not None:
            # patch local rom
            romFileName = args.rom
            outFileName = fileName + '.sfc'
            shutil.copyfile(romFileName, outFileName)
            romPatcher = RomPatcher(outFileName, magic=args.raceMagic)
        else:
            outFileName = args.output
            romPatcher = RomPatcher(magic=args.raceMagic)

        if args.patchOnly == False:
            suitsMode = "Classic"
            if args.progressiveSuits:
                suitsMode = "Progressive"
            elif args.noGravHeat:
                suitsMode = "Vanilla"
            romPatcher.applyIPSPatches(args.startAP, args.patches,
                                       args.noLayout, suitsMode,
                                       args.area, args.bosses, args.areaLayoutBase,
                                       args.noVariaTweaks, args.nerfedCharge,
                                       args.noEscapeRando, args.noRemoveEscapeEnemies)
        else:
            romPatcher.addIPSPatches(args.patches)
        if args.sprite is not None:
            romPatcher.customSprite(args.sprite) # adds another IPS
        romPatcher.commitIPS() # actually write IPS data
        if args.patchOnly == False:
            romPatcher.setNothingId(args.startAP, itemLocs)
            romPatcher.writeItemsLocs(itemLocs)
            romPatcher.writeItemsNumber()
            romPatcher.writeSeed(seed) # lol if race mode
            romPatcher.writeSpoiler(itemLocs, progItemLocs)
            romPatcher.writeRandoSettings(randoSettings, itemLocs)
            romPatcher.writeDoorConnections(doors)
            if escapeTimer is not None:
                romPatcher.writeEscapeTimer(escapeTimer)
        if ctrlDict is not None:
            romPatcher.writeControls(ctrlDict)
        if args.moonWalk == True:
            romPatcher.enableMoonWalk()
        if args.patchOnly == False:
            romPatcher.writeMagic()
            romPatcher.writeMajorsSplit(args.majorsSplit)
            romPatcher.writeNothingId()
        if args.palette == True:
            paletteSettings = {
                "global_shift": None,
                "individual_suit_shift": None,
                "individual_tileset_shift": None,
                "match_ship_and_power": None,
                "seperate_enemy_palette_groups": None,
                "match_room_shift_with_boss": None,
                "shift_tileset_palette": None,
                "shift_boss_palettes": None,
                "shift_suit_palettes": None,
                "shift_enemy_palettes": None,
                "shift_beam_palettes": None,
                "shift_ship_palette": None,
                "min_degree": None,
                "max_degree": None,
                "invert": None,
            }
            for param in paletteSettings:
                paletteSettings[param] = getattr(args, param)
            PaletteRando(romPatcher, paletteSettings, args.sprite).randomize()
        romPatcher.end()
        if args.rom is None:
            data = romPatcher.romFile.data
            fileName = '{}.sfc'.format(fileName)
            data["fileName"] = fileName
            # error msg in json to be displayed by the web site
            if optErrMsg != "":
                msg = optErrMsg + '\n' + randomizer.errorMsg
            else:
                msg = randomizer.errorMsg
            data["errorMsg"] = msg
            with open(outFileName, 'w') as jsonFile:
                json.dump(data, jsonFile)
    except Exception as e:
        msg = "Error patching {}: ({}: {})".format(outFileName, type(e).__name__, e)
        dumpErrorMsg(args.output, msg)
        sys.exit(-1)

    if stuck == True:
        print("Rom generated for debug purpose: {}".format(fileName))
    else:
        print("Rom generated: {}".format(fileName))
