import os
from typing import Annotated
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from src.simulation.chat import llm

from ..models.models import Product, Inventory
from ..index import db as app_db

load_dotenv()

# SQLDatabase and toolkit
sql_db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))
toolkit = SQLDatabaseToolkit(db=sql_db, llm=llm)
tools = toolkit.get_tools()

