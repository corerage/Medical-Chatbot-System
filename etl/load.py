from io import BytesIO
import json
import boto3
import requests
from langchain.schema import Document
from src.config import (
    S3_BUCKET_NAME,
    URL,
    USER_AGENT,
)
from src.logger import setup_logger

logger = setup_logger(__name__)

Bucket = S3_BUCKET_NAME
s3_key = "data/medical_book.pdf"


def get_pdf_file(URL):
    try:
        logger.info("ingesting pdf file from url....")
        response = requests.get(URL, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()  # Check if the request was successful

        if response.status_code == 200:
            content = BytesIO(response.content)
            logger.info("PDF file ingested successfully....")
            logger.info(f"File size: {len(response.content)} bytes")
            return content
    except Exception as e:
        logger.error(f"Error Downloading the PDF file: {e}")


#


def inject_data_to_s3(Bucket, s3_key, file_type, json_data=None):
    data = None
    try:
        s3 = boto3.client("s3")
        logger.info("Uploading file to S3...")
        if file_type == "application/pdf":
            logger.info("File is a valid PDF.")

            data = s3.put_object(
                Bucket=Bucket, Key=s3_key, Body=file_type, ContentType="application/pdf"
            )
        elif file_type == "application/json" and json_data is not None:
            logger.info("file is a valid Json")
            if isinstance(json_data, list) and all(
                isinstance(doc, Document) for doc in json_data
            ):
                json_data = [
                    {"page_content": doc.page_content, "metadata": doc.metadata}
                    for doc in json_data
                ]
            json_str = json.dumps(json_data)
            logger.info(json_data[0])
            data = s3.put_object(
                Bucket=Bucket,
                Key=s3_key,
                Body=json_str,
                ContentType="application/json",
            )

        logger.info(f"Bucket: {Bucket}")
        if data and data["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.info("File uploaded successfully to S3...")
        return data
    except Exception as e:
        logger.error(f"Error uploading file to s3 {e}")


def main():
    try:
        logger.info("Data Ingestion process started....")
        pdf_file = get_pdf_file(URL)
        data = inject_data_to_s3(Bucket, s3_key, pdf_file)
        if data:
            logger.info(f"File uploaded successfully to S3 bucket {Bucket}")
    except Exception as e:
        logger.info(f"Data Ingestion process failed {e}....")


if __name__ == "__main__":
    main()
