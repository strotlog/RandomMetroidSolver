# -*- coding: utf-8 -*-

import sys, os.path
path = os.path.expanduser('~/RandomMetroidSolver')
if os.path.exists(path) and path not in sys.path:
    sys.path.append(path)

import datetime, os, hashlib, json, subprocess, tempfile, glob, random, re
from datetime import datetime, date
from collections import OrderedDict

# to solve the rom
from parameters import easy, medium, hard, harder, hardcore, mania
from parameters import Knows, Settings, Controller, isKnows, isButton
from solver import Conf
from parameters import diff2text, text2diff
from solver import StandardSolver, DifficultyDisplayer, InteractiveSolver
from utils import PresetLoader, removeChars
import db
from graph_access import vanillaTransitions, vanillaBossesTransitions, vanillaEscapeTransitions, accessPoints, GraphUtils
from utils import isStdPreset
from graph_locations import locations
from smboolmanager import SMBoolManager
from rom import RomReader
from rom_patches import RomPatches

# put an expiration date to the default cookie to have it kept between browser restart
response.cookies['session_id_solver']['expires'] = 31 * 24 * 3600

# use the correct one
pythonExec = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)

def maxPresetsReach():
    # to prevent a spammer to create presets in a loop and fill the fs
    return len(os.listdir('community_presets')) >= 2048

def getPresetDir(preset):
    if isStdPreset(preset):
        return 'standard_presets'
    else:
        return 'community_presets'

def loadPreset():
    # load conf from session if available
    loaded = False

    if request.vars.action is not None:
        # press solve, load or save button
        if request.vars.action in ['Update', 'Create']:
            # store the changes in case the form won't be accepted
            presetDict = genJsonFromParams(request.vars)
            session.presets['presetDict'] = presetDict
            params = PresetLoader.factory(presetDict).params
            loaded = True
        elif request.vars.action in ['Load']:
            # nothing to load, we'll load the new params file with the load form code
            pass
    else:
        # no forms button pressed
        if session.presets['presetDict'] is not None:
            params = PresetLoader.factory(session.presets['presetDict']).params
            loaded = True

    if not loaded:
        params = PresetLoader.factory('{}/{}.json'.format(getPresetDir(session.presets['preset']), session.presets['preset'])).params

    return params

def completePreset(params):
    # add missing knows
    for know in Knows.__dict__:
        if isKnows(know):
            if know not in params['Knows'].keys():
                params['Knows'][know] = Knows.__dict__[know]

    # add missing settings
    for boss in ['Kraid', 'Phantoon', 'Draygon', 'Ridley', 'MotherBrain']:
        if boss not in params['Settings']:
            params['Settings'][boss] = 'Default'
    for hellrun in ['Ice', 'MainUpperNorfair', 'LowerNorfair']:
        if hellrun not in params['Settings']:
            params['Settings'][hellrun] = 'Default'
    for hardroom in ['X-Ray', 'Gauntlet']:
        if hardroom not in params['Settings']:
            params['Settings'][hardroom] = 'Default'

    # add missing controller buttons
    for button in Controller.__dict__:
        if isButton(button):
            if button not in params['Controller'].keys():
                params['Controller'][button] = Controller.__dict__[button]

def loadPresetsList():
    files = sorted(os.listdir('community_presets'), key=lambda v: v.upper())
    stdPresets = ['noob', 'casual', 'regular', 'veteran', 'speedrunner', 'master']
    tourPresets = ['Season_Races', 'Playoff_Races', 'Playoff_Races_Chozo', 'SMRAT2020']
    comPresets = [os.path.splitext(file)[0] for file in files if file != '.git']
    return (stdPresets, tourPresets, comPresets)

def loadRandoPresetsList():
    tourPresets = ['Season_Races', 'Season_Races_Chozo', 'Playoff_Races', 'Playoff_Races_Chozo', 'SMRAT2020']
    files = sorted(os.listdir('rando_presets'), key=lambda v: v.upper())
    randoPresets = [os.path.splitext(file)[0] for file in files]
    randoPresets = [preset for preset in randoPresets if preset not in tourPresets]
    return (randoPresets, tourPresets)

def validatePresetsParams(action):
    if action == 'Create':
        preset = request.vars.presetCreate
    else:
        preset = request.vars.preset

    if IS_NOT_EMPTY()(preset)[1] is not None:
        return (False, "Preset name is empty")
    if IS_ALPHANUMERIC()(preset)[1] is not None:
        return (False, "Preset name must be alphanumeric: {}".format(preset))
    if IS_LENGTH(32)(preset)[1] is not None:
        return (False, "Preset name must be max 32 chars: {}".format(preset))

    if action in ['Create', 'Update']:
        if IS_NOT_EMPTY()(request.vars.password)[1] is not None:
            return (False, "Password is empty")
        if IS_ALPHANUMERIC()(request.vars.password)[1] is not None:
            return (False, "Password must be alphanumeric")
        if IS_LENGTH(32)(request.vars.password)[1] is not None:
            return (False, "Password must be max 32 chars")

        # check that there's not two buttons for the same action
        map = {}
        for button in Controller.__dict__:
            if isButton(button):
                value = request.vars[button]
                if button == "Moonwalk":
                    if value not in [None, 'on']:
                        return (False, "Invalid value for Moonwalk: {}".format(value))
                else:
                    if value is None:
                        return (False, "Button {} not set".format(button))
                    else:
                        if value in map:
                            return (False, "Action {} set for two buttons: {} and {}".format(value, button, map[value]))
                        map[value] = button

    if request.vars.currenttab not in ['Global', 'Techniques1', 'Techniques2', 'Techniques3', 'Techniques4', 'Techniques5', 'Techniques6', 'Techniques7', 'Mapping']:
        return (False, "Wrong value for current tab: [{}]".format(request.vars.currenttab))

    return (True, None)

def getSkillLevelBarData(preset):
    result = {'standards': {}}
    result['name'] = preset
    try:
        params = PresetLoader.factory('{}/{}.json'.format(getPresetDir(preset), preset)).params
        result['custom'] = (preset, params['score'])
        # add stats on the preset
        result['knowsKnown'] = len([know for know in params['Knows'] if params['Knows'][know][0] == True])
    except:
        result['custom'] = (preset, 'N/A')
        result['knowsKnown'] = 'N/A'

    # get score of standard presets
    for preset in ['noob', 'casual', 'regular', 'veteran', 'speedrunner', 'master', 'samus']:
        score = PresetLoader.factory('{}/{}.json'.format(getPresetDir(preset), preset)).params['score']
        result['standards'][preset] = score

    DB = db.DB()
    result['generatedSeeds'] = DB.getGeneratedSeeds(result['custom'][0])
    result['lastAction'] = DB.getPresetLastActionDate(result['custom'][0])
    DB.close()

    # TODO: normalize result (or not ?)
    return result

def initPresetsSession():
    if session.presets is None:
        session.presets = {}

        session.presets['preset'] = 'regular'
        session.presets['presetDict'] = None
        session.presets['currentTab'] = 'Global'

def updatePresetsSession():
    if request.vars.action == 'Create':
        session.presets['preset'] = request.vars.presetCreate
    elif request.vars.preset == None:
        session.presets['preset'] = 'regular'
    else:
        session.presets['preset'] = request.vars.preset

def computeGauntlet(sm, bomb, addVaria):
    result = {}

    for key in Settings.hardRoomsPresets['Gauntlet']:
        Settings.hardRooms['Gauntlet'] = Settings.hardRoomsPresets['Gauntlet'][key]
        sm.resetItems()
        if addVaria == True:
            sm.addItem('Varia')
        sm.addItem(bomb)

        result[key] = {easy: -1, medium: -1, hard: -1, harder: -1, hardcore: -1, mania: -1}

        for i in range(18):
            ret = sm.energyReserveCountOkHardRoom('Gauntlet', 0.51 if bomb == 'Bomb' else 1.0)

            if ret.bool == True:
                nEtank = 0
                for item in ret.items:
                    if item.find('ETank') != -1:
                        nEtank = int(item[0:item.find('-ETank')])
                        break
                result[key][ret.difficulty] = nEtank

            sm.addItem('ETank')

    return result

def computeXray(sm, addVaria):
    result = {}

    for key in Settings.hardRoomsPresets['X-Ray']:
        if key == 'Solution':
            continue
        Settings.hardRooms['X-Ray'] = Settings.hardRoomsPresets['X-Ray'][key]
        sm.resetItems()
        if addVaria == True:
            sm.addItem('Varia')

        result[key] = {easy: -1, medium: -1, hard: -1, harder: -1, hardcore: -1, mania: -1}

        for i in range(18):
            ret = sm.energyReserveCountOkHardRoom('X-Ray')

            if ret.bool == True:
                nEtank = 0
                for item in ret.items:
                    if item.find('ETank') != -1:
                        nEtank = int(item[0:item.find('-ETank')])
                        break
                result[key][ret.difficulty] = nEtank

            sm.addItem('ETank')

    return result

def computeHardRooms(hardRooms):
    # add gravity patch (as we add it by default in the randomizer)
    RomPatches.ActivePatches.append(RomPatches.NoGravityEnvProtection)

    sm = SMBoolManager()

    # xray
    xray = {}
    xray['Suitless'] = computeXray(sm, False)
    xray['Varia'] = computeXray(sm, True)
    hardRooms['X-Ray'] = xray

    # gauntlet
    gauntlet = {}
    gauntlet['SuitlessBomb'] = computeGauntlet(sm, 'Bomb', False)
    gauntlet['SuitlessPowerBomb'] = computeGauntlet(sm, 'PowerBomb', False)
    gauntlet['VariaBomb'] = computeGauntlet(sm, 'Bomb', True)
    gauntlet['VariaPowerBomb'] = computeGauntlet(sm, 'PowerBomb', True)
    hardRooms['Gauntlet'] = gauntlet

    return hardRooms

def addCF(sm, count):
    sm.addItem('Morph')
    sm.addItem('PowerBomb')

    for i in range(count):
        sm.addItem('Missile')
        sm.addItem('Missile')
        sm.addItem('Super')
        sm.addItem('Super')
        sm.addItem('PowerBomb')
        sm.addItem('PowerBomb')

def computeHellruns(hellRuns):
    sm = SMBoolManager()
    for hellRun in ['Ice', 'MainUpperNorfair']:
        hellRuns[hellRun] = {}

        for (actualHellRun, params) in Settings.hellRunsTable[hellRun].items():
            hellRuns[hellRun][actualHellRun] = {}
            for (key, difficulties) in Settings.hellRunPresets[hellRun].items():
                if key == 'Solution':
                    continue
                Settings.hellRuns[hellRun] = difficulties
                hellRuns[hellRun][actualHellRun][key] = {easy: -1, medium: -1, hard: -1, harder: -1, hardcore: -1, mania: -1}
                if difficulties == None:
                    continue

                sm.resetItems()
                for etank in range(19):
                    ret = sm.canHellRun(**params)

                    if ret.bool == True:
                        nEtank = 0
                        for item in ret.items:
                            if item.find('ETank') != -1:
                                nEtank = int(item[0:item.find('-ETank')])
                                break
                        hellRuns[hellRun][actualHellRun][key][ret.difficulty] = nEtank

                    sm.addItem('ETank')

    hellRun = 'LowerNorfair'
    hellRuns[hellRun] = {}
    hellRuns[hellRun]["NoScrew"] = computeLNHellRun(sm, False)
    hellRuns[hellRun]["Screw"] = computeLNHellRun(sm, True)

def getNearestDifficulty(difficulty):
    epsilon = 0.001
    if difficulty < medium - epsilon:
        return easy
    elif difficulty < hard - epsilon:
        return medium
    elif difficulty < harder - epsilon:
        return hard
    elif difficulty < hardcore - epsilon:
        return harder
    elif difficulty < mania - epsilon:
        return hardcore
    else:
        return mania

