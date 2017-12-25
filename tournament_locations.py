from parameters import Knows, Settings
# the canXXX functions
from helpers import *

# all the items locations with the prerequisites to access them

locations = [
{
    'Area': "Crateria",
    'SubArea': "Gauntlet",
    'Name': "Energy Tank, Gauntlet",
    'Class': "Major",
    'Address': 0x78264,
    'Visibility': "Visible",
    # EXPLAINED: difficulty already handled in the canEnterAndLeaveGauntlet function
#    'Available': lambda items: canEnterAndLeaveGauntlet(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Crateria",
    'SubArea' : "Bombs",
    'Name': "Bomb",
    'Address': 0x78404,
    'Class': "Major",
    'Visibility': "Chozo",
    # EXPLAINED: need to morph to enter Alcatraz. red door at Flyway.
    #            we may not have bombs or power bomb to get out of Alcatraz.
    # 'Available': lambda items: wand(haveItem(items, 'Morph'),
    #                                 canOpenRedDoors(items)),
    'Available': lambda items: (True, 0)
    # 'PostAvailable': lambda items: wor(Knows.AlcatrazEscape,
    #                                    canPassBombPassages(items))
},
{
    'Area': "Crateria",
    'SubArea' : "Terminator",
    'Name': "Energy Tank, Terminator",
    'Class': "Major",
    'Address': 0x78432,
    'Visibility': "Visible",
    # 'Available': lambda items: wor(haveItem(items, 'SpeedBooster'), # FIXME getting through here with SpeedBooster is not easy...
    #                                canDestroyBombWalls(items))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea' : "Green/Reserve",
    'Name': "Reserve Tank, Brinstar",
    'Class': "Major",
    'Address': 0x7852C,
    'Visibility': "Chozo",
    # EXPLAINED: break the bomb wall at left of Parlor and Alcatraz,
    #            open red door at Green Brinstar Main Shaft,
    #            mock ball for early retreval or speed booster
    # 'Available': lambda items: wand(wor(haveItem(items, 'SpeedBooster'),
    #                                     canDestroyBombWalls(items)),
    #                                 canOpenRedDoors(items),
    #                                 wor(wand(Knows.Mockball,
    #                                          haveItem(items, 'Morph')),
    #                                     haveItem(items, 'SpeedBooster')))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea': "Pink",
    'Name': "Charge Beam",
    'Class': "Major",
    'Address': 0x78614,
    'Visibility': "Chozo",
    # EXPLAINED: open red door at Green Brinstar Main Shaft (down right),
    #            break the bomb wall at left of Parlor and Alcatraz
    # 'Available': lambda items: wand(canOpenRedDoors(items),
    #                                 wor(canPassBombPassages(items),
    #                                     canUsePowerBombs(items)))
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "Brinstar",
    'SubArea' : "Blue",
    'Name': "Morphing Ball",
    'Class': "Major",
    'Address': 0x786DE,
    'Visibility': "Visible",
    # EXPLAINED: no difficulty
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea' : "Blue",
    'Name': "Energy Tank, Brinstar Ceiling",
    'Class': "Major",
    'Address': 0x7879E,
    'Visibility': "Hidden",
    # EXPLAINED: to get this major item the different technics are:
    #  -can fly (continuous bomb jump or space jump)
    #  -have the high jump boots
    #  -freeze the Reo to jump on it
    #  -do a damage boost with one of the two Geemers
    'Available': lambda items: wor(Knows.CeilingDBoost,
                                   canFly(items),
                                   haveItem(items, 'HiJump'),
                                   haveItem(items, 'Ice'))
},
{
    'Area': "Brinstar",
    'SubArea' : "Green",
    'Name': "Energy Tank, Etecoons",
    'Class': "Major",
    'Address': 0x787C2,
    'Visibility': "Visible",
    # EXPLAINED: break the bomb wall at left of Parlor and Alcatraz,
    #            power bomb down of Green Brinstar Main Shaft
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Brinstar",
    'SubArea' : "Pink",
    'Name': "Energy Tank, Waterway",
    'Class': "Major",
    'Address': 0x787FA,
    'Visibility': "Visible",
    # EXPLAINED: break the bomb wall at left of Parlor and Alcatraz with power bombs,
    #            open red door at Green Brinstar Main Shaft (down right),
    #            power bomb at bottom of Big Pink (Charge Beam),
    #            open red door leading to waterway,
    #            at waterway, either do:
    #  -with gravity do a speed charge
    #  -a simple short charge from the blocks above the water
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    canOpenRedDoors(items),
                                    haveItem(items, 'SpeedBooster'),
                                    wor(haveItem(items, 'Gravity'),
                                        Knows.SimpleShortCharge))
},
{
    'Area': "Brinstar",
    'SubArea' : "Pink",
    'Name': "Energy Tank, Brinstar Gate",
    'Class': "Major",
    'Address': 0x78824,
    'Visibility': "Visible",
    # DONE: use Knows.ReverseGateGlitch
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    wor(haveItem(items, 'Wave'),
                                        wand(haveItem(items, 'Super'),
                                             haveItem(items, 'HiJump'),
                                             Knows.ReverseGateGlitch)))
},
{
    'Area': "Brinstar",
    'SubArea' : "Red",
    'Name': "X-Ray Scope",
    'Class': "Major",
    'Address': 0x78876,
    'Visibility': "Chozo",
    # 'Available': lambda items: wand(canAccessRedBrinstar(items),
    #                                 canUsePowerBombs(items),
    #                                 wor(haveItem(items, 'Grapple'),
    #                                     haveItem(items, 'SpaceJump'),
    #                                     wand(haveItem(items, 'Varia'),
    #                                          energyReserveCountOk(items, 4),
    #                                          Knows.XrayDboost),
    #                                     wand(energyReserveCountOk(items, 6),
    #                                          Knows.XrayDboost)))
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    wor(haveItem(items, 'Grapple'),
                                        haveItem(items, 'SpaceJump'),
                                        wand(haveItem(items, 'Varia'),
                                             energyReserveCountOk(items, 4),
                                             Knows.XrayDboost),
                                        wand(energyReserveCountOk(items, 6),
                                             Knows.XrayDboost)))
},
{
    'Area': "Brinstar",
    'SubArea' : "Red/Bottom",
    'Name': "Spazer",
    'Class': "Major",
    'Address': 0x7896E,
    'Visibility': "Chozo",
    # DONE: no difficulty
#    'Available': lambda items: canAccessRedBrinstar(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea' : "Kraid",
    'Name': "Energy Tank, Kraid",
    'Class': "Major",
    'Address': 0x7899C,
    'Visibility': "Hidden",
    # DONE: no difficulty
#    'Available': lambda items: wand(canAccessKraid(items), Bosses.bossDead('Kraid'))
    'Available': lambda items: Bosses.bossDead('Kraid')
},
{
    'Area': "Brinstar",
    'SubArea' : "Kraid",
    'Name': "Varia Suit",
    'Class': "Major",
    'Address': 0x78ACA,
    'Visibility': "Chozo",
    # DONE: no difficulty
    # 'Available': lambda items: wand(canAccessKraid(items),
    #                                 enoughStuffsKraid(items)),
    'Available': lambda items: enoughStuffsKraid(items),
    'Pickup': lambda: Bosses.beatBoss('Kraid')
},
{
    'Area': "Norfair",
    'SubArea' : "Ice",
    'Name': "Ice Beam",
    'Class': "Major",
    'Address': 0x78B24,
    'Visibility': "Chozo",
    # DONE: harder without varia
    # 'Available': lambda items: wand(canAccessKraid(items),
    #                                 wor(heatProof(items),
    #                                     energyReserveCountOkList(items, Settings.hellRuns['Ice'])),
    #                                 wor(wand(haveItem(items, 'Morph'),
    #                                          Knows.Mockball),
    #                                     haveItem(items, 'SpeedBooster'))) # FIXME : Knows.EarlyKraid has nothing to do with this and is implied by canAccessKraid
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea' : "Crocomire",
    'Name': "Energy Tank, Crocomire",
    'Class': "Major",
    'Address': 0x78BA4,
    'Visibility': "Visible",
    # DONE: difficulty already set in canHellRun
#    'Available': lambda items: canAccessCrocomire(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Entrance",
    'Name': "Hi-Jump Boots",
    'Class': "Major",
    'Address': 0x78BAC,
    'Visibility': "Chozo",
    # DONE: no difficulty
#    'Available': lambda items: canAccessRedBrinstar(items)
    'Available': lambda items: canOpenRedDoors(items)
},
{
    'Area': "Norfair",
    'SubArea': "Crocomire",
    'Name': "Grapple Beam",
    'Class': "Major",
    'Address': 0x78C36,
    'Visibility': "Chozo",
    # 'Available': lambda items: wand(canAccessCrocomire(items),
    #                                 wor(canFly(items),
    #                                     wand(haveItem(items, 'Ice'),
    #                                          Knows.ClimbToGrappleWithIce),
    #                                     haveItem(items, 'SpeedBooster'),
    #                                     Knows.GreenGateGlitch))
    'Available': lambda items: wor(canFly(items),
                                   wand(haveItem(items, 'Ice'),
                                        Knows.ClimbToGrappleWithIce),
                                   haveItem(items, 'SpeedBooster'),
                                   wand(haveItem(items, 'Super'), Knows.GreenGateGlitch))
},
{
    'Area': "Norfair",
    'SubArea' : "Reserve",
    'Name': "Reserve Tank, Norfair",
    'Class': "Major",
    'Address': 0x78C3E,
    'Visibility': "Chozo",
    # TODO: also Ice to freeze a Waver
    # 'Available': lambda items: wand(canAccessHeatedNorfair(items),
    #                                 wor(canFly(items),
    #                                     haveItem(items, 'Grapple'),
    #                                     wand(haveItem(items, 'HiJump'),
    #                                          Knows.NorfairReserveHiJump)))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Speed",
    'Name': "Speed Booster",
    'Class': "Major",
    'Address': 0x78C82,
    'Visibility': "Chozo",
    # DONE: difficulty already done in the function
#    'Available': lambda items: canAccessHeatedNorfair(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Wave",
    'Name': "Wave Beam",
    'Class': "Major",
    'Address': 0x78CCA,
    'Visibility': "Chozo",
    # DONE: this one is not easy without grapple beam nor space jump, with hijump medium wall jump is required
    # FLO : no need of high jump for this, just wall jumping
    # 'Available': lambda items: wand(canAccessHeatedNorfair(items),
    #                                 wor(haveItem(items, 'Grapple'),
    #                                     haveItem(items, 'SpaceJump'),
    #                                     Knows.WaveBeamWallJump))
    'Available': lambda items: wor(haveItem(items, 'Grapple'),
                                   haveItem(items, 'SpaceJump'),
                                   Knows.WaveBeamWallJump)
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Energy Tank, Ridley",
    'Class': "Major",
    'Address': 0x79108,
    'Visibility': "Hidden",
    # DONE: already set in function
    # 'Available': lambda items: wand(canPassWorstRoom(items),
    #                                 enoughStuffsRidley(items)),
    'Available': lambda items: enoughStuffsRidley(items)),
    'Pickup': lambda: Bosses.beatBoss('Ridley')
},
{
    'Area': "LowerNorfair",
    'SubArea': "ScrewAttack",
    'Name': "Screw Attack",
    'Class': "Major",
    'Address': 0x79110,
    'Visibility': "Chozo",
    # DONE: easy with green gate glitch TODO add exit conditions
    # 'Available': lambda items: wand(canAccessLowerNorfair(items),
    #                                 wor(haveItem(items, 'SpaceJump'),
    #                                     Knows.GreenGateGlitch))
    'Available': lambda items: (True, 0) 
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Energy Tank, Firefleas",
    'Class': "Major",
    'Address': 0x79184,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "WreckedShip",
    'SubArea': "Gravity",
    'Name': "Reserve Tank, Wrecked Ship",
    'Class': "Major",
    'Address': 0x7C2E9,
    'Visibility': "Chozo",
    # DONE: easy
    # 'Available': lambda items: wand(canAccessWs(items),
    #                                 haveItem(items, 'SpeedBooster'),
    #                                 wor(haveItem(items, 'Varia'),
    #                                     energyReserveCountOk(items, 1)),
    #                                 Bosses.bossDead('Phantoon'))
    'Available': lambda items: haveItem(items, 'SpeedBooster')
},
{
    'Area': "WreckedShip",
    'SubArea': "Back",
    'Name': "Energy Tank, Wrecked Ship",
    'Class': "Major",
    'Address': 0x7C337,
    'Visibility': "Visible",    
    # 'Available': lambda items: wand(canAccessWs(items),
    #                                 Bosses.bossDead('Phantoon'),
    #                                 wor(wor(haveItem(items, 'Bomb'),
    #                                         haveItem(items, 'PowerBomb')),
    #                                     Knows.SpongeBathBombJump,
    #                                     wand(haveItem(items, 'HiJump'),
    #                                          Knows.SpongeBathHiJump),
    #                                     wor(haveItem(items, 'SpaceJump', difficulty=easy),
    #                                         wand(haveItem(items, 'SpeedBooster'),
    #                                              Knows.SpongeBathSpeed),
    #                                         wand(haveItem(items, 'SpringBall'),
    #                                              Knows.SpringBallJump))))
    'Available': lambda items: wand(Bosses.bossDead('Phantoon'),
                                    wor(haveItem(items, 'Grapple'),
                                        haveItem(items, 'SpeedBooster'),
                                        haveItem(items, 'Gravity'),
                                        Knows.JumpToWsEtank))
},
{
    'Area': "WreckedShip",
    'SubArea': "Main",
    'Name': "Right Super, Wrecked Ship",
    'Class': "Major",
    'Address': 0x7C365,
    'Visibility': "Visible",
    # DONE: easy once WS is accessible
    # 'Available': lambda items: wand(canAccessWs(items),
    #                                 enoughStuffsPhantoon(items)),
    'Available': lambda items: enoughStuffsPhantoon(items),
    'Pickup': lambda: Bosses.beatBoss('Phantoon')
},
{
    'Area': "WreckedShip",
    'SubArea': "Gravity",
    'Name': "Gravity Suit",
    'Class': "Major",
    'Address': 0x7C36D,
    'Visibility': "Chozo",
    # DONE: easy
    # 'Available': lambda items: wand(canAccessWs(items),
    #                                 Bosses.bossDead('Phantoon'),
    #                                 wor(haveItem(items, 'Varia'),
    #                                     energyReserveCountOk(items, 1)))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Green",
    'Name': "Energy Tank, Mama turtle",
    'Class': "Major",
    'Address': 0x7C47D,
    'Visibility': "Visible",
    # DONE: difficulty already handled in canAccessOuterMaridia
    # to acces the ETank in higher part of the room:
    #  -use grapple to attach to the block
    #  -use speedbooster ??
    #  FIXME: is SpeedBooster possible without gravity in this room ? is it a simple short or short charge ?
    #  -can fly (space jump or infinite bomb jump)
    #  FIXME: is it possible to infinite bomb jump from the mama turtle when it's up ?
    # 'Available': lambda items: wand(canAccessOuterMaridia(items),
    #                                 wor(canFly(items),
    #                                     haveItem(items, 'SpeedBooster'),
    #                                     haveItem(items, 'Grapple')))
    'Available': lambda items: wor(canFly(items),
                                   haveItem(items, 'Grapple'),
                                   wand(haveItem(items, 'Gravity'), haveItem(items, 'SpeedBooster')))
},
{
    'Area': "Maridia",
    'SubArea': "ForgottenHighway",
    'Name': "Plasma Beam",
    'Class': "Major",
    'Address': 0x7C559,
    'Visibility': "Chozo",
    # DONE: to leave the Plasma Beam room you have to kill the space pirates and return to the door
    # to unlock the door:
    #  -can access draygon room to kill him
    # to kill the space pirates:
    #  -do short charges with speedbooster
    #  -do beam charges with spin jump attacks
    #  -have screw attack
    #  -have plasma beam
    # to go back to the door:
    #  -have high jump boots
    #  -can fly (space jump or infinite bomb jump)
    #  -use short charge with speedbooster
    # 'Available': lambda items: wand(canDefeatDraygon(items),
    #                                 Bosses.bossDead('Draygon'),
    #                                 wor(wand(haveItem(items, 'SpeedBooster'),
    #                                          Knows.ShortCharge,
    #                                          Knows.KillPlasmaPiratesWithSpark),
    #                                     wand(haveItem(items, 'Charge'),
    #                                          Knows.KillPlasmaPiratesWithCharge),
    #                                     haveItem(items, 'ScrewAttack', difficulty=easy),
    #                                     haveItem(items, 'Plasma', difficulty=easy)),
    #                                 wor(canFly(items),
    #                                     wand(haveItem(items, 'HiJump'),
    #                                          Knows.ExitPlasmaRoomHiJump),
    #                                     wand(haveItem(items, 'SpeedBooster'),
    #                                          Knows.ShortCharge)))
    'Available': lambda items: wand(Bosses.bossDead('Draygon'),
                                    wor(wand(haveItem(items, 'SpeedBooster'),
                                             Knows.ShortCharge,
                                             Knows.KillPlasmaPiratesWithSpark),
                                        wand(haveItem(items, 'Charge'),
                                             Knows.KillPlasmaPiratesWithCharge),
                                        haveItem(items, 'ScrewAttack'),
                                        haveItem(items, 'Plasma')),
                                    wor(canFly(items),
                                        wand(haveItem(items, 'HiJump'),
                                             Knows.ExitPlasmaRoomHiJump),
                                        wand(haveItem(items, 'SpeedBooster'),
                                             Knows.ShortCharge)))
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Reserve Tank, Maridia",
    'Class': "Major",
    'Address': 0x7C5E3,
    'Visibility': "Chozo",
    # DONE: this item can be taken without gravity, but it's super hard because of the quick sands...
    # 'Available': lambda items: wand(canAccessOuterMaridia(items),
    #                                 wor(haveItem(items, 'Gravity'),
    #                                     wand(canDoSuitlessMaridia(items),
    #                                          Knows.SuitlessSandpit)))
    'Available': lambda items: wor(haveItem(items, 'Gravity'),
                                   Knows.SuitlessSandpit)
},
{
    'Area': "Maridia",
    'SubArea': "Sandpits",
    'Name': "Spring Ball",
    'Class': "Major",
    'Address': 0x7C6E5,
    'Visibility': "Chozo",
    # DONE: handle puyo clip and diagonal bomb jump
    # to access the spring ball you can either:
    #  -use the puyo clip with ice
    #  -use the grapple to destroy the block and then:
    #    -use high boots jump
    #    -fly (with space jump or diagonal bomb jump
    # 'Available': lambda items: wand(canAccessInnerMaridia(items),
    #                                 wor(wand(haveItem(items, 'Ice'),
    #                                          Knows.PuyoClip),
    #                                     wand(haveItem(items, 'Grapple'),
    #                                          wor(canFlyDiagonally(items),
    #                                              haveItem(items, 'HiJump')))))
    'Available': lambda items: wor(wand(haveItem(items, 'Ice'),
                                        Knows.PuyoClip),
                                   wand(haveItem(items, 'Grapple'),
                                        wor(canFlyDiagonally(items),
                                            haveItem(items, 'HiJump'))))
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Top",
    'Name': "Energy Tank, Botwoon",
    'Class': "Major",
    'Address': 0x7C755,
    'Visibility': "Visible",
    # DONE: difficulty already handled in the functions
#    'Available': lambda items: canDefeatBotwoon(items)
    'Available': lambda items: (True, 0) # FIXME add botwoon difficulty?
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Top",
    'Name': "Space Jump",
    'Class': "Major",
    'Address': 0x7C7A7,
    'Visibility': "Chozo",
    # DONE: difficulty already handled in the function,
    # we need to have access to the boss and enough stuff to kill him
    # 'Available': lambda items: wand(canDefeatDraygon(items),
    #                                 enoughStuffsDraygon(items)),
    'Available': lambda items: haveItem(items, 'Gravity'),
    'Pickup': lambda: Bosses.beatBoss('Draygon')
},
{
    'Area': "Crateria",
    'SubArea': "LandingSite",
    'Name': "Power Bomb (Crateria surface)",
    'Class': "Minor",
    'Address': 0x781CC,
    'Visibility': "Visible",
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    wor(haveItem(items, 'SpeedBooster'),
                                        canFly(items)))
},
{
    'Area': "Crateria",
    'SubArea': "WreckedShipBottom",
    'Name': "Missile (outside Wrecked Ship bottom)",
    'Class': "Minor",
    'Address': 0x781E8,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Crateria",
    'SubArea': "WreckedShipTop",
    'Name': "Missile (outside Wrecked Ship top)",
    'Class': "Minor",
    'Address': 0x781EE,
    'Visibility': "Hidden",
#    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Crateria",
    'SubArea': "WreckedShipTop",
    'Name': "Missile (outside Wrecked Ship middle)",
    'Class': "Minor",
    'Address': 0x781F4,
    'Visibility': "Visible",
    #    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Crateria",
    'SubArea': "LandingSite",
    'Name': "Missile (Crateria moat)",
    'Class': "Minor",
    'Address': 0x78248,
    'Visibility': "Visible",
    # it's before actual wrecked ship access
    # 'Available': lambda items: wand(haveItem(items, 'Super'),
    #                                 canDestroyBombWalls(items)) # no need to destroy bomb walls with wall jumps up
    'Available': lambda items: haveItem(items, 'Super')
},
{
    'Area': "Crateria",
    'SubArea': "LandingSite",
    'Name': "Missile (Crateria bottom)",
    'Class': "Minor",
    'Address': 0x783EE,
    'Visibility': "Visible",
    'Available': lambda items: canDestroyBombWalls(items)
},
{
    'Area': "Crateria",
    'SubArea': "Gauntlet",
    'Name': "Missile (Crateria gauntlet right)",
    'Class': "Minor",
    'Address': 0x78464,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canEnterAndLeaveGauntlet(items),
    #                                 canPassBombPassages(items))
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "Crateria",
    'SubArea': "Gauntlet",
    'Name': "Missile (Crateria gauntlet left)",
    'Class': "Minor",
    'Address': 0x7846A,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canEnterAndLeaveGauntlet(items),
    #                                 canPassBombPassages(items))
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "Crateria",
    'SubArea': "LandingSite",
    'Name': "Super Missile (Crateria)",
    'Class': "Minor",
    'Address': 0x78478,
    'Visibility': "Visible",
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    haveItem(items, 'SpeedBooster'),
                                    wor(haveItem(items, 'Ice'),
                                        Knows.ShortCharge))
},
{
    'Area': "Crateria",
    'SubArea': "LandingSite",
    'Name': "Missile (Crateria middle)",
    'Class': "Minor",
    'Address': 0x78486,
    'Visibility': "Visible",
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Green",
    'Name': "Power Bomb (green Brinstar bottom)",
    'Class': "Minor",
    'Address': 0x784AC,
    'Visibility': "Chozo",
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Pink",
    'Name': "Super Missile (pink Brinstar)",
    'Class': "Minor",
    'Address': 0x784E4,
    'Visibility': "Chozo",
    # brinstar access, and
    # either you go the back way, using a super and the camera glitch,
    # or just beat spore spawn (so no Knows* setting needed for the glitch)
    # 'Available': lambda items: wand(wor(haveItem(items, 'SpeedBooster'),
    #                                     canDestroyBombWalls(items)),
    #                                 canOpenRedDoors(items),
    #                                 wor(wand(canPassBombPassages(items),
    #                                          haveItem(items, 'Super')),
    #                                     (True, easy)))
    'Available': lambda items: wor(wand(canPassBombPassages(items),
                                        haveItem(items, 'Super')),
                                   (True, easy))
},
{
    'Area': "Brinstar",
    'SubArea': "Green",
    'Name': "Missile (green Brinstar below super missile)",
    'Class': "Minor",
    'Address': 0x78518,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canPassBombPassages(items),
    #                                 canOpenRedDoors(items))
    'Available': lambda items: canOpenRedDoors(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Reserve",
    'Name': "Super Missile (green Brinstar top)",
    'Class': "Minor",
    'Address': 0x7851E,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(wor(haveItem(items, 'SpeedBooster'),
    #                                     canDestroyBombWalls(items)),
    #                                 canOpenRedDoors(items),
    #                                 wor(wand(haveItem(items, 'Morph'), Knows.Mockball),
    #                                     haveItem(items, 'SpeedBooster')))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea': "Reserve",
    'Name': "Missile (green Brinstar behind missile)",
    'Class': "Minor",
    'Address': 0x78532,
    'Visibility': "Hidden",
    # 'Available': lambda items: wand(canPassBombPassages(items),
    #                                 canOpenRedDoors(items),
    #                                 wor(wand(haveItem(items, 'Morph'), Knows.Mockball),
    #                                     haveItem(items, 'SpeedBooster')))
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Reserve",
    'Name': "Missile (green Brinstar behind reserve tank)",
    'Class': "Minor",
    'Address': 0x78538,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(wor(haveItem(items, 'SpeedBooster'),
    #                                     canDestroyBombWalls(items)),
    #                                 canOpenRedDoors(items),
    #                                 haveItem(items, 'Morph'),
    #                                 wor(Knows.Mockball,
    #                                     haveItem(items, 'SpeedBooster')))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea': "Pink",
    'Name': "Missile (pink Brinstar top)",
    'Class': "Minor",
    'Address': 0x78608,
    'Visibility': "Visible",
    # 'Available': lambda items: wor(wand(canDestroyBombWalls(items),
    #                                     canOpenRedDoors(items)),
    #                                canUsePowerBombs(items))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea': "Pink",
    'Name': "Missile (pink Brinstar bottom)",
    'Class': "Minor",
    'Address': 0x7860E,
    'Visibility': "Visible",
    # 'Available': lambda items: wor(wand(wor(haveItem(items, 'SpeedBooster'),
    #                                         canDestroyBombWalls(items)),
    #                                     canOpenRedDoors(items)),
    #                                canUsePowerBombs(items))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea' : "Pink",
    'Name': "Power Bomb (pink Brinstar)",
    'Class': "Minor",
    'Address': 0x7865C,
    'Visibility': "Visible",
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    haveItem(items, 'Super'))
},
{
    'Area': "Brinstar",
    'SubArea': "Hills",
    'Name': "Missile (green Brinstar pipe)",
    'Class': "Minor",
    'Address': 0x78676,
    'Visibility': "Visible",
    # 'Available': lambda items: wor(wand(canPassBombPassages(items),
    #                                     canOpenGreenDoors(items)),
    #                                canUsePowerBombs(items))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Brinstar",
    'SubArea': "Blue",
    'Name': "Power Bomb (blue Brinstar)",
    'Class': "Minor",
    'Address': 0x7874C,
    'Visibility': "Visible",
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Blue",
    'Name': "Missile (blue Brinstar middle)",
    'Address': 0x78798,
    'Class': "Minor",
    'Visibility': "Visible",
    'Available': lambda items: haveItem(items, 'Morph')
},
{
    'Area': "Brinstar",
    'SubArea': "Green",
    'Name': "Super Missile (green Brinstar bottom)",
    'Class': "Minor",
    'Address': 0x787D0,
    'Visibility': "Visible",
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    canOpenGreenDoors(items))
},
{
    'Area': "Brinstar",
    'SubArea': "Blue",
    'Name': "Missile (blue Brinstar bottom)",
    'Class': "Minor",
    'Address': 0x78802,
    'Visibility': "Chozo",
    'Available': lambda items: haveItem(items, 'Morph')
},
{
    'Area': "Brinstar",
    'SubArea': "Blue",
    'Name': "Missile (blue Brinstar top)",
    'Class': "Minor",
    'Address': 0x78836,
    'Visibility': "Visible",
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Blue",
    'Name': "Missile (blue Brinstar behind missile)",
    'Class': "Minor",
    'Address': 0x7883C,
    'Visibility': "Hidden",
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Red/Top",
    'Name': "Power Bomb (red Brinstar sidehopper room)",
    'Class': "Minor",
    'Address': 0x788CA,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessRedBrinstar(items),
    #                                 canUsePowerBombs(items))
    'Available': lambda items: wand(canOpenGreenDoors(items), canUsePowerBombs(items))
},
{
    'Area': "Brinstar",
    'SubArea': "Red/Top",
    'Name': "Power Bomb (red Brinstar spike room)",
    'Class': "Minor",
    'Address': 0x7890E,
    'Visibility': "Chozo",
    # can access from red brinstar lower or upper
    # from upper: power bomb
    # from lower: ice or screw or climb red tower
    # 'Available': lambda items: wand(canAccessRedBrinstar(items),
    #                                 wor(canUsePowerBombs(items),
    #                                     Knows.RedTowerClimb,
    #                                     haveItem(items, 'Ice'),
    #                                     haveItem(items, 'ScrewAttack')))
    'Available': lambda items: canOpenGreenDoors(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Red/Top",
    'Name': "Missile (red Brinstar spike room)",
    'Class': "Minor",
    'Address': 0x78914,
    'Visibility': "Visible",
    # same as "Power Bomb (red Brinstar spike room)"
    # 'Available': lambda items: wand(canAccessRedBrinstar(items),
    #                                 wor(canUsePowerBombs(items),
    #                                     Knows.RedTowerClimb,
    #                                     haveItem(items, 'Ice'),
    #                                     haveItem(items, 'ScrewAttack')))
    'Available': lambda items: canOpenGreenDoors(items)
},
{
    'Area': "Brinstar",
    'SubArea': "Kraid",
    'Name': "Missile (Kraid)",
    'Class': "Minor",
    'Address': 0x789EC,
    'Visibility': "Hidden",
    # 'Available': lambda items: wand(canAccessKraid(items),
    #                                 canUsePowerBombs(items))
    'Available': lambda items: canUsePowerBombs(items)
},
{
    'Area': "Norfair",
    'SubArea': "Entrance", # FIXME create an area for this ??
    'Name': "Missile (lava room)",
    'Class': "Minor",
    'Address': 0x78AE4,
    'Visibility': "Hidden",
#    'Available': lambda items: canAccessHeatedNorfair(items)
    'Available': lambda items: canHellRun(items)
},
{
    'Area': "Norfair",
    'SubArea': 'Ice',
    'Name': "Missile (below Ice Beam)",
    'Class': "Minor",
    'Address': 0x78B46,
    'Visibility': "Hidden",
    # 'Available': lambda items: wand(canAccessKraid(items),
    #                                 canUsePowerBombs(items),
    #                                 canHellRun(items))
    'Available': lambda items: wand(canUsePowerBombs(items),
                                    canHellRun(items))
},
{
    'Area': "Norfair",
    'SubArea': "GrappleEscape",
    'Name': "Missile (above Crocomire)",
    'Class': "Minor",
    'Address': 0x78BC0,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessCrocomire(items),
    #                                 wor(canFly(items), haveItem(items, 'Grapple'),
    #                                     wand(haveItem(items, 'HiJump'),
    #                                          haveItem(items, 'SpeedBooster'))))
    'Available': lambda items: (True, 0) # FIXME count this in grapple escape transition???
},
{
    'Area': "Norfair",
    'SubArea': "Entrance",
    'Name': "Missile (Hi-Jump Boots)",
    'Class': "Minor",
    'Address': 0x78BE6,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessRedBrinstar(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Entrance",
    'Name': "Energy Tank (Hi-Jump Boots)",
    'Class': "Minor",
    'Address': 0x78BEC,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessRedBrinstar(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Crocomire",
    'Name': "Power Bomb (Crocomire)",
    'Class': "Minor",
    'Address': 0x78C04,
    'Visibility': "Visible",
    'Available': lambda items:  wor(canFly(items),
                                    haveItem(items, 'Grapple'),
                                    wand(haveItem(items, 'HiJump'),
                                         haveItem(items, 'SpeedBooster')))

},
{
    'Area': "Norfair",
    'SubArea': "Crocomire",
    'Name': "Missile (below Crocomire)",
    'Class': "Minor",
    'Address': 0x78C14,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessCrocomire(items)
    'Available': lambda items: (True 0) # FIXME WTF is this item??
},
{
    'Area': "Norfair",
    'SubArea': "Crocomire",
    'Name': "Missile (Grapple Beam)",
    'Class': "Minor",
    'Address': 0x78C2A,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessCrocomire(items),
    #                                 wor(canFly(items), haveItem(items, 'Grapple'),
    #                                     haveItem(items, 'SpeedBooster')))
    'Available': lambda items: wor(canFly(items), haveItem(items, 'Grapple'),
                                   haveItem(items, 'SpeedBooster'))
},
{
    'Area': "Norfair",
    'SubArea': "Reserve",
    'Name': "Missile (Norfair Reserve Tank)",
    'Class': "Minor",
    'Address': 0x78C44,
    'Visibility': "Hidden",
    # 'Available': lambda items: wand(canAccessHeatedNorfair(items),
    #                                 wor(canFly(items), haveItem(items, 'Grapple'),
    #                                     wand(haveItem(items, 'HiJump'), Knows.NorfairReserveHiJump)))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Reserve",
    'Name': "Missile (bubble Norfair green door)",
    'Class': "Minor",
    'Address': 0x78C52,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessHeatedNorfair(items),
    #                                 wor(canFly(items), haveItem(items, 'Grapple'),
    #                                     wand(haveItem(items, 'HiJump'), Knows.NorfairReserveHiJump)))
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Bubble/Bottom",
    'Name': "Missile (bubble Norfair)",
    'Class': "Minor",
    'Address': 0x78C66,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessHeatedNorfair(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Speed",
    'Name': "Missile (Speed Booster)",
    'Class': "Minor",
    'Address': 0x78C74,
    'Visibility': "Hidden",
#    'Available': lambda items: canAccessHeatedNorfair(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Norfair",
    'SubArea': "Wave",
    'Name': "Missile (Wave Beam)",
    'Class': "Minor",
    'Address': 0x78CBC,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessHeatedNorfair(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': 'ScrewAttack',
    'Name': "Missile (Gold Torizo)",
    'Class': "Minor",
    'Address': 0x78E6E,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessLowerNorfair(items),
    #                                 haveItem(items, 'SpaceJump'))
    'Available': lambda items: haveItem(items, 'SpaceJump')
},
{
    'Area': "LowerNorfair",
    'SubArea': "ScrewAttack",
    'Name': "Super Missile (Gold Torizo)",
    'Class': "Minor",
    'Address': 0x78E74,
    'Visibility': "Hidden",
    # 'Available': lambda items: wand(canAccessLowerNorfair(items),
    #                                 wor(haveItem(items, 'SpaceJump'),
    #                                     Knows.GreenGateGlitch))
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': "BeforeAmphitheater",
    'Name': "Missile (Mickey Mouse room)",
    'Class': "Minor",
    'Address': 0x78F30,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Missile (lower Norfair above fire flea room)",
    'Class': "Minor",
    'Address': 0x78FCA,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Power Bomb (lower Norfair above fire flea room)",
    'Class': "Minor",
    'Address': 0x78FD2,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Power Bomb (Power Bombs of shame)",
    'Class': "Minor",
    'Address': 0x790C0,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "LowerNorfair",
    'SubArea': "AfterAmphitheater",
    'Name': "Missile (lower Norfair near Wave Beam)",
    'Class': "Minor",
    'Address': 0x79100,
    'Visibility': "Visible",
#    'Available': lambda items: canPassWorstRoom(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "WreckedShip",
    'SubArea': "Main",
    'Name': "Missile (Wrecked Ship middle)",
    'Class': "Minor",
    'Address': 0x7C265,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "WreckedShip",
    'SubArea': "Gravity",
    'Name': "Missile (Gravity Suit)",
    'Class': "Minor",
    'Address': 0x7C2EF,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessWs(items),
    #                                 wor(haveItem(items, 'Varia'),
    #                                     energyReserveCountOk(items, 1)))
    'Available': lambda items: canPassBombPassages(items)
},
{
    'Area': "WreckedShip",
    'SubArea': "Top",
    'Name': "Missile (Wrecked Ship top)",
    'Class': "Minor",
    'Address': 0x7C319,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "WreckedShip",
    'SubArea': "Main",
    'Name': "Super Missile (Wrecked Ship left)",
    'Class': "Minor",
    'Address': 0x7C357,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessWs(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Green",
    'Name': "Missile (green Maridia shinespark)",
    'Class': "Minor",
    'Address': 0x7C437,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessRedBrinstar(items),
    #                                 canUsePowerBombs(items),
    #                                 haveItem(items, 'Gravity'),
    #                                 haveItem(items, 'SpeedBooster'))
    'Available': lambda items: wand(haveItem(items, 'Gravity'),
                                    haveItem(items, 'SpeedBooster'))
},
{
    'Area': "Maridia",
    'SubArea': "Green",
    'Name': "Super Missile (green Maridia)",
    'Class': "Minor",
    'Address': 0x7C43D,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessOuterMaridia(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Green",
    'Name': "Missile (green Maridia tatori)",
    'Class': "Minor",
    'Address': 0x7C483,
    'Visibility': "Hidden",
#    'Available': lambda items: canAccessOuterMaridia(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Super Missile (yellow Maridia)",
    'Class': "Minor",
    'Address': 0x7C4AF,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessInnerMaridia(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Missile (yellow Maridia super missile)",
    'Class': "Minor",
    'Address': 0x7C4B5,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessInnerMaridia(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Missile (yellow Maridia false wall)",
    'Class': "Minor",
    'Address': 0x7C533,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessInnerMaridia(items)
    'Available': lambda items: (True, 0)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Missile (left Maridia sand pit room)",
    'Class': "Minor",
    'Address': 0x7C5DD,
    'Visibility': "Visible",
#    'Available': lambda items: canAccessInnerMaridia(items)
    'Available': lambda items: wor(haveItem(items, 'Gravity'),
                                   Knows.SuitlessSandpit)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Missile (right Maridia sand pit room)",
    'Class': "Minor",
    'Address': 0x7C5EB,
    'Visibility': "Visible",
    'Available': lambda items: wor(haveItem(items, 'Gravity'),
                                   Knows.SuitlessSandpit)
#    'Available': lambda items: canAccessInnerMaridia(items)
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Power Bomb (right Maridia sand pit room)",
    'Class': "Minor",
    'Address': 0x7C5F1,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessOuterMaridia(items),
    #                                 haveItem(items, 'Gravity'))
    'Available': lambda items: haveItem(items, 'Gravity')
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Missile (pink Maridia)",
    'Address': 0x7C603,
    'Class': "Minor",
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessOuterMaridia(items),
    #                                 haveItem(items, 'Gravity'))
    'Available': lambda items: wand(haveItem(items, 'Gravity'), haveItem(items, 'SpeedBooster'))
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Bottom",
    'Name': "Super Missile (pink Maridia)",
    'Class': "Minor",
    'Address': 0x7C609,
    'Visibility': "Visible",
    # 'Available': lambda items: wand(canAccessOuterMaridia(items),
    #                                 haveItem(items, 'Gravity'))
    'Available': lambda items: wand(haveItem(items, 'Gravity'), haveItem(items, 'SpeedBooster'))
},
{
    'Area': "Maridia",
    'SubArea': "Pink/Top",
    'Name': "Missile (Draygon)",
    'Class': "Minor",
    'Address': 0x7C74D,
    'Visibility': "Hidden",
#    'Available': lambda items: canDefeatBotwoon(items)
    'Available': lambda items: (True, 0)
}
]
