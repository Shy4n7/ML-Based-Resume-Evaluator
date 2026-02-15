# Database PRD
## ML-Based Resume Evaluator

---

## Purpose
Store minimal resume text and similarity scores.

## Storage Strategy
Lightweight SQLite database or in-memory processing.

## Tables

### resumes
| Field | Type | Description |
|-------|---------|--------------|
| id | INTEGER | Primary key |
| filename | TEXT | Resume name |
| extracted_text | TEXT | Parsed text |

### results
| Field | Type | Description |
|-------|---------|--------------|
| id | INTEGER | Primary key |
| resume_id | INTEGER | Foreign key |
| score | FLOAT | Similarity score |

## Non-Functional Requirements
- Lightweight
- Local storage only
- Fast operations

## Tech Stack
- SQLite
