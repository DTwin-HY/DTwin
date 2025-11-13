from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def create_mcp_agent():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent(model="openai:gpt-4.1", tools=tools)
    return agent


async def main():
    agent = await create_mcp_agent()
    payload = {"messages": [{"role": "user", "content": "what is the weather like in helsinki?"}]}
    result = await agent.ainvoke(payload)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())