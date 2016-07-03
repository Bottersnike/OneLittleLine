global screenFuzz


version = "Pre Alpha 0.1.7"
deployment = False
fancyGraphics = True
demo = False
warnSaveVersion = False
gameSaveVersion = -1
gsv = 2

fullscreen = False

gameName = 'One Little Line'
subTitle = 'One Massive Journey'


from Box2D import *
from base64 import b64decode as b64d
import math
import time
import sys
import os
import tempfile
import cPickle
import random
if deployment: import pygame._view
import pygame
import os
from font import fontData
import pygame.gfxdraw as gfx


GLOBALDATA = {'summonParticles': []}



savePath = 'game.dat' if not deployment else '%s/BallRollerThing.dat' % os.environ['APPDATA']


def decry(d):
    return cPickle.loads(d)

def save():
    def encry(d):
        return cPickle.dumps(d)

    data = [gameSaveVersion, gameSettings, achievements, achievementsData]
    open(savePath, 'w').write(encry(data).replace('\n', '\\n'))

def reset():
    global gameSaveVersion
    global gameSettings
    global achievementsData
    global achievements

    gameSettings = {
        'PPM': 20.0,
        'GSS': 0.5,
        'PAR': 10,
    }

    achievementsData = {
                        'CurrPage': 'TS', #GAME, TS, HTP1, HTP2, OPT, DESC, PAUSE, GAMEOVER
                        'CurrDist': -1,
                        'CurrSpeed': -1,
                        'CurrTime': -1,
                        'AlltimeDist': 0,
                        'AlltimeSpees': 0,
                        'HighScoreDist': 0,
                        'HighScoreSpeed': 0,
                        'EndDist': -1,
                        'EndSpeed': -1,
                        'EndTime': -1,
                        }

    achievements = [
                    ['First Game', 'Play your first game',
                     False,
                     'achievementsData["CurrPage"][:4]=="GAME";achievements[0][2]==False'],
                    ['Far Roll', 'Roll 2k in one game',
                     False,
                     'achievementsData["CurrDist"]>=2000; achievements[1][2]==False'],
                    ['Farther Roll', 'Roll 5k in one game',
                     False,
                     'achievementsData["CurrDist"]>=5000; achievements[2][2]==False'],
                    ['Usain Bolt', 'Get a speed of over 10 m/s',
                     False,
                     'achievementsData["EndSpeed"]>=10; achievements[3][2]==False'],
                    ['Maths Wizz', 'Get a score of 3141m',
                     False,
                     'achievementsData["EndDist"]==3141; achievements[4][2]==False'],
                    ['Customizer', 'Change the settings',
                     False,
                     'achievementsData["CurrPage"]=="OPT";achievements[5][2]==False'],
                    ['Quick Learner', 'Read the tutorial',
                     False,
                     'achievementsData["CurrPage"]=="HTP1";achievements[6][2]==False'],
                    ['Over Achiver', 'Get all other achevements',
                     False,
                     'all([i[2] for i in achievements if i[0] != "Over Achiver"]);achievements[7][2]==False'],
                   ]

    lvls = os.listdir('levels')
    levels = []
    for i in lvls:
        if i[-4:] == '.lvl':
            path = i
            data = open('levels/%s' % i).read()
            data = data.replace('\n', '')
            data = data.split('##')
            while '' in data:
                data.remove('')
            levelNo = eval(data[0])
            levelUnlocked = bool(eval(data[1]))
            levelData = []
            for i in data[2].split(';'):
                if i:
                    levelData.append(eval(i))
            levels.append((levelNo, levelData, levelUnlocked, path))
    levels.sort()
    for n, l in enumerate(levels):
        if n != 0:
            nl = (l[0], l[1], False, l[3])
            levels[n] = nl
    for d in levels:
        s = '##\n%d\n##\n%r\n##\n' % (d[0], d[2])
        s2 = ''
        for i in d[1]:
            s2 += '%d,%d,\'%s\';\n' % i
        s += s2
        open('levels/%s' % d[3], 'w').write(s)
    gameSaveVersion = gsv

    save()

try: #Try to find a game save...
    data = decry(open(savePath).read().replace('\\n', '\n'))
    [gameSaveVersion, gameSettings, achievements, achievementsData] = data
    print gameSettings
    if gameSaveVersion < gsv:
        warnSaveVersion = True
except: #But if there isn't one, create a new one
    reset()

    screen_size = [0, 0]




#Create the surface for the corner rounding
screenFuzz = pygame.Surface((32, 32))

global screen_size
#More globals
screen_size = [0, 0]
messages = []
achives = []
msgTime = 420
msgFreq = 20
pygame.time.set_timer(27, msgFreq)

#Initilise pygame
pygame.init()

#Create the font
if deployment:
    fontPath = "data/font.ttf"
else:
    fontPath = tempfile.mktemp()
    open(fontPath, 'w').write(b64d(fontData.strip('\n')))

global gameSettings


def line(surf, col, p1, p2, w):
    if fancyGraphics:
        cx = (p1[0] + p2[0]) / 2
        cy = (p1[1] + p2[1]) / 2
        w /= 2.
        length = math.sqrt(abs(p1[0]-p2[0])**2 + abs(p1[1]-p2[1])**2)
        angle = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
        UL = (
              cx + (length / 2.) * math.cos(angle) - (w / 2.) * math.sin(angle),
              cy + (w / 2.) * math.cos(angle) + (length / 2.) * math.sin(angle)
             )
        UR = (
              cx - (length / 2.) * math.cos(angle) - (w / 2.) * math.sin(angle),
              cy + (w / 2.) * math.cos(angle) - (length / 2.) * math.sin(angle)
             )
        BL = (
              cx + (length / 2.) * math.cos(angle) + (w / 2.) * math.sin(angle),
              cy - (w / 2.) * math.cos(angle) + (length / 2.) * math.sin(angle)
             )
        BR = (
              cx - (length / 2.) * math.cos(angle) + (w / 2.) * math.sin(angle),
              cy - (2 / 2.) * math.cos(angle) - (length / 2.) * math.sin(angle)
             )
        __polygon(surf, col, [UL, UR, BR, BL])
    else:
        pygame.draw.line(surf, col, p1, p2, w)

def circle(surf, col, p1, r, solid=True):
    if fancyGraphics:
        gfx.aacircle(surf, p1[0], p1[1], r, col)
        if solid:
            gfx.filled_circle(surf, p1[0], p1[1], r, col)
    else:
        if solid:
            pygame.draw.circle(surf, col, p1, r)
        else:
            pygame.draw.circle(surf, col, p1, r, solid)

def polygon(surf, col, points, solid=True):
    if fancyGraphics:
        if solid == True:
            gfx.aapolygon(surf, points, col)
            gfx.filled_polygon(surf, points, col)
        else:
            for n, p in enumerate(points):
                p1 = p
                p2 = points[n+1 if n < len(points)-1 else 0]
                line(surf, col, p1, p2, solid)
    else:
        if solid == True:
            pygame.draw.polygon(surf, col, points)
        else:
            pygame.draw.polygon(surf, col, points, solid)

def __polygon(surf, col, points, solid=True):
    if fancyGraphics:
        gfx.aapolygon(surf, points, col)
        if solid==True:
            gfx.filled_polygon(surf, points, col)
    else:
        if solid == True:
            pygame.draw.polygon(surf, col, points)
        else:
            pygame.draw.polygon(surf, col, points, solid)

def rect(surf, col, rect, width=0):
    pygame.draw.rect(surf, col, rect, width)
    return

def dfxRect(surf, col, rect, width=True):
    if width == False:
        gfx.rectangle(surf, rect, col)
    else:
        p = []
        p.append((rect[0], rect[1]))
        p.append((rect[0]+rect[2], rect[1]))
        p.append((rect[0]+rect[2], rect[1]+rect[3]))
        p.append((rect[0], rect[1]+rect[3]))

        polygon(surf, col, p, width)
    return

def aarect(surf, col, rect):
    p = [
         (rect[0], rect[1]),
         (rect[0] + rect[2], rect[1]),
         (rect[0] + rect[2], rect[1] + rect[3]),
         (rect[0], rect[1] + rect[3])
        ]
    polygon(surf, col, p)


def screenshot(surface):
    try: #Check if the screenshots dir exists
        os.chdir('screenshots')
        os.chdir('..')
    except: #If it doesn't, make it
        os.mkdir('screenshots')
    d = int(round(time.time()*100))
    d = int(str(d)[3:])
    pygame.image.save(surface, 'screenshots/%d.png' % d)
    return 'screenshots/' + str(d) + '.png'

def runCmd(cmd):
    m = cmd.split(' ')
    if m[0] == 'get':
        if len(m) == 1:
            return
        else:
            try:
                a = int(m[1])
                if a < len(achievements) and not achievements[a][2]:
                    achievements[a][2] = True
                    messages.append(['Achivement Get: %s' % achievements[a][0], msgTime])
                else:
                    return
            except:
                return
    elif m[0] == 'unget':
        if len(m) == 1:
            return
        else:
            try:
                a = int(m[1])
                if a < len(achievements) and achievements[a][2]:
                    achievements[a][2] = False
                    messages.append(['Achivement Unget: %s' % achievements[a][0], msgTime])
                else:
                    return
            except:
                return

def test(case):
    #Test if an acchievement case has been met
    dat = case.split(';')
    while '' in dat:
        dat.remove('')
    check = []
    for i in dat:
        i = i.strip()
        check.append(eval(i))
    return all(check)

def checkForAchieves():
    #Enumerate through all the accheievements and check each one
    save()
    for n, i in enumerate(achievements):
        if test(i[3]):
            achievements[n][2] = True
            messages.append(['Achivement Get: %s' % i[0], msgTime])

def screenFlip(screen):
    #Update the screen applying 'shaders' in the process

    global screenFuzz

    if demo:
        polygon(screen, (20, 20, 20, 127), [(0, 0), (screen_size[0] / 6, 0), (0, screen_size[0] / 6)])
        t = pygame.font.Font(fontPath, screen_size[0] / 24).render('DEMO', 1, (230, 230, 230))
        t = pygame.transform.rotozoom(t, 45, 1)
        screen.blit(t, (0, 0))

    screen.blit(screenFuzz, (0, 0))
    pygame.display.flip()

