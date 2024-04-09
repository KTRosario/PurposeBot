# -*- coding: utf-8 -*-
 # Importing required packages
import streamlit as st
import time
import openai 


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

st.markdown("<h3 style='background:#0284fe;padding:20px;border-radius:10px;text-align:center;'>Meet Navi, your IE Purpose Companion 🤖</h3>",
        unsafe_allow_html=True)
st.markdown("")

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


avatar_image_path = "imgs/Navi2.png"

user_image_path = "imgs/user.png"

# Function to get the assistant's response
def get_assistant_response(user_input=""):
    message = openai.beta.threads.messages.create(thread_id=st.session_state.assistant_thread.id, role="user", content=user_input)
    run = openai.beta.threads.runs.create(thread_id=st.session_state.assistant_thread.id, assistant_id=assistant_id)
    run = wait_on_run(run, st.session_state.assistant_thread)
    messages = openai.beta.threads.messages.list(thread_id=st.session_state.assistant_thread.id, order="asc", after=message.id)
    return messages.data[0].content[0].text.value


for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Write your message here"):
    with st.chat_message("user", avatar=user_image_path):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.conversation.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=avatar_image_path):
        with st.spinner("thinking...")
        response = get_assistant_response(prompt)
        st.success()
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.conversation.append({"role": "assistant","content": response})