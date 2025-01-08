from typing import Dict, List, Optional
from Views.functions import (
    afficher_titre, afficher_message, afficher_erreur, afficher_tableau
)
from Models.client import Client

def afficher_repertoire(client):
    client.afficher_repertoire()
def appeler_depuis_repertoire(client):
    """
    Permet à l'utilisateur de sélectionner un contact pour appeler en fonction de la position, du nom ou du numéro.
    """
    client.afficher_repertoire()

    choix = input("Entrez la position, le nom ou le numéro du contact à appeler [Q pour quitter] : ").strip()
    if choix.upper() == "Q":
        afficher_message("Opération annulée.")
        return

    # Recherche par position
    try:
        position = int(choix) - 1
        contacts = list(client.repertoire.items())
        if 0 <= position < len(contacts):
            nom, details = contacts[position]
            numero = details.get("numeros", [None])[0]  # Prendre le premier numéro si plusieurs
            if numero:
                afficher_message(f"Appel en cours vers {nom} ({numero}).")
                Client.lancer_appel(client.numero, numero)
                return
    except ValueError:
        pass

    # Recherche par nom
    if choix in client.repertoire:
        details = client.repertoire[choix]
        numeros = details.get("numeros", [])
        if len(numeros) == 1:
            afficher_message(f"Appel en cours vers {choix} ({numeros[0]}).")
            Client.lancer_appel(client.numero, numeros[0])
        elif len(numeros) > 1:
            numero = selectionner_numero(numeros)
            if numero:
                Client.lancer_appel(client.numero, numero)
        return

    # Recherche par numéro
    for nom, details in client.repertoire.items():
        if choix in details.get("numeros", []):
            Client.lancer_appel(client.numero, choix)
            return

    afficher_erreur("Contact introuvable. Vérifiez votre entrée.")

def afficher_credit(credit: float):
    """
    Affiche le crédit d’un client avec style.
    """
    afficher_message(f"Votre crédit actuel est de [bold]{credit} FCFA[/bold].")

def afficher_historique_appels(historique: List[dict], numero_client: str):
    """
    Affiche l’historique des appels d’un client avec coloration pour les appels émis/reçus.
    Les vocaux non lus sont affichés en rouge.
    """
    afficher_titre("Historique des appels")
    data = []
    for appel in historique:
        emetteur = appel['emetteur']
        recepteur = appel['recepteur']
        duree = f"{appel['duree']} sec"
        date = appel['date']
        vocal_lu = appel.get('vocal_lu', True)

        if emetteur == numero_client:
            ligne = [f"[green]{emetteur}[/green]", recepteur, duree, date]
        else:
            ligne = [emetteur, f"[red]{recepteur}[/red]", duree, date]

        if not vocal_lu and appel.get('vocal'):
            ligne = [f"[red]{val}[/red]" for val in ligne]

        data.append(tuple(ligne))

    if not data:
        afficher_message("Aucun appel dans l'historique.")
    else:
        afficher_tableau(data, headers=["Émetteur", "Récepteur", "Durée", "Date"])


def rechercher_contact(client, mot_cle: str):
    from Controllers.client_controller import rechercher_contact as controller_rechercher_contact
    """
    Recherche un contact dans le répertoire via le contrôleur et affiche les résultats.
    """
    try:
        resultats = controller_rechercher_contact(client, mot_cle)
        if not resultats:
            afficher_message("Aucun contact trouvé pour ce mot-clé.")
        else:
            afficher_titre("Résultats de la recherche")
            data = [
                (i + 1, nom, ", ".join(details.get("numeros", [])))
                for i, (nom, details) in enumerate(resultats.items())
            ]
            afficher_tableau(data, headers=["#", "Nom du contact", "Numéros"])
    except ValueError as e:
        afficher_erreur(str(e))

