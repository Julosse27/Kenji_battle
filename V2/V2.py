# title: Kenji Battle
# author: Lateurte Jules et Fauchereau Evan
# desc: Un petit jeu d'enfants de 15 ans qui commencent tout juste à programmer
# version: 2

import pyxel as px
from collections import defaultdict
import sqlite3
from os import path
from typing import Literal, Final
from random import randint

Ressources = path.abspath(r"Ressources\Kenji_battle_ressources.pyxres")
Données = path.abspath(r"Ressources\Données.sq3")

lettres = (
           ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"),
           ("a", "b", "c", "d", "e", "f", "h", "i", "k", "l", "m", "n", "o", "r", "s", "t", "u", "v", "w", "x", "z"),
           ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "),
           ("é", "è", "à", "ê", "ù", "-", "'", ".", "!", "?", ":", "_", "(", ")", "%", "="),
           ("g", "j", "p", "q", "y", ",", "ç", ";"),
           ("/")
           )

touches = ( (px.KEY_A, "a"), (px.KEY_Z, "z"), (px.KEY_E, "e"), (px.KEY_R, "r"), (px.KEY_T, "t"), (px.KEY_Y, "y"),
            (px.KEY_U, "u"), (px.KEY_I, "i"), (px.KEY_O, "o"), (px.KEY_P, "p"), (px.KEY_Q, "q"), (px.KEY_S, "s"),
            (px.KEY_D, "d"), (px.KEY_F, "f"), (px.KEY_G, "g"), (px.KEY_H, "h"), (px.KEY_J, "j"), (px.KEY_K, "k"),
            (px.KEY_L, "l"), (px.KEY_M, "m"), (px.KEY_W, "w"), (px.KEY_X, "x"), (px.KEY_C, "c"), (px.KEY_V, "v"),
            (px.KEY_B, "b"), (px.KEY_N, "n"), (px.KEY_SPACE, " "), (px.KEY_RIGHTBRACKET, ")"), (px.KEY_COLON, ":"), 
            (px.KEY_1, "1"), (px.KEY_3, "3"))

touches_spé =  ((px.KEY_2, "2", "é"), (px.KEY_4, "4", "'"), (px.KEY_5, "5", "("), (px.KEY_6, "6", "-"),
                (px.KEY_7, "7", "è"), (px.KEY_8, "8", "_"), (px.KEY_9, "9", "ç"), (px.KEY_0, "0", "à"),
                (px.KEY_COMMA, "?", ","), (px.KEY_SEMICOLON, ".", ";")
                )

touches_keypad = ((px.KEY_KP_0, "0"), (px.KEY_KP_1, "1"), (px.KEY_KP_2, "2"), (px.KEY_KP_3, "3"), (px.KEY_KP_4, "4"), (px.KEY_KP_5, "5"), (px.KEY_KP_6, "6"),
                (px.KEY_KP_7, "7"), (px.KEY_KP_8, "8"), (px.KEY_KP_9, "9"))

def ajouter_texte(x: float, y: float, taille: float, txt: str, couleur, gr_elements: str, type_retour: Literal["Normal", "Millieu", "Inversé"] = "Normal"):
    global elements
    elements[gr_elements]["texte"].append(Draw_texte(x, y, taille, txt, couleur, type_retour, len(elements[gr_elements]["texte"])))

def ajouter_bouton(x: int, y: int, width: int, height: int, gr_elements: str, fonction, *paramètres_fonction, modèle = False, coolkey = 15, taille = 1, x_img: int = None, y_img: int = None, x_img_a: int = None, y_img_a: int = None, couleur1 = None, couleur2 = None, bordure: int = 1): #type: ignore
    global elements
    if not (type(fonction) != type(ajouter_bouton) or type(fonction) != type(def_pseudo.chek_touches)):
        raise Exception("L'action demandée n'est pas executable.")
    if modèle:
        if not (x_img or y_img or x_img_a or y_img_a):
            raise ValueError("Les coordonées de l'images doivent être préscisées.")
    else:
        if not (couleur1 or couleur2):
            raise ValueError("Les couleurs doivent être préscisées.")
    bouton = Bouton(x, y, width, height, fonction, paramètres_fonction, taille, x_img, y_img, x_img_a, y_img_a, coolkey, modèle, (couleur1, couleur2), bordure)
    elements[gr_elements]["boutons"].append(bouton)
    return bouton

def update_elements(gr_elements, *type_elements):
    if not len(type_elements) == 0:
        for type_element in type_elements:
            for element in elements[gr_elements][type_element]:
                element.update()

def draw_elements(gr_elements, *type_elements):
    if not len(type_elements) == 0:
        for type_element in type_elements:
            for element in elements[gr_elements][type_element]:
                if gr_elements == "Shop" and type_element == "boutons" and elements["Shop"]["boutons"].index(element) == len(elements["Shop"]["boutons"]) - 1:
                    px.rect(0, 64, px.width, 16, 9)
                    px.rect(0, 32, px.width, 16, 9)
                    px.rect(0, 48, px.width, 16, 10)
                element.draw()