def computeLNHellRun(sm, addScrew):
    result = {}
    hellRun = 'LowerNorfair'
    for (actualHellRun, params) in Settings.hellRunsTable[hellRun].items():
        result[actualHellRun] = {}
        for (key, difficulties) in Settings.hellRunPresets[hellRun].items():
            if key == 'Solution':
                continue
            Settings.hellRuns[hellRun] = difficulties
            result[actualHellRun][key] = {'ETank': {easy: -1, medium: -1, hard: -1, harder: -1, hardcore: -1, mania: -1}, 'CF': {easy: -1, medium: -1, hard: -1, harder: -1, hardcore: -1, mania: -1}}
            if difficulties == None:
                continue

            for cf in range(3, 0, -1):
                sm.resetItems()
                if addScrew == True:
                    sm.addItem('ScrewAttack')
                addCF(sm, cf)
                for etank in range(19):
                    ret = sm.canHellRun(**params)

                    if ret.bool == True:
                        nEtank = 0
                        for item in ret.items:
                            if item.find('ETank') != -1:
                                nEtank = int(item[0:item.find('-ETank')])
                                break
                        result[actualHellRun][key]['ETank'][getNearestDifficulty(ret.difficulty)] = nEtank
                        result[actualHellRun][key]['CF'][getNearestDifficulty(ret.difficulty)] = cf

                    sm.addItem('ETank')
    return result

def presets():
    initPresetsSession()

    # use web2py builtin cache to avoid recomputing the hardrooms requirements
    hardRooms = cache.ram('hardRooms', lambda:dict(), time_expire=None)
    if len(hardRooms) == 0:
        computeHardRooms(hardRooms)

    hellRuns = cache.ram('hellRuns', lambda:dict(), time_expire=None)
    if len(hellRuns) == 0:
        computeHellruns(hellRuns)

    if request.vars.action is not None:
        (ok, msg) = validatePresetsParams(request.vars.action)
        if not ok:
            session.flash = msg
            redirect(URL(r=request, f='presets'))
        else:
            session.presets['currentTab'] = request.vars.currenttab

        if request.vars.action == 'Create':
            preset = request.vars.presetCreate
        else:
            preset = request.vars.preset

    # in web2py.js, in disableElement, remove 'working...' to have action with correct value
    if request.vars.action == 'Load':
        # check that the presets file exists
        fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)
        if os.path.isfile(fullPath):
            # load it
            try:
                params = PresetLoader.factory(fullPath).params
                updatePresetsSession()
                session.presets["presetDict"] = None
            except Exception as e:
                session.flash = "L:Error loading the preset {}: {}".format(preset, e)
        else:
            session.flash = "Presets file not found: {}".format(fullPath)
        redirect(URL(r=request, f='presets'))

    elif request.vars.action in ['Update', 'Create']:
        # check if the presets file already exists
        password = request.vars['password']
        password = password.encode('utf-8')
        passwordSHA256 = hashlib.sha256(password).hexdigest()
        fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)
        if os.path.isfile(fullPath):
            # load it
            end = False
            try:
                oldParams = PresetLoader.factory(fullPath).params
            except Exception as e:
                session.flash = "UC:Error loading the preset {}: {}".format(preset, e)
                end = True
            if end == True:
                redirect(URL(r=request, f='presets'))

            # check if password match
            if 'password' in oldParams and passwordSHA256 == oldParams['password']:
                # update the presets file
                paramsDict = genJsonFromParams(request.vars)
                paramsDict['password'] = passwordSHA256
                try:
                    PresetLoader.factory(paramsDict).dump(fullPath)
                    DB = db.DB()
                    DB.addPresetAction(preset, 'update')
                    DB.close()
                    updatePresetsSession()
                    session.flash = "Preset {} updated".format(preset)
                except Exception as e:
                    session.flash = "Error writing the preset {}: {}".format(preset, e)
                redirect(URL(r=request, f='presets'))
            else:
                session.flash = "Password mismatch with existing presets file {}".format(preset)
                redirect(URL(r=request, f='presets'))

        else:
            # check that there's no more than 2K presets (there's less than 2K sm rando players in the world)
            if not maxPresetsReach():
                # write the presets file
                paramsDict = genJsonFromParams(request.vars)
                paramsDict['password'] = passwordSHA256
                try:
                    PresetLoader.factory(paramsDict).dump(fullPath)
                    DB = db.DB()
                    DB.addPresetAction(preset, 'create')
                    DB.close()
                    updatePresetsSession()
                    session.flash = "Preset {} created".format(preset)
                except Exception as e:
                    session.flash = "Error writing the preset {}: {}".format(preset, e)
                redirect(URL(r=request, f='presets'))
            else:
                session.flash = "Sorry, there's already 2048 presets on the website, can't add more"
                redirect(URL(r=request, f='presets'))

    # set title
    response.title = 'Super Metroid VARIA Presets'

    # load conf from session if available
    error = False
    try:
        params = loadPreset()
    except Exception as e:
        session.presets['preset'] = 'regular'
        session.flash = "S:Error loading the preset: {}".format(e)
        error = True
    if error == True:
        redirect(URL(r=request, f='presets'))

    # load presets list
    (stdPresets, tourPresets, comPresets) = loadPresetsList()

    # add missing knows/settings
    completePreset(params)

    # compute score for skill bar
    skillBarData = getSkillLevelBarData(session.presets['preset'])

    # send values to view
    return dict(desc=Knows.desc, difficulties=diff2text,
                categories=Knows.categories, settings=params['Settings'], knows=params['Knows'],
                easy=easy, medium=medium, hard=hard, harder=harder, hardcore=hardcore, mania=mania,
                controller=params['Controller'], stdPresets=stdPresets, tourPresets=tourPresets,
                comPresets=comPresets, skillBarData=skillBarData, hardRooms=hardRooms, hellRuns=hellRuns)

def initSolverSession():
    if session.solver is None:
        session.solver = {}

        session.solver['preset'] = 'regular'
        session.solver['difficultyTarget'] = Conf.difficultyTarget
        session.solver['pickupStrategy'] = Conf.itemsPickup
        session.solver['itemsForbidden'] = []
        session.solver['romFiles'] = []
        session.solver['romFile'] = None
        session.solver['result'] = None
        session.solver['complexity'] = 'simple'

def updateSolverSession():
    if session.solver is None:
        session.solver = {}

    session.solver['preset'] = request.vars.preset
    session.solver['difficultyTarget'] = text2diff[request.vars.difficultyTarget]
    session.solver['pickupStrategy'] = request.vars.pickupStrategy
    session.solver['complexity'] = request.vars.complexity

    itemsForbidden = []
    for item in ['ETank', 'Missile', 'Super', 'PowerBomb', 'Bomb', 'Charge', 'Ice', 'HiJump', 'SpeedBooster', 'Wave', 'Spazer', 'SpringBall', 'Varia', 'Plasma', 'Grapple', 'Morph', 'Reserve', 'Gravity', 'XRayScope', 'SpaceJump', 'ScrewAttack']:
        boolvar = request.vars[item+"_bool"]
        if boolvar is not None:
            itemsForbidden.append(item)

    session.solver['itemsForbidden'] = itemsForbidden

def getROMsList():
    # filter the displayed roms to display only the ones uploaded in this session
    if session.solver['romFiles'] is None:
        session.solver['romFiles'] = []
        roms = []
    elif len(session.solver['romFiles']) == 0:
        roms = []
    else:
        files = sorted(os.listdir('roms'))
        bases = [os.path.splitext(file)[0] for file in files]
        filtered = [base for base in bases if base in session.solver['romFiles']]
        roms = ['{}.sfc'.format(file) for file in filtered]

    return roms

def getLastSolvedROM():
    if session.solver['romFile'] is not None:
        return '{}.sfc'.format(session.solver['romFile'])
    else:
        return None

def genPathTable(locations, displayAPs=True):
    if locations is None or len(locations) == 0:
        return None

    lastAP = None
    pathTable = """
<table class="full">
  <colgroup>
    <col class="locName" /><col class="area" /><col class="subarea" /><col class="item" /><col class="difficulty" /><col class="knowsUsed" /><col class="itemsUsed" />
  </colgroup>
  <tr>
    <th>Location Name</th><th>Area</th><th>SubArea</th><th>Item</th><th>Difficulty</th><th>Techniques used</th><th>Items used</th>
  </tr>
"""

    for location, area, subarea, item, diff, techniques, items, path, _class in locations:
        if path is not None:
            lastAP = path[-1]
            if displayAPs == True and not (len(path) == 1 and path[0] == lastAP):
                pathTable += """<tr class="grey"><td>Path</td><td colspan="6">{}</td></tr>\n""".format(" -&gt; ".join(path))

        (name, room) = location

        # not picked up items start with an '-'
        if item[0] != '-':
            pathTable += """
<tr class="{}">
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
</tr>
""".format(item, getRoomLink(name, room), getAreaLink(area), getSubArea(subarea),
           getBossImg(name) if "Boss" in _class else getItemImg(item), diff,
           getTechniques(techniques), getItems(items))
        else:
            pathTable += """
<tr class="{}">
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  <td><div class="linethrough">{}</div></td>
  <td>{}</td>
  <td></td>
  <td></td>
</tr>
""".format(item, getRoomLink(name, room), getAreaLink(area), getSubArea(subarea), item, diff)

    pathTable += "</table>"

    return pathTable

def getItems(items):
    ret = ""
    for item in items:
        if item[0] >= '0' and item[0] <= '9':
            # for etanks and reserves
            count = item[:item.find('-')]
            item = item[item.find('-')+1:]
            ret += "<span>{}-{}</span>".format(count, getItemImg(item, True))
        else:
            ret += getItemImg(item, True)
    return ret

def getTechniques(techniques):
    ret = ""
    for tech in techniques:
        if tech in Knows.desc and Knows.desc[tech]['href'] != None:
            ret += """ <a class="marginKnows" href="{}" target="_blank">{}</a>""".format(Knows.desc[tech]['href'], tech)
        else:
            ret += """ {}""".format(tech)
    return ret

def getRoomLink(name, room):
    roomUrl = room.replace(' ', '_').replace("'", '%27')
    roomImg = room.replace(' ', '').replace('-', '').replace("'", '')
    return """<a target="_blank" href="https://wiki.supermetroid.run/{}" data-thumbnail-src="/solver/static/images/{}.png" class="room">{}</a>""".format(roomUrl, roomImg, name)

def getAreaLink(name):
    if name == "WreckedShip":
        url = "Wrecked_Ship"
    elif name == "LowerNorfair":
        url = "Norfair"
    else:
        url = name

    return """<a target="_blank" href="https://metroid.fandom.com/wiki/{}" data-thumbnail-src="/solver/static/images/{}.png" class="area">{}</a>""".format(url, name, name)

def getSubArea(subarea):
    img = subarea.replace(' ', '')
    if img in ["Kraid", "Tourian"]:
        # kraid is already the image for kraid boss
        img += "SubArea"
    return """<span data-thumbnail-src="/solver/static/images/{}.png" class="subarea">{}</span>""".format(img, subarea)

def getBossImg(boss):
    return """<img alt="{}" class="imageBoss" src="/solver/static/images/{}.png" title="{}" />""".format(boss, boss.replace(' ', ''), boss)

def getItemImg(item, small=False):
    if small == True:
        _class = "imageItems"
    else:
        _class = "imageItem"
    return """<img alt="{}" class="{}" src="/solver/static/images/{}.png" title="{}" />""".format(item, _class, item, item)

def prepareResult():
    if session.solver['result'] is not None:
        result = session.solver['result']

        if result['difficulty'] == -1:
            result['resultText'] = "The ROM \"{}\" is not finishable with the known techniques".format(result['randomizedRom'])
        else:
            if result['itemsOk'] is False:
                result['resultText'] = "The ROM \"{}\" is finishable but not all the requested items can be picked up with the known techniques. Estimated difficulty is: ".format(result['randomizedRom'])
            else:
                result['resultText'] = "The ROM \"{}\" estimated difficulty is: ".format(result['randomizedRom'])

        # add generated path (spoiler !)
        result['pathTable'] = genPathTable(result['generatedPath'])
        result['pathremainTry'] = genPathTable(result['remainTry'])
        result['pathremainMajors'] = genPathTable(result['remainMajors'], False)
        result['pathremainMinors'] = genPathTable(result['remainMinors'], False)
        result['pathskippedMajors'] = genPathTable(result['skippedMajors'], False)
        result['pathunavailMajors'] = genPathTable(result['unavailMajors'], False)

        # display the result only once
        session.solver['result'] = None
    else:
        result = None

    return result

