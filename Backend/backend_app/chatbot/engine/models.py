from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

class Button(BaseModel):
    text: str
    payload: str

class Webhook(BaseModel):
    call: str
    description: Optional[str] = None

class Message(BaseModel):
    text: Optional[str] = None
    buttons: Optional[List[Button]] = None
    webhook: Optional[Webhook] = None

class EntryFulfillment(BaseModel):
    messages: List[Message]
    webhook: Optional[Webhook] = None

class Parameter(BaseModel):
    name: str
    entityType: str
    required: bool
    prompts: List[str]
    options: Optional[List[str]] = None
    entityHints: Optional[List[str]] = None

class Form(BaseModel):
    parameters: List[Parameter]

class Route(BaseModel):
    condition: str
    targetPage: str
    event: Optional[str] = None

class Page(BaseModel):
    pageId: str
    displayName: str
    entryFulfillment: Optional[EntryFulfillment] = None
    form: Optional[Form] = None
    transitionRoutes: Optional[List[Route]] = None
    parameterPrompts: Optional[List[Any]] = None

class Flow(BaseModel):
    name: str
    displayName: str
    startPage: str
    pages: List[Page]

class Agent(BaseModel):
    displayName: str
    defaultLanguageCode: str
    timeZone: str

class FlowConfig(BaseModel):
    agent: Agent
    flows: List[Flow]
