"""Dieses Programm ist ein Spiel, bei dem man als Pirat Diamanten einsammeln muss.

    Es wurde im Rahmen des Kurzversuchs 'KV8 - Elektronische Steuerung mit Python unter Linux',
    im Fortgeschrittenen-Praktikum Physik an der UHH geschaffen. Diese Version ist mit
    der Tastatur zu steuern. Um das Spiel mit den GPIO-Tastern zu steuern muss die Version
    'gem_pi_rate_taster.py' verwendet werden.

    2022, Riek Rüstemeier, Noah Tettenborn
"""
from logging.config import listen
import math
import time
from functools import partial
import numpy as np
import pyglet
import lines
import constants

# Fenstergröße
BREITE = constants.BREITE
HOEHE = constants.HOEHE
ABSTAND_UMRANDUNG = constants.ABSTAND_UMRANDUNG
PLAYER_IMG = pyglet.image.load("pirate.png")
PLAYER_IMG.anchor_x = PLAYER_IMG.width // 2
PLAYER_IMG.anchor_y = PLAYER_IMG.height // 3
GEM_IMG = pyglet.image.load("gem.png")
GEM_IMG.anchor_x = GEM_IMG.width // 2
GEM_IMG.anchor_x = GEM_IMG.width // 2
MIN_DIST = constants.MIN_DIST

ZAHL_GEMS = constants.ZAHL_GEMS
SCHRIFTFARBE = constants.schriftfarbe

