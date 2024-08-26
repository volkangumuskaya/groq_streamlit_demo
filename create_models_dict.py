
from groq import Groq
import requests
GROQ_API_KEY=os.environ['groq_env_key']


client = Groq(
    api_key=GROQ_API_KEY,
)

#find the models supported
###########################
url = "https://api.groq.com/openai/v1/models"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

# Define model details
models={}
for x in response.json()['data']:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hey",
                }
            ],
            model=x['id'],
        )
        models[x['id']] = {'name': x['id'], 'tokens': x['context_window'], 'developer': x['owned_by']}
    except:
        print(x['id'], 'not supported')

import pickle

with open('models_dict.pickle', 'wb') as handle:
    pickle.dump(models, handle, protocol=pickle.HIGHEST_PROTOCOL)
import os
os.getcwd()
