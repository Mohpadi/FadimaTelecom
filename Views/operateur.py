from Views.functions import afficher_message, afficher_titre, afficher_tableau, afficher_erreur
from Models.transactions import Transaction
from Models.client import Client

def afficher_operateurs(operateurs):
    """
    Affiche la liste des opérateurs et leurs index avec style et pagination.
    """
    afficher_titre("Liste des opérateurs")
    data = [(i + 1, op.nom, ", ".join(op.index)) for i, op in enumerate(operateurs)]

    if not data:
        afficher_message("Aucun opérateur enregistré.")
    else:
        afficher_tableau(data, headers=["#", "Nom", "Index"])

def afficher_numeros_operateur(numeros, operateur):
    """
    Affiche les numéros associés à un opérateur, organisés par index.
    Les numéros sont affichés en groupes de 10 par ligne.
    Les numéros vendus (associés à un client) sont affichés en rouge, et ceux disponibles en vert.
    """
    afficher_titre(f"Liste complète des numéros de l'opérateur {operateur}")

    data = []
    for index, num_list in numeros.items():
        lignes = []
        ligne_courante = []
        for i, numero in enumerate(num_list, start=1):
            client = Client.lire_par_numero(numero)  # Vérifie si le numéro est vendu
            if client:
                ligne_courante.append(f"[red]{numero}[/red]")  # Numéro vendu
            else:
                ligne_courante.append(f"[green]{numero}[/green]")  # Numéro disponible
            
            # Ajouter la ligne courante après 10 numéros ou si c'est le dernier numéro
            if len(ligne_courante) == 16 or i == len(num_list):
                lignes.append(" ".join(ligne_courante))
                ligne_courante = []

        data.append((index, "\n".join(lignes)))  # Ajouter les lignes formatées pour chaque index

    if not data:
        afficher_message("Aucun numéro disponible pour cet opérateur.")
    else:
        afficher_tableau(data, headers=["Index", "Numéros"])  # Affiche un tableau complet

def choisir_operateur(operateurs):
    """
    Affiche la liste des opérateurs et permet à l'utilisateur de choisir un opérateur.
    :return: L'opérateur sélectionné.
    """
    afficher_titre("Choisir un opérateur")
    data = [(i + 1, op.nom, ", ".join(op.index)) for i, op in enumerate(operateurs)]

    if not data:
        afficher_message("Aucun opérateur enregistré.")
        return None

    afficher_tableau(data, headers=["#", "Nom", "Index"])
    choix = input("Choisissez un opérateur selon sa position : ")
    try:
        choix = int(choix) - 1
        if 0 <= choix < len(operateurs):
            return operateurs[choix]
        else:
            afficher_erreur("Choix invalide.")
            return None
    except ValueError:
        afficher_erreur("Veuillez entrer un numéro valide.")
        return None

def choisir_index(operateur):
    """
    Affiche la liste des index d'un opérateur et permet à l'utilisateur de choisir un index.
    :param operateur: Une instance d'Operateur contenant le nom et la liste des index.
    :return: L'index sélectionné ou None si l'utilisateur annule ou fait un mauvais choix.
    """
    if not hasattr(operateur, "nom") or not hasattr(operateur, "index"):
        afficher_erreur("Opérateur invalide. Assurez-vous que l'opérateur est correctement défini.")
        return None

    afficher_titre(f"Choisir un index pour {operateur.nom}")
    data = [(i + 1, index) for i, index in enumerate(operateur.index)]
    if not data:
        afficher_message(f"Aucun index disponible pour l'opérateur {operateur.nom}.")
        return None

    afficher_tableau(data, headers=["#", "Index"])
    choix = input("Choisissez un index (numéro) ou 'q' pour annuler : ")

    try:
        if choix.lower() == 'q':
            afficher_message("Action annulée par l'utilisateur.")
            return None

        choix = int(choix) - 1
        if 0 <= choix < len(operateur.index):
            return operateur.index[choix]
        else:
            afficher_erreur("Choix invalide. Veuillez sélectionner un numéro valide.")
            return None
    except ValueError:
        afficher_erreur("Veuillez entrer un numéro valide ou 'q' pour annuler.")
        return None

