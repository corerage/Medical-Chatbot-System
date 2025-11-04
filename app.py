from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
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
    allow_origins=["*"],
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
    [("system", sys_prompt), ("placeholder", "{chat_history}"), ("human", "{input}")]
)

query_answer_chain = create_stuff_documents_chain(llm=llm_model, prompt=prompt)
retrieval_chain = create_retrieval_chain(
    retriever=doc_retriever, combine_docs_chain=query_answer_chain
)

# chain_with_context = (
#     RunnablePassthrough.assign(chat_history=lambda x: x.get("chat_history", []))
#     | retrieval_chain
# )


store = {}


def get_session_memory(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


chain_with_memory = RunnableWithMessageHistory(
    retrieval_chain,
    get_session_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})


@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        payload = await request.json()
        message = payload.get("message", "").strip()

        if not message:
            return JSONResponse(
                content={"error": "Message cannot be empty"}, status_code=400
            )

        session_id = payload.get("session_id", "default_session")
        logger.info(f"Input: {message}")

        response = chain_with_memory.invoke(
            {
                "input": message,
            },
            config={"configurable": {"session_id": session_id}},
        )

        rag_response = response["answer"]
        logger.info(f"RAG Response: {rag_response}")

        return JSONResponse(content={"reply": rag_response})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


# if __name__ == "__main__":
#     import uvicorn

# uvicorn.run(app, host="0.0.0.0", port=8000)