class PiRateWindow(pyglet.window.Window):
    """Fenster, dass alle weiteren Objekte enthält und als einziges im 'Main'-Teil instanziert wird.

    Args:
        pyglet (_type_): Superklasse, dessen Eigenschaften vererbt werden
    """
    def __init__(self, breite=BREITE, hoehe=HOEHE):
        super().__init__(breite, hoehe, "Gem Pi-Rate")
        self.start()

    def start(self):
        """Instanziert alle Attribut-Objekte von PiRateWindow und definiert diverse Variablen.
        """
        self.gem_score = 0
        self.time_score = 0
        self.highscore = lade_highscore()
        self.time = time.time()
        self.time_remaining = 20

        self.hintergrund = pyglet.shapes.Rectangle(ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG,
                                                   BREITE - 2 * ABSTAND_UMRANDUNG,
                                                   HOEHE - 5 * ABSTAND_UMRANDUNG,
                                                   color=(255, 248, 220))

        self.spieler = Spieler(PLAYER_IMG, BREITE/2, HOEHE/2)

        endpunkte, self.linebatch, self.line_list = lines.line_generator()

        self.gemlist, self.gembatch = gem_generator(ZAHL_GEMS, endpunkte)

        self.punktestand = pyglet.text.Label(
            text='Hello, world', color=SCHRIFTFARBE, font_name="Arial", font_size=25,
            bold=True, x=self.width // 2, y=1.9 * self.height // 2, anchor_x="center",
            anchor_y="center")
        self.nochmal_button = pyglet.text.Label(
            text='Nochmal', color=SCHRIFTFARBE, font_name="Arial", font_size=25, bold=True,
            x=self.width // 2 - 300, y=self.height // 2 - 200, anchor_x="center",
            anchor_y="center")
        self.weiter_button = pyglet.text.Label(
            text='Weiter spielen', color=SCHRIFTFARBE,
            font_name="Arial", font_size=25, bold=True, x=self.width // 2,
            y=self.height // 2 - 200, anchor_x="center", anchor_y="center")
        self.exit_button = pyglet.text.Label(
            text='Spiel beenden', color=SCHRIFTFARBE,
            font_name="Arial", font_size=25, bold=True, x=self.width // 2 + 300,
            y=self.height // 2 - 200, anchor_x="center", anchor_y="center")
        self.ergebnis_anzeige = pyglet.text.Label(
            text='Game over! Du hast {} Diamanten eingesammelt.'.format(self.gem_score),
            color=SCHRIFTFARBE, font_name="Arial", font_size=25, bold=True,
            x=self.width // 2, y=self.height // 2, anchor_x="center", anchor_y="center")

    def on_draw(self):
        """Wird in jedem Frame aufgerufen und aktualisiert die Darstellung der
            Objekte im Fenster.
        """
        self.clear()
        if self.time_remaining > 0 and self.gem_score != ZAHL_GEMS:
            self.hintergrund.draw()
            self.linebatch.draw()
            self.gembatch.draw()
            self.spieler.draw()
            self.punktestand.draw()
        else:
            self.nochmal_button.draw()
            if self.gem_score != ZAHL_GEMS:
                self.weiter_button.draw()
            self.exit_button.draw()
            self.ergebnis_anzeige.draw()

    def on_key_press(self, button, modifiers):
        """Wird aufgerufen, wenn Tastatur-button gedrückt wird und aktualisiert Geschwindigkeit
            von Spieler

        Args:
            button (int): Der button der Gedrückt wurde
            modifiers (_type_): _description_
        """
        if button == 65361:
            self.spieler.velocity_x -= 50
        elif button == 65362:
            self.spieler.velocity_y += 50
        elif button == 65363:
            self.spieler.velocity_x += 50
        elif button == 65364:
            self.spieler.velocity_y -= 50

    def on_mouse_motion(self, x, y, dx, dy):
        """Wird bei Mausbewegung aufgerufen. Aktualisiert gegebenenfalls die Farbe von Buttons
            beim darüber hovern

        Args:
            x (int): x-Koordinate des Mauszeigers im Fenster
            y (int): y-Koordinate des Mauszeigers im Fenster
            dx (int): dump
            dy (int): dump
        """
        if self.time_remaining <= 0 or self.gem_score == ZAHL_GEMS:
            if self.nochmal_button.position[0] - 85 < x < self.nochmal_button.position[0] + 85 and \
                self.nochmal_button.position[1] - 12 < y < self.nochmal_button.position[1] + 12:
                self.nochmal_button.color = (0, 238, 238, 255)
            else:
                self.nochmal_button.color = SCHRIFTFARBE
            if self.gem_score != ZAHL_GEMS:
                if self.weiter_button.position[0] - 115 < x < self.weiter_button.position[0] + 115 and \
                    self.weiter_button.position[1] - 12 < y < self.weiter_button.position[1] + 12:
                    self.weiter_button.color = (0, 238, 238, 255)
                else:
                    self.weiter_button.color = SCHRIFTFARBE
            if self.exit_button.position[0] - 120 < x < self.exit_button.position[0] + 120 and \
                self.exit_button.position[1] - 12 < y < self.exit_button.position[1] + 12:
                self.exit_button.color = (0, 238, 238, 255)
            else:
                self.exit_button.color = SCHRIFTFARBE

    def on_mouse_press(self, x, y, button, modifiers):
        """Wird bei Maustatastenbetätigung aufgerufen. Ermöglicht interaktion mit Buttons am
            Ende des Spiels.

        Args:
            x (int): X-Koordinate der Maus im Fenster
            y (int): Y-Koordinate der Maus im Fenster
            button (int): Gedrückte Taste
            modifiers (_type_): _description_
        """
        if self.time_remaining <= 0 or self.gem_score == ZAHL_GEMS:
            if self.nochmal_button.position[0] - 85 < x < self.nochmal_button.position[0] + 85:
                if self.nochmal_button.position[1] - 12 < y < self.nochmal_button.position[1] + 12:
                    self.start()
            if self.gem_score != ZAHL_GEMS:
                if self.weiter_button.position[0] - 115 < x < self.weiter_button.position[0] + 115:
                    if self.weiter_button.position[1] - 12 < y < self.weiter_button.position[1] + 12:
                        self.time = time.time()
                        self.time_score += 20
            if self.exit_button.position[0] - 120 < x < self.exit_button.position[0] + 120:
                if self.exit_button.position[1] - 12 < y < self.exit_button.position[1] + 12:
                    self.close()

    def update(self, dt):
        """Wird jeden Frame Aufgerufen. Aktualisiert Verhalten von Spieler, Gems
            und Textanzeigen.

        Args:
            dt (float): intern, Länge eines Frames
        """
        self.time_remaining = 20 - time.time() + self.time
        if self.time_remaining > 0 and self.gem_score != ZAHL_GEMS:
            self.spieler.update(dt)
            for gem in self.gemlist:
                if self.gem_score == ZAHL_GEMS - 1 and gem.update(self.spieler):
                    self.time_score += time.time() - self.time
                    self.gem_score += 1
                self.gem_score += gem.update(self.spieler)
            self.punktestand.text = ("Du hast schon {} Diamanten eingesammelt und noch "
                                     "{:.1f} Sekunden".format(self.gem_score, self.time_remaining))
            for i in range(len(self.line_list)):
                self.line_list[i].update(self.spieler)
        elif self.gem_score == ZAHL_GEMS:
            if self.time_score > self.highscore:
                self.ergebnis_anzeige.text = ("Du hast alle Diamanten in {:.3f} s eingesammelt."
                                              .format(self.time_score))
            else:
                self.ergebnis_anzeige.text = ("Neuer Highscore! Du hast alle Diamanten in {:.3f} s"
                                              " eingesammelt.".format(self.time_score))
                if self.highscore != self.time_score:
                    speicher_highscore(self.time_score)
                    self.highscore = self.time_score
        else:
            self.ergebnis_anzeige.text = ('Game over! Du hast {} Diamanten eingesammelt.'
                                          .format(self.gem_score))

class Spieler(pyglet.sprite.Sprite):
    """Bewegbarer Spieler, wird im Window instanziert.

    Args:
        pyglet.sprite.Sprite (class): Superklasse, die Eigenschaften vererbt
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity_x, self.velocity_y = 0, 0
        self.scale = 0.5

    def update(self, dt):
        """Aktualisiert Position und Geschwindigekeit von Spieler

        Args:
            dt (float): Intern, Länge des Zeitschritts
        """
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_x = self.velocity_x * 0.993
        self.velocity_y = self.velocity_y * 0.993

class Gem(pyglet.sprite.Sprite):
    """Diamant, der vom Spieler eingesammelt werden kann.

    Args:
        pyglet (class): Superklasse, die Eigenschaften vererbt
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.absorbed = False
        self.scale = 0.1

    def update(self, player_obj):
        """Aktualisiert einzelne Gems. Werden entfernt, wenn vom Spieler eingesammelt.

        Args:
            player_obj (object): Spielerobjekt, dessen Nähe zum Gem überprüft wird

        Returns:
            int: Ob der Gem eingesammelt wurde oder nicht. Wird zum erhöhen des Scores verwendet
        """
        dist_to_player = distance(self.position, player_obj.position)
        if dist_to_player < 70 and not self.absorbed:
            self.absorbed = True
            self.visible = False
            return 1
        return 0

def gem_generator(num_gem: int, wall_vertices: list, img=GEM_IMG)->list:
    """Erzeugt die Gems zu spielbeginn, an zufälligen positionen(nicht an den Wänden)

    Args:
        num_gen (int): Anzahl der anfangs zu erzeugenden Gems
        wall_vertices (np.ndarray): Vertizes der Wandsegmente

    Returns:
        list: Liste mit den Gem-Objekten, die zum spielstart erzeugt werden.
        batch: Batch mit allen Gem-Objekten
    """

    def is_viable(position: np.ndarray, zeile: np.ndarray, min: int):
        """Prüft, ob position außerhalb des durch die in Zeile enthaltenen Eckpunkte definierten
            rechtecks liegt, und wenn nicht, ob ein mindestabstand zur verbindungslinie gegeben ist

        Args:
            position (np.ndarray): zu bewertende Position
            zeile (np.ndarray): Eckpunkte der Linie. x_1, y_1, x_2, y_2
            min (int): Mindestabstand, der eingehalten werden sol
        """
        x, y = position
        x_1, y_1, x_2, y_2 = zeile
        if (
                x < x_1 and x < x_2 or
                x < x_1 and x < x_2 or
                y < y_1 and y < y_2 or
                y > y_1 and y > y_2):

            viable = True
        else:
            b = (y_2 - y_1) / (x_2 - x_1)
            a = y_1 - b * x_1
            viable = y - b * x < a - min or y - b * x > a + min
        return viable

    gem_list = []
    gem_batch = pyglet.graphics.Batch()
    rand_pos = np.random.randint(50, (BREITE - 50, HOEHE - 80), size=(200, 2))
    num_generated = 0
    i = 0
    while num_generated < num_gem:
        viable = True
        for row in wall_vertices[4:]:
            if not is_viable(rand_pos[i], row, min=MIN_DIST + 30):
                viable = False
                print("Diese Position wurde verworfen: {}".format(rand_pos[i]))
                break
        if viable:
            pos_x, pos_y = rand_pos[i]
            gem_list.append(Gem(img, x=pos_x, y=pos_y, batch=gem_batch))
            num_generated += 1
        i += 1
    return gem_list, gem_batch

def lade_highscore():
    """Lädt den Highscore aus der Datei highscore.txt

    Returns:
        float: Highscore
    """
    highscore_datei = open('highscore.txt', 'a+')
    highscore_datei.seek(0)
    highscore = highscore_datei.read()
    highscore_datei.close()
    if highscore == "":
        highscore = 20
    highscore = float(highscore)
    return highscore

def speicher_highscore(highscore):
    """Speicher den Highscore in highscore.txt

    Args:
        highscore (float): Zu speichernder highscore
    """
    highscore_datei = open('highscore.txt', 'w')
    highscore_datei.write(str(highscore))
    highscore_datei.close()

def general_update(dt, obj):
    """Allgemeine Updatefunktion mit variablen Update-Objekt. Die Update Funktion für Pyglet darf
        nur einen Parameter annehmen.

    Args:
        dt (float): Länge des Zeitschritts
        obj (object): Objekt mit Update-Methode
    """
    obj.update(dt)

def distance(p_1=(0, 0), p_2=(0, 0)):
    """Abstand zwischen zwei Punkten in einer Ebene

    Args:
        p_1 (tuple, optional): Punkt 1. Defaults to (0, 0).
        p_2 (tuple, optional): Punkt 2. Defaults to (0, 0).

    Returns:
        float: Abstand zwischen p_1 und p_2
    """
    return math.sqrt((p_1[0] - p_2[0]) ** 2 + (p_1[1] - p_2[1]) ** 2)

if __name__ == "__main__":
    WINDOW = PiRateWindow()
    UPDATE = partial(general_update, obj=WINDOW)
    pyglet.clock.schedule_interval(UPDATE, 1.0/40)
    pyglet.app.run()
