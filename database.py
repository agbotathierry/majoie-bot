# =============================================================
#  database.py — Gestion Supabase
# =============================================================

from supabase import create_client
from datetime import datetime, timedelta
from config import SUPABASE_URL, SUPABASE_KEY, DUREE_SESSION_HEURES

from supabase import create_client, ClientOptions
supabase = create_client(
    SUPABASE_URL, 
    SUPABASE_KEY,
    options=ClientOptions(postgrest_client_timeout=10)
)

# --- CLIENTS ---

def get_ou_creer_client(numero: str, nom: str = None) -> dict:
    try:
        res = supabase.table("clients").select("*").eq("numero", numero).execute()
        if res.data:
            client = res.data[0]
            if nom and not client.get("nom"):
                supabase.table("clients").update({"nom": nom}).eq("numero", numero).execute()
            return client
        else:
            nouveau = {
                "numero": numero,
                "nom": nom or "Client",
                "cree_le": datetime.utcnow().isoformat()
            }
            res = supabase.table("clients").insert(nouveau).execute()
            return res.data[0]
    except Exception as e:
        print(f"Erreur client : {e}")
        return {"numero": numero, "nom": nom or "Client"}


# --- HISTORIQUE DE CONVERSATION ---

def get_historique_conversation(numero: str) -> list:
    try:
        limite = (datetime.utcnow() - timedelta(hours=DUREE_SESSION_HEURES)).isoformat()
        res = (
            supabase.table("messages")
            .select("role, contenu")
            .eq("numero_client", numero)
            .gte("date", limite)
            .order("date", desc=False)
            .execute()
        )
        return res.data if res.data else []
    except Exception as e:
        print(f"Erreur historique : {e}")
        return []


def sauvegarder_message(numero: str, role: str, contenu: str):
    try:
        supabase.table("messages").insert({
            "numero_client": numero,
            "role": role,
            "contenu": contenu,
            "date": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Erreur sauvegarde message : {e}")


# --- COMMANDES ---

def creer_commande(numero: str, details: str) -> dict:
    try:
        res = supabase.table("commandes").insert({
            "numero_client": numero,
            "details": details,
            "statut": "nouvelle",
            "date": datetime.utcnow().isoformat()
        }).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        print(f"Erreur commande : {e}")
        return {}


def get_commandes_client(numero: str) -> list:
    try:
        res = (
            supabase.table("commandes")
            .select("*")
            .eq("numero_client", numero)
            .order("date", desc=True)
            .execute()
        )
        return res.data if res.data else []
    except Exception as e:
        print(f"Erreur get commandes : {e}")
        return []


# --- PRODUITS ---

def get_tous_produits() -> list:
    try:
        res = supabase.table("produits").select("*").eq("disponible", True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erreur produits : {e}")
        return []


def formater_catalogue() -> str:
    """Retourne le catalogue formaté en texte pour l'IA — avec les IDs pour les photos."""
    produits = get_tous_produits()
    if not produits:
        return "Aucun produit disponible pour le moment."

    lignes = []
    for p in produits:
        # ✅ On inclut l'ID pour que le bot puisse le retourner dans [PHOTOS]
        ligne = f"- [ID:{p['id']}] {p['nom']} : {p['prix']} FCFA"
        if p.get("description"):
            ligne += f" ({p['description']})"
        if p.get("lien_photo") and "VOTRE_LIEN" not in p["lien_photo"]:
            ligne += f" | photo disponible"  # On dit juste qu'il y a une photo, sans donner l'URL
        lignes.append(ligne)

    return "\n".join(lignes)