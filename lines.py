"""Dieses Programm enthält Klassen und Funktionen, die aus gem_pi_rate.py, bzw. gem_pi_rate_taster.py,
	ausgelagert wurden. 

    Es wurde im Rahmen des Kurzversuchs 'KV8 - Elektronische Steuerung mit Python unter Linux',
    im Fortgeschrittenen-Praktikum Physik an der UHH geschaffen.

    2022, Riek Rüstemeier, Noah Tettenborn
"""
import pyglet
import numpy as np
import constants
import math

MAX_LAENGE = constants.MAX_LAENGE
ABSTAND_UMRANDUNG = constants.ABSTAND_UMRANDUNG
ZAHL_LINES = constants.ZAHL_LINES
HOEHE = constants.HOEHE
BREITE = constants.BREITE
MIN_DIST = constants.MIN_DIST

class Line(pyglet.shapes.Line):
    """Linie, die als Hindernis für den Spieler dient.

    Args:
        pyglet.shapes.Line (class): Superklasse, die Eigenschaften vererbt
    """
    def __init__(self, *args, **kwargs):
    	super().__init__(*args, **kwargs)

    def abstand(self, x, y):
    	"""Berechnet den kürzesten Abstand zwischen einem Punkt (x, y) und der Linie. Dazu werden x und y zunächst in
			ein geeignetes Koordinatensystem transformiert, um die Berechnung zu vereinfachen.
		
		Args:
			x (float): x-Koordinate des Punktes
			y (float): y-Koordinate des Punktes
		Returns: 	
			float: Abstand zwischen Punkt und Linie
		"""
    	p, q = self.transform_positions(x, y)
    	#Länge der Linie:
    	l = distance((self.x, self.y), (self.x2, self.y2)) 
    	if p < 0:
    		return distance((p, q))
    	elif 0 <= p <= l:
    		return abs(q)
    	elif p > l:
    		return distance((p, q), (l, 0))

    def transformationmatrix(self):
    	"""Berechnet die Transformationsmatrix einer Koordinatentransformation, bei der eine Achse parallel und die
			andere senkrecht zur Linie ausgerichtet wird. Der Koordinatenursprung bleibt beim Anfangspunkt der Linie.
			
		Returns:
			 (np.ndarray): Transformationsmatrix
		"""
    	if self.x == self.x2:
    		if (self.y2 - self.y) > 0:
    			phi = np.pi / 2
    		else:
    			phi = - np.pi / 2
    	else:
    		phi = np.arctan((self.y2 - self.y) / (self.x2 - self.x))
    	if self.x2 < self.x:
    		phi += np.pi
    	return np.array([[np.cos(phi), np.sin(phi)], [-np.sin(phi), np.cos(phi)]])

    def transform_positions(self, x, y):
    	"""Führt eine Koordinatentransformation von Ortskoordinaten durch, bei der eine Achse parallel und die
			andere senkrecht zur Linie ausgerichtet wird. Der Koordinatenursprung wird auf den Anfangspunkt der
			Linie gesetzt.
			
		Args:
			x (float): x-Koordinate des zu transformierenden Punktes
			y (float): y-Koordinate des zu transformierenden Punktes

		Returns: 	
			float: p-Koordinate des transformierten Punktes (die p-Achse liegt parallel zur Linie)
			float: q-Koordinate des transformierten Punktes (die q-Achse liegt senkrecht zur Linie)
		"""
    	x -= self.x
    	y -= self.y
    	p, q = np.matmul(self.transformationmatrix(), [x, y])
    	return p, q

    def transform_velocities(self, v_x, v_y):
    	"""Führt eine Koordinatentransformation von Geschwindigkeitskomponenten durch, bei der eine Achse parallel
			und die andere senkrecht zur Linie ausgerichtet wird. Der Koordinatenursprung bleibt unverändert.
			
		Args:
			v_x (float): x-Komponente der zu transformierenden Geschwindigkeit
			v_y (float): y-Komponente der zu transformierenden Geschwindigkeit

		Returns: 	
			float: p-Komponente der transformierten Geschwindigkeit (die p-Achse liegt parallel zur Linie)
			float: q-Komponente der transformierten Geschwindigkeit (die q-Achse liegt senkrecht zur Linie)
		"""
    	v_p, v_q = np.matmul(self.transformationmatrix(), [v_x, v_y])
    	return v_p, v_q

    def retransform_velocities(self, v_p, v_q):
    	"""Rücktransformation zu transform_velocities.

		Args:
			v_p (float): p-Komponente der zu transformierenden Geschwindigkeit (die p-Achse liegt parallel zur Linie)
			v_q (float): q-Komponente der zu transformierenden Geschwindigkeit (die q-Achse liegt senkrecht zur Linie)

		Returns: 	
			float: x-Komponente der transformierten Geschwindigkeit
			float: y-Komponente der transformierten Geschwindigkeit
		"""
    	v_x, v_y = np.matmul(self.transformationmatrix().transpose(), [v_p, v_q])
    	return v_x, v_y

    def update(self, player_obj):
    	"""Prüft, der Spieler der Linie zu nahe kommt. Falls das der Fall ist, wird die Geschwindigkeit des Spielers
			so verändert, dass dieser nicht die Linie durchfliegt.
			
		Args:
			player_obj (objekt): Spielerobjekt
		"""
    	v_p, v_q = self.transform_velocities(player_obj.velocity_x, player_obj.velocity_y)
    	p, q = self.transform_positions(player_obj.position[0], player_obj.position[1])
    	if self.abstand(player_obj.position[0], player_obj.position[1]) <= MIN_DIST:
    		if q * v_q < 0:
    			v_q = -v_q
    			player_obj.velocity_x, player_obj.velocity_y = self.retransform_velocities(v_p, v_q)