def validateSolverParams():
    for param in ['difficultyTarget', 'pickupStrategy', 'complexity']:
        if request.vars[param] is None:
            return (False, "Missing parameter {}".format(param))

    if request.vars.preset == None:
        return (False, "Missing parameter preset")
    preset = request.vars.preset

    if IS_ALPHANUMERIC()(preset)[1] is not None:
        return (False, "Wrong value for preset, must be alphanumeric")

    if IS_LENGTH(maxsize=32, minsize=1)(preset)[1] is not None:
        return (False, "Wrong length for preset, name must be between 1 and 32 characters")

    # check that preset exists
    fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)
    if not os.path.isfile(fullPath):
        return (False, "Unknown preset: {}".format(preset))

    difficultyTargetChoices = ["easy", "medium", "hard", "very hard", "hardcore", "mania"]
    if request.vars.difficultyTarget not in difficultyTargetChoices:
        return (False, "Wrong value for difficultyTarget: {}, authorized values: {}".format(request.vars.difficultyTarget, difficultyTargetChoices))

    pickupStrategyChoices = ["all", "minimal", "any"]
    if request.vars.pickupStrategy not in pickupStrategyChoices:
        return (False, "Wrong value for pickupStrategy: {}, authorized values: {}".format(request.vars.pickupStrategy, pickupStrategyChoice))

    complexityChoices = ["simple", "advanced"]
    if request.vars.complexity not in complexityChoices:
        return (False, "Wrong value for complexity: {}, authorized values: {}".format(request.vars.complexity, complexityChoices))

    itemsForbidden = []
    for item in ['ETank', 'Missile', 'Super', 'PowerBomb', 'Bomb', 'Charge', 'Ice', 'HiJump', 'SpeedBooster', 'Wave', 'Spazer', 'SpringBall', 'Varia', 'Plasma', 'Grapple', 'Morph', 'Reserve', 'Gravity', 'XRayScope', 'SpaceJump', 'ScrewAttack']:
        boolvar = request.vars[item+"_bool"]
        if boolvar is not None:
            if boolvar != 'on':
                return (False, "Wrong value for {}: {}, authorized values: on/off".format(item, boolvar))

    if request.vars.romJson is None and request.vars.uploadFile is None and request.vars.romFile is None:
        return (False, "Missing ROM to solve")

    if request.vars.romFile is not None:
        if IS_LENGTH(maxsize=255, minsize=1)(request.vars.romFile)[1] is not None:
            return (False, "Wrong length for romFile, name must be between 1 and 256 characters: {}".format(request.vars.romFile))

    if request.vars.romJson is not None and len(request.vars.romJson) > 0:
        try:
            json.loads(request.vars.romJson)
        except:
            return (False, "Wrong value for romJson, must be a JSON string: [{}]".format(request.vars.romJson))

    if request.vars.uploadFile is not None:
        if type(request.vars.uploadFile) == str:
            if IS_MATCH('[a-zA-Z0-9_\.() ,\-]*', strict=True)(request.vars.uploadFile)[1] is not None:
                return (False, "Wrong value for uploadFile, must be a valid file name: {}".format(request.vars.uploadFile))

            if IS_LENGTH(maxsize=256, minsize=1)(request.vars.uploadFile)[1] is not None:
                return (False, "Wrong length for uploadFile, name must be between 1 and 255 characters")

    return (True, None)

def generateJsonROM(romJsonStr):
    tempRomJson = json.loads(romJsonStr)
    romFileName = tempRomJson["romFileName"]
    (base, ext) = os.path.splitext(romFileName)
    jsonRomFileName = 'roms/{}.json'.format(base)
    del tempRomJson["romFileName"]

    with open(jsonRomFileName, 'w') as jsonFile:
        json.dump(tempRomJson, jsonFile)

    return (base, jsonRomFileName)

def solver():
    # init session
    initSolverSession()

    if request.vars.action == 'Solve':
        (ok, msg) = validateSolverParams()
        if not ok:
            session.flash = msg
            redirect(URL(r=request, f='solver'))

        updateSolverSession()

        preset = request.vars.preset

        # new uploaded rom ?
        error = False
        if request.vars['romJson'] != '':
            try:
                (base, jsonRomFileName) = generateJsonROM(request.vars['romJson'])
                session.solver['romFile'] = base
                if base not in session.solver['romFiles']:
                    session.solver['romFiles'].append(base)
            except Exception as e:
                print("Error loading the ROM file, exception: {}".format(e))
                session.flash = "Error loading the json ROM file"
                error = True

        elif request.vars['romFile'] is not None and len(request.vars['romFile']) != 0:
            session.solver['romFile'] = os.path.splitext(request.vars['romFile'])[0]
            jsonRomFileName = 'roms/' + session.solver['romFile'] + '.json'
        else:
            session.flash = "No rom file selected for upload"
            error = True

        if not error:
            # check that the json file exists
            if not os.path.isfile(jsonRomFileName):
                session.flash = "Missing json ROM file on the server"
            else:
                try:
                    (ok, result) = computeDifficulty(jsonRomFileName, preset)
                    if not ok:
                        session.flash = result
                        redirect(URL(r=request, f='solver'))
                    session.solver['result'] = result
                except Exception as e:
                    print("Error loading the ROM file, exception: {}".format(e))
                    session.flash = "Error loading the ROM file"

        redirect(URL(r=request, f='solver'))

    # display result
    result = prepareResult()

    # set title
    response.title = 'Super Metroid VARIA Solver'

    ROMs = getROMsList()

    # last solved ROM
    lastRomFile = getLastSolvedROM()

    # load presets list
    (stdPresets, tourPresets, comPresets) = loadPresetsList()

    # generate list of addresses to read in the ROM
    addresses = getAddressesToRead()

    # send values to view
    return dict(desc=Knows.desc, stdPresets=stdPresets, tourPresets=tourPresets, comPresets=comPresets, roms=ROMs,
                lastRomFile=lastRomFile, difficulties=diff2text, categories=Knows.categories,
                result=result, addresses=addresses,
                easy=easy, medium=medium, hard=hard, harder=harder, hardcore=hardcore, mania=mania)

def getAddressesToRead(plando=False):
    addresses = {"locations": [], "patches": [], "transitions": [], "misc": [], "ranges": []}

    # locations
    for loc in locations:
        addresses["locations"].append(loc["Address"])

    # patches
    for (patch, values) in RomReader.patches.items():
        addresses["patches"].append(values["address"])

    # transitions
    for ap in accessPoints:
        if ap.Internal == True:
            continue
        addresses["transitions"].append(0x10000 | ap.ExitInfo['DoorPtr'])

    # misc
    # majors split
    addresses["misc"].append(0x17B6C)
    # escape timer
    addresses["misc"].append(0x1E21)
    addresses["misc"].append(0x1E22)
    # nothing id
    addresses["misc"].append(0x17B6D)
    # start ap
    addresses["misc"].append(0x10F200)
    addresses["misc"].append(0x10F201)

    # ranges [low, high]
    ## doorasm
    addresses["ranges"] += [0x7EB00, 0x7ee60]
    # for next release doorasm addresses will be relocated
    addresses["ranges"] += [0x7F800, 0x7FA5F]

    if plando == True:
        # plando addresses
        addresses["ranges"] += [0x2F6000, 0x2F6100]
        # plando transitions (4 bytes per transitions, ap#/2 transitions)
        addresses["ranges"] += [0x2F6100, 0x2F6100+((len(addresses["transitions"])/2) * 4)]

    return addresses

def genJsonFromParams(vars):
    paramsDict = {'Knows': {}, 'Settings': {}, 'Controller': {}}

    # Knows
    for var in Knows.__dict__:
        if isKnows(var):
            boolVar = vars[var+"_bool"]
            if boolVar is None:
                paramsDict['Knows'][var] = [False, 0]
            else:
                diffVar = vars[var+"_diff"]
                if diffVar is not None:
                    paramsDict['Knows'][var] = [True, text2diff[diffVar]]

    # Settings
    for hellRun in ['Ice', 'MainUpperNorfair', 'LowerNorfair']:
        value = vars[hellRun]
        if value is not None:
            paramsDict['Settings'][hellRun] = value

    for boss in ['Kraid', 'Phantoon', 'Draygon', 'Ridley', 'MotherBrain']:
        value = vars[boss]
        if value is not None:
            paramsDict['Settings'][boss] = value

    for room in ['X-Ray', 'Gauntlet']:
        value = vars[room]
        if value is not None:
            paramsDict['Settings'][room] = value

    # Controller
    for button in Controller.__dict__:
        if isButton(button):
            value = vars[button]
            if value is None:
                paramsDict['Controller'][button] = Controller.__dict__[button]
            else:
                if button == "Moonwalk":
                    if value != None and value == "on":
                        paramsDict['Controller'][button] = True
                    else:
                        paramsDict['Controller'][button] = False
                else:
                    paramsDict['Controller'][button] = value

    return paramsDict

def computeDifficulty(jsonRomFileName, preset):
    randomizedRom = os.path.basename(jsonRomFileName.replace('json', 'sfc'))

    presetFileName = "{}/{}.json".format(getPresetDir(preset), preset)
    (fd, jsonFileName) = tempfile.mkstemp()

    DB = db.DB()
    id = DB.initSolver()

    params = [
        pythonExec,  os.path.expanduser("~/RandomMetroidSolver/solver.py"),
        '-r', str(jsonRomFileName),
        '--preset', presetFileName,
        '--difficultyTarget', str(session.solver['difficultyTarget']),
        '--pickupStrategy', session.solver['pickupStrategy'],
        '--type', 'web',
        '--output', jsonFileName
    ]

    for item in session.solver['itemsForbidden']:
        params += ['--itemsForbidden', item]

    DB.addSolverParams(id, randomizedRom, preset, session.solver['difficultyTarget'],
                       session.solver['pickupStrategy'], session.solver['itemsForbidden'])

    print("before calling solver: {}".format(params))
    start = datetime.now()
    ret = subprocess.call(params)
    end = datetime.now()
    duration = (end - start).total_seconds()
    print("ret: {}, duration: {}s".format(ret, duration))

    if ret == 0:
        with open(jsonFileName) as jsonFile:
            result = json.load(jsonFile)
    else:
        result = "Solver: something wrong happened while solving the ROM"

    DB.addSolverResult(id, ret, duration, result)
    DB.close()

    os.close(fd)
    os.remove(jsonFileName)

    return (ret == 0, result)

def infos():
    # set title
    response.title = 'Super Metroid VARIA Randomizer and Solver'

    return dict()

def initRandomizerSession():
    if session.randomizer is None:
        session.randomizer = {}

        session.randomizer['complexity'] = "simple"
        session.randomizer['preset'] = 'regular'
        session.randomizer['randoPreset'] = ""
        session.randomizer['majorsSplit'] = "Full"
        session.randomizer['startLocation'] = "Landing Site"
        session.randomizer['maxDifficulty'] = 'hardcore'
        session.randomizer['progressionSpeed'] = "medium"
        session.randomizer['progressionDifficulty'] = 'normal'
        session.randomizer['morphPlacement'] = "early"
        session.randomizer['suitsRestriction'] = "on"
        session.randomizer['hideItems'] = "off"
        session.randomizer['strictMinors'] = "off"
        session.randomizer['missileQty'] = "3"
        session.randomizer['superQty'] = "2"
        session.randomizer['powerBombQty'] = "1"
        session.randomizer['minorQty'] = "100"
        session.randomizer['energyQty'] = "vanilla"
        session.randomizer['areaRandomization'] = "off"
        session.randomizer['areaLayout'] = "off"
        session.randomizer['escapeRando'] = "off"
        session.randomizer['removeEscapeEnemies'] = "off"
        session.randomizer['bossRandomization'] = "off"
        session.randomizer['funCombat'] = "off"
        session.randomizer['funMovement'] = "off"
        session.randomizer['funSuits'] = "off"
        session.randomizer['layoutPatches'] = "on"
        session.randomizer['variaTweaks'] = "on"
        session.randomizer['gravityBehaviour'] = "Balanced"
        session.randomizer['nerfedCharge'] = "off"
        session.randomizer['itemsounds'] = "on"
        session.randomizer['elevators_doors_speed'] = "on"
        session.randomizer['spinjumprestart'] = "off"
        session.randomizer['rando_speed'] = "off"
        session.randomizer['animals'] = "off"
        session.randomizer['No_Music'] = "off"

