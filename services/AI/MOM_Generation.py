# from grok_client import GrokClient
#
# # Your cookie values
# cookies = {
#     "x-anonuserid": "87c0f23a-c3e6-43db-a3f4-1c544510ef0d",
#     "x-challenge": "O9V8Z4dVzWim5HUG8rVArgzEh0pKKp4f3xNCGDG9Wvwef66qeMEZY7%2FRYcb9HXhO2l13Ky%2FrjpM%2BW%2B3ncGso2EEKaAD8hGWk%2FiXZhqscSIGlNrz73%2FvrWCGYocqm0h1pCiKUtwc2eIDGygQjqH8mi27xhDBgHtfapmoEGV55rT1XdqZQ1GY%3D",
#     "x-signature": "ikYJe59iiC%2FX0ef1viaYIAE%2BM9Tl4dGYZm%2FXz9I6kehVt3ut%2BSFM6bKYX7NUMmQ7ZPbNMlCRvYswQ%2F%2FFzcQoeA%3D%3D",
#     "sso": "eyJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoiN2FmMGY3MmYtZjlhNC00YzMxLTliZTctYWI1ZjYzZWYxNjkzIn0.3llzkpqNctmYRzt-uEoPH42iEZplmkspnEViuovDPnY",
#     "sso-rw": "eyJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoiN2FmMGY3MmYtZjlhNC00YzMxLTliZTctYWI1ZjYzZWYxNjkzIn0.3llzkpqNctmYRzt-uEoPH42iEZplmkspnEViuovDPnY"
# }
#
# # Initialize the client
# client = GrokClient(cookies)
#
# # Send a message and get response
# response = client.send_message("write a poem")
# print(response)
import os
# import re
# import json
# import sys
# from openai import OpenAI
#
#
# def parse_vtt(file_path):
#     """Parse the .vtt file and extract speaker names and their text."""
#     segments = []
#     with open(file_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             # Look for lines with <v speaker>text</v> pattern
#             if line.startswith('<v') and line.endswith('</v>'):
#                 match = re.search(r'<v (.*?)>(.*?)</v>', line)
#                 if match:
#                     speaker = match.group(1).strip()
#                     text = match.group(2).strip()
#                     segments.append({"speaker": speaker, "text": text})
#     return segments
#
#
# def group_segments(segments):
#     """Group consecutive segments by the same speaker."""
#     if not segments:
#         return []
#     grouped = []
#     current_speaker = segments[0]["speaker"]
#     current_text = [segments[0]["text"]]
#
#     for segment in segments[1:]:
#         if segment["speaker"] == current_speaker:
#             current_text.append(segment["text"])
#         else:
#             grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
#             current_speaker = segment["speaker"]
#             current_text = [segment["text"]]
#
#     # Append the last group
#     grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
#     return grouped
#
#
# def create_transcript(grouped_segments):
#     """Create a formatted transcript from grouped segments."""
#     if not grouped_segments:
#         return "No transcript available."
#     transcript_lines = [f"{seg['speaker']}: {seg['text']}" for seg in grouped_segments]
#     return "\n".join(transcript_lines)
#
#
# def get_chatgpt_response(transcript, model="gpt-4o-mini"):
#     """Send the transcript to OpenAI API and get the analysis."""
#     try:
#         # Initialize the client (replace with your API key or use environment variable)
#         client = OpenAI(api_key="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")  # Set your OpenAI API key
#
#         # Create the API call
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system",
#                  "content": "You are an AI assistant tasked with analyzing the entire meeting transcript provided. "
#                             "From the text, extract the following information:\n"
#                             "1. Organizer: The person who organized the meeting.\n"
#                             "2. Discussion topics: The main topics discussed in the meeting.\n"
#                             "3. Key points of the meeting: The most important points raised.\n"
#                             "4. FAQs from the chat: Frequently asked questions based on what was discussed (assume these are recurring questions from the spoken content if no explicit chat is provided).\n"
#                             "5. Highlight assigned action items with deadlines and ownership: List tasks assigned with their deadlines and responsible individuals.\n\n"
#                             "Provide the extracted information in JSON format with this structure:\n"
#                             "{\n"
#                             "  \"organizer\": \"name\",\n"
#                             "  \"discussion_topics\": [\"topic1\", \"topic2\", ...],\n"
#                             "  \"key_points\": [\"point1\", \"point2\", ...],\n"
#                             "  \"faqs\": [\"faq1\", \"faq2\", ...],\n"
#                             "  \"action_items\": [\n"
#                             "    {\"item\": \"action item 1\", \"deadline\": \"date\", \"owner\": \"name\"},\n"
#                             "    ...\n"
#                             "  ]\n"
#                             "}"},
#                 {"role": "user", "content": transcript}
#             ],
#             max_tokens=1500,
#             temperature=0.5
#         )
#
#         # Extract and return the response text
#         return response.choices[0].message.content
#
#     except Exception as e:
#         return f"An error occurred: {str(e)}"
#
#
# def main(vtt_file):
#     """Main function to process the .vtt file and extract information."""
#     # Parse the .vtt file
#     segments = parse_vtt(vtt_file)
#     if not segments:
#         print("No valid segments found in the transcript.")
#         return
#
#     # Group consecutive segments by speaker
#     grouped_segments = group_segments(segments)
#
#     # Create the transcript
#     transcript = create_transcript(grouped_segments)
#     print("Generated Transcript:\n", transcript)
#
#     # Analyze with OpenAI API
#     analysis = get_chatgpt_response(transcript)
#
#     # Parse and display the JSON response
#     try:
#         extracted_info = json.loads(analysis)
#         print("\nExtracted Information:\n")
#         print(json.dumps(extracted_info, indent=2))
#     except json.JSONDecodeError:
#         print("Failed to parse JSON response from OpenAI:")
#         print(analysis)
#
#
# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script.py <transcript.vtt>")
#         sys.exit(1)
#
#     vtt_file = sys.argv[1]
#     main(vtt_file)




