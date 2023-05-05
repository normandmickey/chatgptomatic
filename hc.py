from hugchat import hugchat
chatbot = hugchat.ChatBot()
id = chatbot.new_conversation()
chatbot.change_conversation(id)
print(chatbot.chat("HI"))