def randomizer():
    response.title = 'Super Metroid VARIA Randomizer'

    initRandomizerSession()

    (stdPresets, tourPresets, comPresets) = loadPresetsList()
    (randoPresets, tourRandoPresets) = loadRandoPresetsList()
    # add empty entry for default value
    randoPresets.append("")

    startAPs = GraphUtils.getStartAccessPointNamesCategory()
    startAPs = [OPTGROUP(_label="Standard", *startAPs["regular"]),
                OPTGROUP(_label="Custom", *startAPs["custom"]),
                OPTGROUP(_label="Custom (Area rando only)", *startAPs["area"])]

    return dict(stdPresets=stdPresets, tourPresets=tourPresets, comPresets=comPresets,
                randoPresets=randoPresets, tourRandoPresets=tourRandoPresets,
                startAPs=startAPs)

def raiseHttp(code, msg, isJson=False):
    #print("raiseHttp: code {} msg {} isJson {}".format(code, msg, isJson))
    if isJson is True:
        msg = json.dumps(msg)

    raise HTTP(code, msg)

def getInt(param, isJson=False):
    try:
        return int(request.vars[param])
    except:
        raiseHttp(400, "Wrong value for {}: {}, must be an int".format(param, request.vars[param]), isJson)

def getFloat(param, isJson=False):
    try:
        return float(request.vars[param])
    except:
        raiseHttp(400, "Wrong value for {}: {}, must be a float".format(param, request.vars[param]), isJson)

def validateWebServiceParams(switchs, quantities, others, isJson=False):
    parameters = switchs + quantities + others

    for param in parameters:
        if request.vars[param] is None:
            raiseHttp(400, "Missing parameter: {}".format(param), isJson)

    for switch in switchs:
        if request.vars[switch] not in ['on', 'off', 'random']:
            raiseHttp(400, "Wrong value for {}: {}, authorized values: on/off".format(switch, request.vars[switch]), isJson)

    for qty in quantities:
        if request.vars[qty] == 'random':
            continue
        qtyFloat = getFloat(qty, isJson)
        if qtyFloat < 1.0 or qtyFloat > 9.0:
            raiseHttp(400, json.dumps("Wrong value for {}: {}, must be between 1 and 9".format(qty, request.vars[qty])), isJson)

    if 'complexity' in others:
        if request.vars['complexity'] not in ['simple', 'medium', 'advanced']:
            raiseHttp(400, "Wrong value for complexity: {}, authorized values simple/medium/advanced".format(request.vars['complexity']), isJson)

    if 'paramsFileTarget' in others:
        try:
            json.loads(request.vars.paramsFileTarget)
        except:
            raiseHttp(400, "Wrong value for paramsFileTarget, must be a JSON string", isJson)

    if 'seed' in others:
        seedInt = getInt('seed', isJson)
        if seedInt < 0 or seedInt > 9999999:
            raiseHttp(400, "Wrong value for seed: {}, must be between 0 and 9999999".format(request.vars[seed]), isJson)

    preset = request.vars.preset
    if preset != None:
        if IS_ALPHANUMERIC()(preset)[1] is not None:
            raiseHttp(400, "Wrong value for preset, must be alphanumeric", isJson)

        if IS_LENGTH(maxsize=32, minsize=1)(preset)[1] is not None:
            raiseHttp(400, "Wrong length for preset, name must be between 1 and 32 characters", isJson)

        # check that preset exists
        fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)
        if not os.path.isfile(fullPath):
            raiseHttp(400, "Unknown preset: {}".format(preset), isJson)

    randoPreset = request.vars.randoPreset
    if randoPreset != None and len(randoPreset) > 0:
        if IS_ALPHANUMERIC()(randoPreset)[1] is not None:
            raiseHttp(400, "Wrong value for randoPreset, must be alphanumeric", isJson)

        if IS_LENGTH(maxsize=32, minsize=1)(randoPreset)[1] is not None:
            raiseHttp(400, "Wrong length for randoPreset, name must be between 1 and 32 characters", isJson)

        # check that randoPreset exists
        fullPath = 'rando_presets/{}.json'.format(randoPreset)
        if not os.path.isfile(fullPath):
            raiseHttp(400, "Unknown randoPreset: {}".format(randoPreset), isJson)

    # check race mode
    if 'raceMode' in request.vars:
        if request.vars.raceMode not in ['on', 'off']:
            raiseHttp(400, "Wrong value for race mode: {}, must on/off".format(request.vars.raceMode), isJson)

    if 'majorsSplit' in others:
        if request.vars['majorsSplit'] not in ['Full', 'Major', 'Chozo', 'random']:
            raiseHttp(400, "Wrong value for majorsSplit: {}, authorized values Full/Major/Chozo/random".format(request.vars['majorsSplit']), isJson)

    if request.vars['maxDifficulty'] is not None:
        if request.vars.maxDifficulty not in ['no difficulty cap', 'easy', 'medium', 'hard', 'harder', 'hardcore', 'mania', 'random']:
            raiseHttp(400, "Wrong value for difficulty_target, authorized values: no difficulty cap/easy/medium/hard/harder/hardcore/mania", isJson)

    if 'progressionSpeed' in others:
        for progSpeed in request.vars['progressionSpeed'].split(','):
            if progSpeed not in ['slowest', 'slow', 'medium', 'fast', 'fastest', 'random', 'basic', 'VARIAble']:
                raiseHttp(400, "Wrong value for progressionSpeed: {}, authorized values slowest/slow/medium/fast/fastest/basic/VARIAble".format(progSpeed), isJson)

    if 'progressionDifficulty' in others:
        if request.vars['progressionDifficulty'] not in ['easier', 'normal', 'harder', 'random']:
            raiseHttp(400, "Wrong value for progressionDifficulty: {}, authorized values easier/normal/harder".format(request.vars['progressionDifficulty']), isJson)

    if 'morphPlacement' in others:
        if request.vars['morphPlacement'] not in ['early', 'late', 'normal', 'classic', 'random']:
            raiseHttp(400, "Wrong value for morphPlacement: {}, authorized values early/late/normal/classic".format(request.vars['morphPlacement']), isJson)

    if request.vars.minorQty not in ['random', None]:
        minorQtyInt = getInt('minorQty', isJson)
        if minorQtyInt < 7 or minorQtyInt > 100:
            raiseHttp(400, "Wrong value for minorQty, must be between 7 and 100", isJson)

    if 'energyQty' in others:
        if request.vars.energyQty not in ['sparse', 'medium', 'vanilla', 'random']:
            raiseHttp(400, "Wrong value for energyQty: authorized values: sparse/medium/vanilla", isJson)

    if 'gravityBehaviour' in others:
        if request.vars.gravityBehaviour not in ['Balanced', 'Progressive', 'Vanilla']:
            raiseHttp(400, "Wrong value for gravityBehaviour: {}".format(request.vars.gravityBehaviour), isJson)

    if 'startLocation' in others:
        if request.vars.startLocation not in GraphUtils.getStartAccessPointNames() + ['random']:
            raiseHttp(400, "Wrong value for startLocation: {}".format(request.vars.startLocation), isJson)

def sessionWebService():
    # web service to update the session
    switchs = ['suitsRestriction', 'hideItems', 'strictMinors',
               'areaRandomization', 'areaLayout', 'escapeRando', 'removeEscapeEnemies',
               'bossRandomization',
               'funCombat', 'funMovement', 'funSuits',
               'layoutPatches', 'variaTweaks', 'nerfedCharge',
               'itemsounds', 'elevators_doors_speed', 'spinjumprestart',
               'rando_speed', 'animals', 'No_Music']
    quantities = ['missileQty', 'superQty', 'powerBombQty']
    others = ['complexity', 'preset', 'randoPreset', 'majorsSplit',
              'maxDifficulty', 'progressionSpeed', 'progressionDifficulty',
              'morphPlacement', 'minorQty', 'energyQty',
              'gravityBehaviour', 'startLocation']
    validateWebServiceParams(switchs, quantities, others)

    if session.randomizer is None:
        session.randomizer = {}

    session.randomizer['complexity'] = request.vars.complexity
    session.randomizer['preset'] = request.vars.preset
    session.randomizer['randoPreset'] = request.vars.randoPreset
    session.randomizer['majorsSplit'] = request.vars.majorsSplit
    session.randomizer['startLocation'] = request.vars.startLocation
    session.randomizer['maxDifficulty'] = request.vars.maxDifficulty
    session.randomizer['progressionSpeed'] = request.vars.progressionSpeed.split(',')
    session.randomizer['progressionDifficulty'] = request.vars.progressionDifficulty
    session.randomizer['morphPlacement'] = request.vars.morphPlacement
    session.randomizer['suitsRestriction'] = request.vars.suitsRestriction
    session.randomizer['hideItems'] = request.vars.hideItems
    session.randomizer['strictMinors'] = request.vars.strictMinors
    session.randomizer['missileQty'] = request.vars.missileQty
    session.randomizer['superQty'] = request.vars.superQty
    session.randomizer['powerBombQty'] = request.vars.powerBombQty
    session.randomizer['minorQty'] = request.vars.minorQty
    session.randomizer['energyQty'] = request.vars.energyQty
    session.randomizer['areaRandomization'] = request.vars.areaRandomization
    session.randomizer['areaLayout'] = request.vars.areaLayout
    session.randomizer['escapeRando'] = request.vars.escapeRando
    session.randomizer['removeEscapeEnemies'] = request.vars.removeEscapeEnemies
    session.randomizer['bossRandomization'] = request.vars.bossRandomization
    session.randomizer['funCombat'] = request.vars.funCombat
    session.randomizer['funMovement'] = request.vars.funMovement
    session.randomizer['funSuits'] = request.vars.funSuits
    session.randomizer['layoutPatches'] = request.vars.layoutPatches
    session.randomizer['variaTweaks'] = request.vars.variaTweaks
    session.randomizer['gravityBehaviour'] = request.vars.gravityBehaviour
    session.randomizer['nerfedCharge'] = request.vars.nerfedCharge
    session.randomizer['itemsounds'] = request.vars.itemsounds
    session.randomizer['elevators_doors_speed'] = request.vars.elevators_doors_speed
    session.randomizer['spinjumprestart'] = request.vars.spinjumprestart
    session.randomizer['rando_speed'] = request.vars.rando_speed
    session.randomizer['animals'] = request.vars.animals
    session.randomizer['No_Music'] = request.vars.No_Music

    # to create a new rando preset, uncomment next lines
    #with open('rando_presets/new.json', 'w') as jsonFile:
    #    json.dump(session.randomizer, jsonFile)

def getCustomMapping(controlMapping):
    if len(controlMapping) == 0:
        return (False, None)

    inv = {}
    for button in controlMapping:
        inv[controlMapping[button]] = button

    return (True, "{},{},{},{},{},{},{}".format(inv["Shoot"], inv["Jump"], inv["Dash"], inv["Item Select"], inv["Item Cancel"], inv["Angle Up"], inv["Angle Down"]))

