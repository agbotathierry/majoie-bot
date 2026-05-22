from database import get_ou_creer_client
from services.delivery import detecter_zone_par_choix, menu_zones
from services.cart import (
    get_panier,
    ajouter_au_panier,
    mettre_a_jour_quartier,
    vider_panier
)
from services.orders import creer_commande_structuree
from bot.states import get_etat, set_etat
from database import supabase

PRODUITS_PAR_PAGE = 5


def get_categories():
    res = supabase.table("CATEGORIE").select("*").order("id").execute()
    return res.data or []


def get_produits_categorie(categorie_id):
    res = supabase.table("produits").select("*").eq("categorie_id", categorie_id).eq("disponible", True).execute()
    return res.data or []


def menu_principal():
    return (
        "Bonjour ! 👋 Bienvenue chez Majoie Mercerie.\n\n"
        "Que voulez-vous faire ?\n\n"
        "1. Voir le catalogue\n"
        "2. Frais de livraison\n"
        "3. Mon panier\n\n"
        "Tapez le numéro de votre choix."
    )


def menu_categories():
    categories = get_categories()
    texte = "Choisissez une catégorie :\n\n"
    for i, cat in enumerate(categories, 1):
        texte += f"{i}. {cat['nom']}\n"
    texte += "\n0. Retour"
    return texte, categories


def construire_page_produits(produits, page, categorie_id):
    """Construit le texte et la liste de produits pour une page donnée."""
    debut = page * PRODUITS_PAR_PAGE
    fin = debut + PRODUITS_PAR_PAGE
    total_pages = (len(produits) + PRODUITS_PAR_PAGE - 1) // PRODUITS_PAR_PAGE
    produits_page = produits[debut:fin]

    texte = (
        f"Page {page + 1}/{total_pages} "
        f"({debut + 1}-{min(fin, len(produits))} sur {len(produits)} produits)\n\n"
        f"Tapez *A + numéro* pour ajouter au panier\n"
        f"Exemple : A{debut + 1}, A{debut + 2}...\n\n"
    )
    for i, p in enumerate(produits_page, debut + 1):
        texte += f"{i}. {p['nom']} — {p['prix']} FCFA\n"

    if page + 1 < total_pages:
        texte += "\nTapez *SUITE* pour voir plus de produits\n"
    texte += "\n0. Retour"

    return texte, produits_page


def confirmer_commande(numero_client, panier, zone_nom, frais):
    commande = creer_commande_structuree(
        numero_client,
        panier["produits"],
        zone_nom,
        frais
    )
    vider_panier(numero_client)
    set_etat(numero_client, "MENU")
    total_produits = commande["total"] - commande["frais_livraison"]
    texte = (
        f"✅ Commande confirmée !\n\n"
        f"Total produits : {total_produits} FCFA\n"
        f"Frais livraison : {frais} FCFA\n"
        f"*TOTAL : {commande['total']} FCFA*\n\n"
        f"Numéro de commande : #{commande['commande_id']}\n"
        "Merci pour votre commande ! 🎉\n\n"
        + menu_principal()
    )
    return texte, commande


