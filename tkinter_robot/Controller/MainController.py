from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import random
from PIL import Image, ImageTk
import math, os
import threading
import time
from Model.Map import Map
from Model.Robot import Robot
from Model.Coordonnee import Coordonnee
from View.MainView import MainView
from Model.Lazer import Lazer
import os


class MainController:
    def __init__(self):
        self.root_directory = os.path.dirname(os.path.abspath(__file__))

        self.root = Tk()
        self.carte = Map()
        self.coordonnee = Coordonnee()
        self.robot = Robot(name="bot1")
        self.lazer = Lazer()
        self.nbLazer = 20
        self.espacement = 8
        self.lidarGroup = []
        self.auto_movement_active = False
        self.view = MainView(self)
        self.time = time.time()
        self.efficiency = 0.0
        self.visited_coordinates = set()
    #Fonction de convertion
    def radians_to_degrees(self,radians):
        degrees = (radians * (180 / math.pi)) % 360
        return degrees
    #Active la navigation autonome 
    def toggle_automation(self):
        self.auto_movement_active = not self.auto_movement_active
        if self.auto_movement_active:
            # Si l'automatisation est activée, démarrez la fonction moveAuto dans un thread
            threading.Thread(target=self.move_auto_loop).start()
            
    #Permet d'activer la naviagation autonome
    def move_auto_loop(self):
        # Fonction pour lancer la fonction moveAuto à intervalles réguliers
        while self.auto_movement_active:
            self.moveAuto()
            time.sleep(2)  # Attendre une seconde entre chaque itération
    #Action de placement du robot
    def clicSouris(self, event):
        if self.carte.getPath() != "" and self.view.verifTag(self.robot.getName()) == False : 
            x, y = event.x, event.y
            newCoordonnee = Coordonnee(x, y)
            self.robot.setCoordonnee(newCoordonnee)
            self.placerRobot()
            if self.view.verifTag(self.robot.getName()) == False : 
                self.view.show_popup('Erreur', "Le robot est déjà présent ! ")
                
        else:
            self.view.show_popup('Erreur', "Impossible de placer le robot en dehors d'un environnement. ")
    #Action de positionnement de la trajectoire GAUCHE     
    def pivotGauche(self, event):
        if self.view.verifTag(self.robot.getName()):
            trajectoire = self.robot.getTrajectoire() + 5
            self.robot.setTrajectoire(trajectoire)
            self.view.deleteRobot()
            self.updateRobot()
    #Action de positionnement de la trajectoire DROITE     
    def pivotDroite(self, event):
        if self.view.verifTag(self.robot.getName()):
            trajectoire = self.robot.getTrajectoire() - 5
            self.robot.setTrajectoire(trajectoire)
            self.view.deleteRobot()
            self.updateRobot()
    #Déplacement simple du robot
    def move(self, robot, distance):
        vitesse = robot.getVitesse()
        trajectoire = math.radians(robot.getTrajectoire())
        xRobot = robot.getCoordonnee().getAbscisse()
        yRobot = robot.getCoordonnee().getOrdonnee()

        xRobot += distance * math.cos(trajectoire)
        yRobot -= distance * math.sin(trajectoire)
        self.placerRobot()
        robot.setCoordonnee(Coordonnee(xRobot, yRobot))

        # Mise à jour de l'angle en fonction de la distance parcourue et de la vitesse
        trajectoire = (trajectoire + distance / vitesse) % (2 * math.pi)

        if self.view.telemetrieIsActif :
            self.view.dessineLazer()
        else : 
            self.view.effacerLazer()
        self.updateEfficiency()
    #Déplacement automatique avec strategie de déplacement
    def moveAuto(self):
            while self.auto_movement_active:

                # Fonction qui contrôle la distance entre le robot et l'obstacle
                analyse_result = self.analyseZone(1)
                
                if analyse_result and self.view.verifPlacement(self.robot.getTaille(), self.robot.getCoordonnee()):
                    # Si pas d'obstacle on appelle move
                    self.move(self.robot, 9)
                else :
                    rdm = random.randrange(1,180)
                    newTrajectoire = self.robot.getTrajectoire() + rdm
                    self.robot.setTrajectoire(newTrajectoire)
                    self.placerRobot()
                if self.view.verifPlacement(self.robot.getTaille(), self.robot.getCoordonnee()) == False : 
                    self.move(self.robot, -10)

    #Création du robot sur la carte
    def placerRobot(self):
        if(self.view.verifPlacement(self.robot.getTaille(), self.robot.getCoordonnee())):
            
            robotCoordonnee = self.robot.getCoordonnee()
            
            if robotCoordonnee is not None:
                self.view.deleteRobot()
                self.view.placerPoint()
                self.initiationLazer(self.nbLazer, self.espacement)#Paramétrage des faisceaux
                
            else :                 
                print("Le robot n'a pas de coordonnée")
        else : 
            print("Vous êtes dans une zone non blanche")  
    #Mise à jour des paramètre du robot et l'affiche sur la carte
    def updateRobot(self): 
        self.view.placerPoint()
        self.initiationLazer(self.nbLazer, self.espacement)
        if self.view.minimap_active:
            self.view.updateMinimap()
    #Fonction de vérification d'obstacle pour éviter de placer les robots dans de mauvaises zones
    def verifObstacle(self, x, y, trajectoire):
        image = Image.open(self.carte.getPath())
        trajectoire_radian = math.radians(trajectoire)

        while 0 <= x < image.width and 0 <= y < image.height:
            pixel = image.getpixel((int(x), int(y)))
            if pixel != (255, 255, 255):  # Tout ce qui est non blanc
                break

            x += math.cos(trajectoire_radian)
            y -= math.sin(trajectoire_radian)

        return x, y
    
    #Initialise les lasers en fonction du nombre de faisceau et son degré d'espacement    
    def initiationLazer(self, nbLazer, degreeEspacement):
        self.destructionLazer()
        trajectoire_robot = self.robot.getTrajectoire()
        tailleRobot = self.robot.getTaille() 
        xBot = self.robot.getCoordonnee().getAbscisse()
        yBot = self.robot.getCoordonnee().getOrdonnee()

        for i in range(nbLazer):
            lazer = Lazer(nom=f"l{i}", coordonneeInitial=Coordonnee(xBot, yBot), coordonneeFinal=Coordonnee())

            angle_degrees = -(i - nbLazer / 2 + 1) * degreeEspacement

            xData, yData = self.verifObstacle(xBot, yBot, angle_degrees + trajectoire_robot)
            offset_x = tailleRobot * math.cos(math.radians(angle_degrees+ trajectoire_robot))
            offset_y = tailleRobot * math.sin(math.radians(angle_degrees+ trajectoire_robot))
            lazer.setCoordonneeInitial(Coordonnee(xBot + offset_x, yBot - offset_y))
            lazer.setCoordonneeFinal(Coordonnee(xData, yData))
            lazer.setAngle(angle_degrees)

            self.lidarGroup.append(lazer)          
    #On supprime tous les objets Lazers existant
    def destructionLazer(self):
        self.lidarGroup = []  
    #Vérification de la zone de déplacement par les faisceaux
    def analyseZone(self, distanceAutorise):
        for lazer in self.lidarGroup:
            abs_diff = abs(lazer.getCoordonneeInitial().getAbscisse() - lazer.getCoordonneeFinal().getAbscisse())
            ord_diff = abs(lazer.getCoordonneeInitial().getOrdonnee() - lazer.getCoordonneeFinal().getOrdonnee())
            if abs_diff < distanceAutorise or ord_diff < distanceAutorise:
                return False
        return True    
    #Calcule de l'efficience du robot sur la carte
    def updateEfficiency(self):
        total_pixels = self.view.canvas.winfo_width() * self.view.canvas.winfo_height()

        # Assuming the robot covers a circular area, update covered_pixels based on your logic
        # You might need to adjust this part based on how you determine covered pixels
        if self.robot.getCoordonnee():
            robot_x, robot_y = self.robot.getCoordonnee().getAbscisse(), self.robot.getCoordonnee().getOrdonnee()
            robot_radius = int(self.robot.getTaille())

            for x in range(int(robot_x - robot_radius), int(robot_x + robot_radius + 1)):
                for y in range(int(robot_y - robot_radius), int(robot_y + robot_radius + 1)):
                    # Check if the pixel is within the canvas
                    if 0 <= x < self.view.canvas.winfo_width() and 0 <= y < self.view.canvas.winfo_height():
                        coordinate = (x, y)

                        # Check if the coordinate has not been visited
                        if coordinate not in self.visited_coordinates:
                            # Mark the coordinate as visited
                            self.visited_coordinates.add(coordinate)

        # Calculate the percentage efficiency
        covered_pixels = len(self.visited_coordinates)
        self.efficiency = (covered_pixels / total_pixels) * 100
    
    #Choix de la carte
    def browseImage(self):
        img_folder_path = os.path.join(self.root_directory, 'ressource', 'img')
        initial_dir = os.path.normpath(img_folder_path)

        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg")],
            initialdir=initial_dir
        )

        if file_path:
            self.carte.setPath(file_path)
            self.updateCarte()     
    #Mise à jour de la carte
    def updateCarte(self):
        self.robot.getCoordonnee().setAbscisse(None)
        self.robot.getCoordonnee().setOrdonnee(None) 
        self.view.updateCarte()
        self.efficiency = 0.0
    #Affichage de la carte
    def showMap(self):
        self.view.showMap()
    #Lancement de l'application
    def runApp(self):        
        self.root.mainloop()
        self.showMap()
    