class Perso:
    def __init__(self, vies):
        self.height: Final = 32
        self.width: Final = 32
        
        self.x = px.width / 2
        self.x_draw = self.x + (self.width / 4)
        self.y_draw = px.height - (self.height * 0.75)
        self.hitbox = (self.x, self.x + self.width)

        self.vies = vies

        self._img_b: Final = ((0, 0), (16, 0))
        self._img_m: Final = ((32, 0), (48, 0))
        self._img_att: Final = (64, 0)
        self._x_d_att:Final = (-24, 8)
        self._x_att:Final = (-32, 0)
        self._imgs_ch: Final = ((96, 0), (96, 16), (128, 0), (208, 48))
        self._delay_ch: Final = (base_stats["Delay 1ere charge"], base_stats["Delay 2eme charge"], base_stats["Delay 3eme charge"])
        self.stade_ch = 0
        self._img_ult: Final = ((224, 0), (224, 48), (192, 32))
        self._img_mort: Final = (96, 48)

        self.mouvement = 0
        self.sens = 1

        self.invincibiltee = 240

        self.charge_att = 0
        self.dur_att = 0
        self.reload_t = 0
        self.ult = False

    def slash(self):
        pass

    def touché(self, dmg: int):
        """
        Déclenche l'animation de degat du perso et lui enlève autant de vie que les `dmg` données.
        """
        self.vies -= dmg
        if self.vies <= 0:
            jeu.game_over()
            return
        self.invincibiltee += 120

    def update(self):
        """
        Les vérifications de l'état du personnage chaque frame du jeu.
        """
        self.mouvement = 0
        if px.btn(px.KEY_DOWN) and self.reload_t == 0:
            self.charge_att += 1
        else:
            if self.charge_att != 0:
                if self.stade_ch != 0:
                    self.dur_att = 30
                    if self.stade_ch == 3:
                        self.slash()
                self.reload_t = base_stats["Reload att"]
                self.charge_att = 0
            if self.dur_att == 0:
                self.stade_ch = 0

            if self.reload_t != 0:
                self.reload_t -= 1
            if self.dur_att != 0:
                self.dur_att -= 1

        if self.charge_att != 0:
            for i in range(len(self._delay_ch) - 1, -1, -1):
                if i != 2:
                    if self.charge_att > self._delay_ch[i]:
                        self.stade_ch = i + 1
                        break
            else:
                self.stade_ch = 0
        elif self.dur_att != 0:
            pass
        elif px.btn(px.KEY_LEFT):
            self.mouvement = - base_stats["Vitesse"]
            self.sens = -1
        elif px.btn(px.KEY_RIGHT):
            self.mouvement = base_stats["Vitesse"]
            self.sens = 1

        if self.x + self.width + self.mouvement > px.width or self.x + self.mouvement < 0:
            self.mouvement = 0

        if self.invincibiltee != 0:
            self.invincibiltee -= 1

        self.x: float = self.x + self.mouvement
        self.x_draw += self.mouvement
        self.hitbox = (self.x, self.x + self.width)
    
    def idle(self, imgs):
        r"""
        Prédéfinition de l'animation du type idle.

        /!\A éxecuter chaque frame pour fonctionner correctement/!\ .
        """
        if px.frame_count % 60 > 30:
            px.blt(self.x_draw, self.y_draw, 0, imgs[0][0], imgs[0][1], self.sens * 16, 16, 12, scale= 2)
        else:
            px.blt(self.x_draw, self.y_draw, 0, imgs[1][0], imgs[1][1], self.sens * 16, 16, 12, scale= 2)

    def draw(self):
        """
        Le dessin du personnage uniquement à chaque frame du jeu.
        """
        if self.invincibiltee % 30 < 15 or self.invincibiltee == 0:
            if self.charge_att != 0:            
                px.blt(self.x_draw, self.y_draw, 0, self._imgs_ch[self.stade_ch][0], self._imgs_ch[self.stade_ch][1], self.sens * (self.width / 2), self.height / 2, 12, scale= 2)
            elif self.dur_att != 0:
                px.blt(self.x_draw + self._x_d_att[0 if self.sens == -1 else 1], self.y_draw, 0, self._img_att[0], self._img_att[1], 32 * self.sens, 16, 12, scale= 2)   
            elif self.mouvement == 0:
                self.idle(self._img_b)
            else:
                self.idle(self._img_m)

class Bouton:
    def __init__(self, x: int, y: int, taille_w: int, taille_h: int, fonction, paramètres: tuple, taille: int, x_img, y_img, x_img_a, y_img_a, couleur_transparence, modèle, couleur, bordure):
        self.x = x
        self.y = y
        self.width = taille_w
        self.height = taille_h
        self.fonction = fonction
        self.paramètres = paramètres
        self.modèle = modèle
        self.exclu = False
        self.taille = taille
        if modèle:
            self.x_img = x_img
            self.y_img = y_img
            self.x_img_a = x_img_a
            self.y_img_a = y_img_a
        else:
            global couleurs
            for i in range(len(couleur)):
                if couleur[i] > len(couleurs):
                    if couleur[i] not in couleurs:
                        couleurs.append(couleur[i])
                    couleur[i] = couleurs.index(couleur[i])
            self.couleur1 = couleur[0]
            self.couleur2 = couleur[1]
            self.bordure = bordure
        
        if couleur_transparence > len(couleurs):
            couleur_transparence = couleurs.index(couleur_transparence)
        self.coolkey = couleur_transparence
        self.animation = False

    def exclusion(self, valeur: bool = True):
        self.exclu = valeur

    def change_position(self, x: float = None, y: float = None): #type: ignore
        """
        Change la position du bouton jusqu'au prochain changement ou à jamais.

        Parameters
        -----------
        x: optionel[:class:`float`]
            Le nouveau placement sur l'axe x.
        y: optionel[:class:`float`]
            Le nouveau placement dur l'axe y.
        """
        if x != None:
            self.x = x
        if y != None:
            self.y = y

    def update(self):
        self.animation = False
        mx = px.mouse_x
        my = px.mouse_y
        
        x1 = self.x - ((self.width / 2) * (self.taille - 1))
        x2 = self.x + self.width + ((self.width / 2) * (self.taille - 1))
        y1 = self.y - ((self.height / 2) * (self.taille - 1))
        y2 = self.y + self.height + ((self.height / 2) * (self.taille - 1))
        if not self.exclu:
            if (mx >= x1 and mx <= x2) and (my >= y1 and my <= y2):
                self.animation = True
                if px.btnp(px.MOUSE_BUTTON_LEFT):
                    if len(self.paramètres) == 0:
                        self.fonction()
                    else:
                        self.fonction(*self.paramètres)
    
    def draw(self):
        if not self.exclu:
            if self.modèle:
                if self.animation and px.frame_count % 40 < 20:
                    px.blt(self.x, self.y, 0, self.x_img_a, self.y_img_a, self.width, self.height, self.coolkey, scale= self.taille)
                else:
                    px.blt(self.x, self.y, 0, self.x_img, self.y_img, self.width, self.height, self.coolkey, scale= self.taille)
            else:
                px.rect(self.x, self.y, self.width, self.height, self.couleur2)
                if self.animation and px.frame_count % 40 < 20:
                    px.rect(self.x + (self.bordure * 2), self.y + (self.bordure * 2), self.width - (3 * self.bordure), self.height - (3 * self.bordure), self.couleur1)
                else:
                    px.rect(self.x + self.bordure, self.y + self.bordure, self.width - (2* self.bordure), self.height - (2* self.bordure), self.couleur1)
            
