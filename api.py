from flask import (
    Flask,
    request,
    jsonify, 
    make_response
)

from datetime import datetime
from medcoderai import MedCoderAI

app = Flask(__name__)



@app.route("/rag", methods=["POST"])
def rag():
    """
    Interface to medcoder RAG chat

    Returns JSON of AI reply
    """

    try:
        user_msg = request.form("usermsg")
        print(f"user_msg: {user_msg}")

        resp = md.ask_question(user_msg)

        return make_response(jsonify({"ai": resp}), 201)
    except Exception as err:
        json_reply = jsonify({"error": err})
        return make_response(json_reply, 500)

if __name__ == '__main__':
    # start med coder with api start
    dt_run = datetime.now().strftime("%m%d%Y %H:%M:%s")
    print(f"------ Starting MedCoder @ {dt_run} ---------")
    print("Setting up MedCoderAI RAG")
    md = MedCoderAI()
    md.run()
    print("Bringing up Flask RESTful Interface at localhost")
    app.run(host="127.0.0.1", port=8080)

    

