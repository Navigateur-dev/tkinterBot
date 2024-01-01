from Model.Coordonnee import Coordonnee
import math
class Robot:
    def __init__(self, name = None, taille = 10, vitesse= 1 , couleur= "red", coordonnee= Coordonnee(), trajectoire= 0): 
        self.name = name
        self.taille = taille
        self.vitesse = vitesse
        self.couleur = couleur
        self.coordonnee = coordonnee
        self.trajectoire= trajectoire
    
    def getName(self):
        return self.name
    def setName(self, name):
        self.name = name

    def getTaille(self):
        return self.taille
    def setTaille(self, taille):
        self.taille = taille
    def getVitesse(self):
        return self.vitesse
    def setVitesse(self, vitesse):
        self.vitesse = vitesse

    def getCouleur(self):
        return self.couleur
    def setCouleur(self, couleur):
        self.couleur = couleur
        
    def getCoordonnee(self):
        return self.coordonnee
    def setCoordonnee(self, coordonnee):
        self.coordonnee = coordonnee
    
    def getTrajectoire(self):
        return self.trajectoire
    def setTrajectoire(self, trajectoire):
        # trajectoire = self.radians_to_degrees(trajectoire)
        self.trajectoire = trajectoire
    
    

