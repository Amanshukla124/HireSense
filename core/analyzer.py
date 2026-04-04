import requests
import json
import re
import time
from collections import Counter
from core.ats_checker import check_ats_compliance

# ─────────────────────────────────────────────
# Common filler words to ignore during matching
# ─────────────────────────────────────────────
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'shall', 'can', 'need',
    'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
    'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'out', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'because', 'if', 'while', 'about', 'up',
    'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we', 'our',
    'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they',
    'them', 'their', 'what', 'which', 'who', 'whom', 'whose', 'etc',
    'also', 'well', 'using', 'work', 'working', 'experience', 'team',
    'ability', 'strong', 'good', 'years', 'year', 'role', 'looking',
    'required', 'preferred', 'must', 'including', 'like', 'new', 'join',
    'company', 'job', 'position', 'candidate', 'apply', 'skills',
    'requirements', 'responsibilities', 'qualifications', 'knowledge',
    'plus', 'bonus', 'basics', 'basic', 'development', 'understand',
    'understanding', 'building', 'build', 'create', 'manage', 'ensure',
    'maintain', 'implement', 'design', 'develop', 'support', 'provide',
    'make', 'take', 'get', 'give', 'help', 'show', 'try', 'ask',
    'tell', 'find', 'use', 'know', 'want', 'see', 'come', 'think',
    'look', 'back', 'way', 'day', 'even', 'go', 'any', 'part',
    'related', 'relevant', 'solving', 'problem', 'problems', 'familiar',
    'proficiency', 'proficient', 'excellent', 'expert', 'senior',
    'junior', 'mid', 'level', 'engineering', 'engineer', 'developer',
    'software', 'application', 'applications', 'system', 'systems',
    'service', 'services', 'based', 'driven', 'oriented', 'api',
    'learning', 'pipelines', 'pipeline', 'tools', 'tool', 'platform',
    'platforms', 'environment', 'environments', 'deploying', 'deployment',
    'backend', 'frontend', 'etc.', 'e.g.', 'i.e.'
}

# ─────────────────────────────────────────────
# Known multi-word technical skills / phrases
# ─────────────────────────────────────────────
MULTI_WORD_SKILLS = [
    'machine learning', 'deep learning', 'data science', 'data engineering',
    'data analysis', 'natural language processing', 'computer vision',
    'ci/cd', 'ci cd', 'version control', 'unit testing', 'test driven',
    'rest api', 'rest apis', 'restful api', 'restful apis',
    'project management', 'agile methodology', 'scrum master',
    'cloud computing', 'web development', 'mobile development',
    'front end', 'front-end', 'back end', 'back-end', 'full stack',
    'full-stack', 'object oriented', 'object-oriented',
    'amazon web services', 'google cloud', 'google cloud platform',
    'microsoft azure', 'power bi', 'node js', 'node.js', 'react js',
    'react.js', 'vue js', 'vue.js', 'next js', 'next.js',
    'spring boot', 'ruby on rails', 'asp.net', '.net core',
    'sql server', 'big data', 'problem solving', 'time management',
    'communication skills', 'critical thinking', 'team leadership',
]


def _normalize(text):
    """Lowercase and strip non-alphanumeric characters (keep / and .)."""
    return text.lower().strip()