def screenResize(screen_size):
    #Resize all assets when the screen size changes
    global screenFuzz
    screenFuzz = pygame.Surface(screen_size, depth=32).convert_alpha()
    r = pygame.Rect(0, 0, *screen_size)
    r.x -= 255 * (1.25 * 1)
    r.y -= 255 * (1.25 * 1)
    r.w += 255 * (2.5 * 1)
    r.h += 255 * (2.5 * 1)
    for x in range(255):
        r.x += 1
        r.y += 1
        r.w -= 2
        r.h -= 2
        x2 = 255 - x
        pygame.draw.ellipse(screenFuzz, (x, x, x, x2), r)

class MyContactListener(b2ContactListener):
    def BeginContact(self, contact):
        if contact.fixtureA == self.b1.fixtures[0]:
            GLOBALDATA['summonParticles'].append(self.b1)
        if contact.fixtureB == self.b1.fixtures[0]:
            GLOBALDATA['summonParticles'].append(self.b1)
        if contact.fixtureA == self.b2.fixtures[0]:
            GLOBALDATA['summonParticles'].append(self.b2)
        if contact.fixtureB == self.b2.fixtures[0]:
            GLOBALDATA['summonParticles'].append(self.b2)

class Particle(object):
    def __init__(self, pos, screen, sx, sy):
        self.col = (20, 20, 20)
        self.pos = (pos[0] * gameSettings['PPM'],
                    screen_size[1] - pos[1] * gameSettings['PPM'])
        self.xVel = random.randint(-100, 100) / 100.0
        self.yVel = random.randint(-100, -50) / 100.0
        self.fade = 50

    def tick(self):
        self.pos = (self.pos[0] + self.xVel, self.pos[1] + self.yVel)
        self.yVel += 0.1
        self.fade -= 1
        if self.fade <= 0:
            return False #Dead
        else:
            return True


def levelSelect(screen, fullscreen):
    achievementsData['CurrPage'] = 'LEVSEL'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    lvls = os.listdir('levels')
    levels = []
    for i in lvls:
        if i[-4:] == '.lvl':
            path = i
            data = open('levels/%s' % i).read()
            data = data.replace('\n', '')
            data = data.split('##')
            while '' in data:
                data.remove('')
            levelNo = eval(data[0])
            levelUnlocked = bool(eval(data[1]))
            levelData = []
            for i in data[2].split(';'):
                if i:
                    levelData.append(eval(i))
            levels.append((levelNo, levelData, levelUnlocked, path))
    levels.sort()

    ys = [0.5, 0.65, 0.75, 0.7, 0.6, 0.45, 0.3, 0.2, 0.25, 0.4]
    scrollX = 0

    while True:
        checkForAchieves()
        screen.fill((230, 230, 230))

        t = fontMedium.render('LEVEL SELECT', 1, (20, 20, 20))
        screen.blit(t, (screen_size[0] / 2 - t.get_width() / 2, 0))

        size = screen_size[1] / 7
        mp = pygame.mouse.get_pos()
        for n, i in enumerate(levels):
            if i[2]:
                r = pygame.Rect(
                    (size + n * size * 2) - scrollX - size / 2,
                    int(round(screen_size[1] * ys[n % len(ys)])) - size / 2,
                    size,
                    size
                    )
                if r.collidepoint(mp):
                    circle(screen,
                           (45, 45, 45),
                           ((size + n * size * 2) - scrollX,
                            int(round(screen_size[1] * ys[n % len(ys)]))),
                           size/2)
                else:
                    circle(screen,
                           (20, 20, 20),
                           ((size + n * size * 2) - scrollX,
                            int(round(screen_size[1] * ys[n % len(ys)]))),
                           size/2)
            else:
                circle(screen,
                      (127, 127, 127),
                      ((size + n * size * 2) - scrollX,
                        int(round(screen_size[1] * ys[n % len(ys)]))),
                       size/2)

            t = fontMedium.render('%d' % i[0], 1, (230, 230, 230))
            tx = (size + n * size * 2) - t.get_width() / 2
            tx -= scrollX
            ty = int(round(screen_size[1] * ys[n % len(ys)])) - t.get_height() / 2
            screen.blit(t, (tx, ty))

        clr = 2

        r = pygame.Rect((screen_size[0] / 2 - size) - size / 2, (screen_size[1] - size / 2) - size / 2 - clr, size, size)
        if r.collidepoint(mp):
            circle(screen, (45, 45, 45), (screen_size[0] / 2 - size, screen_size[1] - size / 2 - clr), size / 2)
        else:
            circle(screen, (20, 20, 20), (screen_size[0] / 2 - size, screen_size[1] - size / 2 - clr), size / 2)
        t = fontSmaller.render('FREE', 1, (230, 230, 230))
        screen.blit(t, ((screen_size[0] / 2 - size) - t.get_width() / 2, (screen_size[1] - size / 2) - t.get_height() - clr))
        t = fontSmaller.render('PLAY', 1, (230, 230, 230))
        screen.blit(t, ((screen_size[0] / 2 - size) - t.get_width() / 2, (screen_size[1] - size / 2 - clr)))

        r = pygame.Rect((screen_size[0] / 2 + size) - size / 2, (screen_size[1] - size / 2) - size / 2 - clr, size, size)
        if r.collidepoint(mp):
            circle(screen, (45, 45, 45), (screen_size[0] / 2 + size, screen_size[1] - size / 2 - clr), size / 2)
        else:
            circle(screen, (20, 20, 20), (screen_size[0] / 2 + size, screen_size[1] - size / 2 - clr), size / 2)
        t = fontSmaller.render('BACK', 1, (230, 230, 230))
        screen.blit(t, ((screen_size[0] / 2 + size) - t.get_width() / 2, (screen_size[1] - size / 2) - t.get_height() / 2 - clr))


        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if mp[0] > screen_size[0] - screen_size[0] / 10:
                    scrollX += 10
                    border = (size + (len(levels) - 5) * size * 2)
                    if scrollX > border:
                        scrollX = border
                elif mp[0] < screen_size[0] / 10:
                    scrollX -= 10
                    if scrollX < 0:
                        scrollX = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.MOUSEBUTTONUP:
                for n, i in enumerate(levels):
                    if i[2]:
                        r = pygame.Rect(
                            (size + n * size * 2) - scrollX - size / 2,
                            int(round(screen_size[1] * ys[n % len(ys)])) - size / 2,
                            size,
                            size
                            )
                        if r.collidepoint(event.pos):
                            (lastScreen, screen, fullscreen, distance, timeTaken, success) = mainLeveled(screen, fullscreen, gameSettings, i)
                            fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                            fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                            if success:
                                if n < len(levels) - 1:
                                    nextL = levels[n + 1]
                                    levels[n + 1] = (nextL[0], nextL[1], True, nextL[3])

                                    d = levels[n + 1]
                                    s = '##\n%d\n##\n%r\n##\n' % (d[0], d[2])
                                    s2 = ''
                                    for i in d[1]:
                                        s2 += '%d,%d,\'%s\';\n' % i
                                    s += s2
                                    open('levels/%s' % d[3], 'w').write(s)
                r = pygame.Rect((screen_size[0] / 2 - size) - size / 2, (screen_size[1] - size / 2) - size / 2, size, size)
                if r.collidepoint(mp):
                    main(screen, fullscreen, gameSettings)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                r = pygame.Rect((screen_size[0] / 2 + size) - size / 2, (screen_size[1] - size / 2) - size / 2, size, size)
                if r.collidepoint(mp):
                    return (screen, fullscreen)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    return (screen, fullscreen)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath,
                                               screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath,
                                              screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath,
                                            screen_size[1] / 32)

