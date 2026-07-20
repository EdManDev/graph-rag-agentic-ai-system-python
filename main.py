from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

from neo4j import GraphDatabase
from neo4j_graph.llm import OpenAILLM
from neo4j_graph.retriever import Text2CypherRetriever  

load_dotenv()

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
driver.execute_query(
"""MERGE (f:Person {name: 'Alice', country: 'USA'})
MERGE (c:YTChannel {name: 'Neo4j'})
MERGE (x:OS {name: 'Linux'})
MERGE (l: Person {name: 'Bob', country: 'Canada'})

MERGE (f)-[:OWNED]->(c)
MERGE (f)-[:USES]->(x)
MERGE (l)-[:CREATED]->(x)
""")

SCHEMA = """Node Labels:
    Person(name, country)
    YTChannel(name)
    OS(name)
    Relationships:
        (person)-[:OWNED]->(YTChannel)
        (person)-[:USES]->(OS)
        (person)-[:CREATED]->(OS)
    """

retriever = Text2CypherRetriever(
    driver=driver,
    llm = OpenAILLM(model_name="gpt-4"),
    neo4j_schema = SCHEMA
)

@tool
def cypher_kg(question: str) -> str:
    """query the knowledge graph for information. you can pass entire user question / queries. result graph rows"""
    result = retriever.search(question)
    return '\n'.join(item.constants for item in result) or '(No Content Found)'

agent = create_agent(
    model="gpt-4o-mini",
    tools=[cypher_kg],
    system_prompt='You are a helpful assistant with access to knowledge graph data.  query it whenever you need to.'
    )

if __name__ == "__main__":
    q = "Who owns the Neo4j channel?"

    response = agent.invoke({"messages": q})
