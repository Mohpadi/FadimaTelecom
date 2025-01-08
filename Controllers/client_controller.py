from Models.client import Client
from Views.client import afficher_repertoire, selectionner_contact, selectionner_numero
from Views.functions import afficher_message, afficher_erreur


def se_connecter_client(numero, pin):
    """
    Connecte un client via le modèle.
    """
    return Client.connexion_client(numero, pin)


def consulter_credit(numero, pin):
    """
    Retourne le crédit d'un client après vérification du PIN.
    """
    client = se_connecter_client(numero, pin)
    return client.credit


def verifier_solde(client):
    Client.verifier_solde(client)


def ajouter_contact(numero_client, nom, numeros):
    """
    Ajoute un contact ou ajoute un numéro supplémentaire à un contact existant.
    """
    client = Client.lire_par_numero(numero_client)  # Récupérer directement le client
    if not client:
        print(f"Erreur : Client avec le numéro {numero_client} introuvable.")
        return

    try:
        # Vérifier si le contact existe déjà
        if nom in client.repertoire:
            # Récupérer les numéros existants
            numeros_existants = client.repertoire[nom]['numeros']

            # Vérifier la limite de 3 numéros
            if len(numeros_existants) + len(numeros) > 3:
                raise ValueError(
                    f"Le contact '{nom}' ne peut pas avoir plus de 3 numéros. "
                    f"Actuellement : {len(numeros_existants)} numéros enregistrés."
                )

            # Ajouter les nouveaux numéros (avec validation)
            for num in numeros:
                Client.valider_numero(num)

                if not Client.numero_existe_dans_operateurs(num):
                    raise ValueError(f"Le numéro {num} n'existe chez aucun opérateur du système.")

                if any(num in details['numeros'] for details in client.repertoire.values()):
                    raise ValueError(f"Le numéro {num} est déjà associé à un autre contact.")

                # Ajouter au contact
                if num not in numeros_existants:
                    numeros_existants.append(num)

            afficher_message(f"Nouveau(x) numéro(s) ajouté(s) au contact '{nom}' avec succès.")

        else:
            # Ajouter un nouveau contact si le contact n'existe pas
            client.ajouter_contact(nom, numeros)
            afficher_message(f"Contact '{nom}' ajouté avec succès.")

        # Sauvegarder les modifications et afficher le répertoire
        client.sauvegarder()
        afficher_repertoire(client)

    except ValueError as e:
        afficher_erreur(str(e))




def supprimer_contact(numero_client, nom):
    """
    Supprime un contact.
    """
    client = Client.lire_par_numero(numero_client)
    client.supprimer_contact(nom)
    afficher_message(f"Le contact '{nom}' a été supprimé avec succès.")

def changer_pin(client, ancien_pin):
    Client.changer_pin(client, ancien_pin)
    
def renommer_contact(numero_client, ancien_nom, nouveau_nom):
    """
    Renomme un contact.
    """
    client = Client.lire_par_numero(numero_client)
    client.renommer_contact(ancien_nom, nouveau_nom)


def ajouter_numero_contact(numero_client, nom_contact, nouveau_numero):
    """
    Ajoute un numéro à un contact existant.
    """
    client = Client.lire_par_numero(numero_client)
    client.ajouter_numero_contact(nom_contact, nouveau_numero)

def rechercher_contact(client, mot_cle): 
    """
    Recherche un contact par mot-clé dans le répertoire.
    """
    # Actualiser les données du client
    client = Client.lire_par_numero(client.numero)
    if not client:
        raise ValueError("Client introuvable.")

    # Effectuer la recherche
    resultats = client.rechercher_contact(mot_cle)
    return resultats  # Renvoie les résultats sous forme de dictionnaire


def transferer_credit(source_numero, cible_numero, montant):
    """
    Transfère du crédit d'un client à un autre.
    """
    if montant < 100:
        raise ValueError("Le montant minimum pour un transfert est 100.")
    Client.transferer_credit(source_numero, cible_numero, montant)


def acheter_credit(numero, montant):
    """
    Ajoute du crédit à un client (action initiée par le gestionnaire).
    """
    if montant < 100:
        raise ValueError("Le montant minimum pour acheter du crédit est de 100.")
    # Récupérer le client par son numéro
    client = Client.lire_par_numero(numero)
    client.ajouter_credit(montant)  # Utilise l'instance de Client


def effectuer_appel(numero_client, numero_cible):
    """
    Simule un appel entre deux numéros.
    """
    client = Client.lire_par_numero(numero_client)
    nom_contact = None
    for nom, contact_data in client.repertoire.items():
        if numero_cible in contact_data.get('numeros', []):
            nom_contact = nom
            break
    Client.lancer_appel(numero_client, numero_cible)
    if nom_contact:
        return f"Appel vers {nom_contact} ({numero_cible}) en cours..."
    else:
        return f"Appel vers {numero_cible} en cours..."


def appeler_contact(repertoire):
    """
    Gère l'appel d'un contact en fonction du répertoire.
    """
    contact = selectionner_contact(repertoire)
    if not contact:
        return

    numeros = repertoire[contact]["numeros"]
    if len(numeros) == 1:
        effectuer_appel("0000000", numeros[0])
    else:
        afficher_message(f"'{contact}' a {len(numeros)} numéros.")
        numero = selectionner_numero(numeros)
        if numero:
            effectuer_appel("0000000", numero)


def effectuer_appel_interactif(numero_emetteur, numero_recepteur):
    """
    Simule un appel interactif entre deux numéros.
    """
    Client.lancer_appel(numero_emetteur, numero_recepteur)


def bloquer_contact(numero_client, nom):
    """
    Bloque un contact dans le répertoire du client après une validation de sûreté.
    :param numero_client: Numéro du client.
    :param nom: Nom du contact à bloquer.
    """
    # Confirmer l'action avec l'utilisateur
    confirmation = input(f"Êtes-vous sûr(e) de vouloir bloquer le contact '{nom}' ? (o/n) : ").strip().lower()

    # Si l'utilisateur confirme, procéder au blocage
    if confirmation == "o":
        try:
            client = Client.lire_par_numero(numero_client)
            client.bloquer_contact(nom)
            afficher_message(f"Le contact '{nom}' a été bloqué avec succès.")
        except Exception as e:
            afficher_message(f"Erreur lors du blocage du contact : {e}")
    else:
        afficher_message("Blocage annulé.")



def debloquer_contact(numero_client, nom):
    """
    Débloque un contact dans le répertoire du client.
    """
    client = Client.lire_par_numero(numero_client)
    client.debloquer_contact(nom)
    afficher_message(f"Le contact '{nom}' a été débloqué avec succès.")

def ecouter_vocal(client):
    Client.ecouter_vocal(client)
def supprimer_vocal(numero_client, id_vocal):
    """
    Supprime un vocal de l'historique des appels du client.
    """
    try:
        # Vérifiez si l'appel appartient au client
        historique_client = Client.voir_historique(numero_client)
        if any(appel['id'] == id_vocal for appel in historique_client):
            # Supprime le vocal
            Client.supprimer_vocal(id_vocal)
            afficher_message(f"Le vocal avec l'ID {id_vocal} a été supprimé avec succès.")
        else:
            afficher_erreur("Le vocal spécifié n'appartient pas à ce client.")
    except Exception as e:
        afficher_erreur(f"Erreur lors de la suppression du vocal : {e}")