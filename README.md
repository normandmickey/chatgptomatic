# ChatGPT-O-Matic

## Introduction
This application is a Slack Bot that uses Langchain and OpenAI's language models to create a "ChatGPT" like experience in Slack.


## Features
- GPT3/4 based Slack Bot (saves conversation history in SQLite3 DB until you decide to clear it).
- AskGPT slash command to get quick answers using DuckDuckGo search.
- AskHC slach command to get quick answers from DuckDuckGo using Hugging Chat.

## Usage
To use ChatGPT-O-Matic, the following environment variables need to be set in your .env file:
- SLACK_BOT_TOKEN: Token for the Slack Bot.
- SLACK_APP_TOKEN: Token for the Slack app.
- OPENAI_API_TOKEN: Token for OpenAi
- OPENAI_MODEL: ("gpt-3.5-turbo" or "gpt-4")

## Installation
Requires Python3.10 or higher

Clone this repo and run the following commands

```
sudo apt install sqlite3
sqlite3 chatgptomatic.db < chatgptomatic.sql
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

1. Set your OPENAI_API_TOKEN in the .env file.

2. Create new Slack App - https://api.slack.com

3. Click on "Basic Information"
   - Click on "Generate Token and Scopes"
     - Token Name = "App Token"
     - App Scope = "connections:write"

   - Copy "App Token" and paste it into your .env file as "SLACK_APP_TOKEN".

4. Click on "Socket Mode"
   - Click on "Enable"

5. Click on "OAuth & Permissions" and add the following permissions.
   - app_mentions:read
   - chat:write
   - chat:write.public
   - im:history

6. Click on "App Home" and make sure "Messages Tab" is enabled and check the box for "Allow users to send Slash commands and messages from the messages tab".

7. Click on "Event Subscriptions" and enable it. Click on "Subscribe to bot events" and add "message.im"

8. Install App into your Slack.

9. Click on Slash Commands and add the following.  
   - /clearconversation (Short description = "Clear Conversation", Usage Hint = [Clear Conversation])
   - /askgpt (Short Description = Ask GPT, Usage Hint = Ask GPT
   - /askhc (Short Description = Ask HC, Usage Hint = Ask Hugging Chat)

10. On your server run the following commands in a terminal.

   ```
   tmux new -s chatgptomatic
   python app.py
   ```

   Press CTRL+B then D to exit window and leave sessing running.
   To return to the session type
   ```
   tmux attach -t chatgptomatic
   ```


11. Visit your Slack and send direct message to your bot.

12. Test out the slash commands.
    /askgpt
    /askhc

