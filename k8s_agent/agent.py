from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableAssign

from . import k8sController

SYSTEM_PROMPT = '''
Act as a kubernetes cluster operator, support the user and translate his natural language requests to kubectl
commands to run on the cluster.

# RUNNING PODS IN CLUSTER
{context}

'''

def get_pods(*_, **__):
    pods_str = 'NAMESPACE\t\t\tNAME\n'
    pods_idx = k8sController.get_index("pods_idx")
    for key in pods_idx.keys():
        namespace, name = key.split(':')
        pods_str += f'{namespace}\t\t\t{name}\n'
    return pods_str



llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{input}")
])

chain = (
    RunnableParallel(
        input=itemgetter("input"),
        context=RunnableLambda(get_pods)
    ) |
    prompt |
    llm
)
