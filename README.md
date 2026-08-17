# 🛍️ SmartShop AI

SmartShop AI is a **beginner-friendly Generative AI learning project** that demonstrates how to build a **multi-agent e-commerce shopping assistant** using Python, LangChain, LangGraph, OpenAI, Pandas, and Streamlit.

The project is designed for students who are learning:

* Python project structure
* AI agents
* Multi-agent systems
* LangChain
* LangGraph
* LLMs
* CSV data retrieval
* Streamlit
* `uv` package management
* Environment variables
* Basic debugging

The goal is to understand the complete flow:

```text
Customer Question
        ↓
   Streamlit UI
        ↓
 SmartShop Service
        ↓
      Router
        ↓
 ┌──────┼──────┬───────┐
 ↓      ↓      ↓       ↓
Product Price Review   FAQ
Agent   Agent  Agent   Agent
 ↓      ↓      ↓       ↓
products.csv  reviews.csv
       store_policies.csv
        ↓
  Combine Results
        ↓
   Final Response
        ↓
     Customer
```

---

# 1. Project Goal

Imagine a customer visits an online shopping website and asks:

> I need wireless headphones under $150 with good customer reviews.

A normal application may require the customer to search products, compare prices, and read reviews separately.

SmartShop AI uses specialized AI agents to help with these tasks.

The system can identify that this question requires:

```text
Product Agent
Price Agent
Review Agent
```

Each agent has a specific responsibility.

The results are then combined and displayed to the customer.

---

# 2. What Is a Multi-Agent System?

An **agent** is a component that performs a specific task.

Instead of asking one AI component to do everything, SmartShop AI separates responsibilities among multiple agents.

Our system currently contains four specialized agents.

| Agent         | Responsibility                 | Data                 |
| ------------- | ------------------------------ | -------------------- |
| Product Agent | Finds and recommends products  | `products.csv`       |
| Price Agent   | Compares product prices        | `products.csv`       |
| Review Agent  | Analyzes customer reviews      | `reviews.csv`        |
| FAQ Agent     | Answers store-policy questions | `store_policies.csv` |

There is also a **Router**.

The Router acts like a supervisor and decides which agent or agents should handle the customer's question.

---

# 3. Example

Customer asks:

```text
iphone under 100
```

The router examines the question.

It may select:

```text
Product Agent
Price Agent
```

The Product Agent searches the product dataset.

The Price Agent looks for products matching the customer's budget.

The results are combined and returned to the Streamlit UI.

Another example:

```text
What do customers think about this iPhone?
```

This can activate:

```text
Review Agent
```

Another example:

```text
Can I return a laptop after 20 days?
```

This activates:

```text
FAQ Agent
```

---

# 4. Technology Stack

SmartShop AI currently uses:

| Technology         | Purpose                                      |
| ------------------ | -------------------------------------------- |
| Python             | Main programming language                    |
| uv                 | Python dependency and environment management |
| Pandas             | Reading and filtering CSV data               |
| Streamlit          | Chatbot frontend                             |
| LangChain          | LLM integration                              |
| LangGraph          | Multi-agent workflow orchestration           |
| OpenAI             | Large Language Model                         |
| `langchain-openai` | LangChain integration for OpenAI             |
| `python-dotenv`    | Loading environment variables                |

---

# 5. Project Structure

The current recommended project structure is:

```text
Smart_AI/
│
├── app/
│   │
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── product_agent.py
│   │   ├── price_agent.py
│   │   ├── review_agent.py
│   │   └── faq_agent.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── smartshop_service.py
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   └── smartshop_state.py
│   │
│   ├── data_loader.py
│   └── config.py
│
├── data/
│   ├── products.csv
│   ├── reviews.csv
│   └── store_policies.csv
│
├── frontend/
│   └── frontend.py
│
├── tests/
│   ├── test_agents.py
│   └── test_router.py
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 6. Understanding Each Folder

## `app/`

This contains the main backend application code.

Do not put Streamlit UI code here.

---

## `app/agents/`

Contains all AI agents.

```text
agents/
├── router.py
├── product_agent.py
├── price_agent.py
├── review_agent.py
└── faq_agent.py
```

Each agent should have one clear responsibility.

---

## `app/services/`

Contains the workflow orchestration.

The important file is:

```text
app/services/smartshop_service.py
```

This connects:

```text
LangGraph
    ↓
Router
    ↓
Agents
    ↓
Final Answer
```

---

## `app/state/`

Contains the shared LangGraph state.

```text
app/state/smartshop_state.py
```

LangGraph passes this state between nodes.

For example:

```python
from typing import TypedDict


