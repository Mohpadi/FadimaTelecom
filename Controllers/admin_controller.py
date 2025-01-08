import os
import json
from Models.client import Client
from constants import DEFAULT_PARAMETRES

CLIENTS_FILE = "BD/clients.txt"
USERS_FILE = "BD/gestionnaires.txt"
PARAMETRES_FILE = "BD/parametres.txt"

def initialiser_parametres():
    if not os.path.exists(PARAMETRES_FILE):
        with open(PARAMETRES_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PARAMETRES, f, indent=4)

def lire_parametres():
    initialiser_parametres()
    with open(PARAMETRES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Le fichier des paramètres est corrompu.")


    parametres = {}
    with open(PARAMETRES_FILE, "r", encoding="utf-8") as f:  # Forcer UTF-8
        for line in f:
            line = line.strip()
            if "=" not in line or not line:  # Ignorer les lignes invalides ou vides
                continue
            cle, valeur = line.split("=", 1)  # Limiter à 2 parties
            parametres[cle] = int(valeur) if valeur.isdigit() else float(valeur)
    return parametres

def modifier_parametre(cle, valeur):
    """
    Modifie un paramètre spécifique dans le fichier.
    :param cle: Clé du paramètre à modifier.
    :param valeur: Nouvelle valeur du paramètre.
    """
    parametres = lire_parametres()

    if cle not in parametres:
        raise ValueError(f"Le paramètre '{cle}' n'existe pas.")
    
    # Mettre à jour la valeur
    parametres[cle] = valeur

    # Réécrire le fichier
    with open(PARAMETRES_FILE, "w", encoding="utf-8") as f:  # Forcer UTF-8
        for cle, valeur in parametres.items():
            f.write(f"{cle}={valeur}\n")
def reinitialiser_parametres():
    """
    Réinitialise les paramètres avec les valeurs par défaut.
    """
    with open(PARAMETRES_FILE, "w", encoding="utf-8") as f:  # Forcer UTF-8
        for cle, valeur in DEFAULT_PARAMETRES.items():
            f.write(f"{cle}={valeur}\n")
    print("Paramètres réinitialisés avec les valeurs par défaut.")

def lire_fichier(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def ajouter_utilisateur(user_type, id_or_numero, nom, pin):
    if user_type not in ["gestionnaire", "client"]:
        raise ValueError("Type d'utilisateur invalide. Doit être 'gestionnaire' ou 'client'.")

    if user_type == "gestionnaire":
        gestionnaires = lire_fichier(USERS_FILE)
        if any(line.split(";")[1] == id_or_numero for line in gestionnaires):
            raise ValueError(f"Un gestionnaire avec cet ID {id_or_numero} existe déjà.")

        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_type};{id_or_numero};{nom};{pin}\n")
        print(f"Gestionnaire '{nom}' ajouté avec succès.")

    elif user_type == "client":
        Client.creer_client(id_or_numero,nom,pin)
