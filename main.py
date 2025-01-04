import pygame as pg
from math import floor

#remember to use pygbag you pygfag

#happiness? resources? adsdasdasdasdasdasasdasd
#TODO adjust button sizes based on window size, scrolling guhhh

pg.init()

state = 1
humans = 0
hunters = 0
scholars = 0
unemployed = 0
scholar_points=0
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
user_color_1 = (0,0,0)
user_color_2 = (255,255,255)


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
        if self.x is not None and self.y is not None:
            x, y = self.x, self.y
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
    def __init__(self, func, title, desc, id, layer, enabled=True, requirements=[], used=False):
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

    def draw(self, x, y, num, hover=False):
        width = 500
        button_spacing = 20
        index = layers[self.layer].index(self)
        num_in_layer = len(layers[self.layer])
        research_buttons_width = width * num_in_layer + button_spacing * (num_in_layer-1)
        title_font = pg.font.SysFont('Corbel', 50, True)
        desc_font = pg.font.SysFont('Corbel', 30)
        desc_text = desc_font.render(self.desc, True, user_color_1)
        title_text = title_font.render(self.title, True, user_color_1)
        title_rect = title_text.get_rect()
        start_x = (screen_width - research_buttons_width) // 2
        moved_x = start_x + num * (width + button_spacing)
        moved_y = self.layer * 300

        title_rect.center = (moved_x + width // 2, moved_y)
        desc_rect = desc_text.get_rect()
        desc_rect.y = title_rect.bottom
        desc_rect.centerx = moved_x + width // 2
        self.button_rect = title_rect.union(desc_rect)
        self.button_rect.inflate_ip(width - self.button_rect.width, 20)
        self.button_rect.height = 175
        self.button_rect.centerx = moved_x + width // 2
        if hover or self.used:
            pg.draw.rect(screen, (150, 150, 150), self.button_rect, width=5, border_radius=1)
            desc_text = desc_font.render(self.desc, True, (150, 150, 150))
            title_text = title_font.render(self.title, True, (150, 150, 150))
        else:
            pg.draw.rect(screen, user_color_1, self.button_rect, width=5, border_radius=1)
            desc_text = desc_font.render(self.desc, True, user_color_1)
            title_text = title_font.render(self.title, True, user_color_1)
        screen.blit(title_text, title_rect)
        screen.blit(desc_text, desc_rect)
        pg.draw.line(screen,user_color_1,self.button_rect.midbottom, (self.button_rect.centerx,self.button_rect.bottom+50),4)
        if self.layer != 1:
            pg.draw.line(screen,user_color_1,self.button_rect.midtop, (self.button_rect.centerx,self.button_rect.top-75),4)
            num_in_previous = len(layers[self.layer - 1])
            if index == num_in_layer - 1:
                if num_in_layer >= num_in_previous:
                    pg.draw.line(screen,user_color_1,(self.button_rect.centerx,self.button_rect.top-75),(self.button_rect.centerx-(research_buttons_width-width),self.button_rect.top-75),4)
                else:
                    pg.draw.line(screen,
                                 user_color_1,
                                 (self.button_rect.centerx + (((width+button_spacing)/2)*(num_in_previous-(index+1))), self.button_rect.top - 75),
                                 (self.button_rect.centerx - ((width * num_in_previous + button_spacing * (num_in_previous-(1+((num_in_previous-(index+1))*.5)))) - width * (1+((num_in_previous-(index+1))*.5))), self.button_rect.top - 75),
                                 4)


    def is_researchable(self):
        return all([req.used for req in self.requirements])


def home():
    global current_scene
    current_scene = "home"


def research():
    global current_scene
    current_scene = "research"


def settings():
    global current_scene
    current_scene = "settings"


def about():
    global current_scene
    current_scene = "about"


def spawn():
    global humans
    humans += 1


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
    global food
    global scholar_points
    food+=hunters*2
    scholar_points+=scholars

def color_set():
    global state
    global user_color_1
    global user_color_2
    if state == 1:
        user_color_1 = (255,255,255)
        user_color_2 = (25, 27, 29)
        state = 0
    else:
        user_color_1 = (0,0,0)
        user_color_2 = (255,255,255)
        state = 1

def research_test(id):
    global civ
    if id == "civ":
        civ = True
    if id == "guh":
        pass


def hunter_increase():
    global hunters
    global unemployed
    if unemployed > 0:
        hunters += 1

def hunter_decrease():
    global hunters
    hunters -= 1
def scholar_increase():
    global scholars
    global unemployed
    if unemployed > 0:
        scholars += 1

def scholar_decrease():
    global scholars
    scholars -= 1


home_tab = TabButton("home", home)
research_tab = TabButton("research", research)
settings_tab = TabButton("settings", settings, )
about_tab = TabButton("about", about)

spawn_button = Button("Bless with life", spawn, width=400)
hunter_increase_button = Button(">", hunter_increase, width=50,height=50 ,x=350, y=300)
hunter_decrease_button = Button("<", hunter_decrease, width=50,height=50 ,x=50, y=300)
scholar_increase_button = Button(">", scholar_increase, width=50,height=50 ,x=350, y=400)
scholar_decrease_button = Button("<", scholar_decrease, width=50,height=50 ,x=50, y=400)


civilization = ResearchButton(research_test, "Civilization", "The dawn of your society \n allows life and research",
                       "civ", 1)
layer_1 = [civilization]
testbutton2 = ResearchButton(research_test, "test of second research", "wow this is so incredibly incredible", "guh", 2,
                             requirements=[civilization])
testbutton3 = ResearchButton(research_test, "test of third research", "wow this is so incredibly incredibler", "guh", 2,
                             requirements=[civilization])
testbutton4 = ResearchButton(research_test, "test of fourth research", "wow this is so incredibly incredibler", "guh",
                             2,
                             requirements=[civilization])
layer_2 = [testbutton2, testbutton3, testbutton4]
testbutton5 = ResearchButton(research_test, "test of next layer", "if this doesnt break i will nut", "guh", 3,
                             requirements=[i for i in layer_2])

layer_3 = [testbutton5]
layers = {
    1: layer_1,
    2: layer_2,
    3: layer_3
}

theme_button = Button("switch theme", color_set,x=800,y=200, width=250)

tab_buttons = [home_tab, research_tab, settings_tab, about_tab]
home_buttons = [spawn_button, hunter_increase_button, hunter_decrease_button,scholar_increase_button,scholar_decrease_button]
research_buttons = [button for layer in [layer_1, layer_2, layer_3] for button in layer]
settings_buttons = [theme_button]
buttons_list = [tab_buttons, home_buttons, research_buttons,settings_buttons]

home()

while running:
    screen.fill(user_color_2)
    screen_width, screen_height = screen.get_size()
    mouse_x, mouse_y = pg.mouse.get_pos()
    tab_button = 0
    #event loop
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            button_clicked = True
        if event.type == pg.MOUSEBUTTONUP:
            button_clicked = False
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
        hunter_rect.center = (200, 300)
        screen.blit(hunter_text, hunter_rect)
        scholar_text = text_font.render(f'{scholars} scholars', True, user_color_1)
        scholar_rect = scholar_text.get_rect()
        scholar_rect.center = (200, 400)
        screen.blit(scholar_text, scholar_rect)

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
        about_text = text_font.render('this really pulsars my cubes', False, user_color_1)
        about_rect = about_text.get_rect()
        about_rect.center = (700, 700)
        screen.blit(about_text, about_rect)
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
                        if button.layer == 1:
                            button.draw(400, 400, 0)
                            if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                                button.draw(400, 400, 0, True)
                                if button_clicked:
                                    if button.is_researchable():
                                        button.func(button.id)
                                        button.used = True
                        elif button.layer == 2:
                            button.draw(400, 400, layer_2.index(button))
                            if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                                button.draw(400, 400, layer_2.index(button), True)
                                if button_clicked:
                                    if button.is_researchable():
                                        button.func(button.id)
                                        button.used = True
                        elif button.layer == 3:
                            button.draw(400, 400, layer_3.index(button))
                            if pg.Rect.collidepoint(button.button_rect, mouse_x, mouse_y):
                                button.draw(400, 400, layer_3.index(button), True)
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
    unemployed = humans - hunters - scholars
    pg.display.update()
    frame += 1
    if frame == 60:
        breed()
        seconds += 1
        if seconds % 5 == 0:
            work()
            eat()
        work()
        frame = 0
    clock.tick(60)
pg.quit()
