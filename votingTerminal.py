#!/usr/bin/python3

from tools import sanitize_str

class VotingTerminal:
    def __init(self):
        pass

    # Mise en place d'une communication sécurisée
    def init_connection_server():
        pass

    # Récupération de la liste des candidats depuis le serveur
    def get_candidates():
        pass

    # Envoi crédentials au serveur (celui-ci verifie qu'il n'a pas déjà voté et qu'il existe)
    # Récupère un cookie ?
    def user_login():
        pass

    # Affiche les candidats
    def prompt_candidates():
        pass

    # Envoi l'intention de vote au serveur et récupère la preuve
    def compute_vote(candidat):
        pass

    # Envoi le hash et l'expose sur la liste officielle des votants
    def confirm_vote():
        pass

    # Réinitialise le terminal
    def disconnect():
        pass

    # Terminal sans interface graphique
    def loop():
        while True:
            print("------------------------")
            print("Bonjour, bienvenue dans ce e-bureau de vote pour les élections de l'élève le plus sympa !")
            while True:
                print("Entrez votre informations:")
                prenom = sanitize_str(input("Prenom: "))
                nom = sanitize_str(input("Nom: "))
                naissance = sanitize_str(input("Date de naissance (dd/mm/aaaa): "))
                print("Confirmation des vos identifiants (sans accents): {prenom} {nom} né.e le {naissance}")

                validation = input("Confirmer (o,n): [défaut = oui]") or "oui"
                if validation.lower() in ["oui", "o"]:

