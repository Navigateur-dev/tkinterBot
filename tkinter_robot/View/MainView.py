from tkinter import *
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageColor
import math

#DETECTION PIXEL : self.controller.detectionObstacle(image.width, image.height, image)

class MainView:
    def __init__(self, controller):
        #INIT
        self.controller = controller
        self.root = controller.root
        self.carte = controller.carte
        self.robot = controller.robot    
        self.coordonnee = controller.coordonnee 
        self.canvas = Canvas(self.root, width=400, height=400)
        self.button_frame = Frame(self.root)
        self.canvas.pack()
        self.topParametrageRobot = None
        self.topParametrageLazer = None
        self.photo = None  
        self.telemetrieIsActif = False 
        self.lazer = controller.lazer
        self.halte = False
        self.minimap_active = False
        self.minimap_canvas = None

       # Partie Menu
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)     
        self.nbLazerEntry = None
        self.espacementEntry = None
    
        # Sous-menu "Paramètres"
        settings_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Paramètre général", menu=settings_menu)
        settings_menu.add_command(label="Ouvrir Paramètres du robot", command=self.menuRobot)
        settings_menu.add_command(label="Ouvrir Paramètres du lazer", command=self.menuLazer)
        

        #Composants
        self.btnCarte = Button(self.root, text="Choisir la carte", command=controller.browseImage)
        self.btnTelemetrie = Button(self.button_frame, text="Activer/Désactiver Lazer", command=self.toggleTelemetrie)
        self.btnDataTelemetrique = Button(self.button_frame, text="Voir les données télémétriques", command=self.toggleTelemetrieWindow)
        self.btnAutomate = Button(self.button_frame, text="Automatisation du déplacement", command=controller.toggle_automation)
        self.btnMinimap = Button(self.button_frame, text="Voir la minimap", command=self.createMinimap)
        
        #Placement et positionnement des composants        
        self.btnCarte.pack()
        self.btnTelemetrie.grid(row=0, column=0, padx=5)
        self.btnDataTelemetrique.grid(row=0, column=1, padx=5)
        self.btnAutomate.grid(row=0, column=2, padx=5)
        self.btnMinimap.grid(row=0, column=3, padx=5)
        
        #Listener
        self.canvas.bind("<Button-1>", controller.clicSouris) #OK
        self.root.bind("<KeyPress-Left>", controller.pivotGauche) #OK
        self.root.bind("<KeyPress-Right>", controller.pivotDroite) #OK
        self.root.bind("<KeyPress-Up>", lambda event: self.deleteRobot()) #OK
        self.root.bind("<KeyPress-Down>", lambda event: self.controller.move(self.robot,5)) #OK
        
        #Génération de la notice d'utilisation : 
        self.show_popup("Information ", "Notice d'utilisation : \n Choix de l'angle de départ : flèche de gauche et droit. \n Placer le robot : clique gauche. \n Supprimer le robot : flèche du haut \n Avancer manuellement : flèche du bas. \n Bonne navigation !")
        
        self.telemetry_window = self.createTelemetryWindow()
    ########################    Autres (tools et fonction utiles)   ###########################
            
    #Affichage des boutons nécessaires au robot (Sécurité)
    def afficherBoutons(self):
        # Afficher tous les boutons
        self.button_frame.pack(side=TOP, padx=10)
        
    #Désaffichage des boutons 
    def masquerBoutons(self):
        # Masquer tous les boutons
        self.button_frame.pack_forget()
        
    #Fonction de génération des mini-fenêtres d'informations (gère les erreurs et notices)
    def show_popup(self,title, message):
        popup = Toplevel()
        popup.title(title)

        label = Label(popup, text=message)
        label.pack(padx=20, pady=20)

        close_button = Button(popup, text="Fermer", command=popup.destroy)
        close_button.pack(pady=10)
    def verifTag(self, tags):
        elements = self.canvas.find_withtag(tags)
        return bool(elements)
    #######################################################################
    
    ######## GUI Information télémétrique #########
    
    #Fonction de génération de la fenêtre des données télémétriques
    def createTelemetryWindow(self):
        telemetry_window = Toplevel(self.root)
        telemetry_window.title("Données télémétriques")
        telemetry_window.withdraw()  

        self.telemetry_position_label = Label(telemetry_window, text="Position du robot : ")
        self.telemetry_position_value = Label(telemetry_window, text="")
        self.telemetry_position_label.pack()
        self.telemetry_position_value.pack()

        self.telemetry_trajectoire_label = Label(telemetry_window, text="Trajectoire du robot : ")
        self.telemetry_trajectoire_value = Label(telemetry_window, text="")
        self.telemetry_trajectoire_label.pack()
        self.telemetry_trajectoire_value.pack()

        self.telemetry_lazer_label = Label(telemetry_window, text="Données Lazer : ")
        self.telemetry_lazer_value = Label(telemetry_window, text="")
        self.telemetry_lazer_label.pack()
        self.telemetry_lazer_value.pack()

        return telemetry_window
    
    #Fonction d'activation/désactivation de la fenêtre des données télémétriques
    def toggleTelemetrieWindow(self):
        if hasattr(self, "telemetry_window") and self.telemetry_window.winfo_exists():
            if self.telemetry_window.state() == 'normal':
                self.telemetry_window.withdraw()
            else:
                self.telemetry_window.deiconify()
                self.retourDataTelemetrique()  
                
    #Permet de générer les valeurs télémétrique                
    def retourDataTelemetrique(self):
        self.telemetry_position_value.config(text=f"{self.robot.getCoordonnee().getAbscisse()}, {self.robot.getCoordonnee().getOrdonnee()}")
        self.telemetry_trajectoire_value.config(text=f"{self.robot.getTrajectoire()}")

        lazer_data = ""
        for lazer in self.controller.lidarGroup:
            degree = self.controller.radians_to_degrees(lazer.getAngle())
            lazer_data += f"Lazer {lazer.getNom()} : ({lazer.getCoordonneeFinal().getAbscisse()}, {lazer.getCoordonneeFinal().getOrdonnee()}). Angle trajectoire du Robot: {degree}°\n"

        self.telemetry_lazer_value.config(text=lazer_data)
        
    #################################################
    ########   MINIMAP ##############################
    #Fonction d'affichage de la minimap
    def createMinimap(self):
        self.minimap_active = not self.minimap_active

        if self.minimap_active:
            # Fermez la fenêtre de la minimap si elle existe
            if hasattr(self, "minimap_window") and self.minimap_window.winfo_exists():
                self.minimap_window.destroy()

            # Créez une nouvelle fenêtre
            self.minimap_window = Toplevel(self.root)
            self.minimap_window.title("Minimap")
            
            self.efficiency_label = Label(self.minimap_window, text="")
            self.efficiency_label.pack(side=TOP)
            if self.carte.getPath():
                main_image = Image.open(self.carte.getPath())

                # Obtenir les dimensions de la fenêtre
                window_width = self.minimap_window.winfo_reqwidth()
                window_height = self.minimap_window.winfo_reqheight()

                # Calculer le facteur d'échelle pour s'adapter à la fenêtre
                scale_factor = min(window_width / main_image.width, window_height / main_image.height)

                # Redimensionner l'image en fonction du facteur d'échelle
                resized_width = int(main_image.width * scale_factor)
                resized_height = int(main_image.height * scale_factor)
                resized_image = main_image.resize((resized_width, resized_height))

                # Créer une PhotoImage à partir de l'image redimensionnée
                self.minimap_photo = ImageTk.PhotoImage(resized_image)

                # Afficher l'image redimensionnée dans la fenêtre principale
                self.minimap_canvas = Canvas(self.minimap_window, width=resized_width, height=resized_height, bg="white")
                self.minimap_canvas.pack()

                # Ajoutez un nouveau canevas pour la minimap dans la nouvelle fenêtre
                self.minimap_canvas.create_image(0, 0, anchor=NW, image=self.minimap_photo)
                
                # Dessiner le robot sur la minimap 
                self.updateMinimap()

                # Appeler la méthode après chaque déplacement du robot
                self.root.after(100, self.updateMinimap)
        else:
            # Fermez la fenêtre de la minimap si elle existe
            if hasattr(self, "minimap_window") and self.minimap_window.winfo_exists():
                self.minimap_window.destroy()

    #Fonction de mise à jour de la minimap 
    def updateMinimap(self):
        robot_coord = self.robot.getCoordonnee()
        if robot_coord:
            # Coordonnées du robot sur la carte principale
            robot_x, robot_y = robot_coord.getAbscisse(), robot_coord.getOrdonnee()

            # Conversion des coordonnées de la carte vers la minimap : 
            carte_width = self.canvas.winfo_width()
            carte_height = self.canvas.winfo_height()
            minimap_width = self.minimap_canvas.winfo_width()
            minimap_height = self.minimap_canvas.winfo_height()
            robot_x_minimap = (robot_x / carte_width) * minimap_width
            robot_y_minimap = (robot_y / carte_height) * minimap_height

            self.minimap_canvas.create_rectangle(
                robot_x_minimap - 2, robot_y_minimap - 2,
                robot_x_minimap + 2, robot_y_minimap + 2,
                fill="red"
            )
        
        # Partie efficience afficher au dessus de la minimap : 
        efficiency_text = f"Efficience : {self.controller.efficiency:.2f}%"
        self.efficiency_label.config(text=efficiency_text)

        # On efface l'ancienne valeur 
        self.minimap_canvas.delete("efficiency_text")
        # On remet à jour la minimap 
        self.root.after(100, self.updateMinimap)

    #######################################################################
    ########################    Cartographie  GUI  ###########################
    # Mise à jour de la carte en cas de changement : 
    def updateCarte(self):
        self.canvas.delete("all")
        if self.carte.getPath():
            image = Image.open(self.carte.getPath())
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
            self.canvas.config(width=image.width, height=image.height)
            self.root.update_idletasks()
    # AAffichage de la carte :   
    def showMap(self):
        mapWindow = Toplevel(self.root)
        mapView = self.MapView(mapWindow, self.carte)
    #######################################################################
    
    
    ########################### Faisceaux laser GUI #######################
    
    #Activation/désactivation des faisceaux 
    def toggleTelemetrie(self):
        self.telemetrieIsActif = not self.telemetrieIsActif
        if self.telemetrieIsActif:
            self.dessineLazer()
        else:
            self.effacerLazer()
    
    #Dessine les faisceaux lasers.    
      
    def dessineLazer(self):
        if self.controller.lidarGroup:
            for lazer in self.controller.lidarGroup:
                self.canvas.create_line(
                    lazer.getCoordonneeInitial().getAbscisse(), lazer.getCoordonneeInitial().getOrdonnee(),
                    lazer.getCoordonneeFinal().getAbscisse(), lazer.getCoordonneeFinal().getOrdonnee(),
                    fill="blue", width=1, tags=lazer.getNom()
                )
    
    #Efface les faisceaux lasers                
    def effacerLazer(self):
        # self.telemetrieIsActif = False 
        self.canvas.delete(self.lazer.getNom())
        for lazer in self.controller.lidarGroup:
            self.canvas.delete(lazer.getNom())
            
    #Mise à jour du paramétrages des faisceaux laser
    def updateLazer(self):
        self.effacerLazer()
        if self.nbLazerEntry.get() and self.espacementEntry.get():
            self.show_popup('Information', "Les paramètres de lazers ont bien été pris en compte ! ")
            
            self.controller.nbLazer = int(self.nbLazerEntry.get())
            
            self.controller.espacement = float(self.espacementEntry.get())
            self.topParametrageLazer.destroy()
            self.topParametrageLazer = None
            self.reloadLazer()
            self.controller.initiationLazer(self.controller.nbLazer, self.controller.espacement)
            # self.placerPoint()
        else:
            self.show_popup('Erreur', "Veuillez choisir une valeur pour chacun des champs !")
    #Permets de supprimer les lasers    
    def reloadLazer(self):
        self.controller.destructionLazer()        
    ###############################################################################
    ##########################  ROBOT GUI #########################################
    def placerPoint(self):
        self.deleteRobot()

        robotTaille = self.robot.getTaille()
        robotCoordonnee = self.robot.getCoordonnee()
        if robotCoordonnee is not None:
            robotX, robotY = robotCoordonnee.getAbscisse(), robotCoordonnee.getOrdonnee()
            #verifPlacement(taille, robotCoordonnee)
            self.canvas.create_oval(robotX - robotTaille, robotY - robotTaille, robotX + robotTaille, robotY + robotTaille, fill=self.robot.getCouleur(), tags=self.robot.getName())
            arrow_length = robotTaille
            arrow_angle =  self.robot.getTrajectoire() # Angle des pointes de la flèche
            angle_rad = math.radians(arrow_angle)
            
            arrow_x = robotX + arrow_length * math.cos(angle_rad)
            arrow_y = robotY - arrow_length * math.sin(angle_rad)
            self.canvas.create_line(robotX, robotY, arrow_x, arrow_y, width=2, arrow=LAST, tags=self.robot.getName())
            self.afficherBoutons()
        else:
            print("Coordonnées du robot non définies.")   
    def verifPlacement(self, taille, coordonnee):
        try:
            with Image.open(self.carte.getPath()) as image:
                x, y = coordonnee.getAbscisse(), coordonnee.getOrdonnee()
                rayon = taille

                for angle in range(360):
                    angle_rad = math.radians(angle)

                    x_point = int(x + rayon * math.cos(angle_rad))
                    y_point = int(y + rayon * math.sin(angle_rad))

                    # Vérifiez si les coordonnées sont dans la plage valide de l'image
                    if 0 <= x_point < image.width and 0 <= y_point < image.height:
                        pixel = image.getpixel((x_point, y_point))
                        if pixel != (255, 255, 255):
                            return False
                    else:
                        # Les coordonnées sont en dehors de la plage de l'image
                        return False

                return True
        except Exception as e:
            self.show_popup('Erreur', f"Erreur lors de l'ouverture de l'image : {e}")
            
            return False
    def updateRobot(self):
            if self.tailleEntry.get() and self.vitesseEntry.get() and self.couleurEntry.get():
                self.show_popup('Information', "Les paramètres du robot ont bien été pris en compte")
                
                self.robot.setTaille(float(self.tailleEntry.get()))
                self.robot.setVitesse(float(self.vitesseEntry.get()))
                self.robot.setCouleur(str(self.couleurEntry.get()))  
                self.topParametrageRobot.destroy()
                self.topParametrageRobot = None
                
                if self.verifTag(self.robot.getName()) :
                    self.placerPoint()
            else:
                self.show_popup('Erreur', "Veuillez choisir une valeur pour chacun des champs !")
    def deleteRobot(self): #OK
        self.masquerBoutons()  # Masquer les boutons lorsque le robot est supprimé
        nameRobot = self.robot.getName()
        if nameRobot is not None:
            self.canvas.delete(nameRobot)
            self.effacerLazer()
            self.controller.destructionLazer()
            
    ###############################################################################
    ###########################   PARAMETRAGE #####################################
    def menuLazer(self):
        if(self.topParametrageLazer is None):
            topParametrageLazer = Toplevel()
            self.topParametrageLazer = topParametrageLazer
            canvasParametrageLazer = Canvas(self.topParametrageLazer, width=200, height=100)

            canvasParametrageLazer.pack()
            self.topParametrageLazer.title("Paramétrage du lazer")
            
            nbLazer = self.controller.nbLazer
            self.nbLazer = IntVar()
            self.nbLazer.set(nbLazer)
            self.nbLazerLabel = Label(self.topParametrageLazer, text="Nombre de Lazer")
            self.nbLazerLabel.pack()
            self.nbLazerEntry = Entry(self.topParametrageLazer, textvariable=self.nbLazer)
            self.nbLazerEntry.pack()
            
            espacement = self.controller.espacement
            self.espacement = DoubleVar()
            self.espacement.set(espacement)
            self.espacementLabel = Label(self.topParametrageLazer, text="Espace entre chaque Lazer")
            self.espacementLabel.pack()
            self.espacementEntry = Entry(self.topParametrageLazer, textvariable=self.espacement)
            self.espacementEntry.pack()
            
            self.btnUpdateLazer = Button(self.topParametrageLazer, text="Enregistrer", command=self.updateLazer)
            self.btnUpdateLazer.pack()
            
            self.topParametrageLazer.protocol("WM_DELETE_WINDOW", lambda : self.fermeture("lazer"))      
    def menuRobot(self): #OK
        # if(self.topParametrageRobot is None):
            topParametrageRobot = Toplevel()
            self.topParametrageRobot = topParametrageRobot
            canvasParametrage = Canvas(self.topParametrageRobot, width=200, height=100)

            canvasParametrage.pack()
            self.topParametrageRobot.title("Paramétrage du robot")
            
            vitesse = self.robot.getVitesse()
            self.vitesse = DoubleVar()
            self.vitesse.set(vitesse)
            self.vitesseLabel = Label(self.topParametrageRobot, text="Vitesse du robot:")
            self.vitesseLabel.pack()
            self.vitesseEntry = Entry(self.topParametrageRobot, textvariable=self.vitesse)
            self.vitesseEntry.pack()

            couleur = self.robot.getCouleur()
            self.couleur = StringVar()
            self.couleur.set(couleur)
            self.couleurLabel = Label(self.topParametrageRobot, text="Couleur du robot:")
            self.couleurLabel.pack()

            self.btnColor = Button(self.topParametrageRobot, text="Choisir la couleur", command=self.choixCouleur)
            self.btnColor.pack()
            self.couleurEntry = Entry(self.topParametrageRobot, textvariable=self.couleur)
            self.couleurEntry.pack()

            taille = self.robot.getTaille()
            self.taille = DoubleVar()
            self.taille.set(taille)
            self.tailleLabel = Label(self.topParametrageRobot, text="Taille du robot:")
            self.tailleLabel.pack()
            self.tailleEntry = Entry(self.topParametrageRobot, textvariable=self.taille)
            self.tailleEntry.pack()

            self.btnUpdate = Button(self.topParametrageRobot, text="Enregistrer", command=self.updateRobot)
            self.btnUpdate.pack()
            self.topParametrageRobot.protocol("WM_DELETE_WINDOW", lambda : self.fermeture("robot"))
    def fermeture(self, fenetre):
        if fenetre == "robot":
            self.topParametrageRobot.destroy()
            self.topParametrageRobot = None
        elif fenetre == "lazer":
            self.topParametrageLazer.destroy()
            self.topParametrageLazer = None                        
    def choixCouleur(self):
        # Ouvre le sélecteur de couleur et récupère la couleur sélectionnée
        color = colorchooser.askcolor()[1]

        # Met à jour le champ de couleur avec la couleur sélectionnée
        self.couleurEntry.delete(0, END)
        self.couleurEntry.insert(0, color) 
    ###############################################################################

        