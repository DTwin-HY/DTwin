# Features

DTwin consists of several standalone agents combined together in a graph structure. Separating the agents to sub-categories and task specific work allows the agents to minimize the load on their context windows. A main agent is responsible for curating the work of the other agents, which in turn can call on their teams of agents or tools to answer questions. By limiting the scope a single model's work, we can expand the total information of the network.

Focusing the agent's attention on single problems allows the system prompts to be more specific, allowing the agent less space to hallucinate and generate false replies.

## Main Agents
The main agents are responsible for coordinating teams of other agents to respond to user queries. These agents use the tools given to them to base their reasoning and answers on specific data points.
### Supervisor Agent

The supervisor agent is the user’s first touch the graph structure. The supervisor is responsible for routing the user’s request to the correct agents to answer the prompt fully. The supervisor has connections to the main agents, i.e. the storage, sales and analytics agents. The supervisor can combine different agents in the network to generate robust answers to queries if needed.

### Sales Agent

The sales agent is responsible for generating sales reports and data collection on sales. The agent has several tools at its disposal, such as functions to generate static reports and graphs as well as a connection to the SQL Agent to generate custom reports.

### Storage Agent

The storage agent is responsible for generating reports on inventory, such as which items are running low or which are well-stocked. The storage agent relies on the SQL Agent to generate its reports.

### Analytics Agent

The analytics agent is responsible for generating analytics and simulations on the underlying data. The analytics agent has a tool for simple statistical analysis, the linear regression tool, and for what-if type analysis using the counterfactual agent.


## Auxiliary Agents and Graphs

There are several task-specific agents that are used by the main agents connected to the supervisor agent. These auxiliary agents or graphs are called tools and are used by the main agents to gather data to answer the user's queries.

Most tools use AI-capabilities in some form to do their functions, those named graph are purely functions linked together that do not use any AI to do their work.

### SQL Agent

The SQL agent can create SQL queries to a company’s database to answer natural language queries, such as “What was the most sold item in Q4?” or “What is the average revenue per sale for Q2?”. The SQL agent converts the natural language prompt to a syntactically correct query and returns the resulting dataset to the agent requesting it. Final modifications to make the response human readable are made by the agent prompting the tool.

### Dataframe Agent

The dataframe agent is used to collate tabular time series data for use in statistical analysis. The agent can call on the SQL agent to generate datasets from internal databases as well as the weather MCP server to gather any weather data of interest. The agent creates a .csv-file on disk which can then be read by any tool that requires time series data for its work.

### Linear Regression Graph

The linear regression graph is markedly different from the other agents in that it is a purely function based graph with no LLM-capabilities. The graph accepts an argument from an agent that contains a path to a time series dataset on disk as well as the variable of interest, the graph then computes a linear regression on that dataset and returns the result to the calling agent.

### Weather MCP

The weather model context protocol tool is used to connect to an outside weather API that allows the network to pull data on weather conditions, this data can be used in statistical analysis or what-if analysis to see if weather has any effect on company performance.

In reality, the weather aspect has little importance for many companies. The addition of an MCP to the agent network highlights the flexibility of the graph structure. 


### Counterfactual Agent
The counterfactual agent currently supports simple what-if type queries such as percentage increases or decreases or increasing or decreasing sales volume. Some example use cases would be “What if all pricers were 10% higher?” or “Simulate a scenario where we sold 2000 fewer units.”. 