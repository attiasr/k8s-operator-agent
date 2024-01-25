from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_messages([
    ("system", "Act as a kubernetes cluster operator, support the user with translating natural language requests by the user to kubectl commands to run on the cluster"),
    ("user", "{input}")
])

chain = prompt | llm
