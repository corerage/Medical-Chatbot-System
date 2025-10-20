# from pinecone import Pinecone
# import warnings
# from pinecone import ServerlessSpec
import json
import boto3
from langchain.schema import Document
from dotenv import load_dotenv
import typing
# from langchain_pinecone import PineconeVectorStore

from src import S3_BUCKET_NAME

# from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from src.logger import setup_logger

logger = setup_logger(__name__)


load_dotenv()
s3 = boto3.client("s3")
Bucket = S3_BUCKET_NAME
Key = "doc/processed_document.json"


def get_object_from_s3(Bucket, s3_key):
    try:
        response = s3.get_object(Bucket=Bucket, Key=s3_key)
        pdf_bytes = response["Body"].read().decode("utf-8")
        data = json.loads(pdf_bytes)

        return data

    except Exception as e:
        logger.error(f"Error downloading {s3_key} from s3 bucket {Bucket}: {e}")
        return None


def load_doc_from_s3():
    document_chunks = get_object_from_s3(Bucket, Key)

    if not document_chunks:
        return []

    document = [
        Document(
            page_content=doc["page_content"],
            metadata={**doc["metadata"], "source": "Medical-books.pdf"},
        )
        for doc in document_chunks
    ]
    return document


def get_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def process_relevant_doc(docs: list[Document]) -> typing.List[Document]:
    relevant_docs = []
    for doc in docs:
        doc.metadata.get("source")
        relevant_docs.append(
            Document(
                page_content=doc.page_content, metadata={"source": "medical_book.pdf"}
            )
        )

    return relevant_docs
