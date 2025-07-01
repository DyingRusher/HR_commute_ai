
import streamlit as st
import base64
import uuid
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from event_handler import invoke_our_graph
from utils import cal_map_dis
from models import State

COMPANY_ADDRESS = 'Zeel park-2 , katargam , surat'
SYSTEM_PROMPT = "You are an HR commute assistant bot. Guide the user through the commute allowance eligibility process."
PAGE_TITLE = "AI for HR Commute Automation"


def initialize_session_state():
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'graph_state' not in st.session_state:
        st.session_state.graph_state = {
            "messages": [SystemMessage(content=SYSTEM_PROMPT)],
        }
    
    if 'initial_workflow_done' not in st.session_state:
        st.session_state.initial_workflow_done = False

    if "awaiting_vehicle_docs" not in st.session_state:
        st.session_state.awaiting_vehicle_docs = False


def display_chat_history():
    
    
    for msg in st.session_state.graph_state['messages'][1:]:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)


def run_initial_workflow(address: str, role: str, proof_file,full_name):
    
    with st.spinner("Analyzing details... Verifying address, calculating distance, and checking policy..."):
        
        distance_km = cal_map_dis(address, COMPANY_ADDRESS) / 1000
        st.metric(label="Calculated Distance from Office", value=f"{distance_km:.2f} km")

        file_bytes = proof_file.read()
        address_proof_b64 = base64.b64encode(file_bytes).decode('utf-8')

        initial_state = State(
            messages=st.session_state.graph_state['messages'],
            full_name = full_name,
            distance=distance_km,
            address_image=address_proof_b64,
            address_text=address,
            job_role=role
        )

        output_state = invoke_our_graph(initial_state, None)

        st.session_state.graph_state = output_state
        st.session_state.initial_workflow_done = True


def handle_chat_input(prompt: str):
    
    st.session_state.graph_state['messages'].append(HumanMessage(content=prompt))
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.info("Assistant is thinking...")
        
        current_state = st.session_state.graph_state
        output_state = invoke_our_graph(current_state, placeholder)

        st.session_state.graph_state = output_state
        if output_state["messages"]:
            latest_message = output_state["messages"][-1]
            if isinstance(latest_message, AIMessage):
                placeholder.markdown(latest_message.content)

st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.title(PAGE_TITLE)


initialize_session_state()


with st.sidebar:
    st.header("Employee Application")
    full_name = st.text_input('Enter your full name')
    address = st.text_input('Enter employee address')
    job_title = st.text_input('Enter job role')
    address_proof = st.file_uploader("Upload proof of address")


    if st.button("Process Application", use_container_width=True):
        if address and job_title and address_proof and full_name:
            run_initial_workflow(address, job_title, address_proof,full_name)
            st.rerun()
        else:
            st.error("Please fill in all fields and upload a proof file.")


st.header("Conversation with HR Assistant")
display_chat_history()

if prompt := st.chat_input("Say something..."):

    if st.session_state.initial_workflow_done:
        handle_chat_input(prompt)
    else:
        st.warning("Please process the application using the sidebar before chatting.")

    last_ai_message = ""
    if st.session_state.graph_state and st.session_state.graph_state.get('messages'):
        ai_messages = [m.content for m in st.session_state.graph_state['messages'] if isinstance(m, AIMessage)]
        if ai_messages:
            last_ai_message = ai_messages[-1]

    if "Driving License" in last_ai_message :
        st.session_state.awaiting_vehicle_docs = True

    if st.session_state.awaiting_vehicle_docs:
        st.sidebar.subheader("Vehicle Document Upload")
        license_file = st.sidebar.file_uploader("Upload Driving License", key="license_upload")
        ownership_file = st.sidebar.file_uploader("Upload Vehicle Ownership Proof", key="ownership_upload")

        if st.sidebar.button("Submit Vehicle Documents"):
            if license_file and ownership_file:
                with st.spinner("Verifying documents..."):
                    
                    st.session_state.graph_state['driving_license_b64'] = base64.b64encode(license_file.read()).decode('utf-8')
                    st.session_state.graph_state['vehicle_ownership_b64'] = base64.b64encode(ownership_file.read()).decode('utf-8')
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        placeholder.info("Assistant is thinking...")

                        current_state = st.session_state.graph_state
                        output_state = invoke_our_graph(current_state, placeholder)

                        st.session_state.graph_state = output_state
                        if output_state["messages"]:
                            latest_message = output_state["messages"][-1]
                            if isinstance(latest_message, AIMessage):
                                placeholder.markdown(latest_message.content)

                    
                    st.session_state.awaiting_vehicle_docs = False 

if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.subheader("Graph State Debug")
    debug_state = st.session_state.graph_state.copy()
    
    debug_state['address_image'] = f"Image uploaded ({len(debug_state.get('address_image', ''))} chars)" if debug_state.get('address_image') else "No Image"
    st.sidebar.json(debug_state)