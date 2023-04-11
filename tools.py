import unicodedata
import string
import re
from datetime import datetime


# Fonction pour enlever les accents d'une chaîne de caractères
def remove_accents(chaine):
    # Liste de caractères à conserver lors de la suppression des caractères diacritiques
    caracteres_a_garder = ["'"]
    # Utiliser la fonction normalize du module unicodedata pour décomposer les caractères en unicode
    decomp_chaine = unicodedata.normalize('NFD', chaine)
    # Utiliser la fonction translate du module string pour supprimer les caractères diacritiques (accents),
    # en conservant les caractères spécifiés dans la liste caracteres_a_garder
    sans_accents = "".join(c for c in decomp_chaine if unicodedata.category(c) != 'Mn' or c in caracteres_a_garder)
    return sans_accents


# Sanitize nom prénom et date
def sanitize_str(chaine):
    # Date
    try:
        # Convertir la chaîne de caractères en objet date
        datetime.strptime(chaine, '%d/%m/%Y')
        return str
    except ValueError:
        pass

    return remove_accents(chaine)
