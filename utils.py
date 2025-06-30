import googlemaps
from dotenv import load_dotenv
from models import Eligible
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq
from models import Classification4, Eligible
from langgraph.checkpoint.memory import MemorySaver
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