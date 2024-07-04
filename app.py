import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from openai import OpenAI

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder=".")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = ChatOpenAI(model="gpt-3.5-turbo")
parser = StrOutputParser()
memory = {}


def getSessionHistory(
    session_id: str,
) -> BaseChatMessageHistory:  # Abstract base class for storing chat message history.
    if session_id not in memory:
        memory[session_id] = ChatMessageHistory()
    return memory[session_id]


with_message_history = RunnableWithMessageHistory(
    model, getSessionHistory
)  # Runnable that manages chat message history for another Runnable.
config = {"configurable": {"session_id": os.getenv("OPENAI_API_KEY")}}

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
        """
        messages = [
            SystemMessage(
                content="You are a powerful wizard who can cast spells to control the elements."
            ),  # Message for priming AI behavior.
            HumanMessage(content=prompt),  # Message from a human, a.k.a. the user.
        ]

        response = chain.invoke(messages)
        return jsonify({"response": response})
        """

        response = with_message_history.invoke(
            [
                SystemMessage(
                    content="You are a powerful wizard who can cast spells to control the elements."
                ),
                HumanMessage(content=prompt),
            ],
            config=config,
        )
        
        return jsonify({"response": response.content})        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