def _tokenize(text):
    """Split text into cleaned tokens, removing stop words."""
    text = _normalize(text)
    tokens = re.findall(r'[a-z0-9#+\.\-/]+', text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def _extract_multiword_skills(text):
    """Find known multi-word skills present in the text."""
    text_lower = _normalize(text)
    found = set()
    for skill in MULTI_WORD_SKILLS:
        if skill in text_lower:
            found.add(skill)
    return found


# ═════════════════════════════════════════════
#  KEYWORD-BASED ANALYSIS  (Rule-based engine)
# ═════════════════════════════════════════════

def keyword_analysis(resume_text, job_desc):
    """
    Perform rule-based keyword analysis.
    Returns a dict with:
      - keyword_score (0-100)
      - matched_keywords
      - missing_keywords
      - resume_keywords
      - jd_keywords
    """
    # Single-word tokens
    resume_tokens = set(_tokenize(resume_text))
    jd_tokens = set(_tokenize(job_desc))

    # Multi-word skills
    resume_multi = _extract_multiword_skills(resume_text)
    jd_multi = _extract_multiword_skills(job_desc)

    # Combine
    resume_all = resume_tokens | resume_multi
    jd_all = jd_tokens | jd_multi

    if not jd_all:
        return {
            "keyword_score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "resume_keywords": sorted(resume_all),
            "jd_keywords": sorted(jd_all),
        }

    matched = jd_all & resume_all
    missing = jd_all - resume_all

    keyword_score = round((len(matched) / len(jd_all)) * 100)

    return {
        "keyword_score": keyword_score,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "resume_keywords": sorted(resume_all),
        "jd_keywords": sorted(jd_all),
    }


# ═════════════════════════════════════════════
#  AI-BASED ANALYSIS  (OpenRouter LLM)
# ═════════════════════════════════════════════

def ai_analysis(resume_text, job_desc, api_key, model, target_role=""):
    """
    Call OpenRouter LLM for deep semantic analysis.
    Returns a dict with: ai_score, missing_skills, present_skills,
    suggestions, strengths  (or an error dict).
    """
    role_context = f"\nYou are specifically evaluating this resume for a role in: **{target_role}**." if target_role else ""

    prompt = f"""You are an expert ATS (Applicant Tracking System) and career coach.{role_context}
Analyze the following resume against the given job description.

Job Description:
{job_desc}

Resume:
{resume_text}

Provide your analysis in EXACTLY the following JSON format.
Do NOT wrap it in markdown code fences. Return ONLY the raw JSON object:
{{
  "ai_score": <integer 0–100 representing semantic match>,
  "missing_skills": ["skill1", "skill2"],
  "present_skills": ["skill1", "skill2"],
  "suggestions": ["actionable improvement 1", "actionable improvement 2", "actionable improvement 3"],
  "strengths": ["strength 1", "strength 2"]
}}

Rules:
- ai_score should reflect how well the resume SEMANTICALLY matches the job, not just keyword overlap.
- missing_skills: skills explicitly or implicitly required by the JD that the resume lacks.
- present_skills: skills the resume demonstrates that align with the JD.
- suggestions: 3-5 specific, actionable improvements to the resume for this job.
- strengths: 2-4 things the resume already does well for this role.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "HireSense AI",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    try:
        # Retry up to 4 times with exponential backoff for 429 rate limits
        last_status = None
        for attempt in range(4):
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=45,
            )
            last_status = response.status_code
            if response.status_code == 429 and attempt < 3:
                wait = 8 * (attempt + 1)  # 8s, 16s, 24s
                time.sleep(wait)
                continue
            response.raise_for_status()
            break
        else:
            return {"error": "Rate limit hit after multiple retries. Please wait ~30 seconds and try again.", "error_type": "rate_limit"}
            
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Strip markdown fences if the model added them
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response.", "raw_response": content}
    except requests.exceptions.Timeout:
        return {"error": "AI request timed out. Please try again.", "error_type": "timeout"}
    except Exception as e:
        raw = response.text if 'response' in dir() else 'No response'
        return {"error": str(e), "raw_response": raw, "error_type": "unknown"}


# ═════════════════════════════════════════════
#  COMBINED ANALYSIS  (Blended scoring)
# ═════════════════════════════════════════════

def analyze_resume(resume_text, job_desc, api_key, model, target_role=""):
    """
    Main entry point. Runs both keyword and AI analysis,
    then blends them into a single result.

    Blending: 40% keyword score + 60% AI semantic score.
    """
    if not api_key:
        return {"error": "OpenRouter API Key not configured. Set OPENROUTER_API_KEY in .env."}

    # ── Step 1: Rule-based keyword analysis ──
    kw = keyword_analysis(resume_text, job_desc)

    # ── Step 2: AI semantic analysis ──
    ai = ai_analysis(resume_text, job_desc, api_key, model, target_role)

    if "error" in ai:
        error_type = ai.get("error_type", "unknown")
        if error_type == "rate_limit":
            suggestion = "⏳ OpenRouter rate limit hit. Wait ~30 seconds and click Analyze again."
        elif error_type == "timeout":
            suggestion = "⌛ AI request timed out. Check your connection and try again."
        else:
            suggestion = f"AI analysis failed: {ai.get('error', 'Unknown error')}. Only keyword data is shown."

        return {
            "score": kw["keyword_score"],
            "keyword_score": kw["keyword_score"],
            "ai_score": None,
            "missing_skills": [],
            "present_skills": [],
            "suggestions": [suggestion],
            "strengths": [],
            "matched_keywords": kw["matched_keywords"],
            "missing_keywords": kw["missing_keywords"],
            "error_detail": ai.get("error"),
            "ats_issues": check_ats_compliance(resume_text),
        }

    # ── Step 3: Blend scores (40% keyword + 60% AI) ──
    ai_score = ai.get("ai_score", 50)
    keyword_score = kw["keyword_score"]
    blended_score = round(0.4 * keyword_score + 0.6 * ai_score)

    # Rely purely on the AI for the skill arrays to avoid noise from the basic tokenizer
    all_missing = ai.get("missing_skills", [])
    all_present = ai.get("present_skills", [])

    return {
        "score": blended_score,
        "keyword_score": keyword_score,
        "ai_score": ai_score,
        "missing_skills": all_missing,
        "present_skills": all_present,
        "suggestions": ai.get("suggestions", []),
        "strengths": ai.get("strengths", []),
        "matched_keywords": kw["matched_keywords"],
        "missing_keywords": kw["missing_keywords"],
        "ats_issues": check_ats_compliance(resume_text),
    }