def choisir_numero(operateur, index):
    """
    Affiche la liste des numéros d'un index et permet à l'utilisateur de choisir un numéro.
    :param operateur: L'opérateur sélectionné.
    :param index: L'index pour lequel afficher les numéros.
    :return: Le numéro sélectionné ou None.
    """
    afficher_titre(f"Choix d'un numéro pour l'index {index}")

    numeros = operateur.numeros.get(index, [])

    if not numeros:
        afficher_message("Aucun numéro disponible pour cet index.")
        return None

    # Pagination et affichage amélioré
    lignes_par_page = 5  # 5 lignes affichées par page
    numeros_par_ligne = 10  # 10 numéros par ligne
    total_pages = (len(numeros) + (lignes_par_page * numeros_par_ligne) - 1) // (lignes_par_page * numeros_par_ligne)
    current_page = 0

    while True:
        start = current_page * lignes_par_page * numeros_par_ligne
        end = start + (lignes_par_page * numeros_par_ligne)
        numeros_page = numeros[start:end]

        # Afficher les numéros avec une numérotation continue
        print("\n" + "=" * 50)
        print(f"Page {current_page + 1}/{total_pages}")
        print("=" * 50)

        for i, num in enumerate(numeros_page, start=start + 1):
            print(f"{i:3}. {num}", end="  ")
            if (i - start) % numeros_par_ligne == 0:  # Retour à la ligne tous les 10 numéros
                print()

        if len(numeros_page) % numeros_par_ligne != 0:  # S'assurer que la dernière ligne est bien terminée
            print()
        print("=" * 50)

        if total_pages > 1:
            print("[P] Précédent  |  [S] Suivant  |  [Q] Quitter")

        choix = input("Choisissez une position ou une action : ").strip().lower()

        # Navigation dans les pages
        if choix == 'q':
            return None
        elif choix == 'p' and current_page > 0:
            current_page -= 1
        elif choix == 's' and current_page < total_pages - 1:
            current_page += 1
        else:
            try:
                choix_numero = int(choix) - 1
                if start <= choix_numero < end:
                    return numeros[choix_numero]
                else:
                    afficher_erreur("Choix invalide, veuillez réessayer.")
            except ValueError:
                afficher_erreur("Entrée invalide, veuillez entrer un numéro ou une action.")


def afficher_numeros_par_colonnes(numeros, colonnes=10):
    """
    Affiche les numéros en colonnes.
    :param numeros: Liste des numéros à afficher.
    :param colonnes: Nombre de colonnes (par défaut 10).
    """
    lignes = [numeros[i:i + colonnes] for i in range(0, len(numeros), colonnes)]
    tableau = []
    for ligne in lignes:
        tableau.append(["{:2}. {}".format(i + 1, numero) for i, numero in enumerate(ligne)])

    max_colonne_largeur = max(len(cell) for row in tableau for cell in row)
    tableau_format = "\n".join(
        " | ".join(cell.ljust(max_colonne_largeur) for cell in row)
        for row in tableau
    )
    print(tableau_format)

def afficher_resume_vente(numero, client_nom):
    """
    Affiche un résumé de la vente d'un numéro.
    """
    afficher_titre("Résumé de la vente")
    data = [
        ("Numéro vendu", numero),
        ("Client associé", client_nom if client_nom else "Client inconnu")
    ]
    afficher_tableau(data, headers=["Détail", "Valeur"])

def afficher_etat_caisse(etat):
    """
    Affiche l’état de la caisse (journalier, mensuel, annuel) avec style.
    """
    afficher_titre("État de la caisse")
    if not etat:
        afficher_message("Aucune transaction enregistrée.")
        return

    # Préparer les données pour le tableau
    data = [
        (operateur if operateur else "Non défini", f"{montant} FCFA", description)
        for operateur, montant, description in etat
    ]

    # Afficher le tableau avec les colonnes ajoutées
    afficher_tableau(
        data, headers=["Opérateur", "Montant", "Description"]
    )



def confirmer_action(message):
    """
    Demande une confirmation avant de poursuivre une action critique.
    """
    choix = input(f"{message} (o/n) : ").strip().lower()
    return choix == 'o'
def afficher_menu():
    """
    Affiche un menu pour sélectionner la période.
    """
    print("\n=== Menu Périodes ===")
    options = ["1. État journalier", "2. État mensuel", "3. État annuel", "0. Annuler"]
    for option in options:
        print(option)
    print("=====================\n")
    return options

def choisir_periode():
    """
    Permet à l'utilisateur de choisir une période en fonction de la position dans le menu.
    :return: Une chaîne représentant la période choisie.
    """
    afficher_menu()
    choix = input("Veuillez sélectionner une option : ").strip()

    if choix == "1":
        return "journalier"
    elif choix == "2":
        return "mensuel"
    elif choix == "3":
        return "annuel"
    elif choix == "0":
        exit(0)
    else:
        print("Option invalide. Veuillez choisir un nombre entre 1 et 3.")
        return choisir_periode()  # Répéter jusqu'à obtenir un choix valide