def randomizerWebService():
    # web service to compute a new random (returns json string)
    print("randomizerWebService")

    session.forget(response)

    # set header to authorize cross domain AJAX
    response.headers['Access-Control-Allow-Origin'] = '*'

    # check validity of all parameters
    switchs = ['suitsRestriction', 'hideItems', 'strictMinors',
               'areaRandomization', 'areaLayout', 'escapeRando', 'removeEscapeEnemies',
               'bossRandomization',
               'funCombat', 'funMovement', 'funSuits',
               'layoutPatches', 'variaTweaks', 'nerfedCharge',
               'itemsounds', 'elevators_doors_speed', 'spinjumprestart',
               'rando_speed', 'animals', 'No_Music']
    quantities = ['missileQty', 'superQty', 'powerBombQty']
    others = ['complexity', 'paramsFileTarget', 'seed', 'preset', 'majorsSplit',
              'maxDifficulty', 'progressionSpeed', 'progressionDifficulty',
              'morphPlacement', 'minorQty', 'energyQty',
              'gravityBehaviour', 'startLocation']
    validateWebServiceParams(switchs, quantities, others, isJson=True)

    # randomize
    DB = db.DB()
    id = DB.initRando()

    # race mode
    useRace = False
    if request.vars.raceMode == 'on':
        magic = getMagic()
        useRace = True

    (fd1, presetFileName) = tempfile.mkstemp()
    presetFileName += '.json'
    (fd2, jsonFileName) = tempfile.mkstemp()

    print("randomizerWebService, params validated")
    for var in request.vars:
        print("{}: {}".format(var, request.vars[var]))

    with open(presetFileName, 'w') as presetFile:
        presetFile.write(request.vars.paramsFileTarget)

    seed = request.vars.seed
    if seed == '0':
        seed = str(random.randint(0, 9999999))

    preset = request.vars.preset

    params = [pythonExec,  os.path.expanduser("~/RandomMetroidSolver/randomizer.py"),
              '--runtime', '20',
              '--seed', seed,
              '--output', jsonFileName,
              '--param', presetFileName,
              '--preset', preset,
              '--progressionSpeed', request.vars.progressionSpeed,
              '--progressionDifficulty', request.vars.progressionDifficulty,
              '--morphPlacement', request.vars.morphPlacement,
              '--majorsSplit', request.vars.majorsSplit,
              '--startAP', request.vars.startLocation]
    params += ['--missileQty', request.vars.missileQty if request.vars.missileQty != 'random' else '0',
               '--superQty', request.vars.superQty if request.vars.superQty != 'random' else '0',
               '--powerBombQty', request.vars.powerBombQty if request.vars.powerBombQty != 'random' else '0',
               '--minorQty', request.vars.minorQty if request.vars.minorQty != 'random' else '0',
               '--energyQty', request.vars.energyQty]

    if useRace == True:
        params += ['--race', str(magic)]

    if request.vars.nerfedCharge == 'on':
        params.append('--nerfedCharge')

    if request.vars.itemsounds == 'on':
        params += ['-c', 'itemsounds.ips']
    if request.vars.elevators_doors_speed == 'on':
        params += ['-c', 'elevators_doors_speed.ips']
    if request.vars.spinjumprestart == 'on':
        params += ['-c', 'spinjumprestart.ips']
    if request.vars.rando_speed == 'on':
        params += ['-c', 'rando_speed.ips']
    if request.vars.No_Music == 'on':
        params += ['-c', 'No_Music']

    if request.vars.animals == 'on':
        params.append('--animals')
    if request.vars.variaTweaks == 'off':
        params.append('--novariatweaks')

    if request.vars.maxDifficulty != 'no difficulty cap':
        params.append('--maxDifficulty')
        params.append(request.vars.maxDifficulty)

    def addParamRandom(id, params):
        if request.vars[id] in ['on', 'random']:
            params.append('--{}'.format(id))
        if request.vars[id] == 'random':
            params.append('random')

    addParamRandom('suitsRestriction', params)
    addParamRandom('hideItems', params)
    addParamRandom('strictMinors', params)

    def addSuperFun(id, params):
        fun = id[len('fun'):]
        if request.vars[id] == 'on':
            params += ['--superFun', fun]
        elif request.vars[id] == 'random':
            params += ['--superFun', "{}Random".format(fun)]

    addSuperFun('funCombat', params)
    addSuperFun('funMovement', params)
    addSuperFun('funSuits', params)

    if request.vars.layoutPatches == 'off':
        params.append('--nolayout')


    if request.vars.gravityBehaviour == 'Vanilla':
        params.append('--nogravheat')
    elif request.vars.gravityBehaviour == 'Progressive':
        params.append('--progressiveSuits')

    if request.vars.areaRandomization == 'on':
        params.append('--area')
        if request.vars.areaLayout == 'off':
            params.append('--areaLayoutBase')
        if request.vars.escapeRando == 'off':
            params.append('--noEscapeRando')
        if request.vars.removeEscapeEnemies == 'off':
            params.append('--noRemoveEscapeEnemies')
    elif request.vars.areaRandomization == 'random':
        params += ['--area', 'random']

    if request.vars.bossRandomization == 'on':
        params.append('--bosses')
    elif request.vars.bossRandomization == 'random':
        params += ['--bosses', 'random']

    # load content of preset to get controller mapping
    try:
        controlMapping = PresetLoader.factory(presetFileName).params['Controller']
    except Exception as e:
        os.close(fd1)
        os.remove(presetFileName)
        os.close(fd2)
        os.remove(jsonFileName)
        raise HTTP(400, json.dumps("randomizerWebService: can't load the preset"))

    (custom, controlParam) = getCustomMapping(controlMapping)
    if custom == True:
        params += ['--controls', controlParam]
        if "Moonwalk" in controlMapping and controlMapping["Moonwalk"] == True:
            params.append('--moonwalk')

    DB.addRandoParams(id, params + ['--complexity', request.vars.complexity])

    print("before calling: {}".format(params))
    start = datetime.now()
    ret = subprocess.call(params)
    end = datetime.now()
    duration = (end - start).total_seconds()
    print("ret: {}, duration: {}s".format(ret, duration))

    if ret == 0:
        with open(jsonFileName) as jsonFile:
            locsItems = json.load(jsonFile)

        # check if an info message has been returned
        msg = ''
        if len(locsItems['errorMsg']) > 0:
            msg = locsItems['errorMsg']
            if msg[0] == '\n':
                msg = msg[1:]
            locsItems['errorMsg'] = msg.replace('\n', '<br/>')

        DB.addRandoResult(id, ret, duration, msg)
        DB.close()

        os.close(fd1)
        os.remove(presetFileName)
        os.close(fd2)
        os.remove(jsonFileName)

        return json.dumps(locsItems)
    else:
        # extract error from json
        try:
            with open(jsonFileName) as jsonFile:
                msg = json.load(jsonFile)['errorMsg']
                if msg[0] == '\n':
                    msg = msg[1:]
                    msg = msg.replace('\n', '<br/>')
        except:
            msg = "randomizerWebService: something wrong happened"

        DB.addRandoResult(id, ret, duration, msg)
        DB.close()

        os.close(fd1)
        os.remove(presetFileName)
        os.close(fd2)
        os.remove(jsonFileName)
        raise HTTP(400, json.dumps(msg))

def presetWebService():
    # web service to get the content of the preset file
    if request.vars.preset == None:
        raiseHttp(400, "Missing parameter preset")
    preset = request.vars.preset

    if IS_ALPHANUMERIC()(preset)[1] is not None:
        raise HTTP(400, "Preset name must be alphanumeric")

    if IS_LENGTH(maxsize=32, minsize=1)(preset)[1] is not None:
        raise HTTP(400, "Preset name must be between 1 and 32 characters")

    print("presetWebService: preset={}".format(preset))

    fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)

    # check that the presets file exists
    if os.path.isfile(fullPath):
        # load it
        try:
            params = PresetLoader.factory(fullPath).params
        except Exception as e:
            raise HTTP(400, "Can't load the preset")
        params = json.dumps(params)
        return params
    else:
        raise HTTP(400, "Preset '{}' not found".format(fullPath))

def randoPresetWebService():
    # web service to get the content of the rando preset file
    if request.vars.randoPreset == None:
        raiseHttp(400, "Missing parameter rando preset")
    preset = request.vars.randoPreset

    if IS_ALPHANUMERIC()(preset)[1] is not None:
        raise HTTP(400, "Preset name must be alphanumeric")

    if IS_LENGTH(maxsize=32, minsize=1)(preset)[1] is not None:
        raise HTTP(400, "Preset name must be between 1 and 32 characters")

    if request.vars.origin not in ["extStats", "randomizer"]:
        raise HTTP(400, "Unknown origin")

    print("randoPresetWebService: preset={}".format(preset))

    fullPath = 'rando_presets/{}.json'.format(preset)

    # check that the presets file exists
    if os.path.isfile(fullPath):
        # load it
        try:
            updateSession = request.vars.origin == "randomizer"

            params = loadRandoPreset(fullPath, updateSession)
            if updateSession == True:
                session.randomizer['randoPreset'] = preset
            params = json.dumps(params)
            return params
        except Exception as e:
            raise HTTP(400, "Can't load the rando preset: {}".format(preset))
    else:
        raise HTTP(400, "Rando preset '{}' not found".format(fullPath))

def loadRandoPreset(presetFullPath, updateSession):
    with open(presetFullPath) as jsonFile:
        randoPreset = json.load(jsonFile)

    if updateSession == True:
        # update session
        for key in randoPreset:
            session.randomizer[key] = randoPreset[key]

    return randoPreset

def home():
    # set title
    response.title = 'Super Metroid VARIA Randomizer, Solver and Trackers'

    return dict()

def getErrors():
    # check dir exists
    errDir = os.path.expanduser("~/web2py/applications/solver/errors")
    if os.path.isdir(errDir):
        # list error files
        errFiles = glob.glob(os.path.join(errDir, "*"))

        # sort by date
        errFiles.sort(key=os.path.getmtime)
        errFiles = [os.path.basename(f) for f in errFiles]
        return errFiles
    else:
        return []

def getFsUsage():
    fsData = os.statvfs('/home')
    percent = round(100 - (100.0 * fsData.f_bavail / fsData.f_blocks), 2)
    if percent < 80:
        return ('OK', percent)
    elif percent < 95:
        return ('WARNING', percent)
    else:
        return ('CRITICAL', percent)

def randoParamsWebService():
    # get a string of the randomizer parameters for a given seed
    if request.vars.seed == None:
        raiseHttp(400, "Missing parameter seed", False)

    seed = getInt('seed', False)
    if seed < 0 or seed > 9999999:
        raiseHttp(400, "Wrong value for seed: {}, must be between 0 and 9999999".format(request.vars[seed]), False)

    DB = db.DB()
    params = DB.getRandomizerSeedParams(seed)
    DB.close()

    return params

def stats():
    response.title = 'Super Metroid VARIA Randomizer and Solver usage statistics'

    DB = db.DB()
    weeks = 1

    solverPresets = DB.getSolverPresets(weeks)
    randomizerPresets = DB.getRandomizerPresets(weeks)

    solverDurations = DB.getSolverDurations(weeks)
    randomizerDurations = DB.getRandomizerDurations(weeks)

    solverData = DB.getSolverData(weeks)
    randomizerData = DB.getRandomizerData(weeks)

    isolver = DB.getISolver(weeks)
    isolverData = DB.getISolverData(weeks)

    errors = getErrors()

    DB.close()

    (fsStatus, fsPercent) = getFsUsage()

    return dict(solverPresets=solverPresets, randomizerPresets=randomizerPresets,
                solverDurations=solverDurations, randomizerDurations=randomizerDurations,
                solverData=solverData, randomizerData=randomizerData,
                isolver=isolver, isolverData=isolverData, errors=errors,
                fsStatus=fsStatus, fsPercent=fsPercent)

def transition2isolver(transition):
    transition = str(transition)
    return transition[0].lower() + removeChars(transition[1:], " ,()-")

def tracker():
    response.title = 'Super Metroid VARIA Areas and Items Tracker'

    # init session
    if session.tracker is None:
        session.tracker = {}

        session.tracker["state"] = {}
        session.tracker["preset"] = "regular"
        session.tracker["seed"] = None
        session.tracker["startLocation"] = "Landing Site"

        # set to False in tracker.html
        session.tracker["firstTime"] = True

    # load presets list
    (stdPresets, tourPresets, comPresets) = loadPresetsList()

    # access points
    vanillaAPs = []
    for (src, dest) in vanillaTransitions:
        vanillaAPs += [transition2isolver(src), transition2isolver(dest)]

    vanillaBossesAPs = []
    for (src, dest) in vanillaBossesTransitions:
        vanillaBossesAPs += [transition2isolver(src), transition2isolver(dest)]

    escapeAPs = []
    for (src, dest) in vanillaEscapeTransitions:
        escapeAPs += [transition2isolver(src), transition2isolver(dest)]

    # generate list of addresses to read in the ROM
    addresses = getAddressesToRead()

    startAPs = GraphUtils.getStartAccessPointNamesCategory()
    startAPs = [OPTGROUP(_label="Standard", *startAPs["regular"]),
                OPTGROUP(_label="Custom", *startAPs["custom"]),
                OPTGROUP(_label="Custom (Area rando only)", *startAPs["area"])]

    return dict(stdPresets=stdPresets, tourPresets=tourPresets, comPresets=comPresets,
                vanillaAPs=vanillaAPs, vanillaBossesAPs=vanillaBossesAPs, escapeAPs=escapeAPs,
                curSession=session.tracker, addresses=addresses, startAPs=startAPs)

