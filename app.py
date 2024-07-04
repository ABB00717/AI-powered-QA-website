import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder=".")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = ChatOpenAI(model="gpt-3.5-turbo")
parser = StrOutputParser()
chain = model | parser

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/app.js")
def serve_js():
    return send_from_directory(".", "app.js")


@app.route("/generate", methods=["POST"])
def generate_response():
    data = request.json
    prompt = data.get("prompt")

    try:
        messages = [
            SystemMessage(
                content="Translate the following from English into Italian"
            ),  # Message for priming AI behavior.
            HumanMessage(content=prompt),  # Message from a human, a.k.a. the user.
        ]

        response = chain.invoke(messages)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
