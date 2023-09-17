import kivy
import random

from kivy.app import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from random import randint
from kivy.config import Config
from kivy.graphics import *
from kivy.core.window import *

linhas = 10

lista_bombas = list()
active_btn_dict = dict()
lista_pos = list()
btn_dict = dict()
btn_list = list()
flag_list = list()


class RootWidget(GridLayout):
    def __init__(self):
        super().__init__()
        self.size = Window.size
        self.rows = self.cols = 1


root = RootWidget()


class MyApp(App):
    game_layout = FloatLayout(size_hint=(None, None))
    root.add_widget(game_layout)
    is_resize = False
    botao_mouse = ""
    maior_lado = 0
    revealing = False
    cont_flags = 0
    to_reveal = list()

    ganhou = Label(size_hint=(None, None), text="Você venceu", size=(0, 0))

    perdeu = Label(size_hint=(None, None), text="Você perdeu", size=(0, 0))

    def build(self):
        if kivy.utils.platform in ("win", "macosx", "linux"):
            Config.set('input', 'mouse', 'mouse,disable_multitouch')
            self.plataforma = "not_touch"
        else:
            self.plataforma = "touch"

        if Window.width > Window.height:
            self.game_layout.size = (Window.height * 85 / 100, Window.height * 85 / 100)
            self.maior_lado = Window.width

        elif Window.height > Window.width:
            self.game_layout.size = (Window.width * 85 / 100, Window.width * 85 / 100)
            self.maior_lado = Window.height

        self.game_layout.pos = ((Window.width / 2) - self.game_layout.width / 2,
                                Window.height / 2 - self.game_layout.height / 2)

        self.create_lista_bombas()
        self.build_buttons()
        self.print_bombs_label()
        for button in btn_dict.keys():
            btn_list.append(button)
        self.draw_action_buttons()

        Window.bind(on_resize=self.on_resize)

        self.rect = Rectangle(pos=self.game_layout.pos, size=self.game_layout.size)
        self.color = Color(215 / 255, 171 / 255, 52 / 255, 0.93)

        self.game_layout.canvas.before.add(self.color)
        self.game_layout.canvas.before.add(self.rect)

        return root

    def on_resize(self, *args):

        if Window.width > Window.height:
            self.game_layout.size = (Window.height * 85 / 100, Window.height * 85 / 100)
            self.maior_lado = Window.width
        elif Window.height > Window.width:
            self.game_layout.size = (Window.width * 85 / 100, Window.width * 85 / 100)
            self.maior_lado = Window.height
        self.game_layout.pos = ((Window.width / 2) - self.game_layout.width / 2,
                                Window.height / 2 - self.game_layout.height / 2)

        self.game_layout.canvas.before.remove(self.rect)

        self.rect = Rectangle(pos=self.game_layout.pos, size=self.game_layout.size)

        self.game_layout.canvas.before.add(self.rect)

        self.is_resize = True
        self.build_buttons()
        self.draw_action_buttons()
        self.print_bombs_label()

    def touch_down(self, inst, touch):
        if self.plataforma == "not_touch":
            self.botao_mouse = touch.button

    def print_bandeira(self, botao):

        if botao in flag_list:
            self.cont_flags -= 1
            flag_list.remove(botao)
            botao.text = " "
        elif botao not in flag_list:
            flag_list.append(botao)
            botao.color = (0, 0, 0, 1)
            self.cont_flags += 1
            botao.text = "🏴"

    def create_lista_bombas(self):
        while len(lista_bombas) < linhas * 1.25:
            bomba_pos = [randint(1, linhas), randint(1, linhas)]

            if bomba_pos not in lista_bombas:
                lista_bombas.append(bomba_pos)
            else:
                continue

    def is_bomb(self, btn):
        pos = btn_dict.get(btn)
        if pos in lista_bombas:
            return True
        else:
            return False

    def analisar_arredores(self, btn):
        btn_pos = btn_dict.get(btn)

        n_bombas = 0

        btn_x = btn_pos[0]
        btn_y = btn_pos[1]
        global lista_arredores
        lista_arredores = [[btn_x - 1, btn_y - 1],
                           [btn_x - 1, btn_y],
                           [btn_x - 1, btn_y + 1],
                           [btn_x, btn_y - 1],
                           [btn_x, btn_y + 1],
                           [btn_x + 1, btn_y - 1],
                           [btn_x + 1, btn_y],
                           [btn_x + 1, btn_y + 1]]

        for pos in lista_arredores:
            for button in btn_dict.keys():
                if btn_dict[button] == pos:
                    if self.is_bomb(button):
                        n_bombas += 1

        if n_bombas == 0:
            n_bombas = " "

        if self.is_bomb(btn):
            btn.text = "💣"
        else:
            btn.text = f"{n_bombas}"

        return btn.text

    def print_bombs_label(self):

        try:
            self.game_layout.remove_widget(self.label)
        except:
            pass

        self.label = Label(size_hint=(None, None),
                           text=f"{len(lista_bombas) - self.cont_flags} bombas restantes",
                           font_size=15 * self.game_layout.width / 500)

        self.label.size = (0, 0)

        if Window.width == self.maior_lado:
            self.label.pos = (Window.width / 2,
                              (Window.height / 2 - self.game_layout.height / 2) / 2)
        elif Window.height == self.maior_lado:
            self.label.pos = (Window.width / 2 + self.game_layout.width / 4,
                              (Window.height / 2 - self.game_layout.width / 2) / 2)

        self.game_layout.add_widget(self.label)

    def reveal_surroundings(self, btn):

        if btn.text == " ":
            for pos in lista_arredores:
                for button in btn_dict.keys():
                    if btn_dict[button] == pos:
                        self.to_reveal.append(button)

            for button in self.to_reveal:
                if self.analisar_arredores(button) == " ":
                    for pos in lista_arredores:
                        for botao in btn_dict.keys():
                            if btn_dict[botao] == pos:
                                if botao not in self.to_reveal:
                                    self.to_reveal.append(botao)

            self.revealing = True

            for button in self.to_reveal:
                self.on_touch_sweep(button)

            self.revealing = False

    def on_touch(self, botao):

        if botao == self.sweep_button:
            self.sweep_button.disabled = True
            self.flag_button.disabled = False
            for button in btn_dict.keys():
                button.unbind(on_press=self.on_touch)
                button.unbind(on_press=self.on_touch_flag)
                button.bind(on_press=self.on_touch_sweep)

        elif botao == self.flag_button:
            self.flag_button.disabled = True
            self.sweep_button.disabled = False
            for button in btn_dict.keys():
                button.unbind(on_press=self.on_touch)
                button.unbind(on_press=self.on_touch_sweep)
                button.bind(on_press=self.on_touch_flag)

        else:

            if self.botao_mouse == "left" or self.plataforma == "touch":
                botao.unbind(on_press=self.on_touch_flag)
                self.on_touch_sweep(botao)

            if self.botao_mouse == "right":
                botao.unbind(on_press=self.on_touch_sweep)
                self.on_touch_flag(botao)

    def on_touch_sweep(self, botao):
        if self.botao_mouse == "left" or self.plataforma == "touch":

            if botao.text == "🏴":
                self.cont_flags -= 1
                flag_list.remove(botao)
            elif botao in flag_list:
                self.cont_flags -= 1
                flag_list.remove(botao)
            if botao in active_btn_dict:
                active_btn_dict.pop(botao)
                self.analisar_arredores(botao)

            if not self.revealing:
                self.reveal_surroundings(botao)
            botao.disabled = True
            self.print_bombs_label()
            self.game_over(botao)


        elif self.botao_mouse == "right":
            self.on_touch_flag(botao)

    def on_touch_flag(self, botao):
        self.print_bandeira(botao)
        self.print_bombs_label()

    def build_buttons(self):
        cont = 0
        cont_pos_y = self.game_layout.pos[1]
        for pos_x in range(1, linhas + 1):
            cont_pos_x = self.game_layout.pos[0]
            for pos_y in range(1, linhas + 1):
                global btn
                if self.is_resize:
                    btn = btn_list[cont]
                    btn.pos = (cont_pos_x, cont_pos_y)
                    btn.font_size = (self.game_layout.width * 35 / 600)

                elif not self.is_resize:
                    btn = Button(on_press=self.on_touch,
                                 on_touch_down=self.touch_down,
                                 pos=(cont_pos_x, cont_pos_y),
                                 size_hint=(1 / linhas, 1 / linhas),
                                 font_size=self.game_layout.width * 35 / 600,
                                 text=" ",
                                 font_name = "NotoEmoji-VariableFont_wght",
                                 disabled_color=(0, 0, 0, 1))
                    pos = [pos_x, pos_y]
                    lista_pos.append(pos)
                    btn_dict[btn] = pos
                    active_btn_dict[btn] = pos
                    self.game_layout.add_widget(btn)

                cont_pos_x += self.game_layout.width / linhas
                cont += 1
            cont_pos_y += self.game_layout.height / linhas

    def draw_action_buttons(self):

        if not self.is_resize:
            self.sweep_button = Button()
            self.flag_button = Button()
            self.game_layout.add_widget(self.sweep_button)
            self.game_layout.add_widget(self.flag_button)

        self.sweep_button.text = "💣"
        self.sweep_button.size = ((self.game_layout.width / linhas), (self.game_layout.width / linhas))
        self.sweep_button.size_hint = (None, None)
        self.sweep_button.font_size = self.game_layout.width * 35 / 600
        self.sweep_button.font_name = btn.font_name
        self.sweep_button.color = (0, 0, 0, 1)
        self.sweep_button.disabled_color = (0, 0, 0, 1)

        self.flag_button.text = "🏴"
        self.flag_button.size = self.sweep_button.size
        self.flag_button.size_hint = self.sweep_button.size_hint
        self.flag_button.font_size = self.sweep_button.font_size
        self.flag_button.font_name = btn.font_name
        self.flag_button.color = (0, 0, 0, 1)
        self.flag_button.disabled_color = (0, 0, 0, 1)

        if Window.width == self.maior_lado:
            self.sweep_button.pos = (Window.width / 2 + self.game_layout.width / 2 +
                                     (Window.width - self.game_layout.width) / 4 - self.sweep_button.width / 2,
                                     Window.height / 2)

            self.flag_button.pos = (Window.width / 2 + self.game_layout.width / 2 +
                                    (Window.width - self.game_layout.width) / 4 - self.flag_button.width / 2,
                                    Window.height / 2 - self.game_layout.height / linhas)

        elif Window.height == self.maior_lado:
            self.sweep_button.pos = (Window.width / 2 - self.game_layout.width / linhas,
                                     Window.height / 2 - self.game_layout.height / 2 -
                                     (Window.height - self.game_layout.height) / 4 -
                                     self.sweep_button.height / 2)
            self.flag_button.pos = (Window.width / 2, Window.height / 2 - self.game_layout.height / 2 -
                                    (Window.height - self.game_layout.height) / 4 -
                                    self.sweep_button.height / 2)

        self.sweep_button.bind(on_press=self.on_touch)
        self.flag_button.bind(on_press=self.on_touch)

        self.sweep_button.disabled = True
        self.flag_button.disabled = False

    def game_over(self, btn):
        btn.disabled = True

        if self.is_bomb(btn):
            for button in btn_dict.keys():
                self.analisar_arredores(button)
                button.disabled = True

            self.perdeu.pos = self.label.pos
            self.game_layout.remove_widget(self.label)
            self.game_layout.add_widget(self.perdeu)

        else:
            button_counter = 0
            for button in active_btn_dict.keys():
                if self.is_bomb(button):
                    button_counter += 1

            if button_counter == len(active_btn_dict):
                for button in btn_dict.keys():
                    self.analisar_arredores(button)
                    button.disabled = True

                self.ganhou.pos = self.label.pos
                self.game_layout.remove_widget(self.label)
                self.game_layout.add_widget(self.ganhou)
            else:
                pass


if __name__ == "__main__":
    MyApp().run()