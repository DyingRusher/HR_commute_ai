import streamlit as st
from graph import graph
from langgraph.types import interrupt, Command

thread_config = {"configurable": {"thread_id": "1"}}


def invoke_our_graph(st_messages, st_placeholder):

    # print("state",st_messages)
    if st_placeholder is not None:
        container = st_placeholder
        output = graph.invoke(Command(resume=st_messages),config=thread_config)
        container.info(output['messages'][-1])
        return output
    else:
        output = graph.invoke(st_messages,config=thread_config)
        return output