class SmartShopState(TypedDict, total=False):
    query: str
    selected_agents: list[str]

    product_response: str
    price_response: str
    review_response: str
    faq_response: str

    final_answer: str
```

Think of state as a shared dictionary traveling through the workflow.

For example:

```python
{
    "query": "iphone under 100",
    "selected_agents": [
        "product_agent",
        "price_agent"
    ]
}
```

---

# 7. Important Import Rule

Because `SmartShopState` is located here:

```text
app/state/smartshop_state.py
```

the correct import is:

```python
from app.state.smartshop_state import SmartShopState
```

Do not use:

```python
from app.state import SmartShopState
```

unless `SmartShopState` is explicitly exported from:

```text
app/state/__init__.py
```

For beginners, using the full explicit import is easier to understand.

---

# 8. Avoid Circular Imports

A circular import happens when two Python files import each other.

For example:

```text
smartshop_service.py
        ↓
   faq_agent.py
        ↓
smartshop_service.py
```

This can produce an error such as:

```text
ImportError: cannot import name 'SmartShopState'
from partially initialized module
```

Do not define `SmartShopState` inside `smartshop_service.py`.

Keep it in:

```text
app/state/smartshop_state.py
```

Then both files can safely import it:

```python
from app.state.smartshop_state import SmartShopState
```

The dependency direction should be:

```text
frontend.py
      ↓
smartshop_service.py
      ↓
router + agents
      ↓
state + data
```

---

# 9. Dataset

SmartShop AI currently uses three CSV files.

## `products.csv`

Contains product information.

Example:

```csv
product_id,name,brand,category,price
P001,iPhone 12,Apple,Smartphone,299
P002,Galaxy S21,Samsung,Smartphone,249
P003,Sony WH-CH720N,Sony,Headphones,129
```

Used by:

```text
Product Agent
Price Agent
```

---

## `reviews.csv`

Contains customer reviews.

Example:

```csv
review_id,product_id,rating,review
R001,P001,5,Excellent phone
R002,P001,4,Good battery life
R003,P002,4,Great display
```

Used by:

```text
Review Agent
```

---

## `store_policies.csv`

Contains store policies.

Example:

```csv
policy_type,description,conditions,timeframe
Return Policy,Products can be returned,Product must be eligible,30 days
Refund Policy,Refund after approval,Original payment method,5-7 business days
Shipping Policy,Standard shipping,US orders,3-5 business days
```

Used by:

```text
FAQ Agent
```

---

# 10. Data Loader

Instead of writing CSV-loading code repeatedly inside every agent, we use:

```text
app/data_loader.py
```

Example:

```python
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_products():
    return pd.read_csv(DATA_DIR / "products.csv")


def load_reviews():
    return pd.read_csv(DATA_DIR / "reviews.csv")


def load_store_policies():
    return pd.read_csv(DATA_DIR / "store_policies.csv")
```

This is better than:

```python
pd.read_csv("data/products.csv")
```

because relative paths can break depending on where the program is started.

With our project structure:

```python
Path(__file__).resolve()
```

starts from:

```text
Smart_AI/app/data_loader.py
```

Then:

```python
.parent.parent
```

takes us to:

```text
Smart_AI/
```

Finally:

```python
DATA_DIR = PROJECT_ROOT / "data"
```

points to:

```text
Smart_AI/data/
```

---

# 11. Router

File:

```text
app/agents/router.py
```

The Router decides which agent should handle the question.

The first version uses simple keyword matching.

Example product keywords:

```text
find
recommend
looking
need
product
iphone
phone
```

Price keywords:

```text
price
compare
cheaper
cost
under
budget
```

Review keywords:

```text
review
reviews
customer
rating
feedback
```

FAQ keywords:

```text
return
refund
shipping
policy
exchange
warranty
```

For example:

```text
Recommend headphones under $150 with good reviews
```

could activate:

```text
Product Agent
Price Agent
Review Agent
```

Keyword routing is intentionally simple because this project is designed for learning.

Later it can be replaced with an LLM-based supervisor.

---

# 12. Product Agent

File:

```text
app/agents/product_agent.py
```

Responsibilities:

* Read product information
* Find products matching the customer's request
* Recommend relevant products
* Avoid inventing products that are not in the dataset

Data source:

```text
products.csv
```

---

# 13. Price Agent

File:

```text
app/agents/price_agent.py
```

Responsibilities:

* Read product prices
* Compare prices
* Find products within a customer's budget
* Identify cheaper alternatives

Data source:

```text
products.csv
```

Example:

```text
iphone under 100
```

The Price Agent should search the dataset for products matching the customer's budget.

If no product exists under `$100`, the system should clearly tell the customer rather than inventing one.

---

# 14. Review Agent

File:

```text
app/agents/review_agent.py
```

Responsibilities:

* Read customer reviews
* Summarize customer feedback
* Identify common positive comments
* Identify common negative comments
* Use ratings when available

Data source:

```text
reviews.csv
```

---

# 15. FAQ Agent

File:

```text
app/agents/faq_agent.py
```

Responsibilities:

* Answer return questions
* Answer refund questions
* Answer warranty questions
* Answer shipping questions
* Answer exchange questions

Data source:

```text
store_policies.csv
```

The agent should use the dataset rather than inventing company policies.

---

# 16. SmartShop Service

File:

```text
app/services/smartshop_service.py
```

This is the main orchestration layer.

The frontend should not directly call every agent.

Instead:

```text
frontend.py
      ↓