def plando():
    response.title = 'Super Metroid VARIA Areas and Items Plandomizer'

    # init session
    if session.plando is None:
        session.plando = {}

        session.plando["state"] = {}
        session.plando["preset"] = "regular"
        session.plando["seed"] = None
        session.plando["startLocation"] = "Landing Site"

        # rando params
        session.plando["rando"] = {}

        # set to False in plando.html
        session.plando["firstTime"] = True

    # load presets list
    (stdPresets, tourPresets, comPresets) = loadPresetsList()

    # access points
    vanillaAPs = []
    for (src, dest) in vanillaTransitions:
        vanillaAPs += [transition2isolver(src), transition2isolver(dest)]

    vanillaBossesAPs = []
    for (src, dest) in vanillaBossesTransitions:
        vanillaBossesAPs += [transition2isolver(src), transition2isolver(dest)]

    escapeAPs = []
    for (src, dest) in vanillaEscapeTransitions:
        escapeAPs += [transition2isolver(src), transition2isolver(dest)]

    # generate list of addresses to read in the ROM
    addresses = getAddressesToRead(plando=True)

    startAPs = GraphUtils.getStartAccessPointNamesCategory()
    startAPs = [OPTGROUP(_label="Standard", *startAPs["regular"]),
                OPTGROUP(_label="Custom", *startAPs["custom"]),
                OPTGROUP(_label="Custom (Area rando only)", *startAPs["area"])]

    return dict(stdPresets=stdPresets, tourPresets=tourPresets, comPresets=comPresets,
                vanillaAPs=vanillaAPs, vanillaBossesAPs=vanillaBossesAPs, escapeAPs=escapeAPs,
                curSession=session.plando, addresses=addresses, startAPs=startAPs)

class WS(object):
    @staticmethod
    def factory():
        scope = request.vars.scope
        if scope not in ["area", "item", "common"]:
            raiseHttp(400, "Unknown scope: {}, must be area/item/common".format(scope), True)

        action = request.vars.action
        if action not in ['add', 'remove', 'clear', 'init', 'get', 'save', 'replace', 'randomize']:
            raiseHttp(400, "Unknown action {}, must be add/remove/clear/init/get/save/randomize".format(action), True)

        mode = request.vars.mode
        if mode not in ["standard", "seedless", "plando"]:
            raiseHttp(400, "Unknown mode, must be standard/seedless/plando", True)

        try:
            WSClass = globals()["WS_{}_{}".format(scope, action)]
            return WSClass(mode)
        except Exception as e:
            raiseHttp(400, "{}".format(e.body if "body" in e.__dict__ else e).replace('"', ''), True)

    def __init__(self, mode):
        if mode == "plando":
            if session.plando is None:
                raiseHttp(400, "No session found for the Plandomizer Web service", True)
            self.session = session.plando
        else:
            if session.tracker is None:
                raiseHttp(400, "No session found for the Tracker Web service", True)
            self.session = session.tracker

    def validate(self):
        if self.session is None:
            raiseHttp(400, "No session found for the Tracker", True)

        if request.vars.action == None:
            raiseHttp(400, "Missing parameter action", True)
        action = request.vars.action

        if action not in ['init', 'add', 'remove', 'clear', 'get', 'save', 'replace', 'randomize']:
            raiseHttp(400, "Unknown action {}, must be init/add/remove/clear/get/save/randomize".format(action), True)

        if request.vars.escapeTimer != None:
            if re.match("[0-9][0-9]:[0-9][0-9]", request.vars.escapeTimer) == None:
                raiseHttp(400, "Wrong escape timer value")

    def validatePoint(self, point):
        if request.vars[point] == None:
            raiseHttp(400, "Missing parameter {}".format(point), True)

        pointValue = request.vars[point]

        if pointValue not in ['lowerMushroomsLeft', 'moatRight', 'greenPiratesShaftBottomRight',
                              'keyhunterRoomBottom', 'morphBallRoomLeft', 'greenBrinstarElevator',
                              'greenHillZoneTopRight', 'noobBridgeRight', 'westOceanLeft', 'crabMazeLeft',
                              'lavaDiveRight', 'threeMuskateersRoomLeft', 'warehouseZeelaRoomLeft',
                              'warehouseEntranceLeft', 'warehouseEntranceRight', 'singleChamberTopRight',
                              'kronicBoostRoomBottomLeft', 'mainStreetBottom', 'crabHoleBottomLeft', 'leCoudeRight',
                              'redFishRoomLeft', 'redTowerTopLeft', 'caterpillarRoomTopRight', 'redBrinstarElevator',
                              'eastTunnelRight', 'eastTunnelTopRight', 'glassTunnelTop', 'goldenFour',
                              'ridleyRoomOut', 'ridleyRoomIn', 'kraidRoomOut', 'kraidRoomIn',
                              'draygonRoomOut', 'draygonRoomIn', 'phantoonRoomOut', 'phantoonRoomIn',
                              'tourianEscapeRoom4TopRight', 'climbBottomLeft', 'greenBrinstarMainShaftTopLeft',
                              'basementLeft', 'businessCenterMidLeft', 'crabHoleBottomRight']:
            raiseHttp(400, "Wrong value for {}: {}".format(point, pointValue), True)

    def action(self):
        pass

    def locName4isolver(self, locName):
        # remove space and special characters
        # sed -e 's+ ++g' -e 's+,++g' -e 's+(++g' -e 's+)++g' -e 's+-++g'
        locName = str(locName)
        return locName[0].lower() + removeChars(locName[1:], " ,()-")

    def returnState(self):
        if len(self.session["state"]) > 0:
            state = self.session["state"]
            #print("state returned to frontend: availWeb {}, visWeb {}".format(state["availableLocationsWeb"], state["visitedLocationsWeb"]))
            return json.dumps({
                # item tracker
                "availableLocations": state["availableLocationsWeb"],
                "visitedLocations": state["visitedLocationsWeb"],
                # compatibility with existing sessions
                "remainLocations": state["remainLocationsWeb"] if "remainLocationsWeb" in state else [],
                "lastAP": self.locName4isolver(state["lastAP"]),

                # area tracker
                "lines": state["linesWeb"],
                "linesSeq": state["linesSeqWeb"],
                "allTransitions": state["allTransitions"],

                # infos on seed
                "mode": state["mode"],
                "areaRando": state["areaRando"],
                "bossRando": state["bossRando"],
                "escapeRando": state["escapeRando"],
                "escapeTimer": state["escapeTimer"],
                "seed": state["seed"],
                "preset": os.path.basename(os.path.splitext(state["presetFileName"])[0]),
                "errorMsg": state["errorMsg"],
                "last": state["last"]
            })
        else:
            raiseHttp(200, "OK", True)

    def callSolverAction(self, scope, action, parameters):
        # check that we have a state in the session
        if "state" not in self.session:
            raiseHttp(400, "Missing Solver state in the session", True)

        mode = self.session["mode"]

        (fd1, jsonInFileName) = tempfile.mkstemp()
        (fd2, jsonOutFileName) = tempfile.mkstemp()
        params = [
            pythonExec,  os.path.expanduser("~/RandomMetroidSolver/solver.py"),
            '--interactive',
            '--state',  jsonInFileName,
            '--output', jsonOutFileName,
            '--action', action,
            '--mode', mode,
            '--scope', scope
        ]
        if action in ['add', 'replace']:
            if scope == 'item':
                params += ['--loc', parameters["loc"]]
                if mode != 'standard':
                    params += ['--item', parameters["item"]]
                    if parameters['hide'] == True:
                        params.append('--hide')
            elif scope == 'area':
                params += ['--startPoint', parameters["startPoint"],
                           '--endPoint', parameters["endPoint"]]
        elif action == 'remove' and scope == 'item':
            params += ['--count', str(parameters["count"])]
        elif action == 'remove' and scope == 'area' and "startPoint" in parameters:
            params += ['--startPoint', parameters["startPoint"]]
        elif action == 'save' and scope == 'common':
            if parameters['lock'] == True:
                params.append('--lock')
            if 'escapeTimer' in parameters:
                params += ['--escapeTimer', parameters['escapeTimer']]
        elif action == 'randomize':
            params += ['--progressionSpeed', parameters["progressionSpeed"],
                       '--minorQty', parameters["minorQty"],
                       '--energyQty', parameters["energyQty"]
            ]

        if request.vars.debug != None:
            params.append('--vcr')
            params.append('--debug')

        # dump state as input
        with open(jsonInFileName, 'w') as jsonFile:
            json.dump(self.session["state"], jsonFile)

        print("before calling isolver: {}".format(params))
        start = datetime.now()
        ret = subprocess.call(params)
        end = datetime.now()
        duration = (end - start).total_seconds()
        print("ret: {}, duration: {}s".format(ret, duration))

        if ret == 0:
            with open(jsonOutFileName) as jsonFile:
                state = json.load(jsonFile)
            os.close(fd1)
            os.remove(jsonInFileName)
            os.close(fd2)
            os.remove(jsonOutFileName)
            if action == 'save':
                return json.dumps(state)
            else:
                # save the escape timer at every step to avoid loosing its value
                if request.vars.escapeTimer != None:
                    state["escapeTimer"] = request.vars.escapeTimer

                self.session["state"] = state
                return self.returnState()
        else:
            os.close(fd1)
            os.remove(jsonInFileName)

            msg = "Something wrong happened while iteratively solving the ROM"
            try:
                with open(jsonOutFileName, 'r') as jsonFile:
                    data = json.load(jsonFile)
                    if "errorMsg" in data:
                        msg = data["errorMsg"]
            except Exception as e:
                pass
            os.close(fd2)
            os.remove(jsonOutFileName)
            raiseHttp(400, msg, True)

class WS_common_init(WS):
    def validate(self):
        super(WS_common_init, self).validate()

        if request.vars.scope != 'common':
            raiseHttp(400, "Unknown scope, must be common", True)

        # preset
        preset = request.vars.preset
        if request == None:
            raiseHttp(400, "Missing parameter preset", True)
        if IS_NOT_EMPTY()(preset)[1] is not None:
            raiseHttp(400, "Preset name is empty", True)
        if IS_ALPHANUMERIC()(preset)[1] is not None:
            raiseHttp(400, "Preset name must be alphanumeric: {}".format(preset), True)
        if IS_LENGTH(32)(preset)[1] is not None:
            raiseHttp(400, "Preset name must be max 32 chars: {}".format(preset), True)
        fullPath = '{}/{}.json'.format(getPresetDir(preset), preset)
        if not os.path.isfile(fullPath):
            raiseHttp(400, "Unknown preset: {}".format(preset), True)

        if request.vars.mode != 'seedless':
            # ROM (only through file API)
            if request.vars.romJson is None or len(request.vars.romJson) == 0:
                raiseHttp(400, "Missing ROM to solve", True)
            try:
                json.loads(request.vars.romJson)
            except:
                raiseHttp(400, "Wrong value for romJson, must be a JSON string: [{}]".format(request.vars.romJson))

            # ROM file name
            uploadFile = request.vars.fileName
            if uploadFile is None:
                raiseHttp(400, "Missing ROM file name", True)
            if IS_NOT_EMPTY()(uploadFile)[1] is not None:
                raiseHttp(400, "File name is empty", True)
            if IS_LENGTH(maxsize=255, minsize=1)(uploadFile)[1] is not None:
                raiseHttp(400, "Wrong length for ROM file name, name must be between 1 and 255 characters", True)

        if request.vars.startLocation != None:
            if request.vars.startLocation not in GraphUtils.getStartAccessPointNames():
                raiseHttp(400, "Wrong value for startLocation: {}".format(request.vars.startLocation), True)

    def action(self):
        mode = request.vars.mode
        if mode != 'seedless':
            try:
                (base, jsonRomFileName) = generateJsonROM(request.vars.romJson)
            except Exception as e:
                raiseHttp(400, "Can't load JSON ROM: {}".format(e), True)
            seed = base + '.sfc'
            startLocation = None
        else:
            seed = 'seedless'
            jsonRomFileName = None
            startLocation = request.vars.startLocation

        preset = request.vars.preset
        presetFileName = '{}/{}.json'.format(getPresetDir(preset), preset)

        self.session["seed"] = seed
        self.session["preset"] = preset
        self.session["mode"] = mode
        self.session["startLocation"] = startLocation if startLocation != None else "Landing Site"

        vcr = request.vars.debug != None
        fill = request.vars.fill == "true"

        return self.callSolverInit(jsonRomFileName, presetFileName, preset, seed, mode, vcr, fill, startLocation)

    def callSolverInit(self, jsonRomFileName, presetFileName, preset, romFileName, mode, vcr, fill, startLocation):
        (fd, jsonOutFileName) = tempfile.mkstemp()
        params = [
            pythonExec,  os.path.expanduser("~/RandomMetroidSolver/solver.py"),
            '--preset', presetFileName,
            '--output', jsonOutFileName,
            '--action', "init",
            '--interactive',
            '--mode', mode,
            '--scope', 'common',
        ]

        if mode != "seedless":
            params += ['-r', str(jsonRomFileName)]

        if vcr == True:
            params.append('--vcr')

        if fill == True:
            params.append('--fill')

        if startLocation != None:
            params += ['--startAP', startLocation]

        print("before calling isolver: {}".format(params))
        start = datetime.now()
        ret = subprocess.call(params)
        end = datetime.now()
        duration = (end - start).total_seconds()
        print("ret: {}, duration: {}s".format(ret, duration))

        if ret == 0:
            DB = db.DB()
            DB.addISolver(preset, romFileName)
            DB.close()

            with open(jsonOutFileName) as jsonFile:
                state = json.load(jsonFile)
            os.close(fd)
            os.remove(jsonOutFileName)
            self.session["state"] = state
            return self.returnState()
        else:
            os.close(fd)
            os.remove(jsonOutFileName)
            raiseHttp(400, "Something wrong happened while initializing the ISolver", True)

