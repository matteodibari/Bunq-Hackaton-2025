# Bunq API Documentation RAG System

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system to efficiently query and retrieve information from the Bunq API documentation. It leverages LangChain, NVIDIA AI endpoints, and a custom RAG pipeline to provide accurate and context-aware answers to user queries.

## Features

- **Efficient Text Processing:** Uses `MarkdownTextSplitter` to split the Bunq API documentation into manageable chunks.
- **NVIDIA AI Integration:** Employs NVIDIA's `ChatNVIDIA` for generating responses based on retrieved information.
- **Custom RAG Pipeline:** Implements a `NvidiaRAGPipeline` for retrieving relevant documents and generating answers.
- **Environment Variable Management:** Securely manages API keys using a `.env` file.

## Requirements

- Python 3.10+
- NVIDIA API Key
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2. Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root and add your NVIDIA API key:

    ```
    NVIDIA_API_KEY=<your_nvidia_api_key>
    ```

## Usage

1. Place the Bunq API documentation in a text file named `bunq_full_docs.txt` in the `scraped_data` directory.

2. Run the `test.py` script:

    ```bash
    python test.py
    ```

    The script will initialize the RAG pipeline, and then query the system with two example questions:

    - "Tell me the account information for service providers?"
    - "Which is the bunq api object directly connected to the user and why is it directly connected?"

    The script will print the assistant's response and the sources used to generate the response for each query.

## Project Structure

```
.
├── scraped_data/
│   └── bunq_full_docs.txt  # Bunq API documentation
├── streamlit-version/
│   └── app.py              # Streamlit app for the project
├── data_update.py          # Script for updating data
├── embeddings.npy          # Precomputed embeddings
├── env_variables.json      # Environment variables in JSON format
├── rag.py                  # Custom RAG pipeline implementation
├── README.md               # Project documentation
├── requirements.txt        # Python package dependencies
├── streamlit.py            # Streamlit script
├── test.py                 # Main script
├── utils.py                # Utility functions
└── __pycache__/            # Compiled Python files
```

## Code Overview

- **`test.py`**: This is the main script that loads the Bunq API documentation, initializes the RAG pipeline, and runs example queries. It demonstrates how to use the `NvidiaRAGPipeline` to get answers to questions about the Bunq API.
- **`rag.py`**: This file contains the implementation of the `NvidiaRAGPipeline` class. This class handles the retrieval of relevant documents and the generation of answers using the `ChatNVIDIA` model.
- **`streamlit-version/app.py`**: A Streamlit app for interacting with the RAG system through a web interface.

## Troubleshooting

- **Missing API Key Warning:** Ensure that you have set the `NVIDIA_API_KEY` environment variable in your `.env` file.
- **Model Not Found Error:** Verify that the model name specified in `test.py` is a valid model supported by NVIDIA AI endpoints.
- **Other Errors:** Check the traceback for specific error messages and consult the documentation for LangChain and NVIDIA AI endpoints.

## License

[Specify the license under which your project is released] (e.g., MIT License)
