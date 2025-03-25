import os
from fastapi import HTTPException
from google import genai
from google.genai import types

class Matcher:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def match_names(self, names_list: list[str], attendees_list: list[str]) -> str:
        prompt_text = f"""
                                                You are an intelligent matching assistant tasked with matching a list of names with a list of attendees. The names in the first list may contain errors, typos, or variations (e.g., "pvbn" instead of "Pavan"), while the attendees' list contains the correct or properly written names. Your goal is to identify the closest possible match between the two lists, accounting for potential misspellings, abbreviations, phonetic similarities, or other minor discrepancies.

                                                Instructions:

                                                Analyze each name in the first list and compare it with all names in the attendees' list.

                                                Use fuzzy matching techniques to identify the closest match based on:

                                                Phonetic similarity (e.g., "pvbn" → "Pavan").

                                                Character similarity (e.g., "Jhon" → "John").

                                                Common abbreviations or nicknames (e.g., "PR" → "Pavan Reddy (PR)"). However, do not consider names that are very different and can stand alone as separate names. For example:

                                                Mike and Michael: If "Mike" is in the names list and "Michael" is in the attendees list, do not consider them a match because "Mike" can be a standalone name.

                                                Full forms: If the name in the list is an abbreviation (e.g., "KPR"), match it only if:

                                                The attendees list contains a single matching full form (e.g., "K Pavan Reddy").

                                                If the attendees list contains multiple possible matches (e.g., "K Pavan" and "Krishna Praveen Reddy"), do not match it.

                                                If the attendees list contains only a single letter (e.g., "K"), do not match it with "KPR".

                                                Typographical errors (e.g., "Sara" → "Sarah").

                                                Assign a confidence score (0 to 1) for each match, where 1 indicates a perfect match and lower scores indicate less certainty.

                                                If no reasonable match is found, flag the name as "Unmatched" for manual review.

                                                Provide the final output as a table with the following columns:

                                                Original Name: The name from the first list.

                                                Matched Attendee: The closest match from the attendees' list.

                                                Confidence Score: The confidence level of the match.


                                                Example Input:

                                                Names List:{names_list}

                                                Attendees List:{attendees_list}

                                                Example Output:
                                                don't explain anything even your thought process just give me the output in the format shown below.
                                                "{
                                                 "  \"Original_Name\": \"Orginal Name\",\n"
                                                 "  \"Matched_Attendee\": \"Matched Name\",\n"
                                                 "  \"Confidence_Score\": \"Score\",\n"
                                                 "  \"Notes\": \"why it is wrongly written ,for example is it beacuse of Phonetic similarity/Typographical/Missing some charecter/etc..\",\n"
                                                 "  ]\n"
                                                 }"
                                                 """
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_text)
                ]
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )
        result_text = ""
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                result_text += chunk.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
        return result_text

