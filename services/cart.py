from datetime import datetime
from database import supabase
import json


def get_panier(numero_client):
    try:
        res = supabase.table("paniers").select("*").eq("numero_client", numero_client).execute()
        if res.data:
            panier = res.data[0]
            panier["produits"] = panier.get("produits") or []
            return panier
        return None
    except Exception as e:
        print(f"Erreur get panier : {e}")
        return None


def ajouter_au_panier(numero_client, produit, quantite=1):
    try:
        produit_item = {
        "id": produit["id"],
        "nom": produit["nom"],
        "prix": produit["prix"],
        "quantite": quantite,
        "lien_photo": produit.get("lien_photo", "")
        }

        panier = get_panier(numero_client)

        if panier:
            produits = panier["produits"]
            # Vérifier si produit déjà dans panier
            for p in produits:
                if p["id"] == produit["id"]:
                    p["quantite"] += quantite
                    supabase.table("paniers").update({"produits": produits}).eq("numero_client", numero_client).execute()
                    return produits

            produits.append(produit_item)
            supabase.table("paniers").update({"produits": produits}).eq("numero_client", numero_client).execute()
        else:
            produits = [produit_item]
            supabase.table("paniers").insert({
                "numero_client": numero_client,
                "produits": produits,
                "date": datetime.utcnow().isoformat()
            }).execute()

        return produits

    except Exception as e:
        print(f"Erreur ajout panier : {e}")
        return []


def mettre_a_jour_quartier(numero_client, quartier):
    try:
        supabase.table("paniers").update({"quartier": quartier}).eq("numero_client", numero_client).execute()
    except Exception as e:
        print(f"Erreur update quartier : {e}")


def vider_panier(numero_client):
    try:
        supabase.table("paniers").delete().eq("numero_client", numero_client).execute()
    except Exception as e:
        print(f"Erreur vider panier : {e}")