def traiter_message(numero_client, message_client):
    get_ou_creer_client(numero_client)

    etat = get_etat(numero_client)
    message = message_client.strip()

    print(f"📍 État : {etat} | Message : {message}")

    # ═══════════════════════════════
    # ÉTAT : MENU PRINCIPAL
    # ═══════════════════════════════
    if etat == "MENU":
        if message == "1":
            texte, _ = menu_categories()
            set_etat(numero_client, "CATALOGUE")
            return {"texte": texte, "produits": [], "commande": None}

        elif message == "2":
            set_etat(numero_client, "LIVRAISON")
            return {"texte": menu_zones(), "produits": [], "commande": None}

        elif message == "3":
            panier = get_panier(numero_client)
            if not panier or not panier.get("produits"):
                return {"texte": "Votre panier est vide.\n\n" + menu_principal(), "produits": [], "commande": None}
            texte = "🛒 Votre panier :\n\n"
            for i, p in enumerate(panier["produits"], 1):
                texte += f"{i}. {p['quantite']}x {p['nom']} — {p['prix']} FCFA\n"
            texte += "\n1. Confirmer la commande\n2. Continuer les achats\n3. Vider le panier\n\n0. Retour"
            set_etat(numero_client, "PANIER")
            return {"texte": texte, "produits": [], "commande": None}

        else:
            return {"texte": menu_principal(), "produits": [], "commande": None}

    # ═══════════════════════════════
    # ÉTAT : CATALOGUE
    # ═══════════════════════════════
    elif etat == "CATALOGUE":
        categories = get_categories()

        if message == "0":
            set_etat(numero_client, "MENU")
            return {"texte": menu_principal(), "produits": [], "commande": None}

        if message.isdigit():
            index = int(message) - 1
            if 0 <= index < len(categories):
                cat = categories[index]
                produits = get_produits_categorie(cat["id"])

                if not produits:
                    return {"texte": "Aucun produit disponible.\n\n0. Retour", "produits": [], "commande": None}

                texte, produits_page = construire_page_produits(produits, 0, cat["id"])
                set_etat(numero_client, f"PRODUITS_{cat['id']}_PAGE_0")
                return {"texte": texte, "produits": produits_page, "commande": None}

        texte, _ = menu_categories()
        return {"texte": texte, "produits": [], "commande": None}

    # ═══════════════════════════════
    # ÉTAT : PRODUITS D'UNE CATÉGORIE
    # ═══════════════════════════════
    elif etat.startswith("PRODUITS_"):
        parties = etat.split("_")
        categorie_id = int(parties[1])
        page = int(parties[3]) if len(parties) > 3 else 0
        produits = get_produits_categorie(categorie_id)
        total_pages = (len(produits) + PRODUITS_PAR_PAGE - 1) // PRODUITS_PAR_PAGE

        if message == "0":
            texte, _ = menu_categories()
            set_etat(numero_client, "CATALOGUE")
            return {"texte": texte, "produits": [], "commande": None}

        # Navigation page suivante
        if message.upper() == "SUITE":
            nouvelle_page = page + 1
            if nouvelle_page < total_pages:
                texte, produits_page = construire_page_produits(produits, nouvelle_page, categorie_id)
                set_etat(numero_client, f"PRODUITS_{categorie_id}_PAGE_{nouvelle_page}")
                return {"texte": texte, "produits": produits_page, "commande": None}
            else:
                texte, produits_page = construire_page_produits(produits, page, categorie_id)
                return {"texte": "Vous êtes déjà à la dernière page.\n\n" + texte, "produits": produits_page, "commande": None}

        # Ajouter au panier
        message_upper = message.upper()
        if message_upper.startswith("A") and message_upper[1:].isdigit():
            index = int(message_upper[1:]) - 1
            if 0 <= index < len(produits):
                produit = produits[index]
                ajouter_au_panier(numero_client, produit)
                texte = (
                    f"✅ *{produit['nom']}* ajouté au panier.\n"
                    f"Prix : {produit['prix']} FCFA\n\n"
                    "1. Voir d'autres produits\n"
                    "2. Confirmer ma commande\n\n"
                    "0. Retour"
                )
                set_etat(numero_client, "CONTINUER")
                return {"texte": texte, "produits": [], "commande": None}

        # Affichage par défaut de la page actuelle
        texte, produits_page = construire_page_produits(produits, page, categorie_id)
        return {"texte": texte, "produits": produits_page, "commande": None}

    # ═══════════════════════════════
    # ÉTAT : CONTINUER OU CONFIRMER
    # ═══════════════════════════════
    elif etat == "CONTINUER":
        if message == "0" or message == "1":
            texte, _ = menu_categories()
            set_etat(numero_client, "CATALOGUE")
            return {"texte": texte, "produits": [], "commande": None}

        elif message == "2":
            panier = get_panier(numero_client)
            if panier and panier.get("quartier"):
                zone = detecter_zone_par_choix(panier.get("zone_choix", ""))
                frais = zone["frais"] if zone else 0
                texte, commande = confirmer_commande(numero_client, panier, panier["quartier"], frais)
                return {"texte": texte, "produits": [], "commande": commande}
            else:
                set_etat(numero_client, "QUARTIER_COMMANDE")
                return {"texte": menu_zones(), "produits": [], "commande": None}

        return {"texte": "Tapez 1 pour continuer ou 2 pour confirmer.\n\n0. Retour", "produits": [], "commande": None}

    # ═══════════════════════════════
    # ÉTAT : QUARTIER POUR COMMANDE
    # ═══════════════════════════════
    elif etat == "QUARTIER_COMMANDE":
        if message == "0":
            set_etat(numero_client, "MENU")
            return {"texte": menu_principal(), "produits": [], "commande": None}

        zone = detecter_zone_par_choix(message)
        if not zone:
            return {"texte": "Tapez 1, 2, 3 ou 4.\n\n" + menu_zones(), "produits": [], "commande": None}

        mettre_a_jour_quartier(numero_client, zone["nom"])
        panier = get_panier(numero_client)
        frais = zone["frais"]
        texte, commande = confirmer_commande(numero_client, panier, zone["nom"], frais)
        return {"texte": texte, "produits": [], "commande": commande}

    # ═══════════════════════════════
    # ÉTAT : LIVRAISON
    # ═══════════════════════════════
    elif etat == "LIVRAISON":
        if message == "0":
            set_etat(numero_client, "MENU")
            return {"texte": menu_principal(), "produits": [], "commande": None}

        zone = detecter_zone_par_choix(message)
        if not zone:
            return {"texte": "Tapez 1, 2, 3 ou 4.\n\n" + menu_zones(), "produits": [], "commande": None}

        set_etat(numero_client, "MENU")
        return {
            "texte": f"Frais de livraison *{zone['nom']}* : {zone['frais']} FCFA\n\n" + menu_principal(),
            "produits": [],
            "commande": None
        }

    # ═══════════════════════════════
    # ÉTAT : PANIER
    # ═══════════════════════════════
    elif etat == "PANIER":
        if message == "0":
            set_etat(numero_client, "MENU")
            return {"texte": menu_principal(), "produits": [], "commande": None}

        if message == "1":
            panier = get_panier(numero_client)
            if panier and panier.get("quartier"):
                zone = detecter_zone_par_choix(panier.get("zone_choix", ""))
                frais = zone["frais"] if zone else 0
                texte, commande = confirmer_commande(numero_client, panier, panier["quartier"], frais)
                return {"texte": texte, "produits": [], "commande": commande}
            else:
                set_etat(numero_client, "QUARTIER_COMMANDE")
                return {"texte": menu_zones(), "produits": [], "commande": None}

        elif message == "2":
            texte, _ = menu_categories()
            set_etat(numero_client, "CATALOGUE")
            return {"texte": texte, "produits": [], "commande": None}

        elif message == "3":
            vider_panier(numero_client)
            set_etat(numero_client, "MENU")
            return {"texte": "Panier vidé. 🗑️\n\n" + menu_principal(), "produits": [], "commande": None}

        return {"texte": "Tapez 1, 2 ou 3.\n\n0. Retour", "produits": [], "commande": None}

    # ═══════════════════════════════
    # DÉFAUT
    # ═══════════════════════════════
    else:
        set_etat(numero_client, "MENU")
        return {"texte": menu_principal(), "produits": [], "commande": None}