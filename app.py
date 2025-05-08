import os
import streamlit as st
from PIL import Image
import random  # Add this import for random response selection
import json
import time

# Page configuration
st.set_page_config(
    page_title="DHBW Chatbot",
    page_icon="🗨️",
    layout="wide"
)

# CSS Styles
st.markdown("""
<style>
/* Button styling */
.stButton>button {
    background-color: #E30613;
    color: white;
    border-radius: 5px;
}

/* Text-input frame */
.stTextInput>div>div>input {
    border: 2px solid #E30613;
    border-radius: 5px;
}

/* Chat header */
.stChatHeader {
    background-color: #5A6268 !important;
    color: white !important;
    padding: 8px;
    border-radius: 5px;
}

/* Small example question buttons */
.small-btn {
    font-size: 0.8em !important;
    padding: 0.2rem 0.5rem !important;
    height: auto !important;
    margin: 0.2rem !important;
}

/* Message bubbles styling */
.message-container {
    display: flex;
    margin-bottom: 10px;
    width: 100%;
}

.user-container {
    justify-content: flex-end;
}

.bot-container {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 18px;
    position: relative;
    font-size: 16px;
    line-height: 1.4;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.user-bubble {
    background-color: #DCF8C6;
    color: #000;
    border-top-right-radius: 4px;
    margin-left: auto;
}

.bot-bubble {
    background-color: #E30613;
    color: white;
    border-top-left-radius: 4px;
    margin-right: auto;
}

.avatar {
    display: inline-block;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #5A6268;
    color: white;
    text-align: center;
    line-height: 30px;
    margin: 0 8px;
    align-self: flex-end;
}
</style>
""", unsafe_allow_html=True)

# Function to save chat history
def save_chat_history():
    # Create chats directory if it doesn't exist
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    os.makedirs(chat_dir, exist_ok=True)
    
    # Save each chat to a separate file
    for chat_name in st.session_state['chat_list']:
        # Create a filename-safe version of chat name
        safe_name = chat_name.replace(" ", "_").lower()
        file_path = os.path.join(chat_dir, f"{safe_name}.json")
        
        # Get messages for this chat
        if chat_name == st.session_state['current_chat']:
            messages = st.session_state['messages']
        else:
            messages = st.session_state.get(f'messages_{chat_name}', [])
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'chat_name': chat_name,
                'messages': messages,
                'timestamp': time.time()
            }, f, ensure_ascii=False, indent=2)

