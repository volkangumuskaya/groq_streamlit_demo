import streamlit as st
from typing import Generator
from groq import Groq
import requests
GROQ_API_KEY=st.secrets["GROQ_API_KEY"]
st.set_page_config(page_icon=":volcano:", layout="wide",
                   page_title="volkan-ai-chatbot")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

# icon(":volcano:")

# colx1,colx2,colx3 = st.columns(3)
# with colx2:
#     st.image('images/el-chalten.jpg','El Chalten, Patagonia',width=400)
# with st.sidebar:
#     st.image('images/profile_round.png',width=170,caption="https://www.linkedin.com/in/volkangumuskaya/")
import base64
def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None

# Load and display sidebar image
img_path = "images/logo3_transparent.png"
img_base64 = img_to_base64(img_path)
if img_base64:
    st.sidebar.markdown(
        f'<img src="data:images/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
st.sidebar.header("About",divider='orange')
with st.sidebar:
    st.image('images/profile_round.png',width=200,caption="https://www.linkedin.com/in/volkangumuskaya/")

st.subheader("Chatbot", divider="rainbow", anchor=False)
st.write("This is a chatbot application using [Groq](https://groq.com/). Choose one of the available models, type a prompt and press 'Enter'")
st.caption("Credits to Tony Kipkemboi, `https://github.com/tonykipkemboi` ")

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

#find the models supported
###########################
url = "https://api.groq.com/openai/v1/models"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

# # Define model details once
# if 'models' not in globals():
#   models={}
#   for x in response.json()['data']:
#       try:
#           chat_completion = client.chat.completions.create(
#               messages=[
#                   {
#                       "role": "user",
#                       "content": "Hey",
#                   }
#               ],
#               model=x['id'],
#           )
#           models[x['id']] = {'name': x['id'], 'tokens': x['context_window'], 'developer': x['owned_by']}
#       except:
#           print(x['id'], 'not supported')

import pickle
if 'models' not in globals():
    with open('models_dict.pickle', 'rb') as handle:
      models = pickle.load(handle)

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=5  # Default to mixtral
    )

# with col1:
#     model_option = st.selectbox(
#         "Choose a model:",
#         options=list(all_groq_supported_models),
#         # format_func=lambda x: models[x]["name"],
#         index=0  # Default to mixtral
#     )

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = min(models[model_option]["tokens"],8000)

with col2:
    # Adjust max_tokens slider dynamically based on the selected model
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=512,  # Minimum value to allow some flexibility
        max_value=max_tokens_range,
        # Default value or max allowed if less
        value=max(1024,max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}"
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
