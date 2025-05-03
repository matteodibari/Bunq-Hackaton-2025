# BunqBuddy - Hackathon 2025 Project

## Overview
This project is developed for the Bunq Hackathon 2025. It includes tools and scripts for web scraping, data processing, and building a Streamlit-based application. The project leverages various Python libraries to handle tasks such as scraping Medium posts, processing embeddings, and interacting with AI models.

## Project Structure
```
data_update.py          # Script for updating data
embeddings.npy          # Precomputed embeddings file
env_variables.json      # Environment variables configuration
logo.png                # Project logo
rag.py                  # Script for retrieval-augmented generation
requirements.txt        # Python dependencies
scrapping_medium.py     # Script for scraping Medium posts
streamlit.py            # Streamlit application entry point
utils.py                # Utility functions

scraped_data/           # Directory containing scraped data
  bunq_full_docs.txt    # Full documentation scraped
  medium_bunq_posts.txt # Medium posts related to Bunq

streamlit-version/      # Streamlit application compiled files
  __pycache__/          # Python cache files
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
Special thanks to Bunq for organizing this hackathon and providing the resources to make this project possible.
