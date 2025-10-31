# title: Kenji Battle
# author: Lateurte Jules et Fauchereau Evan
# desc: Un petit jeu d'enfants de 15 ans qui commencent tout juste à programmer
# version: 1.5

import pyxel as px
import sqlite3

Données = "Ressources//Données.sq3"
Fichier_ressource = "Ressources//kenji_battle_ressources.pyxres"

class App:
    def __init__(self, h, l, titre, fps):
        px.init(l, h, title = titre, fps = fps)
        px.load(Fichier_ressource)
        
        self.données = Base_donées()
        
        global Pseudo
        Pseudo = self.données.recup_pseudo()
        
        px.colors.from_list([0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF, 0xEEEEEE, 0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3, 0xFF9798, 0xEDC7B0, 0xff2626, 0x33ff00])
        
        self.score = 0
        
        self.play = False
        
        self.pause = False
        
        self.game_over = None
        
        self.perso = None
        
        self.ennemis_spawn = []
        self.ennemis_t = []
        
        self.menu = Menu()
        self.chek = True
            
        self.rendement = None
        
        self.fond = Fond()
        
        px.run(self.update, self.draw)
        
    def start(self):
        px.mouse(False)
        self.ennemis_spawn = []
        self.perso = None
        self.score = 0
        self.menu.menu = None
        
        global taille
        taille = self.menu.menu_p.scale
        
        self.game_over = Game_over()
        
        if self.menu.menu_p.difficultée[0] == "Façile":
            self.ennemis_spawn.append(Spawn(2, "Sabre", 700))
            self.ennemis_spawn.append(Spawn(2, "Distance", 500))
            vies = 5
            self.rendement = 0.5
            
        elif self.menu.menu_p.difficultée[0] == "Moyen":
            self.ennemis_spawn.append(Spawn(3, "Sabre", 600))
            self.ennemis_spawn.append(Spawn(3, "Distance", 400))
            vies = 4
            self.rendement = 1
            
        elif self.menu.menu_p.difficultée[0] == "Difficile":
            self.ennemis_spawn.append(Spawn(4, "Sabre", 500))
            self.ennemis_spawn.append(Spawn(4, "Distance", 400))
            vies = 3
            self.rendement = 2
            
        self.perso = Perso(px.width / 2, px.height - (16 + (8 * (taille-1))), vies)
        self.play = True
        
    def update(self):
        
        if self.play:
            self.fond.action()
            if self.perso.vies != 0:
                self.perso.actions()
                de = 600
                xep = None
                for ennemi_s in self.ennemis_spawn:
                    ennemi_s.spawn()
                    if not self.perso.ult:
                        ennemi_s.action(self.perso.x)
                    
                    for ennemi in ennemi_s.ennemis:                        
                        xe = ennemi.x
                        xj = self.perso.x
                        if abs(xe - xj) < de:
                            de = abs(xe - xj)
                            xep = xe
                        
                        numero_ennemi = ennemi_s.ennemis.index(ennemi)
                        
                        # vérification kill kunai
                        for kunai in self.perso.kunais:
                            if kunai.chek_touche(ennemi.x, ennemi.width):
                                ennemi.touché(1)
                                self.perso.kunais.remove(kunai)
                                if ennemi.alive <= 0:
                                    self.score += ennemi.recompense
                            if ennemi.kunai != None:
                                if kunai.chek_touche(ennemi.kunai.x, ennemi.kunai.width):
                                    self.perso.kunais.remove(kunai)
                                    self.score += ennemi.kunai.recompense
                                    ennemi.kunai_s()
                                        
                        for slash in self.perso.slashs:
                            b = slash
                            ok = False if self.perso.att else True
                            if [numero_ennemi, ennemi.type] not in slash.e_touchés:
                                if slash.chek_touche(ennemi.x, ennemi.width, ok, numero_ennemi, ennemi.type):
                                    ennemi.touché(slash.att)
                                    if ennemi.alive <= 0:
                                        self.score += ennemi.recompense
                                        slash.mort(numero_ennemi, ennemi.type)
                            if ennemi.kunai != None:
                                if slash.chek_touche(ennemi.kunai.x, ennemi.kunai.width, ok):
                                    self.score += ennemi.kunai.recompense
                                    ennemi.kunai_s()
                                                            
                            if slash.suppression():
                                self.perso.slashs.remove(b)
                        
                        # verification kill sabre
                        if self.perso.att_timer != 0:
                            if ennemi.chek_touché(self.perso.x, self.perso.att_charge, self.perso.sens):
                                if ennemi.alive <= 0:
                                    self.score += ennemi.recompense
                                    
                            if ennemi.kunai != None:
                                if ennemi.kunai.chek_att(self.perso.x, self.perso.sens):
                                    if self.perso.att_charge >= 2:
                                        self.perso.kunais.append(Kunai(ennemi.kunai.x, 16, self.perso.sens))
                                        self.score += ennemi.kunai.recompense
                                    self.score += ennemi.kunai.recompense
                                    ennemi.kunai_s()
                                        
                        elif self.perso.ult and self.perso.ult_timer >= 170:
                            if ennemi.chek_ult(self.perso.ult_cible):
                                ennemi.touché(Stats[5])
                                if ennemi.alive <= 0:
                                    self.score += ennemi.recompense
                            if ennemi.kunai != None:
                                if ennemi.kunai.chek_ult(self.perso.ult_cible):
                                    self.score += ennemi.kunai.recompense
                                    ennemi.kunai_s()
                                        
                        else:
                            if not self.perso.ult:
                                # Vérification du degat
                                if self.perso.touche == False:
                                    if ennemi.kunai != None:
                                        if ennemi.kunai.chek_touche(xj, 16):
                                            if not self.perso.touché():
                                                ennemi.touche()
                                            ennemi.kunai_s()
                                    else:
                                        if ennemi.type != "Distance":
                                            if ennemi.chek_touche(self.perso.x):
                                                if self.perso.touché():
                                                    ennemi.repouse()
                                                    self.score += 25 * Stats[2]
                                                if ennemi.vitesse_b != ennemi.vitesse:
                                                    ennemi.touche()
                        
                        if ennemi.is_alive() <= 0:
                            ennemi_s.ennemis.remove(ennemi_s.ennemis[numero_ennemi])
                if not self.perso.ult:            
                    self.perso.ennemi_proche(xep)
            else:
                self.perso.touche = False
                self.game_over.mort(self.score, self.menu.pseudo, self.perso.x)
                if self.game_over.timer == 1:
                    self.données.ajouter_suchis(self.menu.menu_b.suchis + (self.score // 100 * self.rendement * Stats[1]))
                self.perso.sens = px.sgn(self.game_over.ennemi.x - self.perso.x)
                if self.game_over.timer == 1000:
                    self.play = False
                    self.menu.menu_s.refresh()
                    self.menu.menu_b.refresh_suchis()
                
        else:
            if self.chek:
                if self.données.chek_new():
                    self.menu.menu_p.changement = True
                else:
                    self.données.init(self.données.recup_pseudo())
                    self.menu.refresh_données()
                self.chek = False
            else:
                start = self.menu.action()
                if start:
                    self.start()
    
    def draw(self):
        if self.play:
            self.fond.draw()
            if self.perso.vies != 0:
                for ennemi_s in self.ennemis_spawn:
                    ennemi_s.draw(self.perso.x)
            else:
                self.game_over.draw(self.perso.x)
            
            self.perso.draw()
            
            draw_texte(5, 5, f"Score: {self.score}", 1, 0xFFD700, False)
            
            
        else:
            px.cls(0)
            
            self.menu.draw()
            
class Fond:    
    def __init__(self):
        self.elements_list = (
                        [16, 0, 0.3, 16, 16, 5, False],
                        [0, 0, 0.3, 16, 16, 5, False],
                        [0, 19, 0.8, 12, 7, [3, 5], True],
                        [48, 2, 0.6, 16, 6, [3, 5], True],
                        [16, 16, 0.4, 16, 16, 2, False],
                        [32, 0, 0.5, 16, 16, [2, 3], False],
                        [32, 16, 0.5, 16, 16, [2, 3], False]
                        )
        
        self.roulette = (0, 1, 2, 2, 2, 3, 3, 3, 4, 5, 6)
        
        self.elements_stats = []
        self.elements = []
        self.timer = -1
        self.changement_nuit = 2000
        self.c = 0
        self.ciel = 12
        self.a = 0
        
    def spawn(self):
        if self.timer == -1:
            for i in range(4):
                modèle = self.elements_list[self.roulette[px.rndi(0, 10)]]
                if type(modèle[5]) == list:
                    modèle[5] = px.rndi(modèle[5][0], modèle[5][1])
                self.elements += [modèle[0:6]]
                self.elements_stats += [[px.rndi(50, px.width - 100), px.rndi(50, px.height - 100) if modèle[6] else px.height - (modèle[4] + (modèle[4] / 2 * (modèle[5] - 1))), 1 if px.rndi(0,1) == 1 else -1]]
            self.timer = 500
        elif self.timer == 0:
            modèle = self.elements_list[self.roulette[px.rndi(0, 10)]]
            if type(modèle[5]) == list:
                modèle[5] = px.rndi(modèle[5][0], modèle[5][1])
            self.elements += [modèle[0:6]]
            sens = 1 if px.rndi(0,1) == 1 else -1
            self.elements_stats += [[-(modèle[3] + (modèle[3] / 2 * (modèle[5] - 1))) if sens == 1 else px.width + (modèle[3] / 2 * (modèle[5] - 1)), px.rndi(50, px.height - 100) if modèle[6] else px.height - (modèle[4] + (modèle[4] / 2 * (modèle[5] - 1))), sens]]
            self.timer = 500
        self.timer -= 1
                     
    def action(self):
        self.spawn()
        self.c += 1
        if self.c == self.changement_nuit:
            self.ciel = 5
        elif self.c == self.changement_nuit * 2:
            self.ciel = 12
            self.c = 0
        for i in range(len(self.elements)):
            if px.frame_count % 10 == 0:
                self.elements_stats[i][0] += self.elements[i][2] * self.elements_stats[i][2]
                
    def draw(self):
        px.cls(self.ciel)
        for i in range(len(self.elements)):
            px.blt(self.elements_stats[i][0], self.elements_stats[i][1], 1, self.elements[i][0], self.elements[i][1], self.elements[i][3] * self.elements_stats[i][2], self.elements[i][4], 12, scale = self.elements[i][5])
        
class Changement_pseudo:
    def __init__(self):
        self.donnees = Base_donées()
        self.pseudo = ""
        self.enter = False
        self.keys = ((px.KEY_A, "A", "a"), (px.KEY_Z, "Z", "z"), (px.KEY_E, "E", "e"), (px.KEY_R, "R", "r"), (px.KEY_T, "T", "t"), (px.KEY_Y, "Y", "y"),
                     (px.KEY_U, "U", "u"), (px.KEY_I, "I", "i"), (px.KEY_O, "O", "o"), (px.KEY_P, "P", "p"), (px.KEY_Q, "Q", "q"), (px.KEY_S, "S", "s"),
                     (px.KEY_D, "D", "d"), (px.KEY_F, "F", "f"), (px.KEY_G, "G", "g"), (px.KEY_H, "H", "h"), (px.KEY_J, "J", "j"), (px.KEY_K, "K", "k"),
                     (px.KEY_L, "L", "l"), (px.KEY_M, "M", "m"), (px.KEY_W, "W", "w"), (px.KEY_X, "X", "x"), (px.KEY_C, "C", "c"), (px.KEY_V, "V", "v"),
                     (px.KEY_B, "B", "b"), (px.KEY_N, "N", "n"), (px.KEY_1, "1", ""), (px.KEY_2, "2", "é"), (px.KEY_3, "3", ""), (px.KEY_4, "4", "'"),
                     (px.KEY_5, "5", "("), (px.KEY_6, "6", "-"), (px.KEY_7, "7", "è"), (px.KEY_8, "8", "_"), (px.KEY_9, "9", "ç"), (px.KEY_0, "0", "à"),
                     (px.KEY_RIGHTBRACKET, "", ")"), (px.KEY_COMMA, "?", ","), (px.KEY_SEMICOLON, ".", ";"),
                     (px.KEY_COLON, "", ":"), (px.KEY_SPACE, " ", " ")
                     )
        
        self.majuscule = True
        self.caractère = None
        self.x = px.width / 2 - 55
        self.y = px.height / 2 + 12
        self.x_base = self.x
    
    def recup(self):
        self.donnees.init(self.pseudo)
        self.pseudo = ""
        self.enter = False
        self.majuscule = True
        self.x = px.width / 2 - 55
    
    def ecriture(self):
        self.caractère = None
        if px.btnp(px.KEY_LSHIFT) or px.btnp(px.KEY_SHIFT):
            if self.majuscule:
                self.majuscule = False
            else:
                self.majuscule = True
        if len(self.pseudo) != 19:
            for code, majuscule, minuscule in self.keys:
                if px.btnp(code, 50, 5):
                    if self.majuscule:
                        self.caractère = majuscule
                    else:
                        self.caractère = minuscule
                    
        if self.caractère != None:
            if len(self.pseudo) == 0:
                self.pseudo = self.caractère
            else:
                self.pseudo += self.caractère
            if self.caractère != "":
                self.x += 6
        
        if px.btnp(px.KEY_BACKSPACE, 50, 5):
            if len(self.pseudo) != 0:
                self.x -= 6
            self.pseudo = self.pseudo[:-1]
            
            
        if px.btnp(px.KEY_RETURN):
            if len(self.pseudo) != 0:
                self.enter = True
    
    def ecrit(self):
        return self.enter
    
    def draw(self):
        draw_lignes(16)
        
        px.blt(px.width / 2 - 32, px.height / 2 - 16, 0, 64, 128, 64, 32, scale = 2)
        draw_texte(px.width / 2 - 60, px.height / 2 - 16, "Quel est ton pseudo?", 1, 7, False)
        
        if px.frame_count % 60 < 30:
            px.rect(self.x, self.y, 1, 8, 0)
            
        draw_texte(self.x_base, self.y, self.pseudo, 1, 0, False)
          
class Informations:
    def __init__(self):
        self.boutons = [
                        Bouton(px.width - 46, 15, 1, "Croix")
                        ]
        
    def action(self):
        for bouton in self.boutons:
            bouton.action()
        
    def draw(self):
        px.blt(px.width / 2 - 16, px.height / 2 - 8, 0, 128, 32, 32, 16, scale = 14)
        draw_texte(px.width / 2 - 2, 50, "'Malheur, Ma femme à été kidnapée par ces enflures de nijas/pendant mon entrainement à la montagne, je ne reviendrai pas sans/l'avoir récupérée'/Kenji//Kenji Battle est un jeu de platformer et un jeu de survie face à/des vagues d'ennemis de toutes sorte. Survivez à ces ennemis pour/gagner des points et acheter des améliorations.//Battez votre score encore et encore et peut etre que Kaze vous/rejoindra dans votre quète de vengence.//Les flèches pour bouger le bas pour attaquer.", 1, 0, True)
        for bouton in self.boutons:
            bouton.draw()

class Paramètres:
    def __init__(self):
        self.données = Base_donées()
        self.changement = False
        self.att = False
        self.boutons = [
                        Bouton(px.width - 46, 15, 1, "Croix")
                        ]
        self.reset = False
        self.att_t = 0
        self.taille_list = (2, 2.5, 3)
        self.difficultée_list = (("Façile", 17, "Un mode juste chill/-2 ennemis maximum/-2 type seulement/-5 vies/x0.5 suchis"), ("Moyen", 9, "Un mode juste normal/-3 ennemis max/-3 types/-4 vies/x1 suchis") , ("Difficile", 16, "La même en plus dur/-4 ennemis max/-3 types d'ennemis/-3 vies/x2 suchis"), ("Secret", 3, "???"))
        
    def refresh_données(self):
        liste_params = self.données.recup_paramètres()
        
        for taille, difficultée in liste_params:
                self.scale = taille
                for i in range(len(self.difficultée_list)):
                    if difficultée == self.difficultée_list[0]:
                        a = i
                        self.difficultée = self.difficultée_list[a]
        
        print(a)
        print(self.scale)
                            
        self.boutons = [
                        Bouton(px.width - 46, 15, 1, "Croix"),
                        Bouton(400, 53, 2, "Bouton", "Changement_p"),
                        Gr_boutons(81, 70, 12, 8, 2, "Bouton", "Taille", "x", self.taille_list.index(self.scale), 3),
                        Gr_boutons(81, 110, 12, 8, 2, "Bouton", "Difficulté", "x", a, 3),
                        Bouton(400, 90, 2, "Bouton", "Supression_d")
                        ]
        
    def action(self):
        for bouton in self.boutons:
            bouton.action()
            if bouton.type == "Croix":
                if bouton.état():
                    self.données.sauvegarder_param(self.scale, self.difficultée[0])
            if bouton.type == "Changement_p":
                if bouton.état():
                    self.changement = True
                    bouton.desactivation()
            if bouton.type == "Taille":
                self.scale = self.taille_list[bouton.activé]
            if bouton.type == "Difficulté":
                self.difficultée = self.difficultée_list[bouton.activé]
            if bouton.type == "Supression_d":
                if bouton.état():
                    if self.att:
                        self.att_t = 0
                        self.att = False
                        self.données.reinitialisation()
                        self.changement = True
                        self.reset = True
                    else:
                        self.att = True
                    bouton.desactivation()
                        
        if self.att:
            self.att_t += 1
            if self.att_t == 500:
                self.att = False
                self.att_t = 0
    
    def draw(self):
        px.blt(px.width / 2 - 16, px.height / 2 - 8, 0, 128, 48, 32, 16, scale = 14)
        draw_texte(290, 53, "3.Changer le pseudo/(changer de sauvegarde)", 1, 7, True)
        draw_texte(290, 90, "4.Réinitialiser toutes les/sauvegardes", 1, 7, True)
        if self.att:
            if self.att_t % 76 < 38:
                draw_texte(310, 115, "Attention la supression est définitive", 1, 16, True)
        for bouton in self.boutons:
            bouton.draw()
        draw_texte(60, 53, "1.Changer la taille", 1, 7, False)
        draw_texte(60, 74, "     2   2.5   3", 1, 0, False)
        draw_texte(60, 95, "2.Changer la difficultée", 1, 7, False)
        draw_texte(125, 130, self.difficultée[0], 2, self.difficultée[1], True)
        draw_texte(125, 150, self.difficultée[2], 1 if self.difficultée[2] != "???" else 3, self.difficultée[1], True)
            
class Gr_boutons:
    def __init__(self, x, y, width, height, scale, b_types, nom_gr, ligne, depart = None, nb_gr = 0, nb_lignes = 1, espacement = 6):
        if ligne == "Double":
            base_x = x
        if type(b_types) == str:
            if ligne == "x":
                self.boutons = [Bouton(x + (width * scale + espacement) * i, y, scale, b_types) for i in range(nb_gr)]
            if ligne == "y":
                self.boutons = [Bouton(x, y + (height * scale + espacement) * i, scale, b_types) for i in range(nb_gr)]
            if ligne == "Double":
                self.boutons = []
                for i in range(nb_gr):
                    if i % nb_lignes == 0:
                        y += (height * scale + 6)
                        x = base_x
                    else:
                        x += (width * scale + 6)
                    self.boutons.append(Bouton(x, y, scale, b_types))
        else:
            self.boutons = []
            for i in range(len(b_types)):
                self.boutons.append(Bouton(x, y, scale, b_types[i]))
                if ligne == "x":
                    x += (width * scale + espacement)
                if ligne == "y":
                    y += (height * scale + espacement)
                if ligne == "Double":
                    x += (width * scale + espacement)
                    if (i + 1) % nb_lignes == 0:
                        y += (height * scale + espacement)
                        x = base_x
                    
        self.activé = depart
        self.type = nom_gr
        
    def scroll(self, pixel_scroll):
        if pixel_scroll != 0:
            for bouton in self.boutons:
                bouton.y += pixel_scroll
        
    def action(self):
        for bouton in self.boutons:
            bouton.action()
            if bouton.select:
                if px.btn(px.MOUSE_BUTTON_LEFT):
                    self.activé = self.boutons.index(bouton)
            if self.activé == self.boutons.index(bouton):
                bouton.activation()
            else:
                bouton.desactivation()
            
    def draw(self):
        for bouton in self.boutons:
            bouton.draw()
            
class Upgrade:
    def __init__(self, u_type, prix, valeur, nom_variable = None):
        self.list_upg = (
                        ("Vitesse", 5, f"Améliore la vitesse/un petit peu.///Vitesse = {valeur}", 12),
                        ("Ultimate", 8, "Débloquez une/attaque/surpuissante", 0),
                        ("Amélioration/de/l'ulti", 8, f"Améliorez votre/meilleure attaque.///{nom_variable} = {valeur}", 0),
                        ("Temps de/charge", 9, f"Améliorez votre/première attaque.///{nom_variable} = {valeur}", 10),
                        ("Revenus/suchis", 10, f"Améliorez les suchis/que vous gagnez.///Suchis = x{valeur}", 4),
                        ("Revenus/score", 10, f"Améliorez le score/que vous gagnez.///Score = x{valeur}", 9),
                        ("Parade", 1, f"Améliorez la chance/de parer un coup/au lieu de perdre/une vie.///Parade = {valeur}%", 10),
                        ("Une 3eme/charge", 3, "???", 3),
                        ("La 3eme/charge", 3, f"{nom_variable} = {valeur}", 3)
                        )
        
        for u_types, color_t, texte, color_te in self.list_upg:
            if u_type == u_types:
                self.texte = texte
                self.color_type = color_t
                self.color_texte = color_te
                
        self.bouton = Bouton(40, px.height - 50, 1, "Acheter")
        
        self.prix = prix
        self.valeur = valeur
        self.type = u_type
        self.nom_variable = nom_variable
        
    def action(self):
        self.bouton.action()
    
    def draw(self):
        px.blt(56, px.height / 2 - 16, 0, 192, 0, 16, 32, scale = 8)
        draw_texte(64, 15, self.type, 1.5, self.color_type, True)
        draw_texte(64, px.height / 2 - 40, self.texte, 1 if self.texte != "???" else 3, self.color_texte, True)
        self.bouton.draw()
        draw_texte(61, px.height - 30, f"Prix = {self.prix}", 1, 3, True)
            
class Boutique:
    def __init__(self):
        self.données = Base_donées()
        
        self.suchis = 0
        self.quart_bouton = 16
        
        self.list_paramètres = [
                                ["Vitesse", 1],
                                ["Revenus/suchis", 1],
                                ["Revenus/score", 1],
                                ["Range", 3],
                                ["Reload", 1000],
                                ["Att", 1],
                                ["Parade", 5],
                                ["Delay 1ere/charge", 75],
                                ["Delay 2eme/charge", 150],
                                ["Delay", 300],
                                ["Reload ", 100],
                                ['Une 3eme/charge', False],
                                ['Ultimate', False],
                                ['Mini slash', False],
                                ['Mini slash chance', 10]
                                ]
        self.increment = (0, 1, 2, 3, 5, 6)
        self.decrement = (4, 7, 8, 9, 10)
        
        self.bouton_c = Bouton(px.width - 46, 15, 1, "Croix")
        
        self.boutons = []
                
        self.refresh_stats()
    
    def refresh_données(self):
        self.refresh_objets()
        
        for i in range(len(self.objets_achetés)):
            if self.objets_achetés[i][2] == None:
                for nom, valeur in self.list_paramètres:
                    if self.objets_achetés[i][0] == nom:
                        if self.list_paramètres.index([nom, valeur]) in self.increment:
                            if self.objets_achetés[i][1] > valeur:
                                self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = self.objets_achetés[i][1]
                        elif self.list_paramètres.index([nom, valeur]) in self.decrement:
                            if self.objets_achetés[i][1] < valeur:
                                self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = self.objets_achetés[i][1]
                        else:
                            self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = True
            else:
                for nom, valeur in self.list_paramètres:
                    if self.objets_achetés[i][2] == nom:
                        if self.list_paramètres.index([nom, valeur]) in self.increment:
                            if self.objets_achetés[i][1] > valeur:
                                self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = self.objets_achetés[i][1]
                        elif self.list_paramètres.index([nom, valeur]) in self.decrement:
                            if self.objets_achetés[i][1] < valeur:
                                self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = self.objets_achetés[i][1]
                        else:
                            self.list_paramètres[self.list_paramètres.index([nom, valeur])][1] = True
                            
        self.refresh_stats()
        
        self.boutons = [
                        Gr_boutons(136, 100, 16, 16, 3, self.upgrades_noms, "Objets", "Double", None, 3, 6, 16)
                        ]
        self.refresh_suchis()
        
    def refresh_suchis(self):
        self.suchis = self.données.recup_suchis()
                 
    def refresh_stats(self, indice = None, valeur = None):
        if indice != None:
            self.list_paramètres[indice][1] = valeur
        global Stats
        Stats = [self.list_paramètres[i][1] for i in range(len(self.list_paramètres))]
        
    def refresh_objets(self):
        liste = self.données.recup_objets()
        liste += self.données.recup_require()
        liste.sort()
        self.upgrades = []
        self.objets_achetés = []
        for prix, u_type, valeur, paramètre, acheté in liste:
            if acheté == 0:
                if u_type == "Amélioration/de/lulti":
                    u_type = "Amélioration/de/l'ulti"
                self.upgrades.append(Upgrade(u_type, prix, valeur, paramètre))
            elif acheté == 1:
                self.objets_achetés.append([u_type, valeur, paramètre])
        
        self.upgrades_noms = []
        for i in range(len(self.upgrades)):
            self.upgrades_noms.append(self.upgrades[i].type)
        
    def action(self):
        self.boutons[0].scroll(self.quart_bouton * px.mouse_wheel)
        self.bouton_c.action()
        for bouton in self.boutons:
            bouton.action()
            if bouton.type == "Objets":
                for i in range(len(bouton.boutons)):
                    if bouton.boutons[i].état():
                        self.upgrades[i].action()
                        if self.upgrades[i].bouton.état():
                            if self.suchis >= self.upgrades[i].prix:
                                self.suchis -= self.upgrades[i].prix
                                if self.upgrades[i].nom_variable != None:
                                    for a in range(len(self.list_paramètres)):
                                        if self.upgrades[i].nom_variable == self.list_paramètres[a][0]:
                                            if a in self.increment:
                                                if self.upgrades[i].valeur >= self.list_paramètres[a][1]:
                                                    self.refresh_stats(a, self.upgrades[i].valeur)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, self.upgrades[i].valeur)
                                            elif a in self.decrement:
                                                if self.upgrades[i].valeur <= self.list_paramètres[a][1]:
                                                    self.refresh_stats(a, self.upgrades[i].valeur * 100)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, self.upgrades[i].valeur)
                                            else:
                                                self.refresh_stats(a, True)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, True)
                                else:
                                    for a in range(len(self.list_paramètres)):
                                        if self.upgrades[i].type == self.list_paramètres[a][0]:
                                            if a in self.increment:
                                                if self.upgrades[i].valeur >= self.list_paramètres[a][1]:
                                                    self.refresh_stats(a, self.upgrades[i].valeur)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, self.upgrades[i].valeur)
                                            elif a in self.decrement:
                                                if self.upgrades[i].valeur <= self.list_paramètres[a][1]:
                                                    self.refresh_stats(a, self.upgrades[i].valeur * 100)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, self.upgrades[i].valeur)
                                            else:
                                                self.refresh_stats(a, True)
                                                self.données.acheter_objet(self.upgrades[i].type, self.suchis, True)
                                                
                                self.refresh_objets()
                                self.boutons[0] = Gr_boutons(136, 100, 16, 16, 3, self.upgrades_noms, "Objets", "Double", None, 3, 6, 16)
                            else:
                                self.upgrades[i].bouton.desactivation()
        
    def draw(self):
        px.blt(56, px.height / 2 - 16, 0, 192, 0, 16, 32, scale = 8)
        draw_texte(64, 15, "-------", 1.5, 0, True)
        draw_texte(64, px.height / 2 - 20, "----------/----------", 1, 0, True)
        draw_texte(61, px.height - 30, f"Prix = ---", 1, 3, True)
        for bouton in self.boutons:
            if bouton.type == "Objets":
                for i in range(len(bouton.boutons)):
                    if bouton.boutons[i].état():
                        self.upgrades[i].draw()
                bouton.draw()
                draw_lignes(16, 64, 128)
                
        self.bouton_c.draw()        
        
        draw_texte(px.width / 2, 5, f"{self.suchis}", 2, 2, True)
        px.blt(px.width / 2 - (len(f"{self.suchis}") * 6) - 14, 8, 0, 113, 49, 14, 14)
        