import re
import json
from fastapi import FastAPI, HTTPException, Query
import uvicorn
from openai import OpenAI
import datetime
from dotenv import load_dotenv

load_dotenv()

# Get current date and numeric weekday (0=Monday, 1=Tuesday, etc.)
current_time = datetime.date.today()
current_day_num = datetime.date.today().weekday()

# Create a list of day names
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Convert numeric weekday to day name
current_day_name = day_names[current_day_num]


app = FastAPI()

def parse_vtt(file_path: str):
    """Parse the .vtt file and extract speaker names and their text."""
    segments = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Look for lines with <v speaker>text</v> pattern
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
    """Group consecutive segments by the same speaker."""
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

    # Append the last group
    grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
    return grouped

def create_transcript(grouped_segments):
    """Create a formatted transcript from grouped segments."""
    if not grouped_segments:
        return "No transcript available."
    transcript_lines = [f"{seg['speaker']}: {seg['text']}" for seg in grouped_segments]
    return "\n".join(transcript_lines)

def get_chatgpt_response(transcript, model="gpt-4o-mini"):
    """Send the transcript to OpenAI API and get the analysis."""
    try:
        # Initialize the client (replace with your API key or set it via environment variable)
        client = OpenAI(api_key=os.getenv("OpenAI_API"))

        # Create the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": (
                     "You are an AI assistant tasked with analyzing the entire meeting transcript provided. "
                     "From the text, extract the following information:\n"
                     "1. Organizer: The person who organized the meeting.\n"
                     "2. Discussion topics: The main topics discussed in the meeting.\n"
                     "3. Key points of the meeting: The most important points raised.\n"
                     "4. FAQs from the chat: Frequently asked questions based on what was discussed (assume these are recurring questions from the spoken content if no explicit chat is provided).\n"
                     "5. Highlight assigned action items with deadlines and ownership: List tasks assigned with their deadlines and responsible individuals.\n\n"
                     
                      "**Special Instructions for Deadlines**:\n"
                      "- Assume the workweek is **Monday to Friday** (ignore weekends).\n"
                      "- For relative deadlines:\n"
                      "  - 'End of the week' refers to **Friday** of the current week.\n"
                      "  - 'Next [Weekday]' (e.g., 'Next Tuesday') means the **next occurrence** of that weekday within the workweek.\n"
                      "  - 'End of next week' refers to **Friday of the following week**.\n"
                      "- Convert all deadlines to `day/month/year` format using today's date as reference.\n\n"
                    
                      "**Examples**:\n"
                      f"- Today: {current_time.strftime('%d/%m/%Y')} ({current_day_name})\n"
                      "  - 'Today at 2 PM' → `21/03/2025`\n"
                      "  - 'End of the week' → `21/03/2025` (Friday)\n"
                      "  - 'Next Tuesday' → `25/03/2025` (if today is Friday, 21/03/2025)\n"
                      "  - 'End of next week' → `28/03/2025` (Friday of the following week)\n"
                      "  - 'April 2nd' → `02/04/2025`\n\n"
                     
                     "Provide the extracted information in JSON format with this structure:\n"
                     "{\n"
                     "  \"organizer\": \"name\",\n"
                     "  \"discussion_topics\": [\"topic1\", \"topic2\", ...],\n"
                     "  \"key_points\": [\"point1\", \"point2\", ...],\n"
                     "  \"faqs\": [\"faq1\", \"faq2\", ...],\n"
                     "  \"action_items\": [\n"
                     "    {\"item\": \"action item 1\", \"deadline\": \"date\", \"owner\": \"name\"},\n"
                     "    ...\n"
                     "  ]\n"
                     "}"
                 )},
                {"role": "user", "content": transcript}
            ],
            max_tokens=1500,
            temperature=0.5
        )

        raw_response = response.choices[0].message.content
        print("Raw OpenAI API response:", raw_response)

        # Remove markdown formatting if present
        if raw_response.startswith("```") and raw_response.endswith("```"):
            raw_response = raw_response.strip("```").strip()

        # Extract the JSON portion from the response if there is extra text
        start = raw_response.find("{")
        end = raw_response.rfind("}")
        if start != -1 and end != -1:
            cleaned_response = raw_response[start: end + 1]
        else:
            cleaned_response = raw_response

        return cleaned_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


@app.get("/process")
def process_transcript(filename: str = Query(..., description="The .vtt transcript file in the same directory")):
    """
    Process a transcript file (.vtt) and extract the meeting analysis.
    Example URL: http://localhost:8000/process?filename=your_transcript.vtt
    """
    segments = parse_vtt(filename)
    if not segments:
        raise HTTPException(status_code=404, detail="No valid segments found in the transcript.")

    grouped_segments = group_segments(segments)
    transcript = create_transcript(grouped_segments)
    analysis = get_chatgpt_response(transcript)

    try:
        extracted_info = json.loads(analysis)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from OpenAI.")

    return {"transcript": transcript, "extracted_info": extracted_info}

if __name__ == "__main__":
    # Run the app with: uvicorn your_script_name:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8001)


