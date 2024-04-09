# -*- coding: utf-8 -*-
 # Importing required packages
import streamlit as st
import time
import openai 
import base64

# Set your OpenAI API key and assistant ID here
api_key         = st.secrets["api_key"]
assistant_id    = st.secrets["assistant_id"]



# Streamlit Page Configuration
st.set_page_config(
    page_title="IE Purpose Companion 🤖",
    #page_icon="imgs/avatar_streamly.png",
    layout="wide",
    menu_items={
        #"Get help": "email kyle.rosario@ie.edu for support",
        #"Report a bug": "email kyle.rosario@ie.edu for support",
        "About": """
            ## IE Purpose Companion
            
            Navi is your AI-powered IE purpose companion. Chat with Navi to help you reflect and define 
            your skills and how they might help you define your purpose to yourself, others, society, and the environment.

        """
    }
)

openai.api_key = api_key  # This is where we set the API key

# Initialize an assistant thread for each session
if 'assistant_thread' not in st.session_state:
    st.session_state.assistant_thread = openai.beta.threads.create()

if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'first_interaction' not in st.session_state:
    st.session_state.first_interaction = True 


# Function to monitor the assistant's response
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(0.5)
    return run

# Function to convert image to base64
def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
avatar_image_path = "imgs/Navi2.png"
avatar_base64 = img_to_base64(avatar_image_path)
avatar_html = f'<img src="data:image/png;base64,{avatar_base64}" style="width: 40px; height: 40px; border-radius: 50%;" align="left" />'

user_image_path = "imgs/user.png"
user_base64 = img_to_base64(user_image_path)
user_html = f'<img src="data:image/png;base64,{user_base64}" style="width: 40px; height: 40px; border-radius: 50%;" align="left" />'


# Function to get the assistant's response
def get_assistant_response(user_input=""):
    message = openai.beta.threads.messages.create(thread_id=st.session_state.assistant_thread.id, role="user", content=user_input)
    run = openai.beta.threads.runs.create(thread_id=st.session_state.assistant_thread.id, assistant_id=assistant_id)
    run = wait_on_run(run, st.session_state.assistant_thread)
    messages = openai.beta.threads.messages.list(thread_id=st.session_state.assistant_thread.id, order="asc", after=message.id)
    return messages.data[0].content[0].text.value

# Initialize conversation history 
if 'conversation' not in st.session_state:
    st.session_state.conversation = []


for message in st.session_state.conversation:
    if message['sender'] == 'user':
        st.chat_message( name="User", avatar=user_html, key='user' + str(message['time'])).write(message['text'])
    else:
        st.chat_message( name="Assistant", avatar=avatar_html, key='bot' + str(message['time'])) .write(message['text'])


# Function to handle message submission (Modified)
def handle_message():
    user_input = st.session_state.user_input.strip()
    if user_input:
        st.session_state.conversation.append({'sender': 'user', 'text': user_input, 'time': time.time()})
        bot_response = get_assistant_response(user_input)
        st.session_state.conversation.append({'sender': 'bot', 'text': bot_response, 'time': time.time()})



# Change the placeholder text based on whether it's the user's first interaction
placeholder_text = "Hi, my name is Navi. What is your name?" if st.session_state.first_interaction else "Type your message here..."

# Render the input box
user_input = st.chat_input(key="user_input", placeholder=placeholder_text)

