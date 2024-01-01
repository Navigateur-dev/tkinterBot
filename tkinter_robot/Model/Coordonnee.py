class Coordonnee:
    def __init__(self, x= None, y= None):
        self.x = x
        self.y = y
    def __construct__(self, x, y):
        self.x = x 
        self.y = y
    def getAbscisse(self):
        return self.x
    def setAbscisse(self, x):
        self.x = x 
    def getOrdonnee(self):
        return self.y
    def setOrdonnee(self, y):
        self.y = y