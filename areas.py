

from parameters import *
from helpers import *
from dijkstra import *

_transitionsDict = {
    'Crateria/LandingSite': {
        'Brinstar/Blue': lambda items: (True, 0),
        'Crateria/Bombs': lambda items: wand(haveItem(items, 'Morph'),
                                             canOpenRedDoors(items)),
        'Crateria/Terminator': lambda items: wor(wand(haveItem(items, 'SpeedBooster'), wor(Knows.TerminatorSpark, Knows.ShortCharge)), 
                                                 canDestroyBombWalls(items)),
        'Crateria/Gauntlet': lambda items: canEnterAndLeaveGauntlet(items),
        'Crateria/WreckedShipBottom': lambda items: canAccessWs(items),
        'Brinstar/Red/Top': lambda items: wand(canOpenGreenDoors(items),
                                               canUsePowerBombs(items))
    },
    'Crateria/Bombs': {
        'Crateria/LandingSite': lambda items: wor(Knows.AlcatrazEscape,
                                                  canPassBombPassages(items))
    },
    'Crateria/Terminator': {
        'Crateria/LandingSite': lambda items: wor(haveItem(items, 'SpeedBooster'), # much easier this way (gain speed in terminator)
                                                  canDestroyBombWalls(items)),
        'Brinstar/Green': lambda items: (True, 0)
    },
    'Crateria/Gauntlet': {
        # difficulty already handled in canEnterAndLeaveGauntlet
        'Crateria/LandingSite': lambda items: (True, 0), 
        'Crateria/Terminator': lambda items: (True, 0)
    },
    'Crateria/WreckedShipBottom': {
        'Crateria/LandingSite': lambda items: (True, 0),
        'WreckedShip/Main': lambda items: (True, 0) #FIXME handle ocean difficulty?
    },
    'Crateria/WreckedShipTop': {
        'WreckedShip/Gravity': lambda items: (True, 0),
        'Crateria/WreckedShipBottom': lambda items: (True, 0),
        'WreckedShip/Top': lambda items: (True, 0)
    },
    'Crateria/ForgottenHighway': { # FIXME handle difficulty in navigation??
        'WreckedShip/Back': lambda items: (True, 0),
        'Maridia/ForgottenHighway': lambda items: (True, 0)
    },
    'Brinstar/Blue': {
        'Crateria/LandingSite': lambda items: (True, 0),
        'Brinstar/Hills': lambda items: canUsePowerBombs(items)
    },
    'Brinstar/Green': {
        'Brinstar/Green/Reserve': lambda items: wand(canOpenRedDoors(items),
                                                     wor(wand(Knows.Mockball,
                                                              haveItem(items, 'Morph')),
                                                         haveItem(items, 'SpeedBooster'))),
        'Brinstar/Pink': lambda items: wand(canOpenRedDoors(items),
                                            canDestroyBombWalls(items))
    },
    'Brinstar/Green/Reserve': {
        'Brinstar/Green': lambda items: (True, 0)
    },
    'Brinstar/Pink': {
        'Brinstar/Hills': lambda items: wand(canPassBombPassages(items),
                                             canOpenGreenDoors(items)),
        'Green': lambda items: canDestroyBombWalls(items)
    },
    'Brinstar/Hills': {
        'Brinstar/Pink': lambda items: canPassBombPassages(items),
        'Brinstar/Red': lambda items: canOpenGreenDoors(items)
    },
    'Brinstar/Red': {
        'Brinstar/Hills': lambda items: (True, 0),
        'Brinstar/Red/Top': lambda items: wor(Knows.RedTowerClimb,
                                              haveItem(items, 'Ice'),
                                              haveItem(items, 'ScrewAttack')),
        'Brinstar/Red/Bottom': lambda items: (True, 0)
    },
    'Brinstar/Red/Top': {
        'Brinstar/Red': lambda items: canUsePowerBombs(items),
        'Crateria/LandingSite': lambda items: (True, 0)
    },
    'Brinstar/Red/Bottom': {
        'Brinstar/Red': lambda items: (True, 0),
        'Brinstar/Kraid': lambda items: wand(haveItem('Super'),
                                             wor(haveItem(items, 'HiJump'),
                                                 canFly(items),
                                                 Knows.EarlyKraid),
                                             canPassBombPassages(items)),
        'Norfair/Entrance': lambda items: (True, 0),
        'Maridia/Green': lambda items: canUsePowerBombs(items)
    },
    'Brinstar/Kraid': {
        'Brinstar/Red/Bottom': lambda items: wand(haveItem('Super'), canPassBombPassages(items))
    },
    'WreckedShip/Main': {
        'WreckedShip/Back': lambda items: wand(Bosses.bossDead('Phantoon'),
                                               wor(wor(haveItem(items, 'Bomb'),
                                                       haveItem(items, 'PowerBomb')),
                                                   Knows.SpongeBathBombJump,
                                                   wand(haveItem(items, 'HiJump'),
                                                        Knows.SpongeBathHiJump),
                                                   wor(haveItem(items, 'SpaceJump', difficulty=easy),
                                                       wand(haveItem(items, 'SpeedBooster'),
                                                            Knows.SpongeBathSpeed),
                                                       wand(haveItem(items, 'SpringBall'),
                                                            Knows.SpringBallJump)))), # FIXME add spiky death?
        'WreckedShip/Top': lambda items: Bosses.bossDead('Phantoon')
    },
    'WreckedShip/Back': {
        'WreckedShip/Main': lambda items: (True, 0), # FIXME add spiky death?
        'Crateria/ForgottenHighway': lambda items: (True, 0)
    },
    'WreckedShip/Top': {
        'WreckedShip/Main': lambda items: (True, 0),
        'Crateria/WreckedShipTop': lambda items: (True, 0) #FIXME attic?
    },
    'WreckedShip/Gravity': {
        'Crateria/WreckedShipBottom': lambda items: (True, 0)
    },
    'Norfair/Entrance': {
        'Norfair/Ice': lambda items: wand(wor(heatProof(items),
                                              energyReserveCountOkList(items, Settings.hellRuns['Ice'])),
                                          wor(wand(haveItem(items, 'Morph'),
                                                   Knows.Mockball),
                                              haveItem(items, 'SpeedBooster'))),
        'Norfair/Bubble/Bottom': lambda items: wor(canHellRun(items),
                                                   haveItem(items, 'SpeedBooster')) # frog speedway
        'Brinstar/Red/Bottom': lambda items: (True, 0),
        'Norfair/Crocomire': lambda items: wand(wor(heatProof(items),
                                                    energyReserveCountOkList(items, 3)),
                                                haveItem(items, 'SpeedBooster'),
                                                canOpenGreenDoors(items))
    },
    'Norfair/Ice': {
        'Norfair/Entrance': lambda items: (True, 0)
    },
    'Norfair/Crocomire': {
        'Norfair/GrappleEscape': lambda items: wor(canFly(items),
                                                   haveItem(items, 'Grapple'),
                                                   wand(haveItem(items, 'HiJump'),
                                                        haveItem(items, 'SpeedBooster'))),
        'Norfair/Bubble/Bottom': lambda items: wor(heatProof(items),
                                                   energyReserveCountOkList(items, 3))
        'Norfair/Bottom': lambda items: wand(wor(heatProof(items),
                                                 energyReserveCountOkList(items, 3)), # grapple/spike+acid room 
                                             wor(haveItem(items, 'Grapple'),
                                                 haveItem(items, 'SpaceJump')))
    },
    # actually top right
    'Norfair/Bubble/Top': {
        'Norfair/Bubble/Bottom': lambda items: (True, 0),
        'Norfair/Reserve': lambda items: wor(haveItem(items, 'SpaceJump'),
                                             haveItem(items, 'Grapple')),
        'Norfair/Speed': lambda items: (True, 0),
        'Norfair/Wave': lambda items: (True, 0)
    },
    'Norfair/Bubble/Bottom': {
        'Norfair/Bubble/Top': lambda items: wor(canFly(items),
                                                haveItem(items, 'HiJump'), # FIXME add trick for this?
                                                haveItem(items, 'SpeedBooster'))
        'Norfair/Crocomire': lambda items: wor(Knows.GreenGateGlitch, haveItem(items, 'Wave')), 
        'Norfair/Reserve': lambda items: wor(canFly(items), wand(haveItem(items, 'HiJump'), Knows.NorfairReserveHiJump))
        'Norfair/Bottom': lambda items: (True, 0), 
        'Norfair/Entrance': lambda items: wor(canHellRun(items),
                                              haveItem(items, 'SpeedBooster')) # frog speedway
    },
    'Norfair/Bottom': {
        'Norfair/Bubble/Bottom': lambda items: (True, 0), 
        'Norfair/Wave': lambda items: (True, 0),
        'LowerNorfair/BeforeAmphitheater': lambda items: canAccessLowerNorfair(items),
    },
    'Norfair/Reserve': {
        'Norfair/Bubble/Top': lambda items: wor(haveItem(items, 'Grapple'),
                                                haveItem(items, 'SpaceJump')),
        'Norfair/Bubble/Bottom': lambda items: (True, 0)
    },
    'Norfair/Wave': {
        'Norfair/Bubble/Top': lambda items: (True, 0),
        'Norfair/Bottom': lambda items: (True, 0)
    },
    'Norfair/Speed': {
        'Norfair/Bubble/Top': lambda items: (True, 0)
    },
    'Norfair/GrappleEscape': {
        'Norfair/Crocomire': lambda items: (True, 0),
        'Norfair/Entrance': lambda items: (True, 0)
    },
    'LowerNorfair/BeforeAmphitheater': {
        'LowerNorfair/ScrewAttack': lambda items: wor(haveItem(items, 'SpaceJump'),
                                                      Knows.GreenGateGlitch),
        'LowerNorfair/AfterAmphitheater': lambda items: canPassWorstRoom(items)
    },
    'LowerNorfair/ScrewAttack': {
        'LowerNorfair/BeforeAmphitheater': lambda items: wor(canFly(items),
                                                             wand(haveItem(items, 'HiJump'),
                                                                  haveItem(items, 'SpeedBooster'),
                                                                  haveItem(items, 'ScrewAttack'),
                                                                  Knows.ScrewAttackExit),
                                                             wand(haveItem(items, 'SpringBall'),
                                                                  Knows.SpringBallJump))
    },
    'LowerNorfair/AfterAmphitheater': {
        'Norfair/Bubble/Top': (True, 0) # handle difficulty in LowerNorfair navigation
    },
    'Maridia/ForgottenHighway' : {
        'Crateria/ForgottenHighway': lambda items: (True, 0),
        'Maridia/Pink/Top': lambda items: Bosses.bossDead('Draygon'),
        'Maridia/Sandpits': lambda items: haveItem(items, 'Gravity')
    },
    'Maridia/Green': {
        'Maridia/Pink/Bottom': lambda items: canDefeatBotwoon(items),
        'Brinstar/Red/Bottom': lambda items: canUsePowerBombs(items),
        'Brinstar/Red/Top': lambda items: canAccessOuterMaridia(items)
    },
    'Maridia/Pink/Bottom': {
        'Maridia/Pink/Top': lambda items: canAccessOuterMaridia(items),
        'Maridia/Sandpits': lambda items: haveItem(items, 'Gravity'),
        'Maridia/Green': lambda items: canAccessOuterMaridia(items)
    },
    'Maridia/Pink/Top': {
        'Maridia/Pink/Bottom': lambda items: (True, 0),
        'Maridia/ForgottenHighway': lambda items: Bosses.bossDead('Draygon'),
        'Maridia/Draygon': lambda items: haveItem(items, 'Gravity')
    },
    'Maridia/Draygon': {
        'Maridia/Pink/Top': lambda items: haveItem(items, 'Gravity')
    },
    'Maridia/Sandpits': {
        # gravity here because getting out of sand without it is almost impossible
        'Maridia/ForgottenHighway': lambda items: haveItem(items, 'Gravity'),
        'Maridia/Green': lambda items: haveItem(items, 'Gravity'),
        'Brinstar/Red/Bottom': lambda items: haveItem(items, 'Gravity')
    }
}

_navigationDict = {
}

# very naive idea for now : create whole transition graph each time
# depending on items
def getDepGraph(items):
    g = Graph()
    

