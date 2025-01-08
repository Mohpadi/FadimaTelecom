from datetime import datetime
import json
import logging
import os
import sys
import threading
import time
from winsound import PlaySound
import numpy as np
from playsound import playsound
import pygame
from Models.transactions import Transaction
import sounddevice as sd
from scipy.io.wavfile import write
from Views.functions import afficher_message, afficher_erreur, afficher_tableau, afficher_titre
from constants import NUMERO_LENGTH, TARIF_DIFF_OPERATEUR, TARIF_MEME_OPERATEUR
# Fichier centralisé pour tous les appels
APPELS_FILE = "BD/appels.txt"
OPERATEURS_FILE = "BD/operateurs.txt"
SONNERIE_FILE = "sonnerie/son1.mp3"  # Chemin vers le fichier de sonnerie
VOCAL_FOLDER = 'vocales'  # Définir un dossier pour les fichiers vocaux
logging.basicConfig(filename='logs/telecom.log', level=logging.INFO, format='%(asctime)s - %(message)s')
class Client:
    clients_file = 'BD/clients.txt' 
    file_lock = threading.Lock() 
    def __init__(self, numero, pin=0000, credit=0, repertoire=None, nom=None):
        self.numero = numero
        self.pin = str(pin).zfill(4)  # S'assurer que le PIN a 4 chiffres
        self.credit = credit
        self.repertoire = repertoire if repertoire else {}
        self.nom = nom
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
    def creer_client(numero, nom=None, pin="0000", credit=0):
        """
        Crée un client avec les informations fournies après validation.
        :param numero: Numéro de téléphone du client.
        :param nom: Nom du client (facultatif).
        :param pin: Code PIN du client (par défaut "0000").
        :param credit: Crédit initial du client (par défaut 0).
        """
        # Validation du numéro
        try:
            Client.valider_numero(numero)
        except ValueError as e:
            raise ValueError(f"Erreur de validation du numéro : {e}")

        # Vérification de l'existence du numéro chez les opérateurs
        if not Client.numero_existe_dans_operateurs(numero):
            raise ValueError(f"Le numéro {numero} n'existe chez aucun opérateur du système.")

        # Création de l'instance de Client
        client = Client(numero=numero, pin=pin, credit=credit, nom=nom)

        # Sauvegarde des données du client
        try:
            client.sauvegarder()
            afficher_message(f"Client '{nom if nom else 'Anonyme'}' avec le numéro {numero} créé avec succès.")
        except Exception as e:
            raise IOError(f"Erreur lors de la sauvegarde des données du client : {e}")


    def mettre_a_jour_nom(self, nouveau_nom):
        """
        Met à jour le nom du client dans le fichier des clients.
        :param numero: Numéro de téléphone du client.
        :param nouveau_nom: Nouveau nom à attribuer au client.
        """
        # Charger les données existantes
        if not os.path.exists(Client.clients_file):
            raise FileNotFoundError("Le fichier des clients n'existe pas.")

        with open(Client.clients_file, "r") as f:
            try:
                clients = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("Le fichier des clients est corrompu.")

        # Vérifier si le client existe
        if self.numero not in clients:
            raise ValueError(f"Le client avec le numéro {self.numero} n'existe pas.")

        # Mettre à jour le nom
        clients[self.numero]["nom"] = nouveau_nom

        # Sauvegarder les modifications
        with open(Client.clients_file, "w") as f:
            json.dump(clients, f, indent=4)

        afficher_message(f"Nom du client avec le numéro {self.numero} mis à jour en '{nouveau_nom}'.")
    def changer_pin(self, ancien_pin):
        """
        Vérifie l'ancien PIN et, s'il est correct, demande un nouveau PIN pour le modifier.
        :param client: Instance du client actuel.
        :param ancien_pin: PIN actuel pour vérification.
        """
        # Charger les données existantes
        if not os.path.exists(Client.clients_file):
            raise FileNotFoundError("Le fichier des clients n'existe pas.")

        with open(Client.clients_file, "r") as f:
            try:
                clients = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("Le fichier des clients est corrompu.")

        # Vérifier si le client existe dans le fichier
        if self.numero not in clients:
            raise ValueError(f"Le client avec le numéro {self.numero} n'existe pas.")

        # Vérification de l'ancien PIN
        client_data = clients[self.numero]
        if client_data["pin"] != str(ancien_pin).zfill(4):  # Vérifier la correspondance avec l'ancien PIN
            raise ValueError("L'ancien PIN est incorrect.")

        # Demander le nouveau PIN
        nouveau_pin = input("Entrez un nouveau PIN (4 chiffres) : ").strip()

        # Validation du nouveau PIN
        if not nouveau_pin.isdigit() or len(nouveau_pin) != 4:
            raise ValueError("Le nouveau PIN doit être un entier de 4 chiffres.")

        # Mise à jour du PIN
        clients[self.numero]["pin"] = str(nouveau_pin).zfill(4)

        # Sauvegarde des modifications
        with open(Client.clients_file, "w") as f:
            json.dump(clients, f, indent=4)

        afficher_message("Votre PIN a été modifié avec succès.")

    @staticmethod
    def connexion_client(numero, pin):
        client = Client.lire_par_numero(numero)
        if client:
            if client.pin == pin:
                return client
            else:
                afficher_erreur("Erreur : PIN incorrect.")
                raise ValueError("Numéro ou PIN incorrect.")
        else:
            afficher_erreur("Erreur : Numéro inconnu.")
            raise ValueError("Numéro ou PIN incorrect.")

    def sauvegarder(self): 
        """Sauvegarde les données du client dans un fichier texte centralisé.""" 
        if not os.path.exists('BD'): 
            os.makedirs('BD') 
        try:
            with Client.file_lock: 
                # Charger les clients existants 
                clients = {} 
                if os.path.exists(Client.clients_file): 
                    with open(Client.clients_file, 'r') as f: 
                        try: 
                            clients = json.load(f) 
                        except json.JSONDecodeError: 
                            clients = {} 
                else: 
                    # Créer le fichier s'il n'existe pas 
                    with open(Client.clients_file, 'w') as f: 
                        json.dump({}, f)
                # Mettre à jour ou ajouter le nouveau client 
                clients[self.numero] = { 
                    'nom': self.nom, 
                    'pin': self.pin, 
                    'credit': self.credit, 
                    'repertoire': self.repertoire 
                } 
                # Sauvegarder les clients mis à jour 
                with open(Client.clients_file, 'w') as f: 
                    json.dump(clients, f, indent=4)
        except Exception as e:
            afficher_erreur(f"Erreur lors de la sauvegarde du client {self.numero} : {e}")
            raise
    @staticmethod
    def lancer_appel(emetteur, recepteur):
        """
        Simule un appel interactif avec sonnerie, chronomètre et capture audio réelle.
        """
        # Charger les clients
        client_emetteur = Client.lire_par_numero(emetteur)
        client_recepteur = Client.lire_par_numero(recepteur)

        if not client_emetteur or not client_recepteur:
            afficher_erreur("Ce numéro n'est attribué à aucun client.")
            return

        # Vérifier si le numéro émetteur ou récepteur est bloqué
        if any(
            [
                any(numero == emetteur and contact.get("bloque", False) for contact in client_recepteur.repertoire.values() for numero in contact["numeros"]),
                any(numero == recepteur and contact.get("bloque", False) for contact in client_emetteur.repertoire.values() for numero in contact["numeros"]),
            ]
        ):
            afficher_erreur("Appel impossible numéro est bloqué.")
            return
        # Rechercher les noms des contacts
        nom_emetteur_pour_recepteur = next(
            (nom for nom, details in client_recepteur.repertoire.items() if emetteur in details.get("numeros", [])),
            emetteur
        )
        nom_recepteur_pour_emetteur = next(
            (nom for nom, details in client_emetteur.repertoire.items() if recepteur in details.get("numeros", [])),
            recepteur
        )

        # Déterminer si les opérateurs sont les mêmes
        def meme_operateur(client1, client2):
            return client1.repertoire.keys() & client2.repertoire.keys()

        tarif_par_seconde = (
            TARIF_MEME_OPERATEUR if meme_operateur(client_emetteur, client_recepteur) else TARIF_DIFF_OPERATEUR
        )

        # Vérifier le crédit suffisant pour démarrer l'appel
        if client_emetteur.credit < tarif_par_seconde:
            afficher_erreur("Crédit insuffisant pour démarrer l'appel.")
            return

        # Verrou pour synchroniser l'affichage
        print_lock = threading.Lock()

        def jouer_sonnerie():
            """Joue la sonnerie en boucle jusqu'à ce que l'utilisateur réponde ou refuse."""
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(SONNERIE_FILE)
                pygame.mixer.music.play(-1)  # Lecture en boucle
                with print_lock:
                    print("Ça sonne...")
                while True:
                    reponse = input("Tapez R+Entrée pour répondre ou Q+Entrée pour refuser : ").strip().upper()
                    if reponse == "R":
                        pygame.mixer.music.stop()
                        with print_lock:
                            afficher_message("Appel accepté.")
                        return True
                    elif reponse == "Q":
                        pygame.mixer.music.stop()
                        with print_lock:
                            afficher_message("Appel refusé.")
                        return False
            except Exception as e:
                with print_lock:
                    afficher_erreur(f"Erreur lors de la lecture de la sonnerie : {e}")
            finally:
                pygame.mixer.quit()

        # Jouer la sonnerie et vérifier si l'appel est accepté
        if not jouer_sonnerie():
            return  # Arrêter le processus si l'appel est refusé

        # Début de l'enregistrement
        with print_lock:
            afficher_message(f"Appel avec {nom_recepteur_pour_emetteur} en cours. Parlez dans le micro.")
            print("Appuyez sur Entrée pour raccrocher.")

        sample_rate = 44100  # Fréquence d'échantillonnage
        audio_data = []  # Données audio

        # Variables pour gérer l'arrêt
        stop_recording = False
        last_chunk_time = time.time()

        def capturer_audio():
            """Enregistre l'audio en temps réel tant que l'utilisateur n'arrête pas."""
            nonlocal audio_data, stop_recording, last_chunk_time
            with print_lock:
                print("\nParlez maintenant :")
            while not stop_recording:
                try:
                    current_time = time.time()
                    chunk_duration = current_time - last_chunk_time
                    if chunk_duration > 0:
                        chunk = sd.rec(
                            int(sample_rate * chunk_duration),
                            samplerate=sample_rate,
                            channels=1,
                            dtype="int16",
                        )
                        sd.wait()
                        audio_data.extend(chunk)
                        last_chunk_time = current_time
                except Exception as e:
                    with print_lock:
                        afficher_erreur(f"Erreur lors de l'enregistrement audio : {e}")
                    break

        def afficher_chronometre():
            """Affiche un chronomètre en temps réel."""
            start_time = time.time()
            while not stop_recording:
                duree = int(time.time() - start_time)
                with print_lock:
                    sys.stdout.write(f"\rDurée de l'appel : {duree}s")
                    sys.stdout.flush()
                time.sleep(1)

        # Lancer les threads pour l'enregistrement et le chronomètre
        audio_thread = threading.Thread(target=capturer_audio)
        chrono_thread = threading.Thread(target=afficher_chronometre)

        audio_thread.start()
        chrono_thread.start()

        # Attendre que l'utilisateur arrête l'enregistrement
        input("")
        stop_recording = True

        # Attendre la fin des threads
        audio_thread.join()
        chrono_thread.join()

        # Calculer la durée totale
        duree_totale = len(audio_data) / sample_rate
        cout_total = duree_totale * tarif_par_seconde

        # Vérifier le crédit suffisant pour la durée totale
        if client_emetteur.credit < cout_total:
            afficher_erreur("Crédit insuffisant pour couvrir la durée totale de l'appel.")
            return

        # Déduire le coût de l'appel
        client_emetteur.credit -= cout_total
        client_emetteur.sauvegarder()

        # Enregistrer l'audio dans un fichier
        vocal_file = None
        if audio_data:
            if not os.path.exists(VOCAL_FOLDER):
                os.makedirs(VOCAL_FOLDER)
            vocal_file = os.path.join(VOCAL_FOLDER, f"vocal_{emetteur}_{recepteur}.wav")
            audio_array = np.array(audio_data, dtype="int16")
            write(vocal_file, sample_rate, audio_array)

        # Enregistrer l'appel
        Client.enregistrer_appel(emetteur, recepteur, int(duree_totale), vocal_file)

        with print_lock:
            afficher_message(
                f"\nAppel terminé. Durée totale : {int(duree_totale)} secondes. Coût total : {cout_total:.2f} FCFA."
            )
        return True


    @staticmethod
    def lire_par_numero(numero):
        """
        Charge un client depuis le fichier centralisé par numéro de téléphone.
        """
        Client.valider_numero(numero)
        if not os.path.exists(Client.clients_file):
            return None
        with open(Client.clients_file, 'r') as f:
            try:
                clients = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Le fichier des clients est corrompu : {e}")
        if numero in clients:
            data = clients[numero]
            return Client(numero, data['pin'], data['credit'], data['repertoire'],data['nom'])
        return None

    def verifier_solde(self):
        """
        Affiche le solde de crédit du client après confirmation du PIN.
        """
        self.recharger_client()
        try:
            pin = input("Entrez votre PIN pour vérifier le solde : ").strip()
            if pin != self.pin:
                raise ValueError("PIN incorrect.")
            afficher_message(f"Votre solde est de {self.credit} FCFA.")
        except Exception as e:
            afficher_erreur(f"Erreur : {e}")

    def recharger_client(self):
        """
        Recharge les données du client depuis le fichier de sauvegarde.
        """
        try:
            with Client.file_lock:
                # Charger tous les clients
                with open(Client.clients_file, 'r') as f:
                    clients = json.load(f)

                # Recharger les données du client actuel
                if self.numero in clients:
                    client_data = clients[self.numero]
                    self.nom = client_data['nom']
                    self.pin = client_data['pin']
                    self.credit = client_data['credit']
                    self.repertoire = client_data['repertoire']
                else:
                    raise ValueError(f"Le client avec le numéro {self.numero} n'existe pas dans la sauvegarde.")
        except Exception as e:
            afficher_erreur(f"Erreur lors du rechargement des données du client {self.numero} : {e}")
            raise


    def ajouter_credit(self, montant):
        """Ajoute du crédit au client."""
        self.credit += montant
        afficher_message(f"Ajout de crédit pour {montant} avec succès")
        self.sauvegarder()
        Transaction("achat_credit", None, montant, f"Ajout de crédit pour {self.numero}").sauvegarder()

    @staticmethod
    def transferer_credit(source_numero, cible_numero, montant):
        """Transfère du crédit entre deux clients et enregistre la transaction."""
        if not isinstance(montant, (int, float)) or montant < 100:
            raise ValueError("Le montant doit être un nombre supérieur ou égal à 100.")
        source = Client.lire_par_numero(source_numero)
        cible = Client.lire_par_numero(cible_numero)

        if not source or not cible:
            raise ValueError("Un ou les deux clients n'existent pas.")
        
        frais = montant * 0.10
        montant_final = montant + frais

        if source.credit < montant_final:
            raise ValueError("Crédit insuffisant pour le transfert.")

        source.credit -= montant_final
        cible.credit += montant

        source.sauvegarder()
        cible.sauvegarder()

        # Enregistrer les transactions
        Transaction("transfert_credit", None, montant + frais, f"Transfert de {montant} de {source_numero} à {cible_numero}").sauvegarder()

        afficher_message(f"Transfert réussi : {montant} FCFA de {source_numero} à {cible_numero}. Frais : {frais} FCFA.")

    @staticmethod
    def enregistrer_appel(emetteur, recepteur, duree, vocal_file=None):
        """
        Enregistre un appel dans l’historique avec un fichier audio réel.
        """
        appels = Client.charger_historique()

        nouvel_appel = {
            "id": len(appels) + 1,
            "emetteur": emetteur,
            "recepteur": recepteur,
            "duree": duree,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vocal": vocal_file,
            "vocal_lu": False,
        }
        appels.append(nouvel_appel)
        Client.sauvegarder_historique(appels)

    @staticmethod
    def charger_historique():
        """
        Charge l'historique des appels depuis le fichier centralisé.
        Retourne une liste vide si le fichier est absent ou mal formatté.
        """
        if os.path.exists(APPELS_FILE):
            with open(APPELS_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    else:
                        afficher_erreur("Format incorrect dans appels.txt, réinitialisation...")
                        return []
                except json.JSONDecodeError:
                    afficher_erreur("Erreur de lecture du fichier appels.txt, réinitialisation...")
                    return []
        return []


    @staticmethod
    def sauvegarder_historique(appels):
        """
        Sauvegarde l'historique des appels dans le fichier centralisé.
        """
        if not isinstance(appels, list):
            raise ValueError("L'historique des appels doit être une liste.")
        with open(APPELS_FILE, 'w') as f:
            json.dump(appels, f, indent=4)


    @staticmethod
    def voir_historique(numero):
        """Récupère l'historique des appels pour un client."""
        appels = Client.charger_historique()
        return [appel for appel in appels if appel['emetteur'] == numero or appel['recepteur'] == numero]

    def bloquer_contact(self, nom):
        if nom in self.repertoire:
            self.repertoire[nom]['bloque'] = True
            self.sauvegarder()
            self.afficher_repertoire()

    def debloquer_contact(self, nom):
        if nom in self.repertoire and 'bloque' in self.repertoire[nom]:
            del self.repertoire[nom]['bloque']
            self.sauvegarder()
            self.afficher_repertoire()
    @staticmethod
    def ecouter_vocal(self):
        """
        Permet d'afficher tous les vocaux associés à un numéro de téléphone, 
        de sélectionner un vocal à écouter, et de le lire.
        """
        appels = Client.charger_historique()
        vocaux = [
            appel for appel in appels 
            if (appel['emetteur'] == self.numero or appel['recepteur'] == self.numero) and appel.get('vocal')
        ]

        if not vocaux:
            raise ValueError("Aucun vocal trouvé pour ce numéro.")

        # Afficher le tableau des vocaux
        vocaux.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"), reverse=True)
        data = [
            (index + 1, appel['date'], "Non lu" if not appel.get('vocal_lu') else "Lu")
            for index, appel in enumerate(vocaux)
        ]
        afficher_titre("Vocaux disponibles")
        afficher_tableau(data, headers=["#", "Date", "État"])

        # Demander à l'utilisateur de choisir un vocal
        try:
            choix = int(input("Entrez la position du vocal à écouter : ").strip())
            if choix < 1 or choix > len(vocaux):
                raise ValueError("Position invalide.")

            # Récupérer le vocal choisi
            dernier_vocal = vocaux[choix - 1]
            vocal_file = dernier_vocal.get('vocal')
            if vocal_file and os.path.exists(vocal_file):
                afficher_message(f"Lecture du vocal sélectionné ({dernier_vocal['date']}):")
                try:
                    pygame.mixer.init()
                    pygame.mixer.music.load(vocal_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(1)  # Attendre que la lecture se termine
                    pygame.mixer.quit()

                    # Marquer le vocal comme lu
                    dernier_vocal['vocal_lu'] = True
                    Client.sauvegarder_historique(appels)
                except Exception as e:
                    afficher_erreur(f"Erreur lors de la lecture du fichier vocal : {e}")
            else:
                raise FileNotFoundError(f"Aucun fichier vocal valide trouvé pour l'appel ID {dernier_vocal['id']}.")

        except ValueError as e:
            afficher_erreur(f"Erreur : {e}")
        except Exception as e:
            afficher_erreur(f"Une erreur inattendue s'est produite : {e}")

        return True  # Indiquer que le processus s'est terminé avec succès

    @staticmethod
    def supprimer_vocal(id_vocal):
        appels = Client.charger_historique()
        appels = [appel for appel in appels if appel['id'] != id_vocal]
        Client.sauvegarder_historique(appels)

    @staticmethod
    def numero_existe_dans_operateurs(numero):
        """
        Vérifie si un numéro existe chez au moins un opérateur dans le système.
        :param numero: Le numéro à vérifier.
        :return: True si le numéro existe, False sinon.
        """
        if not os.path.exists(OPERATEURS_FILE):
            raise FileNotFoundError("Le fichier des opérateurs est introuvable.")

        with open(OPERATEURS_FILE, "r") as f:
            try:
                operateurs = json.load(f)
                for operateur in operateurs.values():
                    for num_list in operateur.get("numeros", {}).values():
                        if numero in num_list:
                            return True
            except json.JSONDecodeError:
                raise ValueError("Le fichier des opérateurs est corrompu.")

        return False

    def ajouter_numero_contact(self, nom, nouveau_numero):
        if nom not in self.repertoire:
            raise ValueError("Le contact n'existe pas.")
        if len(self.repertoire[nom]['numeros']) >= 3:
            raise ValueError("Un contact ne peut avoir plus de 3 numéros.")
        Client.valider_numero(nouveau_numero)
        if not Client.numero_existe_dans_operateurs(nouveau_numero):
            raise ValueError(f"Le numéro {nouveau_numero} n'existe pas chez un opérateur.")
        self.repertoire[nom]['numeros'].append(nouveau_numero)
        self.sauvegarder()

    def ajouter_contact(self, nom, numeros):
        """
        Ajoute un contact au répertoire après validation.
        """
        if nom in self.repertoire:
            raise ValueError(f"Le contact '{nom}' existe déjà dans le répertoire.")

        if len(numeros) > 3:
            raise ValueError("Un contact ne peut pas avoir plus de 3 numéros.")

        # Vérifier les numéros
        numeros_verifies = set()
        for num in numeros:
            Client.valider_numero(num)
            
            if not Client.numero_existe_dans_operateurs(num):
                raise ValueError(f"Le numéro {num} n'existe chez aucun opérateur du système.")
            
            if any(num in details['numeros'] for details in self.repertoire.values()):
                raise ValueError(f"Le numéro {num} est déjà associé à un autre contact.")
            
            numeros_verifies.add(num)

        # Ajouter le contact au répertoire
        self.repertoire[nom] = {'numeros': list(numeros_verifies), 'bloque': False}

        # Sauvegarder les modifications
        self.sauvegarder()
        # Rafraîchir l'affichage du répertoire
        self.afficher_repertoire()



    def rechercher_contact(self, mot_cle):
        resultats = {nom: details for nom, details in self.repertoire.items() if mot_cle.lower() in nom.lower()}
        if not resultats:
            raise ValueError("Aucun contact trouvé pour ce mot-clé.")
        return resultats

    def supprimer_contact(self, nom):
        if nom in self.repertoire:
            del self.repertoire[nom]
            self.sauvegarder()
            self.afficher_repertoire()

    def renommer_contact(self, ancien_nom, nouveau_nom):
        if ancien_nom not in self.repertoire:
            raise ValueError("Le contact à renommer n'existe pas.")
        self.repertoire[nouveau_nom] = self.repertoire.pop(ancien_nom)
        self.sauvegarder()
        # Rafraîchir l'affichage du répertoire
        self.afficher_repertoire()
    def afficher_repertoire(self):
        """
        Affiche le répertoire téléphonique d’un client avec couleur et pagination.
        Les numéros bloqués sont affichés en rouge.
        """
        if not isinstance(self.repertoire, dict):
            afficher_erreur("Le répertoire fourni n'est pas valide.")
            return

        afficher_titre("Répertoire téléphonique")
        data = []
        for position, (nom, details) in enumerate(self.repertoire.items()):
            numeros = details.get("numeros", [])
            bloque = details.get("bloque", False)
            
            # Si le contact est bloqué, les numéros sont affichés en rouge
            numeros_affiches = ", ".join(f"[red]{numero}[/red]" for numero in numeros) if bloque else ", ".join(numeros)
            
            # Le nom reste inchangé
            nom_contact = f"[green]{nom}[/green]"
            
            data.append((position + 1, nom_contact, numeros_affiches))

        if not data:
            afficher_message("Aucun contact dans le répertoire.")
        else:
            afficher_tableau(data, headers=["#", "Nom du contact", "Numéros"])