def mainLeveled(screen, fullscreen, gameSettings, level):
    achievementsData['CurrPage'] = 'GAME-LEVEL:%d' % level[0]
    global screen_size
    GLOBALDATA['summonParticles'] = []
    hud = True
    ehud = False
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    _map = level[1]

    particles = []

    MAXSIZE = 20
    MINSIZE = 1

    speed = 0 #M/S

    def calcGrad(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return float(dy) / dx

    groundBodies = []

    size = 5

    world = b2World(gravity=(0, -40), doSleep=False)

    lp = (0, 0)
    for p in _map:
        p = (p[0], p[1])
        groundBodies.append(world.CreateBody(
            shapes=b2EdgeShape(vertices=(lp, p))
        ))
        lp = p

    barBallBody1 = world.CreateDynamicBody(
        position=(12 - size, 12),
        angle=0
        )
    barBallBody1.CreatePolygonFixture(
        shape=b2CircleShape(radius=1),
        density=0.1,
        friction=30000
        )

    centralBarBody = world.CreateDynamicBody(
        position=(12, 12),
        angle=0,
        userData={'show': True}
        )
    centralBarBody.CreatePolygonFixture(
        maskBits=0,
        box=(MAXSIZE, 0.1),
        density=0.1,
        friction=0.3
        )

    barBallBody2 = world.CreateDynamicBody(
        position=(12 + size, 12),
        angle=0
        )
    barBallBody2.CreatePolygonFixture(
        shape=b2CircleShape(radius=1),
        density=0.1,
        friction=30000
        )

    lockPointFixture = world.CreateDynamicBody(
        position=(12, 12),
        fixedRotation=True,
        )
    lockPointFixture.CreatePolygonFixture(
        maskBits=0,
        shape=b2CircleShape(radius=0),
        density=1,
        friction=0.3
        )

    motorJoint = world.CreateRevoluteJoint(
        bodyA=centralBarBody,
        bodyB=lockPointFixture,
        enableMotor = True,
        motorSpeed=5,
        maxMotorTorque=500,
        anchor=(12, 12),
        )
    wj1 = world.CreateWeldJoint(
        bodyA=barBallBody1,
        bodyB=centralBarBody,
        localAnchorB=(-size, 0),
        )
    wj2 = world.CreateWeldJoint(
        bodyA=barBallBody2,
        bodyB=centralBarBody,
        localAnchorB=(size, 0),
        )

    cl = MyContactListener()
    cl.b1 = barBallBody1
    cl.b2 = barBallBody2
    world.contactListener = cl

    timeStep = 1.0 / 60
    vel_iters, pos_iters = 6, 2

    speedFreq = 100
    healthFreq = 25
    regenFreq = 500
    physicsFreq = 17
    pygame.time.set_timer(31, speedFreq)
    pygame.time.set_timer(30, regenFreq)
    pygame.time.set_timer(29, healthFreq)
    pygame.time.set_timer(28, physicsFreq)

    maxHealth = 250
    health = maxHealth
    healthCountdown = maxHealth
    speedThreshold = 0.05

    furthestDist = (centralBarBody.position[0]) - screen_size[0] / 3

    clock = pygame.time.Clock()

    startTime = time.time()

    lastClick = 0

    xMet = False
    yMet = False

    while True:
        clock.tick()
        checkForAchieves()

        scrollX = (gameSettings['PPM'] * centralBarBody.position[0]) - screen_size[0] / 3
        mapX = centralBarBody.position[0]
        scrollY = (screen_size[1] - gameSettings['PPM'] * centralBarBody.position[1]) - screen_size[1] / 2

        achievementsData['CurrDist'] = round(mapX)
        achievementsData['CurrTime'] = round(time.time() - startTime)
        achievementsData['CurrSpeed'] = (achievementsData['CurrDist'] / achievementsData['CurrTime']) if achievementsData['CurrTime'] else 0

        screen.fill((230, 230, 230))

        p1 = barBallBody1.fixtures[0].shape.pos
        p1 = barBallBody1.transform * p1 * gameSettings['PPM']
        p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
        circle(
            screen,
            (20, 20, 20),
            p1,
            int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM'])
            )
        p2 = barBallBody2.fixtures[0].shape.pos
        p2 = barBallBody2.transform * p2 * gameSettings['PPM']
        p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
        circle(
            screen,
            (20, 20, 20),
            p2,
            int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM'])
            )
        line(screen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))

        lst = [(_map[-1][0] * gameSettings['PPM']-scrollX, screen_size[1]),
               (-gameSettings['PPM'], screen_size[1]),
               (-gameSettings['PPM'], screen_size[1]-(_map[0][1]*gameSettings['PPM'])-scrollY)]

        for n, i in enumerate(_map):
            d = ((i[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i[1]*gameSettings['PPM'])-scrollY))
            if d[0] < screen_size[0] and d[0] > 0:
                lst.append(d)
            elif d[0] > screen_size[0]:
                i2 = _map[n-1]
                d2 = ((i2[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i2[1]*gameSettings['PPM'])-scrollY))
                if d2[0] < screen_size[0] and d2[0] > 0:
                    lst.append(d)
            elif d[0] < 0:
                if n + 1 < len(_map):
                    i2 = _map[n+1]
                    d2 = ((i2[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i2[1]*gameSettings['PPM'])-scrollY))
                    if d2[0] < screen_size[0] and d2[0] > 0:
                        lst.append(d)

        if centralBarBody.position[0] > level[1][-1][0]:
            xMet = True
        if centralBarBody.position[1] < min(level[1], key=lambda x:x[1])[1]:
            yMet = True

        for body in groundBodies:
            for fixture in body.fixtures:
                shape = fixture.shape
                if type(shape) == b2EdgeShape:
                    p1 = shape.vertices[0]
                    p2 = shape.vertices[1]
                    p1 = (p1[0]*gameSettings['PPM']-scrollX, screen_size[1]-p1[1]*gameSettings['PPM']-scrollY)
                    p2 = (p2[0]*gameSettings['PPM']-scrollX, screen_size[1]-p2[1]*gameSettings['PPM']-scrollY)
                    if p1[0] < -(gameSettings['PPM']*6) and p2[0] < -(gameSettings['PPM']*6):
                        world.DestroyBody(body)
                        groundBodies.remove(body)

        polygon(screen, (225, 225, 225), lst)
        polygon(screen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

        for particle in particles:
            rect(screen, particle.col, (particle.pos[0] - scrollX, particle.pos[1] - scrollY, 2, 2))

        if hud:
            h1 = (gameSettings['PPM']/2) * 5
            h2 = (gameSettings['PPM']/2) * 4
            h3 = (gameSettings['PPM']/2) * 3
            h4 = (gameSettings['PPM']/2) * 2
            h5 = (gameSettings['PPM']/2) * 1


            if health * (screen_size[0] / float(maxHealth)): rect(screen, (255, 95, 95), (0, screen_size[1] - h1, health * (screen_size[0] / float(maxHealth)), h1))
            if healthCountdown * (screen_size[0] / float(maxHealth)): rect(screen, (255, 182, 95), (0, screen_size[1] - h2, healthCountdown * (screen_size[0] / float(maxHealth)), h3))
            if speed*gameSettings['PPM']>0: rect(screen, (95, 255, 95), (0, screen_size[1] - h3, speed*gameSettings['PPM'], h5))

            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
            screen.blit(t, (0, 0))
            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
            screen.blit(t2, (0, t.get_height()))

            if ehud:
                t3 = fontMedium.render('%dFPS' % clock.get_fps(), 1, (20, 20, 20))
                screen.blit(t3, (0, t.get_height()*2))

            p = screen_size[1] / 16
            for m in messages[::-1]:
                if m[1] <= 255:
                    v = m[1]
                else:
                    v = 255
                t = fontTiny.render(m[0], 1, (20, 20, 20))

                pixels_alpha = pygame.surfarray.pixels_alpha(t)
                pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
                del pixels_alpha

                screen.blit(t, (0, (screen_size[1] - 50) - p))
                p += t.get_height()

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        screenFlip(screen)

        if xMet and yMet:
            (screen, fulscreen) = gameover(screen, screen, fullscreen, mapX, time.time() - startTime, True, True, level[0])
            return (pygame.Surface((32, 32)), screen, fullscreen, mapX, time.time() - startTime, True)

        if health <= 0:
            achievementsData['EndDist'] = mapX
            achievementsData['EndTime'] = time.time() - startTime
            achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

            lastScreen = pygame.Surface(screen_size)
            lastScreen.fill((230, 230, 230))
            p1 = barBallBody1.fixtures[0].shape.pos
            p1 = barBallBody1.transform * p1 * gameSettings['PPM']
            p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
            circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
            p2 = barBallBody2.fixtures[0].shape.pos
            p2 = barBallBody2.transform * p2 * gameSettings['PPM']
            p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
            circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
            line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
            polygon(lastScreen, (225, 225, 225), lst)
            polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
            lastScreen.blit(t, (0, 0))
            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
            lastScreen.blit(t2, (0, t.get_height()))
            t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
            lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

            (screen, fulscreen) = gameover(lastScreen, screen, fullscreen, mapX, time.time() - startTime, True)
            return (lastScreen, screen, fullscreen, mapX, time.time() - startTime, False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == 29:
                if speed < speedThreshold:
                    if healthCountdown > 0:
                        healthCountdown -= 1
                    else:
                        health -= 1
                elif healthCountdown < maxHealth:
                    healthCountdown += 1
            elif event.type == 30:
                if health < maxHealth:
                    if healthCountdown > 0:
                        health += 1
            elif event.type == 31:
                dist = mapX - furthestDist
                speed = round(dist * (1000.0/speedFreq), 2)
                if mapX > furthestDist:
                    furthestDist = mapX
            elif event.type == 27:
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    (screen, fullscreen, good) = pause(screen, fullscreen)
                    achievementsData['CurrPage'] = 'GAME'
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                    if good:
                        achievementsData['EndDist'] = mapX
                        achievementsData['EndTime'] = time.time() - startTime
                        achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

                        lastScreen = pygame.Surface(screen_size)
                        lastScreen.fill((230, 230, 230))
                        p1 = barBallBody1.fixtures[0].shape.pos
                        p1 = barBallBody1.transform * p1 * gameSettings['PPM']
                        p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
                        circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
                        p2 = barBallBody2.fixtures[0].shape.pos
                        p2 = barBallBody2.transform * p2 * gameSettings['PPM']
                        p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
                        circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
                        line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
                        polygon(lastScreen, (225, 225, 225), lst)
                        polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

                        t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
                        lastScreen.blit(t, (0, 0))
                        t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
                        lastScreen.blit(t2, (0, t.get_height()))
                        t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
                        lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

                        return (lastScreen, screen, fullscreen, mapX, time.time() - startTime, False)
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_F1:
                    hud = not hud
                elif event.key == pygame.K_F3:
                    ehud = not ehud
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    size += gameSettings['GSS']
                    if size < MINSIZE:
                        size = MINSIZE
                    if size > MAXSIZE:
                        size = MAXSIZE

                    world.DestroyJoint(wj1)
                    world.DestroyJoint(wj2)
                    wj1 = world.CreateWeldJoint(
                        bodyA=barBallBody1,
                        bodyB=centralBarBody,
                        localAnchorB=(-size, 0),
                        )
                    wj2 = world.CreateWeldJoint(
                        bodyA=barBallBody2,
                        bodyB=centralBarBody,
                        localAnchorB=(size, 0),
                        )

                    motorJoint.maxMotorTorque = (size if size > 5 else 5) * 100
                elif event.button == 5:
                    size -= gameSettings['GSS']
                    if size < MINSIZE:
                        size = MINSIZE
                    if size > MAXSIZE:
                        size = MAXSIZE

                    world.DestroyJoint(wj1)
                    world.DestroyJoint(wj2)
                    wj1 = world.CreateWeldJoint(
                        bodyA=barBallBody1,
                        bodyB=centralBarBody,
                        localAnchorB=(-size, 0),
                        )
                    wj2 = world.CreateWeldJoint(
                        bodyA=barBallBody2,
                        bodyB=centralBarBody,
                        localAnchorB=(size, 0),
                        )

                    motorJoint.maxMotorTorque = (size if size > 5 else 5) * 100
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    timeSinceClick = time.time() - lastClick
                    if timeSinceClick < 0.5:
                        (screen, fullscreen, good) = pause(screen, fullscreen)
                        achievementsData['CurrPage'] = 'GAME'
                        fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                        fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                        if good:
                            achievementsData['EndDist'] = mapX
                            achievementsData['EndTime'] = time.time() - startTime
                            achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

                            lastScreen = pygame.Surface(screen_size)
                            lastScreen.fill((230, 230, 230))
                            p1 = barBallBody1.fixtures[0].shape.pos
                            p1 = barBallBody1.transform * p1 * gameSettings['PPM']
                            p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
                            circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
                            p2 = barBallBody2.fixtures[0].shape.pos
                            p2 = barBallBody2.transform * p2 * gameSettings['PPM']
                            p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
                            circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
                            line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
                            polygon(lastScreen, (225, 225, 225), lst)
                            polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

                            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
                            lastScreen.blit(t, (0, 0))
                            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
                            lastScreen.blit(t2, (0, t.get_height()))
                            t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
                            lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

                            return (lastScreen, screen, fullscreen, mapX, time.time() - startTime, False)
                    lastClick = time.time()

            elif event.type == 28:
                GLOBALDATA['summonParticles'] = []
                world.Step(timeStep, vel_iters, pos_iters)
                if gameSettings['PAR']:
                    for par in GLOBALDATA['summonParticles']:
                        for i in xrange(random.randint(int(gameSettings['PAR'] - 5), int(gameSettings['PAR'] + 5))):
                            p = Particle(par.position, screen, scrollX, scrollY)
                            particles.append(p)
                GLOBALDATA['summonParticles'] = []
                for particle in particles:
                    particle.tick()
                    if 0 > particle.pos[0] - scrollX or particle.pos[0] - scrollX > screen_size[0]:
                        particles.remove(particle)
                    elif 0 > particle.pos[1] - scrollY or particle.pos[1] - scrollY > screen_size[1]:
                        particles.remove(particle)
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def main(screen, fullscreen, gameSettings):
    achievementsData['CurrPage'] = 'GAME'
    global screen_size
    #global GLOBALDATA['summonParticles']
    GLOBALDATA['summonParticles'] = []
    hud = True
    ehud = False
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    _map = [(0, 0), (20, 0), (30, 0)]

    particles = []

    MAXSIZE = 20
    MINSIZE = 1

    speed = 0 #M/S

    def calcGrad(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return float(dy) / dx

    groundBodies = []

    size = 5


    world = b2World(gravity=(0, -40), doSleep=False)

    lp = (0, 0)
    for p in _map:
        groundBodies.append(world.CreateBody(
            shapes=b2EdgeShape(vertices=(lp, p))
        ))
        lp = p

    barBallBody1 = world.CreateDynamicBody(
        position=(12 - size, 12),
        angle=0
        )
    barBallBody1.CreatePolygonFixture(
        shape=b2CircleShape(radius=1),
        density=0.1,
        friction=30000
        )

    centralBarBody = world.CreateDynamicBody(
        position=(12, 12),
        angle=0,
        userData={'show': True}
        )
    centralBarBody.CreatePolygonFixture(
        maskBits=0,
        box=(MAXSIZE, 0.1),
        density=0.1,
        friction=0.3
        )

    barBallBody2 = world.CreateDynamicBody(
        position=(12 + size, 12),
        angle=0
        )
    barBallBody2.CreatePolygonFixture(
        shape=b2CircleShape(radius=1),
        density=0.1,
        friction=30000
        )

    lockPointFixture = world.CreateDynamicBody(
        position=(12, 12),
        fixedRotation=True,
        )
    lockPointFixture.CreatePolygonFixture(
        maskBits=0,
        shape=b2CircleShape(radius=0),
        density=1,
        friction=0.3
        )

    motorJoint = world.CreateRevoluteJoint(
        bodyA=centralBarBody,
        bodyB=lockPointFixture,
        enableMotor = True,
        motorSpeed=5,
        maxMotorTorque=500,
        anchor=(12, 12),
        )
    wj1 = world.CreateWeldJoint(
        bodyA=barBallBody1,
        bodyB=centralBarBody,
        localAnchorB=(-size, 0),
        )
    wj2 = world.CreateWeldJoint(
        bodyA=barBallBody2,
        bodyB=centralBarBody,
        localAnchorB=(size, 0),
        )

    cl = MyContactListener()
    cl.b1 = barBallBody1
    cl.b2 = barBallBody2
    world.contactListener = cl

    timeStep = 1.0 / 60
    vel_iters, pos_iters = 6, 2

    speedFreq = 100
    healthFreq = 25
    regenFreq = 500
    physicsFreq = 17
    pygame.time.set_timer(31, speedFreq)
    pygame.time.set_timer(30, regenFreq)
    pygame.time.set_timer(29, healthFreq)
    pygame.time.set_timer(28, physicsFreq)

    maxHealth = 250
    health = maxHealth
    healthCountdown = maxHealth
    speedThreshold = 0.05

    furthestDist = (centralBarBody.position[0]) - screen_size[0] / 3

    clouds = []
    for i in [0, 1, 2]:
        w = random.randint(100, 700)
        clouds.append((-w, random.randint(0, screen_size[1]), w, w/3))

    clock = pygame.time.Clock()

    startTime = time.time()

    lastClick = 0

    while True:
        clock.tick()
        checkForAchieves()

        scrollX = (gameSettings['PPM'] * centralBarBody.position[0]) - screen_size[0] / 3
        mapX = centralBarBody.position[0]
        scrollY = (screen_size[1] - gameSettings['PPM'] * centralBarBody.position[1]) - screen_size[1] / 2

        achievementsData['CurrDist'] = round(mapX)
        achievementsData['CurrTime'] = round(time.time() - startTime)
        achievementsData['CurrSpeed'] = (achievementsData['CurrDist'] / achievementsData['CurrTime']) if achievementsData['CurrTime'] else 0

        while len(_map) < 5 or _map[-1][0] * gameSettings['PPM'] - scrollX < screen_size[0] + gameSettings['PPM']*6:
            g = 10
            while g > 3:
                x = _map[-1][0] + random.randint(1, 5)
                np = (x, random.randint(0, 500))
                g = calcGrad(np, _map[-1])
            _map.append(np)
            groundBodies.append(world.CreateBody(
                shapes=b2EdgeShape(vertices=(_map[-3], _map[-2]))
            ))

        screen.fill((230, 230, 230))

        p1 = barBallBody1.fixtures[0].shape.pos
        p1 = barBallBody1.transform * p1 * gameSettings['PPM']
        p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
        circle(
            screen,
            (20, 20, 20),
            p1,
            int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM'])
            )
        p2 = barBallBody2.fixtures[0].shape.pos
        p2 = barBallBody2.transform * p2 * gameSettings['PPM']
        p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
        circle(
            screen,
            (20, 20, 20),
            p2,
            int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM'])
            )
        line(screen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))

        lst = [(screen_size[0]+gameSettings['PPM'], screen_size[1]),
               (-gameSettings['PPM'], screen_size[1]),
               (-gameSettings['PPM'], screen_size[1]-(_map[0][1]*gameSettings['PPM'])-scrollY)]

        for n, i in enumerate(_map):
            d = ((i[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i[1]*gameSettings['PPM'])-scrollY))
            if d[0] < screen_size[0] and d[0] > 0:
                lst.append(d)
            elif d[0] > screen_size[0]:
                i2 = _map[n-1]
                d2 = ((i2[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i2[1]*gameSettings['PPM'])-scrollY))
                if d2[0] < screen_size[0] and d2[0] > 0:
                    lst.append(d)
            elif d[0] < 0:
                i2 = _map[n+1]
                d2 = ((i2[0]*gameSettings['PPM']-scrollX, screen_size[1]-(i2[1]*gameSettings['PPM'])-scrollY))
                if d2[0] < screen_size[0] and d2[0] > 0:
                    lst.append(d)

        for body in groundBodies:
            for fixture in body.fixtures:
                shape = fixture.shape
                if type(shape) == b2EdgeShape:
                    p1 = shape.vertices[0]
                    p2 = shape.vertices[1]
                    p1 = (p1[0]*gameSettings['PPM']-scrollX, screen_size[1]-p1[1]*gameSettings['PPM']-scrollY)
                    p2 = (p2[0]*gameSettings['PPM']-scrollX, screen_size[1]-p2[1]*gameSettings['PPM']-scrollY)
                    if p1[0] < -(gameSettings['PPM']*6) and p2[0] < -(gameSettings['PPM']*6):
                        world.DestroyBody(body)
                        groundBodies.remove(body)

        polygon(screen, (225, 225, 225), lst)
        polygon(screen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

        for particle in particles:
            rect(screen, particle.col, (particle.pos[0] - scrollX, particle.pos[1] - scrollY, 2, 2))

        if hud:
            h1 = (gameSettings['PPM']/2) * 5
            h2 = (gameSettings['PPM']/2) * 4
            h3 = (gameSettings['PPM']/2) * 3
            h4 = (gameSettings['PPM']/2) * 2
            h5 = (gameSettings['PPM']/2) * 1


            if health * (screen_size[0] / float(maxHealth)): rect(screen, (255, 95, 95), (0, screen_size[1] - h1, health * (screen_size[0] / float(maxHealth)), h1))
            if healthCountdown * (screen_size[0] / float(maxHealth)): rect(screen, (255, 182, 95), (0, screen_size[1] - h2, healthCountdown * (screen_size[0] / float(maxHealth)), h3))
            if speed*gameSettings['PPM']>0: rect(screen, (95, 255, 95), (0, screen_size[1] - h3, speed*gameSettings['PPM'], h5))

            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
            screen.blit(t, (0, 0))
            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
            screen.blit(t2, (0, t.get_height()))

            if ehud:
                t3 = fontMedium.render('%dFPS' % clock.get_fps(), 1, (20, 20, 20))
                screen.blit(t3, (0, t.get_height()*2))

            p = screen_size[1] / 16
            for m in messages[::-1]:
                if m[1] <= 255:
                    v = m[1]
                else:
                    v = 255
                t = fontTiny.render(m[0], 1, (20, 20, 20))

                pixels_alpha = pygame.surfarray.pixels_alpha(t)
                pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
                del pixels_alpha

                screen.blit(t, (0, (screen_size[1] - 50) - p))
                p += t.get_height()

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        screenFlip(screen)

        if health <= 0:
            achievementsData['EndDist'] = mapX
            achievementsData['EndTime'] = time.time() - startTime
            achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

            lastScreen = pygame.Surface(screen_size)
            lastScreen.fill((230, 230, 230))
            p1 = barBallBody1.fixtures[0].shape.pos
            p1 = barBallBody1.transform * p1 * gameSettings['PPM']
            p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
            circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
            p2 = barBallBody2.fixtures[0].shape.pos
            p2 = barBallBody2.transform * p2 * gameSettings['PPM']
            p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
            circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
            line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
            polygon(lastScreen, (225, 225, 225), lst)
            polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
            lastScreen.blit(t, (0, 0))
            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
            lastScreen.blit(t2, (0, t.get_height()))
            t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
            lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

            (screen, fulscreen) = gameover(lastScreen, screen, fullscreen, mapX, time.time() - startTime)
            return (lastScreen, screen, fullscreen, mapX, time.time() - startTime)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == 29:
                if speed < speedThreshold:
                    if healthCountdown > 0:
                        healthCountdown -= 1
                    else:
                        health -= 1
                elif healthCountdown < maxHealth:
                    healthCountdown += 1
            elif event.type == 30:
                if health < maxHealth:
                    if healthCountdown > 0:
                        health += 1
            elif event.type == 31:
                dist = mapX - furthestDist
                speed = round(dist * (1000.0/speedFreq), 2)
                if mapX > furthestDist:
                    furthestDist = mapX
            elif event.type == 27:
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    (screen, fullscreen, good) = pause(screen, fullscreen)
                    achievementsData['CurrPage'] = 'GAME'
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                    if good:
                        achievementsData['EndDist'] = mapX
                        achievementsData['EndTime'] = time.time() - startTime
                        achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

                        lastScreen = pygame.Surface(screen_size)
                        lastScreen.fill((230, 230, 230))
                        p1 = barBallBody1.fixtures[0].shape.pos
                        p1 = barBallBody1.transform * p1 * gameSettings['PPM']
                        p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
                        circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
                        p2 = barBallBody2.fixtures[0].shape.pos
                        p2 = barBallBody2.transform * p2 * gameSettings['PPM']
                        p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
                        circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
                        line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
                        polygon(lastScreen, (225, 225, 225), lst)
                        polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

                        t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
                        lastScreen.blit(t, (0, 0))
                        t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
                        lastScreen.blit(t2, (0, t.get_height()))
                        t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
                        lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

                        return (lastScreen, screen, fullscreen, mapX, time.time() - startTime)
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_F1:
                    hud = not hud
                elif event.key == pygame.K_F3:
                    ehud = not ehud
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    size += gameSettings['GSS']
                    if size < MINSIZE:
                        size = MINSIZE
                    if size > MAXSIZE:
                        size = MAXSIZE

                    world.DestroyJoint(wj1)
                    world.DestroyJoint(wj2)
                    wj1 = world.CreateWeldJoint(
                        bodyA=barBallBody1,
                        bodyB=centralBarBody,
                        localAnchorB=(-size, 0),
                        )
                    wj2 = world.CreateWeldJoint(
                        bodyA=barBallBody2,
                        bodyB=centralBarBody,
                        localAnchorB=(size, 0),
                        )

                    motorJoint.maxMotorTorque = (size if size > 5 else 5) * 100
                elif event.button == 5:
                    size -= gameSettings['GSS']
                    if size < MINSIZE:
                        size = MINSIZE
                    if size > MAXSIZE:
                        size = MAXSIZE

                    world.DestroyJoint(wj1)
                    world.DestroyJoint(wj2)
                    wj1 = world.CreateWeldJoint(
                        bodyA=barBallBody1,
                        bodyB=centralBarBody,
                        localAnchorB=(-size, 0),
                        )
                    wj2 = world.CreateWeldJoint(
                        bodyA=barBallBody2,
                        bodyB=centralBarBody,
                        localAnchorB=(size, 0),
                        )

                    motorJoint.maxMotorTorque = (size if size > 5 else 5) * 100
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    timeSinceClick = time.time() - lastClick
                    if timeSinceClick < 0.5:
                        lastClick = 0
                        (screen, fullscreen, good) = pause(screen, fullscreen)
                        achievementsData['CurrPage'] = 'GAME'
                        fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                        fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                        if good:
                            achievementsData['EndDist'] = mapX
                            achievementsData['EndTime'] = time.time() - startTime
                            achievementsData['EndSpeed'] = achievementsData['EndDist'] / achievementsData['EndTime']

                            lastScreen = pygame.Surface(screen_size)
                            lastScreen.fill((230, 230, 230))
                            p1 = barBallBody1.fixtures[0].shape.pos
                            p1 = barBallBody1.transform * p1 * gameSettings['PPM']
                            p1 = (int(p1[0]-scrollX), int(screen_size[1]-p1[1]-scrollY))
                            circle(lastScreen, (20, 20, 20), p1, int(barBallBody1.fixtures[0].shape.radius * gameSettings['PPM']))
                            p2 = barBallBody2.fixtures[0].shape.pos
                            p2 = barBallBody2.transform * p2 * gameSettings['PPM']
                            p2 = (int(p2[0]-scrollX), int(screen_size[1]-p2[1]-scrollY))
                            circle(lastScreen, (20, 20, 0), p2, int(barBallBody2.fixtures[0].shape.radius * gameSettings['PPM']))
                            line(lastScreen, (20, 20, 20), p1, p2, int(gameSettings['PPM']/6))
                            polygon(lastScreen, (225, 225, 225), lst)
                            polygon(lastScreen, (20, 20, 20), lst, int(round(gameSettings['PPM']/4)) if int(round(gameSettings['PPM']/4)) > 1 else 2)

                            t = fontMedium.render('%dM' % round(mapX-12), 1, (20, 20, 20))
                            lastScreen.blit(t, (0, 0))
                            t2 = fontMedium.render('%dS' % round(time.time() - startTime), 1, (20, 20, 20))
                            lastScreen.blit(t2, (0, t.get_height()))
                            t3 = fontMedium.render('%dM/S' % round((mapX-12) / (time.time() - startTime)), 1, (20, 20, 20))
                            lastScreen.blit(t3, (0, t.get_height() + t2.get_height()))

                            return (lastScreen, screen, fullscreen, mapX, time.time() - startTime)
                    lastClick = time.time()

            elif event.type == 28:
                GLOBALDATA['summonParticles'] = []
                world.Step(timeStep, vel_iters, pos_iters)
                if gameSettings['PAR']:
                    for par in GLOBALDATA['summonParticles']:
                        for i in xrange(random.randint(int(gameSettings['PAR'] - 5), int(gameSettings['PAR'] + 5))):
                            p = Particle(par.position, screen, scrollX, scrollY)
                            particles.append(p)
                GLOBALDATA['summonParticles'] = []
                for particle in particles:
                    particle.tick()
                    if 0 > particle.pos[0] - scrollX or particle.pos[0] - scrollX > screen_size[0]:
                        particles.remove(particle)
                    elif 0 > particle.pos[1] - scrollY or particle.pos[1] - scrollY > screen_size[1]:
                        particles.remove(particle)
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def pause(screen, fullscreen):
    achievementsData['CurrPage'] = 'PAUSE'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    fade = pygame.Surface(screen_size)
    fade.fill((230, 230, 230))
    fade.set_alpha(127)

    ss = screen.copy()

    rtgAnim = 0
    etmAnim = 0

    while True:
        checkForAchieves()
        screen.fill((0, 0, 0))

        screen.blit(pygame.transform.scale(ss, screen.get_size()), (0, 0))
        screen.blit(fade, (0, 0))

        t = font.render('PAUSED', 1, (20, 20, 20))
        screen.blit(t, (screen_size[0] / 2 - t.get_width() / 2, font.get_descent()))


        tw = fontMedium.render('RETURN TO GAME', 1, (230, 230, 230))
        t = fontMedium.render('RETURN TO GAME', 1, (20, 20, 20))
        rtgr = t.get_rect()
        rtgr.x = screen_size[0] / 2 - t.get_width() / 2
        rtgr.y = screen_size[1] / 3 - t.get_height() / 2
        screen.blit(t, rtgr)
        if rtgAnim:
            s = pygame.Surface((rtgAnim * 2, rtgr.h))
            s.fill((20, 20, 20))
            s.blit(tw, (s.get_width() / 2 - rtgr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - rtgAnim, rtgr.y))

        t = fontMedium.render('EXIT TO MENU', 1, (20, 20, 20))
        etmR = t.get_rect()
        etmR.x = screen_size[0] / 2 - t.get_width() / 2
        etmR.y = screen_size[1] / 3 * 2 - t.get_height() / 2
        screen.blit(t, etmR)

        tw = fontMedium.render('EXIT TO MENU', 1, (230, 230, 230))
        t = fontMedium.render('EXIT TO MENU', 1, (20, 20, 20))
        etmr = t.get_rect()
        etmr.x = screen_size[0] / 2 - t.get_width() / 2
        etmr.y = screen_size[1] / 3 * 2 - t.get_height() / 2
        screen.blit(t, etmr)
        if etmAnim:
            s = pygame.Surface((etmAnim * 2, etmr.h))
            s.fill((20, 20, 20))
            s.blit(tw, (s.get_width() / 2 - etmr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - etmAnim, etmr.y))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))
            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha
            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if rtgr.collidepoint(mp):
                    if rtgAnim < screen_size[0] / 3:
                        rtgAnim += 25
                    if rtgAnim > screen_size[0] / 3:
                        rtgAnim = screen_size[0] / 3
                else:
                    if rtgAnim > 0:
                        rtgAnim -= 25
                    if rtgAnim < 0:
                        rtgAnim = 0
                if etmr.collidepoint(mp):
                    if etmAnim < screen_size[0] / 3:
                        etmAnim += 25
                    if etmAnim > screen_size[0] / 3:
                        etmAnim = screen_size[0] / 3
                else:
                    if etmAnim > 0:
                        etmAnim -= 25
                    if etmAnim < 0:
                        etmAnim = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if etmr.collidepoint(event.pos):
                        return (screen, fullscreen, True)
                    elif rtgr.collidepoint(event.pos):
                        return (screen, fullscreen, False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    return (screen, fullscreen, False)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                fade = pygame.Surface(screen_size)
                fade.fill((230, 230, 230))
                fade.set_alpha(127)
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def gameover(lastscreen, screen, fullscreen, dist, timeT, challenge = False, success = False, chalNo = 0):
    achievementsData['CurrPage'] = 'GAMEOVER'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    ss = pygame.Surface(screen_size)
    ss.blit(screen, (0, 0))

    message = """
GAME OVER!
 \nYOU TRAVELED %dM
IN %dS!
 \nHIT SPACE TO CONTINUE""" % (dist, timeT)
    if challenge:
        if not success:
            message = """
GAME OVER!
 \nYOU FAILED TO COMPLETE
THE CHALLENGE
 \nBETTER LUCK
NEXT TIME!
 \nHIT SPACE TO CONTINUE"""
        else:
            message = """
CHALLENGE COMPLEATED!
 \nYOU COMPLEATED CHALLENGE %d
IN %d SECCONDS!
 \nHIT SPACE TO CONTINUE""" % (chalNo, timeT)

    fde = 0

    while True:
        checkForAchieves()

        fade = pygame.Surface(screen_size)
        fade.fill((230, 230, 230))
        fade.set_alpha(fde)
        screen.blit(pygame.transform.scale(ss, screen_size), (0, 0))
        screen.blit(fade, (0, 0))

        y = screen_size[1] / 2 - (fontSmaller.get_ascent() * len(message.split('\n'))) / 2
        for line in message.split('\n'):
            if line != '':
                t = fontSmaller.render(line, 1, (20, 20, 20))
                br = t.get_rect()
                br.x = screen_size[0] / 2 - t.get_width() / 2
                br.y = y
                screen.blit(t, br)
                y += fontSmaller.get_ascent()

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                fde += 2
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return (screen, fullscreen)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def between(a, b):
    return (a + b) / 2

def titleScreen():
    global fullscreen
    achievementsData['CurrPage'] = 'TS'
    global screen_size
    s = pygame.Surface((64, 64))
    s.fill((255, 0, 255))

    pygame.draw.polygon(s, (230, 230, 230), [(12, 0), (64-12, 0), (64-12, 64), (12, 64)])
    pygame.draw.polygon(s, (230, 230, 230), [(0, 12), (64, 12), (64, 64-12), (0, 64-12)])

    pygame.draw.circle(s, (20, 20, 20), (12, 12), 12)
    pygame.draw.circle(s, (230, 230, 230), (64-12, 12), 12)
    pygame.draw.circle(s, (230, 230, 230), (12, 64-12), 12)
    pygame.draw.circle(s, (20, 20, 20), (64-12, 64-12), 12)
    pygame.draw.line(s, (20, 20, 20), (12, 12), (64-12, 64-12), 4)

    s.set_colorkey((255, 0, 255))

    pygame.display.set_icon(s)

    if fullscreen:
        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.RESIZABLE|pygame.DOUBLEBUF)
    else:
        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
    screen_size = screen.get_size()
    screen.fill((20, 20, 20))
    pygame.display.flip()
    screenResize(screen_size)

    pygame.display.set_caption(gameName, gameName)

    lastScreen = pygame.Surface(screen_size)
    time = None
    distance = None
    lastScreen = None
    showachievements = False
    achievementsScroll = 0
    holdingBar = False
    cmdBar = False
    cmdText = 'sfe'

    if warnSaveVersion:
        message = """WARNING!
THE GAME SAVE DATA LOADED WAS
CREATED BY AN OLDER VERSION
OF %s AND THUS MIGHT
NOT WORK CORRECTLY
 \nUNTIL VERSION CONVERTERS
ARE BUILT IN, IT WOULD BE
ADVISED TO RESET THE GAME""" % gameName
        messageBase(screen, fullscreen, message)

    font = pygame.font.Font(fontPath, screen_size[1] / 8)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
    fontTitchy = pygame.font.Font(fontPath, screen_size[1] / 64)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    drawList = []

    oss = sum((1280, 1024)) / 2.0
    nss = sum(screen_size) / 2.0
    gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss

    animation = [0, 0, 0, 0]

    while True:
        checkForAchieves()
        if False:
            fade = pygame.Surface(screen_size)
            fade.fill((230, 230, 230))
            fade.set_alpha(127)
            screen.blit(pygame.transform.scale(lastScreen, screen_size), (0, 0))
            screen.blit(fade, (0, 0))
        else:
            screen.fill((230, 230, 230))

        t = font.render(gameName.upper(), 1, (20, 20, 20))
        screen.blit(t, (screen_size[0] / 2 - t.get_width() / 2, screen_size[1] / 8 - t.get_height() / 2))

        t2 = fontSmaller.render(subTitle.upper(), 1, (20, 20, 20))
        screen.blit(t2, (screen_size[0] / 2 - t2.get_width() / 2, t.get_height() + font.get_descent() * 2 + screen_size[1] / 8 - t2.get_height() / 2))

        p1x = min((screen_size[0] / 2 - t.get_width() / 2, screen_size[0] / 2 - t2.get_width() / 2))
        p2x = max((screen_size[0] / 2 + t.get_width() / 2, screen_size[0] / 2 + t2.get_width() / 2))
        p1y = t.get_height() + font.get_descent() * 2 + screen_size[1] / 8 - t2.get_height() / 2
        p2y = t.get_height() + font.get_descent() * 2 + screen_size[1] / 8 - t2.get_height() / 2

        line(
            screen,
            (20, 20, 20),
            (p1x, p1y),
            (p2x, p2y),
            2,
        )


        t3w = fontMedium.render('HOW TO PLAY', 1, (230, 230, 230))
        t3 = fontMedium.render('HOW TO PLAY', 1, (20, 20, 20))
        htpr = t3.get_rect()
        htpr.x = screen_size[0] / 2 - t3.get_width() / 2
        htpr.y = screen_size[1] / 16 * 11 - t3.get_height() / 2
        screen.blit(t3, htpr)
        if animation[1]:
            s = pygame.Surface((animation[1] * 2, htpr.h))
            s.fill((20, 20, 20))
            s.blit(t3w, (s.get_width() / 2 - htpr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - animation[1], htpr.y))

        t4w = fontMedium.render('PLAY', 1, (230, 230, 230))
        t4 = fontMedium.render('PLAY', 1, (20, 20, 20))
        pr = t4.get_rect()
        pr.x = screen_size[0] / 2 - t4.get_width() / 2
        pr.y = screen_size[1] / 16 * 9 - t4.get_height() / 2
        screen.blit(t4, pr)
        if animation[0]:
            s = pygame.Surface((animation[0] * 2, pr.h))
            s.fill((20, 20, 20))
            s.blit(t4w, (s.get_width() / 2 - pr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - animation[0], pr.y))

        t5w = fontMedium.render('OPTIONS', 1, (230, 230, 230))
        t5 = fontMedium.render('OPTIONS', 1, (20, 20, 20))
        opr = t5.get_rect()
        opr.x = screen_size[0] / 2 - t5.get_width() / 2
        opr.y = screen_size[1] / 16 * 13 - t5.get_height() / 2
        screen.blit(t5, opr)
        if animation[2]:
            s = pygame.Surface((animation[2] * 2, opr.h))
            s.fill((20, 20, 20))
            s.blit(t5w, (s.get_width() / 2 - opr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - animation[2], opr.y))

        t6w = fontMedium.render('QUIT', 1, (230, 230, 230))
        t6 = fontMedium.render('QUIT', 1, (20, 20, 20))
        qr = t6.get_rect()
        qr.x = screen_size[0] / 2 - t6.get_width() / 2
        qr.y = screen_size[1] / 16 * 15 - t6.get_height() / 2
        screen.blit(t6, qr)
        if animation[3]:
            s = pygame.Surface((animation[3] * 2, qr.h))
            s.fill((20, 20, 20))
            s.blit(t6w, (s.get_width() / 2 - qr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - animation[3], qr.y))

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        if not showachievements:
            circle(screen, (20, 20, 20), (0, screen_size[1] / 3), screen_size[1] / 32)
            rect(screen, (20, 20, 20), (0, screen_size[1] / 3, screen_size[1] / 32, screen_size[1] / 3))
            circle(screen, (20, 20, 20), (0, screen_size[1] / 3 * 2), screen_size[1] / 32)
            t7 = fontTiny.render('ACHIVMENTS', 1, (230, 230, 230))
            t7 = pygame.transform.rotate(t7, 90)
            screen.blit(t7, (fontTiny.get_descent(), screen_size[1] / 2 - t7.get_height() / 2))
        else:
            fontTitchy = pygame.font.Font(fontPath, screen_size[1] / 64)

            circle(screen, (20, 20, 20), (screen_size[0] / 4, screen_size[1] / 3), screen_size[1] / 32)
            rect(screen, (20, 20, 20), (screen_size[0] / 4, screen_size[1] / 3, screen_size[1] / 32, screen_size[1] / 3))
            circle(screen, (20, 20, 20), (screen_size[0] / 4, screen_size[1] / 3 * 2), screen_size[1] / 32)

            rect(screen, (20, 20, 20), (0, screen_size[1] / 3 - screen_size[1] / 32, screen_size[0] / 4, screen_size[1] / 32))
            rect(screen, (20, 20, 20), (0, screen_size[1] / 3 * 2, screen_size[0] / 4, screen_size[1] / 32))


            achive = pygame.Surface((screen_size[0] / 4, screen_size[1] / 3))
            achive.fill((230, 230, 230))

            totAchives = len(achievements)
            perPage = 3.0

            scrollLim = totAchives * (screen_size[1] / 9) - (screen_size[1] / 9 * 3)

            if achievementsScroll > scrollLim:
                achievementsScroll = scrollLim
            if achievementsScroll < 0:
                achievementsScroll = 0

            for n, a in enumerate(achievements):
                rect(achive, (20, 20, 20), (2, 2 + (screen_size[1] / 9) * n - achievementsScroll, screen_size[0] / 4 - 4 - 25, screen_size[1] / 9 - 4), 1)
                t = fontTiny.render(a[0], 1, (20, 20, 20))
                achive.blit(t, (2, 2 + (screen_size[1] / 9) * n - achievementsScroll + fontTiny.get_descent()))
                t2 = fontTitchy.render(a[1], 1, (20, 20, 20))
                achive.blit(t2, (4, t.get_height() + 2 + (screen_size[1] / 9) * n - achievementsScroll + fontTitchy.get_descent() + fontTiny.get_descent()))

                t3 = fontTitchy.render('COMPLEATED' if a[2] else 'NOT COMPLEATED', 1, (20, 20, 20))
                achive.blit(t3, (4, (2 + (screen_size[1] / 9) * n - achievementsScroll) + (screen_size[1] / 9 - 4) - t3.get_height()))
            rect(achive, (20, 20, 20), (screen_size[0] / 4 - 25, 2, 23, screen_size[1] / 3 - 4), 1)

            size = (perPage / totAchives) * screen_size[1] / 3 - 8
            pos = ((screen_size[1] / 3 - 8.) - size) / scrollLim * achievementsScroll
            rect(achive, (20, 20, 20), (screen_size[0] / 4 - 23, 4 + pos, 19, size))

            if pygame.mouse.get_pressed()[0]:
                mp = pygame.mouse.get_pos()
                if pygame.Rect(screen_size[0] / 4 - 25, screen_size[1] / 3 + 2, 23, screen_size[1] / 3 - 4).collidepoint(mp):
                    holdingBar = True
            else:
                holdingBar = False

            if holdingBar:
                p = mp[1] - screen_size[1] / 3
                p -= size / 2
                achievementsScroll = p / (((screen_size[1] / 3 - 8.) - size) / scrollLim)

            screen.blit(achive, (0, screen_size[1] / 3))

            t7 = fontTiny.render('ACHIVMENTS', 1, (230, 230, 230))
            t7 = pygame.transform.rotate(t7, 90)
            screen.blit(t7, (fontTiny.get_descent() + screen_size[0] / 4, screen_size[1] / 2 - t7.get_height() / 2))

        if cmdBar:
            aarect(screen, (20, 20, 20, 127), (20, 20, screen_size[0] - 40, screen_size[1] / 32))
            t = fontTiny.render(cmdText + '_', 1, (20, 20, 20))
            screen.blit(t, (20, 20 + fontTiny.get_descent()))

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if pr.collidepoint(mp):
                    if animation[0] < screen_size[0] / 3:
                        animation[0] += 25
                    if animation[0] > screen_size[0] / 3:
                        animation[0] = screen_size[0] / 3
                else:
                    if animation[0] > 0:
                        animation[0] -= 25
                    if animation[0] < 0:
                        animation[0] = 0
                if htpr.collidepoint(mp):
                    if animation[1] < screen_size[0] / 3:
                        animation[1] += 25
                    if animation[1] > screen_size[0] / 3:
                        animation[1] = screen_size[0] / 3
                else:
                    if animation[1] > 0:
                        animation[1] -= 25
                    if animation[1] < 0:
                        animation[1] = 0
                if opr.collidepoint(mp):
                    if animation[2] < screen_size[0] / 3:
                        animation[2] += 25
                    if animation[2] > screen_size[0] / 3:
                        animation[2] = screen_size[0] / 3
                else:
                    if animation[2] > 0:
                        animation[2] -= 25
                    if animation[2] < 0:
                        animation[2] = 0
                if qr.collidepoint(mp):
                    if animation[3] < screen_size[0] / 3:
                        animation[3] += 25
                    if animation[3] > screen_size[0] / 3:
                        animation[3] = screen_size[0] / 3
                else:
                    if animation[3] > 0:
                        animation[3] -= 25
                    if animation[3] < 0:
                        animation[3] = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 and not cmdBar:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    if cmdBar:
                        cmdBar = False
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_z and not cmdBar:
                    cmdText = ''
                    cmdBar = True
                elif event.key == pygame.K_F2 and not cmdBar:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
                elif event.key == pygame.K_p and not cmdBar:
                    (lastScreen, screen, fullscreen, distance, time) = main(screen, fullscreen, gameSettings)
                    font = pygame.font.Font(fontPath, screen_size[1] / 8)
                    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    achievementsData['CurrPage'] = 'TS'
                elif event.key == pygame.K_o and not cmdBar:
                    (screen, fullscreen) = options(screen, fullscreen)
                    font = pygame.font.Font(fontPath, screen_size[1] / 8)
                    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    achievementsData['CurrPage'] = 'TS'
                elif event.key == pygame.K_RETURN:
                    runCmd(cmdText)
                    cmdBar = False
                elif cmdBar:
                    if event.key == pygame.K_BACKSPACE:
                        cmdText = cmdText[:-1]
                    elif event.key == pygame.K_SPACE:
                        cmdText += ' '
                    else:
                        if event.unicode != ' ' :
                            cmdText += event.unicode
            elif event.type == pygame.MOUSEBUTTONUP and not cmdBar:
                if htpr.collidepoint(event.pos):
                    (screen, fullscreen) = howToPlayPT1(screen, fullscreen)
                    (screen, fullscreen) = howToPlayPT2(screen, fullscreen)
                    font = pygame.font.Font(fontPath, screen_size[1] / 8)
                    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    achievementsData['CurrPage'] = 'TS'
                elif opr.collidepoint(event.pos):
                    (screen, fullscreen) = options(screen, fullscreen)
                    font = pygame.font.Font(fontPath, screen_size[1] / 8)
                    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    achievementsData['CurrPage'] = 'TS'
                elif pr.collidepoint(event.pos):
                    (screen, fullscreen) = levelSelect(screen, fullscreen)
                    font = pygame.font.Font(fontPath, screen_size[1] / 8)
                    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                    achievementsData['CurrPage'] = 'TS'
                elif qr.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif pygame.Rect(0, screen_size[1] / 3, screen_size[1] / 32, screen_size[1] / 3).collidepoint(event.pos)and not showachievements:
                    showachievements = True
                elif pygame.Rect(screen_size[0] / 4, screen_size[1] / 3, screen_size[1] / 32, screen_size[1] / 3).collidepoint(event.pos)and showachievements:
                    showachievements = False
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 8)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 16)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def messageBase(screen, fullscreen, message):
    achievementsData['CurrPage'] = 'DESC'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    buttAnim = 0

    while True:
        checkForAchieves()
        screen.fill((230, 230, 230))

        y = screen_size[1] / 2 - (fontSmaller.get_ascent() * len(message.split('\n'))) / 2
        for line in message.split('\n'):
            if line != '':
                t = fontSmaller.render(line, 1, (20, 20, 20))
                br = t.get_rect()
                br.x = screen_size[0] / 2 - t.get_width() / 2
                br.y = y
                screen.blit(t, br)
                y += fontSmaller.get_ascent()
        y += fontSmaller.get_ascent()

        t3w = fontSmaller.render('CONTINUE', 1, (230, 230, 230))
        t3 = fontSmaller.render('CONTINUE', 1, (20, 20, 20))
        htpr = t3.get_rect()
        htpr.x = screen_size[0] / 2 - t3.get_width() / 2
        htpr.y = y
        screen.blit(t3, htpr)
        if buttAnim:
            s = pygame.Surface((buttAnim * 2, htpr.h))
            s.fill((20, 20, 20))
            s.blit(t3w, (s.get_width() / 2 - htpr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - buttAnim, htpr.y))

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if htpr.collidepoint(mp):
                    if buttAnim < screen_size[0] / 3:
                        buttAnim += 25
                    if buttAnim > screen_size[0] / 3:
                        buttAnim = screen_size[0] / 3
                else:
                    if buttAnim > 0:
                        buttAnim -= 25
                    if buttAnim < 0:
                        buttAnim = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.MOUSEBUTTONUP:
                if htpr.collidepoint(event.pos):
                    return (screen, fullscreen)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    return (screen, fullscreen)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def howToPlayPT1(screen, fullscreen):
    message = """HOW TO PLAY:\n \nUSE THE SCROLL WHEEL TO
CHANGE THE DISTANCE
BETWEEN THE TWO BALLS\n \nUSE THE FRICTION BETWEEN THE BALLS
AND THE GROUND TO MOVE FORWARDS\n \nYOU CAN EXTEND RAPIDLY OVER
A HILL TO GET PAST IT"""
    return messageBase(screen, fullscreen, message)

