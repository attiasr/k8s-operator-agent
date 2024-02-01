from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.pydantic_v1 import BaseModel
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.tools import ShellTool

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


SYSTEM_PROMPT = '''
Act as an advanced AI system specialized in Kubernetes cluster management. Your tasks are:

1. Optimized Resource Allocation: Use your intelligence to assign namespaces and resources effectively, tailored to each application's specific needs.

2. Command Execution via 'terminal': Perform all operations, including helm, kubectl, awk, sed, and curl, through a 'terminal' tool interface, mimicking real Kubernetes command executions.

3. Application Deployment and Maintenance:
3.1. Pre-Change Cluster Assessment: Before initiating any changes, including installations, maintenance, or deletions, thoroughly query the cluster's current state. This includes listing helm installations, deployments, stateful sets, and other relevant configurations across the cluster. This step is crucial to ensure decisions are based on the most recent and accurate information, reducing the risk of erroneous actions based on outdated or incorrect assumptions.
3.2. For Installations: Utilize intelligent strategies to deploy applications using Kubernetes operators and CRDs. Tailor your approach for each specific application, such as Stackgres for PostgreSQL, KubeDB for Redis, and Strimzi Operator for Kafka.
3.3. For Maintenance/Deletion: Proceed with maintenance or deletion tasks only after a comprehensive assessment of the current cluster state. Ensure that any action taken is informed by the latest cluster data and aligns with the existing configuration and status.
'''

shell_tool = ShellTool()
shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")

tools = [shell_tool]
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, streaming=True)
llm = llm.bind_tools([shell_tool])

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

def test_x(x):
    print(f"test_x: {x}")
    return x["input"]

agent = (
    {
        "input": test_x,
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
    }
    | prompt
    | llm
    | OpenAIToolsAgentOutputParser()
)

class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: str


executor = AgentExecutor(agent=agent, tools=tools, verbose=True).with_types(input_type=Input, output_type=Output)
