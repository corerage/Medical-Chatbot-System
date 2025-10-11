import boto3
from io import BytesIO
import requests

from src.config import (
    S3_BUCKET_NAME,
    URL,
    USER_AGENT,
)
from src.logger import setup_logger

logger = setup_logger(__name__)


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

Bucket = S3_BUCKET_NAME
s3_key = "data/medical_book.pdf"


def inject_data_to_s3(Bucket, s3_key, pdf_file):
    try:
        logger.info("Uploading file to S3...")
        s3 = boto3.client("s3")
        data = s3.put_object(
            Bucket=Bucket, Key=s3_key, Body=pdf_file, ContentType="application/pdf"
        )
        logger.info(f"Bucket: {Bucket}")
        if data["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.info("File uploaded successfully to S3...")
        return data
    except Exception as e:
        logger.error(f"Error uploading file to s3 {e}")


def main():
    logger.info("Data Ingestion process started....")
    pdf_file = get_pdf_file(URL)
    inject_data_to_s3(Bucket, s3_key, pdf_file)
    logger.info("Data Ingestion process completed....")


if __name__ == "__main__":
    main()
