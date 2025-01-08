import json
import os
from Models.transactions import Transaction
from Views.functions import afficher_message
from constants import INDEX_LENGTH, MAX_INDEX, MAX_NOM_OPERATEUR, MIN_INDEX, MIN_NOM_OPERATEUR, NUMERO_LENGTH
from Models.client import Client
# Fichier centralisé pour tous les opérateurs
OPERATEURS_FILE = "BD/operateurs.txt"
CLIENTS_FILE = "BD/clients.txt"

class Operateur:
    def __init__(self, nom, index, numeros=None):
        self.nom = nom
        # Assurer que `index` est bien une liste
        if not isinstance(index, list):
            raise ValueError(f"index doit être une liste, mais il est de type {type(index)}")
        self.index = index
        # Assurer que `numeros` est bien un dictionnaire
        if not isinstance(numeros, dict):
            raise ValueError(f"numeros doit être un dictionnaire, mais il est de type {type(numeros)}")
        self.numeros = numeros
    def __repr__(self):
        return f"Operateur(nom={self.nom}, index={self.index})"

    def __str__(self):
        return f"Operateur: {self.nom}, Index: {self.index}, Numéros: {len(self.numeros)} groupes"


    @staticmethod
    def valider_nom_operateur(nom):
        if not (MIN_NOM_OPERATEUR <= len(nom) <= MAX_NOM_OPERATEUR):
            raise ValueError("Le nom de l'opérateur doit avoir entre 3 et 15 caractères.")

    @staticmethod
    def valider_index(index):
        """
        Valide que l'index est une liste de 1 à 3 indices de 2 chiffres.
        """
        # Assurez-vous que l'index est une liste
        if isinstance(index, str):
            index = [index]
        
        if not (MIN_INDEX <= len(index) <= MAX_INDEX):
            raise ValueError("Un opérateur peut avoir entre 1 et 3 indices.")
        
        for idx in index:
            if not (idx.isdigit() and len(idx) == INDEX_LENGTH):
                raise ValueError("Chaque index doit être un nombre de 2 chiffres.")

    @staticmethod
    def valider_numero(numero):
        """
        Valide qu'un numéro respecte la règle suivante :
        - Le numéro et l'index de l'opérateur combinés ne doivent pas dépasser 7 chiffres.
        """
        # Vérifie que la chaîne ne contient que des chiffres
        if not numero.isdigit():
            raise ValueError(f"Numéro invalide : {numero}. Le numéro ne doit contenir que des chiffres.")
        
        # Vérifie que la longueur totale ne dépasse pas 7 chiffres
        if len(numero) > NUMERO_LENGTH:
            raise ValueError(f"Numéro invalide : {numero}. Le numéro ne doit pas dépasser 7 chiffres (index inclus).")
    @staticmethod
    def creer(nom, index):
        Operateur.valider_nom_operateur(nom)
        Operateur.valider_index(index)
        
        numeros = {}
        for idx in index:
            # Calculer la longueur du numéro en fonction de l'index
            longueur_numero = NUMERO_LENGTH - len(idx)
            # Générer des numéros de la longueur appropriée
            numeros[idx] = [f"{idx}{str(i).zfill(longueur_numero)}" for i in range(100)]

        op = Operateur(nom, index, numeros)
        Operateur.sauvegarder_operateur(op)

    @staticmethod
    def sauvegarder_operateur(operateur):
        """Sauvegarde un opérateur dans le fichier centralisé."""
        operateurs = Operateur.lister_operateurs()

        # Mettre à jour ou ajouter l'opérateur dans le dictionnaire des opérateurs
        operateurs_dict = {op.nom: {'index': op.index, 'numeros': op.numeros} for op in operateurs}
        # Si un ancien nom est fourni, supprimer l'entrée correspondante

        # Ajouter l'opérateur actuel dans le dictionnaire
        operateurs_dict[operateur.nom] = {
            'index': operateur.index,
            'numeros': operateur.numeros
        }

        # Sauvegarder les opérateurs dans le fichier
        with open(OPERATEURS_FILE, 'w') as f:
            json.dump(operateurs_dict, f, indent=4)  # Utilisation de indent=4 pour un format lisible
    @staticmethod
    def renommer_operateur(ancien_nom, nouveau_nom):
        """
        Renomme un opérateur existant sans effacer les données associées.
        """
        # Charger les opérateurs depuis le fichier
        operateurs = Operateur.lister_operateurs()

        # Convertir en dictionnaire pour accéder facilement aux opérateurs
        operateurs_dict = {op.nom: {'index': op.index, 'numeros': op.numeros} for op in operateurs}

        # Vérifier l'existence de l'ancien opérateur
        if ancien_nom not in operateurs_dict:
            raise ValueError(f"L'opérateur '{ancien_nom}' n'existe pas.")

        # Vérifier si le nouveau nom est déjà utilisé
        if nouveau_nom in operateurs_dict:
            raise ValueError(f"Un opérateur avec le nom '{nouveau_nom}' existe déjà.")

        # Renommer l'opérateur
        operateurs_dict[nouveau_nom] = operateurs_dict.pop(ancien_nom)

        # Sauvegarder les opérateurs modifiés
        with open(OPERATEURS_FILE, 'w') as f:
            json.dump(operateurs_dict, f, indent=4)

        afficher_message(f"Opérateur renommé de '{ancien_nom}' à '{nouveau_nom}'.")

    @staticmethod
    def lister_operateurs():
        """Récupère tous les opérateurs depuis le fichier centralisé."""
        if os.path.exists(OPERATEURS_FILE):
            with open(OPERATEURS_FILE, 'r') as f:
                raw_data = json.load(f)  # Charger les données brutes

            # Créer une liste d'instances d'Operateur
            return [
                Operateur(
                    nom=key,
                    index=list(value.get("numeros", {}).keys()),  # Les index sont les clés de "numeros"
                    numeros=value.get("numeros", {})
                )
                for key, value in raw_data.items()
            ]
        return []

    @staticmethod
    def lire_par_nom(nom):
        """Récupère un opérateur par son nom depuis la liste retournée par lister_operateurs."""
        operateurs = Operateur.lister_operateurs()
        for operateur in operateurs:
            if operateur.nom == nom:
                return operateur
        return None

    
    def mettre_a_jour(self):
        """Met à jour les données de l'opérateur dans le fichier centralisé."""
        Operateur.sauvegarder_operateur(self)

    def ajouter_index(self, nouvel_index):
        """Ajoute un index à l'opérateur après validation."""
        try:
            # Validation de l'index
            if not (nouvel_index.isdigit() and len(nouvel_index) == INDEX_LENGTH):
                raise ValueError(f"L'index {nouvel_index} est invalide. Un index doit être un nombre de {INDEX_LENGTH} chiffres.")

            if len(self.index) >= MAX_INDEX:
                raise ValueError("L'opérateur a déjà le nombre maximal d'indices.")

            if nouvel_index in self.index:
                raise ValueError(f"L'index {nouvel_index} existe déjà pour cet opérateur.")

            # Vérifier si l'index est déjà utilisé par un autre opérateur
            operateurs = Operateur.lister_operateurs()  # Liste d'instances d'Operateur
            for op in operateurs:
                if nouvel_index in op.index:  # Accès à l'attribut `index` de l'objet `Operateur`
                    raise ValueError(f"L'index {nouvel_index} existe déjà dans un autre opérateur ({op.nom}).")

            # Ajouter l'index à la liste
            self.index.append(nouvel_index)

            # Générer les numéros pour cet index
            self.numeros[nouvel_index] = self.generer_numeros_pour_index(nouvel_index)

            # Persister les modifications
            self.mettre_a_jour()
            
            afficher_message(f"L'index {nouvel_index} a été ajouté avec succès à l'opérateur {self.nom}.")
        
        except ValueError as e:
            afficher_message(f"Erreur : {e}")
        except Exception as e:
            afficher_message(f"Une erreur inattendue s'est produite : {e}")


    def generer_numeros_pour_index(self, index):
        """
        Génère une liste de numéros pour un index donné.
        """
        longueur_numero = NUMERO_LENGTH - len(index)
        return [f"{index}{str(i).zfill(longueur_numero)}" for i in range(100)]

    def supprimer_index(self, index_a_supprimer):
        """
        Supprime un index s'il n'est pas utilisé par des clients.
        - Vérifie que l'index appartient à l'opérateur.
        - Vérifie que l'index n'est pas utilisé par des clients (dans DB/clients.py).
        - Supprime l'index et ses numéros du fichier operateurs.txt.
        """
        # Vérifie que l'index appartient à l'opérateur
        if index_a_supprimer not in self.index:
            raise ValueError(f"L'index {index_a_supprimer} n'existe pas.")

        # Charge les données des clients depuis DB/clients.py
        try:
            with open(CLIENTS_FILE, "r") as fichier_clients:
                clients = json.load(fichier_clients)  # Chargement en tant que dict
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError("Le fichier des clients est introuvable ou corrompu.")

        # Vérifie si l'index est utilisé par des clients
        for numero_client, infos_client in clients.items():  # Parcourt clé/valeur
            # Vérifie si le numéro du client commence par l'index
            if numero_client.startswith(index_a_supprimer):
                raise ValueError(f"L'index {index_a_supprimer} est utilisé par le client {numero_client}.")

        # Supprime l'index et ses numéros
        self.index.remove(index_a_supprimer)
        del self.numeros[index_a_supprimer]

        # Met à jour le fichier operateurs.txt
        self.mettre_a_jour()
        afficher_message(f"L'index {index_a_supprimer} a été supprimé avec succès.")



    def vendre_numero(self, index, numero, client_nom=None):
        """Marque un numéro comme vendu et l'attribue à un client."""
        # Vérification de `self.index`
        if index not in self.index:
            raise ValueError(f"L'index {index} n'existe pas.")
        
        # Vérification de l'existence du numéro
        if numero not in self.numeros.get(index, []):
            raise ValueError(f"Le numéro {numero} n'existe pas pour l'index {index}.")
        
        # Vérifier si le numéro est déjà attribué à un client
        try:
            client = Client.lire_par_numero(numero)
            if client:
                raise ValueError(f"Le numéro {numero} est déjà attribué à un autre client.")
            else:
                Client.creer_client(numero,client_nom)
        except FileNotFoundError:
            raise ValueError("Le fichier des clients est introuvable.")
        
        # Retirer le numéro de la liste
        if numero in self.numeros[index]:
            self.numeros[index].remove(numero)
        else:
            raise ValueError(f"Le numéro {numero} n'est pas disponible pour être retiré.")

        # Enregistrer la vente
        client_nom = client_nom if client_nom else "Client inconnu"
        try:
            Transaction("vente_numero", self.nom, 500, f"Vente du numéro {numero} à {client_nom}").sauvegarder()
        except Exception as e:
            raise ValueError(f"Erreur lors de la sauvegarde de la transaction: {e}")

        # Mettre à jour l'état de l'opérateur
        self.mettre_a_jour()
        
        # Logique de la vente
        afficher_message(f"Numéro {numero} vendu à {client_nom} avec succès. Pin par defaut 0000. Veuillez le changer")
        return f"Numéro '{numero}' vendu avec succès. Client associé : {client_nom}."
def supprimer_operateur(nom_operateur):
    """
    Supprime un opérateur existant du fichier centralisé.
    """
    # Charger les opérateurs depuis le fichier
    operateurs = Operateur.lister_operateurs()

    # Convertir en dictionnaire pour simplifier la manipulation
    operateurs_dict = {op.nom: {'index': op.index, 'numeros': op.numeros} for op in operateurs}

    # Vérifier si l'opérateur existe
    if nom_operateur not in operateurs_dict:
        raise ValueError(f"L'opérateur '{nom_operateur}' n'existe pas.")

    # Supprimer l'opérateur
    del operateurs_dict[nom_operateur]

    # Sauvegarder les opérateurs modifiés
    with open(OPERATEURS_FILE, 'w') as f:
        json.dump(operateurs_dict, f, indent=4)

    afficher_message(f"Opérateur '{nom_operateur}' supprimé avec succès.")
