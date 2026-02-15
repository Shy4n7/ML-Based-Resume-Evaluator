import os
import spacy
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from sentence_transformers import SentenceTransformer, util

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Load BERT model
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_skills(text):
    doc = nlp(text)
    skills = []
    # Extract entities that are likely skills (Organizations, Products, Languages, GPE)
    # Note: This is a basic heuristic. A dedicated skill extractor would be better.
    labels = ["ORG", "PRODUCT", "LANGUAGE", "GPE"]
    for ent in doc.ents:
        if ent.label_ in labels:
            skills.append(ent.text)
    
    # Simple Deduplication and cleaning
    return list(set([s.strip() for s in skills if len(s) > 2]))

def extract_highlight(jd_text, resume_text):
    if not resume_text:
        return ""
    
    # Split resume into sentences using spaCy
    doc = nlp(resume_text)
    # Filter short lines (headers, bullet points that are too short)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    
    if not sentences:
        return ""
        
    # Encode JD (query) maps to the whole context
    # Use the first 512 tokens of JD to avoid length issues if JD is huge
    jd_embedding = bert_model.encode(jd_text[:2000], convert_to_tensor=True)
    
    # Encode sentences (corpus)
    # This might take a second for long resumes
    sent_embeddings = bert_model.encode(sentences, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_scores = util.cos_sim(jd_embedding, sent_embeddings)[0]
    
    # Find top match
    best_idx = cosine_scores.argmax().item()
    best_score = cosine_scores[best_idx].item()
    
    # Only return if it's a decent match
    if best_score > 0.25: 
        return sentences[best_idx]
    return ""

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX {file_path}: {e}")
    return text

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting TXT {file_path}: {e}")
            return ""
    return ""

def preprocess_text(text):
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    
    # NLP processing
    doc = nlp(text.lower())
    
    # Lemmatize and remove stop words
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    
    return " ".join(tokens)

def calculate_similarity(jd_text, resume_texts):
    if not resume_texts or not jd_text:
        return []
    
    # Compute embeddings
    jd_embedding = bert_model.encode(jd_text, convert_to_tensor=True)
    resume_embeddings = bert_model.encode(resume_texts, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_scores = util.cos_sim(jd_embedding, resume_embeddings)
    
    # Flatten result
    return cosine_scores[0].tolist()

def generate_reason(score, jd_text, resume_text):
    # Simple logic to generate a reason based on score and keywords
    
    jd_words = set(preprocess_text(jd_text).split())
    resume_words = set(preprocess_text(resume_text).split())
    
    common_words = list(jd_words.intersection(resume_words))
    missing_words = list(jd_words - resume_words)
    
    # Filter out very common/short words (keep words > 2 chars to include SQL, AWS, AI)
    significant_common = [w for w in common_words if len(w) > 2][:4]
    significant_missing = [w for w in missing_words if len(w) > 2][:4]
    
    reason = ""
    
    resume_unique = list(resume_words - jd_words)
    
    # Filter for interesting words (len > 3)
    significant_common = [w for w in common_words if len(w) > 2][:4]
    significant_missing = [w for w in missing_words if len(w) > 2][:4]
    other_skills = [w for w in resume_unique if len(w) > 3][:5]
    
def generate_reason(score, jd_text, resume_text):
    # Use NER-based skills for smarter comparison
    jd_skills = set([s.lower() for s in extract_skills(jd_text)])
    resume_skills = set([s.lower() for s in extract_skills(resume_text)])
    
    common_skills = list(jd_skills.intersection(resume_skills))
    missing_skills = list(jd_skills - resume_skills)
    resume_unique_skills = list(resume_skills - jd_skills)
    
    # Fallback to smart word matching if NER fails to find enough
    if len(common_skills) < 2 and len(missing_skills) < 2:
        jd_words = set(preprocess_text(jd_text).split())
        resume_words = set(preprocess_text(resume_text).split())
        common_skills = [w for w in list(jd_words.intersection(resume_words)) if len(w) > 3][:5]
        missing_skills = [w for w in list(jd_words - resume_words) if len(w) > 3][:5]

    # Capitalize for display
    significant_common = [s.title() for s in common_skills[:5]]
    significant_missing = [s.title() for s in missing_skills[:5]]
    other_skills = [s.title() for s in resume_unique_skills[:5]]
    
    reason = ""
    
    if score >= 70:
        reason = "Excellent Match! We recommend interviewing them because "
        if significant_common:
            skills = ", ".join(significant_common)
            reason += f"they demonstrate solid experience in key areas like {skills}. "
        else:
            reason += "their profile strongly aligns with the job description. "
        
        if other_skills:
            unique = ", ".join(other_skills)
            reason += f"Plus, they bring additional expertise in {unique}."
        
    elif score >= 30:
        reason = "Potential Match. This profile is worth considering because "
        if significant_common:
            skills = ", ".join(significant_common)
            reason += f"they have relevant skills like {skills}, "
        else:
            reason += "there is some overlap with the requirements, "
            
        if significant_missing:
            missing = ", ".join(significant_missing)
            reason += f"although they might lack specific tools like {missing}. "
            
        if other_skills:
            unique = ", ".join(other_skills)
            reason += f"They also have skills in {unique}, which could be useful."
            
    else:
        reason = "Low Match. This candidate may not be suitable for this specific role because "
        if significant_missing:
            missing = ", ".join(significant_missing)
            reason += f"they appear to be missing core requirements such as {missing}. "
        else:
            reason += "there is minimal overlap with the job description. "
            
        if other_skills:
            unique = ", ".join(other_skills)
            reason += f"However, they have strong skills in {unique}, so they might be a better fit for a different position."
            
    return reason