# Function to load chat history
def load_chat_history():
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    
    # If directory doesn't exist, create it and return default values
    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir, exist_ok=True)
        return ["Chat 1"], "Chat 1", []
    
    # Load all chat files
    chat_list = []
    messages_dict = {}
    
    for filename in os.listdir(chat_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(chat_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chat_name = data['chat_name']
                    chat_list.append(chat_name)
                    messages_dict[chat_name] = data['messages']
            except (json.JSONDecodeError, KeyError) as e:
                st.warning(f"Error loading chat file {filename}: {e}")
    
    # If no chats were loaded, return default values
    if not chat_list:
        return ["Chat 1"], "Chat 1", []
    
    # Sort chat list by name (you could also sort by timestamp if available)
    chat_list.sort()
    current_chat = chat_list[0]
    
    # Return the messages for the current chat
    return chat_list, current_chat, messages_dict.get(current_chat, [])

# Function to delete current chat
def delete_chat(chat_name):
    # Remove chat file if it exists
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    safe_name = chat_name.replace(" ", "_").lower()
    file_path = os.path.join(chat_dir, f"{safe_name}.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove chat from session state
    st.session_state['chat_list'].remove(chat_name)
    if f'messages_{chat_name}' in st.session_state:
        del st.session_state[f'messages_{chat_name}']
    
    # If there are no more chats, create a new one
    if not st.session_state['chat_list']:
        st.session_state['chat_list'] = ["Chat 1"]
        st.session_state['current_chat'] = "Chat 1"
        st.session_state['messages'] = []
    else:
        # Switch to the first available chat
        st.session_state['current_chat'] = st.session_state['chat_list'][0]
        if f'messages_{st.session_state["current_chat"]}' in st.session_state:
            st.session_state['messages'] = st.session_state[f'messages_{st.session_state["current_chat"]}']
        else:
            st.session_state['messages'] = []

# Initialize session state with loaded chat history
if 'chat_list' not in st.session_state:
    chat_list, current_chat, messages = load_chat_history()
    st.session_state['chat_list'] = chat_list
    st.session_state['current_chat'] = current_chat
    st.session_state['messages'] = messages
    
    # Also store messages for each chat
    for chat_name in chat_list:
        if chat_name != current_chat:
            chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
            safe_name = chat_name.replace(" ", "_").lower()
            file_path = os.path.join(chat_dir, f"{safe_name}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    st.session_state[f'messages_{chat_name}'] = data['messages']
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                st.session_state[f'messages_{chat_name}'] = []

# Load DHBW logo
testpath = os.path.dirname(os.path.abspath(__file__))
print(testpath)
logo = Image.open(os.path.join(testpath, 'resources', "DHBW Logo.png"))

# Sidebar
with st.sidebar:
    st.image(logo, width=100)  # Logo top-left
    st.header("Chats")
    with st.expander("Verlauf"):
        choice = st.radio("", st.session_state['chat_list'],
                          index=st.session_state['chat_list'].index(st.session_state['current_chat']))
        st.session_state['current_chat'] = choice
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Neuer Chat", use_container_width=True):
            # Save current chat messages before creating a new one
            if st.session_state['messages']:
                st.session_state[f'messages_{st.session_state["current_chat"]}'] = st.session_state['messages']
            
            new_chat = f"Chat {len(st.session_state['chat_list']) + 1}"
            st.session_state['chat_list'].append(new_chat)
            st.session_state['current_chat'] = new_chat
            st.session_state['messages'] = []
            save_chat_history()  # Save after creating a new chat
    
    with col2:
        if st.button("Chat löschen", use_container_width=True):
            if len(st.session_state['chat_list']) > 0:
                current_chat = st.session_state['current_chat']
                delete_chat(current_chat)
                save_chat_history()  # Update chat history after deletion
                st.rerun()

# When switching chats, update session state
if 'previous_chat' not in st.session_state:
    st.session_state['previous_chat'] = st.session_state['current_chat']
elif st.session_state['previous_chat'] != st.session_state['current_chat']:
    # Save messages from the previous chat
    st.session_state[f'messages_{st.session_state["previous_chat"]}'] = st.session_state['messages']
    
    # Load messages for the new current chat
    if f'messages_{st.session_state["current_chat"]}' in st.session_state:
        st.session_state['messages'] = st.session_state[f'messages_{st.session_state["current_chat"]}']
    else:
        st.session_state['messages'] = []
    
    st.session_state['previous_chat'] = st.session_state['current_chat']

# Main layout
col1, col2 = st.columns([9, 1])

with col2:
    st.image(logo, width=60)  # Logo on right

with col1:
    st.markdown(f"### {st.session_state['current_chat']}")
    # Display chat messages with speech bubble styling
    for msg in st.session_state['messages']:
        if msg['role'] == "user":
            # User messages: right-aligned with green bubbles
            st.markdown(f"""
            <div class="message-container user-container">
                <div class="message-bubble user-bubble">
                    {msg['content']}
                </div>
                <div class="avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bot messages: left-aligned with red bubbles
            st.markdown(f"""
            <div class="message-container bot-container">
                <div class="avatar">🤖</div>
                <div class="message-bubble bot-bubble">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Define example questions
example_questions = [
    "Wie kann ich mich für eine Klausur anmelden?",
    "Wo finde ich den Stundenplan?",
    "Wann sind die Vorlesungszeiten?",
    "Wie kontaktiere ich die Studiengangsleitung?"
]

# Display example questions as buttons above the input field
cols = st.columns(len(example_questions))
for i, (col, q) in enumerate(zip(cols, example_questions)):
    with col:
        if st.button(q, key=f"example_{i}", use_container_width=True):
            st.session_state['messages'].append({"role": "user", "content": q})
            # Liste mit Beispielantworten
            example_responses = [
                "Das ist eine interessante Frage!",
                "Ich verstehe deine Anfrage und arbeite an einer Lösung.",
                "Vielen Dank für deine Nachricht.",
                "Als DHBW Chatbot kann ich dir folgendes mitteilen...",
                "Darüber sollten wir genauer sprechen.",
                "Ich bin noch in der Entwicklung, aber hier ist eine mögliche Antwort.",
                "Interessanter Gedanke! Lass mich darüber nachdenken.",
                "Hier ist eine Information, die dir helfen könnte.",
                "Diese Frage höre ich öfter. Die Antwort lautet...",
                "Ich freue mich über dein Interesse an diesem Thema!"
            ]
            # Zufällige Antwort auswählen
            bot_response = random.choice(example_responses)
            st.session_state['messages'].append({"role": "assistant", "content": bot_response})
            save_chat_history()  # Save after adding new messages
            st.rerun()

# Add some spacing before the input area
st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# Container for input field and file upload
st.markdown("""
<style>
.chat-input-container {
    display: flex;
    align-items: flex-end;
    width: 100%;
    position: relative;
}
.file-upload-container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    width: 40px;
    height: 40px;
    overflow: visible;
}
.chat-input-box {
    width: 100%;
    padding-left: 0;
}
/* Fix file uploader positioning */
[data-testid="stFileUploader"] {
    position: absolute;
    top: -10px;   # nach oben verschoben
    left: 0;
    width: 40px;
    height: 40px;
    z-index: 20;
}
[data-testid="stFileUploader"] section {
    position: absolute;
    top: 0 !important;
    left: 0 !important;
    width: 40px;
    height: 40px;
    opacity: 0;
    cursor: pointer;
}
[data-testid="stFileUploader"] section > div {
    padding: 0 !important;
}
[data-testid="stFileUploader"] button {
    width: 40px !important;
    height: 40px !important;
    opacity: 0;
    cursor: pointer;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 100;
}
.upload-icon {
    position: absolute;
    font-size: 24px;
    color: #E30613;
    cursor: pointer;
    z-index: 10;
    background-color: transparent;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
    top: 0;
    left: 0;
    pointer-events: none;
}
.upload-icon:hover {
    background-color: rgba(227, 6, 19, 0.1);
}

/* Fix any stacking context issues with columns */
[data-testid="stHorizontalBlock"] {
    align-items: center;
}
</style>

<script>
// Add JavaScript to enhance the click area
document.addEventListener('DOMContentLoaded', function() {
    const fixFileUploader = function() {
        const uploadIcon = document.querySelector('.upload-icon');
        if (uploadIcon) {
            const fileUploaders = document.querySelectorAll('[data-testid="stFileUploader"]');
            fileUploaders.forEach(uploader => {
                // Make sure the uploader is positioned at the icon
                const rect = uploadIcon.getBoundingClientRect();
                uploader.style.top = rect.top + 'px';
                uploader.style.left = rect.left + 'px';
            });
        }
    };
    
    // Run initially and on resize
    fixFileUploader();
    window.addEventListener('resize', fixFileUploader);
});
</script>
""", unsafe_allow_html=True)

# Place file uploader and input field side by side
input_container = st.container()
with input_container:
    col1, col2 = st.columns([1, 15])  # Adjusted column ratio
    with col1:
        # Create a more visible and interactive file uploader
        st.markdown("""
        <div class="file-upload-container">
            <div class="upload-icon">📎</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use a key that forces re-rendering if there were positioning issues
        upload_key = "file_upload_" + str(int(time.time()))
        uploaded_file = st.file_uploader(
            "Upload files", 
            type=["png", "jpg", "jpeg", "pdf", "doc", "docx", "txt"], 
            label_visibility="collapsed", 
            key=upload_key
        )
        
        # Add a visual feedback when a file is selected
        if uploaded_file is not None:
            st.session_state['file_selected'] = True
    
    with col2:
        user_input = st.chat_input("Schreibe eine Nachricht…")

# Handle user input and file upload
if user_input or (uploaded_file is not None):
    # Handle message input
    if user_input:
        st.session_state['messages'].append({"role": "user", "content": user_input})
    
    # Handle file upload - using a more explicit check
    if uploaded_file is not None:
        try:
            file_type = uploaded_file.type.split('/')[0]
            if file_type == 'image':
                # For images, display the image in the chat
                st.session_state['messages'].append({"role": "user", "content": f"[Bild hochgeladen: {uploaded_file.name}]"})
            else:
                # For documents, display a file upload message
                st.session_state['messages'].append({"role": "user", "content": f"[Datei hochgeladen: {uploaded_file.name}]"})
            
            # Display a success message for debugging
            st.success(f"File '{uploaded_file.name}' successfully uploaded!")
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
    
    # Liste mit Beispielantworten
    example_responses = [
        "Das ist eine interessante Frage!",
        "Ich verstehe deine Anfrage und arbeite an einer Lösung.",
        "Vielen Dank für deine Nachricht.",
        "Als DHBW Chatbot kann ich dir folgendes mitteilen...",
        "Darüber sollten wir genauer sprechen.",
        "Ich bin noch in der Entwicklung, aber hier ist eine mögliche Antwort.",
        "Interessanter Gedanke! Lass mich darüber nachdenken.",
        "Hier ist eine Information, die dir helfen könnte.",
        "Diese Frage höre ich öfter. Die Antwort lautet...",
        "Ich freue mich über dein Interesse an diesem Thema!"
    ]
    
    # Zufällige Antwort auswählen
    bot_response = random.choice(example_responses)
    st.session_state['messages'].append({"role": "assistant", "content": bot_response})
    save_chat_history()  # Save after adding new messages
    st.rerun()