answer_customer_query()
      ↓
LangGraph
      ↓
Router
      ↓
Agents
      ↓
Combine Results
```

The public function should look similar to:

```python
def answer_customer_query(query: str):

    result = smartshop_graph.invoke(
        {
            "query": query
        }
    )

    return result
```

Notice this important line:

```python
{"query": query}
```

The key must match the state definition:

```python
query: str
```

If one part uses:

```python
state["query"]
```

but another sends:

```python
{"message": query}
```

Python can raise:

```text
KeyError: 'query'
```

Keep state names consistent throughout the application.

---

# 17. LangGraph

LangGraph controls the workflow between components.

Conceptually:

```text
START
  ↓
Router
  ↓
Agent Dispatcher
  ↓
Selected Agents
  ↓
Combine Responses
  ↓
END
```

A simplified graph can look like:

```python
from langgraph.graph import END, START, StateGraph

from app.state.smartshop_state import SmartShopState


workflow = StateGraph(SmartShopState)

workflow.add_node("router", route_query)
workflow.add_node("agents", dispatch_agents)
workflow.add_node("combine", combine_responses)

workflow.add_edge(START, "router")
workflow.add_edge("router", "agents")
workflow.add_edge("agents", "combine")
workflow.add_edge("combine", END)

smartshop_graph = workflow.compile()
```

---

# 18. Streamlit Frontend

File:

```text
frontend/frontend.py
```

The frontend should only be responsible for:

* Displaying the chatbot
* Getting the customer's question
* Calling the SmartShop service
* Displaying the response

It should not contain product-search or routing logic.

Import the backend service with:

```python
from app.services.smartshop_service import answer_customer_query
```

Then:

```python
query = st.chat_input(
    "Ask about products, prices, reviews, or store policies..."
)
```

and:

```python
result = answer_customer_query(query)
```

---

# 19. Install `uv`

Check whether `uv` is already installed:

```bash
uv --version
```

If you are on macOS and already installed `uv` using Homebrew, you do not need to install it again.

One installation option is:

```bash
brew install uv
```

See the official `uv` documentation for other supported installation methods.

---

# 20. Install Project Dependencies

Go to the project root:

```bash
cd /Users/swatisalunkke/Smart_AI
```

Then run:

```bash
uv sync
```

To add a new dependency:

```bash
uv add package-name
```

For example:

```bash
uv add streamlit
uv add pandas
uv add langchain
uv add langgraph
uv add langchain-openai
uv add python-dotenv
```

You normally should not need to manually activate `.venv` when using:

```bash
uv run
```

---

# 21. Environment Variables

Create:

```text
.env
```

in the project root:

```text
Smart_AI/.env
```

Add:

```text
OPENAI_API_KEY=your_openai_api_key
```

Never upload your real API key to GitHub.

Add `.env` to `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
.DS_Store
```

---

# 22. VS Code Setup

Open the **entire project folder** in VS Code:

```text
Smart_AI/
```

Do not open only:

```text
frontend/
```

Select the correct Python interpreter:

```text
Cmd + Shift + P
```

Select:

```text
Python: Select Interpreter
```

Then choose:

```text
Smart_AI/.venv/bin/python
```

You can verify it in the terminal:

```bash
which python
```

---

# 23. Running the Application

Always start from the project root:

```bash
cd /Users/swatisalunkke/Smart_AI
```

Then:

```bash
uv run streamlit run frontend/frontend.py
```

Streamlit should display something similar to:

```text
Local URL: http://localhost:8501
```

Open that URL in your browser.

---

# 24. Test Components Separately

When debugging, do not immediately run the entire application.

Test individual components first.

## Test Python

```bash
uv run python --version
```

## Test `app` import

```bash
uv run python -c "import app; print('app works')"
```

Expected:

```text
app works
```

## Test State

```bash
uv run python -c "from app.state.smartshop_state import SmartShopState; print(SmartShopState)"
```

## Test Product CSV

```bash
uv run python -c "from app.data_loader import load_products; print(load_products().head())"
```

## Test Reviews

```bash
uv run python -c "from app.data_loader import load_reviews; print(load_reviews().head())"
```

## Test Policies

```bash
uv run python -c "from app.data_loader import load_store_policies; print(load_store_policies().head())"
```

Only after these tests work should you run Streamlit.

---

# 25. Common Errors We Learned From

## Error 1 — `ModuleNotFoundError: No module named 'app'`

Example:

```text
ModuleNotFoundError: No module named 'app'
```

Make sure you run Streamlit from:

```text
Smart_AI/
```

using:

```bash
uv run streamlit run frontend/frontend.py
```

Also make sure:

```text
app/__init__.py
```

exists.

---

## Error 2 — Cannot Import `SmartShopState`

Example:

```text
ImportError: cannot import name 'SmartShopState'
from 'app.state'
```

Our state is located at:

```text
app/state/smartshop_state.py
```

Therefore use:

```python
from app.state.smartshop_state import SmartShopState
```

---

## Error 3 — Circular Import

Example:

```text
ImportError: cannot import name 'SmartShopState'
from partially initialized module
```

Do not do this inside agents:

```python
from app.services.smartshop_service import SmartShopState
```

Instead:

```python
from app.state.smartshop_state import SmartShopState
```

---

## Error 4 — `KeyError: 'query'`

Example:

```text
Something went wrong: 'query'
```

If your agent reads:

```python
query = state["query"]
```

then LangGraph must be invoked with:

```python
smartshop_graph.invoke(
    {
        "query": query
    }
)
```

Use the same state key everywhere.

---

## Error 5 — CSV File Not Found

Example:

```text
No such file or directory:
/Users/.../data/products.csv
```

Use `Path` to calculate the project root:

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
```

