import pygame as pg
from math import floor, ceil
from random import uniform, randint

#remember to use pygbag you pygfag
#TODO age labels (v1.1)
#TODO adjust button sizes based on window size?
#TODO think of minigames (v1.1)
#TODO tutorials
#TODO flavor text for research
pg.init()

research_gain = 1
food_storage = 20
storage_scale = 1
workers = 0
clicking = False
allow_building = False
death_factor = 3
scroll_y = 0
scroll_speed = 50
passive_food = 0
total_research_height = 0
houses = 0
resources = 0
theme_state = 1
humans = 0
hunters = 0
scholars = 0
builders = 0
#change to miners after tools/mining unlocked or something
gatherers = 0
unemployed = 0
knowledge = 0
button_font = pg.font.SysFont('Corbel', 35, True)
text_font = pg.font.SysFont('Corbel', 50)
clock = pg.time.Clock()
screen = pg.display.set_mode((1600, 900), pg.RESIZABLE)
screen_width, screen_height = screen.get_size()
running = True
button_clicked = False
frame = 0
humans_base = 2
food = 10
civ = False
current_scene = "home"
pg.display.set_caption("untitled incremental game")
seconds = 0
user_color_1 = (0, 0, 0)
user_color_2 = (255, 255, 255)


class Button:
    def __init__(self, text, func, width=150, height=75, enabled=True, x=None, y=None):
        self.text = text
        self.width = width
        self.height = height
        self.func = func
        self.enabled = enabled
        self.button_rect = pg.Rect(0, 0, width, height)
        self.x = x
        self.y = y

    def draw(self, x, y, hover=False):
        if self.x is not None:
            x = self.x
        if self.y is not None:
            y = self.y
        self.button_rect.center = (x, y)
        if hover:
            pg.draw.rect(screen, (150, 150, 150), self.button_rect, width=4, border_radius=1)
            text = button_font.render(self.text, True, (150, 150, 150))
        else:
            pg.draw.rect(screen, user_color_1, self.button_rect, width=4, border_radius=1)
            text = button_font.render(self.text, True, user_color_1)

        text_rect = text.get_rect()
        text_rect.center = self.button_rect.center
        screen.blit(text, text_rect)


class TabButton(Button):
    def __init__(self, text, func, width=150, height=75):
        super().__init__(text, func, width, height, enabled=True)

    def draw(self, y, num, hover=False):
        button_count = 4
        button_width = self.width * button_count + button_count * 30
        start_x = ((screen_width - button_width) / 2) + self.width / 2
        moved_x = start_x + num * self.width + num * 20
        self.button_rect.center = (moved_x, y)
        super().draw(moved_x, y, hover)


