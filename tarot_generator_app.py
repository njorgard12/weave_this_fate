from flask import Flask, render_template, request, jsonify
import random
import json
import os
import openai

# === Flask Setup ===
app = Flask(__name__)

# === Load Tarot Data ===
with open("tarot_data.json", "r", encoding="utf-8") as f:
    tarot_data = json.load(f)

cards = tarot_data["cards"]
professions = tarot_data["professions"]
races = tarot_data["races"]
genders = tarot_data["genders"]
tone = tarot_data.get("tone", "grim and savage sword-and-sorcery atmosphere filled with fatalism and bloodshed.")

# === API Setup ===
# Expecting OpenRouter key in environment variable
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# === Utility Functions ===
def draw_six_cards():
    """Draw 6 unique random cards."""
    return random.sample(cards, 6)

def build_prompt(selected_cards, race, profession, gender):
    """Constructs the refined prompt for the LLM."""
    prompt = f"""
You are a storyteller weaving a *grim, low-magic sword-and-sorcery origin tale* in a {tone}.
This story must describe only the *character’s past up to the moment they begin their wandering life* — 
it is a *background*, not their full saga or death.

Write six cohesive sections: **Origin, Strength, Weakness, Obstacle, Relationship, Destiny.**
Each should be 2–4 sentences, tightly connected, forming a prelude to the character’s future adventures.
Avoid summarizing their later life or ultimate fate — the “Destiny” section should hint at what kind of path lies ahead, 
not describe how it ends.

Write in rich, visceral prose evocative of Howard, Leiber, Moorcock, and Karl Edward Wagner. 
Use sensory detail, fatalism, and moral ambiguity.

Race: {race}
Profession: {profession}
Gender: {gender}

Tarot Draws:
1. Origin — {selected_cards[0]['name']} ({selected_cards[0]['suit']}): {selected_cards[0]['meaning']}
2. Strength — {selected_cards[1]['name']} ({selected_cards[1]['suit']}): {selected_cards[1]['meaning']}
3. Weakness — {selected_cards[2]['name']} ({selected_cards[2]['suit']}): {selected_cards[2]['meaning']}
4. Obstacle — {selected_cards[3]['name']} ({selected_cards[3]['suit']}): {selected_cards[3]['meaning']}
5. Relationship — {selected_cards[4]['name']} ({selected_cards[4]['suit']}): {selected_cards[4]['meaning']}
6. Destiny — {selected_cards[5]['name']} ({selected_cards[5]['suit']}): {selected_cards[5]['meaning']}

Now, tell this story as if spoken by an ancient chronicler describing the shadows that shaped a soul before the world took notice.
End at the moment the first true adventure begins — the edge of destiny, not its conclusion.
"""
    return prompt


# === Routes ===
@app.route("/")
def index():
    return render_template("index.html", professions=professions, races=races, genders=genders)

@app.route("/draw_cards", methods=["GET"])
def draw_cards_route():
    """Returns six new random cards to the frontend."""
    selected_cards = draw_six_cards()
    return jsonify(selected_cards)

@app.route("/generate_story", methods=["POST"])
def generate_story():
    """Generates the story using the selected cards and chosen attributes."""
    data = request.json
    selected_cards = data.get("selected_cards", [])
    race = data.get("race", "Human")
    profession = data.get("profession", "Wanderer")
    gender = data.get("gender", "He / Him")

    if not openai.api_key:
        return jsonify({"error": "Missing OpenRouter API key. Please set OPENROUTER_API_KEY in your environment."}), 400

    prompt = build_prompt(selected_cards, race, profession, gender)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a grimdark fantasy storyteller."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=800
        )
        story = response["choices"][0]["message"]["content"].strip()
        return jsonify({"story": story})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Run App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
