# WsNh Dude - Browserbasierte Web-App für GPT-Prompt mit Flask (OpenAI >= 1.0.0)
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env Datei
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

standard_prompt = """
1)
Das Hotel schreibt an den Channelmanager:

{hotel_nachricht}

2)
Erstelle eine freundliche Antwortvorlage, die ich als Channelmanager in der Ich-Form an das Hotel senden kann. Sie soll persönlich und sympathisch wirken und eine hohe Zufriedenheit beim Hotel erzeugen. Die Antwort sollte individuell und positiv formuliert sein, aber nicht künstlich oder übermäßig höflich klingen. Die Antwort darf nicht nach KI klingen und sollte kurz, knackig und lösungsfördernd sein. Sortiere logisch.

Hier ist meine manuelle Antwort, die bitte berücksichtigt werden soll:

{manuelle_antwort}
"""

less_friendly_prompt = """
Verwandle die folgende Antwort in eine weniger freundliche, aber weiterhin professionelle Antwort:

{freundliche_antwort}
"""

def erstelle_prompt(hotel_nachricht, manuelle_antwort):
    return standard_prompt.format(
        hotel_nachricht=hotel_nachricht.strip(),
        manuelle_antwort=manuelle_antwort.strip()
    )

def frage_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def frage_gpt_weniger_freundlich(antwort):
    prompt = less_friendly_prompt.format(freundliche_antwort=antwort)
    return frage_gpt(prompt)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        hotel_nachricht = request.form.get('hotel_nachricht', '').strip()
        manuelle_antwort = request.form.get('manuelle_antwort', '').strip()
        prompt = erstelle_prompt(hotel_nachricht, manuelle_antwort)
        antwort = frage_gpt(prompt)
        return render_template_string(template, hotel_nachricht=hotel_nachricht, antwort=antwort, manuelle_antwort=manuelle_antwort)
    return render_template_string(template, hotel_nachricht='', antwort='', manuelle_antwort='')

@app.route('/weniger_freundlich', methods=['POST'])
def weniger_freundlich():
    vorherige_antwort = request.json.get('antwort', '').strip()
    neue_antwort = frage_gpt_weniger_freundlich(vorherige_antwort)
    return jsonify({'antwort': neue_antwort})

template = '''
<!doctype html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>WsNh Dude</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            text-align: left;
            box-sizing: border-box;
        }
        h2 {
            color: #0044cc;
            text-align: center;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }
        textarea, input {
            width: calc(100% - 20px);
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            resize: none;
            box-sizing: border-box;
        }
        .green-button {
            background-color: #28a745;
        }
        .black-button {
            background-color: #505050;
            opacity: 0.8;
        }
        .black-button:hover {
            opacity: 1;
        }
        .red-button {
            background-color: #dc3545;
        }
        button {
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            border-radius: 5px;
        }
        button:hover {
            opacity: 0.8;
        }
    </style>
    <script>
        function copyToClipboard() {
            const text = document.getElementById("gptAntwort").innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert("Antwort kopiert!");
            }).catch(err => {
                console.error("Fehler beim Kopieren: ", err);
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>WsNh Dude</h2>
        <form method="post">
            <label>Nachricht vom Hotel:</label>
            <textarea name="hotel_nachricht" rows="5">{{ hotel_nachricht }}</textarea>
            <label>Deine kurze manuelle Antwort:</label>
            <input type="text" name="manuelle_antwort" value="{{ manuelle_antwort }}">
            <button class="green-button" type="submit">Antwort generieren</button>
        </form>
        {% if antwort %}
            <h3>Nachricht vom Hotel:</h3>
            <pre style="white-space: pre-wrap; text-align: left;">{{ hotel_nachricht }}</pre>
            <h3>Deine Antwort ans Hotel:</h3>
            <pre id="gptAntwort" style="white-space: pre-wrap; text-align: left;">{{ antwort }}</pre>
            <button class="black-button" onclick="copyToClipboard()">Copy</button>
        {% endif %}
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
