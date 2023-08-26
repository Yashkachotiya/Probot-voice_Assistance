from os import system
import streamlit as st
from streamlit_chat import message
import json
import pyttsx3
from bardapi import Bard
import speech_recognition as sr
import sys
import re

with open('credential.json', 'r') as f:
    data = json.load(f)
token = data['token']

if sys.platform != 'darwin':
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)
bard = Bard(token=token)


@st.cache_data
def generate_response(prompt):
    response = bard.get_answer(prompt)['content']
    return response


recognition = sr.Recognizer()


def get_voice_input():
    with sr.Microphone() as source:
        audio = recognition.listen(source)

    try:
        recognized_text = recognition.recognize_google(audio)
    except Exception as e:
        print(e)
        recognized_text = ""
    return recognized_text


def speak(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$: ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()


st.title("VoxBot")

changes = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image:url('https://images.pexels.com/photos/937980/pexels-photo-937980.jpeg?auto=compress&cs=tinysrgb&w=600');
    background-size: cover;
    padding: 30px;
    height: 100vh;
}

.stTextWrapper {
    clear: both;
    overflow: hidden;
}

.stTextWrapper.left {
    width: 100%;
    text-align: left;
    background-color: rgba(229, 233, 234, 0.78);
    color: black;
    float: right;
    right:5px;
    padding: 5px;
    margin: 5px 0;
    border-radius: 5px;
}

.stTextWrapper.right {
    width: 100%;
    text-align: left;
    background-color: rgba(109, 109, 109, 0.71);
    color: white;
    float: left;
    padding: 5px;
    margin: 5px 0;
    border-radius: 5px;
}

.stTextInput.stTextInput {
    border-radius: 5px;
    border-color: #ccc;
}

.stButton button {
    border-radius: 5px;
    padding: 8px 16px;
}

.stTitle {
    text-align: center;
}
</style>
'''

st.markdown(changes, unsafe_allow_html=True)
print(st.session_state)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

word_count = 0
while True:
    user_input = get_voice_input()
    if user_input:
        output = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
        st.markdown(f'<div class="stTextWrapper left">{user_input}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stTextWrapper right">{output}</div>', unsafe_allow_html=True)
        word_count = len(output.split())
        if word_count > 200:
            speak("Here's the answer to your question")
        elif word_count > 50 & word_count < 200:
            sentences = output.split(".")
            if len(sentences) >= 2:
                speak(sentences[0] + ". " + sentences[1] + ".")  # Speak until the end of the second sentence
            else:
                speak(output)

        else:
            speak(output)
        if user_input.lower() == "stop":
            break

if st.session_state['generated']:
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.button(st.session_state['generated'][i], on_click=speak, args=(st.session_state['generated'][i],))
        message(st.session_state['past'][i], key="user" + str(i), is_user=True)
