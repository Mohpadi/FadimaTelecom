from Controllers.admin_controller import ajouter_utilisateur
from Controllers.operateur_controller import (
    lister_numeros_operateur,
    lister_operateurs,
    vendre_numero,
    se_connecter_gestionnaire,
    creer_operateur,
    renommer_operateur,
    ajouter_index,
    supprimer_index,
    vendre_credit_client,
    etat_caisse
)
from Controllers.client_controller import (
    changer_pin,
    ecouter_vocal,
    se_connecter_client,
    verifier_solde,
    ajouter_contact,
    supprimer_contact,
    transferer_credit,
    acheter_credit,
    effectuer_appel,
    bloquer_contact,
    debloquer_contact,
    supprimer_vocal
)
from Models.operateur import Operateur
from Views.client import (
    afficher_historique_appels,
    afficher_vocaux_menu,
    appeler_depuis_repertoire,
    rechercher_contact as afficher_recherche_contact,
    afficher_credit,
    renommer_contact_menu
)
from Views.operateur import (
    afficher_operateurs,
    afficher_numeros_operateur,
    afficher_etat_caisse,
    choisir_periode,
    confirmer_action
)
from Views.functions import afficher_message, afficher_erreur

def menu_client(client):
    """
    Menu principal pour les clients avec actions regroupées.
    """
    while True:
        print("\n=== Menu Client ===")
        print("1. Mon Compte")
        print("2. Contacts")
        print("3. Appels")
        print("4. Crédit")
        print("5. Vocaux")
        print("0. Déconnexion")
        choix = input("Choisissez une option : ").strip()

        try:
            if choix == "1":  # Mon Compte
                menu_mon_compte(client)
            elif choix == "2":  # Contacts
                menu_contacts(client)
            elif choix == "3":  # Appels
                menu_appels(client)
            elif choix == "4":  # Crédit
                menu_credit(client)
            elif choix == "5":  # Vocaux
                menu_vocaux(client)
            elif choix == "0":  # Déconnexion
                print("Déconnexion en cours...")
                break
            else:
                print("Choix invalide. Veuillez réessayer.")
        except Exception as e:
            print(f"Erreur : {e}")
def menu_mon_compte(client):
    while True:
        print("\n=== Mon Compte ===")
        print("1. Vérifier le solde")
        print("2. Modifier le PIN")
        print("0. Retour")
        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            verifier_solde(client)
        elif choix == "2":
            ancien_pin = input("Entrez votre ancien PIN : ").strip()
            try:
                changer_pin(client, ancien_pin)
            except ValueError as e:
                print(f"Erreur : {e}")
            except FileNotFoundError as e:
                print(f"Erreur : {e}")
            except Exception as e:
                print(f"Une erreur inattendue est survenue : {e}")



        elif choix == "0":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
def menu_contacts(client):
    while True:
        print("\n=== Contacts ===")
        print("1. Ajouter un contact")
        print("2. Afficher le répertoire")
        print("3. Rechercher un contact")
        print("4. Renommer un contact")
        print("5. Bloquer/Débloquer un contact")
        print("6. Supprimer un contact")
        print("0. Retour")
        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            nom = input("Entrez le nom du contact : ").strip()
            numeros = input("Entrez le numero ou les numéros séparés par des virgules : ").strip().split(",")
            ajouter_contact(client.numero, nom, numeros)
        elif choix == "2":
            appeler_depuis_repertoire(client)
        elif choix == "3":
            mot_cle = input("Entrez le nom pour la recherche : ").strip()
            afficher_recherche_contact(client, mot_cle)
        elif choix == "4":
            renommer_contact_menu(client)
        elif choix == "5":
            nom = input("Entrez le nom du contact à bloquer/débloquer : ").strip()
            if nom in client.repertoire:
                if client.repertoire[nom].get("bloque", False):
                    debloquer_contact(client.numero, nom)
                else:
                    bloquer_contact(client.numero, nom)
            else:
                print("Contact introuvable.")
        elif choix == "6":
            nom = input("Entrez le nom du contact à supprimer : ").strip()
            if confirmer_action(f"Voulez-vous vraiment supprimer le contact '{nom}' ?"):
                supprimer_contact(client.numero, nom)
        elif choix == "0":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
