from celery import shared_task
import time
from .utils import (create_bot, remove_bot, start_recording, stop_recording,
                    get_meeting, download_recording)


@shared_task
def record_meeting(meeting_url, bot_name="Faris2"):
    """
        Main entry point for the meeting bot automation program.
        Creates a bot for a meeting and removes it after 30 seconds.
        """
    # Example data (can be replaced with user input later)

    # Create a bot and handle the response
    result = create_bot(meeting_url, bot_name)

    if result["status"] == "success":
        bot_id = result["data"].get("id")
        # print("Bot created successfully:", result["data"])
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

        # Wait for 30 seconds before removing the bot
        count = 0
        while count < 10:

            # Retrieve and display the meeting details
            meeting_result = get_meeting(bot_id)
            if meeting_result["status"] == "success":
                print("Meeting details retrieved successfully.\n\n")
                meeting_data = meeting_result["data"]
                if not meeting_data["video_url"]:
                    time.sleep(30)
                    continue
                print("\n\nMeeting URL: ", meeting_data["video_url"])
                download_recording(meeting_data["video_url"])
                break
            else:
                print("Failed to retrieve meeting details:",
                      meeting_result["message"])
                time.sleep(30)

    else:
        print("Failed to create bot:", result["message"])