class Bouton:
    def __init__(self, x, y, scale, b_type, paramètre = None):
        self.scale = scale
        
        self.liste_types = (
                            (None, "Play", 0, 32, 128, 64, 32, 15),
                            (None, "Paramètres", 0, 64, 96, 32, 32, 15),
                            (None, "Information", 32, 64, 96, 32, 32, 15),
                            (None, "Croix", 80, 32, 48, 16, 16, 1),
                            (self.bouton, "Bouton", 112, 16, 24, 12, 8, None),
                            (None, "Boutique", 128, 128, 144, 16, 16, None),
                            (None, "Vitesse", 64, 32, 48, 16, 16, None),
                            (None, "Ultimate", 176, 64, 80, 16, 16, None),
                            (None, "Amélioration/de/l'ulti", 176, 64, 80, 16, 16, None),
                            (None, "Temps de/charge", 160, 0, 16, 16, 16, None),
                            (None, "Revenus/score", 176, 0, 16, 16, 16, None),
                            (None, "Revenus/suchis", 160, 32, 48, 16, 16, None),
                            (None, "Parade", 176, 32, 48, 16, 16, None),
                            (self.acheter, "Acheter", 144, 128, 144, 48, 16, None),
                            (None, "Score", 208, 0, 16, 16, 16, None),
                            (None, "Une 3eme/charge", 192, 64, 80, 16, 16, None),
                            (None, "La 3eme/charge", 192, 64, 80, 16, 16, None)
                            )
        for _, types, _, _, _, width, height, colkey in self.liste_types:
            if b_type == types:
                self.x = x + ((width / 2) * (scale - 1))
                self.y = y + ((height / 2) * (scale - 1))
                self.width = width
                self.height = height
                self.colkey = colkey if colkey != None else 16
                
        self.img = b_type
        self.type = b_type if paramètre == None else paramètre
        self.img_x = 0
        self.img_y = 0
        self.anim = 0
        self.etat = False
        self.select = False
        self.texte = None
        
    def état(self):
        return self.etat
    
    def Texte(self, texte, scale, couleur):
        draw_texte(self.x + ((self.width * self.scale) / 2) - 3, self.y + (((self.height * self.scale)/2) - 4), texte, scale * self.scale, couleur, True)
    
    def activation(self):
        self.etat = True
        
    def acheter(self):
        self.texte = ["Acheter"]
        
    def desactivation(self):
        self.etat = False
        
    def bouton(self):
        if self.etat:
            self.img_y -= 16
        
    def action(self):
        for b_type, nom, img_x, img_y1, img_y2, width, height, _ in self.liste_types:
            if self.img == nom:
                self.width = width
                self.height = height
                self.img_x = img_x
                self.img_y = img_y1
                self.chek_souris()
                if self.select:
                    if self.anim % 40 < 20:
                        self.img_y = img_y2
                    if px.btnp(px.MOUSE_BUTTON_LEFT):
                        self.etat = True
                if b_type != None and b_type != self.texte:
                        b_type()
        
    def chek_souris(self):
        if (px.mouse_x <= self.x + (self.width + ((self.width / 2) * (self.scale- 1))) and px.mouse_x >= self.x - ((self.width / 2) * (self.scale - 1))) and (px.mouse_y <= self.y + (self.height + ((self.height / 2) * (self.scale - 1))) and px.mouse_y >= self.y - ((self.height / 2) * (self.scale - 1))):
            self.anim += 1
            self.select = True
        else:
            self.anim = 0
            self.select = False
    
    def draw(self):
        px.mouse(True)
        if self.type == "Boutique":
            px.pal(8, 16)
        px.blt(self.x, self.y, 0, self.img_x, self.img_y, self.width, self.height, self.colkey, scale = self.scale)
        if self.texte != None:
            self.Texte(self.texte[0], self.texte[1] if len(self.texte) > 1 else 1, self.texte[2] if len(self.texte) > 2 else 7)
        px.pal()
        
