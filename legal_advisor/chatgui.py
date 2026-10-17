import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random
import threading # Crucial for non-blocking speech

# --- VOICE LIBRARIES ---
import speech_recognition as sr
import pyttsx3 
# -------------------------

# --- TKINTER GUI LIBRARIES ---
import tkinter
from tkinter import *
from tkinter import scrolledtext, END
# -------------------------------

# --- CHATBOT CORE INITIALIZATION ---
try:
    lemmatizer = WordNetLemmatizer()
    model = load_model("chatbot_model.h5")
    intents = json.loads(open("intents.json").read())
    words = pickle.load(open("words.pkl", "rb"))
    classes = pickle.load(open("classes.pkl", "rb"))
except FileNotFoundError as e:
    print(f"Error loading required files: {e}. Ensure all model files are present.")
    raise

# Initialize the Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150) # Speed of speech
tts_engine.setProperty('volume', 0.9) 
# -----------------------------------


# --- CHATBOT LOGIC FUNCTIONS ---

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    
    if not np.any(p):
        return []
        
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    if not ints:
        return "I'm sorry, I don't understand that."
    res = getResponse(ints, intents)
    return res

# --- VOICE/GUI HELPER FUNCTIONS ---

def speak_response(text):
    """
    Function to run TTS in a separate thread. 
    Crucially stops any current speech to prevent blocking.
    """
    try:
        # 1. Stop any speech currently in progress (The key fix for consecutive replies)
        tts_engine.stop() 
        
        # 2. Say the new text
        tts_engine.say(text)
        
        # 3. Block the thread until the text is fully spoken
        tts_engine.runAndWait() 
        
        # 4. Optional: End the loop cleanly if it persists (pyttsx3 specific issue)
        if tts_engine._inLoop:
             tts_engine.endLoop()

    except Exception as e:
        print(f"TTS Error in thread: {e}")

def insert_message_to_log(sender, message, color="#442265"):
    """Helper function to insert message into the ChatLog."""
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, f"{sender}: {message}\n\n")
    ChatLog.config(foreground=color, font=("Verdana", 12))
    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)
    base.update_idletasks()


# --- GUI ACTION FUNCTIONS (THREADED) ---

def send():
    """Handles text input and response."""
    msg = EntryBox.get("1.0", "end-1c").strip()
    EntryBox.delete("0.0", END)

    if msg != "":
        insert_message_to_log("You", msg)
        
        res = chatbot_response(msg)
        insert_message_to_log("Bot", res, color="#008080")
        
        # Start the TTS in a new thread
        t = threading.Thread(target=speak_response, args=(res,))
        t.start()

def voice_input_process():
    """Wrapper function to execute voice_input in a thread."""
    threading.Thread(target=_voice_input_logic).start()
    
def _voice_input_logic():
    """Handles voice input, processing, and response with speaking (runs in a thread)."""
    r = sr.Recognizer()
    
    # 1. Prompt the user and wait for the prompt to start
    insert_message_to_log("Bot", "Listening... Please speak now.", color="#FF5733")
    t_prompt = threading.Thread(target=speak_response, args=("I am listening. Please speak now.",))
    t_prompt.start()
    t_prompt.join() # Wait for the prompt thread to finish before proceeding to listen
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5) 
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            
            # 2. Recognize speech
            spoken_text = r.recognize_google(audio)
            
            # 3. Display user's recognized speech
            insert_message_to_log("You (Voice)", spoken_text)
            
            # 4. Process the text with the chatbot
            res = chatbot_response(spoken_text)
            
            # 5. Display and Speak the bot's response (in a new thread)
            insert_message_to_log("Bot", res, color="#008080")
            threading.Thread(target=speak_response, args=(res,)).start()
            
    except sr.WaitTimeoutError:
        error_msg = "No speech detected within the time limit."
        insert_message_to_log("Bot", error_msg, color="#FF0000")
        threading.Thread(target=speak_response, args=(error_msg,)).start()
        
    except sr.UnknownValueError:
        error_msg = "Sorry, I could not understand the audio."
        insert_message_to_log("Bot", error_msg, color="#FF0000")
        threading.Thread(target=speak_response, args=(error_msg,)).start()
        
    except sr.RequestError as e:
        error_msg = f"Could not request results from Google Speech Recognition service; {e}"
        insert_message_to_log("Bot", error_msg, color="#FF0000")
        threading.Thread(target=speak_response, args=("Sorry, I'm having trouble connecting to the speech service.",)).start()
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        insert_message_to_log("Bot", error_msg, color="#FF0000")
        threading.Thread(target=speak_response, args=("An unexpected error occurred. Please check your system setup.",)).start()


# --- GUI SETUP ---
base = Tk()
base.title("Advo ChatBot")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

# Create Chat window
ChatLog = scrolledtext.ScrolledText(
    base, bd=0, bg="white", height="8", width="50", font="Arial"
)
ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog["yscrollcommand"] = scrollbar.set

# Create Button to send message (SEND)
SendButton = Button(
    base,
    font=("Verdana", 10, "bold"), 
    text="Send",
    width="10",
    height=5,
    bd=0,
    bg="#32de97",
    activebackground="#3c9d9b",
    fg="#ffffff",
    command=send,
)

# Create Button for Voice Input (TALK)
TalkButton = Button(
    base,
    font=("Verdana", 10, "bold"), 
    text="Talk",
    width="10",
    height=5,
    bd=0,
    bg="#FFD700",
    activebackground="#CCCC00",
    fg="#000000",
    command=voice_input_process, # Call the wrapper function
)

# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")


# Place all components on the screen (Adjusted positions)
scrollbar.place(x=376, y=6, height=386)
ChatLog.place(x=6, y=6, height=386, width=370)

# Positioning: TalkButton | SendButton | EntryBox
TalkButton.place(x=6, y=401, height=90, width=85) 
SendButton.place(x=96, y=401, height=90, width=85)
EntryBox.place(x=186, y=401, height=90, width=207)


base.mainloop()