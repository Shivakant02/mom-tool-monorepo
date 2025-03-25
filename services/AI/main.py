import json
import os
import shutil
import sys
import time
import datetime
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Import your custom modules ---
from MOM_Generation import TranscriptProcessor
from FixingNames import Matcher
from teams_extractor import MeetingProcessor
from Send_mail import MeetingMailer

# Watchdog imports for file monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Load environment variables
load_dotenv()

# --- Initialize custom processors ---
matcher = Matcher(api_key=os.getenv("GeminiAPI"))
processor = TranscriptProcessor(openai_api_key=os.getenv("OpenAIAPI"))
DB_URL = os.getenv("MongoDB")
ACCESS_TOKEN = os.getenv("GraphToken")
mailer = MeetingMailer(DB_URL, "meeting_db", "meeting_records", ACCESS_TOKEN)

Processor = MeetingProcessor(
    db_url=DB_URL,
    db_name="meeting_db",
    collection_name="meeting_records",
    access_token=ACCESS_TOKEN
)

# --- FastAPI App Setup ---
app = FastAPI()

# Pydantic request models
class MatchingRequest(BaseModel):
    names_list: list[str]
    attendees_list: list[str]

class UpdateMOMRequest(BaseModel):
    meeting_id: str
    mom_data: dict

class Attendee(BaseModel):
    name: str
    email: str

class SendMOMRequest(BaseModel):
    meeting_id: str
    attendees: list[Attendee]

