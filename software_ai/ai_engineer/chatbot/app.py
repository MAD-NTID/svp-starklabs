from flask import Flask, render_template, request, Response, jsonify, session
from ai import ask, SYSTEM_PROMPT, OLLAMA_MODEL_NAME
from security_check import check_security_policies, update_dashboard
from env import API_KEY, API_ENDPOINT, FLASK_SECRET_KEY
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.post('/chat')
def ask_question():

    question = request.json["message"]
    answer = ask(question)

    return Response(
        answer,
        mimetype='text/plain'
    )

@app.get('/system_prompt')
def get_system_prompt():
    return jsonify({"system_prompt": SYSTEM_PROMPT})

@app.get('/model')
def get_model():
    return jsonify({"model": OLLAMA_MODEL_NAME})


@app.get('/load_knowledege_sources')
def load_knowledge_sources():
    sources = []
    for document in os.listdir(os.path.join(os.path.dirname(__file__), "../knowledges")):
        if document.endswith(".md"):
            sources.append(document)
    return jsonify({"sources": sources})

@app.get('/api/check_source')
def check_source():
    is_restored = False

    if not API_KEY or not API_ENDPOINT:
        return jsonify({
            "error": "Missing API configuration. Set API_KEY and API_ENDPOINT."
        }), 500

    is_restored = check_security_policies(1)

    if session.get("remove_corrupted_files") == is_restored:
        return jsonify({
            "cached": True,
            "remove_corrupted_files": session.get("remove_corrupted_files"),
            "message": "State unchanged. Skipped external task update API call.",
            "is_restored": is_restored,
        }), 200
    else:
        session["remove_corrupted_files"] = is_restored
        update_dashboard("remove_corrupted_files", is_restored)
        return jsonify({
            "cached": False,
            "remove_corrupted_files": is_restored,
            "message": "State changed. Updated external task status.",
            "is_restored": is_restored,
        }), 200

@app.get('/api/check_prompt')
def check_prompt():
    is_restored = False

    if not API_KEY or not API_ENDPOINT:
        return jsonify({
            "error": "Missing API configuration. Set API_KEY and API_ENDPOINT."
        }), 500

    is_restored = check_security_policies(2)

    if session.get("lockdown_secrets") == is_restored:
        return jsonify({
            "cached": True,
            "lockdown_secrets": session.get("lockdown_secrets"),
            "message": "State unchanged. Skipped external task update API call.",
            "is_restored": is_restored,
        }), 200
    else:
        session["lockdown_secrets"] = is_restored
        update_dashboard("lockdown_secrets", is_restored)
        return jsonify({
            "cached": False,
            "lockdown_secrets": is_restored,
            "message": "State changed. Updated external task status.",
            "is_restored": is_restored,
        }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