def line_generator():
	"""Erzeugt die Linien zu Spielbeginn. Dabei werden vier Linien als Umrandung des Spielfeldes verwendet und
		die anderen werden zufällig verteilt mit zufälligen Längen.

	Returns: 	
		np.ndarray: Endpunkte aller Linien, jeweils x- und y-Koordinate von Anfangs- und Endpunkt
		batch: Batch mit allen Linien-Objekten
		list: Liste mit allen Linien-Objekten
	"""
	line_batch = pyglet.graphics.Batch()
	line_list = []
	endpunkte = np.empty((ZAHL_LINES + 4, 4)) #x1, y1, x2, y2
	
	endpunkte[0,] = ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG, HOEHE - 4 * ABSTAND_UMRANDUNG
	endpunkte[1,] = ABSTAND_UMRANDUNG, HOEHE - 4 * ABSTAND_UMRANDUNG, BREITE - ABSTAND_UMRANDUNG, HOEHE - 4 * ABSTAND_UMRANDUNG
	endpunkte[2,] = BREITE - ABSTAND_UMRANDUNG, HOEHE - 4 * ABSTAND_UMRANDUNG, BREITE - ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG
	endpunkte[3,] = BREITE - ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG, ABSTAND_UMRANDUNG
	
	for i in range(ZAHL_LINES):
		endpunkte[i + 4, 0] = ABSTAND_UMRANDUNG + (BREITE - 2 * ABSTAND_UMRANDUNG) * np.random.rand() 
		endpunkte[i + 4, 1] = ABSTAND_UMRANDUNG + (HOEHE - 2 * ABSTAND_UMRANDUNG) * np.random.rand()
		endpunkte[i + 4, 2] = endpunkte[i + 4, 0] + MAX_LAENGE * (np.random.rand() - 0.5)
		endpunkte[i + 4, 3] = endpunkte[i + 4, 1] + MAX_LAENGE * (np.random.rand() - 0.5)

	for i in range(ZAHL_LINES + 4):
		line_list.append(Line(endpunkte[i, 0], endpunkte[i, 1], endpunkte[i, 2], endpunkte[i, 3], color =(0,0,0), width=5, batch=line_batch))

	return endpunkte, line_batch, line_list


def distance(p_1 =(0, 0), p_2 = (0, 0)):
    """Abstand zwischen zwei Punkten in einer Ebene

    Args:
        p_1 (tuple, optional): Punkt 1. Defaults to (0, 0).
        p_2 (tuple, optional): Punkt 2. Defaults to (0, 0).

    Returns:
        float: Abstand zwischen p_1 und p_2
    """
    return math.sqrt((p_1[0]-p_2[0]) ** 2 + (p_1[1] - p_2[1]) ** 2)