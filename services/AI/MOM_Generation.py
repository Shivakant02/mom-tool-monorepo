import re
import json
import datetime
import os
from fastapi import HTTPException
from openai import OpenAI


current_time = datetime.date.today()
current_day_num = datetime.date.today().weekday()

# Create a list of day names
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Convert numeric weekday to day name
current_day_name = day_names[current_day_num]

class TranscriptProcessor:
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def parse_transcript(self,file_path: str) -> str:
        """
        Parse the transcript .txt file and remove timestamps.
        Expected format per line: "Speaker X (mm:ss): text"
        This function removes the timestamp and returns a cleaned transcript.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")

        cleaned_lines = []
        # Remove timestamp pattern e.g. (0:51) using regex.
        timestamp_pattern = re.compile(r'\(\d+:\d+\)')
        for line in lines:
            line = line.strip()
            # Remove the timestamp pattern.
            cleaned_line = timestamp_pattern.sub("", line)
            # Clean up extra spaces
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()
            cleaned_lines.append(cleaned_line)
        return "\n".join(cleaned_lines)

    def combine_transcript_and_chats(self,transcript_file: str, chat_file: str) -> str:
        """
        Combines the transcript and chat files into a single text.

        The transcript file is first parsed to remove timestamps.
        Then, after a clear separator, the contents of the chat file are appended.
        """
        transcript_text =self.parse_transcript(transcript_file)

        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_text = f.read().strip()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Chat file '{chat_file}' not found.")

        # Create final text with a clear header for each section.
        final_text = f"Transcript:\n{transcript_text}\n\nChats:\n{chat_text}"
        return final_text

    def get_chatgpt_response(self, transcript: str):
        """Send the transcript to OpenAI API and get the analysis."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": (
                         "You are an AI assistant tasked with analyzing the entire meeting transcript provided. "
                         "From the text, extract the following information:\n"
                         "1. Organizer: The person who organized the meeting.\n"
                         "2. Discussion topics: The main topics discussed in the meeting.\n"
                         "3. Key points of the meeting: The most important points raised.\n"
                         "4. FAQs from the chat: Frequently asked questions based solely on the chat messages (ignore FAQs that come from the spoken transcript if no explicit chat is provided) return NO FAQS.\n"
                         "5. Highlight assigned action items with deadlines and ownership: List tasks assigned with their deadlines and responsible individuals.\n\n"

                         "**Special Instructions for Deadlines**:\n"
                         "- Assume the workweek is **Monday to Friday** (ignore weekends).\n"
                         "- For relative deadlines:\n"
                         "  - 'End of the week' refers to **Friday** of the current week.\n"
                         "  - 'Next [Weekday]' (e.g., 'Next Tuesday') means the **next occurrence** of that weekday within the workweek.\n"
                         "  - 'End of next week' refers to **Friday of the following week**.\n"
                         "- Convert all deadlines to `day/month/year` format using today's date as reference.\n\n"

                         "**Examples**:\n"
                         f"- Today: {current_time.strftime('%Y-%m-%d')} ({current_day_name})\n"
                         "  - 'Today at 2 PM' → `2025-03-21`\n"
                         "  - 'End of the week' → `2025-03-21` (Friday)\n"
                         "  - 'Next Tuesday' → `2025-03-25` (if today is Friday, 21/03/2025)\n"
                         "  - 'End of next week' → `2025-03-25` (Friday of the following week)\n"
                         "  - 'April 2nd' → `2025-04-02`\n\n"

                         "Provide the extracted information in JSON format with this structure:\n"
                         "{\n"
                         "  \"organizer\": \"name\",\n"
                         "  \"discussion_topics\": [\"topic1\", \"topic2\", ...],\n"
                         "  \"key_points\": [\"point1\", \"point2\", ...],\n"
                         "  \"faqs\": [\"faq1\", \"faq2\", ...],\n"
                         "  \"action_items\": [\n"
                         "    {\"item\": \"action item 1\", \"deadline\": \"yyyy-mm-dd\", \"owner\": \"name\"},\n"
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
            # Extract JSON portion
            start = raw_response.find("{")
            end = raw_response.rfind("}")
            if start != -1 and end != -1:
                cleaned_response = raw_response[start:end+1]
            else:
                cleaned_response = raw_response
            return cleaned_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")











# def parse_vtt(self, file_path: str):
    #     """Parse the .vtt file and extract speaker names and their text."""
    #     segments = []
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             for line in f:
    #                 line = line.strip()
    #                 # Look for lines with <v speaker>text</v> pattern
    #                 if line.startswith('<v') and line.endswith('</v>'):
    #                     match = re.search(r'<v (.*?)>(.*?)</v>', line)
    #                     if match:
    #                         speaker = match.group(1).strip()
    #                         text = match.group(2).strip()
    #                         segments.append({"speaker": speaker, "text": text})
    #     except FileNotFoundError:
    #         raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")
    #     return segments
    #
    # def group_segments(self, segments):
    #     """Group consecutive segments by the same speaker."""
    #     if not segments:
    #         return []
    #     grouped = []
    #     current_speaker = segments[0]["speaker"]
    #     current_text = [segments[0]["text"]]
    #     for segment in segments[1:]:
    #         if segment["speaker"] == current_speaker:
    #             current_text.append(segment["text"])
    #         else:
    #             grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
    #             current_speaker = segment["speaker"]
    #             current_text = [segment["text"]]
    #     # Append the last group
    #     grouped.append({"speaker": current_speaker, "text": " ".join(current_text)})
    #     return grouped
    #
    # def create_transcript(self, grouped_segments):
    #     """Create a formatted transcript from grouped segments."""
    #     if not grouped_segments:
    #         return "No transcript available."
    #     transcript_lines = [f"{seg['speaker']}: {seg['text']}" for seg in grouped_segments]
    #     return "\n".join(transcript_lines)