class Draw_texte:
    class Retour:
        def __init__(self, x, y, taille, texte, couleur, y_img, decallage):
            self.x = x
            self.y = y
            self.taille = taille
            self.couleur = couleur
            self.y_img = y_img
            self.decallage = decallage
            self.positions = []
            for caractère in texte:
                for u in range(len(lettres)):
                    for i in range(len(lettres[u])):
                        if caractère == lettres[u][i]:
                            if u != 5:
                                self.positions.append((i, u))

            self.taille_x = 8 * len(self.positions)

        def draw(self):
            for o in range(len(self.positions)):
                px.tilemaps[7].pset(o + self.decallage, 0 + self.y_img, self.positions[o])
                if self.positions[o][1] == 4:
                    px.tilemaps[7].pset(o + self.decallage, 1 + self.y_img, (self.positions[o][0], self.positions[o][1] + 1))
                else:
                    px.tilemaps[7].pset(o + self.decallage, 1 + self.y_img, (10, 2))
            
            px.bltm(self.x, self.y, 7, 8 * self.decallage, 8 * self.y_img, self.taille_x, 16, 0, scale = self.taille)

    def __init__(self, x, y, taille, texte, couleur, type_retour: Literal["Normal", "Millieu", "Inversé"], index):
        self.x = x
        self.y = y
        self.x_base = x
        self.taille = taille
        self.change_couleur(couleur)
        self.type_retour = type_retour
        self.index = index
        self.change_texte(texte)

    def change_couleur(self, couleur):
        global couleurs
        if couleur > len(couleurs):
            if couleur not in couleurs:
                couleurs.append(couleur)
                px.colors.from_list(couleurs)
            self.couleur = couleurs.index(couleur)
        else:
            self.couleur = couleur
        
    def change_texte(self, nouveau_txt):
        if self.type_retour == "Normal":
            self.x = self.x_base + 4 * len(nouveau_txt) * (self.taille - 1)
        else:
            self.x = self.x_base
        nouveau_txt = list(nouveau_txt)
        txt = []
        self.txts_retours = []
        if "/" in nouveau_txt:
            for i in range(len(nouveau_txt)):
                if "/" == nouveau_txt[i]:
                    txt.append(i)
            txt.append(len(nouveau_txt))

        if self.type_retour == "Millieu":
            if len(txt) > 0:
                self.x -= ((txt[0] * 8) / 2)
            else:
                self.x -= ((len(nouveau_txt) * 8) / 2)

        if not len(txt) == 0:
            for u in range(len(txt)):
                if u == 0:
                    txt_base = nouveau_txt[:txt[u]]
                else:
                    if self.type_retour == "Normal":
                        x_retour = self.x_base
                    elif self.type_retour == "Millieu":
                        x_retour = self.x + ((txt[0] * 8) / 2) - (((txt[u] - txt[u - 1]) * 8) / 2)
                    elif self.type_retour == "Inversé":
                        x_retour = self.x_base - (txt[u] * 8)

                    self.txts_retours.append(self.Retour(x_retour, self.y + (16 * u), self.taille, nouveau_txt[txt[u - 1] + 1:txt[u]], self.couleur, 2 * self.index, txt[u - 1]))

            nouveau_txt = txt_base
        
        if self.type_retour == "Inversé":
            self.x = self.x_base - (len(nouveau_txt) * 8)

        positions = []
        for caractère in nouveau_txt:
            for u in range(len(lettres)):
                for i in range(len(lettres[u])):
                    if caractère == lettres[u][i]:
                        if u != 5:
                            positions.append((i, u))
        
        self.taille_x = 8 * len(positions)
        self.positions = positions
        
    def draw(self):
        for o in range(len(self.positions)):
            px.tilemaps[7].pset(o, 0 + (2 * self.index), self.positions[o])
            if self.positions[o][1] == 4:
                px.tilemaps[7].pset(o, 1 + (2 * self.index), (self.positions[o][0], self.positions[o][1] + 1))
            else:
                px.tilemaps[7].pset(o, 1 + (2 * self.index), (10, 2))

        px.pal(7, self.couleur)

        for retour in self.txts_retours:
            retour.draw()
        
        px.bltm(self.x, self.y, 7, 0, 16 * self.index, self.taille_x, 16, 0, scale = self.taille)

        px.pal()

class Def_pseudo:
    def __init__(self, changement_p = False):
        global elements
        elements = defaultdict(lambda: {"boutons": [], "texte": []})
        self.pseudo = ""
        self.ch_p = changement_p
        self.majuscule = True
        self.gr_element = "def_pseudo"

        self.couleur_txt = 0xEEEEEE
        self.x_txt = 197
        self.y_txt = 139

        if not new:
            self.pseudo = Base_données.recup_last_pseudo() #type: ignore
            self.choisi = True
        else:
            self.choisi = False

        if changement_p:
            self.choisi = False
            self.pseudo = ""

        ajouter_texte(256, 100, 1, "Choisit ton/pseudo !", self.couleur_txt, self.gr_element, "Millieu")
        ajouter_texte(self.x_txt, self.y_txt, 1, self.pseudo, self.couleur_txt, self.gr_element)

        self.limite_taille_pseudo: Final = 15
        
        self.couleur_txt = couleurs.index(self.couleur_txt)

    def chek_touches(self):
        écrit = False
        if len(self.pseudo) < self.limite_taille_pseudo:
            for code, lettre in touches:
                if not écrit:
                    if px.btnp(code, hold= 30, repeat= 3):
                        if self.majuscule:
                            lettre = lettre.upper()
                        self.pseudo += lettre
                    if px.btn(code):
                        écrit = True

            for code, majuscule, minuscule in touches_spé:
                if not écrit:
                    if px.btnp(code, hold= 30, repeat= 3):
                        if self.majuscule:
                            self.pseudo += majuscule
                        else:
                            self.pseudo += minuscule
                    if px.btn(code):
                        écrit = True

            for code, lettre in touches_keypad:
                if not écrit:
                    if px.btnp(code, hold= 30, repeat= 3):
                        self.pseudo += lettre
                    if px.btn(code):
                        écrit = True

        if px.btnp(px.KEY_RSHIFT) or px.btnp(px.KEY_LSHIFT):
            if self.majuscule:
                self.majuscule = False
            else:
                self.majuscule = True

        if not écrit:
            if px.btnp(px.KEY_BACKSPACE, hold = 30, repeat= 3):
                self.pseudo = self.pseudo[:-1]
                écrit = True

        if not écrit:
            if px.btnp(px.KEY_RETURN) or px.btnp(px.KEY_RETURN2) or px.btnp(px.KEY_KP_ENTER):
                self.choisi = True
                init(self.pseudo)
        else:
            elements[self.gr_element]["texte"][1].change_texte(self.pseudo.replace(" ", "$"))        

    def draw(self):
        yL1 = -32
        yL2 = -16
        while yL1 <= px.height:
            yL1 += 32
            yL2 += 32
            px.rect(0, yL1, px.width, 16, 9)
            px.rect(0, yL2, px.width, 16, 10)

        px.blt(px.width / 2 - 32, px.height / 2 - 16, 0, 64, 128, 64, 32, scale= 2)

        draw_elements(self.gr_element, "texte")
        if px.frame_count % 30 < 15:
            px.line(self.x_txt + (8 * len(self.pseudo)), self.y_txt, self.x_txt + (8 * len(self.pseudo)), self.y_txt + 8, self.couleur_txt)

class Kunai:
    def __init__(self, cible: Literal["joueur", "ennemis"], x_base: int | float, y_base: int | float, sens: Literal[1, -1], width: int = 16, height: int = 16):
        self._POT_CIBLE = ["joueur", "ennemis"]
        self.cible = cible
        self.x = x_base
        self.y = y_base
        self.sens = sens