def howToPlayPT2(screen, fullscreen):
    message = """THE RED BAR IS YOUR HEALTH\n \nTHE ORANGE ONE IS THE AMOUNT OF
SURPLUS OXYGEN IN YOUR ENVIROMENT LEFT\n \nTHE GREEN ONE IS YOUR CURRENT SPEED\n \nIF YOU STOP OR GO BACKWARDS, SURPLUS
OXYGEN WILL GO DOWN THEN YOU WILL START
TAKING DAMAGE"""
    return messageBase(screen, fullscreen, message)

def description(screen, fullscreen):
    message = """
YOU HAVE BEEN STRANDED
ON AN ALIEN PLANET.
EARTH HAVE SAID THEY CAN
SAVE YOU...
...BUT THE LANDING SITE IS
100KM AWAY\n \nTHE ONLY PROBLEM IS THAT LIFE SUPPORT
REQUIRES YOU TO KEEP MOVING"""
    return messageBase(screen, fullscreen, message)

def checkReset(screen, fullscreen):
    achievementsData['CurrPage'] = 'DESC'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

    yAnim = 0
    nAnim = 0

    while True:
        checkForAchieves()
        screen.fill((230, 230, 230))

        t = fontMedium.render('ARE YOU SURE YOU', 1, (20, 20, 20))
        br = t.get_rect()
        br.x = screen_size[0] / 2 - t.get_width() / 2
        br.y = screen_size[1] / 4 - t.get_height() / 2
        screen.blit(t, br)
        t2 = fontMedium.render('WANT TO RESET', 1, (20, 20, 20))
        br = t2.get_rect()
        br.x = screen_size[0] / 2 - t2.get_width() / 2
        br.y = screen_size[1] / 4 + t.get_height() / 2
        screen.blit(t2, br)

        t = fontSmaller.render('THIS CANNOT BE UNDONE', 1, (20, 20, 20))
        br = t.get_rect()
        br.x = screen_size[0] / 2 - t.get_width() / 2
        br.y = screen_size[1] / 2 - t.get_height()
        screen.blit(t, br)


        tw = fontMedium.render('YES', 1, (230, 230, 230))
        t = fontMedium.render('YES', 1, (20, 20, 20))
        yr = t.get_rect()
        yr.x = yr.x = screen_size[0] / 4 - t.get_width() / 2
        yr.y = screen_size[1] / 4 * 3 - t.get_height()
        screen.blit(t, yr)
        if yAnim:
            s = pygame.Surface((yAnim * 2, yr.h))
            s.fill((20, 20, 20))
            s.blit(tw, (s.get_width() / 2 - yr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 4 - yAnim, yr.y))

        tw = fontMedium.render('NO', 1, (230, 230, 230))
        t = fontMedium.render('NO', 1, (20, 20, 20))
        nr = t.get_rect()
        nr.x = screen_size[0] / 4 * 3 - t.get_width() / 2
        nr.y = screen_size[1] / 4 * 3 - t.get_height()
        screen.blit(t, nr)
        if nAnim:
            s = pygame.Surface((nAnim * 2, nr.h))
            s.fill((20, 20, 20))
            s.blit(tw, (s.get_width() / 2 - nr.w / 2, 0))
            screen.blit(s, (screen_size[0] / 4 * 3 - nAnim, nr.y))

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if yr.collidepoint(mp):
                    if yAnim < screen_size[0] / 9:
                        yAnim += 15
                    if yAnim > screen_size[0] / 9:
                        yAnim = screen_size[0] / 9
                else:
                    if yAnim > 0:
                        yAnim -= 15
                    if yAnim < 0:
                        yAnim = 0
                if nr.collidepoint(mp):
                    if nAnim < screen_size[0] / 9:
                        nAnim += 15
                    if nAnim > screen_size[0] / 9:
                        nAnim = screen_size[0] / 9
                else:
                    if nAnim > 0:
                        nAnim -= 15
                    if nAnim < 0:
                        nAnim = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.MOUSEBUTTONUP:
                if nr.collidepoint(event.pos):
                    return (screen, fullscreen, False)
                elif yr.collidepoint(event.pos):
                    reset()
                    return (screen, fullscreen, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    return (screen, fullscreen, False)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 12)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)