def menu_appels(client):
    while True:
        print("\n=== Appels ===")
        print("1. Passer un appel")
        print("2. Voir l'historique des appels")
        print("0. Retour")
        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            numero_cible = input("Entrez le numéro à appeler : ").strip()
            effectuer_appel(client.numero, numero_cible)
        elif choix == "2":
            historique = client.voir_historique(client.numero)
            afficher_historique_appels(historique, client.numero)
        elif choix == "0":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
def menu_credit(client):
    while True:
        print("\n=== Crédit ===")
        print("1. Acheter du crédit")
        print("2. Transférer du crédit")
        print("0. Retour")
        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            montant = float(input("Entrez le montant à ajouter : ").strip())
            acheter_credit(client.numero, montant)
        elif choix == "2":
            cible_numero = input("Entrez le numéro du destinataire : ").strip()
            montant = float(input("Entrez le montant à transférer : ").strip())
            transferer_credit(client.numero, cible_numero, montant)
            print(f"Transfert de {montant} FCFA au numéro {cible_numero} réussi.")
        elif choix == "0":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
def menu_vocaux(client):
    while True:
        print("\n=== Vocaux ===")
        print("1. Afficher les vocaux")
        print("2. Lire un vocal")
        print("3. Supprimer un vocal")
        print("0. Retour")
        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            afficher_vocaux_menu(client)
        elif choix == "2":
            ecouter_vocal(client)
        elif choix == "3":
            vocal_id = int(input("Entrez l'ID du vocal à supprimer : ").strip())
            if confirmer_action("Voulez-vous vraiment supprimer ce vocal ?"):
                supprimer_vocal(client.numero, vocal_id)
        elif choix == "0":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def menu_gestionnaire():
    """
    Menu principal pour les gestionnaires.
    """
    while True:
        print("\n=== Menu Gestionnaire ===")
        print("1. Créer un opérateur")
        print("2. Renommer un opérateur")
        print("3. Ajouter un index à un opérateur")
        print("4. Supprimer un index d'un opérateur")
        print("5. Lister les opérateurs")
        print("6. Lister les numéros d'un opérateur")
        print("7. Vendre un numéro")
        print("8. Vendre du crédit à un client")
        print("9. Voir l'état de la caisse")
        print("0. Déconnexion")
        choix = input("Choisissez une option : ").strip()

        try:
            if choix == "1":
                nom = input("Entrez le nom du nouvel opérateur : ").strip()
                index = input("Entrez le premier index de l'opérateur : ").strip()
                creer_operateur(nom, index)
                afficher_message(f"Opérateur '{nom}' créé avec succès.")
            elif choix == "2":
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
                ancien_nom = input("Entrez le nom actuel de l'opérateur : ").strip()
                nouveau_nom = input("Entrez le nouveau nom de l'opérateur : ").strip()
                renommer_operateur(ancien_nom, nouveau_nom)
                afficher_message(f"Opérateur renommé en '{nouveau_nom}'.")
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
            elif choix == "3":
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
                nom = input("Entrez le nom de l'opérateur : ").strip()
                nouvel_index = input("Entrez le nouvel index : ").strip()
                ajouter_index(nom, nouvel_index)
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
            elif choix == "4":
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
                nom = input("Entrez le nom de l'opérateur : ").strip()
                index_a_supprimer = input("Entrez l'index à supprimer : ").strip()
                if confirmer_action(f"Voulez-vous vraiment supprimer l'index '{index_a_supprimer}' ?"):
                    supprimer_index(nom, index_a_supprimer)
                    operateurs = lister_operateurs()
                    afficher_operateurs(operateurs)
            elif choix == "5":
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
            elif choix == "6":
                operateurs = lister_operateurs()
                afficher_operateurs(operateurs)
                nom = input("Entrez le nom de l'opérateur : ").strip()
                numeros = lister_numeros_operateur(nom)
                afficher_numeros_operateur(numeros, nom)
            elif choix == "7":
                vendre_numero()
            elif choix == "8":
                numero_client = input("Entrez le numéro du client : ").strip()
                montant = float(input("Entrez le montant de crédit à ajouter : ").strip())
                vendre_credit_client(numero_client, montant)
            elif choix == "9":
                periode = choisir_periode()
                etat = etat_caisse(periode)
                afficher_etat_caisse(etat)
            elif choix == "0":
                afficher_message("Déconnecté !")
                break
            else:
                afficher_erreur("Choix invalide. Veuillez réessayer.")
        except Exception as e:
            afficher_erreur(f"Erreur : {e}")
