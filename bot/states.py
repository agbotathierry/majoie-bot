from database import supabase


def get_etat(numero_client):
    try:
        res = supabase.table("clients").select("etats").eq("numero", numero_client).execute()
        if res.data:
            return res.data[0].get("etats") or "MENU"
        return "MENU"
    except Exception as e:
        print(f"Erreur get_etat : {e}")
        return "MENU"


def set_etat(numero_client, etat):
    try:
        supabase.table("clients").update({"etats": etat}).eq("numero", numero_client).execute()
    except Exception as e:
        print(f"Erreur set_etat : {e}")