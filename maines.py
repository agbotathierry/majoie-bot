from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from bot.router import traiter_message
from services.whatsapp import envoyer_message, envoyer_image
from config import WHATSAPP_VERIFY_TOKEN, NUMERO_PROPRIO

app = FastAPI()

messages_traites = set()


@app.get("/webhook")
async def verifier_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(content="Token invalide", status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        message_id = message.get("id", "")

        if message_id in messages_traites:
            print(f"⚠️ Doublon ignoré : {message_id}")
            return {"status": "ok"}
        messages_traites.add(message_id)

        numero = message["from"]

        if message["type"] == "text":
            texte = message["text"]["body"]
        elif message["type"] == "interactive":
            texte = message["interactive"]["button_reply"]["id"]
        else:
            return {"status": "ok"}

        resultat = traiter_message(numero, texte)

        await envoyer_message(numero, resultat["texte"])

        # Alerte propriétaire si commande confirmée
        if resultat.get("commande"):
            c = resultat["commande"]
            total_produits = c["total"] - c["frais_livraison"]
            alerte = (
                f"🛍️ *Nouvelle commande #{c['commande_id']}*\n\n"
                f"Client : {c['numero_client']}\n"
                f"Produits : {c['details']}\n"
                f"Quartier : {c['quartier']}\n"
                f"Frais livraison : {c['frais_livraison']} FCFA\n"
                f"*TOTAL : {c['total']} FCFA*"
            )
            await envoyer_message(NUMERO_PROPRIO, alerte)
            for produit in c.get("produits", []):
                 if produit.get("lien_photo"):
                     await envoyer_image(NUMERO_PROPRIO, produit["lien_photo"], produit["nom"])

        for produit in resultat.get("produits", []):
            if produit.get("lien_photo"):
                await envoyer_image(
                    numero,
                    produit["lien_photo"],
                    f"{produit['nom']} — {produit['prix']} FCFA"
                )

    except Exception as e:
        print(f"Erreur webhook : {e}")

    return {"status": "ok"}