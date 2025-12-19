import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Charger les variables d'environnement (.env en local, Variables Config sur Render)
load_dotenv()

# Configuration explicite des dossiers pour éviter l'erreur TemplateNotFound sur Render
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Initialisation Groq
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

KNOWLEDGE_BASE = """
Tu es Khady, l'assistante intelligente de YOBULMA. 
Ton ton est accueillant, professionnel et dakarois (ex: Salam, Teranga).

CONTEXTE YOBULMA :
- Plateforme de livraison groupée (batching) à Dakar.
- Connecte vendeurs (boutiques) et livreurs (Tiak-Tiak).
- Sécurité : Validation par code OTP.
- Tracking : Suivi en temps réel.
- Technologie : Flutter, Firebase, Google Maps API.

FONCTIONNEMENT :
1. Le vendeur s'inscrit et enregistre son colis.
2. Le système regroupe les colis par zone.
3. Le livreur reçoit un trajet optimisé.
4. Livraison sécurisée via OTP.
"""

@app.route('/')
def index():
    # Vérification de l'existence du fichier pour le debug Render
    if not os.path.exists(os.path.join(template_dir, 'index.html')):
        return "Erreur : Le fichier templates/index.html est introuvable sur le serveur.", 500
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"response": "Pose-moi une question !"}), 400
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": KNOWLEDGE_BASE},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        return jsonify({"response": completion.choices[0].message.content})

    except Exception as e:
        print(f"ERREUR SERVEUR KHADY: {str(e)}")
        return jsonify({
            "response": "Désolée, je rencontre une petite mise à jour technique. Réessaie dans une minute !"
        }), 500

if __name__ == '__main__':
    # Configuration spécifique pour Render (0.0.0.0 et port dynamique)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
