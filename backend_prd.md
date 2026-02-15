# Backend PRD
## ML-Based Resume Evaluator

---

## Purpose
Process uploaded files, apply NLP + ML, compute similarity scores, and return ranked candidates.

## Responsibilities
- Handle file uploads
- Extract text from PDF/DOCX
- Clean and preprocess text
- Vectorize text using TF-IDF
- Compute cosine similarity
- Rank candidates
- Return JSON results

## Machine Learning Components

### TF-IDF Vectorizer
Converts text to numerical vectors (feature extraction)

### Cosine Similarity
Computes similarity score between JD and resumes

### Optional Classification
Logistic Regression / Naive Bayes for Selected/Rejected prediction

## APIs

### POST /evaluate
Input: JD + resumes  
Output: ranked scores JSON

### GET /health
Returns server status

## Tech Stack
- Python
- Flask/FastAPI
- Scikit-learn
- NLTK/spaCy
- pdfplumber
- python-docx