def afficher_vocaux(historique: List[dict]):
    """
    Affiche l'historique des vocaux avec une couleur distinctive pour les vocaux non lus.
    Les vocaux non lus sont affichés en rouge, les vocaux lus en vert.
    """
    vocaux = [appel for appel in historique if appel.get('vocal')]
    if not vocaux:
        afficher_message("Aucun vocal disponible.")
        return

    # Préparer les données à afficher
    data = []
    for appel in vocaux:
        etat = "[red]Non lu[/red]" if not appel.get('vocal_lu') else "[green]Lu[/green]"
        data.append((appel['id'], appel['date'], etat))

    # Afficher le tableau
    afficher_titre("Historique des Vocaux")
    afficher_tableau(data, headers=["ID", "Date", "État"])


def selectionner_contact(client: Client, repertoire: Dict[str, dict]):
    """
    Permet à l'utilisateur de sélectionner un contact pour appeler.
    Si le contact a plusieurs numéros, l'utilisateur doit en sélectionner un.
    L'appel est lancé automatiquement après la sélection.
    """
    while True:
        choix = input("Tapez la position pour appeler [Q pour quitter] : ").strip()
        if choix.upper() == "Q":
            afficher_message("Opération annulée.")
            return

        try:
            position = int(choix) - 1
            if 0 <= position < len(repertoire):
                contacts = list(repertoire.keys())
                contact = contacts[position]
                numeros = repertoire[contact].get("numeros", [])

                if len(numeros) > 1:
                    numero = selectionner_numero(numeros)
                    if not numero:
                        continue
                elif len(numeros) == 1:
                    numero = numeros[0]
                else:
                    afficher_erreur(f"Le contact '{contact}' n'a aucun numéro.")
                    continue

                afficher_message(f"Appel de {client.numero} vers ({numero}).")
                Client.lancer_appel(client.numero, numero)
                afficher_message(f"Appel vers {contact} ({numero}) terminé.")
                return
            else:
                afficher_erreur("Position invalide. Veuillez réessayer.")
        except ValueError:
            afficher_erreur("Entrée invalide. Veuillez entrer un nombre ou 'Q' pour quitter.")

def selectionner_numero(numeros: List[str]) -> Optional[str]:
    """
    Permet à l'utilisateur de sélectionner un numéro si le contact en a plusieurs.
    """
    while True:
        print("\nNuméros disponibles :")
        for i, numero in enumerate(numeros, start=1):
            print(f"{i}. {numero}")

        choix = input("Lequel appeler [Q pour quitter] : ").strip()
        if choix.upper() == "Q":
            return None

        try:
            index = int(choix) - 1
            if 0 <= index < len(numeros):
                return numeros[index]
            else:
                afficher_erreur("Position invalide. Veuillez réessayer.")
        except ValueError:
            afficher_erreur("Entrée invalide. Veuillez entrer un nombre ou 'Q' pour quitter.")

def afficher_resultat_achat_credit(montant):
    """
    Affiche un message confirmant l'achat de crédit.
    """
    afficher_message(f"Achat de crédit réussi : {montant} FCFA ajouté à votre solde.")

def afficher_resultat_transfert_credit(montant, numero_cible):
    """
    Affiche un message confirmant le transfert de crédit.
    """
    afficher_message(f"Transfert de {montant} FCFA au numéro {numero_cible} réussi.")
def renommer_contact_menu(client):
    """
    Permet au client de renommer un contact dans son répertoire.
    """
    try:
        ancien_nom = input("Entrez le nom du contact à renommer : ").strip()
        nouveau_nom = input("Entrez le nouveau nom pour ce contact : ").strip()
        client.renommer_contact(ancien_nom, nouveau_nom)
        print(f"Le contact '{ancien_nom}' a été renommé en '{nouveau_nom}'.")
    except Exception as e:
        print(f"Erreur : {e}")
def rechercher_contact_menu(client):
    """
    Permet au client de rechercher un contact dans son répertoire.
    """
    try:
        mot_cle = input("Entrez un mot-clé pour rechercher un contact : ").strip()
        rechercher_contact(client.repertoire, mot_cle)
    except Exception as e:
        print(f"Erreur : {e}")
def afficher_vocaux_menu(client):
    """
    Affiche les vocaux disponibles pour le client.
    """
    try:
        historique = Client.voir_historique(client.numero)
        afficher_vocaux(historique)
    except Exception as e:
        print(f"Erreur : {e}")
