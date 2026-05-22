import httpx
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

WHATSAPP_API_URL = (
    f"https://graph.facebook.com/v19.0/"
    f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
)

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}


async def envoyer_message(numero, texte):
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texte}
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
        print(f"📤 Texte : {r.status_code}")


async def envoyer_boutons(numero, texte, boutons):
    """
    boutons = [{"id": "CATALOGUE", "titre": "Voir catalogue"}]
    Max 3 boutons
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texte},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": b["id"],
                            "title": b["titre"][:20]
                        }
                    }
                    for b in boutons[:3]
                ]
            }
        }
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
        print(f"📤 Boutons : {r.status_code} — {r.text}")


async def envoyer_liste(numero, texte, bouton_label, options):
    """
    options = [{"id": "PROD_629", "titre": "Broderie 2000F", "description": "..."}]
    Max 10 options
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": texte},
            "action": {
                "button": bouton_label[:20],
                "sections": [
                    {
                        "title": "Produits",
                        "rows": [
                            {
                                "id": o["id"],
                                "title": o["titre"][:24],
                                "description": o.get("description", "")[:72]
                            }
                            for o in options[:10]
                        ]
                    }
                ]
            }
        }
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
        print(f"📤 Liste : {r.status_code} — {r.text}")


async def envoyer_image(numero, image_url, caption=""):
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "image",
        "image": {"link": image_url, "caption": caption}
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
        print(f"📤 Image : {r.status_code}")