Then:

```python
pd.read_csv(DATA_DIR / "products.csv")
```

Also verify the actual filename.

For example:

```text
product.csv
```

and:

```text
products.csv
```

are different filenames.

Run:

```bash
ls data
```

to see the real names.

---

# 26. Debugging with `print()`

For a learning project, `print()` is a very useful debugging tool.

Inside the service:

```python
print("INPUT QUERY:", query)
```

Inside the router:

```python
print("ROUTER STATE:", state)
```

Inside the Product Agent:

```python
print("PRODUCT AGENT:", state)
```

You can then watch the VS Code terminal while using Streamlit.

For:

```text
iphone under 100
```

you might see:

```text
INPUT QUERY: iphone under 100

ROUTER STATE:
{'query': 'iphone under 100'}

SELECTED AGENTS:
['product_agent', 'price_agent']
```

This helps you understand exactly how data moves through the system.

---

# 27. Beginner Development Strategy

Do not try to build everything at once.

Follow these stages.

## Version 1 — Static Agents

```text
Customer
   ↓
Router
   ↓
Hardcoded Agent Response
```

Goal:

Learn routing and application structure.

---

## Version 2 — CSV Agents

```text
Customer
   ↓
Router
   ↓
Agent
   ↓
CSV / Pandas
   ↓
Response
```

Goal:

Learn data retrieval.

This is the current direction of SmartShop AI.

---

## Version 3 — LLM + CSV

```text
Customer
   ↓
Router
   ↓
Retrieve Relevant CSV Records
   ↓
LLM
   ↓
Natural Language Response
```

Goal:

Learn how retrieval and LLM generation work together.

---

## Version 4 — LangGraph Multi-Agent System

```text
                 ┌→ Product Agent
                 │
Customer → Supervisor → Price Agent
                 │
                 ├→ Review Agent
                 │
                 └→ FAQ Agent
                         ↓
                  Response Synthesizer
                         ↓
                      Customer
```

Goal:

Learn agent orchestration.

---

## Version 5 — Production-Style Architecture

Eventually the CSV files can be replaced with databases.

For example:

```text
Customer
   ↓
Streamlit / Web UI
   ↓
FastAPI
   ↓
LangGraph Supervisor
   │
   ├── Product Agent → PostgreSQL
   │
   ├── Price Agent → PostgreSQL
   │
   ├── Review Agent → PGVector
   │
   └── FAQ Agent → Vector Search
   │
   ↓
LLM Response
```

