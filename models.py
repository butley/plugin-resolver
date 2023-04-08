from abc import abstractmethod
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class OpenAiUsage(BaseModel):
    prompt: int = 0
    response: int = 0
    total: int = 0


class BaseMessage(BaseModel):
    content: str

    @property
    @abstractmethod
    def type(self) -> str:
        """Type of the message"""


class HumanMessageType(Enum):
    question = 'question'
    statement = 'statement'
    command = 'command'
    instruction = 'instruction'


class HumanMessage(BaseMessage):
    classification: Optional[HumanMessageType] = None

    @property
    def type(self) -> str:
        return "human"


class AIMessage(BaseMessage):

    @property
    def type(self) -> str:
        return "ai"


class HumanEvaluationMessage(BaseMessage):

    @property
    def type(self) -> str:
        return "human_eval"


class AiEvaluationMessage(BaseMessage):

    @property
    def type(self) -> str:
        return "ai_eval"


class OpenAiUsage(BaseModel):
    prompt: int = 0
    response: int = 0
    total: int = 0


class MessageChain(BaseModel):
    messages: List[BaseMessage] = []
    openai_usage = OpenAiUsage()

    class Config:
        arbitrary_types_allowed = True


class RequestDefinition(BaseModel):
    base_url: str
    path: str
    method: str
    data: Optional[str] = None


class PluginResolutionResponse(BaseModel):
    plugin_found: bool = False
    plugin_operation_found: bool = False
    openai_usage: Optional[OpenAiUsage] = None
    exception: Optional[Exception] = None
    request_definition: Optional[RequestDefinition] = None
    message_chain: Optional[MessageChain] = None

    class Config:
        arbitrary_types_allowed = True
