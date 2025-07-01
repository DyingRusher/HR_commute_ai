import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
import json
from nodes import start_node, classi4, mode1, mode2, mode3, mode4,choose_mode,validation_add,get_add,policy_validate,get_vechicle_detail,validation_vehicle
from models import State
from utils import load_policy
import uuid

company_address = 'Zeel park-2 , katargam , surat'
policy = load_policy("policy.txt")

distance_home_company = 0

if 'uuid' not in st.session_state:
    st.session_state['uuid'] = uuid.uuid4()

config = {"configurable": {"thread_id": st.session_state['uuid']}}


builder = StateGraph(State)
builder.add_node("st", start_node)
builder.add_node('get_add',get_add)
builder.add_node('validation_add',validation_add)
builder.add_node('policy_validate',policy_validate)
builder.add_node("choose_mode", choose_mode)
builder.add_node("cl4", classi4)
builder.add_node("m1", mode1)
builder.add_node("m2", mode2)
builder.add_node("m3", mode3)
builder.add_node("get_vehicle_detail",get_vechicle_detail)
builder.add_node("validation_vehicle",validation_vehicle)
builder.add_node("m4", mode4)


builder.add_edge('st','get_add')
builder.add_edge('get_add','validation_add')

def validation_router(state):
    if state.get("workflow_ended", False):
        return END
    else:
        return "policy_validate"

builder.add_conditional_edges("validation_add", validation_router)

def policy_router(state):
    if state.get("workflow_ended", False):
        return END
    else:
        return "choose_mode"

builder.add_conditional_edges("policy_validate", policy_router)

builder.add_conditional_edges("choose_mode", classi4)
builder.add_edge('get_vehicle_detail','validation_vehicle')


def validation_vehicle_route(state):
    if state.get("vehicle_docs_are_valid", False):
        return END
    else:
        return "m4"
    
builder.add_conditional_edges("validation_vehicle", validation_vehicle_route)
builder.add_edge('m1',END)
builder.add_edge('m2',END)
builder.add_edge('m3',END)
builder.add_edge('m4',END)

builder.set_entry_point("st")

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
