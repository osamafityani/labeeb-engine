from celery import shared_task
import time
from .utils import (create_bot, remove_bot, start_recording, stop_recording,
                    get_meeting, download_recording)
from teams.models import Team
from transcription.models import Project


@shared_task
def record_meeting(meeting_url, bot_name="Faris2", team_id=None, project_id=None):
    """
    Main entry point for the meeting bot automation program.
    Creates a bot for a meeting and removes it after recording is complete.
    
    Args:
        meeting_url (str): URL of the meeting to record
        bot_name (str): Name of the bot (default: "Faris2")
        team_id (int): ID of the team the recording belongs to
        project_id (int): ID of the project the recording belongs to
    """
    # Get team and project objects
    team = None
    project = None
    
    if team_id:
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            print(f"Team with id {team_id} not found")
            
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            print(f"Project with id {project_id} not found")

    # Create a bot and handle the response
    result = create_bot(meeting_url, bot_name)

    if result["status"] == "success":
        bot_id = result["data"].get("id")
        print("Bot created successfully.\n\n")

        # Start recording the meeting
        record_result = start_recording(bot_id)
        if record_result["status"] == "success":
            print("Recording started successfully.\n\n")
        else:
            print("Failed to start recording:", record_result["message"])
            # If recording fails, remove the bot immediately
            remove_bot(bot_id)
            return

        # Wait for 30 seconds before removing the bot
        print("Waiting for 30 seconds before removing the bot...\n\n")
        time.sleep(60)

        # Stop recording the meeting
        stop_result = stop_recording(bot_id)
        if stop_result["status"] == "success":
            print("Recording stopped successfully.\n\n")
        else:
            print("Failed to stop recording:", stop_result["message"])

        # Remove the bot
        remove_result = remove_bot(bot_id)
        if remove_result["status"] == "success":
            print("Bot removed successfully.\n\n")
        else:
            print("Failed to remove bot:", remove_result["message"])

        # Wait for video URL to be available
        count = 0
        while count < 10:
            # Retrieve and display the meeting details
            meeting_result = get_meeting(bot_id)
            if meeting_result["status"] == "success":
                print("Meeting details retrieved successfully.\n\n")
                meeting_data = meeting_result["data"]
                if not meeting_data["video_url"]:
                    time.sleep(30)
                    count += 1
                    continue
                print("\n\nMeeting URL: ", meeting_data["video_url"])
                # Pass team and project objects to download_recording
                download_recording(meeting_data["video_url"], team=team, project=project)
                break
            else:
                print("Failed to retrieve meeting details:", meeting_result["message"])
                time.sleep(30)
                count += 1

    else:
        print("Failed to create bot:", result["message"])
