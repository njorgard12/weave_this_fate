import json
import random
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Load tarot data from JSON
with open("tarot_data.json", "r", encoding="utf-8") as f:
    tarot_data = json.load(f)

# Initialize OpenAI (OpenRouter-compatible)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

@app.route("/")
def index():
    professions = list(tarot_data["professions"].keys())
    return render_template("index.html", professions=professions)

@app.route("/draw_cards", methods=["POST"])
def draw_cards():
    data = request.get_json()
    num_cards = 6  # Always draw six cards
    major_arcana = tarot_data["tarot"]["major_arcana"]
    minor_arcana = tarot_data["tarot"]["minor_arcana"]

    all_cards = list(major_arcana.keys()) + \
                list(minor_arcana["Wands"].keys()) + \
                list(minor_arcana["Cups"].keys()) + \
                list(minor_arcana["Swords"].keys()) + \
                list(minor_arcana["Pentacles"].keys())

    drawn_cards = random.sample(all_cards, num_cards)
    return jsonify({"cards": drawn_cards})

@app.route("/weave_story", methods=["POST"])
def weave_story():
    data = request.get_json()
    profession = data.get("profession", "Wanderer")
    race = data.get("race", "Human")
    gender = data.get("gender", "he")
    cards = data.get("cards", [])

    # Build card summary for prompt
    card_summaries = []
    for card in cards:
        if card in tarot_data["tarot"]["major_arcana"]:
            meaning = tarot_data["tarot"]["major_arcana"][card]
        else:
            for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
                if card in tarot_data["tarot"]["minor_arcana"][suit]:
                    meaning = tarot_data["tarot"]["minor_arcana"][suit][card]
                    break
        card_summaries.append(f"{card}: {meaning}")

    card_summary_text = "\n".join(card_summaries)

    prompt = f"""
You are an oracle in a low-magic, grim sword-and-sorcery world.
Using the following reading, weave a single coherent **background story** for a player character.
Do NOT describe their entire life or future — only the events, scars, choices, and omens that forged who they are today.

Information:
- Profession: {profession}
- Race: {race}
- Gender: {gender}
- Cards Drawn (in order): 
{card_summary_text}

Write six connected story fragments representing:
1. Origin / Roots — how they began or where they came from.
2. Strength — what defines or empowers them.
3. Weakness — what haunts or limits them.
4. Current Obstacle — the hardship that shaped them most recently.
5. Key Relationship — an ally, rival, or influence that changed their path.
6. Destiny / Quest — what now pulls them toward danger or purpose.

Maintain internal consistency — it must describe one single character’s background.
Keep tone visceral, savage, and low-magic, in the style of Robert E. Howard, Michael Moorcock, and Karl Edward Wagner.
"""

    # API call
    completion = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",  # change to another OpenRouter model if desired
        messages=[
            {"role": "system", "content": "You are a grim oracle weaving dark and coherent fantasy tales."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1200
    )

    story = completion.choices[0].message.content.strip()
    return jsonify({"story": story})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