class Base_donées:
    def création(self):
        self.ouverture()
        self.cur.execute("create table Pseudos(pseudo text, last boolean)")
        self.cur.execute("create table Hscores(score integer, joueur text)")
        self.fermeture()
    
    def ouverture(self):
        self.conn = sqlite3.connect(Données)
        self.cur = self.conn.cursor()
        
    def fermeture(self):
        self.cur.close()
        self.conn.close()
        
    def reinitialisation(self):
        self.ouverture()
        
        l = self.recup_sqlite_master()
        
        l.remove("Hscores")
        l.remove('Pseudos')
        
        for i in range(len(l)):
            self.cur.execute(f"drop table {l[i]}")
        self.cur.execute("delete from Hscores")
        self.cur.execute("delete from Pseudos")
        self.conn.commit()
        self.fermeture()
        
    def recup_sqlite_master(self):
        l = []
        u = self.cur.execute("select name from sqlite_master").fetchall()
        for i in range(len(u)):
            l.append(u[i][0])
        return l
        
    def init(self, Pseudo):
        global pseudo
        pseudo = Pseudo
        self.ouverture()
        
        if Pseudo not in self.recup_pseudo():
            Pseudo = Pseudo.replace(" ", "$")
            print("true")
            
            self.cur.execute(f"create table {Pseudo}_generale(suchis integer, Taille integer, Difficultée text)")
            self.cur.execute(f"create table {Pseudo}_objets(type text, prix integer, valeur integer, paramètre text, acheté boolean default 0, deblocage_nom text, deblocage_valeur integer)")
            
            list_objets = (
                        ('Parade', 400, 10, None, None, None),
                        ('Vitesse', 500, 1.20, None, None, None),
                        ('Temps de/charge', 600, 0.5, 'Delay 1ere/charge', None, None),
                        ('Revenus/suchis', 700, 1.10, None, None, None),
                        ('Une 3eme/charge', 750, True, None, None, None),
                        ('Revenus/score', 800, 1.10, None, None, None),
                        ('Temps de/charge', 900, 1, 'Delay 2eme/charge', None, None),
                        ('Parade', 1000, 20, None, 'Parade', 10),
                        ('Ultimate', 1000, True, None, None, None),
                        ('La 3eme/charge', 900, 2.7, 'Delay', 'Une 3eme/charge', True),
                        ('La 3eme/charge', 1400, True, 'Mini slash', 'Une 3eme/charge', True),
                        ('Amélioration/de/lulti', 700, 3.5, 'Range', 'Ultimate', True),
                        ('Amélioration/de/lulti', 800, 9, 'Rechargement', 'Ultimate', True),
                        ('Amélioration/de/lulti', 700, 2, 'Att', 'Ultimate', True)
                        )
            
            objets = ", "
            objets = objets.join(list(map(str, list_objets))).replace("None", "null").replace("True", "'True'")
            
            if Pseudo == 'Cheat_test':
                self.cur.execute("insert into Cheat_test_generale(suchis, Taille, Difficultée) values(5000, 2, 'Moyen')")
            else:
                self.cur.execute(f"insert into {Pseudo}_generale(suchis, Taille, Difficultée) values(0, 2, 'Moyen')")
            self.cur.execute(f'insert into {Pseudo}_objets(type, prix, valeur, paramètre, deblocage_nom, deblocage_valeur) values {objets}')
            
            self.conn.commit()
            
        self.change_pseudo()
        
        self.fermeture()
        
    def change_pseudo(self):
        self.cur.execute("update Pseudos set last = False where last = True")
        if len(self.cur.execute(f"select pseudo from Pseudos where pseudo = '{pseudo}'").fetchall()) == 0:
            self.cur.execute(f"insert into Pseudos(pseudo, last) values('{pseudo}', True)")
        else:
            self.cur.execute(f"update Pseudos set last = True where pseudo = '{pseudo}'")
        self.conn.commit()
        
    def recup_last_pseudo(self):
        self.ouverture()
        u = self.cur.execute("select pseudo from Pseudos where last = True").fetchone()
        if u != None:
            u = u[0]
        self.fermeture()
        return u
        
    def chek_new(self):
        self.ouverture()
        if self.recup_pseudo == None:
            u = False
        else:
            u = True
        
        self.fermeture()
        return u
    
    def recup_objet(self):
        self.ouverture()
        liste_require = self.cur_p.execute(f"select prix, type, valeur, paramètre, acheté, deblocage_nom, deblocage_valeur from {pseudo}_objets where deblocage_nom not null").fetchall()
        liste_requirement = []
        for i in range(len(liste_require)):
            if liste_require[i][6] == 'True':
                self.cur_p.execute(f"select type, valeur, acheté from {pseudo}_objets where type = '{liste_require[i][5]}'")
            else:
                self.cur_p.execute(f"select type, valeur, acheté from {pseudo}_objets where type = '{liste_require[i][5]}' and valeur = {liste_require[i][6]}")
            liste = self.cur_p.fetchall()
            if not liste[0] in liste_requirement:
                liste_requirement.append(liste[0])
        
        v = []
        for u_type, prix, valeur, paramètre, acheté, deblocage_n, deblocage_v in liste_require:
            if (deblocage_n, deblocage_v, 1) in liste_requirement:
                v.append((u_type, prix, valeur, paramètre, acheté))
                
        u = self.cur_p.execute(f"select prix, type, valeur, paramètre, acheté from {pseudo}_objets where deblocage_nom is null").fetchall()
        
        self.fermeture()
        v += u
        return v
            
    def recup_pseudo(self):
        self.ouverture()
        l = []
        u = self.cur.execute("select pseudo from Pseudos").fetchall()
        for i in range(len(u)):
            l.append(u[i][0])
        return l
        
    def recup_paramètres(self):
        self.ouverture()
        v = self.cur_p.execute(f"select Taille, Difficultée from {pseudo}_generale").fetchall()
        self.fermeture()
        return v
    
    def recup_score(self):
        self.ouverture()
        v = self.cur_c.execute("select joueur, score from Hscores").fetchall()
        self.fermeture()
        return v
    
    def recup_suchis(self):
        self.ouverture()
        u = self.cur_p.execute(f"select suchis from {pseudo}_generale").fetchall()
        self.fermeture()
        return u
    
    def ajouter_suchis(self, suchis):
        self.ouverture()
        self.cur_p.execute(f"update {pseudo}_generale set suchis = {suchis}")
        self.conn_p.commit()
        self.fermeture() 
    
    def acheter_objet(self, nom, suchis, valeur):
        self.ouverture()
        if valeur == True:
            valeur = "'True'"
        if nom == "Amélioration/de/l'ulti":
            nom = "Amélioration/de/lulti"
        self.cur_p.execute(f"update {pseudo}_objets set acheté = 1 where valeur = {valeur} and type = '{nom}'")
        self.cur_p.execute(f"update {pseudo}_generale set suchis = {suchis}")
        self.conn_p.commit()
        self.fermeture()
    
    def sauvegarder_param(self, taille, difficultée):
        self.ouverture()
        self.cur_p.execute(f"update {pseudo}_generale set Taille = {taille}, Difficultée = '{difficultée}'")
        self.conn_p.commit()
        self.fermeture()
    
    def ajouter_score(self, score, joueur):
        self.ouverture()
        self.cur_c.execute(f"insert into Hscores(score, joueur) values ({score}, '{joueur}')")
        self.conn_c.commit()
        self.fermeture()
        