class WS_common_get(WS):
    def validate(self):
        super(WS_common_get, self).validate()

    def action(self):
        return self.returnState()

class WS_common_save(WS):
    def validate(self):
        super(WS_common_save, self).validate()

        if request.vars.lock == None:
            raiseHttp(400, "Missing parameter lock", True)

        if request.vars.lock not in ["save", "lock"]:
            raiseHttp(400, "Wrong value for lock: {}, authorized values: save/lock".format(request.vars.lock), True)

    def action(self):
        if self.session["mode"] != "plando":
            raiseHttp(400, "Save can only be use in plando mode", True)

        params = {'lock': request.vars.lock == "lock"}
        if request.vars.escapeTimer != None:
            params['escapeTimer'] = request.vars.escapeTimer

        return self.callSolverAction("common", "save", params)

class WS_common_randomize(WS):
    def validate(self):
        super(WS_common_randomize, self).validate()

        if request.vars.progressionSpeed not in ["slowest", "slow", "medium", "fast", "fastest", "basic", "VARIAble"]:
            raiseHttp(400, "Wrong value for progressionSpeed: {}".format(request.vars.progressionSpeed), True)
        minorQtyInt = getInt('minorQty', True)
        if minorQtyInt < 7 or minorQtyInt > 100:
            raiseHttp(400, "Wrong value for minorQty, must be between 7 and 100", True)
        if request.vars.energyQty not in ["sparse", "medium", "vanilla"]:
            raiseHttp(400, "Wrong value for energyQty: {}".format(request.vars.energyQty), True)

    def action(self):
        if self.session["mode"] != "plando":
            raiseHttp(400, "Randomize can only be use in plando mode", True)

        params = {}
        for elem in "progressionSpeed", "minorQty", "energyQty":
            params[elem] = request.vars[elem]

        self.session["rando"] = params

        return self.callSolverAction("common", "randomize", params)

class WS_area_add(WS):
    def validate(self):
        super(WS_area_add, self).validate()

        # startPoint and endPoint
        self.validatePoint("startPoint")
        self.validatePoint("endPoint")

        if len(self.session["state"]) == 0:
            raiseHttp(400, "ISolver state is empty", True)

    def action(self):
        return self.callSolverAction("area", "add", {"startPoint": request.vars.startPoint,
                                                     "endPoint": request.vars.endPoint})

class WS_area_remove(WS):
    def validate(self):
        if request.vars["startPoint"] != None:
            self.validatePoint("startPoint")

        super(WS_area_remove, self).validate()

    def action(self):
        parameters = {}
        if request.vars["startPoint"] != None:
            parameters["startPoint"] = request.vars.startPoint

        return self.callSolverAction("area", "remove", parameters)

class WS_area_clear(WS):
    def validate(self):
        super(WS_area_clear, self).validate()

    def action(self):
        return self.callSolverAction("area", "clear", {})

class WS_item_add(WS):
    def validate(self):
        super(WS_item_add, self).validate()

        # new location
        def name4isolver(locName):
            # remove space and special characters
            # sed -e 's+ ++g' -e 's+,++g' -e 's+(++g' -e 's+)++g' -e 's+-++g'
            return removeChars(locName, " ,()-")

        locName = name4isolver(request.vars.locName)

        if locName not in ['EnergyTankGauntlet', 'Bomb', 'EnergyTankTerminator', 'ReserveTankBrinstar', 'ChargeBeam', 'MorphingBall', 'EnergyTankBrinstarCeiling', 'EnergyTankEtecoons', 'EnergyTankWaterway', 'EnergyTankBrinstarGate', 'XRayScope', 'Spazer', 'EnergyTankKraid', 'VariaSuit', 'IceBeam', 'EnergyTankCrocomire', 'HiJumpBoots', 'GrappleBeam', 'ReserveTankNorfair', 'SpeedBooster', 'WaveBeam', 'EnergyTankRidley', 'ScrewAttack', 'EnergyTankFirefleas', 'ReserveTankWreckedShip', 'EnergyTankWreckedShip', 'RightSuperWreckedShip', 'GravitySuit', 'EnergyTankMamaturtle', 'PlasmaBeam', 'ReserveTankMaridia', 'SpringBall', 'EnergyTankBotwoon', 'SpaceJump', 'PowerBombCrateriasurface', 'MissileoutsideWreckedShipbottom', 'MissileoutsideWreckedShiptop', 'MissileoutsideWreckedShipmiddle', 'MissileCrateriamoat', 'MissileCrateriabottom', 'MissileCrateriagauntletright', 'MissileCrateriagauntletleft', 'SuperMissileCrateria', 'MissileCrateriamiddle', 'PowerBombgreenBrinstarbottom', 'SuperMissilepinkBrinstar', 'MissilegreenBrinstarbelowsupermissile', 'SuperMissilegreenBrinstartop', 'MissilegreenBrinstarbehindmissile', 'MissilegreenBrinstarbehindreservetank', 'MissilepinkBrinstartop', 'MissilepinkBrinstarbottom', 'PowerBombpinkBrinstar', 'MissilegreenBrinstarpipe', 'PowerBombblueBrinstar', 'MissileblueBrinstarmiddle', 'SuperMissilegreenBrinstarbottom', 'MissileblueBrinstarbottom', 'MissileblueBrinstartop', 'MissileblueBrinstarbehindmissile', 'PowerBombredBrinstarsidehopperroom', 'PowerBombredBrinstarspikeroom', 'MissileredBrinstarspikeroom', 'MissileKraid', 'Missilelavaroom', 'MissilebelowIceBeam', 'MissileaboveCrocomire', 'MissileHiJumpBoots', 'EnergyTankHiJumpBoots', 'PowerBombCrocomire', 'MissilebelowCrocomire', 'MissileGrappleBeam', 'MissileNorfairReserveTank', 'MissilebubbleNorfairgreendoor', 'MissilebubbleNorfair', 'MissileSpeedBooster', 'MissileWaveBeam', 'MissileGoldTorizo', 'SuperMissileGoldTorizo', 'MissileMickeyMouseroom', 'MissilelowerNorfairabovefireflearoom', 'PowerBomblowerNorfairabovefireflearoom', 'PowerBombPowerBombsofshame', 'MissilelowerNorfairnearWaveBeam', 'MissileWreckedShipmiddle', 'MissileGravitySuit', 'MissileWreckedShiptop', 'SuperMissileWreckedShipleft', 'MissilegreenMaridiashinespark', 'SuperMissilegreenMaridia', 'MissilegreenMaridiatatori', 'SuperMissileyellowMaridia', 'MissileyellowMaridiasupermissile', 'MissileyellowMaridiafalsewall', 'MissileleftMaridiasandpitroom', 'MissilerightMaridiasandpitroom', 'PowerBombrightMaridiasandpitroom', 'MissilepinkMaridia', 'SuperMissilepinkMaridia', 'MissileDraygon', 'Kraid', 'Ridley', 'Phantoon', 'Draygon', 'MotherBrain']:
            raiseHttp(400, "Unknown location name: {}".format(request.vars.locName), True)

        request.vars.locName = locName

        itemName = request.vars.itemName
        if itemName == "NoEnergy":
            itemName = "Nothing"

        if itemName not in [None, 'ETank', 'Missile', 'Super', 'PowerBomb', 'Bomb', 'Charge', 'Ice', 'HiJump', 'SpeedBooster', 'Wave', 'Spazer', 'SpringBall', 'Varia', 'Plasma', 'Grapple', 'Morph', 'Reserve', 'Gravity', 'XRayScope', 'SpaceJump', 'ScrewAttack', 'Nothing', 'NoEnergy', 'Boss']:
            raiseHttp(400, "Unknown item name: {}".format(request.vars.itemName), True)

    def action(self):
        item = request.vars.itemName
        # items used only in the randomizer that we get in vcr mode
        if item in ["Boss", "NoEnergy"]:
            item = 'Nothing'

        return self.callSolverAction("item", "add", {"loc": request.vars.locName, "item": item, "hide": request.vars.hide == "true"})

class WS_item_replace(WS_item_add):
    def validate(self):
        super(WS_item_replace, self).validate()

    def action(self):
        return self.callSolverAction("item", "replace", {"loc": request.vars.locName, "item": request.vars.itemName, "hide": request.vars.hide == "true"})

class WS_item_remove(WS):
    def validate(self):
        super(WS_item_remove, self).validate()

    def action(self):
        count = request.vars.count
        if count != None:
            count = getInt("count", True)
            if count > 105 or count < 1:
                raiseHttp(400, "Wrong value for count, must be in [1-105] ", True)
        else:
            count = 1

        return self.callSolverAction("item", "remove", {"count": count})

class WS_item_clear(WS):
    def validate(self):
        super(WS_item_clear, self).validate()

    def action(self):
        return self.callSolverAction("item", "clear", {})

def trackerWebService():
    # unified web service for item/area trackers
    print("trackerWebService called")

    ws = WS.factory()
    ws.validate()
    ret = ws.action()

    if ret == None:
        # return something
        raiseHttp(200, "OK", True)
    else:
        return ret

# race mode
def getMagic():
    return random.randint(1, 0xffff)

def initCustomizerSession():
    if session.customizer == None:
        session.customizer = {}

        session.customizer['colorsRandomization'] = "off"
        session.customizer['suitsPalettes'] = "on"
        session.customizer['beamsPalettes'] = "on"
        session.customizer['tilesPalettes'] = "on"
        session.customizer['enemiesPalettes'] = "on"
        session.customizer['bossesPalettes'] = "on"
        session.customizer['minDegree'] = -15
        session.customizer['maxDegree'] = 15
        session.customizer['invert'] = "on"
        session.customizer['globalShift'] = "on"
        session.customizer['customSpriteEnable'] = "off"
        session.customizer['customSprite'] = "samus"
        session.customizer['itemsounds'] = "off"
        session.customizer['spinjumprestart'] = "off"
        session.customizer['rando_speed'] = "off"
        session.customizer['elevators_doors_speed'] = "off"
        session.customizer['animals'] = "off"
        session.customizer['No_Music'] = "off"

