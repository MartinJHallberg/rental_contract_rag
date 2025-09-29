# Rental Contract Checker 🏠

This is a demo application that uses Retrieval-Augmented Generation (RAG) to analyze rental contracts against Danish Rental Law. Upload your rental contract PDF and get instant analysis for potential legal issues and violations.

*Note: RAG is quite overkill since ChatGPT very well can analyze a rental contract and refer to paragraphs. The goal with this project was however to learn how to set up a RAG pipeline in a somewhat realistic scenario.*

## Demo

Play in 1.5x speed (for now :) )


https://github.com/user-attachments/assets/7a2ccace-113d-404c-b449-e61081fb8f3a



## 🚀 Features

- **PDF Contract Upload**: Drag and drop or upload rental contract PDFs
- **AI-Powered Analysis**: Uses OpenAI GPT models with RAG to analyze contracts
- **Legal Compliance Check**: Compares contracts against Danish Rental Act (Lejeloven)
- **Interactive Web Interface**: Clean, responsive web app built with Dash

## 🔧 To be improved 
- **Speed**
- **Correct flaggin**: Deposit and prepayment sometimes flagged even though correct
- **Paragraph number and page**: Paragraph number and page is sometimes wrong.

## 📋 Prerequisites

- Python 3.12 or higher
- Poetry (recommended) or pip
- OpenAI API key
- (Optional) LangSmith API key for tracing

## 🔧 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/rental_contract_rag.git
cd rental_contract_rag
```

### 2. Set Up Environment

**Using Poetry**
```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` file with your API keys:
```env
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: LangSmith for tracing (leave empty to disable)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=rental-contract-rag
ENABLE_TRACING=false
```

### 4. Run the Application

```bash
# Using Poetry
poetry run python src/app.py
```

The application will start on `http://localhost:8050`

## 📖 How to Use

1. **Open the Application**: Navigate to `http://localhost:8050` in your browser
2. **Upload Contract**: Drag and drop or click to upload a rental contract PDF
3. **Wait for Processing**: The app will extract text and analyze the contract
4. **View Results**: Get detailed analysis including:
   - Deposit amount validation
   - Termination condition checks
   - Price adjustment reviews
   - General legal compliance

## 🐳 Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build the image
docker-compose build

# Run the application
docker-compose up
```

The app will be available at `http://localhost:8050`

## 🧪 Running Tests

```bash
# Using Poetry
poetry run pytest
```

## 📁 Project Structure

```
rental_contract_rag/
├── src/
│   ├── app.py              # Main Dash application
│   ├── config.py           # Configuration and environment variables
│   ├── contract_loader.py  # PDF processing and text extraction
│   ├── data_loading.py     # Data loading utilities
│   ├── rag.py             # RAG implementation and analysis
│   └── data/              # Sample contracts and vector stores
├── tests/                 # Unit tests
├── exploration/           # Jupyter notebooks for development
├── pyproject.toml        # Poetry dependencies
├── README.md             # This file
└── .env.example          # Environment variables template
```

## 🔍 How It Works

1. **Document Processing**: Uploaded PDFs are processed using PyMuPDF and pdfplumber for text extraction
2. **Vector Store**: Danish Rental Law documents are embedded and stored in ChromaDB
3. **RAG Pipeline**: User queries are enhanced with relevant legal context from the vector store
4. **AI Analysis**: OpenAI GPT models analyze contracts using the retrieved legal context
5. **Results**: Structured analysis is returned with specific legal findings

## 🚨 Troubleshooting

1. **API Key Errors**
   - Ensure your OpenAI API key is correctly set in `.env`
   - Check that you have sufficient API credits

2. **PDF Processing Issues**
   - Make sure your PDF is text-based (not scanned images)
   - Try a different PDF if extraction fails


## 📄 License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Danish Rental Act data from [Retsinformation.dk](https://www.retsinformation.dk/eli/lta/2023/1793)
- Built with [LangChain](https://langchain.com/) and [Dash](https://dash.plotly.com/)
- Powered by [OpenAI](https://openai.com/) language models
