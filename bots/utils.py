import os
import requests
import ssl
from dotenv import load_dotenv
from .env_loader import get_env_variable


def create_bot(meeting_url: str, bot_name: str):
    """
    Creates a bot and assigns it to a meeting.

    Args:
        meeting_url (str): The URL of the meeting.
        bot_name (str): The name of the bot to be created.

    Returns:
        dict: A dictionary containing the response data or error message.
    """
    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = get_env_variable("API_KEY")
    api_base_url = get_env_variable("API_BASE_URL")

    if not api_key:
        raise ValueError("API_KEY is not set in the environment variables.")

    # Display OpenSSL version for debugging (optional)
    print(f"Using OpenSSL version: {ssl.OPENSSL_VERSION}")

    # Define API endpoint and headers
    url = f"{api_base_url}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {api_key}",
    }

    # Define request body
    body = {
        "meeting_url": meeting_url,
        "bot_name": bot_name,
    }

    try:
        # Send POST request
        response = requests.post(api_base_url, headers=headers, json=body)
        response.raise_for_status()  # Raise an error for bad status codes

        # Return success response
        return {"status": "success", "data": response.json()}

    except requests.exceptions.RequestException as e:
        # Handle and return error response
        return {"status": "error", "message": str(e)}


def remove_bot(bot_id: str):
    """
    Removes a bot from a call by making a POST request to the leave call API.

    Args:
        bot_id (str): The unique ID of the bot to be removed.

    Returns:
        dict: A dictionary containing the response data or error message.
    """
    # Load API key and base URL from environment variables
    api_key = get_env_variable("API_KEY")
    api_base_url = get_env_variable("API_BASE_URL")

    # Construct the URL for the leave call endpoint
    url = f"{api_base_url}{bot_id}/leave_call/"
    headers = {
        "accept": "application/json",
        "Authorization": f"Token {api_key}",
    }

    try:
        # Send POST request
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        # Return success response
        return {"status": "success", "data": response.json()}

    except requests.exceptions.RequestException as e:
        # Handle and return error response
        return {"status": "error", "message": str(e)}


def start_recording(bot_id: str):
    """
    Starts recording a meeting using the specified bot.

    Args:
        bot_id (str): The unique ID of the bot that will record the meeting.

    Returns:
        dict: A dictionary containing the response data or an error message.
    """
    api_key = get_env_variable("API_KEY")
    api_base_url = get_env_variable("API_BASE_URL")

    url = f"{api_base_url}{bot_id}/start_recording/"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {api_key}",
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def stop_recording(bot_id: str):
    """
    Stops recording a meeting using the specified bot.

    Args:
        bot_id (str): The unique ID of the bot that is recording the meeting.

    Returns:
        dict: A dictionary containing the response data or an error message.
    """
    api_key = get_env_variable("API_KEY")
    api_base_url = get_env_variable("API_BASE_URL")

    url = f"{api_base_url}{bot_id}/stop_recording/"

    headers = {
        "accept": "application/json",
        "Authorization": f"Token {api_key}",
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def get_meeting(bot_id: str):
    """
    Retrieves the meeting details for a specific bot.

    Args:
        bot_id (str): The unique ID of the bot.

    Returns:
        dict: A dictionary containing the meeting details or an error message.
    """
    api_key = get_env_variable("API_KEY")
    api_base_url = get_env_variable("API_BASE_URL")

    url = f"{api_base_url}{bot_id}/"

    headers = {
        "accept": "application/json",
        "Authorization": f"Token {api_key}",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def download_recording(recording_url):
    # URL of the file to download

    # Output file path
    output_file = "downloaded_video.mp4"

    try:
        # Send GET request to the URL
        response = requests.get(recording_url, stream=True)
        response.raise_for_status()  # Check for HTTP request errors

        # Write the file to disk in chunks
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):  # 8 KB chunks
                file.write(chunk)

        print(f"File downloaded successfully as '{output_file}'")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
