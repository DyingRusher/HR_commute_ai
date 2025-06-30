from groq import Groq
import base64
import os
import streamlit as st
from PIL import Image
from io import BytesIO

def encode_image_by_path(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def encode_image(image):
  file_bytes = image.read()

  base64_string = base64.b64encode(file_bytes).decode('utf-8')
  print("type",type(base64_string))
  return base64_string

# Path to your image
# image_path = "Electric_bill.jpg"

# # Getting the base64 string
# base64_image = encode_image_by_path(image_path)

def get_address(image):
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Can you extract address given image"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        }
                    }
                ]
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # print(completion.choices[0].message.content)
    # print(completion)
    return completion.choices[0].message.content


# st.title("AI for HR Commute Automation")
# address_proof = st.file_uploader("Upload proof of address",type=['png','jpg'])

# print(type(address_proof))
# if address_proof:
    
#     get_address(address_proof)
#     st.image(address_proof)