class Ennemi:
    """
    La dedans c'est un ennemis et comment tout est géré.

    Paramètre
    --------------------------------------------------
    type_ennemi: `Literal["distance", "sabre", "assasin", "lanceur", "tank"]`\n
        Quel ennemi c'est.
    """
    def __init__(self, type_ennemi: Literal["distance", "sabre", "assasin", "lanceur", "tank"]):
        self._UP = {"distance": self.distance_up, "sabre": self.sabre_up, "assasin": self.assasin_up, "lanceur": self.lanceur_up, "tank": self.tank_up}
        self._SETUP = {"distance": self.distance_setup, "sabre": self.sabre_setup, "assasin": self.assasin_setup, "lanceur": self.lanceur_setup, "tank": self.tank_setup}

        self.update: Final = self._UP[type_ennemi]
        self._SETUP[type_ennemi]()

        self.type_e: str = type_ennemi

    def mort(self):
        for nom, infos in jeu.ennemis:
            if nom == self.type_e:
                infos["stock"].remove(self)

    def touche(self):
        self.touches -= 1
        if self.touches <= 0:
            self.mort()

    def touché(self, dmg):
        self.vies -= dmg
        if self.vies <= 0:
            self.mort()
            return True
        return False

    def setup_b(self):
        self.vies = 1
        self.att = 1
        self.touches = 1

        self.height = 32
        self.width = 32

        self.x = 0 if randint(0, 1) else px.width - self.width
        self.x_draw = self.x + 8
        self.y_draw = px.height - self.width * 0.75

        self.hitbox = (self.x, self.x + self.width)
        self.sens = 1

    def deplacement_b(self):
        emp_j = jeu.perso.x + jeu.perso.width / 2
        if emp_j > self.x + self.width / 2:
            self.mouvement = self.vitesse
            self.sens = 1
        elif emp_j == self.x + self.width / 2:
            self.mouvement = 0
        else:
            self.mouvement = - self.vitesse
            self.sens = -1

        if self.x + self.width + self.mouvement >= px.width or self.x + self.mouvement <= 0:
            self.mouvement = 0

        return emp_j

    def distance_setup(self):
        """
        Les variables de base necessaire à ce type d'ennemi
        """
        self.setup_b()

        self.recompense = 200
        self.reload_kunai = 200
        self.att_kunai = 1
        self.kunais = self.Kunai()
        self.vitesse = 0.5 * base_stats["Vitesse"]
        self.distance_j = 100
        self.anim_b = ((0, 16), (16, 16))

    def distance_up(self):
        """
        Les modification apportées à l'ennemi chaque frame.
        """
        emp_j = self.deplacement_b()

        if not (self.x + self.width + (- self.mouvement) >= px.width or self.x + (- self.mouvement) <= 0):
            if abs(self.x + self.width / 2 - emp_j) == self.distance_j:
                self.mouvement = 0
            elif abs(self.x + self.width / 2 - emp_j) < self.distance_j:
                self.mouvement = - self.mouvement
        
        self.x += self.mouvement
        self.x_draw += self.mouvement
        self.hitbox = (self.x, self.x + self.width)

    def sabre_setup(self):
        """
        Les variables de base necessaire à ce type d'ennemi
        """
        self.setup_b()
        self.recompense = 300
        self.touches = 2
        self.vitesse = 0.7 * base_stats["Vitesse"]
        self.anim_b = ((32, 16), (48, 16))

    def sabre_up(self):
        """
        Les modification apportées à l'ennemi chaque frame.
        """
        self.deplacement_b()

        self.x += self.mouvement
        self.x_draw += self.mouvement
        self.hitbox = (self.x, self.x + self.width)

    def assasin_setup(self):
        """
        Les variables de base necessaire à ce type d'ennemi
        """
        pass

    def assasin_up(self):
        """
        Les modification apportées à l'ennemi chaque frame.
        """
        pass

    def lanceur_setup(self):
        """
        Les variables de base necessaire à ce type d'ennemi
        """
        pass

    def lanceur_up(self):
        """
        Les modification apportées à l'ennemi chaque frame.
        """
        pass

    def tank_setup(self):
        """
        Les variables de base necessaire à ce type d'ennemi
        """
        pass

    def tank_up(self):
        """
        Les modification apportées à l'ennemi chaque frame.
        """
        pass

    def draw(self):
        phase = 0 if px.frame_count % 60 < 30 else 1
        px.blt(self.x_draw, self.y_draw, 0, self.anim_b[phase][0], self.anim_b[phase][1], self.width / 2 * self.sens, self.height / 2, 12, scale= 2)

    class Kunai:
        def __init_subclass__(cls):
            pass

class Jeu:
    def __init__(self):
        self.perso = Perso(difficultées[paramètres["Difficultée"]]["vies"])
        self.ennemis = list[tuple[Literal["distance", 'sabre', "assasin", "lanceur", "tank"], dict()]()]()
        for ennemi in ("distance", 'sabre', "assasin", "lanceur", "tank"):
            if difficultées[paramètres["Difficultée"]]["ennemis"][ennemi]["nb_max"] != 0:
                self.ennemis.append((
                ennemi,
                {
                    "nb_max": difficultées[paramètres["Difficultée"]]["ennemis"][ennemi]["nb_max"],
                    "t_spawn": difficultées[paramètres["Difficultée"]]["ennemis"][ennemi]["respawn"],
                    "stock": list[Ennemi](),
                    "delay_spawn": 0
                }
                ))
        
        self.score = 0

        elements["Jeu"]["texte"][0].change_texte("Score: 0")
        elements["Jeu"]["texte"][1].change_texte(pseudo)

    def recompense(self, score: int):
        self.score += score
        elements["Jeu"]["texte"][0].change_texte(f"Score: {self.score}")

    def spawn(self):
        """
        Fonction qui vérifie a chaque frame si un ennemi doit spawner.
        """
        for nom, infos in self.ennemis:
            if len(infos["stock"]) != infos["nb_max"]:
                infos["delay_spawn"] += 1 #incrementation du timer propre à chaque type

            if infos["delay_spawn"] == infos["t_spawn"]: #vérification si celui ci doit spawner
                infos["stock"].append(Ennemi(nom))          
                infos["delay_spawn"] = 0

    def colisions(self):
        """
        Fonction qui vérifie à chaque frame les colisions entre le personnage et les ennemis.
        """
        hitbox_j = self.perso.hitbox
        x_att = self.perso.x + self.perso._x_att[0 if self.perso.sens == -1 else 1]

        for nom, infos in self.ennemis:
            ennemis = infos["stock"]
            for ennemi in ennemis:
                hitbox_e = ennemi.hitbox
                if self.perso.dur_att != 0:
                    if x_att < hitbox_e[1] and x_att + self.perso.width * 2 > hitbox_e [0]:
                        if ennemi.touché(self.perso.stade_ch if self.perso.stade_ch != 3 else 2):
                            self.recompense(ennemi.recompense)
                if hitbox_j[0] < hitbox_e[1] and hitbox_j[1] > hitbox_e[0] and self.perso.invincibiltee == 0:
                    if nom != "distance":
                        self.perso.touché(ennemi.att)
                        ennemi.touche()

    def game_over(self):
        global etat_jeu, timer_g
        etat_jeu = "game_over"
        timer_g = 0
        données.ajouter_score(self.score)

    def update(self):
        """
        L'update de toutes les variables nessesaires pour le jeu en sa globalitée.
        """
        self.colisions()
        self.spawn()
        self.perso.update()
        for _, infos in self.ennemis:
            ennemis= infos["stock"]
            for ennemi in ennemis:
                ennemi.update()

    def draw(self):
        """
        Dessin de tout ce qui ce passe dans le jeu.
        """
        # Affichage de l'ui
        px.cls(12) # Arrière-plan
        for i in range(self.perso.vies): # Affichage du nb de vies
            px.blt(px.width - 15 - 15*i, 5, 0, 98, 34, 12, 12, 12)
        # Affichage du nb de vies manquantes
        for u in range(difficultées[paramètres["Difficultée"]]["vies"] - self.perso.vies):
            x_base = px.width - 15 - difficultées[paramètres["Difficultée"]]["vies"] * 15

            px.blt(x_base + 15 + 15 * u, 5, 0, 114, 34, 12, 12, 12)
        
        draw_elements("Jeu", "texte") # Affichage des textes

        # Affichage des entitées
        for _, infos in self.ennemis:
            ennemis: list[Ennemi] = infos["stock"]
            for ennemi in ennemis:
                ennemi.draw()
        
        self.perso.draw()