class ResearchButton(Button):
    def __init__(self, func, title, desc, id, layer, point_req, enabled=True, requirements=[], used=False):
        super().__init__("", func, enabled)
        if requirements is None:
            requirements = []
        self.title = title
        self.desc = desc
        self.func = func
        self.id = id
        self.requirements = requirements
        self.enabled = enabled
        self.used = used
        self.layer = layer
        self.point_req = point_req

    def draw(self, x, y, num, hover=False):

        width = 500
        button_spacing = 20
        index = layers[self.layer].index(self)
        num_in_layer = len(layers[self.layer])
        research_buttons_width = width * num_in_layer + button_spacing * (num_in_layer - 1)
        title_font = pg.font.SysFont('Corbel', 50, True)
        desc_font = pg.font.SysFont('Corbel', 30)
        smol_font = pg.font.SysFont('Corbel', 40, bold=True)

        desc_text = desc_font.render(self.desc, True, user_color_1)
        title_text = title_font.render(self.title, True, user_color_1)
        title_rect = title_text.get_rect()
        start_x = (screen_width - research_buttons_width) // 2
        moved_x = start_x + num * (width + button_spacing)

        moved_y = self.layer * 300 + scroll_y

        if moved_y + 175 < 300 or moved_y > screen_height:
            self.button_rect = pg.Rect(moved_x, moved_y, width, 175)
            return

        title_rect.center = (moved_x + width // 2, moved_y)
        desc_rect = desc_text.get_rect()
        desc_rect.y = title_rect.bottom
        desc_rect.centerx = moved_x + width // 2
        self.button_rect = title_rect.union(desc_rect)
        self.button_rect.inflate_ip(width - self.button_rect.width, 20)
        self.button_rect.height = 175
        self.button_rect.centerx = moved_x + width // 2
        req_text = smol_font.render(str(self.point_req), True, (150, 150, 150))
        req_rect = req_text.get_rect()
        req_rect.topleft = (self.button_rect.left + 10, self.button_rect.top + 10)
        if (hover and not self.used) or not self.is_researchable():  #unused or unresearchable
            pg.draw.rect(screen, (150, 150, 150), self.button_rect, width=5, border_radius=1)
            desc_text = desc_font.render(self.desc, True, (150, 150, 150))
            title_text = title_font.render(self.title, True, (150, 150, 150))
            req_text = smol_font.render(str(self.point_req), True, (150, 150, 150))
        elif self.used:
            pg.draw.rect(screen, (34, 139, 34), self.button_rect, width=5, border_radius=1)
            desc_text = desc_font.render(self.desc, True, (34, 139, 34))
            title_text = title_font.render(self.title, True, ((34, 139, 34)))
            req_text = smol_font.render(str(self.point_req), True, (34, 139, 34))
        else:
            pg.draw.rect(screen, (255, 236, 161), self.button_rect, width=5, border_radius=1)
            desc_text = desc_font.render(self.desc, True, user_color_1)
            title_text = title_font.render(self.title, True, user_color_1)
            req_text = smol_font.render(str(self.point_req), True, (user_color_1))
        screen.blit(title_text, title_rect)
        screen.blit(desc_text, desc_rect)
        screen.blit(req_text, req_rect)
        pg.draw.line(screen, user_color_1,
                     self.button_rect.midbottom,
                     (self.button_rect.centerx, self.button_rect.bottom + 50),
                     4)

        if self.layer != 1:
            pg.draw.line(screen, user_color_1,
                         self.button_rect.midtop,
                         (self.button_rect.centerx, self.button_rect.top - 75),
                         4)
            num_in_previous = len(layers[self.layer - 1])
            if index == num_in_layer - 1:
                if num_in_layer >= num_in_previous:
                    pg.draw.line(screen, user_color_1,
                                 (self.button_rect.centerx, self.button_rect.top - 75),
                                 (self.button_rect.centerx - (research_buttons_width - width),
                                  self.button_rect.top - 75),
                                 4)
                else:
                    pg.draw.line(screen, user_color_1,
                                 (self.button_rect.centerx + (
                                         ((width + button_spacing) / 2) * (num_in_previous - (index + 1))),
                                  self.button_rect.top - 75),
                                 (self.button_rect.centerx - ((width * num_in_previous + button_spacing * (
                                         num_in_previous - (
                                         1 + ((num_in_previous - (index + 1)) * .5)))) - width * (
                                                                      1 + ((num_in_previous - (index + 1)) * .5))),
                                  self.button_rect.top - 75),
                                 4)

    def is_researchable(self):
        return (all([req.used for req in self.requirements]) and self.point_req <= knowledge) or self.used

def reset():
    global humans, food_storage, food, resources, houses, research_gain, knowledge, civ, death_factor, storage_scale, passive_food, hunters,gatherers,builders,scholars
    civ = False
    humans, resources, houses, knowledge, passive_food, hunters, gatherers, builders, scholars = (0,0,0,0,0,0,0,0,0)
    food = 10
    research_gain = 1
    food_storage = 20
    death_factor = 3
    storage_scale = 1

    for layer in layers.values():
        for button in layer:
            button.used = False

def home_scene():
    global current_scene
    current_scene = "home"


def research_scene():
    global current_scene
    current_scene = "research"


def settings_scene():
    global current_scene
    current_scene = "settings"


def about_scene():
    global current_scene
    current_scene = "about"


def spawn():
    global humans
    if houses == 0:
        if humans < 5:
            humans += 1
    else:
        if humans <= 5*(houses+1):
            humans += 1


def build_house():
    global resources
    global houses
    global food_storage
    if resources >= 10:
        houses += 1
        food_storage += 10 * storage_scale
        resources -= 10


def breed():
    global humans
    global humans_base
    if humans >= 2:
        humans_base = humans
        humans_base *= 1.01
        humans = floor(humans_base)


def eat():
    global humans
    global food
    food -= humans
    if food < 0:
        humans += food
        food = 0


def work():
    global hunters
    global scholars
    global gatherers
    global resources
    global food
    global knowledge
    global seconds
    global food_storage
    global research_gain
    if food < food_storage:
        food += hunters
    knowledge += ceil(scholars * research_gain)
    if seconds % 2 == 0:
        resources += gatherers


def death():
    global humans, death_factor
    global workers, hunters, scholars, gatherers, builders

    work_list = [workers, hunters, scholars, gatherers]
    humans -= (ceil((uniform(humans / 100, humans / 50) * death_factor)))

    if humans < workers:
        for i in range(workers - humans):
            dead = randint(0, 3)
            while work_list[dead] == 0:
                dead = randint(0, 3)
            work_list[dead] -= 1

            workers = work_list[0]
            hunters = work_list[1]
            scholars = work_list[2]
            gatherers = work_list[3]


def color_set():
    global theme_state
    global user_color_1
    global user_color_2
    if theme_state == 1:
        user_color_1 = (255, 255, 255)
        user_color_2 = (25, 27, 29)
        theme_state = 0
    else:
        user_color_1 = (0, 0, 0)
        user_color_2 = (255, 255, 255)
        theme_state = 1


def handle_research_scrolling(event):
    global scroll_y, total_research_height

    max_layer = max(layers.keys())
    total_research_height = (max_layer * 300) + 400

    if event.type == pg.MOUSEWHEEL:
        scroll_y += event.y * scroll_speed

        scroll_y = min(0, scroll_y)
        scroll_y = max(-(total_research_height - screen_height + 100), scroll_y)


def research(id):
    global civ,knowledge,research_gain
    #TODO this entire thing
    if id == "civ" or civilization.used:
        civ = True
    if id == "fire" or fire.used:
        global death_factor
        death_factor = 2
        if not fire.used:
            knowledge -= fire.point_req
    if id == "stone" or stone_tools.used:
        global allow_building
        allow_building = True
        if not stone_tools.used:
            knowledge -= stone_tools.point_req
    if id == "pot" or pottery.used:
        global food_storage
        global storage_scale
        food_storage = 100
        storage_scale = 2
        if not pottery.used:
            knowledge -= pottery.point_req
    if id == "culti" or cultivation.used:
        global passive_food
        passive_food = 1
        if not cultivation.used:
            knowledge -= cultivation.point_req
    if id == "writing" or writing.used:
        research_gain = 1.5
    if id == "metal" or metallurgy.used:
        pass
        #change label of gatherers to miners
    if id == "edu" or education.used:
        research_gain = 2
    if id == "iron" or iron.used:
        pass
    if id == "butch" or butchery.used:
        pass
    if id == "agri" or agriculture.used:
        pass
    if id == "smith" or smithing.used:
        pass
    if id == "math" or mathematics.used:
        pass
    if id == "fert" or fertilizer.used:
        pass
    if id == "chem" or chemistry.used:
        pass
    if id == "steel" or steel.used:
        pass
    if id == "meds" or medicine.used:
        pass
    if id == "boom" or gunpowder.used:
        pass
    if id == "steam" or steam.used:
        pass
    if id == "colon" or colonies.used:
        pass
    if id == "indus" or industry.used:
        pass
    if id == "clean" or hygiene.used:
        pass

def hunter_increase():
    global hunters
    global unemployed
    if unemployed > 0:
        hunters += 1


def hunter_decrease():
    global hunters
    if hunters > 0:
        hunters -= 1


def scholar_increase():
    global scholars
    global unemployed
    if unemployed > 0:
        scholars += 1


def scholar_decrease():
    global scholars
    if scholars > 0:
        scholars -= 1


def builder_increase():
    global builders
    global unemployed
    if unemployed > 0 and allow_building:
        builders += 1


def builder_decrease():
    global builders
    if builders > 0:
        builders -= 1


def gatherer_increase():
    global gatherers
    global unemployed
    if unemployed > 0:
        gatherers += 1


def gatherer_decrease():
    global gatherers
    if gatherers > 0:
        gatherers -= 1


home_tab = TabButton("home", home_scene)
research_tab = TabButton("research", research_scene)
settings_tab = TabButton("settings", settings_scene)
about_tab = TabButton("about", about_scene)

spawn_button = Button("Bless with life", spawn, width=400)
build_button = Button("Build a House (10 resources)", build_house, width=450, y=screen_height // 2 + 100)
hunter_increase_button = Button(">", hunter_increase, width=50, height=50, x=screen_width // 2 + 150, y=225)
hunter_decrease_button = Button("<", hunter_decrease, width=50, height=50, x=screen_width // 2 - 150, y=225)
scholar_increase_button = Button(">", scholar_increase, width=50, height=50, x=screen_width // 2 + 150, y=275)
scholar_decrease_button = Button("<", scholar_decrease, width=50, height=50, x=screen_width // 2 - 150, y=275)
gatherer_increase_button = Button(">", gatherer_increase, width=50, height=50, x=screen_width // 2 + 150, y=325)
gatherer_decrease_button = Button("<", gatherer_decrease, width=50, height=50, x=screen_width // 2 - 150, y=325)
builder_increase_button = Button(">", builder_increase, width=50, height=50, x=screen_width // 2 + 150, y=375)
builder_decrease_button = Button("<", builder_decrease, width=50, height=50, x=screen_width // 2 - 150, y=375)
#the power of friendship
civilization = ResearchButton(research, "Civilization", "The dawn of your society \n allows life and research",
                              "civ", 1, 0)
layer_1 = [civilization]
#fire emoji
fire = ResearchButton(research, "Fire", "       Your people discover fire, "
                                        "\n Reduces death chance through cooking", "fire", 2, 50,
                      requirements=[civilization])
#getting stoned
stone_tools = ResearchButton(research, "Stone Tools", "Your people invent basic tools,"
                                                      "\n Allows home building", "stone", 2, 50,
                             requirements=[civilization])

layer_2 = [fire, stone_tools]
#the less cool kind of pot
pottery = ResearchButton(research, "Pottery", "Your people discover pottery, "
                                              "\n Increases food storage by 100, scales storage ", "pot",
                         3, 200,
                         requirements=[i for i in layer_2])
#the more cool kind of pot
cultivation = ResearchButton(research, "cultivation", "Your people invent basic crop cultivation \n "
                                                      "Allows passive food growth", "culti", 3, 250,
                             requirements=[stone_tools])

writing = ResearchButton(research, "Writing", "Your people develop a writing system \n "
                                              "increases scholar gain", "writing", 3, 250,
                         requirements=[i for i in layer_2])

layer_3 = [pottery, cultivation, writing]

metallurgy = ResearchButton(research, "Metallurgy", "Your people learn to smelt metals \n "
                                                    "increases resource gain, unlocks mining", "metal", 4, 1000,
                            requirements=[i for i in layer_3])

education = ResearchButton(research, "Education", "Education becomes more commonplace \n "
                                                    "further increases scholar gain", "edu", 4, 1500,
                            requirements=[writing])
layer_4 = [metallurgy,education]
agriculture = ResearchButton(research, "Education", "Develop advanced agriculture \n "
                                                    "increased passive food growth", "agri", 5, 3000,
                            requirements=[education,cultivation])

butchery = ResearchButton(research, "Butchery", "More efficient meat slicing \n "
                                                    "hunters produce more food", "butch", 5, 2500,
                            requirements=[i for i in layer_4])

iron = ResearchButton(research, "iron", "Your people learn to use iron \n "
                                                    "even more efficient mining and hunting", "iron", 5, 4000,
                            requirements=[metallurgy])

layer_5 = [butchery,iron,agriculture]

mathematics = ResearchButton(research, "Mathematics", "Your people invent a math system \n "
                                                    "further increases scholar gain", "math", 6, 8000,
                            requirements=[i for i in layer_5])

fertilizer = ResearchButton(research, "Fertilizer", "Your people learn to fertilize fields \n "
                                                    "more passive food", "fert", 6, 4500,
                            requirements=[agriculture, butchery])

smithing = ResearchButton(research, "Smithing", "Form metal into better shapes \n "
                                                    "increase storage, hunting, resource gain", "smith", 6, 6000,
                            requirements=[iron])
layer_6 = [mathematics,fertilizer,smithing]

chemistry = ResearchButton(research, "Chemistry", "Basic chemistry \n "
                                                    "increases scholarly gain", "chem", 7, 6000,
                            requirements=[i for i in layer_6])
layer_7 = [chemistry]
#TODO actually do this
steel = ResearchButton(research, "Steel", "Make your iron stronger \n "
                                                    "increase resource gain", "steel", 8, 10000,
                            requirements=[chemistry,smithing ])
medicine = ResearchButton(research, "Medicine", "Unlock basic medicine \n "
                                                    "reduce death", "meds", 8, 7500,
                            requirements=[chemistry])
#we bring the boom
gunpowder = ResearchButton(research, "Gunpowder", "Invent some explosives \n "
                                                    "mooore resource gain from mining", "boom", 8, 12000,
                            requirements=[chemistry, smithing])
layer_8 = [gunpowder,medicine,steel]

colonies = ResearchButton(research, "Colonies", "Start colonizing the empty land \n "
                                                    "increases potential houses", "colon", 9, 15000,
                            requirements=[chemistry, smithing])
#is this an idle game now
steam = ResearchButton(research, "Steam Power", "Make the water work for you \n "
                                                    "allows passive resource gain", "steam", 9, 15000,
                            requirements=[steel, gunpowder])
layer_9 = [colonies,steam]

hygiene = ResearchButton(research, "Hygiene", "Your people can clean themselves \n "
                                                    "further reduces death", "clean", 10, 20000,
                            requirements=[steam, medicine])

industry = ResearchButton(research, "Industrialization", "Make your iron stronger \n "
                                                    "increases passive resource gain", "indus", 10, 20000,
                            requirements=[steam])

layer_10 = [hygiene,industry]
layers = {
    1: layer_1,
    2: layer_2,
    3: layer_3,
    4: layer_4,
    5: layer_5,
    6: layer_6,
    7: layer_7,
    8: layer_8,
    9: layer_9,
    10: layer_10
}

theme_button = Button("switch theme", color_set, x=800, y=200, width=250)
reset_button = Button("reset game", reset, x=800, y=400, width=250)

tab_buttons = [home_tab, research_tab, settings_tab, about_tab]
home_buttons = [spawn_button, build_button, hunter_increase_button, hunter_decrease_button, scholar_increase_button,
                scholar_decrease_button, gatherer_increase_button, gatherer_decrease_button, builder_increase_button,
                builder_decrease_button]
research_buttons = [button for layer in layers.values() for button in layer]
settings_buttons = [theme_button,reset_button]
buttons_list = [tab_buttons, home_buttons, research_buttons, settings_buttons]

home_scene()

while running:
    screen.fill(user_color_2)
    screen_width, screen_height = screen.get_size()
    mouse_x, mouse_y = pg.mouse.get_pos()
    tab_button = 0
    #event loop
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            break
        if event.type == pg.MOUSEBUTTONDOWN:
            button_clicked = True
        if event.type == pg.MOUSEBUTTONUP:
            button_clicked = False
        if current_scene == 'research':
            handle_research_scrolling(event)
    if current_scene == "home":
        for button in home_buttons:
            button.enabled = True
        for list in research_buttons, settings_buttons:
            for button in list:
                button.enabled = False
        home_text = text_font.render('home', True, user_color_1)
        home_rect = home_text.get_rect()
        home_rect.center = (500, 500)
        screen.blit(home_text, home_rect)
        hunter_text = text_font.render(f'{hunters} hunters', True, user_color_1)
        hunter_rect = hunter_text.get_rect()
        hunter_rect.center = (screen_width // 2, 225)
        screen.blit(hunter_text, hunter_rect)
        scholar_text = text_font.render(f'{scholars} scholars', True, user_color_1)
        scholar_rect = scholar_text.get_rect()
        scholar_rect.center = (screen_width // 2, 275)
        screen.blit(scholar_text, scholar_rect)
        gatherer_text = text_font.render(f'{gatherers} gatherers', True, user_color_1)
        gatherer_rect = gatherer_text.get_rect()
        gatherer_rect.center = (screen_width // 2, 325)
        screen.blit(gatherer_text, gatherer_rect)
        builder_text = text_font.render(f'{builders} builders', True, user_color_1)
        builder_rect = builder_text.get_rect()
        builder_rect.center = (screen_width // 2, 375)
        screen.blit(builder_text, builder_rect)

    if current_scene == "research":
        for list in home_buttons, settings_buttons:
            for button in list:
                button.enabled = False
        for button in research_buttons:
            button.enabled = True
        research_text = text_font.render('', True, user_color_1)
        research_rect = research_text.get_rect()
        research_rect.center = (500, 500)
        screen.blit(research_text, research_rect)

    if current_scene == "settings":
        for list in home_buttons, research_buttons:
            for button in list:
                button.enabled = False
        for button in settings_buttons:
            button.enabled = True
        settings_text = text_font.render('settings', True, user_color_1)
        settings_rect = settings_text.get_rect()
        settings_rect.center = (500, 500)
        screen.blit(settings_text, settings_rect)


    elif current_scene == "about":
        for list in home_buttons, research_buttons, settings_buttons:
            for button in list:
                button.enabled = False
        about_text = text_font.render('this really pulsars my cubes', True, user_color_1)
        about_rect = about_text.get_rect()
        about_rect.center = (800, 700)
        screen.blit(about_text, about_rect)
        stats_text = text_font.render(f'you have played for {seconds} {"seconds" if seconds != 1 else "second"}', True,
                                      user_color_1)
        stats_rect = stats_text.get_rect()
        stats_rect.center = (800, 400)
        screen.blit(stats_text, stats_rect)
        #button loooop
    for list in buttons_list:
        for button in list:
            if button.enabled:
                if isinstance(button, TabButton):
                    button.draw(50, tab_button)
                    if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                        button.draw(50, tab_button, True)
                        if button_clicked:
                            button.func()
                            button_clicked = False
                    tab_button += 1
                if civ or button is civilization or button in settings_buttons:
                    if isinstance(button, ResearchButton):

                        button.draw(400, 400, layers[button.layer].index(button))
                        if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                            button.draw(400, 400, layers[button.layer].index(button), True)
                            if button_clicked:
                                if button.is_researchable():
                                    button.func(button.id)
                                    button.used = True
                    else:
                        button.draw(screen_width / 2, screen_height / 2)
                        if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                            button.draw(screen_width / 2, screen_height / 2, True)
                            if button_clicked:
                                button.func()
                                button_clicked = False

    humans_text = text_font.render(f'{humans} {"people" if humans != 1 else "person"}', True, user_color_1)
    humans_rect = humans_text.get_rect()
    humans_rect.center = (100, 50)
    screen.blit(humans_text, humans_rect)

    food_text = text_font.render(f'{food} food', True, user_color_1)
    food_rect = food_text.get_rect()
    food_rect.center = (80, 100)
    screen.blit(food_text, food_rect)

    knowledge_text = text_font.render(f'{knowledge} knowledge', True, user_color_1)
    knowledge_rect = knowledge_text.get_rect()
    knowledge_rect.center = (130, 150)
    screen.blit(knowledge_text, knowledge_rect)

    resources_text = text_font.render(f'{resources} resources', True, user_color_1)
    resources_rect = resources_text.get_rect()
    resources_rect.center = (120, 200)
    screen.blit(resources_text, resources_rect)

    houses_text = text_font.render(f'{houses} houses', True, user_color_1)
    houses_rect = houses_text.get_rect()
    houses_rect.center = (100, 250)
    screen.blit(houses_text, houses_rect)

    workers = hunters + scholars + gatherers + builders
    unemployed = humans - unemployed
    pg.display.update()
    if food > food_storage:
        food = food_storage
    frame += 1

    if frame == 60:
        breed()
        food += passive_food
        seconds += 1
        if seconds % 5 == 0:
            work()
            eat()
            if food == 0:
                humans -= ceil(humans / 10)
        if seconds % 30 == 0:
            death()
        work()
        frame = 0

    clock.tick(60)
pg.quit()
