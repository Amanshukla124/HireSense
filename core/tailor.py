import requests
import json
import logging
import time

def generate_tailored_resumes(resume_text, job_desc, api_key, model, target_role=""):
    """
    Calls the LLM to generate two tailored versions of the resume 
    based on the job description.
    """
    
    # Base prompt to construct the LLM instruction
    prompt = f"""
You are an expert technical recruiter and resume writer. I am going to give you a candidate's resume and a target job description.
Your goal is to tailor the resume to the job description to improve its ATS score and keyword matching. 

Target Role (if provided): {target_role}

### Original Resume:
{resume_text}

### Target Job Description:
{job_desc}

You must return EXACTLY valid JSON, with no markdown code blocks outside or extra text.
The JSON must contain two keys: "conservative_option" and "aggressive_option".

1. "conservative_option": A string containing the tailored resume where you mostly keep the candidate's original structure and bullet points, but naturally weave in missing keywords from the JD and rephrase sentences slightly to highlight relevance.
2. "aggressive_option": A string containing the tailored resume where you aggressively rewrite, reorder, and restructure the bullet points to perfectly align with the exact metrics, skills, and language demanded by the JD.

Format requirement:
{{
  "conservative_option": "Full text of resume option 1...",
  "aggressive_option": "Full text of resume option 2..."
}}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5001",
        "X-Title": "HireSense AI Tailoring",
        "Content-Type": "application/json"
    }

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "You are a specialized AI designed to output only valid JSON. Do not include markdown wraps like ```json."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4
                },
                timeout=40
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data['choices'][0]['message']['content'].strip()

            # Clean up any potential markdown wrap if the model ignored the system prompt
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
                
            parsed = json.loads(raw_content)
            
            return {
                "conservative": parsed.get("conservative_option", "Error generating option."),
                "aggressive": parsed.get("aggressive_option", "Error generating option.")
            }

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logging.warning(f"Rate limited (429). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    logging.error(f"Rate limit exhausted after {max_retries} attempts.")
                    return {
                        "error": "The AI provider's rate limit was exceeded (429). Please wait a minute and try again.",
                        "conservative": "",
                        "aggressive": ""
                    }
            logging.error(f"HTTP error during tailoring: {e}")
            return {
                "error": f"API Error: {response.status_code} - {response.reason}",
                "conservative": "",
                "aggressive": ""
            }
        except Exception as e:
            logging.error(f"Tailoring strictly failed: {e}")
            return {
                "error": "Unexpected error while generating tailored resumes. Check logs for details.",
                "conservative": "",
                "aggressive": ""
            }
