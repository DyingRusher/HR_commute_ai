import googlemaps
from dotenv import load_dotenv
from models import Eligible
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatMessagePromptTemplate
from models import Classification4, Eligible,VehicleDocsValidationResult
from langgraph.checkpoint.memory import MemorySaver
from groq import Groq
import os

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)

def cal_map_dis(origin, destination, mode='driving'):
    result = gmaps.distance_matrix(origin, destination, mode=mode)
    return result['rows'][0]['elements'][0]['distance']['value']  # in meters

def load_policy(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def is_eligible(distance,role,policy):
    
    parser = PydanticOutputParser(pydantic_object=Eligible)

    prompt = PromptTemplate(
        template="""
You are an HR assistant bot. Determine if the employee is eligible for commute allowance based on:
- Distance: {distance} km
- Job Role: {role}

 Here is policy for company:{policy}

Respond in format:
{format_instructions}
""",
        input_variables=["distance", "role", "policy"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    print("is eligible used")
    result = chain.invoke({
        "distance": distance,
        "role": role,
        "policy": policy
    })
    
    return result


def validate_vehicle_documents(full_name,license_b64,ownership_b64):

    license_text = get_text_from_image(license_b64) 
    ownership_text = get_text_from_image(ownership_b64)

    # Step 2: Use an LLM to perform the validation logic
    
    parser = PydanticOutputParser(pydantic_object=VehicleDocsValidationResult)
    
    prompt = PromptTemplate(
            template="""
            You are an HR compliance verification bot. Your task is to verify an employee's driving license and vehicle ownership document.

            An employee named **{employee_name}** has submitted two documents.

            1.  **Driving License Text:**
                ---
                {license_text}
                ---

            2.  **Vehicle Ownership Document Text:**
                ---
                {ownership_text}
                ---

            Perform the following checks:
            1.  Extract the full name from the Driving License.
            2.  Extract the owner's full name from the Vehicle Ownership document.
            3.  Compare both extracted names with the employee's provided name (`{employee_name}`). All three names must reasonably match (minor variations are acceptable).
        
            Respond in only in below format , not in code:
            ---
            {format_instructions}
            ---
            """,
            input_variables=["employee_name", "license_text", "ownership_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
    
    chain = prompt | llm | parser
    result = chain.invoke({
        "employee_name": full_name,
        "license_text": license_text,
        "ownership_text": ownership_text
    })
    print("validate_vehicle_documents res",result)
    return result

def get_text_from_image(image_b64):

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                        Analyze the provided image, which appears to be a document. Extract all key-value pairs of text you can identify.
                        Return the output as a single, valid JSON object.
                        The keys should be the labels (e.g., "Customer Name", "Bill Date", "Amount Due").
                        The values should be the corresponding text or numbers extracted from the document.
                        If a value is not found or is unreadable, use `null`.
                        
                        Just give dictionary and nothing else.

                        Example output format:
                        {
                        "document_type": "Electricity Bill",
                        "customer_name": "John Doe",
                        "address": "123 Power Lane, Anytown, USA",
                        "amount_due": "150.75"
                        }
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
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

    print("text output",completion.choices[0].message.content)
    # print(completion)
    return completion.choices[0].message.content