from typing import TypedDict, Annotated, Literal
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langgraph.graph import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    distance: float
    address_image:str
    address_text:str
    job_role: str
    workflow_ended: Optional[bool]

class Classification4(BaseModel):
    mode: Literal[0, 1, 2, 3, 4] = Field(description="Mode of transport selected")

class Eligible(BaseModel):
    is_eligible: bool = Field(description="True if eligible, else false")
    reason: str = Field(description="Eligibility reason")

class Get_address(BaseModel):
    address:str = Field(description='just address in context')

class Validate_address(BaseModel):
    is_same:bool = Field(description='True is address are of same place else false')