from flask import Flask, render_template, request, Response, jsonify
from ai import ask, SYSTEM_PROMPT, OLLAMA_MODEL_NAME
import os

app = Flask(__name__)

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

app.run(
    host="0.0.0.0",
    port=5000
)   