customSprites = {
    'samus': {"index":0, "name": "Samus", "desc": "Samus, with a distinct animation for Screw Attack without Space Jump and a new Crystal Flash animation", "author": "Artheau and Feesh", "group": "Samus"},
    'hitbox_helper': {"index":1, "name": "Hitbox", "desc": "Samus, with her actual hitbox on top", "author": "Artheau and Komaru", "group": "Samus"},
    'hack_ancient_chozo': {"index":2, "name": "Chozo", "desc": "Samus, from Ancient Chozo hack", "author": "Albert V.", "group": "Samus"},
    'hack_ascent': {"index":3, "name": "Ascent", "desc": "Samus, from Ascent hack", "author": "Benox50", "group": "Samus"},
    'hack_decision': {"index":4, "name": "Decision", "desc": "Samus, from Decision hack", "author": "JoshShoeWah", "group": "Samus"},
    'hack_escape2': {"index":5, "name": "Escape II", "desc": "Samus, from Escape II hack", "author": "Hiroishi", "group": "Samus"},
    'hack_hyper': {"index":6, "name": "Hyper", "desc": "Samus, from Hyper Metroid hack", "author": "RealRed", "group": "Samus"},
    'hack_nature': {"index":7, "name": "Nature", "desc": "Samus, from Nature hack", "author": "Jefe962", "group": "Samus"},
    'hack_phazon': {"index":8, "name": "Phazon", "desc": "Samus, from Phazon hack", "author": "A_red_monk_called_Key", "group": "Samus"},
    'hack_redesign': {"index":9, "name": "Redesign", "desc": "Samus, from Redesign hack", "author": "Drewseph", "group": "Samus"},
    'hack_szm': {"index":10, "name": "SZM", "desc": "Samus, from Super Zero Mission hack", "author": "SBniconico", "group": "Samus"},
    'bailey': {"index":11, "name": "Bailey", "desc": "Justin Bailey, aka Samus in an 80s swimsuit", "author": "Auximines", "group": "Custom"},
    'alucard': {"index":12, "name": "Alucard", "desc": "Alucard from Castlevania Symphony Of The Night", "author": "Nintoaster", "group": "Custom"},
    'megaman': {"index":13, "name": "Megaman", "desc": "Megaman X!", "author": "Artheau", "group": "Custom"},
    'fed_trooper': {"index":14, "name": "GF Trooper", "desc": "A Galactic Federation trooper", "author": "Physix", "group": "Custom"},
    'super_controid': {"index":15, "name": "Contra", "desc": "Badass soldier from Contra III", "author": "Nintoaster", "group": "Custom"},
    'luigi': {"index":16, "name": "Luigi", "desc": "Let's-a go!", "author": "RonnSama", "group": "Custom"},
    'marga': {"index":17, "name": "Margatroid", "desc": "Alice Margatroid from the Touhou Project", "author": "Plan", "group": "Custom"},
    'win95_cursor': {"index":18, "name": "Win95 Cursor", "desc": "A classic Windows cursor...", "author": "PlaguedOne", "group": "Custom"}
}

def customizer():
    response.title = 'Super Metroid VARIA Seeds Customizer'

    initCustomizerSession()

    return dict(customSprites=customSprites)

def customWebService():
    # check validity of all parameters
    patches = ['itemsounds', 'spinjumprestart', 'rando_speed', 'elevators_doors_speed', 'No_Music', 'animals']
    others = ['colorsRandomization', 'suitsPalettes', 'beamsPalettes', 'tilesPalettes', 'enemiesPalettes',
              'bossesPalettes', 'minDegree', 'maxDegree', 'invert']
    validateWebServiceParams(patches, [], others, isJson=True)
    if request.vars.customSpriteEnable == 'on':
        if request.vars.customSprite not in customSprites:
            raiseHttp(400, "Wrong value for customSprite", True)

    if session.customizer == None:
        session.customizer = {}

    # update session
    session.customizer['colorsRandomization'] = request.vars.colorsRandomization
    session.customizer['suitsPalettes'] = request.vars.suitsPalettes
    session.customizer['beamsPalettes'] = request.vars.beamsPalettes
    session.customizer['tilesPalettes'] = request.vars.tilesPalettes
    session.customizer['enemiesPalettes'] = request.vars.enemiesPalettes
    session.customizer['bossesPalettes'] = request.vars.bossesPalettes
    session.customizer['minDegree'] = request.vars.minDegree
    session.customizer['maxDegree'] = request.vars.maxDegree
    session.customizer['invert'] = request.vars.invert
    session.customizer['globalShift'] = request.vars.globalShift
    session.customizer['customSpriteEnable'] = request.vars.customSpriteEnable
    session.customizer['customSprite'] = request.vars.customSprite
    session.customizer['itemsounds'] = request.vars.itemsounds
    session.customizer['spinjumprestart'] = request.vars.spinjumprestart
    session.customizer['rando_speed'] = request.vars.rando_speed
    session.customizer['elevators_doors_speed'] = request.vars.elevators_doors_speed
    session.customizer['animals'] = request.vars.animals
    session.customizer['No_Music'] = request.vars.No_Music

    # call the randomizer
    (fd, jsonFileName) = tempfile.mkstemp()
    params = [pythonExec,  os.path.expanduser("~/RandomMetroidSolver/randomizer.py"),
              '--output', jsonFileName, '--patchOnly']

    if request.vars.itemsounds == 'on':
        params += ['-c', 'itemsounds.ips']
    if request.vars.elevators_doors_speed == 'on':
        params += ['-c', 'elevators_doors_speed.ips']
    if request.vars.spinjumprestart == 'on':
        params += ['-c', 'spinjumprestart.ips']
    if request.vars.rando_speed == 'on':
        params += ['-c', 'rando_speed.ips']
    if request.vars.No_Music == 'on':
        params += ['-c', 'No_Music']
    if request.vars.animals == 'on':
        params.append('--animals')

    if request.vars.colorsRandomization == 'on':
        params.append('--palette')
        if request.vars.suitsPalettes == 'off':
            params.append('--no_shift_suit_palettes')
        if request.vars.beamsPalettes == 'off':
            params.append('--no_shift_beam_palettes')
        if request.vars.tilesPalettes == 'off':
            params.append('--no_shift_tileset_palette')
        if request.vars.enemiesPalettes == 'off':
            params.append('--no_shift_enemy_palettes')
        if request.vars.bossesPalettes == 'off':
            params.append('--no_shift_boss_palettes')
        if request.vars.globalShift == 'off':
            params.append('--no_global_shift')
            params.append('--individual_suit_shift')
            params.append('--individual_tileset_shift')
            params.append('--no_match_ship_and_power')
        params += ['--min_degree', request.vars.minDegree, '--max_degree', request.vars.maxDegree]
        if request.vars.invert == 'on':
            params.append('--invert')

    if request.vars.customSpriteEnable == 'on':
        params += ['--sprite', "{}.ips".format(request.vars.customSprite)]

    print("before calling: {}".format(params))
    start = datetime.now()
    ret = subprocess.call(params)
    end = datetime.now()
    duration = (end - start).total_seconds()
    print("ret: {}, duration: {}s".format(ret, duration))

    if ret == 0:
        with open(jsonFileName) as jsonFile:
            data = json.load(jsonFile)

        os.close(fd)
        os.remove(jsonFileName)

        return json.dumps(data)
    else:
        # extract error from json
        try:
            with open(jsonFileName) as jsonFile:
                msg = json.load(jsonFile)['errorMsg']
        except:
            msg = "customizerWebService: something wrong happened"

        os.close(fd)
        os.remove(jsonFileName)
        raise HTTP(400, json.dumps(msg))

def initExtStatsSession():
    if session.extStats == None:
        session.extStats = {}
        session.extStats['preset'] = 'regular'
        session.extStats['randoPreset'] = 'default'

def updateExtStatsSession():
    if session.extStats is None:
        session.extStats = {}

    session.extStats['preset'] = request.vars.preset
    session.extStats['randoPreset'] = request.vars.randoPreset

def validateExtStatsParams():
    for (preset, directory) in [("preset", "standard_presets"), ("randoPreset", "rando_presets")]:
        if request.vars[preset] == None:
            return (False, "Missing parameter preset")
        preset = request.vars[preset]

        if IS_ALPHANUMERIC()(preset)[1] is not None:
            return (False, "Wrong value for preset, must be alphanumeric")

        if IS_LENGTH(maxsize=32, minsize=1)(preset)[1] is not None:
            return (False, "Wrong length for preset, name must be between 1 and 32 characters")

        # check that preset exists
        fullPath = '{}/{}.json'.format(directory, preset)
        if not os.path.isfile(fullPath):
            return (False, "Unknown preset: {}".format(preset))

    return (True, None)

def extStats():
    response.title = 'Super Metroid VARIA Randomizer statistics'

    initExtStatsSession()

    if request.vars.action == 'Load':
        (ok, msg) = validateExtStatsParams()
        if not ok:
            session.flash = msg
            redirect(URL(r=request, f='extStats'))

        updateExtStatsSession()

        skillPreset = request.vars.preset
        randoPreset = request.vars.randoPreset

        # load rando preset
        fullPath = 'rando_presets/{}.json'.format(randoPreset)
        try:
            with open(fullPath) as jsonFile:
                randoPreset = json.load(jsonFile)
        except Exception as e:
            raise HTTP(400, "Can't load the rando preset: {}: {}".format(randoPreset, e))

        # load skill preset
        fullPath = '{}/{}.json'.format(getPresetDir(skillPreset), skillPreset)
        try:
            skillPresetContent = PresetLoader.factory(fullPath).params
            completePreset(skillPresetContent)
        except Exception as e:
            raise HTTP(400, "Error loading the preset {}: {}".format(skillPreset, e))

        parameters = {
            'preset': skillPreset,
            'area': 'areaRandomization' in randoPreset and randoPreset['areaRandomization'] == 'on',
            'boss': 'bossRandomization' in randoPreset and randoPreset['bossRandomization'] == 'on',
            'gravityBehaviour': randoPreset['gravityBehaviour'],
            'nerfedCharge': randoPreset['nerfedCharge'] == 'on',
            'maxDifficulty': randoPreset['maxDifficulty'],
            # parameters which can be random:
            'majorsSplit': randoPreset['majorsSplit'] if 'majorsSplit' in randoPreset else 'Full',
            'startAP': randoPreset['startLocation'] if 'startLocation' in randoPreset else 'Landing Site',
            'progSpeed': randoPreset['progressionSpeed'] if 'progressionSpeed' in randoPreset else 'variable',
            'morphPlacement': randoPreset['morphPlacement'] if 'morphPlacement' in randoPreset else 'early',
            'suitsRestriction': 'suitsRestriction' in randoPreset and randoPreset['suitsRestriction'] == 'on',
            'progDiff': randoPreset['progressionDifficulty'] if 'progressionDifficulty' in randoPreset else 'normal',
            'superFunMovement': 'funMovement' in randoPreset and randoPreset['funMovement'] == 'on',
            'superFunCombat': 'funCombat' in randoPreset and randoPreset['funCombat'] == 'on',
            'superFunSuit': 'funSuits' in randoPreset and randoPreset['funSuits'] == 'on'
        }

        if randoPreset['suitsRestriction'] == "random":
            parameters["suitsRestriction"] = "random"
        if randoPreset['funMovement'] == "random":
            parameters["superFunMovement"] = "random"
        if randoPreset['funCombat'] == "random":
            parameters["superFunCombat"] = "random"
        if randoPreset['funSuits'] == "random":
            parameters["superFunSuit"] = "random"

        DB = db.DB()
        (itemsStats, techniquesStats, difficulties) = DB.getExtStat(parameters)
        DB.close()

        # check that all items are present in the stats:
        nbItems = 19
        nbLocs = 105
        if itemsStats != None and len(itemsStats) > 0 and len(itemsStats) != nbItems:
            for i, item in enumerate(['Bomb', 'Charge', 'Grapple', 'Gravity', 'HiJump', 'Ice', 'Missile', 'Morph',
                                      'Plasma', 'PowerBomb', 'ScrewAttack', 'SpaceJump', 'Spazer', 'SpeedBooster',
                                      'SpringBall', 'Super', 'Varia', 'Wave', 'XRayScope']):
                if itemsStats[i][1] != item:
                    itemsStats.insert(i, [itemsStats[0][0], item] + [0]*nbLocs)
    else:
        itemsStats = None
        techniquesStats = None
        difficulties = None
        skillPresetContent = None
        parameters = None

    (randoPresets, tourRandoPresets) = loadRandoPresetsList()
    # remove random presets those statistics are useless
    randoPresets.remove("all_random")
    randoPresets.remove("quite_random")
    (stdPresets, tourPresets, comPresets) = loadPresetsList()

    return dict(stdPresets=stdPresets, tourPresets=tourPresets,
                randoPresets=randoPresets, tourRandoPresets=tourRandoPresets,
                itemsStats=itemsStats, techniquesStats=techniquesStats,
                categories=Knows.categories, knowsDesc=Knows.desc, skillPresetContent=skillPresetContent,
                locations=locations, parameters=parameters, difficulties=difficulties)
