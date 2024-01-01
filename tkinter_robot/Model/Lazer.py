from Model.Coordonnee import Coordonnee
class Lazer :
    def __init__(self, nom=None, coordonneeInitial = Coordonnee(None,None), coordonneeFinal = Coordonnee(None, None), angle = None):
        self.nom = nom
        self.coordonneeInitial = coordonneeInitial
        self.coordonneeFinal = coordonneeFinal
        self.angle = angle

    def getNom(self):
        return self.nom
    def getCoordonneeInitial(self):
        return self.coordonneeInitial
    def getCoordonneeFinal(self):
        return self.coordonneeFinal
    def getAngle(self):
        return self.angle
    
    def setNom(self,nom):
        self.nom = nom
    def setCoordonneeInitial(self,coordonneeInitial):
        self.coordonneeInitial = coordonneeInitial
    def setCoordonneeFinal(self, coordonneeFinal):
        self.coordonneeFinal = coordonneeFinal
    def setAngle(self, angle):
        self.angle = angle
        
        
        
