from services.whatsapp import envoyer_image


async def envoyer_photos_produits(
    numero,
    produits
):

    deja_envoyes = set()

    for produit in produits:

        if produit["id"] in deja_envoyes:
            continue

        deja_envoyes.add(produit["id"])

        if not produit.get("lien_photo"):
            continue

        caption = (
            f"*{produit['nom']}*\n"
            f"💰 {produit['prix']} FCFA\n"
            f"{produit.get('description', '')}"
        )

        await envoyer_image(
            numero,
            produit["lien_photo"],
            caption
        )