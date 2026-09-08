# SmartHire Answer Quality Evaluation

Compact live benchmark for retrieval, mentor quality, prompt comparison, and refusal safety.

## Overall

- Retrieval: Top-1 **100%** | Top-5 **100%** | Top-10 **100%**
- Mentor: Correctness **5.0/5** | Grounding **5.0/5** | Helpfulness **5.0/5**
- Refusal accuracy: **100%**
- Judge calls: **8** | Prompt comparison: **True**
- In-scope cases scored: **1/8**

## Mentor scores

| # | Case | C | G | H | Evidence |
|---:|---|---:|---:|---:|---:|
| 1 | What skills should I prioritise to become a Data Scientist? | 5 | 5 | 5 | 6 |
| 2 | What is a practical career path for becoming a Software Engineer? | N/A | N/A | N/A | 6 |
| 3 | Which skills are most important for entry-level Data Analyst roles? | N/A | N/A | N/A | 0 |
| 4 | How can I move from a non-technical background into machine learning engineering? | N/A | N/A | N/A | 0 |
| 5 | What skills should I strengthen for Python backend developer jobs? | N/A | N/A | N/A | 0 |
| 6 | What skills should I learn to become an NLP-focused Data Scientist, and which specific tools or pro… | N/A | N/A | N/A | 0 |
| 7 | Based on the included Data Scientist and Data Engineer postings, how do the skills for those roles… | N/A | N/A | N/A | 0 |
| 8 | Since the Data Scientist career path in SmartHire has Foundation, Entry-level data work, Data Scien… | N/A | N/A | N/A | 0 |

## Evaluation warnings

- What is a practical career path for becoming a Software Engineer? — quality judge score unavailable.
- Which skills are most important for entry-level Data Analyst roles? — quality judge score unavailable.
- How can I move from a non-technical background into machine learning engineering? — quality judge score unavailable.
- What skills should I strengthen for Python backend developer jobs? — quality judge score unavailable.
- What skills should I learn to become an NLP-focused Data Scientist, and which specific tools or projects should I prioritise? — quality judge score unavailable.
- Based on the included Data Scientist and Data Engineer postings, how do the skills for those roles overlap, and where do they differ? — quality judge score unavailable.
- Since the Data Scientist career path in SmartHire has Foundation, Entry-level data work, Data Scientist, Senior Data Scientist, and Specialist or lea… — quality judge score unavailable.

## Retrieval

| Query | Accepted categories | Top-1 | Top-5 | Top-10 |
|---|---|---:|---:|---:|
| Python backend APIs Java Spring REST services | `Python Developer, Backend Developer, Java Developer, Software Engineer, Software Development Engineer` | True | True | True |
| Node.js JavaScript cloud backend development | `Backend Developer, Software Engineer, Software Development Engineer, Web Developer, Cloud Engineer` | True | True | True |
| machine learning Python TensorFlow statistics | `Machine Learning Engineer, Data Scientist` | True | True | True |
| data science NLP deep learning SQL | `Data Scientist, Machine Learning Engineer` | True | True | True |
| predictive modelling data analysis Python | `Data Scientist, Data Analyst, Business Analyst, Machine Learning Engineer` | True | True | True |
| software development debugging unit testing APIs | `Software Engineer, Software Development Engineer, Backend Developer, Application Developer, Application Support Engineer` | True | True | True |
| PHP Laravel MySQL backend web application development | `PHP Developer, Web Developer, Backend Developer` | True | True | True |
| AWS Azure GCP cloud infrastructure deployment DevOps automation | `Cloud Engineer, GCP Data Engineer` | True | True | True |
| HTML CSS JavaScript responsive UI frontend web development | `Frontend Developer, Web Developer` | True | True | True |
| React JavaScript JSX frontend components hooks responsive web applications | `React JS Developer, Frontend Developer, Web Developer` | True | True | True |
| Android iOS mobile application development Flutter Kotlin Swift | `Mobile App Developer` | True | True | True |
| production application support incident troubleshooting monitoring bug resolution SLA | `Application Support Engineer` | True | True | True |

## Prompt comparison

- Status: **SKIPPED**
- Reason: Gemini generation was unavailable during prompt comparison: The AI service is temporarily busy or unavailable. SmartHire tried the configured Gemini fallback models as well. Pleas…

## Safety

- **PASS** — 3/3 out-of-scope cases correctly refused.

## Notes

- C/G/H = correctness / grounding / helpfulness (1–5). N/A means no Gemini judge score was available; it is not a zero score.
- Retrieval counts a result as correct when its category belongs to that query's accepted category set.