Additional tools could then include:

```text
PostgreSQL
PGVector
FastAPI
Docker
LangSmith
MLflow
Cloud deployment
```

Do not add these until the basic version works.

---

# 28. Why Not Send the Entire CSV to the LLM?

For a tiny learning dataset, this may work:

```python
products = load_products()

prompt = f"""
Customer: {query}

Products:
{products.to_csv(index=False)}
"""
```

However, this does not scale well.

A better design is:

```text
1000 Products
      ↓
Pandas Filtering
      ↓
10 Relevant Products
      ↓
LLM
      ↓
Final Recommendation
```

The database/Pandas layer should retrieve relevant records.

The LLM should focus on reasoning and generating a useful response.

---

# 29. Testing Questions

Try these questions in the Streamlit chatbot.

### Product

```text
Recommend an iPhone
```

### Price

```text
iphone under 100
```

### Product + Price

```text
Recommend headphones under $150
```

### Reviews

```text
What do customers think about the Sony headphones?
```

### Product + Price + Reviews

```text
Recommend wireless headphones under $150 with good reviews
```

### FAQ

```text
What is the return policy?
```

### Warranty

```text
What is the laptop warranty?
```

The exact results depend on the products, reviews, and policies available in your CSV files.

---

# 30. Current Limitations

SmartShop AI is currently a learning prototype.

Current limitations include:

* CSV-based local data
* Simple keyword routing
* Limited product matching
* No authentication
* No production database
* No vector database
* No persistent chat history
* Limited error handling
* No production deployment
* No API layer yet

These limitations are intentional while learning the core concepts.

---

# 31. Next Steps

Recommended development order:

1. Make sure all three CSV files load correctly.
2. Make Product Agent retrieve real products.
3. Make Price Agent filter by price.
4. Make Review Agent retrieve relevant reviews.
5. Make FAQ Agent search store policies.
6. Test each agent individually.
7. Test router selection.
8. Combine agent responses.
9. Improve prompts.
10. Replace keyword routing with an LLM supervisor.
11. Add LangSmith tracing.
12. Add FastAPI.
13. Add PostgreSQL/PGVector.
14. Add automated tests.
15. Add Docker.
16. Deploy the application.

---

# 32. Important Learning Principle

Keep the responsibilities separated.

```text
Streamlit
    ↓
UI only

Service
    ↓
Workflow orchestration

Router
    ↓
Decides which agent runs

Agents
    ↓
Perform specialized tasks

Data Loader
    ↓
Loads datasets

CSV / Database
    ↓
Stores information

LangGraph State
    ↓
Shares information between nodes

LLM
    ↓
Reasoning + natural language generation
```

This separation makes the project easier to understand, debug, test, and extend.

---

# 33. Useful Commands

Synchronize dependencies:

```bash
uv sync
```

Add a package:

```bash
uv add package-name
```

Check Python:

```bash
uv run python --version
```

Check installed packages:

```bash
uv pip list
```

List datasets:

```bash
ls data
```

Test product loading:

```bash
uv run python -c "from app.data_loader import load_products; print(load_products().head())"
```

Run Streamlit:

```bash
uv run streamlit run frontend/frontend.py
```

Stop Streamlit:

```text
Ctrl + C
```

---

# 34. Useful Resources

* uv documentation: https://docs.astral.sh/uv/
* Streamlit documentation: https://docs.streamlit.io/
* LangChain documentation: https://docs.langchain.com/
* LangGraph documentation: https://docs.langchain.com/oss/python/langgraph/overview
* OpenAI documentation: https://platform.openai.com/docs
* Pandas documentation: https://pandas.pydata.org/docs/

---

# 35. Learning Outcome

After completing SmartShop AI, a student should understand how to:

* Structure a Python AI application
* Manage dependencies using `uv`
* Build a Streamlit chatbot
* Read CSV datasets using Pandas
* Create specialized AI agents
* Route customer queries to appropriate agents
* Share data using LangGraph state
* Build a LangGraph workflow
* Connect LangChain to an LLM
* Separate frontend, orchestration, agents, and data
* Debug Python import errors
* Debug file-path errors
* Debug LangGraph state errors
* Avoid circular imports
* Progress from a simple prototype toward a production-style GenAI application

The purpose of this project is not only to build a shopping chatbot.

The bigger goal is to learn the architecture and engineering concepts behind **multi-agent Generative AI applications**.
# SmartShop-AI
