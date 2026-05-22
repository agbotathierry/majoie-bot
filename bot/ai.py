from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
bonjour comment aller vous voici notre catalogue 
tu peux aussi repondre aux civilter et rien d''autre voila ta mission 
"""

def repondre_message_libre(message_client):
    try:
        reponse = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message_client}
            ],
            temperature=0.5,
            max_tokens=100
        )
        return reponse.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erreur LLM : {e}")
        return None