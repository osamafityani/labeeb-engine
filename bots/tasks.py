from celery import shared_task
import time
from .utils import (create_bot, remove_bot, start_recording, stop_recording,
                    get_meeting, download_recording)
from transcription.models import Project


@shared_task
def record_meeting(meeting_url, bot_name="AI", project_id=None):
    """
    Main entry point for the meeting bot automation program.
    Creates a bot for a meeting and lets it record until it automatically leaves based on meeting conditions.
    
    Args:
        meeting_url (str): URL of the meeting to record
        bot_name (str): Name of the bot (default: "Faris2")
        project_id (int): ID of the project the recording belongs to
    """
    # Get project objects
    project = None
            
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            print(f"Project with id {project_id} not found")

    # Create a bot and handle the response
    result = create_bot(meeting_url, bot_name)

    if result["status"] == "success":
        bot_id = result["data"].get("id")
        print("Bot created successfully with ID:", bot_id)

        # Start recording the meeting
        record_result = start_recording(bot_id)
        if record_result["status"] == "success":
            print("Recording started successfully.")
            print("Waiting for meeting to complete...")
        else:
            print("Failed to start recording:", record_result["message"])
            # If recording fails, remove the bot immediately
            remove_bot(bot_id)
            return

        # Keep checking the meeting status until the bot leaves or the meeting ends
        recording_completed = False
        while True:
            meeting_result = get_meeting(bot_id)
            if meeting_result["status"] == "success":
                meeting_data = meeting_result["data"]
                
                # Get the latest status from status_changes
                status_changes = meeting_data.get("status_changes", [])
                current_status = status_changes[-1] if status_changes else {"code": "unknown"}
                status_code = current_status.get("code", "unknown")
                sub_code = current_status.get("sub_code")
                
                print(f"Current meeting status: {status_code} (sub_code: {sub_code})")
                
                # Check if the bot has left the meeting
                if status_code in ["call_ended", "done"]:
                    print(f"Bot has left the meeting. Status: {status_code}")
                    if sub_code:
                        print(f"Sub code: {sub_code}")
                    recording_completed = True
                    break
                elif status_code == "recording_done":
                    print("Recording is ready for download")
                    recording_completed = True
                    break
                elif status_code == "failed":
                    print(f"Recording failed. Error: {meeting_data.get('error', 'Unknown error')}")
                    break
                
                time.sleep(30)  # Check every 30 seconds
            else:
                print("Failed to get meeting status:", meeting_result["message"])
                time.sleep(30)
                continue

        # Once the bot has left, wait for the video URL
        if recording_completed:
            print("Waiting for video URL to become available...")
            count = 0
            while count < 20:  # Try for 10 minutes (20 * 30 seconds)
                meeting_result = get_meeting(bot_id)
                if meeting_result["status"] == "success":
                    meeting_data = meeting_result["data"]
                    video_url = meeting_data.get("video_url")
                    
                    # Also check recording status
                    recordings = meeting_data.get("recordings", [])
                    latest_recording = recordings[-1] if recordings else {}
                    recording_status = latest_recording.get("status", {}).get("code") if latest_recording else None
                    
                    print(f"Recording status: {recording_status}")
                    print(f"Video URL status: {'Available' if video_url else 'Not available yet'}")
                    
                    if video_url and recording_status == "done":
                        print("Video URL found:", video_url)
                        # Pass project objects to download_recording
                        download_recording(video_url, project=project)
                        print("Recording downloaded and processed successfully")
                        break
                    time.sleep(30)
                    count += 1
                else:
                    print("Failed to get video URL:", meeting_result["message"])
                    time.sleep(30)
                    count += 1

            if count >= 20:
                print("Timeout waiting for video URL after 10 minutes")
        else:
            print("Recording was not completed successfully, skipping video download")

    else:
        print("Failed to create bot:", result["message"])
