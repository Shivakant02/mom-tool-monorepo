import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

fixing_router = APIRouter()

class MatchingRequest(BaseModel):
    names_list: list[str]
    attendees_list: list[str]

@fixing_router.post("/match")
def match_names(request: MatchingRequest):
    """
    Matches names with attendees using Google's Gemini API.
    """
    client = genai.Client(api_key=os.getenv("Gemini_API"))
    model = "gemini-2.0-flash"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""
                    You are an intelligent name-matching assistant.
                    Match names from `names_list` with the correct names in `attendees_list`.
                    Correct spelling errors, phonetic similarities, and minor discrepancies.

                    Example Input:
                    Names List: {request.names_list}
                    Attendees List: {request.attendees_list}

                    Expected Output (JSON Format):
                    [
                        {{"Original_Name": "pvbn", "Matched_Attendee": "Pavan", "Confidence_Score": 0.95, "Notes": "Phonetic similarity"}},
                        {{"Original_Name": "Jhon", "Matched_Attendee": "John", "Confidence_Score": 0.98, "Notes": "Typographical error"}}
                    ]
                """),
            ],
        ),
    ]

    try:
        generate_content_config = types.GenerateContentConfig(
            temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192, response_mime_type="text/plain"
        )
        result_text = ""
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config):
            result_text += chunk.text
        return {"result": result_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
