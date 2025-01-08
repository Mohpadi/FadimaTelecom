import json
import os
import logging
from datetime import datetime

TRANSACTIONS_FILE = "BD/transactions.txt"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transaction:
    def __init__(self, type_transaction, operateur, montant, description=""):
        if not isinstance(type_transaction, str) or not type_transaction:
            raise ValueError("type_transaction doit être une chaîne non vide.")
        if montant <= 0:
            raise ValueError("montant doit être un nombre positif.")

        self.type_transaction = type_transaction
        self.operateur = operateur
        self.montant = montant
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.description = description

    def sauvegarder(self):
        if not os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'w') as f:
                json.dump([], f)

        with open(TRANSACTIONS_FILE, 'r+') as f:
            try:
                transactions = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Fichier transactions corrompu ou vide. Réinitialisation...")
                transactions = []

            transactions.append(self.__dict__)
            f.seek(0)
            json.dump(transactions, f, indent=4)
            f.truncate()

        # logging.info(f"Transaction sauvegardée : {self.__dict__}")

    @staticmethod
    def charger_transactions():
        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    logging.warning("Erreur de lecture dans le fichier transactions. Réinitialisation...")
                    return []
        return []

    @staticmethod
    def filtrer_par_date(debut=None, fin=None):
        """
        Filtre les transactions par une plage de dates.
        :param debut: Date de début (format: 'YYYY-MM-DD').
        :param fin: Date de fin (format: 'YYYY-MM-DD').
        :return: Liste des transactions filtrées.
        """
        transactions = Transaction.charger_transactions()
        resultats = []

        for t in transactions:
            date_transaction = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
            if (not debut or datetime.strptime(debut, '%Y-%m-%d') <= date_transaction) and \
               (not fin or date_transaction <= datetime.strptime(fin, '%Y-%m-%d')):
                resultats.append(t)

        logging.info(f"{len(resultats)} transactions trouvees entre {debut} et {fin}.")
        return resultats

    @staticmethod
    def filtrer_par_operateur(operateur):
        """
        Filtre les transactions par opérateur.
        :param operateur: Nom de l'opérateur.
        :return: Liste des transactions associées à cet opérateur.
        """
        transactions = Transaction.charger_transactions()
        resultats = [t for t in transactions if t['operateur'] == operateur]

        logging.info(f"{len(resultats)} transactions trouvees pour l'opérateur {operateur}.")
        return resultats
