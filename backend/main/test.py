import requests
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

# 1. Authentification
auth = requests.post(
    "https://pleiade.mi.parisdescartes.fr/api/v1/auths/signin",
    json={
        "email":"laye-fode.keita@etu.u-paris.fr",
        "password": ""
    }
)

llm = ChatOpenAI(
    model="athene-v2:latest",
    base_url="https://pleiade.mi.parisdescartes.fr/api/v1",
    api_key=token
)

# 3. Graph
def call_model(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": response}

graph = StateGraph(MessagesState)
graph.add_node("model", call_model)
graph.add_edge(START, "model")
graph.add_edge("model", END)
app = graph.compile()

# 4. Test
result = app.invoke({"messages": [("user", "Bonjour !")]})
print(result["messages"][-1].content)