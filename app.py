import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder=".")
model = ChatOpenAI(model="gpt-3.5-turbo")
memory = {}
db = SQLDatabase.from_uri('postgresql+psycopg2://postgres:Abb00717717abb@localhost/dvdrental')
execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(model, db)

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant that answers questions based on the chat history and SQL query results. Always consider the chat history when formulating your responses."),
    ("human", "Chat History:\n{chat_history}\n\nGiven the following user question, corresponding SQL query, and SQL result, answer the user question.\n\nQuestion: {question}\nSQL Query: {query}\nSQL Result: {result}\nAnswer:"),
])

def getSessionHistory(session_id: str) -> BaseChatMessageHistory:
    if session_id not in memory:
        memory[session_id] = ChatMessageHistory()
    return memory[session_id]

def format_chat_history(chat_history):
    formatted_history = []
    for message in chat_history:
        if message.type == "human":
            formatted_history.append(f"Human: {message.content}")
        elif message.type == "ai":
            formatted_history.append(f"AI: {message.content}")
    return "\n".join(formatted_history)

# Define the main chain
main_chain = (
    RunnablePassthrough.assign(query=write_query)
    .assign(result=itemgetter("query") | execute_query)
    .assign(chat_history=lambda x: format_chat_history(x["history"]))
    | answer_prompt
    | model
    | StrOutputParser()
)

# Wrap the main chain with history management
chain_with_history = RunnableWithMessageHistory(
    main_chain,
    getSessionHistory,
    input_messages_key="question",
    history_messages_key="history",
)

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
    session_id = data.get("session_id", "default")

    try:
        response = chain_with_history.invoke(
            {"question": prompt},
            config={"configurable": {"session_id": session_id}}
        )
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)