class Tableaux_scores:
    def __init__(self):
        self.données = Base_donées()
        
        self.bouton = Bouton(px.width - 46, 15, 1, "Croix")
        
        self.refresh()
        
    def refresh(self):
        liste = self.données.recup_score()
        liste_sort = []
        for Score, Pseudo in liste:
            liste_sort.append((Score, Pseudo))
        liste_sort.sort(reverse = True)
        list_Pseudos = []
        list_Scores = []
        
        for Score, Pseudo in liste_sort:
            list_Pseudos.append(Pseudo)
            list_Scores.append(Score)
            
        scores_list = [(f"{i}.Score encore non enregistré") for i in range(1, 19)]
        scores_list1 = [(f"{i}.Score encore non enregistré") for i in range(18, 36)]
        slash = "/"
        
        for i in range(0, min(len(list_Pseudos), 16)):
                espace = ""
                espaces = [(" ") for _ in range(27 - (len(list_Pseudos[i]) + len(str(list_Scores[i] + len(str(i))))))]
                espace = espace.join(espaces)
                scores_list[i] = f"{i + 1}.{list_Pseudos[i]}" + espace + f"{list_Scores[i]}"
        
        if len(list_Pseudos) > 17:            
            for i in range(17, min(len(list_Pseudos), 34)):
                espace = ""
                espaces = [(" ") for _ in range(27 - (len(list_Pseudos[i]) + len(str(list_Scores[i] + len(str(i))))))]
                espace = espace.join(espaces)
                scores_list1[i] = f"{i + 1}.{list_Pseudos[i]}" + espace + f"{list_Scores[i]}"
        
        self.scores = slash.join(scores_list)
        self.scores1 = slash.join(scores_list1)
    
    def action(self):
        self.bouton.action()
    
    def draw(self):
        self.bouton.draw()
        draw_texte(120, 52, self.scores, 1, 0x4B0082, True)
        draw_texte(380, 52, self.scores1, 1, 0x4B0082, True)
        

