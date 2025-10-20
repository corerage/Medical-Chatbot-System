from pinecone import Pinecone

# import warnings
from pinecone import ServerlessSpec

# import json
# import boto3
# from langchain.schema import Document
# from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

from src import PINECONE_API_KEY
from src.helper import load_doc_from_s3, get_embeddings, process_relevant_doc

# from langchain.schema import Document
# from langchain_huggingface import HuggingFaceEmbeddings
from src.logger import setup_logger

logger = setup_logger(__name__)

# try:
#     from langchain_core._api.deprecation import LangChainDeprecationWarning

#     warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
# except ImportError:
#     pass

# warnings.filterwarnings("ignore", message=".*pydantic.*", category=DeprecationWarning)
# warnings.filterwarnings(
#     "ignore",
#     message=".*The 'langchain_pinecone' module is deprecated.*",
#     category=DeprecationWarning,
# )

# load_dotenv()
# s3 = boto3.client("s3")
# Bucket = S3_BUCKET_NAME
# Key = "doc/processed_document.json"


# def get_object_from_s3(Bucket, s3_key):
#     try:
#         response = s3.get_object(Bucket=Bucket, Key=s3_key)
#         pdf_bytes = response["Body"].read().decode("utf-8")
#         data = json.loads(pdf_bytes)

#         return data

#     except Exception as e:
#         logger.error(f"Error downloading {s3_key} from s3 bucket {Bucket}: {e}")
#         return None


# def load_doc_from_s3():
#     document_chunks = get_object_from_s3(Bucket, Key)

#     if not document_chunks:
#         return []

#     document = [
#         Document(
#             page_content=doc["page_content"],
#             metadata={**doc["metadata"], "source": "Medical-books.pdf"},
#         )
#         for doc in document_chunks
#     ]
#     return document


# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "nne-medical-chatbot-system"


# Check if the index exists before creating it
def create_pinecone_index(index_name, pc, dimension=384):
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=384,  # same as your embedding model dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info(f" Index '{index_name}' created successfully!")
    else:
        logger.info(f"  Index '{index_name}' already exists.")


# def get_embeddings():
#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )
#     return embeddings


# embeddings = get_embeddings()

# vectorstore = PineconeVectorStore.from_documents(
#     documents=document_chunks, embedding=embeddings, index_name=index_name
# )

# doc_retriever = vectorstore.as_retriever(
#     search_type="similarity", search_kwargs={"k": 3}
# )


def main():
    try:
        document_chunks = load_doc_from_s3()
        document_chunks = process_relevant_doc(document_chunks)
        logger.info(document_chunks[:1])
        create_pinecone_index(index_name, pc, dimension=384)
        pc.Index(index_name)
        logger.info(f"Pinecone index '{index_name}' created successfully.")
        embeddings = get_embeddings()
        PineconeVectorStore.from_documents(
            documents=document_chunks, embedding=embeddings, index_name=index_name
        )
        logger.info("pinecone vectostore created successfully.")

        logger.info(
            f"sucessfully loaded {len(document_chunks)} document chunks into pinecone index."
        )
    except Exception as e:
        logger.error(
            f"Error loading document chunks into pinecone index : {e}", exc_info=True
        )


if __name__ == "__main__":
    try:
        main()
        logger.info("Document chunks loaded successfully into pinecone index.")
    except Exception as e:
        logger.error(
            f"Error loading document chunks into pinecone index : {e}", exc_info=True
        )
