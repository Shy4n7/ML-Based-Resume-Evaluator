# ML-Based Resume Evaluator

A premium, intelligent resume ranking system using Natural Language Processing (NLP) and Machine Learning (Cosine Similarity).

## Setup

1. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

2. **Initialize Database**:
    ```bash
    python database.py
    ```

3. **Run Application**:
    ```bash
    python app.py
    ```

4. **Access UI**:
    Open [http://localhost:5000](http://localhost:5000)

## Features

- **Multi-Format Support**: Upload PDF, DOCX, or TXT for Job Descriptions and Resumes.
- **Advanced NLP**: Uses `spaCy` for text preprocessing (lemmatization, stop-word removal).
- **Intelligent Ranking**: Uses TF-IDF and Cosine Similarity to score candidates.
- **Premium UI**: Dark-themed, responsive interface built with Tailwind CSS.
- **Persistent Storage**: Saves all resumes and scores in a local SQLite database.

## Usage

1. Upload a Job Description (JD) file.
2. Upload one or more Resume files.
3. Click **Evaluate Capabilities**.
4. View the ranked list of candidates with their match scores.
