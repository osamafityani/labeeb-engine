from pyannote.audio import Pipeline
import os
from openai import OpenAI
import pandas as pd
import tiktoken


def split_audio_by_speaker(audio_path, diarization_pipeline):
    """
    Perform speaker diarization to detect speakers and their timestamps.

    :param audio_path: Path to the audio file.
    :param diarization_pipeline: Pre-loaded Pyannote pipeline for diarization.
    :return: List of (speaker, start_time, end_time).
    """
    diarization_result = diarization_pipeline({'uri': 'audio', 'audio': audio_path})
    speaker_segments = []

    for segment, track, speaker in diarization_result.itertracks(yield_label=True):
        speaker_segments.append((speaker, segment.start, segment.end))

    return speaker_segments


def transcribe_audio(audio_path):
    """
    Perform speech-to-text transcription using OpenAI Whisper API.

    :param audio_path: Path to the audio file.
    :return: Transcription segments with timestamps.
    """

    client = OpenAI()
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["segment"]
    )

    # Process the response to extract segments and timestamps
    transcription_segments = []
    for segment in transcript.segments:
        transcription_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })

    return transcription_segments


def match_speakers_to_transcript(transcription_segments):
    """
    Match speakers to the transcript using timestamps.

    :param speaker_segments: List of (speaker, start_time, end_time).
    :param transcription_segments: Transcription segments with timestamps.
    :return: Combined transcript in "speaker: text" format.
    """
    final_transcript = []

    for speaker, start, end in speaker_segments:
        speaker_text = []

        for segment in transcription_segments:
            # Check if the transcription segment is within the speaker's time range
            if start <= segment['start'] <= end or start <= segment['end'] <= end:
                speaker_text.append(segment['text'])

        # Join speaker text into one chunk
        if speaker_text:
            combined_text = " ".join(speaker_text)
            final_transcript.append(f"{speaker}: {combined_text}")

    return "\n".join(final_transcript)


def transcription_pipeline(audio_path):
    # Load the diarization pipeline
    # diarization_pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization')

    # Step 1: Perform speaker diarization
    print("Performing speaker diarization...")
    # speaker_segments = split_audio_by_speaker(audio_path, diarization_pipeline)

    # Step 2: Perform speech-to-text transcription
    print("Transcribing audio...")
    transcription_segments = transcribe_audio(audio_path)

    # Step 3: Match speakers with transcript
    print("Matching speakers with transcript...")
    # return the final transcript
    return " \n ".join([seg['text'] for seg in transcription_segments])


def summarize(content, project=None):
    client = OpenAI()
    
    # Build project details string if project exists
    project_details = ""
    if project:
        project_details = f"""
Project Information:
- Title: {project.title}
- Description: {project.description}
- Team: {project.team.name if project.team else 'No team assigned'}
- Start Date: {project.start_date}
- End Date: {project.end_date}
"""
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""You are responsible for documenting meetings. You will be given a transcript for a meeting and project details, and you should write a structured minutes of meeting. Please include the following information in your report, if any information is not available, write "Not mentioned":

{project_details}
1. Meeting Name: (Try to deduce this from the transcript)
2. Related Project: (Use the project information provided above)
3. Date:
4. Time:
5. Participants:
6. Meeting Transcript: (A detailed restructured transcript of everything discussed, mention as many details as possible)
7. Action Plan: (List any action items, tasks, or next steps mentioned in the meeting)

Please maintain this exact structure in your response. The report should be clear and professional. Meetings and reports are in Arabic."""},
            {
                "role": "user",
                "content": content
            }
        ]
    )
    summary = completion.choices[0].message.content
    
    # Extract meeting name from the summary
    meeting_name = "Untitled Meeting"
    for line in summary.split('\n'):
        if line.startswith('1. Meeting Name:'):
            name = line.replace('1. Meeting Name:', '').strip()
            if name.lower() != 'not mentioned':
                meeting_name = name
            break
    
    return summary, meeting_name


def num_tokens(text: str, model: str = 'gpt-4o-mini') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def read_txt_files(file_paths):
    """
    Reads a list of .txt files and returns their contents as a list of strings.

    Args:
        file_paths (list): List of file paths to .txt files.

    Returns:
        list: A list where each element is the content of a file as a string.
    """
    file_contents = []
    for file_path in file_paths:
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents.append(file.read())
        else:
            print(f"Skipping invalid file: {file_path}")
    return file_contents


def halved_by_delimiter(string: str, delimiter: str = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = num_tokens(string)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]


def truncated_string(
    string: str,
    model: str,
    max_tokens: int,
    print_warning: bool = True,
) -> str:
    """Truncate a string to a maximum number of tokens."""
    encoding = tiktoken.encoding_for_model(model)
    encoded_string = encoding.encode(string)
    truncated_string = encoding.decode(encoded_string[:max_tokens])
    if print_warning and len(encoded_string) > max_tokens:
        print(f"Warning: Truncated string from {len(encoded_string)} tokens to {max_tokens} tokens.")
    return truncated_string


def split_strings(
    string: tuple[list[str], str],
    max_tokens: int = 1000,
    model: str = 'gpt-4o-mini',
    max_recursion: int = 5,
) -> list[str]:
    """
    Split a subsection into a list of subsections, each with no more than max_tokens.
    Each subsection is a tuple of parent titles [H1, H2, ...] and text (str).
    """

    num_tokens_in_string = num_tokens(string)
    # if length is fine, return string
    if num_tokens_in_string <= max_tokens:
        return [string]
    # if recursion hasn't found a split after X iterations, just truncate
    elif max_recursion == 0:
        return [truncated_string(string, model=model, max_tokens=max_tokens)]
    # otherwise, split in half and recurse
    else:
        for delimiter in ["\n\n", "\n", ". "]:
            left, right = halved_by_delimiter(string, delimiter=delimiter)
            if left == "" or right == "":
                # if either half is empty, retry with a more fine-grained delimiter
                continue
            else:
                # recurse on each half
                results = []
                for half in [left, right]:
                    half_strings = split_strings(
                        half,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    results.extend(half_strings)
                return results
    # otherwise no split was found, so just truncate (should be very rare)
    return [truncated_string(string, model=model, max_tokens=max_tokens)]


def embedding_pipeline(content):
    client = OpenAI()
    MAX_TOKENS = 1600

    strings = split_strings(content, max_tokens=MAX_TOKENS)

    print(f"split into {len(strings)} strings.")

    EMBEDDING_MODEL = "text-embedding-3-small"
    BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request

    embeddings = []
    for batch_start in range(0, len(strings), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = strings[batch_start:batch_end]
        print(f"Batch {batch_start} to {batch_end - 1}")
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)


    # df = pd.DataFrame({"text": strings, "embedding": embeddings})
    #
    # SAVE_PATH = "data/meeting.csv"
    #
    # df.to_csv(SAVE_PATH, index=False)

    return embeddings[0]


