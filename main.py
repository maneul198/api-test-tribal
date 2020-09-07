from typing import List
from fastapi import FastAPI
from clients.Clients import ClientProvider
from schemas import Query, SearchResults
import uvicorn

app = FastAPI()


@app.post("/search", response_model=List[SearchResults])
def search(query: Query):
    search_provider = ClientProvider.get_instance()
    return search_provider.launch_query(query)


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
