from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
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
    """Matches names with attendees using Gemini API."""
    # (Include your existing name-matching logic here)
    return {"message": "Name matching completed"}