# --- Transcript & Video Processing Functions ---
def transcribe_audio(audio_path: Path) -> Optional[Dict[str, Any]]:
    """
    Transcribe the given .wav audio file using Deepgram's API.
    Returns a dictionary with transcript details (utterances and paragraph transcript).
    """
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource  # local import
    api_key = os.environ.get('DEEPGRAM_API_KEY')
    if not api_key:
        raise ValueError("Please set the DEEPGRAM_API_KEY environment variable.")
    try:
        deepgram = DeepgramClient(api_key)
        with open(audio_path, 'rb') as audio_file:
            audio_content = audio_file.read()
        payload: FileSource = {
            'buffer': audio_content,
            'mimetype': 'audio/wav'
        }
        options = PrerecordedOptions(
            model='nova-3',
            language='en',
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            diarize=True,
            utterances=True,
            utt_split=0.5,
            filler_words=False,
            profanity_filter=False
        )
        response = deepgram.listen.rest.v('1').transcribe_file(payload, options)
        print("Deepgram response:", response)
        if response and hasattr(response, 'results'):
            transcript_details = {
                'utterances': [],
                'paragraph_transcript': ""
            }
            # Use the paragraphs transcript if available
            channel = response.results.channels[0]
            alternative = channel.alternatives[0]
            if hasattr(alternative, 'paragraphs'):
                paragraphs_obj = alternative.paragraphs
                if hasattr(paragraphs_obj, 'transcript'):
                    transcript_details['paragraph_transcript'] = paragraphs_obj.transcript
            # Save utterances if available
            if hasattr(response.results, 'utterances'):
                transcript_details['utterances'] = response.results.utterances
            return transcript_details
        else:
            print("No transcript found.")
            return None
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_audio(video_path: Path) -> Path:
    """
    Extracts audio from the video file using ffmpeg.
    The resulting .wav file is created in the same directory as the video.
    """
    try:
        import ffmpeg
        audio_path = video_path.parent / f"{video_path.stem}_audio.wav"
        (
            ffmpeg
            .input(str(video_path))
            .output(str(audio_path), acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return audio_path
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise ValueError(f"Failed to extract audio from {video_path}")

def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to a mm:ss formatted string."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02}"

def group_utterances_with_timestamps(utterances: List) -> List[Dict[str, Any]]:
    """
    Group consecutive utterances by the same speaker.
    Each group includes the start time (from the first utterance in that group).
    Expects each utterance as an object with attributes 'speaker', 'transcript', and 'start'.
    """
    if not utterances:
        return []
    grouped = []
    current_speaker = getattr(utterances[0], 'speaker', 'Unknown')
    current_text = [getattr(utterances[0], 'transcript', '')]
    current_timestamp = getattr(utterances[0], 'start', 0.0)
    for utterance in utterances[1:]:
        speaker = getattr(utterance, 'speaker', 'Unknown')
        text = getattr(utterance, 'transcript', '')
        if speaker == current_speaker:
            current_text.append(text)
        else:
            grouped.append({
                "speaker": current_speaker,
                "timestamp": seconds_to_timestamp(current_timestamp),
                "text": " ".join(current_text)
            })
            current_speaker = speaker
            current_text = [text]
            current_timestamp = getattr(utterance, 'start', 0.0)
    grouped.append({
        "speaker": current_speaker,
        "timestamp": seconds_to_timestamp(current_timestamp),
        "text": " ".join(current_text)
    })
    return grouped

def create_transcript_from_utterances(grouped_segments: List[Dict[str, Any]]) -> str:
    """
    Create a formatted transcript from grouped utterances.
    Each line follows the format: "Speaker X (mm:ss): text"
    """
    if not grouped_segments:
        return "No transcript available."
    transcript_lines = [
        f"Speaker {seg['speaker']} ({seg['timestamp']}): {seg['text']}"
        for seg in grouped_segments
    ]
    return "\n".join(transcript_lines)

def save_transcript_from_utterances(transcript_details: Dict[str, Any], video_path: Path) -> Path:
    """
    Generate a transcript file from utterances (with timestamps) and save it in the video's folder.
    The transcript file is named after the video (e.g. videoName_transcript.txt).
    """
    transcript_path = video_path.parent / f"{video_path.stem}_transcript.txt"
    utterances = transcript_details.get('utterances', [])
    grouped_segments = group_utterances_with_timestamps(utterances)
    formatted_transcript = create_transcript_from_utterances(grouped_segments)
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(formatted_transcript)
    return transcript_path

def process_video(video_path: Path):
    """
    Process a video file: extract audio, transcribe it, save the transcript,
    delete the intermediate .wav file, and move the video to a Processed folder.
    Then automatically trigger meeting processing using the generated transcript file.
    """
    print(f"Processing video: {video_path}")
    try:
        # Extract audio from the video file
        audio_path = extract_audio(video_path)
        print(f"Extracted audio to: {audio_path}")

        # Transcribe the audio via Deepgram
        transcript_details = transcribe_audio(audio_path)
        if transcript_details:
            transcript_path = save_transcript_from_utterances(transcript_details, video_path)
            print(f"Transcript saved to: {transcript_path}")
            # Auto-trigger meeting processing with the generated transcript file
            auto_process_meeting(transcript_path)
        else:
            print("Transcription failed.")

        # Delete the intermediate audio file
        if audio_path.exists():
            os.remove(audio_path)
            print(f"Deleted intermediate audio file: {audio_path}")

        # Move processed video to a "Processed" folder
        processed_dir = video_path.parent / "Processed"
        processed_dir.mkdir(exist_ok=True)
        destination = processed_dir / video_path.name
        shutil.move(str(video_path), str(destination))
        print(f"Moved processed video to: {destination}")

    except Exception as e:
        print(f"An error occurred while processing {video_path}: {e}")

# def auto_process_meeting(transcript_file: Path):
#     """
#     Auto-trigger meeting processing using the generated transcript file.
#     This function replaces the hard-coded transcript filename with the actual file.
#     """
#     try:
#         # Use the transcript file from video processing
#         meeting_id, chat_id, event = Processor.get_latest_meeting_info()
#         if not chat_file.exists():
#             msg = Processor.extract_teams_chat_messages(chat_id)
#             if msg:
#                 start_time = event["start"]["dateTime"]
#                 start_time_str = datetime.datetime.fromisoformat(
#                     start_time.replace('Z', '+00:00')
#                 ).strftime("%Y%m%d_%H%M%S")
#                 # Define a new chat filename based on the meeting start time.
#                 chat_file = Path(chat_file.parent) / f"chat_{start_time_str}.txt"
#                 Processor.save_to_text_file(msg, str(chat_file))
#             else:
#                 chat_file = chat_file.with_name("chat_default.txt")
#                 with open(chat_file, 'w', encoding='utf-8') as f:
#                     f.write("No chat messages found.")
#                 print("No chat messages found. Default chat file created.")
#
#         # segments = processor.parse_vtt(str(transcript_file))
#         #
#         # if not segments:
#         #     print("No valid segments found in transcript.")
#         #     return
#         # grouped_segments = processor.group_segments(segments)
#         # transcript = processor.create_transcript(grouped_segments)
#         transcript = processor.combine_transcript_and_chats(str(transcript_file), str(chat_file))
#         analysis = processor.get_chatgpt_response(transcript)
#         extracted_info = json.loads(analysis)
#
#         meeting_subject = event.get('subject', 'Unnamed Meeting')
#         attendees = Processor.extract_attendees(event)
#         meeting_record = {
#             "meeting_id": meeting_id,
#             "meeting_subject": meeting_subject,
#             "meeting_time": datetime.datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '+00:00')),
#             "attendees": attendees,
#             "mom_data": extracted_info,
#             "processed_at": datetime.datetime.now()
#         }
#         result_insert = Processor.meeting_records.insert_one(meeting_record)
#         print(f"Auto-processed meeting. Stored meeting data with ID: {result_insert.inserted_id}")
#     except Exception as e:
#         print(f"Error during auto meeting processing: {e}")
def auto_process_meeting(transcript_file: Path):
    """
    Auto-trigger meeting processing using the generated transcript file.
    This function creates the chat file in the same directory as the transcript file.
    """
    try:
        # Retrieve meeting information from Teams
        meeting_id, chat_id, event = Processor.get_latest_meeting_info()

        # Define the chat file path in the transcript file's directory.
        # This is our intended destination for chat messages.
        chat_file = transcript_file.parent / "chat.txt"

        # If the chat file does not exist, attempt to extract Teams chat messages.
        if not chat_file.exists():
            msg = Processor.extract_teams_chat_messages(chat_id)
            if msg:
                start_time = event["start"]["dateTime"]
                start_time_str = datetime.datetime.fromisoformat(
                    start_time.replace('Z', '+00:00')
                ).strftime("%Y%m%d_%H%M%S")
                # Save the chat file in the transcript file's directory using a name based on meeting start time.
                chat_file = transcript_file.parent / f"chat_{start_time_str}.txt"
                Processor.save_to_text_file(msg, str(chat_file))
            else:
                # No chat messages found; create a default chat file in the transcript directory.
                chat_file = transcript_file.parent / "chat_default.txt"
                with open(chat_file, 'w', encoding='utf-8') as f:
                    f.write("No chat messages found.")
                print("No chat messages found. Default chat file created in transcript directory.")

        # Combine transcript and chat file.
        combined_text = processor.combine_transcript_and_chats(str(transcript_file), str(chat_file))
        analysis = processor.get_chatgpt_response(combined_text)
        extracted_info = json.loads(analysis)

        meeting_subject = event.get('subject', 'Unnamed Meeting')
        attendees = Processor.extract_attendees(event)
        meeting_record = {
            "meeting_id": meeting_id,
            "meeting_subject": meeting_subject,
            "meeting_time": datetime.datetime.fromisoformat(
                event["start"]["dateTime"].replace('Z', '+00:00')
            ),
            "attendees": attendees,
            "mom_data": extracted_info,
            "processed_at": datetime.datetime.now()
        }
        result_insert = Processor.meeting_records.insert_one(meeting_record)
        print(f"Auto-processed meeting. Stored meeting data with ID: {result_insert.inserted_id}")
    except Exception as e:
        print(f"Error during auto meeting processing: {e}")

# --- Watchdog File Monitor ---
class VideoEventHandler(FileSystemEventHandler):
    """Watches the Meetings folder for new video files and triggers processing."""
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
                # Delay briefly to ensure file write completion
                time.sleep(2)
                process_video(file_path)

def start_file_monitor():
    """Start monitoring the Meetings folder for new video files."""
    meetings_path = Path.home() / 'Downloads' / 'Meetings'
    if not meetings_path.exists():
        print("Meetings directory not found.")
        return
    event_handler = VideoEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(meetings_path), recursive=False)
    observer.start()
    print(f"Monitoring {meetings_path} for new video files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# --- FastAPI Endpoints ---
@app.get("/process")
def process_transcript(
        transcript_filename: str = Query(..., description="The transcript .txt file in the same directory"),
        chat_filename: str = Query(..., description="The chat .txt file in the same directory")
):
    """
    Combines the provided transcript and chat files (removing timestamps from the transcript)
    and then sends the combined text to OpenAI. Returns the combined transcript and extracted info.
    """
    try:
        combined_text = processor.combine_transcript_and_chats(transcript_filename, chat_filename)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    analysis = processor.get_chatgpt_response(combined_text)
    try:
        extracted_info = json.loads(analysis)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from OpenAI.")

    return {"transcript": combined_text, "extracted_info": extracted_info}


@app.post("/match")
def match_names(request: MatchingRequest):
    result_text = matcher.match_names(request.names_list, request.attendees_list)
    return {"result": result_text}

@app.get("/process_meeting")
def process_meeting():
    try:
        meeting_id, chat_id, event = Processor.get_latest_meeting_info()
        meeting_subject = event.get('subject', 'Unnamed Meeting')
        print(f"Processing meeting: {meeting_subject} {meeting_id}")
        existing_record = Processor.meeting_records.find_one({"meeting_id": meeting_id})
        if existing_record:
            print("Found cached meeting data in MongoDB")
            return {"mom_data": existing_record["mom_data"]}
        attendees = Processor.extract_attendees(event)
        messages = Processor.extract_teams_chat_messages(chat_id)
        if messages:
            start_time = event["start"]["dateTime"]
            start_time_str = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime("%Y%m%d_%H%M%S")
            chat_filename = f"chat_{start_time_str}.txt"
            Processor.save_to_text_file(messages, chat_filename)
        else:
            print("No chat messages found.")
        final_items, mom_data = Processor.process_transcript("MOMTesting.vtt", attendees)
        meeting_record = {
            "meeting_id": meeting_id,
            "meeting_subject": meeting_subject,
            "meeting_time": datetime.datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '+00:00')),
            "attendees": attendees,
            "mom_data": mom_data,
            "processed_at": datetime.datetime.now()
        }
        result_insert = Processor.meeting_records.insert_one(meeting_record)
        print(f"Stored meeting data in MongoDB with ID: {result_insert.inserted_id}")
        return {"mom_data": mom_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update_mom")
def update_mom(data: UpdateMOMRequest):
    try:
        updated_record = Processor.update_mom(data.meeting_id, data.mom_data)
        return {"updated_record": updated_record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_mom")
def send_mom_endpoint(request: SendMOMRequest, background_tasks: BackgroundTasks):
    attendees = [att.dict() for att in request.attendees]
    background_tasks.add_task(mailer.process_and_send_mom, request.meeting_id, attendees)
    return {"message": "MOM processing, email sending, and OneDrive upload initiated via Graph API."}

# --- Startup Event to Launch File Monitor in Background ---
@app.on_event("startup")
def startup_event():
    monitor_thread = threading.Thread(target=start_file_monitor, daemon=True)
    monitor_thread.start()
    print("File monitor thread started.")

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
