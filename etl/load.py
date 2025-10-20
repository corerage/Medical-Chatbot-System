from io import BytesIO
import os
import tempfile
import json
import boto3
import requests
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
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
    temp_path = None
    try:
        logger.info("Extracting PDF file from URL....")
        response = requests.get(URL, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()

        # Validate response
        content_type = response.headers.get("Content-Type", "").lower()
        file_size = len(response.content)
        logger.info(f"Response Content-Type: {content_type}")
        # logger.info(f"File size: {file_size} bytes")

        if not file_size:
            raise ValueError("Downloaded file is empty.")

        # Check if it's a PDF by examining the file header (magic bytes)
        # PDF files start with %PDF
        if not response.content.startswith(b"%PDF"):
            raise ValueError("URL did not return a valid PDF file.")

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(response.content)
            temp.flush()
            temp_path = temp.name

        # Check if file was written correctly
        if os.path.getsize(temp_path) == 0:
            raise ValueError("Temporary file is empty after writing.")

        # Load using LangChain
        py_loader = PyPDFLoader(temp_path)
        docs = py_loader.load()

        # Update metadata
        file_name = URL.split("/")[-1] or "medical_book.pdf"
        for d in docs:
            d.metadata["source"] = file_name

        # Return BytesIO for S3 upload
        content = BytesIO(response.content)

        logger.info("PDF file extracted successfully.")
        return content, docs

    except Exception as e:
        logger.error(f"Error extracting the PDF file: {e}")
        raise

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            # logger.info(f"Temporary file {temp_path} removed.")


#


def inject_data_to_s3(Bucket, s3_key, file_obj, file_type, json_data=None):
    data = None
    try:
        s3 = boto3.client("s3")
        logger.info("Uploading file to S3...")
        # logger.info(f"Bucket: {Bucket}")
        # logger.info(f"Key: {s3_key}")

        if file_type == "application/pdf":
            logger.info("File is a valid PDF.")

            # Reset file pointer to beginning
            file_obj.seek(0)
            file_size = file_obj.getbuffer().nbytes
            logger.info(
                f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)"
            )

            # Upload the actual file object, not the file_type string!
            data = s3.put_object(
                Bucket=Bucket,
                Key=s3_key,
                Body=file_obj,  # ← Changed from file_type to file_obj
                ContentType="application/pdf",
            )

        elif file_type == "application/json" and json_data is not None:
            logger.info("File is a valid JSON")

            if isinstance(json_data, list) and all(
                isinstance(doc, Document) for doc in json_data
            ):
                json_data = [
                    {"page_content": doc.page_content, "metadata": doc.metadata}
                    for doc in json_data
                ]

            json_str = json.dumps(json_data)
            logger.info(f"Sample data: {json_data[0]}")
            logger.info(f"JSON size: {len(json_str)} bytes")

            data = s3.put_object(
                Bucket=Bucket,
                Key=s3_key,
                Body=json_str,
                ContentType="application/json",
            )

        if data and data["ResponseMetadata"]["HTTPStatusCode"] == 200:
            # logger.info("File uploaded successfully to S3!")
            return True
        else:
            logger.error("Upload failed - no valid response")
            return False

    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    try:
        logger.info("data extraction process started....")
        pdf_file, docs = get_pdf_file(URL)

        for c, doc in enumerate(docs[:2], start=1):
            logger.info(f"\n --- SAMPLE PAGE {c} ---")
            logger.info(f"Metadata: {doc.metadata}")
            logger.info(f"Content: {doc.page_content[:500]}...")

        logger.info("Starting S3 upload...")
        # Pass pdf_file as the file_obj parameter
        success = inject_data_to_s3(
            Bucket=Bucket,
            s3_key=s3_key,
            file_obj=pdf_file,  # ← Add this parameter
            file_type="application/pdf",
        )

        if success:
            logger.info(f"File uploaded successfully to S3 bucket {Bucket}")
            logger.info("Data extraction process completed....")
        else:
            logger.error("S3 upload returned False - upload failed")

    except Exception as e:
        logger.error(f"Data extraction process failed: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
