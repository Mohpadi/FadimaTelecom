# Constantes pour les opérateurs
MIN_NOM_OPERATEUR = 3
MAX_NOM_OPERATEUR = 15
MIN_INDEX = 1
MAX_INDEX = 3
INDEX_LENGTH = 2

# Tarifs d'appel (par exemple en FCFA par minute)
TARIF_MEME_OPERATEUR = 10
TARIF_DIFF_OPERATEUR = 20

# Règles pour les numéros de téléphone
NUMERO_LENGTH = 7  # Sans l'index
MIN_CREDIT_ACHAT = 100  # Montant minimum pour achat ou transfert
FRAIS_TRANSFERT = 0.10  # 10% des transferts
# Paramètres dynamiques (valeurs par défaut)
DEFAULT_PARAMETRES = {
    "tarif_meme_operateur": 10,  # Tarifs d'appel (par minute)
    "tarif_diff_operateur": 20,
}