import pygame as pg
from math import floor, ceil
from random import uniform, randint
import asyncio
import sys

if sys.platform == "emscripten":
    from platform import window

#TODO age labels (v1.1)
#TODO adjust button sizes based on window size?
#TODO think of minigames (v1.1)
#TODO add flavor texts for research


pg.init()

tab_image = pg.image.load("media/tabs.png")
job_image = pg.image.load("media/jobs.png")
research_image = pg.image.load("media/research.png")
home_image = pg.image.load("media/home.png")

backup_time = 0
used_buttons = []
research_buttons = []
prompt = 0
research_gain = 1
food_storage = 20
storage_scale = 1
passive_knowledge = 0
passive_resources = 0
house_price = 10
hunt_scale = 1
gather_scale = 1
workers = 0
clicking = False
allow_building = False
death_scale = 3
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
gatherers = 0
unemployed = 0
knowledge = 0
button_font = pg.font.SysFont('Corbel', 35, True)
text_font = pg.font.SysFont('Corbel', 50)
clock = pg.time.Clock()
screen = pg.display.set_mode((1600, 900))
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
prompts = {
    0: "Welcome to Untitled Incremental",
    1: "This is an incremental game where you build a civilization from nothing",
    2: "These are your four tabs",
    3: "Home holds the buttons allowing you to bring people into the world",
    4: "Research helps your society improve",
    5: "Your people can have jobs that \n"
       "collect materials, hunt, and gain knowledge",
    6: "Resources are used for houses",
    7: "Your people also need food, and \n"
       "die of natural causes",
    8: "Good Luck! (continue on for a note from the dev)",
    9: "Hi, thank you for playing! Right now the game is pretty simple and repetitive\n"
       "but there is a lot more planned for the future \n"
       "I originally intended for a minigames system to be added among other things, \n"
       "But life got in the way and I would not have been able to ship for High Seas\n"
       "Thank you for being here anyways! -PulsarCubes "
}