class Menu:
    def __init__(self):
        self.menu_p = Paramètres()
        self.menu_i = Informations()
        self.menu_b = Boutique()
        self.menu_s = Tableaux_scores()
        self.lancement = Lancement()
        self.menu = None
        self.pseudo = None
        
        self.changement_pseudo = Changement_pseudo()
        
        self.données = Base_donées()
        
        self.boutons = [
                        Bouton(20, 20, 3, "Play"),
                        Bouton(50, 150, 2, "Information"),
                        Bouton(170, 150, 2, "Paramètres"),
                        Bouton(290, 150, 4, "Boutique"),
                        Bouton(410, 150, 4, "Score")
                        ]
        
    def refresh_données(self):
        self.pseudo = self.données.recup_pseudo()
        self.menu_p.refresh_données()
        self.menu_b.refresh_données()
    
    def action(self):
        if self.menu_p.reset:
                self.menu = None
        if self.menu_p.changement:
            self.changement_pseudo.ecriture()
            if self.changement_pseudo.ecrit():
                self.changement_pseudo.recup()
                self.refresh_données()
                self.menu_p.changement = False
                self.menu_p.reset = False
        else:
            if self.menu_p.boutons[0].état() or self.menu_i.boutons[0].état() or self.menu_b.bouton_c.état() or self.menu_s.bouton.état():
                self.menu = None
                self.menu_p.boutons[0].desactivation()
                self.menu_i.boutons[0].desactivation()
                self.menu_b.bouton_c.desactivation()
                self.menu_s.bouton.desactivation()
            
            if self.menu == None:
                for bouton in self.boutons:
                    bouton.action()
                    if bouton.etat:
                        self.menu = bouton.type
                        bouton.desactivation()
                    
            if self.menu == "Information":
                self.menu_i.action()
            elif self.menu == "Boutique":
                self.menu_b.action()
            elif self.menu == "Paramètres":
                self.menu_p.action()
            elif self.menu == "Score":
                self.menu_s.action()
            elif self.menu == "Play":
                return self.lancement.action()
            if self.changement_pseudo == None:
                self.changement_pseudo = Changement_pseudo()
        return None
            
    def draw(self):
        draw_lignes(16)
        if self.menu_p.changement:
            self.changement_pseudo.draw()
        else:            
            if self.menu == None or self.menu == "Play":
                for bouton in self.boutons:
                    bouton.draw()
            if self.menu == "Paramètres":
                self.menu_p.draw()
            if self.menu == "Information":
                self.menu_i.draw()
            if self.menu == "Play":
                self.lancement.draw()
            if self.menu == "Boutique":
                self.menu_b.draw()
            elif self.menu == "Score":
                self.menu_s.draw()
            
            if self.pseudo != None:
                draw_texte(px.width - (len(self.pseudo) * 6) - 10, 5, self.pseudo, 1, 16, False)
            
