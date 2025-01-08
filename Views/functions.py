from rich.console import Console
from rich.table import Table

console = Console()

def afficher_titre(titre):
    """
    Affiche un titre formaté pour les sections avec couleur.
    """
    console.print(f"\n[turquoise4 bold]{titre.upper()}[/turquoise4 bold]\n", justify="center")

def afficher_message(message):
    """
    Affiche un message générique avec couleur.
    """
    console.print(f"[green]{message}[/green]")

def afficher_erreur(message):
    """
    Affiche un message d'erreur avec couleur.
    """
    console.print(f"[red]{message}[/red]")

def choisir_type_utilisateur():
    """
    Affiche les types d'utilisateur disponibles et permet à l'utilisateur de faire un choix.
    :return: Le type d'utilisateur choisi ('gestionnaire' ou 'client').
    """
    types_utilisateurs = ["gestionnaire", "client"]
    print("Veuillez choisir un type d'utilisateur :")
    for i, type_user in enumerate(types_utilisateurs, 1):
        print(f"{i}. {type_user}")

    choix = input("Entrez le numéro correspondant à votre choix : ")
    try:
        choix = int(choix) - 1
        if 0 <= choix < len(types_utilisateurs):
            return types_utilisateurs[choix]
        else:
            print("Choix invalide. Veuillez réessayer.")
            return choisir_type_utilisateur()
    except ValueError:
        print("Entrée invalide. Veuillez entrer un numéro.")
        return choisir_type_utilisateur()

def afficher_tableau(data, headers, title="", lignes_par_page=10):
    """
    Affiche une liste de données sous forme de tableau avec pagination.
    :param data: Liste des tuples contenant les données.
    :param headers: Liste des en-têtes de colonnes.
    :param title: Titre optionnel pour le tableau.
    :param lignes_par_page: Nombre de lignes à afficher par page.
    """
    if not data:
        console.print("[yellow]Aucune donnée à afficher.[/yellow]")
        return

    total_lignes = len(data)
    pages = (total_lignes + lignes_par_page - 1) // lignes_par_page  # Calcul du nombre de pages

    for page in range(pages):
        start = page * lignes_par_page
        end = start + lignes_par_page
        page_data = data[start:end]

        table = Table(title=f"{title} (Page {page + 1}/{pages})", show_header=True, header_style="bold magenta")
        for header in headers:
            table.add_column(header)

        for row in page_data:
            table.add_row(*[str(item) for item in row])

        console.print(table)

        # Afficher une pause entre les pages sauf pour la dernière
        if page < pages - 1:
            console.print("[yellow]Appuyez sur Entrée pour continuer...[/yellow]")
            input()