class TextCache:
    def __init__(self):
        self.cache = {}
        self.dirty_rects = []
        self.previous_frame_rects = []

    def get_text(self, text, font, color) -> tuple:
        cache_key = f"{text}_{id(font)}_{color}"
        is_new = False

        if cache_key not in self.cache:
            self.cache[cache_key] = font.render(text, True, color)
            is_new = True

        return self.cache[cache_key], is_new

    def clear(self):
        self.cache.clear()

    def add_dirty_rect(self, rect: pg.Rect):
        self.dirty_rects.append(rect)

    def get_update_rects(self) -> list[pg.Rect]:
        update_rects = self.dirty_rects + self.previous_frame_rects
        self.previous_frame_rects = self.dirty_rects.copy()
        self.dirty_rects.clear()
        return update_rects


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.text_cache = TextCache()
        self.background = pg.Surface(screen.get_size())
        self.background_dirty = True

    def render_text(self, text, font, color,
                    position, center=True) -> pg.Rect:
        text_surface, is_new = self.text_cache.get_text(text, font, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position

        self.text_cache.add_dirty_rect(text_rect)

        self.screen.blit(text_surface, text_rect)
        return text_rect

    def render_button(self, button, hover=False):

        if hover:
            color = (150, 150, 150)
        else:
            color = user_color_1

        pg.draw.rect(self.screen, color, button.button_rect, width=4, border_radius=1)
        self.text_cache.add_dirty_rect(button.button_rect)

        self.render_text(
            button.text,
            button_font,
            color,
            button.button_rect.center
        )

    def update_display(self):
        update_rects = self.text_cache.get_update_rects()
        if update_rects:
            pg.display.update(update_rects)

    def render_background(self):
        if self.background_dirty:
            self.background.fill(user_color_2)
            self.background_dirty = False
        self.screen.blit(self.background, (0, 0))
        self.text_cache.add_dirty_rect(self.screen.get_rect())


renderer = GameRenderer(screen)


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

        old_rect = self.button_rect.copy()
        self.button_rect.center = x, y

        renderer.text_cache.add_dirty_rect(old_rect)
        renderer.text_cache.add_dirty_rect(self.button_rect)

        renderer.render_button(self, hover)

    def is_visible(self) -> bool:
        return self.enabled


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
    def __init__(self, func, title, desc, id, layer, point_req, enabled=True, requirements=None, used=False,
                 flavor_text=""):
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
        self.flavor_text = flavor_text

    def draw(self, x, y, num, hover=False):
        width = 500
        button_spacing = 20
        index = layers[self.layer].index(self)
        num_in_layer = len(layers[self.layer])
        research_buttons_width = width * num_in_layer + button_spacing * (num_in_layer - 1)

        desc_font = pg.font.SysFont('Corbel', 30)
        smol_font = pg.font.SysFont('Corbel', 25, bold=True)

        moved_x = (screen_width - research_buttons_width) // 2 + num * (width + button_spacing)
        moved_y = self.layer * 300 + scroll_y

        if moved_y + 175 < 350 or moved_y > screen_height - 50:
            self.button_rect = pg.Rect(moved_x, moved_y, width, 175)
            return

        old_rect = self.button_rect.copy()

        self.button_rect = pg.Rect(moved_x, moved_y, width, 200)
        self.button_rect.centerx = moved_x + width // 2

        renderer.text_cache.add_dirty_rect(old_rect)
        renderer.text_cache.add_dirty_rect(self.button_rect)

        if (hover and not self.used) or not self.is_researchable():
            color = (150, 150, 150)
        elif self.used:
            color = (34, 139, 34)
        else:
            color = (255, 236, 161)

        pg.draw.rect(screen, color, self.button_rect ,width=5, border_radius=1)

        title_pos = (self.button_rect.centerx, moved_y+50)
        renderer.render_text(self.title, pg.font.SysFont('Corbel', 50, True), user_color_1, title_pos)

        desc_pos = (self.button_rect.centerx, moved_y + 100)
        renderer.render_text(self.desc, desc_font, user_color_1, desc_pos)

        req_pos = (self.button_rect.left + 10, self.button_rect.top + 10)
        renderer.render_text(shrink_num(self.point_req), smol_font, user_color_1, req_pos, center=False)

        flavor_pos = (self.button_rect.centerx, self.button_rect.bottom - 30)
        renderer.render_text(self.flavor_text, desc_font, (150, 150, 150), flavor_pos)

        if self.layer != 20:
            pg.draw.line(screen, user_color_1,
                         self.button_rect.midbottom,
                         (self.button_rect.centerx, self.button_rect.bottom + 25),
                         4)
            renderer.text_cache.add_dirty_rect(pg.Rect(
                self.button_rect.centerx - 2,
                self.button_rect.bottom,
                4,
                25
            ))

        if self.layer != 1:
            line_rect = pg.Rect(
                self.button_rect.centerx - 2,
                self.button_rect.top - 75,
                4,
                75
            )
            pg.draw.line(screen, user_color_1,
                         self.button_rect.midtop,
                         (self.button_rect.centerx, self.button_rect.top - 75),
                         4)
            renderer.text_cache.add_dirty_rect(line_rect)

            num_in_previous = len(layers[self.layer - 1])
            if index == num_in_layer - 1:
                if num_in_layer >= num_in_previous:
                    horizontal_line_rect = pg.Rect(
                        self.button_rect.centerx - (research_buttons_width - width),
                        self.button_rect.top - 77,
                        research_buttons_width - width,
                        4
                    )
                    pg.draw.line(screen, user_color_1,
                                 (self.button_rect.centerx, self.button_rect.top - 75),
                                 (self.button_rect.centerx - (research_buttons_width - width),
                                  self.button_rect.top - 75),
                                 4)
                    renderer.text_cache.add_dirty_rect(horizontal_line_rect)
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


    def is_researchable(self) -> bool:
        return (all([req.used for req in self.requirements]) and self.point_req <= knowledge) or self.used

    def is_visible(self) -> bool:
        return False if self.layer * 300 + scroll_y + 175 < 350 or self.layer * 300 + scroll_y > screen_height - 50 else True

    def recover(self):
        self.used = True
        research(self.id)

def next():
    global prompt
    prompt += 1


def back():
    global prompt
    if prompt > 0:
        prompt -= 1


def skip():
    global prompt
    prompt = len(prompts)


def reset():
    global humans, food_storage, food, resources, houses, research_gain, knowledge, civ, death_scale, storage_scale, passive_food, hunters, gatherers, builders, scholars
    civ = False
    humans, resources, houses, knowledge, passive_food, hunters, gatherers, builders, scholars = (
        0, 0, 0, 0, 0, 0, 0, 0, 0)
    food = 10
    research_gain = 1
    food_storage = 20
    death_scale = 3
    storage_scale = 1

    for layer in layers.values():
        for button in layer:
            button.used = False
    keys = []
    for i in range(window.localStorage.length):
        keys.append(window.localStorage.key(i))
    while keys:
        window.localStorage.removeItem(keys.pop())

def backup():
    global used_buttons, knowledge, food, houses, resources, humans, hunters, gatherers, builders, scholars, seconds, backup_time
    backup_time = seconds
    researched = ''
    vars = ''
    if sys.platform == "emscripten":
        for button in research_buttons:
            if button in used_buttons:
                researched += f'{button.id} '
        window.localStorage.setItem("untitled_incremental_research", researched)
        for var in (knowledge, food, houses, resources, humans, hunters, gatherers, scholars):
            vars += str(var) + ','
        vars += str(builders)
        window.localStorage.setItem("untitled_incremental_vars",vars)

def load_save():
    global knowledge, food, houses, resources, humans, hunters, gatherers, builders, scholars, research_buttons
    if sys.platform == "emscripten":
        try:
            researched = window.localStorage.getItem("untitled_incremental_research")
            if researched != '' or None:
                for button in research_buttons:
                    if str(button.id) in researched:
                        button.recover()
            try:
                vars = window.localStorage.getItem("untitled_incremental_vars").split(",")
            except AttributeError:
                vars = ''
            if vars != '':
                for value in vars:
                    if value != '':
                        vars[vars.index(value)] = int(value)

                knowledge, food, houses, resources, humans, hunters, gatherers, scholars, builders  = vars
        except TypeError:
            print('no backup found')



def home_scene():
    global current_scene
    current_scene = "home"


def research_scene():
    global current_scene
    global research_buttons
    current_scene = "research"
    for button in research_buttons:
        button.enabled = True


def settings_scene():
    global current_scene
    current_scene = "settings"


def about_scene():
    global current_scene
    current_scene = "about"


def spawn():
    global humans
    if not singularity.used:
        if houses == 0:
            if humans < 5:
                humans += 1
        else:
            if humans <= 5 * (houses + 1):
                humans += 1


def build_house():
    global resources
    global houses
    global food_storage
    global house_price
    if resources >= house_price:
        houses += 1
        food_storage += ceil(10 * storage_scale)
        resources -= house_price


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
    global hunters, scholars, gatherers, resources, food, knowledge, seconds, food_storage, research_gain, builders, hunt_scale, gather_scale, houses
    if food < food_storage:
        food += ceil(hunters * hunt_scale)
    knowledge += ceil(scholars * research_gain)
    if seconds % 2 == 0:
        resources += ceil(gatherers * gather_scale)
    if seconds % 30 == 0:
        houses += ceil(builders)


def death():
    global humans, death_scale
    global workers, hunters, scholars, gatherers, builders

    work_list = [workers, hunters, scholars, gatherers]
    humans -= (ceil((uniform(humans / 100, humans / 50) * death_scale)))

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


def shrink_num(num):
    if num < 1000:
        return str(num)
    if 1000 <= num < 1000000:
        return str(num / 1000) + "K"
    if num >= 1000000:
        return str(num / 1000000) + "M"


def shrink_time(secs):
    if 3600 > secs:
        return f"{secs // 60} {'minutes' if secs // 60 != 1 else 'minute'} and {secs % 60} {'seconds' if secs % 60 != 1 else 'second'}"

    if secs >= 3600:
        return f"{secs // 3600} {'hours' if secs // 3600 != 1 else 'hour'}, {(secs % 3600) // 60} {'minutes' if (secs % 3600) // 60 != 1 else 'minute'}, and {(secs % 3600) % 60} {'seconds' if ((secs % 3600) % 60) != 1 else 'second'}"


def handle_research_scrolling(event):
    global scroll_y, total_research_height

    max_layer = max(layers.keys())
    total_research_height = (max_layer * 300) + 400

    if event.type == pg.MOUSEWHEEL:
        renderer.background_dirty = True
        scroll_y += event.y * scroll_speed

        scroll_y = min(0, scroll_y)
        scroll_y = max(-(total_research_height - screen_height + 100), scroll_y)


def research(id):
    global civ, knowledge, research_gain, death_scale, food_storage, storage_scale, passive_food, hunt_scale, gather_scale, passive_knowledge, passive_resources

    if id == "civ" or civilization.used:
        civ = True
    if id == "fire" or fire.used:
        death_scale = 0.5
        if not fire.used:
            knowledge -= fire.point_req
    if id == "stone" or stone_tools.used:
        global allow_building
        allow_building = True
        if not stone_tools.used:
            knowledge -= stone_tools.point_req
    if id == "pot" or pottery.used:
        food_storage = 100
        storage_scale = 2
        if not pottery.used:
            knowledge -= pottery.point_req
    if id == "culti" or cultivation.used:
        passive_food = 1
        if not cultivation.used:
            knowledge -= cultivation.point_req
    if id == "writing" or writing.used:
        if not writing.used:
            research_gain *= 2
            passive_knowledge = 1
            knowledge -= writing.point_req
    if id == "metal" or metallurgy.used:
        gather_scale = 2
        if not metallurgy.used:
            knowledge -= metallurgy.point_req
    if id == "edu" or education.used:
        if not education.used:
            research_gain *= 2
            passive_knowledge *= 2
            knowledge -= education.point_req
    if id == "iron" or iron.used:
        gather_scale = 3
        hunt_scale = 2
        if not iron.used:
            knowledge -= iron.point_req
    if id == "butch" or butchery.used:
        hunt_scale = 3
        if not butchery.used:
            knowledge -= butchery.point_req
    if id == "agri" or agriculture.used:
        passive_food = 3
        if not agriculture.used:
            knowledge -= agriculture.point_req
    if id == "smith" or smithing.used:
        if not smithing.used:
            storage_scale *= 2
            food_storage = 200
            hunt_scale = 4
            gather_scale = 4
            knowledge -= smithing.point_req
    if id == "math" or mathematics.used:
        if not mathematics.used:
            research_gain *= 1.5
            passive_knowledge *= 2
            knowledge -= mathematics.point_req
    if id == "fert" or fertilizer.used:
        if not fertilizer.used:
            passive_food *= 2
            knowledge -= fertilizer.point_req
    if id == "chem" or chemistry.used:
        if not chemistry.used:
            research_gain *= 2
            passive_knowledge *= 1.5
            knowledge -= chemistry.point_req
    if id == "steel" or steel.used:
        if not steel.used:
            gather_scale *= 1.5
            hunt_scale *= 1.5
            knowledge -= steel.point_req
    if id == "meds" or medicine.used:
        if not medicine.used:
            death_scale *= 0.5
            knowledge -= medicine.point_req
    if id == "boom" or gunpowder.used:
        if not gunpowder.used:
            gather_scale *= 2
            knowledge -= gunpowder.point_req
    if id == "steam" or steam.used:
        if not steam.used:
            gather_scale *= 2
            passive_food *= 1.5
            passive_resources = 1
            knowledge -= steam.point_req
    if id == "colon" or colonies.used:
        if not colonies.used:
            storage_scale *= 2
            food_storage *= 2
            passive_resources *= 1.5
            knowledge -= colonies.point_req
    if id == "indus" or industry.used:
        if not industry.used:
            gather_scale *= 2
            hunt_scale *= 2
            passive_food *= 2
            passive_resources *= 2
            knowledge -= industry.point_req
    if id == "clean" or hygiene.used:
        if not hygiene.used:
            death_scale *= 0.5
            knowledge -= hygiene.point_req
    if id == "elec" or electricity.used:
        if not electricity.used:
            research_gain *= 2
            gather_scale *= 1.5
            passive_resources *= 2
            passive_knowledge *= 1.5
            knowledge -= electricity.point_req
    if id == "mats" or materials.used:
        if not materials.used:
            storage_scale *= 1.5
            gather_scale *= 1.5
            knowledge -= materials.point_req
    if id == "city" or cities.used:
        if not cities.used:
            storage_scale *= 2
            passive_food *= 1.5
            passive_resources *= 1.5
            knowledge -= cities.point_req
    if id == "poly" or plastics.used:
        if not plastics.used:
            storage_scale *= 1.5
            knowledge -= plastics.point_req
    if id == "anti" or antibiotics.used:
        if not antibiotics.used:
            death_scale *= 0.25
            knowledge -= antibiotics.point_req
    if id == "food" or processed.used:
        if not processed.used:
            food_storage *= 2
            passive_food *= 1.5
            death_scale *= 1.2
            knowledge -= processed.point_req
    if id == "semi" or semiconductors.used:
        if not semiconductors.used:
            research_gain *= 2
            passive_knowledge *= 2
            knowledge -= semiconductors.point_req
    if id == "space" or SPACE.used:
        if not SPACE.used:
            research_gain *= 1.5
            passive_knowledge *= 1.5
            knowledge -= SPACE.point_req
    if id == "gene" or genetics.used:
        if not genetics.used:
            death_scale *= 0.5
            research_gain *= 1.5
            passive_knowledge *= 1.5
            knowledge -= genetics.point_req
    if id == "GMO" or GMOs.used:
        if not GMOs.used:
            passive_food *= 2
            food_storage *= 1.5
            death_scale *= 1.1
            knowledge -= GMOs.point_req
    if id == "int" or internet.used:
        if not internet.used:
            research_gain *= 2
            passive_knowledge *= 3
            knowledge -= internet.point_req
    if id == "fuse" or fusion.used:
        if not fusion.used:
            gather_scale *= 3
            research_gain *= 1.5
            passive_resources *= 4
            knowledge -= fusion.point_req
    if id == "robo" or robots.used:
        if not robots.used:
            gather_scale *= 2
            hunt_scale *= 2
            passive_food *= 2
            passive_resources *= 3
            passive_knowledge *= 2
            knowledge -= robots.point_req
    if id == "quan" or quantum.used:
        if not quantum.used:
            research_gain *= 3
            passive_knowledge *= 4
            knowledge -= quantum.point_req
    if id == "pink" or food_eng.used:
        if not food_eng.used:
            passive_food *= 3
            food_storage *= 2
            knowledge -= food_eng.point_req
    if id == "AI" or AI.used:
        if not AI.used:
            research_gain *= 3
            gather_scale *= 2
            hunt_scale *= 2
            passive_knowledge *= 5
            passive_resources *= 2
            knowledge -= AI.point_req
    if id == "nano" or nanotubes.used:
        if not nanotubes.used:
            storage_scale *= 3
            gather_scale *= 2
            passive_resources *= 3
            knowledge -= nanotubes.point_req
    if id == "organ" or organs.used:
        if not organs.used:
            death_scale *= 0.25
            knowledge -= organs.point_req
    if id == "wet" or wetware.used:
        if not wetware.used:
            research_gain *= 2
            death_scale *= 0.5
            passive_knowledge *= 3
            knowledge -= wetware.point_req
    if id == "space" or space_colony.used:
        if not space_colony.used:
            storage_scale *= 3
            passive_food *= 3
            passive_resources *= 4
            knowledge -= space_colony.point_req
    if id == "ftl" or ftl.used:
        if not ftl.used:
            research_gain *= 3
            gather_scale *= 3
            passive_resources *= 5
            passive_knowledge *= 4
            knowledge -= ftl.point_req
    if id == "entr" or entropy.used:
        if not entropy.used:
            research_gain *= 4
            gather_scale *= 4
            hunt_scale *= 4
            passive_food *= 4
            passive_resources *= 6
            passive_knowledge *= 6
            death_scale *= 0.1
            knowledge -= entropy.point_req
    if id == "sing" or singularity.used:
        if not singularity.used:
            knowledge -= singularity.point_req


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


async def main():
    global civilization, fire, stone_tools, pottery, cultivation, writing, metallurgy, education, agriculture, butchery, iron, mathematics, fertilizer, smithing, chemistry, steel, medicine, gunpowder, colonies, steam, hygiene, industry, electricity, materials, cities, antibiotics, plastics, processed, semiconductors, SPACE, genetics, GMOs, internet, fusion, robots, quantum, food_eng, nanotubes, AI, organs, wetware, ftl, space_colony, entropy, singularity, layers, screen_width, screen_height, running, button_clicked, button, humans, food, resources, seconds, knowledge, unemployed, frame, workers, research_buttons
    global tab_image
    global running
    global button_clicked
    global prompt
    global prompts
    global screen_width, screen_height
    global research_buttons

    tutorial = True
    prompt = 0
    forward_button = Button("Next", next, x=screen_width // 2 + 200, y=screen_height // 2 + 300)
    back_button = Button("Back", back, x=screen_width // 2 - 200, y=screen_height // 2 + 300)
    skip_button = Button("Skip", skip, x=screen_width // 2, y=screen_height // 2 + 300)
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
    civilization = ResearchButton(research, "Civilization", "The dawn of your society \n allows life and research",
                                  "civ", 1, 0, flavor_text="we live in a society")
    layer_1 = [civilization]
    fire = ResearchButton(research, "Fire", "       Your people discover fire, "
                                            "\n Reduces death chance through cooking", "fire", 2, 50,
                          requirements=[civilization])
    stone_tools = ResearchButton(research, "Stone Tools", "Your people invent basic tools,"
                                                          "\n Allows home building", "stone", 2, 50,
                                 flavor_text="stoned",
                                 requirements=[civilization])
    layer_2 = [fire, stone_tools]
    pottery = ResearchButton(research, "Pottery", "Your people discover pottery, "
                                                  "\n Increases food storage by 100, scales storage ", "pot",
                             3, 200, flavor_text="not the cool pot",
                             requirements=[i for i in layer_2])
    cultivation = ResearchButton(research, "Cultivation", "Your people invent basic crop cultivation \n "
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
                               flavor_text="big brain",
                               requirements=[writing])
    layer_4 = [metallurgy, education]
    agriculture = ResearchButton(research, "Agriculture", "Develop advanced agriculture \n "
                                                          "increased passive food growth", "agri", 5, 3000,
                                 requirements=[education, cultivation])
    butchery = ResearchButton(research, "Butchery", "More efficient meat slicing \n "
                                                    "hunters produce more food", "butch", 5, 2500,
                              requirements=[i for i in layer_4])
    iron = ResearchButton(research, "Iron", "Your people learn to use iron \n "
                                            "even more efficient mining and hunting", "iron", 5, 4000,
                          requirements=[metallurgy])
    layer_5 = [butchery, iron, agriculture]
    mathematics = ResearchButton(research, "Mathematics", "Your people invent a math system \n "
                                                          "further increases scholar gain", "math", 6, 8000,
                                 requirements=[i for i in layer_5])
    fertilizer = ResearchButton(research, "Fertilizer", "Your people learn to fertilize fields \n "
                                                        "more passive food", "fert", 6, 4500,
                                requirements=[agriculture, butchery])
    smithing = ResearchButton(research, "Smithing", "Form metal into better shapes \n "
                                                    "increase storage, hunting, resource gain", "smith", 6, 6000,
                              requirements=[iron])
    layer_6 = [mathematics, fertilizer, smithing]
    chemistry = ResearchButton(research, "Chemistry", "Basic chemistry \n "
                                                      "increases scholarly gain", "chem", 7, 6000,
                               requirements=[i for i in layer_6])
    layer_7 = [chemistry]

    steel = ResearchButton(research, "Steel", "Make your iron stronger \n "
                                              "increase resource gain", "steel", 8, 10000,
                           requirements=[chemistry, smithing])
    medicine = ResearchButton(research, "Medicine", "Unlock basic medicine \n "
                                                    "reduce death", "meds", 8, 7500,
                              flavor_text="we need the medicine drug",
                              requirements=[chemistry])
    gunpowder = ResearchButton(research, "Gunpowder", "Invent some explosives \n "
                                                      "mooore resource gain from mining", "boom", 8, 12000,
                               flavor_text="we bring the boom",
                               requirements=[chemistry, smithing])
    layer_8 = [gunpowder, medicine, steel]
    colonies = ResearchButton(research, "Colonies", "Start colonizing the empty land \n "
                                                    "increases room for resources", "colon", 9, 15000,
                              flavor_text="so much room for activities",
                              requirements=[chemistry, smithing])
    steam = ResearchButton(research, "Steam Power", "Make the water work for you \n "
                                                    "allows passive resource gain", "steam", 9, 15000,
                           flavor_text="is this an idle game now",
                           requirements=[steel, gunpowder])
    layer_9 = [colonies, steam]
    hygiene = ResearchButton(research, "Hygiene", "Your people can clean themselves \n "
                                                  "further reduces death", "clean", 10, 20000,
                             flavor_text="no more pheromones",
                             requirements=[steam, medicine])
    industry = ResearchButton(research, "Industrialization", "Start industrializing \n "
                                                             "increases passive resource gain", "indus", 10, 20000,
                              requirements=[steam])
    layer_10 = [hygiene, industry]
    electricity = ResearchButton(research, "Electricity", "Start producing and using electricity \n "
                                                          "increase passive resources AGAIN", "elec", 11, 25000,
                                 flavor_text="shocking",
                                 requirements=[industry])
    materials = ResearchButton(research, "Material Science", "Start developing better materials \n "
                                                             "reduces house price", "mats", 11, 25000,
                               requirements=[industry])
    layer_11 = [electricity, materials]
    cities = ResearchButton(research, "Cities", "People start living closer \n "
                                                "increases potential houses further", "city", 12, 30000,
                            requirements=[i for i in layer_11])
    antibiotics = ResearchButton(research, "Antibiotics", "Create antibiotics \n "
                                                          "further reduce random death", "anti", 12, 30000,
                                 requirements=[i for i in layer_11])
    plastics = ResearchButton(research, "Plastics", "Invent polymers \n "
                                                    "further reduces house price", "poly", 12, 35000,
                              requirements=[materials])
    layer_12 = [cities, antibiotics, plastics]
    processed = ResearchButton(research, "Processed Foods", "Start processing food \n "
                                                            "increase food gain, random death increase", "food", 13,
                               40000,
                               requirements=[antibiotics, plastics])
    semiconductors = ResearchButton(research, "Semiconductors", "invent semiconductors \n "
                                                                "increase scholar gain, passive knowledge", "semi", 13,
                                    45000, flavor_text="tricking rocks into thinking",
                                    requirements=[i for i in layer_12])
    layer_13 = [processed, semiconductors]
    SPACE = ResearchButton(research, "Space Travel", "Go to space \n "
                                                     "it's just cool dude", "space", 14, 50000, flavor_text="SPACESHIP",
                           requirements=[i for i in layer_13])
    genetics = ResearchButton(research, "Semiconductors", "do genetic research \n "
                                                          "reduce random death more", "gene", 14, 55000,
                              requirements=[semiconductors])
    layer_14 = [SPACE, genetics]
    GMOs = ResearchButton(research, "GMOs", "genetically modify crops \n "
                                            "increase passive food", "GMO", 15, 60000,
                          requirements=[genetics])
    internet = ResearchButton(research, "The Internet", "Create the web \n "
                                                        "increase scholar gain", "int", 15, 70000,
                              flavor_text="what could go wrong",
                              requirements=[SPACE])
    layer_15 = [GMOs, internet]
    fusion = ResearchButton(research, "Fusion Power", "invent fusion power \n "
                                                      "increase scholar gain", "fuse", 16, 100000,
                            requirements=[internet])
    robots = ResearchButton(research, "Advanced Robotics", "Build robots \n "
                                                           "increase passive gain of everything", "robo", 16, 150000,
                            flavor_text="why should we do the hard things",
                            requirements=[internet])
    quantum = ResearchButton(research, "Quantum Computing", "Invent quantum computers \n "
                                                            "increase scholar gain", "quan", 16, 200000,
                             requirements=[internet])
    layer_16 = [fusion, robots, quantum]
    food_eng = ResearchButton(research, "Food Engineering", "Engineer food harder \n "
                                                            "decrease food consume", "pink", 17, 250000,
                              flavor_text="who doesn't like pink paste",
                              requirements=[GMOs])
    nanotubes = ResearchButton(research, "Nanotubes", "more advanced materials \n "
                                                      "reduce house price", "nano", 17, 250000,
                               requirements=[robots])
    AI = ResearchButton(research, "AI", "Invent sentient AI \n "
                                        "increase scholar gain", "AI", 17, 300000,
                        flavor_text="HOW I HAVE COME TO HATE",
                        requirements=[i for i in layer_16])
    layer_17 = [food_eng, nanotubes, AI]
    organs = ResearchButton(research, "Artificial Organs", "more advanced organs \n "
                                                           "end random death", "organ", 18, 500000,
                            flavor_text="theseus?",
                            requirements=[nanotubes, food_eng])
    wetware = ResearchButton(research, "Wetware", "Invent wetware computers \n "
                                                  "increase scholar gain MORE", "wet", 18, 1000000,
                             flavor_text="it watches",
                             requirements=[i for i in layer_17])
    layer_18 = [organs, wetware]
    ftl = ResearchButton(research, "FTL Travel", "FTL Travel \n "
                                                 "more room for things", "ftl", 19, 2000000, flavor_text="weeeee",
                         requirements=[i for i in layer_18])
    space_colony = ResearchButton(research, "Space colonies", "Colonize the universe \n "
                                                              "insane resource production", "space", 19, 1500000,
                                  requirements=[i for i in layer_18])
    entropy = ResearchButton(research, "Entropy Reversal", "Stop the heat death \n "
                                                           "what left is there to gain", "entr", 19, 5000000,
                             requirements=[i for i in layer_18])
    layer_19 = [ftl, space_colony, entropy]
    singularity = ResearchButton(research, "Singularity", "Combine \n "
                                                          "the end", "sing", 20, 10000000,
                                 requirements=[i for i in layer_19])
    layer_20 = [singularity]
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
        10: layer_10,
        11: layer_11,
        12: layer_12,
        13: layer_13,
        14: layer_14,
        15: layer_15,
        16: layer_16,
        17: layer_17,
        18: layer_18,
        19: layer_19,
        20: layer_20
    }
    theme_button = Button("switch theme", color_set, x=800, y=200, width=250)
    tutorial_button = Button("tutorial", tutorial, x=800, y=300, width=250)
    reset_button = Button("reset game", reset, x=800, y=400, width=250)
    backup_button = Button("backup", backup, x=800, y=500, width=250)
    tab_buttons = [home_tab, research_tab, settings_tab, about_tab]
    home_buttons = [spawn_button, build_button, hunter_increase_button, hunter_decrease_button, scholar_increase_button,
                    scholar_decrease_button, gatherer_increase_button, gatherer_decrease_button,
                    builder_increase_button,
                    builder_decrease_button]
    tutorial_buttons = [forward_button, back_button, skip_button]
    research_buttons = [button for layer in layers.values() for button in layer]
    settings_buttons = [theme_button, reset_button, tutorial_button, backup_button]
    buttons_list = [tab_buttons, home_buttons, research_buttons, settings_buttons]
    home_scene()
    if sys.platform == "emscripten":
        load_save()
    while running:
        if tutorial:
            screen.fill(user_color_2)
            if prompt == 2:
                image_rect = tab_image.get_rect()
                image_rect.center = (screen_width // 2, screen_height // 2 + 100)
                screen.blit(tab_image, image_rect)
            if prompt == 3:
                image_rect = home_image.get_rect()
                image_rect.center = (screen_width // 2, screen_height // 2 + 100)
                screen.blit(home_image, image_rect)
            if prompt == 4:
                image_rect = research_image.get_rect()
                image_rect.center = (screen_width // 2, screen_height // 2 + 100)
                screen.blit(research_image, image_rect)
            if prompt == 5:
                image_rect = job_image.get_rect()
                image_rect.center = (screen_width // 2, screen_height // 2 + 100)
                screen.blit(job_image, image_rect)
            mouse_x, mouse_y = pg.mouse.get_pos()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    break
                if event.type == pg.MOUSEBUTTONDOWN:
                    button_clicked = True
                if event.type == pg.MOUSEBUTTONUP:
                    button_clicked = False

            for button in tutorial_buttons:
                if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                    button.draw(0, 0, hover=True)
                    if button_clicked:
                        button.func()
                        button_clicked = False
                else:
                    button.draw(0, 0, hover=False)
            if prompt >= len(prompts):
                tutorial = False
            else:
                text = text_font.render(prompts[prompt], True, user_color_1)
                text_rect = text.get_rect()
                text_rect.center = (screen_width // 2, screen_height // 2 - 200)
                screen.blit(text, text_rect)
            clock.tick(60)
            pg.display.update()

        else:
            renderer.render_background()
            screen_width, screen_height = screen.get_size()
            mouse_x, mouse_y = pg.mouse.get_pos()
            tab_button = 0
            # event loop
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
                renderer.render_text(f'{hunters} hunters',text_font, user_color_1,(screen_width // 2,225))
                renderer.render_text(f'{scholars} scholars', text_font, user_color_1, (screen_width // 2, 275))
                renderer.render_text(f'{gatherers} {" gatherers" if not metallurgy.used else " miners"}',text_font, user_color_1,(screen_width // 2, 325))
                renderer.render_text(f'{builders} builders', text_font, user_color_1, (screen_width // 2, 375))

            if current_scene == "research":
                for list in home_buttons, settings_buttons:
                    for button in list:
                        button.enabled = False

            if current_scene == "settings":
                for list in home_buttons, research_buttons:
                    for button in list:
                        button.enabled = False
                for button in settings_buttons:
                    button.enabled = True


            elif current_scene == "about":
                for list in home_buttons, research_buttons, settings_buttons:
                    for button in list:
                        button.enabled = False
                about_text = text_font.render('this really pulsars my cubes', True, user_color_1)
                about_rect = about_text.get_rect()
                about_rect.center = (800, 700)
                screen.blit(about_text, about_rect)
                renderer.render_text(f'you have played for {shrink_time(seconds)}',text_font, user_color_1, (800, 400))
                renderer.render_text(f'last backup {shrink_time(seconds-backup_time)} ago', text_font, user_color_1, (800, 500))

                # button loooop
            for list in buttons_list:
                for button in list:
                    if button.enabled:
                        if isinstance(button, TabButton):
                            hover = pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y)
                            button.draw(50, tab_button, hover)
                            if button_clicked and hover:
                                button.func()
                                button_clicked = False
                                renderer.text_cache.clear()
                            tab_button += 1
                        elif (civ or button is civilization or button in settings_buttons) and button.is_visible:
                            if isinstance(button, ResearchButton):

                                hover = pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y)
                                button.draw(400, 400, layers[button.layer].index(button), hover)
                                if hover and button_clicked:
                                    if button.is_researchable():
                                        button.func(button.id)
                                        button.used = True
                                        used_buttons.append(button)
                                        renderer.text_cache.clear()
                            else:
                                button.draw(screen_width / 2, screen_height / 2)
                                if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                                    button.draw(screen_width / 2, screen_height / 2, True)
                                    if button_clicked:
                                        button.func()
                                        button_clicked = False

            renderer.render_text(f'{shrink_num(humans)} {"people" if humans != 1 else "person"}', text_font, user_color_1, (120, 50))
            renderer.render_text(f'{shrink_num(food)} food', text_font,
                                 user_color_1, (100, 100))
            renderer.render_text(f'{shrink_num(knowledge)} knowledge', text_font,
                                 user_color_1, (150, 150))
            renderer.render_text(f'{shrink_num(resources)} resources',text_font, user_color_1, (140, 200))
            renderer.render_text(f'{houses} houses', text_font, user_color_1, (120, 250))
            workers = hunters + scholars + gatherers + builders
            unemployed = humans - unemployed

            if food > food_storage:
                food = food_storage
            frame += 1

            if frame == 60:
                breed()
                food += passive_food
                resources += passive_resources
                knowledge += passive_knowledge
                seconds += 1
                if seconds % 5 == 0:
                    work()
                    eat()
                    if food == 0:
                        humans -= ceil(humans / 10)

                if seconds % 30 == 0:
                    death()
                    backup()

                work()
                renderer.text_cache.clear()
                frame = 0
        renderer.update_display()
        clock.tick(60)
        await asyncio.sleep(0)

    pg.quit()


if __name__ == "__main__":
    asyncio.run(main())
