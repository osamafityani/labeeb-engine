import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
from scipy import spatial  # for calculating vector similarities for search
from django.db import connection


# create a list of models
GPT_MODELS = ["gpt-4o", "gpt-4o-mini"]
# models
EMBEDDING_MODEL = "text-embedding-3-small"


def search_similar_embeddings(query_embedding):
    """Finds the most similar transcriptions and returns their text content."""

    sql_query = """
        SELECT transcription_file
        FROM transcription_meeting
        ORDER BY embeddings <-> %s::vector
        LIMIT 5;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [query_embedding])
        results = cursor.fetchall()

    # Read the contents of each transcription file
    transcription_texts = []
    for (file_path,) in results:
        if file_path:  # Ensure file exists
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    transcription_texts.append(file.read())
            except Exception as e:
                transcription_texts.append(f"Error reading {file_path}: {e}")

    return transcription_texts  # List of retrieved transcription texts


def strings_ranked_by_relatedness(
    client,
    query: str,
    top_n: int = 1
):
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings = search_similar_embeddings(query_embedding)
    return strings[:top_n]


def num_tokens(text: str, model: str = GPT_MODELS[0]) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    client,
    query: str,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings = strings_ranked_by_relatedness(client, query)
    introduction = 'Use the below minutes of meetings to answer the subsequent question. If the answer cannot be found in the summaries, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nMinutes of Meeting:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def ask(
    client,
    query: str,
    model: str = GPT_MODELS[0],
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(client, query, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about the minutes of meetings"},
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message


def answer_query(query):
    client = OpenAI()

    return ask(client, query, model=GPT_MODELS[1])
