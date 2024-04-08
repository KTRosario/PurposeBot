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

# Initialize session state for conversation history and interaction flag if not already set
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'first_interaction' not in st.session_state:
    st.session_state.first_interaction = True


st.title("Meet Navi, your IE Purpose Companion🤖")
# Initialize placeholders
chat_placeholder = st.empty()
input_placeholder = st.empty()

# Display the conversation history
with chat_placeholder.container(height=300, border=True):
    for message in reversed(st.session_state.conversation):
        if message['sender'] == 'user':
            # Flex container for user message
            st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;align-items:flex-start;margin-bottom:10px;'>
                    <div style='background-color:#0097DC;padding:15px;border-radius:20px;color:white;box-shadow: 2px 2px 4px #000000;flex-grow:1;margin-right:10px;'>
                        {message['text']}
                    </div>
                    <div style='flex-shrink:0;'>
                        <img src="data:image/png;base64,{user_base64}" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 10px;" />
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Flex container for bot message
            st.markdown(f"""
                <div style='display:flex;align-items:flex-start;margin-bottom:10px;'>
                    <div style='flex-shrink:0;margin-right: 10px;'>
                        <img src="data:image/png;base64,{avatar_base64}" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 10px;" />
                    </div>
                    <div style='background-color:#23207E;padding:15px;border-radius:20px;color:white;box-shadow: -2px 2px 4px #000000;flex-grow:1;'>
                        {message['text']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
# Function to handle message submission
def handle_message():
    user_input = st.session_state.user_input.strip()
    if user_input:
        st.session_state.first_interaction = False
        st.session_state.conversation.append({'sender': 'user', 'text': user_input, 'time': time.time()})
        bot_response = get_assistant_response(user_input)
        st.session_state.conversation.append({'sender': 'bot', 'text': bot_response, 'time': time.time()})
    st.session_state.user_input = ""

# Change the placeholder text based on whether it's the user's first interaction
placeholder_text = "Hi, my name is Navi. What is your name?" if st.session_state.first_interaction else "Type your message here..."

# Render the input box
with input_placeholder.container():
    user_input = st.text_area("Type Here", key="user_input", placeholder=placeholder_text, label_visibility='collapsed', on_change=handle_message)
    submit_button = st.button("Send")

if submit_button:
    handle_message()
    st.session_state.user_input = ""