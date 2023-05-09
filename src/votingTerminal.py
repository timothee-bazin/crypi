#!/usr/bin/python3

from tools import sanitize_str, sanitize_date, check_identifiant
from client import Client

class VotingTerminal:
    def __init__(self):
        self.nom = None
        self.prenom = None
        self.naissance = None
        self.identifiant = None

        self.candidats = ["Felix", "Thimothé", "Léo", "Alexandre"]
        self.public_key = None

        self.client = None # Client()

    # Mise en place d'une communication sécurisée
    def init_connection_server():
        pass

    # Envoi crédentials au serveur (celui-ci verifie qu'il n'a pas déjà voté et qu'il existe)
    # Récupère un cookie ?
    def user_login():
        pass

    # Affiche les candidats
    def prompt_candidates(self):
        if not self.candidats: 
            self.candidats = self.client.get_candidates()
        
        for i, candidat in enumerate(self.candidats):
            print(f"{i + 1}. {candidat}")
        

    # Envoi l'intention de vote au serveur et récupère la preuve
    def compute_vote(candidat):
        pass

    # Envoi le hash et l'expose sur la liste officielle des votants
    def confirm_vote():
        pass

    # Réinitialise le terminal
    def disconnect(self):
        self.prenom = None
        self.nom = None
        self.naissance = None
        self.identifiant = None

    # Terminal sans interface graphique
    def loop(self):
        print(self.candidats)
        separator = "------------------------"
        while True:
            print(separator)
            print("Bonjour, bienvenue dans ce e-bureau de vote pour les élections de l'élève le plus sympa !")
            print("Vérifier bien que vous avez votre lettre reçu chez vous pour cette élection. Autrement, inutile de commencer cette démarche.")
            
            while True: # Informations
                print(separator)
                print("Entrez votre informations:")
                self.prenom = sanitize_str(input("Prenom: "))
                self.nom = sanitize_str(input("Nom: "))
                self.naissance = sanitize_date(input("Date de naissance (dd/mm/aaaa): "))
                if self.naissance is None:
                    print("Erreur de format avec votre date de naissance.")
                    continue
                print(f"Confirmation des vos identifiants (sans accents): {self.prenom} {self.nom} né.e le {self.naissance}")

                validation = input("Confirmer (oui,non): [défaut = oui]") or "oui"
                if validation.lower() in ["oui", "ou", "o"]:
                    break
            
            print(separator)          
            print(f"Mme/M {self.nom}, vous avez reçu par courrier physique un identifiant unique pour ce vote.")
            while True: # Identifiant secret
                self.identifiant = input("Identifiant :")
                if check_identifiant(self.identifiant):
                    break
                print("Erreur de format avec votre identifiant.")
                print("Vérifier que vous avez bien copier l'identifiant sur votre lettre.")

            print(separator)
            print("Verification de vos informations....")
            
            # success, error_message = client.send()
            # if not success:
            #   print(error_message)
            #   continue # Retour au debut

            print("Verification terminée.")
            while True: # Choix candidat
                self.prompt_candidates()
                
                choix = input("Choisissez votre candidat.e (1,2,..): ")
                if not str.isdigit(choix):
                    print("Erreur de format, un chiffre est attendu")
                    continue
                
                choix_int = int(choix)
                if choix_int < 1 or choix_int > len(self.candidats):
                    print("Chiffre inalide, il n'y a de candidat associé")
                    continue
                # +1 car les choix sont de 1 à x
                
                candidat = self.candidats[choix_int - 1]
                print(f"Êtes-vous sûr de vouloir voter pour {candidat}?")
                validation = input("[Attention] Confirmer (oui,non): [défaut = oui]") or "oui"
                if validation.lower() in ["oui", "ou", "o"]:
                    break
            
            # preuve =  client.send_vote() 
            preuve = "0102030405"
            print(f"Votre preuve de vote est : {preuve}")
            print("Nous vous imprimons la preuve de vote...")
            print('"À voté !"')




if __name__ == "__main__":
    terminal = VotingTerminal()
    terminal.loop()
