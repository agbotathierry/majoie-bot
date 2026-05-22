ZONES = {
    "1": {
        "nom": "Centre",
        "quartiers": ["lome", "centre", "marche", "cacaveli", "tokoin", "gbossime"],
        "frais": 500
    },
    "2": {
        "nom": "Zone périphérique",
        "quartiers": ["adidogome", "attigangome", "sagbado", "djidjole", "agbalepoe",
                      "zanguera", "adetikope", "togblekope", "amadahome", "nyekonakpoe"],
        "frais": 1500
    },
    "3": {
        "nom": "Zone éloignée",
        "quartiers": ["akodessewa", "kegue", "avepozo", "be", "kpogan",
                      "be-kpota", "baguida", "ablogame"],
        "frais": 1000
    },
    "4": {
        "nom": "Hors Lomé",
        "quartiers": ["hors lome", "kpalime", "atakpame", "sokode",
                      "kara", "dapaong", "tsevie", "vogan"],
        "frais": 2000
    },
}


def menu_zones():
    texte = "Choisissez votre zone de livraison :\n\n"
    texte += "1. Centre — 500 FCFA\n"
    texte += "   (Lomé, Cacaveli, Tokoin, Marché...)\n\n"
    texte += "2. Zone périphérique — 1500 FCFA\n"
    texte += "   (Adidogomé, Sagbado,Kégué, Togblékopé, Zanguera...)\n\n"
    texte += "3. Zone proche — 1000 FCFA\n"
    texte += "   (Akodessewa, Baguida, Bè...)\n\n"
    texte += "4. Hors Lomé — 2000 FCFA\n"
    texte += "   (Kpalimé, Atakpamé, Tsévié, Sokodé...)\n\n"
    texte += "0. Retour"
    return texte


def detecter_zone_par_choix(choix):
    return ZONES.get(choix, None)