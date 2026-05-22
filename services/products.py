from rapidfuzz import fuzz
from database import get_tous_produits


def normaliser(texte: str):
    return texte.lower().strip()


def rechercher_produits(message: str, limite: int = 5):

    produits = get_tous_produits()

    message = normaliser(message)

    resultats = []

    for produit in produits:

        texte = (
            f"{produit.get('nom', '')} "
            f"{produit.get('description', '')}"
        )

        texte = normaliser(texte)

        score = fuzz.partial_ratio(message, texte)

        if score >= 55:
            resultats.append((score, produit))

    resultats.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [p for _, p in resultats[:limite]]