class Lancement:
    def __init__(self):
        self.y = 0
        self.rideau = []
        self.timer = 0
        self.v_rideau = 30
    
    def action(self):
        if self.timer % self.v_rideau == 0:
            self.rideau.append(self.y)
            self.y += 16
        self.timer += 1
        
        if self.timer == 550:
            self.timer = 0
            return True
        
        return False
            
    def draw(self):
        px.mouse(False)
        for y in self.rideau:
            px.rect(0, y, px.width, 16, 16)
            
        px.pal(15, 16)            
        if self.timer >= 500:
            px.blt(px.width / 2 - 32, px.height / 2 - 16, 0, 128, 96, 64, 32, scale = 8)
        px.pal()
        
class Game_over:
    def __init__(self):
        self.données = Base_donées()
        self.timer = 0
        self.cc_alors_voilà_je_vais_écrire_qlq_chose_____mais_ptn_c_trop_chiant_de_remplacer_les_espaces_par_des_tirets_bagjusteàfarecommeçaetpourlespointsjefaisça_bacbongfini_mercijules_ = "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
        ennemi_l = (Ennemi(px.rndi(0, px.width - 80), px.height - (16 + (8 * (taille - 1))), "Distance", True), Ennemi(px.rndi(0, px.width - 50), px.height - (16 + (8 * (taille - 1))), "Sabre", True))
        self.ennemi = ennemi_l[px.rndi(0, 1)]
        self.mini_ennemi = Ennemi(-16, self.ennemi.y - 20, self.ennemi.type, True)
        self.texte = ""
        self.morceaux_texte = ("Nah", " I'd/", "win/", self.cc_alors_voilà_je_vais_écrire_qlq_chose_____mais_ptn_c_trop_chiant_de_remplacer_les_espaces_par_des_tirets_bagjusteàfarecommeçaetpourlespointsjefaisça_bacbongfini_mercijules_)
        
    def mort(self, score_actuel, Joueur, xj):
        if self.timer == 0:
            self.données.ajouter_score(score_actuel, Joueur)
        self.timer += 1
        self.ennemi.danse_e(xj)
        if self.timer > 400:
            self.mini_ennemi.x += 3
        
        
    def draw(self, x_joueur):
        self.ennemi.draw(x_joueur)
        px.blt(self.ennemi.x + 36, self.ennemi.y - 39 - (8 * (taille - 1)), 0, 128, 18, 16, 14, 12, scale = 5)
        if self.timer == 100:
            self.texte += self.morceaux_texte[0]
        if self.timer == 200:
            self.texte += self.morceaux_texte[1]
        if self.timer == 250:
            self.texte += self.morceaux_texte[2]
        if self.timer == 400:
            self.texte += self.morceaux_texte[3]
        draw_texte(self.ennemi.x + 42, self.ennemi.y - 50 - (8 * (taille - 1)), self.texte, 1, 0, True)
        px.blt(self.mini_ennemi.x, self.mini_ennemi.y - 25 - (8 * (taille - 1)), 0, self.ennemi.x_img, 16, self.mini_ennemi.width, self.mini_ennemi.width, 12)
        
class Spawn:
    def __init__(self, nb_ennemis, e_type, timer_spawn):
        self.nb_ennemis_s = nb_ennemis
        self.type = e_type
        self.ennemis = []
        self.timer_spawn = 0
        self.nb_ennemis = 0
        self.timer_e = timer_spawn
        
    def spawn(self):
        for ennemi in self.ennemis:
            if ennemi.type == self.type:
                self.nb_ennemis += 1
        
        if self.nb_ennemis < self.nb_ennemis_s:
            self.timer_spawn += 1
            if self.timer_spawn % self.timer_e == 0:
                self.ennemis.append(Ennemi(0 if px.rndi(0, 1) == 1 else px.width - (16 + (8 * taille)), px.height - (16 + (8 * (taille - 1))), self.type, True))
                self.timer_spawn = 0
        
        self.nb_ennemis = 0
        
    def action(self, perso_x):
        
        for ennemi in self.ennemis:
            ennemi.action(perso_x)
            
    def draw(self, perso_x):
        
        for ennemi in self.ennemis:
            ennemi.draw(perso_x)
        
        