def options(screen, fullscreen):
    achievementsData['CurrPage'] = 'OPT'
    global screen_size
    font = pygame.font.Font(fontPath, screen_size[1] / 4)
    fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
    fontMedium = pygame.font.Font(fontPath, screen_size[1] / 8)
    fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)


    dudMin = 0.0
    dudMax = 100.0
    dudData = 50.0

    data = [
        ['ZOOM', 5.0, 40.0, gameSettings['PPM'], pygame.Rect(0, 0, 0, 0), 'PPM'],
        ['GROW/SHRINK SPEED', 0.1, 1.0, gameSettings['GSS'], pygame.Rect(0, 0, 0, 0), 'GSS'],
        ['PARTICLES', 0.0, 50.0, gameSettings['PAR'], pygame.Rect(0, 0, 0, 0), 'PAR'],
    ]

    holding = ''

    ba = 0
    ra = 0
    aa = 0

    while True:
        checkForAchieves()
        screen.fill((230, 230, 230))

        ot = fontMedium.render('OPTIONS', 1, (20, 20, 20))
        screen.blit(ot, (screen_size[0] / 2 - ot.get_width() / 2, 0))

        backw = fontSmaller.render('BACK', 1, (230, 230, 230))
        back = fontSmaller.render('BACK', 1, (20, 20, 20))
        backRect = back.get_rect()
        backRect.x = screen_size[0] / 2 - backRect.w / 2
        backRect.y = screen_size[1] - backRect.h
        screen.blit(back, backRect)
        if ba:
            s = pygame.Surface((ba * 2, backRect.h))
            s.fill((20, 20, 20))
            s.blit(backw, (s.get_width() / 2 - backRect.w / 2, 0))
            screen.blit(s, (screen_size[0] / 2 - ba, backRect.y))

        resetw = fontSmaller.render('RESET GAME', 1, (230, 230, 230))
        reset = fontSmaller.render('RESET GAME', 1, (20, 20, 20))
        resetRect = reset.get_rect()
        resetRect.x = 0
        resetRect.y = screen_size[1] - resetRect.h
        screen.blit(reset, resetRect)
        if ra:
            s = pygame.Surface((ra, resetRect.h))
            s.fill((20, 20, 20))
            s.blit(resetw, (0, 0))
            screen.blit(s, (0, resetRect.y))

        aboutw = fontSmaller.render('ABOUT', 1, (230, 230, 230))
        about = fontSmaller.render('ABOUT', 1, (20, 20, 20))
        aboutRect = about.get_rect()
        aboutRect.x = screen_size[0] - aboutRect.w
        aboutRect.y = screen_size[1] - aboutRect.h
        screen.blit(about, aboutRect)
        if aa:
            s = pygame.Surface((aa, aboutRect.h))
            s.fill((20, 20, 20))
            s.blit(aboutw, (aa-aboutRect.w, 0))
            screen.blit(s, (screen_size[0] - aa, aboutRect.y))

        yinc = 4
        for d in data:
            yinc += 2
            dudt = fontSmaller.render('%s    ' % d[0], 1, (20, 20, 20))
            screen.blit(dudt, (screen_size[0] / 4 - dudt.get_width() / 2, screen_size[1] / 16 * yinc))
            rect(
                screen,
                (50, 50, 50),
                (
                    screen_size[0] / 4 - dudt.get_width() / 2 + dudt.get_width(),
                    screen_size[1] / 16 * yinc,
                    screen_size[0] / 2,
                    dudt.get_height()
                )
            )
            bw = screen_size[0] / 2
            ppdu = bw / abs(d[2] - d[1])
            rect(
                screen,
                (20, 20, 20),
                (
                    screen_size[0] / 4 - dudt.get_width() / 2 + dudt.get_width(),
                    screen_size[1] / 16 * yinc,
                    round(ppdu * (d[3] - d[1])),
                    dudt.get_height()
                )
            )
            dudBar = pygame.Rect(
                screen_size[0] / 4 - dudt.get_width() / 2 + dudt.get_width(),
                screen_size[1] / 16 * yinc,
                screen_size[0] / 2,
                dudt.get_height()
            )
            dudd = fontSmaller.render(str(round(d[3], 2)), 1, (230, 230, 230))
            screen.blit(dudd, dudBar.topleft)

            data[data.index(d)][4] = dudBar

        t = fontTiny.render(version, 1, (20, 20, 20))
        screen.blit(t, (screen_size[0]-t.get_width(), 0))

        p = screen_size[1] / 16
        for m in messages[::-1]:
            if m[1] <= 255:
                v = m[1]
            else:
                v = 255
            t = fontTiny.render(m[0], 1, (20, 20, 20))

            pixels_alpha = pygame.surfarray.pixels_alpha(t)
            pixels_alpha[...] = (pixels_alpha * (v / 255.0)).astype(int)
            del pixels_alpha

            screen.blit(t, (0, (screen_size[1] - 50) - p))
            p += t.get_height()

        screenFlip(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == 27:
                mp = pygame.mouse.get_pos()
                if backRect.collidepoint(mp):
                    if ba < backRect.w:
                        ba += 15
                    if ba > backRect.w:
                        ba = backRect.w
                else:
                    if ba > 0:
                        ba -= 15
                    if ba < 0:
                        ba = 0
                if resetRect.collidepoint(mp):
                    if ra < resetRect.w + resetRect.w / 4:
                        ra += 25
                    if ra > resetRect.w + resetRect.w / 4:
                        ra = resetRect.w + resetRect.w / 4
                else:
                    if ra > 0:
                        ra -= 25
                    if ra < 0:
                        ra = 0
                if aboutRect.collidepoint(mp):
                    if aa < aboutRect.w + aboutRect.w / 4:
                        aa += 25
                    if aa > aboutRect.w + aboutRect.w / 4:
                        aa = aboutRect.w + aboutRect.w / 4
                else:
                    if aa > 0:
                        aa -= 25
                    if aa < 0:
                        aa = 0
                for m in messages:
                    m[1] -= 1
                    if m[1] <= 0:
                        messages.remove(m)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN|pygame.RESIZABLE|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
                elif event.key == pygame.K_ESCAPE:
                    gameSettings['PPM'] = data[0][3]
                    gameSettings['GSS'] = data[1][3]
                    gameSettings['PAR'] = data[2][3]
                    return (screen, fullscreen)
                elif event.key == pygame.K_F2:
                    messages.append(['Screenshot saved as \'%s\'' % screenshot(screen), msgTime])
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    holding = ''
                    if resetRect.collidepoint(event.pos):
                        (screen, fullscreen, rst) = checkReset(screen, fullscreen)
                        if rst:
                            return (screen, fullscreen)
                        font = pygame.font.Font(fontPath, screen_size[1] / 4)
                        fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                        fontMedium = pygame.font.Font(fontPath, screen_size[1] / 8)
                        fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                        achievementsData['CurrPage'] = 'OPT'
                    elif backRect.collidepoint(event.pos):
                        gameSettings['PPM'] = data[0][3]
                        gameSettings['GSS'] = data[1][3]
                        gameSettings['PAR'] = data[2][3]
                        return (screen, fullscreen)
                    elif aboutRect.collidepoint(event.pos):
                        message = """%s
 \nA SMALL GAME I WROTE
 IN MY SPARE TIME
 \nCREDITS:
PROGRAMMING: NATHAN "BOTTERSNIKE" TAYLOR
MUSIC: JOHN CENA""" % gameName
                        messageBase(screen, fullscreen, message)
                        font = pygame.font.Font(fontPath, screen_size[1] / 4)
                        fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                        fontMedium = pygame.font.Font(fontPath, screen_size[1] / 8)
                        fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)
                        achievementsData['CurrPage'] = 'OPT'
            elif event.type == pygame.VIDEORESIZE:
                oss = sum(screen_size) / 2.0
                nss = sum(event.size) / 2.0
                gameSettings['PPM'] = (gameSettings['PPM'] / oss) * nss
                screen_size = event.size
                screenResize(screen_size)
                font = pygame.font.Font(fontPath, screen_size[1] / 4)
                fontSmaller = pygame.font.Font(fontPath, screen_size[1] / 20)
                fontMedium = pygame.font.Font(fontPath, screen_size[1] / 8)
                fontTiny = pygame.font.Font(fontPath, screen_size[1] / 32)


        if pygame.mouse.get_pressed()[0]:
            mp = pygame.mouse.get_pos()
            for d in data:
                if (d[4].collidepoint(mp) and holding == '') or holding == d[5]:
                    holding = d[5]
                    rx = mp[0] - d[4].x
                    da = rx / (bw / abs(d[2] - d[1])) + d[1]
                    if da > d[2]:
                        da = d[2]
                    if da < d[1]:
                        da = d[1]
                    data[data.index(d)][3] = da
        else:
            hodling = ''

if __name__ == "__main__":
    titleScreen()