def menu_principal():
    """
    Affiche le menu principal pour choisir entre ajouter un utilisateur, se connecter en tant que gestionnaire ou client.
    """
    while True:
        print("\n=== Menu Principal ===")
        print("1. Ajouter un utilisateur")
        print("2. Se connecter en tant que gestionnaire")
        print("3. Se connecter en tant que client")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            ajouter_utilisateur_menu()
        elif choix == "2":
            se_connecter_gestionnaire_menu()
        elif choix == "3":
            se_connecter_client_menu()
        elif choix == "0":
            print("Merci d'avoir utilisé la plateforme FatimaTelecom. Au revoir!")
            break
        else:
            afficher_erreur("Choix invalide. Veuillez réessayer.")

def ajouter_utilisateur_menu():
    """
    Permet d'ajouter un utilisateur (gestionnaire ou client).
    """
    print("\n=== Ajouter un Utilisateur ===")
    print("1. Gestionnaire")
    print("2. Client")
    print("0. Retour")
    choix_ajout = input("Votre choix : ").strip()

    if choix_ajout == "1":
        print("\nCréation d'un nouveau gestionnaire")
        usertype = "gestionnaire"
        nom = input("Entrez le nom du gestionnaire : ").strip()
        identifiant = input("Entrez un identifiant unique : ").strip()
        pin = input("Entrez un PIN : ").strip()
        try:
            ajouter_utilisateur(usertype, identifiant, nom, pin)
        except Exception as e:
            afficher_erreur(f"Erreur lors de l'ajout du gestionnaire : {e}")

    elif choix_ajout == "2":
        print("\nCréation d'un nouveau client")
        usertype = "client"
        nom = input("Entrez le nom du client (laissez vide si anonyme) : ").strip()
        numero = input("Entrez un numéro unique : ").strip()
        pin = input("Entrez le PIN : ").strip()
        try:
            ajouter_utilisateur(usertype, numero, nom, pin)
        except Exception as e:
            afficher_erreur(f"Erreur lors de l'ajout du client : {e}")

    elif choix_ajout == "0":
        afficher_message("Retour au menu principal.")
    else:
        afficher_erreur("Choix invalide pour le type d'utilisateur à ajouter.")

def se_connecter_gestionnaire_menu():
    """
    Permet à un gestionnaire de se connecter et d'accéder à ses fonctionnalités.
    """
    try:
        identifiant = input("Entrez votre identifiant : ").strip()
        pin = input("Entrez votre PIN : ").strip()
        gestionnaire = se_connecter_gestionnaire(identifiant, pin)
        afficher_message(f"Bienvenue, {gestionnaire['nom']}!")
        menu_gestionnaire()
    except Exception as e:
        afficher_erreur(f"Erreur de connexion : {e}")

def se_connecter_client_menu():
    """
    Permet à un client de se connecter et d'accéder à ses fonctionnalités.
    """
    try:
        numero = input("Entrez votre numéro : ").strip()
        pin = input("Entrez votre PIN : ").strip()
        client = se_connecter_client(numero, pin)
        afficher_message(f"Bienvenue, {client.nom if client.nom else client.numero}!")
        menu_client(client)
    except Exception as e:
        afficher_erreur(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    print("Bienvenue sur la plateforme FatimaTelecom!")
    menu_principal()