class Ennemi:
    def __init__(self, x, y, type_e, spawn):
        self.x = x
        self.y = y
        self.x_img = 0
        
        if spawn:
            if type_e == "Sabre":
                self.nb_touche = 2
                self.recompense = 300 * Stats[2]
                self.width = 16
                self.vitesse = 0.5
                self.vitesse_b = 0.5
                self.alive = 1
                
            elif type_e == "Distance":
                self.nb_touche = 1
                self.recompense = 200 * Stats[2]          
                self.width = 16
                self.vitesse = 0.2
                self.vitesse_b = 0.2
                self.kunai_timer = 0
                self.alive = 1
                
        self.kunai = None
            
        self.type = type_e
        
    def repouse(self):
        self.vitesse = -1.5
        
    def chek_ult(self, xu):
        if self.x + 16 + (8 * (taille - 1)) >= xu - (16 * Stats[3]) and self.x - (8 * (taille - 1)) <= xu + (16 * Stats[3]):
            return True
        return False
        
    def danse_e(self, xj):
        x_base = 0 if self.type == "Distance" else 32
        if self.x + (self.width + (self.width/2 * (taille - 1))) >= xj - ((16 / 2) * (taille - 1)) and self.x - ((self.width / 2) * (taille - 1)) <= xj + (16 + (8 * (taille - 1))):
            self.x = px.rndi(0, px.width - 80)
        if px.frame_count % 50 < 25:
            self.x_img = x_base
        else:
            self.x_img = x_base + 16
        
    def mouvement(self, d_joueur, x_joueur):
        if abs(self.x - x_joueur) > d_joueur:
            self.x += (px.sgn(x_joueur - self.x) * self.vitesse)
        else:
            self.x -= (px.sgn(x_joueur - self.x) * self.vitesse)
        if self.x >= px.width - (16 + (8 * (taille - 1))):
            self.x = px.width - (16 + (8 * (taille - 1)))
        elif self.x <= 0:
            self.x = 0
                    
    def kunai_s(self):
        self.kunai = None
        self.kunai_timer = 0
        
    def touché(self, nb_alive):
        self.alive -= nb_alive
        
    def chek_touché(self, xj, att_charge, sens):
        if self.x + self.width + (self.width/2 * (taille - 1)) >= ((xj - (16 * taille)) if sens == -1 else (xj - (8 * (taille - 1)))) and self.x - ((self.width / 2) * (taille - 1)) <= ((xj + (32 + (16 * (taille - 1)))) if sens == 1 else (xj + (16 + (8 * (taille - 1))))):
            self.touché(att_charge)
            return True
        return False
    
    def chek_touche(self, xj):
        if self.x + (self.width + (self.width / 2 * (taille-1))) >= xj - ((16 / 2) * (taille - 1)) and self.x - ((self.width / 2) * (taille - 1)) <= xj + (16 + (8 * (taille - 1))):
            return True
        return False
        
    def touche(self):
        self.nb_touche -= 1
            
    def is_alive(self):
        if self.nb_touche == 0:
            self.alive = False
        return self.alive
            
    def action(self, x_joueur):
        if self.vitesse != self.vitesse_b:
            if px.frame_count % 5 == 0:
                self.vitesse += 0.1 * px.sgn(self.vitesse_b - self.vitesse)
        
        if self.type == "Sabre":
            self.sabre(x_joueur)
        
        elif self.type == "Distance":
            self.distance(x_joueur)
            
    def sabre(self, x_joueur):
        self.mouvement(0, x_joueur)
        if px.frame_count % 50 < 25:
            self.x_img = 32
        else:
            self.x_img = 48
    
    def distance(self, x_joueur):
        
        if px.frame_count % 50 < 25:
            self.x_img = 0
        else:
            self.x_img = 16
            
        self.kunai_timer += 1
        
        if self.kunai_timer == 700:
            self.kunai = Kunai(self.x, self.width, px.sgn(x_joueur - self.x))
        if self.kunai_timer >= 600 and self.kunai_timer < 700:
            self.x_img = 80
        else:
            self.mouvement(50, x_joueur)
            
        if self.kunai != None:
            self.kunai.mouvement()
            if self.kunai.x >= px.width or self.kunai.x <= - 50:
                self.kunai_s()
        
        
    def draw(self, x_joueur):
        px.blt(self.x, self.y, 0, self.x_img, 16, 16 * px.sgn(x_joueur - self.x), 16, 12, scale = taille)
        if self.type == "Distance":
            if self.kunai != None:
                self.kunai.draw()
                                     
class Kunai:
    def __init__(self, x_base, height, sens):
        
        self.x = x_base
        self.y = px.height - ((height * taille) / 2) - 2
        self.sens = sens
        self.width = 10
        self.recompense = 50 * Stats[2]
        self.vitesse = 0.8
    
    def mouvement(self):
        self.x += self.sens * self.vitesse
        
    def chek_touche(self, x_cible, w_cible):
        if self.x + (self.width + ((self.width/2) * (taille-1))) >= x_cible - ((w_cible/2) * (taille - 1)) and self.x - ((self.width/2) * (taille - 1)) <= x_cible + (w_cible + ((w_cible / 2) * (taille - 1))):
            return True
        return False
    
    def chek_att(self, xj, sens_j):
        if self.x + (self.width * taille) >= ((xj - (16 * taille)) if sens_j == -1 else (xj - (8 * (taille - 1)))) and self.x - ((self.width / 2) * (taille - 1)) <= xj + (((32) if sens_j == 1 else (16)) * taille):
            return True
        return False
    
    def chek_ult(self, xu):
        if self.x + 10 + (5 * (taille - 1)) >= xu - (16 * Stats[3]) and self.x - (5 * (taille - 1)) <= xu + (16 * Stats[3]):
            return True
        return False
    
    def draw(self):
        px.blt(self.x, self.y, 0, 68, 22, self.width * self.sens, 4, 12, scale = taille)
        
class Slash:
    def __init__(self, x, y, sens):
        self.x = x
        self.y = y
        self.sens = sens
        self.vitesse = 1.5
        self.touches = 2
        self.att = 2
        self.e_touchés = []
        
    def suppression(self):
        if self.touches <= 0 or self.x >= px.width or self.x <= -(16 + (8 * (taille - 1))):
            return True
        return False
        
    def mort(self, ne, et):
        self.e_touchés.remove([ne, et])
    
    def chek_touche(self, xc, wc, ok, cible = None, type_e = None):
        if ok:
            if self.x + 16 + (8 * (taille - 1)) >= xc - (wc / 2 * (taille - 1)) and self.x - (8 * (taille - 1)) <= xc + wc + (wc / 2 * (taille - 1)):
                if cible != None:
                    self.touches -= 1
                    self.e_touchés.append([cible, type_e])
                return True
        return False
    
    def mouvement(self):
        self.x += self.vitesse * self.sens
        
    def draw(self):
        px.blt(self.x, self.y, 0, 192, 48, 16 * self.sens, 16, 12, scale = taille)
        
class Mini_slash:
    def __init__(self, x, y, sens):
        self.x = x
        self.y = y
        self.sens = sens
        self.vitesse = 1.5
        self.touches = 1
        self.distance = 0
        self.distance_max = 2 if px.rndi(1, 100) <= Stats[14] else 3
        self.distance_max *= (16 * (taille - 1))
        self.att = 1
        self.e_touchés = []
        
    def suppression(self):
        if self.touches <= 0 or self.distance >= self.distance_max:
            return True
        return False
        
    def chek_touche(self, xc, wc, ok, cible = None, I = None):
        if self.x + 16 + (8 * (taille - 1)) >= xc - (wc / 2 * (taille - 1)) and self.x - (8 * (taille - 1)) <= xc + wc + (wc / 2 * (taille - 1)):
            if cible != None:
                self.touches -= 1
            return True
        return False
    
    def mouvement(self):
        self.x += self.vitesse * (-self.sens)
        self.distance += abs(self.vitesse * (-self.sens))
        
    def draw(self):
        px.blt(self.x, self.y, 0, 192, 48, 16 * (-self.sens), 16, 12, scale = taille)
        
