from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

from neo4j import GraphDatabase
from neo4j_graph.llm import OpenAILLM
from neo4j_graph.retriever import Text2CypherRetriever  

load_dotenv()

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
driver.execute_query(
"""MERGE (f:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'})"""
)