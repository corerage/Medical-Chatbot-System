from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from src.config import OPENAI_API_KEY, PINECONE_API_KEY
from src.helper import get_embeddings
from src.logger import setup_logger
from src.prompt import sys_prompt

logger = setup_logger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (like style.css)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use templates
templates = Jinja2Templates(directory="templates")


embeddings = get_embeddings()
index_name = "nne-medical-chatbot-system"
search = PineconeVectorStore.from_existing_index(
    index_name=index_name, embedding=embeddings
)

doc_retriever = search.as_retriever(search_type="similarity", search_kwargs={"k": 3})
llm_model = ChatOpenAI(model_name="gpt-4o")

prompt = ChatPromptTemplate.from_messages(
    [("system", sys_prompt), ("human", "{input}")]
)

query_answer_chain = create_stuff_documents_chain(llm=llm_model, prompt=prompt)
retrieval_chain = create_retrieval_chain(
    retriever=doc_retriever, combine_docs_chain=query_answer_chain
)


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})


@app.api_route("/chat", methods=["POST", "GET"])
async def chat_endpoint(payload: dict):
    message = payload.get("message", "")
    input = message
    logger.info(input)
    response = retrieval_chain.invoke({"input": message})
    rag_response = response["answer"]
    logger.info(f"RAG Response: {rag_response}")
    return JSONResponse(content={"reply": rag_response})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
