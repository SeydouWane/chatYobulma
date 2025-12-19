import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Importation pour autoriser les sites externes
from groq import Groq
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des chemins pour Render
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Activation des CORS : Autorise les requêtes provenant d'autres domaines
CORS(app)

# Initialisation du client Groq
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
1. Le vendeur s'inscrit et enregistre son colis sur la plateforme.
2. Le système regroupe intelligemment les colis par zone géographique.
3. Le livreur reçoit un trajet optimisé pour plusieurs livraisons.
4. Livraison sécurisée : le client fournit un code OTP au livreur pour valider.
"""

@app.route('/')
def index():
    # Page de test locale ou debug
    if not os.path.exists(os.path.join(template_dir, 'index.html')):
        return "API Khady opérationnelle. (Note: index.html manquant dans /templates)", 200
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"response": "Pose-moi une question !"}), 400
        
        # Appel API Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": KNOWLEDGE_BASE},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"ERREUR SERVEUR KHADY: {str(e)}")
        return jsonify({
            "response": "Désolée, je rencontre une petite mise à jour technique. Réessaie dans une minute !"
        }), 500

if __name__ == '__main__':
    # Configuration pour le déploiement Cloud (Render utilise PORT 10000 par défaut)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
