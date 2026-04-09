import requests
import json
import logging
import time


def generate_cover_letter(resume_text, job_desc, api_key, model, target_role="", tone="professional"):
    """
    Calls the LLM to generate a tailored cover letter based on the
    candidate's resume and the target job description.

    Args:
        resume_text (str): The candidate's resume text.
        job_desc (str): The target job description.
        api_key (str): OpenRouter API key.
        model (str): The model identifier to use.
        target_role (str): Optional target role name.
        tone (str): One of 'professional', 'confident', 'conversational'.

    Returns:
        dict: {"cover_letter": str} or {"error": str}
    """
    tone_instructions = {
        "professional": "Use a formal, polished, and professional tone. Keep it concise and structured.",
        "confident": "Use a bold, assertive, and highly confident tone. Showcase achievements prominently.",
        "conversational": "Use a warm, personable, and slightly informal tone. Make it feel human and genuine.",
    }
    tone_guide = tone_instructions.get(tone, tone_instructions["professional"])

    prompt = f"""
You are an elite career coach and professional cover letter writer.

I will provide a candidate's resume and a job description. Your task is to write a compelling, highly personalized cover letter that:
1. Opens with a strong hook — no generic "I am writing to apply for..." openers.
2. Directly connects the candidate's most relevant experience and achievements to the job requirements.
3. Highlights 2-3 key skills or accomplishments that directly map to the JD.
4. Closes with a confident, action-oriented statement.
5. Is kept to 3-4 concise paragraphs (no more than ~350 words total).

Tone Instruction: {tone_guide}

Target Role (if provided): {target_role if target_role else "Not specified — infer from JD"}

### Candidate Resume:
{resume_text}

### Target Job Description:
{job_desc}

Return ONLY the cover letter text itself — no subject lines, no "Dear Hiring Manager" header, no extra commentary, no markdown. 
Start directly with the opening paragraph. Ensure every sentence is purposeful and tailored.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5001",
        "X-Title": "HireSense Cover Letter Generator",
        "Content-Type": "application/json",
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
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a world-class cover letter writer. "
                                "Return only the cover letter body text, no extra commentary."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.6,
                },
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            cover_letter_text = data["choices"][0]["message"]["content"].strip()

            # Strip any accidental markdown wrapping
            if cover_letter_text.startswith("```"):
                cover_letter_text = cover_letter_text.split("```", 2)[-1].strip()
                if cover_letter_text.endswith("```"):
                    cover_letter_text = cover_letter_text[:-3].strip()

            return {"cover_letter": cover_letter_text}

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logging.warning(f"Rate limited (429). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    logging.error(f"Rate limit exhausted after {max_retries} attempts.")
                    return _mock_cover_letter()
            logging.error(f"HTTP error during cover letter generation: {e}")
            return _mock_cover_letter()

        except Exception as e:
            logging.error(f"Cover letter generation failed: {e}")
            return _mock_cover_letter()

def _mock_cover_letter():
    return {
        "cover_letter": "[DEMO MOCK] Dear Hiring Manager,\n\nI am writing to express my strong interest in joining your engineering team. My background in building robust, high-performance web services uniquely positions me to tackle the challenges outlined in your job description.\n\nIn my previous role, I spearheaded the deployment of highly scalable backend architectures using modern frameworks like FastAPI and Docker. I've consistently focused on performance optimization through caching and query refinement, ensuring seamless experiences for thousands of daily users by dropping response times by over 35%.\n\nI am incredibly excited about the opportunity to bring my technical expertise and drive for engineering excellence to your team. Let's discuss how I can contribute to your continued success."
    }
