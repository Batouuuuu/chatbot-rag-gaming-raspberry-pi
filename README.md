# RAG Chatbot – League of Legends

A chatbot that helps you explore the **League of Legends** universe.

## Legal notice
“This project uses external data from Riot Games (League of Legends) and the Mistral API. All rights of those data sources remain with their respective owners.”

## Features
- Get a detailed view of the **lore** of any champion.
- Quickly retrieve a **summary** of a champion’s backstory.
- *(Planned)* Display the **latest patch information**.
- *(Planned)* Provide **definitions of complex in-game terms**.

## API Key
This project uses the **Mistral 7B** model.  
You need to generate an API key here:  
[https://docs.mistral.ai/getting-started/quickstart/](https://docs.mistral.ai/getting-started/quickstart/)

**Never commit your API key to GitHub.**  
Put it in a `.env` file (added to `.gitignore`) and load it in your code with `os.getenv()`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
```

## Technical Pipeline 

- The user’s question is analyzed with **RapidFuzz** to identify any champion names (or other metadata).

- The documents are filtered by metadata (Name, Region, Source, etc.).

- **FAISS** performs a vector similarity search on the filtered chunks using **MiniLM-L12-v2 multilingual embeddings**.

- The retrieved chunks are concatenated into a single context block.

- The question + context are sent to the **Mistral 7B model** to generate the final answer.

## Installation
Clone the repo and install dependencies 

```bash
pip install -r requirements.txt
```
