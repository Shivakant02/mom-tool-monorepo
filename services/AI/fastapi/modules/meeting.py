import os
import json
import re
from fastapi import APIRouter, HTTPException, Query
from openai import OpenAI
from database import meeting_records
import datetime
from dotenv import load_dotenv

load_dotenv()

meeting_router = APIRouter()

def parse_vtt(file_path: str):
    """
    Parses the .vtt file and extracts speaker names and their text.
    """
    segments = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('<v') and line.endswith('</v>'):
                    match = re.search(r'<v (.*?)>(.*?)</v>', line)
                    if match:
                        speaker = match.group(1).strip()
                        text = match.group(2).strip()
                        segments.append({"speaker": speaker, "text": text})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")
    return segments

def group_segments(segments):
    """
    Groups consecutive segments by the same speaker.
    """
    if not segments:
        return []
    grouped = []
    current_speaker = segments[0]["speaker"]
    current_text = [segments[0]["text"]]

    for segment in segments[1:]:
        if segment["speaker"] == current_speaker:
            current_text.append(segment["text"])
        else:
            grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
            current_speaker = segment["speaker"]
            current_text = [segment["text"]]

    grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
    return grouped

def get_chatgpt_response(transcript):
    """
    Sends the transcript to OpenAI API and retrieves the MOM analysis.
    """
    client = OpenAI(api_key=os.getenv("OpenAI_API"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Analyze this transcript and generate MOM in JSON format."},
                  {"role": "user", "content": transcript}],
        max_tokens=1500,
        temperature=0.5
    )

    return json.loads(response.choices[0].message.content)

@meeting_router.get("/process")
def process_transcript(filename: str = Query(..., description="The .vtt transcript file")):
    """
    Processes a transcript file (.vtt) and extracts MOM details.
    """
    segments = parse_vtt(filename)
    if not segments:
        raise HTTPException(status_code=404, detail="No valid segments found.")

    grouped_segments = group_segments(segments)
    transcript = "\n".join(f"{seg['speaker']}: {seg['text']}" for seg in grouped_segments)
    mom_data = get_chatgpt_response(transcript)

    return {"transcript": transcript, "mom_data": mom_data}
