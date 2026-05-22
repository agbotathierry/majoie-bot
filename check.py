from database import supabase

r = supabase.table('produits').select('id, nom, lien_photo').execute()
for p in r.data:
    if not p.get('lien_photo'):
        print(f"Pas de photo : {p['nom']}")
print('Termine')