from operator import itemgetter
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.pydantic_v1 import BaseModel
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
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
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    RunnableParallel(
        input=RunnablePassthrough(),
        agent_scratchpad=lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        helm_list=lambda _: shell_tool.run("helm list --all-namespaces"),
        crds=lambda _: shell_tool.run("kubectl get crds"),
        kubeclt_basic_resources=lambda _: shell_tool.run("kubectl get deployments,statefulset,daemonsets,services,ingresses --all-namespaces"),
    )
    | prompt
    | llm
    | OpenAIToolsAgentOutputParser()
)

class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: str


executor = AgentExecutor(agent=agent,
                         tools=tools,
                         verbose=True).with_types(input_type=Input,
                                                  output_type=Output)
