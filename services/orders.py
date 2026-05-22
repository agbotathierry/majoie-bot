from datetime import datetime
from database import supabase


def calculer_total(produits, frais_livraison=0):
    total = sum(p["prix"] * p.get("quantite", 1) for p in produits)
    return total + frais_livraison


def creer_commande_structuree(numero_client, produits, quartier, frais_livraison):
    total = calculer_total(produits, frais_livraison)

    commande = {
        "numero_client": numero_client,
        "details": ", ".join([f"{p.get('quantite', 1)}x {p['nom']}" for p in produits]),
        "statut": "nouvelle",
        "date": datetime.utcnow().isoformat()
    }

    res = supabase.table("commandes").insert(commande).execute()
    if not res.data:
        return None

    commande_id = res.data[0]["id"]

    items = []
    for p in produits:
        items.append({
            "command_id": commande_id,
            "nom_produits": p["nom"],
            "quantite": p.get("quantite", 1),
            "prix_unitaire": p["prix"]
        })

    supabase.table("commande_items").insert(items).execute()

    return {
        "commande_id": commande_id,
        "total": total,
        "frais_livraison": frais_livraison,
        "details": commande["details"],
        "numero_client": numero_client,
        "quartier": quartier,
        "produits": produits
    }