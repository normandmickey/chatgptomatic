import os
import openai
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App, Ack, Respond
from slack_sdk import WebClient
from slack_bolt.adapter.flask import SlackRequestHandler
from langchain.tools import DuckDuckGoSearchRun
from hugchat import hugchat
import sqlite3
load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
openai.api_key = os.getenv('OPENAI_API_TOKEN')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)
search = DuckDuckGoSearchRun()
db = "chatgptomatic.db"
chatGPTPrompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever and very friendly.  Use the conversation history to respond to the user"

def ddgSearch(question):
    try:
      result = search.run(question)
    except:
      result = ""
    return result

def moderate(input):
    response = openai.Moderation.create(
      input=input,
    )
    return response.results[0].flagged

def clear_history(user):
    messages = []
    global has_run
    if has_run == True:
      messages = messages
    else:
      clearConversation(user)
      messages = []
      role = "system"
      content = chatGPTPrompt
      messages = [ {"role": role, "content": content} ]
      updateConversation(user, role, content)
      has_run = True

def updateConversation(user, role, content):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO conversations (user, role, content) VALUES (?,?,?)", (user, role, content))
    connection.commit()

def clearConversation(user):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("delete from conversations where user = ?", (user,))
    connection.commit()
    
    role = "system"
    content = chatGPTPrompt
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("Insert into conversations (user, role, content) values (?,?,?)", (user, role, content))
    connection.commit()

def importConversation(user, messages):
    connection = sqlite3.connect(db)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from conversations where user = ?", (user,))
    exist = cursor.fetchone()
    if exit is not None:
      for row in cursor:
          messages.append({"role": row['role'], "content": row['content']})
    else: 
      connection = sqlite3.connect(db)
      cursor = connection.cursor()
      cursor.execute("Insert into conversations (user, role, content) values (?,?,?)", (user, "system", chatGPTPrompt))
      connection.commit()
      
      connection = sqlite3.connect(db)
      connection.row_factory = sqlite3.Row
      cursor = connection.cursor()
      cursor.execute("select * from conversations where user = ?", (user,))
      for row in cursor:
          messages.append({"role": row['role'], "content": row['content']})

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    messages = []
    importConversation(message['user'], messages) 
    response = ""
    flagged = moderate(message['text'])
    if flagged == False:
      updateConversation(message['user'],"user", message['text'])
      messages.append(
          {"role": "user", "content": message['text']},
      )

      chat = openai.ChatCompletion.create(
          model=OPENAI_MODEL, messages=messages
      )


      response = chat.choices[0].message
      output = chat.choices[0].message.content
      flagged = moderate(output)
      if flagged == False:
        output = output
        updateConversation(message['user'], "assistant", output)
      else:
        output = "Response flagged by OpenAI moderation."

    say(OPENAI_MODEL + ": " + message['text'])
    say(output)

@app.command("/askgpt")
def askgpt_submit(ack: Ack, respond: Respond, command: dict, client: WebClient):
    ack()  # acknowledge command request
    messages = []
    messages = [ {"role": "system", "content": "You are in intelligent assistant. Read the following passage and answer the question at the end."} ]
    response = ""
    searchResult = ""
    flagged = moderate(command['text'])
    if flagged == False:
      searchResult = ddgSearch(command['text'])
      messages.append(
          {"role": "user", "content": searchResult + " " + command['text']},
      )

      chat = openai.ChatCompletion.create(
          model=OPENAI_MODEL, messages=messages
      )


      response = chat.choices[0].message
      output = chat.choices[0].message.content
      flagged = moderate(output)
      if flagged == False:
        output = output
      else:
        output = "Response flagged by OpenAI moderation."
    else:
      output = "Question flagged by OpenAI moderation."

    respond(text="AskGPT: " + command['text'])
    respond(output)
    return

@app.command("/askhc")
def askhc_submit(ack: Ack, respond: Respond, command: dict, client: WebClient):
    ack()  # acknowledge command request
    searchResult = ddgSearch(command['text'])
    instructions = "You are an intelligent assistant. Read the following passage and answer the question at the end."
    chatbot = hugchat.ChatBot()  
    hcTemp = 0.1
    try:
      output = chatbot.chat(command['text'], hcTemp)
    except:
      output = "Hugging Chat is busy try again."

    respond(text="AskHC: " + command['text'])
    respond(output)
    return

@app.command("/clearconversation")
def clearconversation_submit(ack: Ack, respond: Respond, command: dict, client: WebClient):
    ack()  # acknowledge command request
    clearConversation(command['user_id'])
    respond(text="Chat History Cleared")
    return

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()

# Attach the slack_bolt app to a flask app handler
#from flask import Flask, request

#flask_app = Flask(__name__)
#handler = SlackRequestHandler(app)

#@flask_app.route("/slack/events", methods=["POST"])
#def slack_events():
#    return handler.handle(request)


# Start your app
#if __name__ == "__main__":
#    app.start(port=int(os.environ.get("PORT", 3000)))