class Perso:
    def __init__(self, x, y, vies):
        self.x = x
        self.y = y
        self.sens = 1
        self.x_img = 0
        self.y_img = 0
        
        self.vies = vies
        self.max_vies = vies
        
        self.att = False
        self.att_charge = 0
        self.att_timer = 0
        self.kunais = []
        self.slashs = []
        
        self.touche = False
        self.invincibilité = 0
        
        self.mouvement = False
        self.att_reload = 200
        self.charge_timer = 0
        self.ult_reload = - 500
        self.ult = False
        self.ult_timer = 0
        self.ult_x = 0
        self.ult_y = 0
        self.vitesse_ult_y = 0
        self.vitesse_ult_y = 0
        
    def actions(self):
        self.att_reload += 1
        self.ult_reload += 1
        for kunai in self.kunais:
            kunai.mouvement()
        for slash in self.slashs:
            slash.mouvement()
        if self.touche:
            self.invincibilité += 1
            if self.invincibilité == 300:
                self.touche = False
                self.invincibilité = 0
        else:
            self.invincibilité = 0
            
        if Stats[12]:
            if self.ult_reload >= Stats[4]:
                if px.btnp(px.KEY_UP) and not self.ult:
                    self.ult = True
                    self.ult_x = self.x
                    self.ult_y = self.y
                    self.sens = px.sgn(self.ult_cible - self.x)
                    self.y_final = px.height - (16 * Stats[3]) - 16
                    self.y_mid = px.height - ((16 * Stats[3]) + 50)
                    self.touche = False
                    
                if self.ult_timer != 0 and self.ult_timer <= 85 and self.ult:
                    self.y = self.y_mid + (abs(self.y_mid - self.y) / (86 - self.ult_timer))
                    
                elif self.ult_timer != 0 and self.ult_timer <= 170 and self.ult:
                    self.y = self.y_final - (abs(self.y_final - self.y) / (171 - self.ult_timer))
                    
                if self.ult and self.ult_timer <= 170:
                    self.vitesse_ult_x = (abs((self.ult_cible - 8) - self.x) / (171 - self.ult_timer))
                    
                if self.ult:
                    self.ult_timer += 1
                    if self.ult_timer < 170:
                        self.x += self.vitesse_ult_x * self.sens
                
                if self.ult_timer == 250:
                    self.ult = False
                    self.ult_reload = 0
                    self.x = self.ult_x
                    self.y = self.ult_y
                    self.ult_timer = 0
                                 
        
        if self.att_reload >= Stats[10]:
            if self.att_timer == 0:
                if px.btn(px.KEY_DOWN):
                    self.charge_timer += 1
                
                if self.charge_timer == Stats[7]:
                    self.att_charge = 1
                    
                if self.charge_timer == Stats[8]:
                    self.att_charge = 2
                    
                if Stats[11]:
                    if self.charge_timer == Stats[9]:
                        self.att_charge = 3
                    
                if px.btn(px.KEY_DOWN):
                    self.att = True
                    self.att_timer = 0
                else:
                    if self.att and self.att_charge != 0:
                        self.att_timer += 1
                        self.charge_timer = 0
                        if self.att_charge == 3:
                            self.slashs.append(Slash(self.x + (16 * taille * self.sens), self.y, self.sens))
                            if Stats[13]:
                                self.slashs.append(Mini_slash(self.x - (5 + (8 * (taille - 1))), self.y, self.sens))
                    else:
                        self.att = False
                        
        if self.ult:
            self.att_charge = 0
            self.att = False
            self.att_timer = 0
            
        if not self.ult:    
            if self.att_timer > 0:
                self.att_timer += 1
                if self.att_timer == 30:
                    self.att_charge = 0
                    self.att = False
                    self.att_timer = 0
                    self.att_reload = 0
            
            if self.att == False and self.ult == False:
                if px.btn(px.KEY_RIGHT):
                    if (self.x < px.width - (16 * taille)):
                        self.x += Stats[0]
                        self.mouvement = True
                        self.sens = 1
                elif px.btn(px.KEY_LEFT):
                    if (self.x > 0):
                        self.x -= Stats[0]
                        self.sens = -1
                        self.mouvement = True
                else:
                    self.mouvement = False
            else:
                self.mouvement = False
            
        if self.ult and self.ult_timer <= 55:
            self.x_img = 224
            self.y_img = 0
        elif self.ult and self.ult_timer <= 115:
            self.x_img = 224
            self.y_img = 32
        elif self.ult and self.ult_timer <= 170:
            self.x_img = 224
            self.y_img = 16
        elif self.ult and self.ult_timer <= 250:
            self.x_img = 224
            self.y_img = 48
        elif self.mouvement:
            if px.frame_count % 50 < 25:
                self.x_img = 32
                self.y_img = 0
            else:
                self.x_img = 48
                self.y_img = 0
        elif self.att and self.att_timer == 0:
            if self.att_charge == 3:
                self.x_img = 208
                self.y_img = 48
            elif self.att_charge == 2:
                self.x_img = 128
                self.y_img = 0
            elif self.att_charge == 1:
                self.x_img = 96
                self.y_img = 16
            else:
                self.x_img = 96
                self.y_img = 0
        elif self.att:
            self.x_img = 64
            self.y_img = 0
        else:
            if px.frame_count % 50 < 25:
                self.x_img = 0
                self.y_img = 0
            else:
                self.x_img = 16
                self.y_img = 0
                
    def ennemi_proche(self, ex):
        if ex != None:
            self.ult_cible = ex
            
    def touché(self):
        if px.rndi(0, 100) <= Stats[6]:
            return True
        else:
            self.vies -= 1
            self.touche = True
            return False

    def draw(self):        
        for i in range(0, self.max_vies):
            px.blt(px.width - (21 +(16 * i)), 5, 0, 112, 32, 16, 16, 12)
        
        for i in range(0, self.vies):
            px.blt(px.width - (21 +(16 * i)), 5, 0, 96, 32, 16, 16, 12)
            
        if self.ult and self.ult_timer >= 170:
            px.blt(self.x + (8 * taille) if self.sens == 1 else self.x - (8 * taille), self.y + (8 * taille), 0, self.x_img + 8, self.y_img + 8, 16 * self.sens, 16, 12, scale = taille)
            px.blt(self.ult_cible - 16, px.height - (16 + (8 * (Stats[3] - 1))), 0, 192, 32, 32, 16, 12, scale = Stats[3])
        elif self.ult and self.ult_timer > 0:
            px.blt(self.ult_x, self.ult_y, 0, 0, 0, 16 * self.sens, 16, 12, scale = taille)
            
        if self.touche:
            if px.frame_count % 26 < 13:
                px.blt(self.x, self.y, 0, self.x_img, self.y_img, 16 * self.sens, 16, 12, scale = taille)
        else:
            px.blt(self.x, self.y, 0, self.x_img, self.y_img, 16 * self.sens, 16, 12, scale = taille)
            
        if self.att and self.att_timer != 0:
            px.blt(self.x + (16 * taille * self.sens), self.y, 0, 80, 0, 16 * self.sens, 16, 12, scale = taille)
            
        for slash in self.slashs:
            slash.draw()
            
        for kunai in self.kunais:
            kunai.draw()
            
def draw_texte(x, y, texte, scale, couleur, retour_m = False):
    x += 3 * (scale - 1)
    y += 4.5 * (scale - 1)
    px_colors = px.colors.to_list()
    colors_px = (i for i in range(len(px_colors)))
    majuscule = ("A", "B", "C", "D", "E", "F", "G", "H", "I",
                "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                "S", "T", "U", "V", "W", "X", "Y", "Z"
                )
    minuscule = ("a", "b", "c", "d", "e", "f", "g", "h", "i",
                "j", "k", "l", "m", "n", "o", "p", "q", "r",
                "s", "t", "u", "v", "w", "x", "y", "z"
                )
    
    caractères_spé = ("é", "è", "à", "ê", "ù", "-", "'", ".", "!", "?", ":", "_", "(", ")", "%", "=", ",", "ç", ";")
    
    chiffres = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    
    if couleur in colors_px:
        px.pal(7, couleur)
    else:
        if couleur not in px_colors:
            nb_color = len(px_colors)
            px_colors.append(couleur)
        else:
            nb_color = px_colors.index(couleur)
        px.colors.from_list(px_colors)
        px.pal(7, nb_color)
        
    retours = []
    chaine = list(texte)
    
    for c in range(len(chaine)):
        if ord(chaine[c]) == 47:
            retours.append(c)
            
    base_x = x
    base_y = y
    for i in range(len(chaine)):
        img_x = 32
        img_y = 0
        y = base_y
        if retour_m:
            if i == 0:
                if len(retours) == 0:
                    x -= ((len(chaine) * 6) * scale) / 2
                else:
                    x -= (((retours[0] - 1) * 6) * scale) / 2
        if i in retours:
            if retour_m:
                if len(retours) == 1:
                    x -= ((len(chaine) * 6) * scale) / 2
                elif i != retours[-1]:
                    x = base_x
                    x -= (((retours[retours.index(i) + 1] - i) * 6) * scale) / 2
                else:
                    x = base_x
                    x -= (((len(chaine) - i) * 6) * scale) / 2
            else:
                x = base_x
            if i != 0:
                base_y += 12 * scale
                
        
        if chaine[i] in caractères_spé:
            img_x = 17
            img_y = caractères_spé.index(chaine[i]) * 8
            if img_y >= 120:
                y += 3
                img_y += 3                    
        elif chaine[i] in chiffres:
            img_x = 25
            img_y = chiffres.index(chaine[i]) * 8
        elif chaine[i] in majuscule:
            img_x = 1
            img_y = majuscule.index(chaine[i]) * 8
            
        elif chaine[i] in minuscule:
            img_x = 9
            img_y = minuscule.index(chaine[i]) * 8 + 2
            y += 2
            
        px.blt(x, y, 2, img_x, img_y, 5 if chaine[i] != "%" else 7, 8, 0, scale = scale)
        
        
        x += 6 * scale if chaine[i] != "%" else 8 * scale
        
    px.pal()
    
def draw_lignes(taille, arrivée = None, depart = 0):
    if arrivée == None:
        arrivée = px.height
    y_L1 = - taille
    y_L2 = 0
    while y_L1 < arrivée:
        px.rect(depart, y_L1, px.width, taille, 9)
        px.rect(depart, y_L2, px.width, taille, 10)
        y_L1 += taille * 2
        y_L2 += taille * 2

App(256, 512, "Kenji Battle V0.5", 100)