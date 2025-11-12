# Nne - AI-Powered Medical Chatbot System

Nne is an intelligent medical chatbot system that provides instant, reliable health information, symptom guidance, and personalized wellness support. Built with OpenAI's language models, LangChain, and FastAPI, it's designed for scalable deployment on AWS.

## Features

- Real-time health information and symptom guidance
- AI-powered conversational interface
- Scalable cloud deployment
- Secure credential management

## Tech Stack

- **Python** - Core programming language
- **LangChain** - LLM orchestration framework
- **FastAPI** - High-performance web framework
- **OpenAI GPT** - Large language model
- **Pinecone** - Vector database for embeddings
- **AWS** - Cloud infrastructure and CI/CD deployment

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- Conda package manager
- AWS account with IAM credentials
- OpenAI API key
- Pinecone API key
- Google Drive account (for data storage)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/corerage/Medical-Chatbot-System.git
cd Medical-Chatbot-System
```

### Step 2: Set Up Conda Environment

```bash
conda create -n medibot python=3.12 -y
conda activate medibot
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory with your credentials:

```env
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Setup & Data Processing

1. **Upload PDF Data**: Set up a Google Drive account and upload your extracted PDF data using the format: `https://drive.google.com/uc?export=download&id={file_id}`

2. **Configure Storage**: Create an S3 bucket on AWS or use an alternative cloud storage solution

3. **Load Data**: Execute the data loading script

   ```bash
   python load.py
   ```

4. **Transform Data**: Run the ETL pipeline

   ```bash
   python etl.py
   ```

5. **Store Embeddings**: Generate and store embeddings in Pinecone

   ```bash
   python store_index.py
   ```

6. **Start Application**: Launch the FastAPI server

   ```bash
   python app.py
   ```

7. **Access Application**: Open your browser and navigate to `http://localhost:8000`

## AWS Deployment

### Prerequisites

1. Login to AWS Console
2. Create an IAM user with the following policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonEC2FullAccess`

### Deployment Steps

1. **Create ECR Repository**

   ```bash
   # Save the ECR URI for later use
   # Example: 315865595366.dkr.ecr.us-east-1.amazonaws.com/medicalbot
   ```

2. **Launch EC2 Instance**

   - Create a new EC2 instance (Ubuntu)
   - Ensure security groups allow HTTP/HTTPS traffic

3. **Install Docker on EC2**

   ```bash
   sudo apt-get update -y
   sudo apt-get upgrade -y
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

4. **Configure Self-Hosted Runner**

   Navigate to: Settings → Actions → Runners → New Self-Hosted Runner
   - Select your OS
   - Follow the provided commands

5. **Set GitHub Secrets**

   Add the following secrets to your GitHub repository:

   | Secret | Value |
   |--------|-------|
   | `AWS_ACCESS_KEY_ID` | Your AWS access key |
   | `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
   | `AWS_DEFAULT_REGION` | Your preferred AWS region |
   | `ECR_REPO` | Your ECR repository URI |
   | `PINECONE_API_KEY` | Your Pinecone API key |
   | `OPENAI_API_KEY` | Your OpenAI API key |

### Deployment Flow

1. Build Docker image from source code
2. Push image to AWS ECR (Elastic Container Registry)
3. Pull image from ECR into EC2 instance
4. Launch Docker container on EC2

## CI/CD Pipeline

This project uses GitHub Actions for automated CI/CD deployment. The pipeline automatically builds and deploys your application to AWS whenever you push to the main branch.

## Troubleshooting

- Ensure all API keys are correctly set in the `.env` file
- Verify AWS IAM user has appropriate permissions
- Check that Docker is running on EC2 before deploying
- Confirm Pinecone index is created before storing embeddings

## Contributing

We welcome contributions! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on the GitHub repository.