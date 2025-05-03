# bunqBuddy - Hackathon 2025 Project

## Overview
This project is developed for the bunq Hackathon 2025. It includes tools and scripts for web scraping, data processing, and building a Streamlit-based application. The project leverages various Python libraries to handle tasks such as scraping Medium posts, processing embeddings, and interacting with AI models.

## Live Demo

Check out the live demo hosted on Streamlit Community:  
[Live Demo](https://bunq-hackaton-2025-nqqfu4khymxubt2bxkrg68.streamlit.app/~/+/?chatbot=true)

## Project Structure
```
data_update.py          # Script for updating and processing data, including embeddings.
embeddings.npy          # Precomputed embeddings file used for AI model interactions.
env_variables.json      # Configuration file for storing environment variables like API keys.
logo.png                # Project logo used in the Streamlit application.
rag.py                  # Script for retrieval-augmented generation (RAG) tasks.
requirements.txt        # List of Python dependencies required for the project.
scrapping_medium.py     # Script for scraping Medium posts related to Bunq.
streamlit.py            # Entry point for the Streamlit web application.
utils.py                # Utility functions and data models used across the project.

scraped_data/           # Directory containing scraped data.
  bunq_full_docs.txt    # Full documentation scraped from relevant sources.
  medium_bunq_posts.txt # Medium posts related to Bunq.

streamlit-version/      # Directory containing compiled Streamlit application files.
  __pycache__/          # Python cache files.
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Bunq-Hackaton-2025
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Update `env_variables.json` with the necessary API keys and configurations.

## Usage

### Web Scraping
- Run `scrapping_medium.py` to scrape Medium posts related to Bunq:
  ```bash
  python scrapping_medium.py
  ```

### Data Update
- Use `data_update.py` to process and update data:
  ```bash
  python data_update.py
  ```

### Streamlit Application
- Launch the Streamlit app:
  ```bash
  streamlit run streamlit.py
  ```

## Dependencies
The project uses the following Python libraries:
- `beautifulsoup4`
- `langchain_core`
- `langchain_nvidia_ai_endpoints`
- `langchain_text_splitters`
- `numpy`
- `pydantic`
- `python-dotenv`
- `selenium`
- `tenacity`
- `streamlit`

Refer to `requirements.txt` for the exact versions.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributors
- Nirmalkumar Balamurugan - Developer and Actor
- Nitish Kumar Gnanasekaran - Developer
- Matteo Di Bari - Developer and Voice Actor
- Anant Trivedi - Developer

## Acknowledgments
Special thanks to bunq for organizing this hackathon and providing the resources to make this project possible.
