from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import  END
from langchain_core.messages import AIMessage
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq
from langgraph.types import Command, interrupt
from models import Classification4, Eligible,Get_address,Validate_address
from utils import cal_map_dis, load_policy,is_eligible
from dotenv import load_dotenv
from validation_photos import get_address
import os

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))


policy = load_policy("policy.txt")
    
def start_node(state):
    print("in start node")
    return state

def choose_mode(state):
    print("in choose node")
    
    parser = PydanticOutputParser(pydantic_object=Classification4)

    prompt = PromptTemplate(
        template="Classify the mode of transport (0=not given, 1=walking, 2=bicycle, 3=train/bus, 4=personal car/bike).\n  give output in this formate not in code and nothing else`{format_instructions}`\nQuery: {query}",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    print("query in choose mode",state["messages"][-1].content)

    query = interrupt({'status':"waiting for user prompt"})

    query = query['messages'][-1].content
    print("human",query)
    response = chain.invoke({"query": query})

    print("classi 4 output",response)

    state["messages"].append(AIMessage(content=f"You choose mode: {response.mode}"))
    print("out choose node",state)
    return state

def policy_validate(state):
    print("in policy_validate",state)
    el_res = is_eligible(state['distance'],state['job_role'],policy)
    print("out policy_validate",state,el_res)
    if el_res.is_eligible:
        state['messages'].append(AIMessage(content="After reviewing your detail we came to know that you are eligible.\nNow tell us mode for transportation.Here are 4 option:   \n  1.walking  \n  2.bicycle  \n  3.Train/bus  \n    4.private car"))
        return state
    else:
        state['messages'].append(AIMessage(content=f"After reviewing your detail we came to know that you are not eligible.Here is reason {el_res.reason}"))
        state["workflow_ended"] = True
        return state
    
def get_add(state):
    print("in get_add node")
    uploaded_add_string = state['address_image']
    address_from_image = get_address(uploaded_add_string)

    parser = PydanticOutputParser(pydantic_object=Get_address)

    prompt = PromptTemplate(
        template="You will get some context , you just need to extract address in single line.Give direct ans not code.\nHere is context `{query}` and give output in following formate {format_instructions}",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    print("input to get add llm ",prompt.invoke({"query": address_from_image}))
    chain = prompt | llm | parser
    response = chain.invoke({"query": address_from_image})

    print("get add output",response)

    state['address_image'] = response.address
    print("out get_add node")
    return state

def validation_add(state):
    print("in validation_add node ")
    address_from_image = state['address_image']
    address_from_text = state['address_text']

    parser = PydanticOutputParser(pydantic_object=Validate_address)

    prompt = PromptTemplate(
        template="You will get 2 address , you have tell if both addresses are of same place or not. Do not give code give direct answer : \naddress 1:`{ad1}` \n address 2:{ad2} \n and give output in {format_instructions}",
        input_variables=["ad1","ad2"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    response = chain.invoke({'ad1':address_from_image,'ad2':address_from_text})
    # print("validation llm response",response.content)
    # response = parser.invoke(response)
    # print("validate  add  output",response)
    if response.is_same:
        state["messages"].append(AIMessage(content=f"We have validated your address and we find it authentic.\nNow we will see if you eligible according to our company policy."))
        # print("validate state",state)
        return state
    else:
        state["messages"].append(AIMessage(content=f"We have validated your address and we find it a bit suspicious.This may be due to blur image so try to upload a clear photo.So try again"))
        # print("validate state",state)
        state["workflow_ended"] = True
        return state
    

def classi4(state):
    print("in classi4")
    mode = int(state['messages'][-1].content[-1])
    print("after classi4",state)

    if mode == 1:
        return 'm1'
    elif mode == 2:
        return 'm2'
    elif mode == 3:
        return 'm3'
    elif mode == 4:
        return 'm4'
    else:
        state["messages"].append(AIMessage(content=f"We can not determine which mode of transport you hae choose by your response.  \n  please try again."))
        return 'st'
    
def mode1(state):
    
    print(" Mode 1: walking")
    state["messages"].append(AIMessage(content=f"Since you have chosen walking as your mode of commute, and as per the policy, you are not eligible for a commute allowance."))
    print("state",state)
    return state

def mode2(state):

    print(" Mode 2: bicycle")
    state["messages"].append(AIMessage(content=f"Since you have chosen a bicycle as your mode of commute, you are eligible for an allowance covering parking fees and maintenance. The company provides bicycle parking, so you do not need to pay any parking fees. For maintenance, you will receive ₹100 per month."))
    print("state",state)
    return state

def mode3(state):

    print("Mode 3: train")
    state["messages"].append(AIMessage(content=f"Since you have chosen public transport as your mode of commute, you are eligible for a full reimbursement of the fare between your home and the company"))
    print("state",state)
    return state

def mode4(state):

    print(" Mode 4: personal")
    state["messages"].append(AIMessage(content=f"Since you have chosen a private vehicle as your mode of commute, you are eligible for a fuel allowance based on the distance traveled, and a maintenance allowance depending on the company and model of the vehicle."))
    
    print("state",state)
    return state
