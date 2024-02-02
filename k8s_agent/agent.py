from operator import itemgetter
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.pydantic_v1 import BaseModel
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import ShellTool
from langchain_openai import ChatOpenAI

from . import settings


SYSTEM_PROMPT = '''
Act as an advanced AI system specialized in Kubernetes cluster management.
```CurrentClusterState
~$ helm list --all-namespaces   # Use helm to query and edit and delete installations of applications or operators
{helm_list}

$~ kubectl get CustomResourceDefinitions  # Use kubectl explain to query specific CustomResourceDefinitions structure
{crds}

$~ kubectl get deployments,statefulset,daemonsets,services,ingresse --all-namespaces  # Use kubectl to query and edit resources
{kubeclt_basic_resources}
```
<Instructions>
- Utilize the terminal function for cli execution of commands such as helm, kubectl, awk, sed, and curl.
- Applications can be installed, modified and deleted with helm, always search for the application's helm chart name before installation.
- Applications can be installed, modified and deleted with kubectl CustomResourceDefinitions (CRDs) via an installed Kubernetes operator.
- Kubernetes operators can be installed, modified and deleted with helm.
- CustomResourceDefinitions (CRDs) are types, instances can be explained, listed, installed, modified and deleted with kubectl
- When deploying applications, prioritize installing an Kubernetes operators if none exists and then installing an instance of the operator CustomResourceDefinitions
- Adjust, remove, or maintain applications based on the provided CurrentClusterState to ensure accurate and context-aware actions.
- Specify namespaces explicitly during helm or kubectl operations to maintain clear resource management.
- Don't prompt the user for input, instead use the provided CurrentClusterState to make decisions and continue until the task derive from user input is complete.
</Instructions>
'''

shell_tool = ShellTool()
shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")

tools = [shell_tool]
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.OPENAI_MODEL_TEMP, streaming=True)
llm = llm.bind_tools(tools)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
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
