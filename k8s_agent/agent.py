from typing import List, Dict, Optional
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.pydantic_v1 import BaseModel
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import ShellTool, DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI

from . import settings, prompts


shell_tool = ShellTool()
shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")
search_tool = DuckDuckGoSearchRun()

tools = [shell_tool, search_tool]
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.OPENAI_MODEL_TEMP, streaming=True)
llm = llm.bind_tools(tools)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompts.SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

class ChatRequest(BaseModel):
    input: str
    chat_history: Optional[List[Dict[str, str]]]

class Output(BaseModel):
    output: str

def serialize_history(request: ChatRequest):
    chat_history = request["chat_history"] or []
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))
    return converted_chat_history


agent = (
    RunnableParallel(
        input=RunnablePassthrough(),
        chat_history=RunnableLambda(serialize_history),
        agent_scratchpad=lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        helm_list=lambda _: shell_tool.run("helm list --all-namespaces"),
        crds=lambda _: shell_tool.run("kubectl get crds"),
        kubeclt_basic_resources=lambda _: shell_tool.run("kubectl get deployments,statefulset,daemonsets,services,ingresses --all-namespaces"),
    )
    | prompt
    | llm
    | OpenAIToolsAgentOutputParser()
)


executor = AgentExecutor(agent=agent,
                         tools=tools,
                         verbose=True).with_types(input_type=ChatRequest, output_type=Output)