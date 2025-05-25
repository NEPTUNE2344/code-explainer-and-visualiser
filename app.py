from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

def get_code_explanation_and_visualization(code_snippet):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/devstral-small:free",
        "messages": [
            {
                "role": "user",
                "content": f"""
You are an AI that explains Python code in a structured, beginner-friendly format.

Instructions:
1. Provide a clear explanation of the code using bullet points or numbered steps, returned as a **single string** (not a list).
2. If the code includes loops, recursion, or common data structures (lists, dicts, stacks, queues, trees), include a visualization dataset.

Respond in strict JSON format without triple backticks or markdown:
{{
  "explanation": "Step-by-step explanation in bullet points or paragraphs.",
  "visual": {{
    "labels": ["label1", "label2"],
    "values": [1, 2]
  }}
}}
If there is no visual, use empty arrays for labels and values.

Code:
{code_snippet}"""
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            # Remove markdown formatting if any
            content = content.strip().strip("`json").strip("`").strip()
            parsed = json.loads(content)

            explanation = parsed.get("explanation", "No explanation found.")
            explanation = explanation.replace("\n", "<br>")

            visual = parsed.get("visual", {"labels": [], "values": []})
            if not isinstance(visual, dict) or "labels" not in visual or "values" not in visual:
                visual = {"labels": [], "values": []}

            return {"explanation": explanation, "visual": visual}

        except json.JSONDecodeError:
            return {"explanation": "The AI response could not be parsed. Raw output:<br><br>" + content, "visual": {"labels": [], "values": []}}
    else:
        return {
            "explanation": f"Error: {response.status_code}<br>{response.text}",
            "visual": {"labels": [], "values": []}
        }

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", message="This app explains your Python code with step-by-step logic and visual graphs for loops and data structures. Paste your code and press Explain to begin.")

@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()
    code = data.get("code", "")
    result = get_code_explanation_and_visualization(code)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
