from datetime import datetime
from Models.operateur import Operateur
from Controllers.client_controller import acheter_credit
from Models.transactions import Transaction
from Views.functions import afficher_message
from constants import MAX_INDEX
from Views.operateur import afficher_resume_vente, choisir_index, choisir_numero, choisir_operateur
USERS_FILE = "BD/gestionnaires.txt"
def se_connecter_gestionnaire(id_gestionnaire, pin):
    """
    Connecte un gestionnaire en vérifiant son ID et son PIN.
    """
    with open(USERS_FILE, "r") as f:
        for line in f:
            data = line.strip().split(";")
            if data[0] == "gestionnaire" and data[1] == id_gestionnaire and data[3] == pin:
                return {"id": data[1], "nom": data[2]}
    raise ValueError("Identifiant ou PIN invalide.")

def se_deconnecter_gestionnaire():
    """
    Déconnecte un gestionnaire (simple confirmation ici).
    """
    return "Gestionnaire déconnecté."
def creer_operateur(nom, index):
    """
    Crée un opérateur avec validation.
    """
    if Operateur.lire_par_nom(nom):
        raise ValueError(f"L'opérateur '{nom}' existe déjà.")
    
    # Si `index` est une chaîne, convertissez-la en liste
    if isinstance(index, str):
        index = [index]
    
    Operateur.creer(nom, index)

def ajouter_index(nom_operateur, nouvel_index):
    """Ajoute un index à un opérateur existant."""
    operateur = Operateur.lire_par_nom(nom_operateur)
    if not operateur:
        raise ValueError(f"L'opérateur '{nom_operateur}' n'existe pas.")
    if len(operateur.index) >= MAX_INDEX:
        raise ValueError(f"L'opérateur '{nom_operateur}' a déjà le nombre maximum d'indices ({MAX_INDEX}).")

    operateur.ajouter_index(nouvel_index)

def supprimer_index(nom_operateur, index_a_supprimer):
    """Supprime un index d'un opérateur si possible."""
    operateur = Operateur.lire_par_nom(nom_operateur)
    if not operateur:
        raise ValueError(f"L'opérateur '{nom_operateur}' n'existe pas.")
    operateur.supprimer_index(index_a_supprimer)

def renommer_operateur(ancien_nom, nouveau_nom):
    """Supprime un index d'un opérateur si possible."""
    Operateur.renommer_operateur(ancien_nom, nouveau_nom)


def lister_operateurs():
    """Retourne la liste de tous les opérateurs."""
    return Operateur.lister_operateurs()

def lister_numeros_operateur(nom_operateur):
    """
    Retourne les numéros d'un opérateur donné.
    """
    operateur = Operateur.lire_par_nom(nom_operateur)
    if not operateur:
        raise ValueError(f"L'opérateur '{nom_operateur}' n'existe pas.")
    return operateur.numeros

def vendre_numero():
    """
    Gère le processus de vente d'un numéro en suivant les étapes spécifiées.
    """
    # Étape 1 : Afficher et choisir un opérateur
    operateurs = lister_operateurs()
    operateur = choisir_operateur(operateurs)
    if not operateur:
        return

    # Étape 2 : Afficher et choisir un index
    index = choisir_index(operateur)
    if not index:
        return

    # Étape 3 : Afficher et choisir un numéro
    numero = choisir_numero(operateur, index)
    if not numero:
        return

    # Étape 4 : Demander le nom du client
    client_nom = input("Entrez le nom du client (laisser vide si inconnu) : ")

    # Étape 5 : Valider la vente
    operateur.vendre_numero(index, numero, client_nom)  # Assurez-vous que cette méthode est correcte

    # Étape 6 : Afficher un résumé de la vente
    afficher_resume_vente(numero, client_nom)


def vendre_credit_client(numero_client, montant):
    """
    Vend du crédit à un client.
    """
    if montant < 100:
        raise ValueError("Le montant minimum pour l'achat de crédit est de 100.")
    
    # Ajouter le crédit au client
    acheter_credit(numero_client, montant)
    # Afficher le message de confirmation
    afficher_message(f"{montant} FCFA de crédit ajouté au client '{numero_client}'.")

def etat_caisse(periode):
    """
    Calcule l'état de la caisse pour une période donnée par opérateur.
    :param periode: "journalier", "mensuel", ou "annuel".
    :return: Liste des transactions avec opérateur, montant, période et description.
    """
    transactions = Transaction.charger_transactions()
    etat = []

    now = datetime.now()
    for t in transactions:
        date_transaction = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
        
        if (periode == "journalier" and date_transaction.date() == now.date()) or \
           (periode == "mensuel" and date_transaction.year == now.year and date_transaction.month == now.month) or \
           (periode == "annuel" and date_transaction.year == now.year):

            operateur = t.get('operateur', "Non spécifié")
            montant = t['montant']
            description = t.get('description', "Aucune description")
            etat.append((operateur, montant, description))

    return etat