class Lancement_jeu:
    def animation(self):
        global etat_jeu
        etat_jeu = "Prepa"
        self.timer = 0

    def lancement(self):
        global etat_jeu, jeu
        etat_jeu = "Jeu"
        jeu = Jeu()

    def update(self):
        self.timer += 1

        if self.timer == 300:
            self.lancement()
    
    def draw(self):
        for i in range(self.timer // 10):
            px.rect(0, 16 * i, px.width, 16, 16)
            if i == (px.height // 16) + 10:
                px.blt(px.width / 2 - 32, px.height / 2 - 16, 0, 128, 96, 64, 32, 15, scale= 8)

class Base_données:
    def ouverture(self):
        conn = sqlite3.connect(Données)
        cur = conn.cursor()
        return conn, cur

    def fermeture(self, conn: sqlite3.Connection, cur: sqlite3.Cursor):
        cur.close()
        conn.close()

    def réinitialisation(): #type: ignore
        conn = sqlite3.connect(Données)
        cur = conn.cursor()
        ll = cur.execute("select name from sqlite_master").fetchall()
        l = []
        for i in ll:
            l.append(i[0])

        for name in l:
            if not (name == "Pseudos" or name == "Hscores"):
                cur.execute(f"drop table {name}")

        cur.execute("delete from Pseudos")
        cur.execute("delete from Hscores")
        conn.commit()

        cur.close()
        conn.close()
        
    def création(): #type: ignore
        conn = sqlite3.connect(Données)
        cur = conn.cursor()
        cur.execute("create table Pseudos(pseudo text, last bolean default False)")
        cur.execute("create table Hscores(score integer, joueur text)")
        cur.close()
        conn.close()

    def recup_pseudos(self):
        conn, cur = self.ouverture()
        r = cur.execute("select pseudo from Pseudos").fetchall()
        result = []
        for i in range(len(r)):
            result.append(r[i][0])
        self.fermeture(conn, cur)
        return result
    
    def recup_score(self):
        conn, cur = self.ouverture()
        r = cur.execute("select * from Hscores").fetchall()
        self.fermeture(conn, cur)
        return r
    
    def refresh_score(self):
        scores: list[tuple[int, str]] = self.recup_score()
        scores.sort(reverse= True)
        if len(scores) < 40:
            scores = scores[:40]
        i = 0
        for score, nom in scores:
            espace = [(" ")for _ in range(23 - len(nom) - len(str(score)))]

            txt = f"{i + 1}.{nom}{"".join(espace)}{score}"

            elements["Score"]["texte"][i].change_texte(txt)
    
    def ajouter_score(self, Score: int):
        global suchis
        conn, cur = self.ouverture()
        cur.execute(f"insert into Hscores(score, joueur) values({Score}, '{pseudo}')")
        cur.execute(f"update {pseudo}_generale set suchis = {suchis + (Score * difficultées[paramètres["Difficultée"]]["rendement"] // 10)}")
        conn.commit()
        suchis = self.recup_suchis()
        self.fermeture(conn, cur)
        self.refresh_score()

    def chek_new(): #type: ignore
        conn = sqlite3.connect(Données)
        cur = conn.cursor()
        if len(cur.execute("select * from Pseudos").fetchall()) == 0:
            i = True
        else:
            i = False
        cur.close()
        conn.close()
        return i
    
    def recup_sqlite_master(self):
        conn, cur = self.ouverture()
        r = cur.execute("select name from sqlite_master").fetchall()
        result = []
        for i in range(len(r)):
            result.append(r[i][0])
        self.fermeture(conn, cur)
        return result
    
    def recup_last_pseudo() -> str: #type: ignore
        conn = sqlite3.connect(Données)
        cur = conn.cursor()
        i = cur.execute("select pseudo from Pseudos where last = True").fetchone()[0]
        cur.close()
        conn.close()
        return i
    
    def recup_objets(self) -> list[bool]:
        conn, cur = self.ouverture()
        r = cur.execute(f"select acheté from {pseudo}_amélioration").fetchall()
        result = []
        for i in range(len(r)):
            result.append(r[i][0])
        self.fermeture(conn, cur)
        return result
    
    def acheter_objet(self, nom: str = None): #type: ignore
        conn, cur = self.ouverture()

        for i in range(len(objets)):
            if objets[i]["nom"] == nom:
                break
        else:
            raise ValueError("Cet amélioration n'éxiste pas.")
    
        global suchis
        if suchis >= objets[i]["prix"]:
            suchis -= objets[i]["prix"]
            cur.execute(f"update {pseudo}_generale set suchis = {suchis} ")
            elements["Shop"]["texte"][0].change_texte(str(suchis))
        else:
            elements[objets[i]["nom"]]["texte"][3].change_texte("Vous ne le/pouvez pas !!")
            return

        i += 1

        if cur.execute(f"select acheté from {pseudo}_amélioration where rowid = {i}").fetchone()[0]:
            self.fermeture(conn, cur)
            raise Exception("Cet amélioration à déjà été acheté.")
        else:
            cur.execute(f"update {pseudo}_amélioration set acheté = True where rowid = {i}")
            conn.commit()

        self.refresh_stats()
        self.refresh_objets()
        self.fermeture(conn, cur)

    def refresh_objets(self):
        achetes = self.recup_objets()

        x_base = x = 160
        y = 50
        espace = 60
        u = 0
        for i in range(len(objets)):
            if not achetes[i] and (objets[i]["requirement"] == None or achetes[objets[i]["requirement"]] == True):
                if u % 6 == 0:
                    y += espace
                    x = x_base
                elements["Shop"]["boutons"][i].exclusion(False)
                elements["Shop"]["boutons"][i].change_position(x = x, y = y)
                x += espace
                u += 1
        
        global ouv_upg
        ouv_upg = None

    def refresh_stats(self):
        global base_stats
        achetés = self.recup_objets()
        for i in range(len(objets)):
            if achetés[i]:
                if base_stats[objets[i]["stat"]] < objets[i]["valeur"]:
                    base_stats[objets[i]["stat"]] = objets[i]["valeur"]
    
    def recup_param(self, paramètre):
        conn, cur = self.ouverture()
        result = cur.execute(f"select {paramètre} from {pseudo}_generale").fetchone()[0]
        self.fermeture(conn, cur)
        return result
    
    def recup_suchis(self):
        conn, cur = self.ouverture()
        result = cur.execute(f"select suchis from {pseudo}_generale").fetchone()[0]
        self.fermeture(conn, cur)
        return result
    
    def changer_paramètre(self, paramètre, valeur):
        conn, cur = self.ouverture()
        global paramètres
        paramètres[paramètre] = valeur
        cur.execute(f"update {pseudo}_generale set {paramètre} = '{valeur}'")
        if paramètre == "Difficultée":
            elements["Params"]["texte"][1].change_texte(difficultées[valeur]["txt"])
            elements["Params"]["texte"][1].change_couleur(difficultées[valeur]["couleur"])
            elements["Params"]["texte"][2].change_texte(valeur)
            elements["Params"]["texte"][2].change_couleur(difficultées[valeur]["couleur"])
        conn.commit()
        self.fermeture(conn, cur)

    def __init__(self, Pseudo: str):
        global pseudo
        conn, cur = self.ouverture()

        pseudo = Pseudo.replace("$", " ")
        
        if Pseudo not in self.recup_pseudos():
            cur.execute(f"create table {Pseudo}_generale(suchis integer, Difficultée text)")
            cur.execute(f"create table {Pseudo}_amélioration(acheté boolean)")
            
            list_objets = []
            for _ in range(len(objets)):
                list_objets.append("(False)")
            
            objet = ", ".join(list_objets)
            
            if Pseudo == 'Cheat_test':
                cur.execute("insert into Cheat_test_generale(suchis, Difficultée) values(5000, 'Moyen')")
            else:
                cur.execute(f"insert into {Pseudo}_generale(suchis, Difficultée) values(0, 'Moyen')")
            cur.execute(f'insert into {Pseudo}_amélioration(acheté) values{objet}')

            cur.execute(f"insert into Pseudos(pseudo) values('{Pseudo}')")
        
        cur.execute("update Pseudos set last = False")
        cur.execute(f"update Pseudos set last = True where pseudo = '{Pseudo}'")

        conn.commit()

        self.fermeture(conn, cur)

        elements["Menu"]["texte"][0].change_texte(pseudo)

        ouvrir_menu("Menu")
            
def ouvrir_menu(menu):
    global menu_ouvert
    menu_ouvert = menu
    if menu == "Score":
        scores = données.recup_score()
        scores.sort(key= lambda a: a[0], reverse= True)

        for i in range(len(scores)):
            elements["Score"]["texte"][i].change_texte(f"{i + 1}.{scores[i][1]}{"_" * (23 - (len(scores[i][1]) + len(str(scores[i][0]))))}{scores[i][0]}")

def change_pseudo():
    global def_pseudo
    def_pseudo = Def_pseudo(True)

def ouvrir_upg(nom_upg: str):
    global ouv_upg
    ouv_upg = nom_upg

def init(Pseudo: str):
    global données, suchis, paramètres, etat_jeu

    ajouter_texte(px.width - 5, 5, 1, "", 7, "Menu", type_retour= "Inversé")
    données = Base_données(Pseudo)

    etat_jeu = "Menu"

    suchis = données.recup_suchis()

    paramètres = {"Difficultée": données.recup_param("Difficultée")}

    données.refresh_stats()

    ### Boutons du Menu principal ###
    ajouter_bouton(115, 70, 64, 32, "Menu", lancement_jeu.animation, taille= 4, x_img= 0, y_img= 32, x_img_a= 0, y_img_a= 128, modèle= True)
    ajouter_bouton(100, 192, 32, 32, "Menu", ouvrir_menu, "Infos", taille= 2, x_img= 32, y_img= 64, x_img_a= 32, y_img_a= 96, modèle= True)
    ajouter_bouton(200, 192, 32, 32, "Menu", ouvrir_menu, "Params", taille= 2, x_img= 0, x_img_a= 0, y_img= 64, y_img_a= 96, modèle= True)
    ajouter_bouton(300, 200, 16, 16, "Menu", ouvrir_menu, "Shop", taille= 4, coolkey= 16, x_img= 128, x_img_a= 128, y_img= 128, y_img_a= 144, modèle= True)
    ajouter_bouton(400, 200, 16, 16, "Menu", ouvrir_menu, "Score", taille= 4, x_img= 208, x_img_a= 208, y_img= 0, y_img_a= 16, modèle= True)

    ### Croix du menu infos ###
    ajouter_bouton(px.width - 31, 7, 16, 16, "Infos", ouvrir_menu, "Menu", modèle= True, x_img= 80, y_img= 32, x_img_a= 80, y_img_a= 48)

    ### Boutons du menu de la boutique ###
    for objet in objets:
        ajouter_bouton(0, 0, 16, 16, "Shop", ouvrir_upg, objet["nom"], taille= 3, modèle= True, x_img= refs_butons_upgs[objet["nom_modèle"]]["x_img"], y_img= refs_butons_upgs[objet["nom_modèle"]]["y_img"], x_img_a= refs_butons_upgs[objet["nom_modèle"]]["x_img_a"], y_img_a= refs_butons_upgs[objet["nom_modèle"]]["y_img_a"])
    données.refresh_objets()
    ajouter_bouton(px.width - 31, 7, 16, 16, "Shop", ouvrir_menu, "Menu", modèle= True, x_img= 80, y_img= 32, x_img_a= 80, y_img_a= 48)
    ### Textes menu de la boutique ###
    ajouter_texte(px.width / 2 + 40, 13, 2, f"{données.recup_suchis()}", 3, "Shop", "Millieu")

    ### Texte et bouton acheté de charque upg ###
    for objet in objets:
        ajouter_texte(65, 20, 1, objet["nom"], 16, objet["nom"], "Millieu")
        ajouter_texte(67, 50, 0.6, objet["description"], 1, objet["nom"], "Millieu")
        ajouter_texte(65, px.height - 50, 1, f"Prix: {objet["prix"]}", 12, objet["nom"], "Millieu")
        ajouter_texte(65, px.height - 40, 1, "", 16, objet["nom"], "Millieu")

        ajouter_bouton(49, px.height - 70, 32, 16, objet["nom"], données.acheter_objet, objet["nom"], modèle= False, couleur1= 10, couleur2= 12, bordure= 3)

    ### Croix du menu des scores ###
    ajouter_bouton(px.width - 31, 7, 16, 16, "Score", ouvrir_menu, "Menu", modèle= True, x_img= 80, y_img= 32, x_img_a= 80, y_img_a= 48)
    ### Textes menu des scores ###
    for i in range(2):
        for u in range(20):
            ajouter_texte(120 + (250 * i), 55 + (10 * u), 1, f"{(20 * i) + (u + 1)}.Score_encore_non_défini", 0, "Score", type_retour= "Millieu")
    ajouter_texte(px.width / 2 - 10, 20, 3, "Scores", 0x008CFF, "Score", "Millieu")
    données.refresh_score()

    ### Boutons du menu paramètres ###
    ajouter_bouton(px.width - 31, 7, 16, 16, "Params", ouvrir_menu, "Menu", modèle= True, x_img= 80, y_img= 32, x_img_a= 80, y_img_a= 48)
    ajouter_bouton(95, 55, 25, 13, "Params", données.changer_paramètre, "Difficultée", "Facile", couleur1= 9, couleur2= 10, bordure= 2)
    ajouter_bouton(125, 55, 25, 13, "Params", données.changer_paramètre, "Difficultée", "Moyen", couleur1= 9, couleur2= 10, bordure= 2)
    ajouter_bouton(155, 55, 25, 13, "Params", données.changer_paramètre, "Difficultée", "Diffiçile", couleur1= 9, couleur2= 10, bordure= 2)
    ajouter_bouton(250, 70, 25, 13, "Params", change_pseudo, couleur1= 9, couleur2= 10, bordure= 2)
    ### Textes du menu paramètres ###
    ajouter_texte(50, 42, 1, "1.Changer la difficultée", 7, "Params")
    ajouter_texte(140, 70, 1, difficultées[paramètres["Difficultée"]]["txt"], difficultées[paramètres["Difficultée"]]["couleur"], "Params", type_retour= "Millieu")
    ajouter_texte(140, 203, 2, paramètres["Difficultée"], difficultées[paramètres["Difficultée"]]["couleur"], "Params", type_retour= "Millieu")
    
    ### Texte du game over ###
    ajouter_texte(px.width / 2, px.height - 70, 1, "Apuyez sur la touche flèche/du bas pour revenir au menu", 7, "game_over", "Millieu")
    
    ### Textes du jeu global ###
    ajouter_texte(10, 10, 2, "", 0xFFB700, "Jeu", "Normal")
    ajouter_texte(px.width / 2, 10, 2, "", 0x00FF66, "Jeu", "Millieu")

def update():
    if not def_pseudo.choisi:
        def_pseudo.chek_touches()
    else:
        global etat_jeu
        if etat_jeu == "Menu":
            if menu_ouvert == "Shop":
                for boutons in elements["Shop"]["boutons"][:-1]:
                    boutons.change_position(y = boutons.y + px.mouse_wheel)
                    if boutons.y <= 48:
                        boutons.exclusion()
                    else:
                        boutons.exclusion(False)
                if ouv_upg != None:
                    update_elements(ouv_upg, "boutons")

            update_elements(menu_ouvert, "boutons")
            
            for bouton in elements["Params"]["boutons"]:
                if bouton.fonction == données.changer_paramètre:
                    if bouton.paramètres[0] == "Difficultée":
                        if bouton.paramètres[1] == paramètres["Difficultée"]:
                            bouton.couleur2 = 0
                        else:
                            bouton.couleur2 = 10
        elif etat_jeu == "Prepa":
            lancement_jeu.update()
        elif etat_jeu == "Jeu":
            jeu.update()
        elif etat_jeu == "game_over":
            global timer_g
            timer_g += 1
            if timer_g >= 180:
                if px.btnp(px.KEY_DOWN):
                    etat_jeu = "Menu"
        
        if px.btnp(px.KEY_A):
            px.quit()

def draw():
    if not def_pseudo.choisi:
        def_pseudo.draw()
    else:
        if etat_jeu == "Jeu":
            jeu.draw()
        elif etat_jeu == "game_over":
            px.cls(0)
            if px.frame_count % 46 < 23:
                img = 64
            else:
                img = 96

            px.blt(px.width / 2 - 32, px.height / 2 - 32, 0, 64, img, 64, 32, scale= 4)

            if timer_g >= 180:
                draw_elements("game_over", "texte")
        else:
            yL1 = -32
            yL2 = -16
            while yL1 <= px.height:
                yL1 += 32
                yL2 += 32
                px.rect(0, yL1, px.width, 16, 9)
                px.rect(0, yL2, px.width, 16, 10)
            px.mouse(True)
            if menu_ouvert == "Infos":
                px.blt(px.width / 2 - 16, px.height / 2 - 8, 0, 128, 32, 32, 16, scale= 15)
            elif menu_ouvert == "Params":
                px.blt(px.width / 2 - 16, px.height / 2 - 8, 0, 128, 48, 32, 16, scale= 15)
            
            draw_elements(menu_ouvert, "boutons", "texte")

            if menu_ouvert == "Shop":
                px.rect(0, 0, 128, px.height, 2)
                px.rect(10, 10, 108, px.height - 20, 10)
                px.blt(px.width / 2 + 75, 10, 0, 162, 35, 12, 11, 12, scale= 2)
                if ouv_upg != None:
                    draw_elements(ouv_upg, "boutons", "texte")

            if etat_jeu == "Prepa":
                lancement_jeu.draw()

px.init(512, 256, title= "Kenji Battle", fps= 60)
px.load(Ressources)

couleurs = px.colors.to_list()
couleurs.append(0xff2626)
px.colors.from_list(couleurs)

# vérifie si l'utilisateur se connecte pour la première fois
new = Base_données.chek_new() #type: ignore

difficultées =      {
    "Facile": {"txt":"Vraiment/vous n'arrivez pas/à jouer !!!//- 3 ennemis par vagues/- 2 types d'ennemis/- 5 vies/x0.5 de récompense", "couleur": 0x109837, "rendement": 0.5, "vies": 5, "ennemis": {"distance": {"nb_max": 3, "respawn": 400}, "sabre": {"nb_max": 3, "respawn": 500}, "assasin": {"nb_max": 0, "respawn": 0}, "lanceur": {"nb_max": 0, "respawn": 0}, "tank": {"nb_max": 0, "respawn": 0}}},
    "Moyen": {"txt":"Vous êtes tout/juste dans la moyenne//- 4 ennemis par vagues/- 3 type d'ennemis/- 4 vies//x1 de récompenses", "couleur": 0xcb6e05, "rendement": 1, "vies": 4, "ennemis": {"distance": {"nb_max": 3, "respawn": 400}, "sabre": {"nb_max": 3, "respawn": 500}, "assasin": {"nb_max": 0, "respawn": 0}, "lanceur": {"nb_max": 0, "respawn": 0}, "tank": {"nb_max": 0, "respawn": 0}}},
    "Diffiçile": {"txt":"La dernière difficultée/???//- 5 ennemis par vagues/- 5 types d'ennemis/- 3 vies//x2 de récompense", "couleur": 0xf50000, "rendement": 2, "vies": 3, "ennemis": {"distance": {"nb_max": 3, "respawn": 400}, "sabre": {"nb_max": 3, "respawn": 500}, "assasin": {"nb_max": 0, "respawn": 0}, "lanceur": {"nb_max": 0, "respawn": 0}, "tank": {"nb_max": 0, "respawn": 0}}}
    }

base_stats = {"Vitesse": 1, 
              "Revenus score": 1, 
              "Revenus suchis": 1, 
              "Range ult": 3, 
              "Reload ult": 10, 
              "Att ult": 1, 
              "Parade": 5,
              "Delay 1ere charge": 60, 
              "Delay 2eme charge": 90, 
              "Delay 3eme charge": 180, 
              "Reload att": 120,
              "3eme charge": False,
              "Ult": False,
              "Mini slash": False
              }
refs_butons_upgs = {"vitesse": {"x_img": 64, "y_img": 32, "x_img_a": 64, "y_img_a": 48},
                    "revenus score": {"x_img": 176, "y_img": 0, "x_img_a": 176, "y_img_a": 16},
                    "revenus suchis": {"x_img": 160, "y_img": 32, "x_img_a": 160, "y_img_a": 48},
                    "ult": {"x_img": 176, "y_img": 64, "x_img_a": 176, "y_img_a": 80},
                    "parade": {"x_img": 176, "y_img": 32, "x_img_a": 176, "y_img_a": 48},
                    "delay": {"x_img": 160, "y_img": 0, "x_img_a": 160, "y_img_a": 16},
                    "3charge": {"x_img": 192, "y_img": 64, "x_img_a": 192, "y_img_a": 80}
                    }
objets = (  {"nom": "La première/vitesse", "stat": "Vitesse", "valeur": 1.1, "description": "Stats visée: la vitesse./Elle augmente ta vitesse/mais attention/elle augmente aussi/un peu celle des ennemis.//Augmentation de 10 %", "prix": 100, "nom_modèle": "vitesse", "requirement": None},
            {"nom": "Adepte du/petit score", "stat": "Revenus score", "valeur": 1.1, "description": "Tu as l'impresion de/ne plus rien gagner/prend ça et profite de ton/bonus de 10% pedegdezgd/ kdoeokakdekdpaokd/dhehduazhhzeua", "prix": 200, "nom_modèle": "revenus score", "requirement": None}, 
            {"nom": "Adepte de la/mini pièce", "stat": "Revenus suchis", "valeur": 1.1, "description": "Un trou dans le monaie ?/Voila un peu d'aide,/un bonus de 10% (encore)/yueahrh fzrjfeijf reifu/rjf uzfiref eziuhf", "prix": 300, "nom_modèle": "revenus suchis", "requirement": None}, 
            {"nom": "Taper qui ?/Tout le monde !", "stat": "Range ult", "valeur": 4, "description": "J'aimerai toucher/tout le monde./He bas voila mon petit/ait l'air un petit/peu plus LARGE (33% plus grand)/ fhrfhzifuherf", "prix": 700, "nom_modèle": "ult", "requirement": 11},
            {"nom": "Je n'ai jamais/mon ult", "stat": "Reload ult", "valeur": 9, "description": "Attaquer en permanence, un bonheur./Utilise ton ulti 10% plus rapidement", "prix": 500, "nom_modèle": "ult", "requirement": 11},
            {"nom": "On tape 2/fois ici", "stat": "Att ult", "valeur": 2, "description": "Attaquer mais en plus/fort !! 2 x plus de dmg/edhiuh hdahuihh hdd/dbehjbajb abbdjz ab d/dhehabbd bajbhba.", "prix": 900, "nom_modèle": "ult", "requirement": 11},
            {"nom": "La parade", "stat": "Parade", "valeur": 10, "description": "Vous avez l'impresion de/trop vous faire toucher/prenez ce bonus et/vous ne le serez plus./10% par coup de parer l'att/jdehi uhfiz efrjifr/ededafrez rfzefrefzf frfrez", "prix": 400, "nom_modèle": "parade", "requirement": None},
            {"nom": "Rapide 1", "stat": "Delay 1ere charge", "valeur": 40, "description": "La vitesse c'est la clé/la première charge arrive/33% plus rapidement./fjojfjr ozjeofjofjz rfz/jrzfrj efjeifoj ez/headud edhuhdiazhd jdao", "prix": 600, "nom_modèle": "delay", "requirement": None},
            {"nom": "Rapide 2", "stat": "Delay 2eme charge", "valeur": 80, "description": "Attaquer vite est/un requis/la première charge arrive/10 % plus rapidement/rhzfiuhfize ffurfhiufhz/hduhz uehfiufh huuzh/fhrf zhfiezuhf ruihfuzif/hfhzifhz hufzhf huifh", "prix": 800, "nom_modèle": "delay", "requirement": None},
            {"nom": "Rapide 3", "stat": "Delay 3eme charge", "valeur": 170, "description": "Tu as deja la 3eme/charge !? Alors ai la/plus rapidement!! ydygdagd/dyuadgey deazydgheadu/gdagy gyduagyugdh/gyedgayegdg hedhhedha", "prix": 1000, "nom_modèle": "delay", "requirement": 12},
            {"nom": "Attaquer mais/en plus rapide", "stat": "reload att", "valeur": 110, "description": "L'attaque de ton/personnage ne suis pas/prend cette upgrade/pour attaques plus/VITE hurzheuhifhz/hfuzhizh hzufhehihf", "prix": 500, "nom_modèle": "delay", "requirement": None},
            {"nom": "Un ult ???", "stat": "Ult", "valeur": True, "description": "Débloque un ultimate/surpuissant. degydgydggg/jideajiodj yeayuagdga/nnndnyuatbhf/opkkdkoeo gdgyge/dnjzndja jdhajzjii/hruzfhfzf fhuzfhefuezhufhzr", "prix": 1000, "nom_modèle": "ult", "requirement": None},
            {"nom": "La 3eme", "stat": "3eme charge", "valeur": True, "description": "Débloque la 3eme et/dernière charge/du jeu. gdyaezgdgdyezg/dbeabzd,ekaedna iduazjha/daziudbuda neadodaooo/dedeza rfrfezfrzrgftrgre", "prix": 1200, "nom_modèle": "3charge", "requirement": None},
            {"nom": "Un petit bonus", "stat": "Mini slash", "valeur": True, "description": "Qu'est ce/que c'est ? deadea/hudazhduehda ijzbrbzfbebf/djaejizjezioajd uduzzue", "prix": 1200, "nom_modèle": "3charge", "requirement": 12}
            )

lancement_jeu = Lancement_jeu()

def_pseudo = Def_pseudo()
if def_pseudo.choisi:
    init(def_pseudo.pseudo)

menu_ouvert = "Menu"
ouv_upg = None

px.run(update, draw)