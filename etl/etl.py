import os
import tempfile
import typing

import boto3
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from src.config import (
    S3_BUCKET_NAME,
)
from src.logger import setup_logger

from etl.load import inject_data_to_s3

logger = setup_logger(__name__)

s3 = boto3.client("s3")


def get_object_from_s3(Bucket, s3_key):
    try:
        response = s3.get_object(Bucket=Bucket, Key=s3_key)
        pdf_bytes = response["Body"].read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_bytes)
            temp_file_path = temp_file.name
        logger.info(f"Temporary file created at {temp_file_path}")
        loader = PyPDFLoader(temp_file_path)
        document = loader.load()

    except Exception as e:
        logger.error(f"Error downloading {s3_key} from s3 bucket {Bucket}: {e}")
        return None

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Temporary {temp_file_path} removed")

    return document


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


def split_docs(clean_pdf):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
    )
    split_documents = text_splitter.split_documents(clean_pdf)
    return split_documents


def main():
    try:
        logger.info("Starting ETL process...")
        Bucket = S3_BUCKET_NAME
        s3_key = "data/medical_book.pdf"
        document = get_object_from_s3(Bucket, s3_key)
        if document is None:
            return logger.error("Failed to retrieve document from S3.")

        document_chunks = split_docs(document)
        logger.info(document_chunks[0])
        logger.info(f"Total document chunks after splitting: {len(document_chunks)}")

        relevant_docs = process_relevant_doc(document_chunks)
        logger.info(relevant_docs[0])

        logger.info(f"Total relevant documents processed: {len(relevant_docs)}")

        inject_data_to_s3(
            Bucket,
            s3_key="processed_document.json",
            file_type="application/json",
            json_data=relevant_docs,
        )
        logger.info("ETL process completed successfully...")
    except Exception as e:
        logger.error(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
