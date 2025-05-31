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


def search_similar_embeddings(query_embedding, user_team_id=None):
    """
    Finds the most similar transcriptions and returns their text content.
    Filters by user's team if team_id is provided.
    """
    print(query_embedding)
    
    if user_team_id:
        sql_query = """
            SELECT m.transcription_file
            FROM transcription_meeting m
            JOIN transcription_project p ON m.project_id = p.id
            WHERE p.team_account_id = %s
            ORDER BY m.embeddings <-> %s::vector
            LIMIT 5;
        """
        params = [user_team_id, query_embedding]
    else:
        sql_query = """
            SELECT transcription_file
            FROM transcription_meeting
            ORDER BY embeddings <-> %s::vector
            LIMIT 5;
        """
        params = [query_embedding]

    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        results = cursor.fetchall()

    # Read the contents of each transcription file
    transcription_texts = []
    print(results)
    for (file_path,) in results:
        if file_path:  # Ensure file exists
            try:
                with open("media/" + file_path, "r", encoding="utf-8") as file:
                    transcription_texts.append(file.read())
            except Exception as e:
                transcription_texts.append(f"Error reading {file_path}: {e}")

    return transcription_texts  # List of retrieved transcription texts


def strings_ranked_by_relatedness(
    client,
    query: str,
    user_team_id: int = None,
    top_n: int = 1
):
    """
    Returns a list of strings and relatednesses, sorted from most related to least.
    Filters by user's team if team_id is provided.
    """
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings = search_similar_embeddings(query_embedding, user_team_id)
    return strings[:top_n]


def num_tokens(text: str, model: str = GPT_MODELS[0]) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    client,
    query: str,
    user_team_id: int = None,
    model: str = GPT_MODELS[0],
    token_budget: int = 4096 - 500,
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings = strings_ranked_by_relatedness(client, query, user_team_id)
    
    if not strings:
        return (
            "You are a helpful assistant that ALWAYS responds in Arabic. The user has asked a question about their meeting transcripts, "
            "but I couldn't find any relevant meetings in their history. "
            "Please respond with this message in Arabic: 'عذراً، لم أتمكن من العثور على أي معلومات ذات صلة في سجل اجتماعات فريقك. "
            "قد يكون ذلك بسبب: \n"
            "١. لم يتم تسجيل الاجتماع بعد\n"
            "٢. لم تتم مناقشة الموضوع الذي تسأل عنه في أي من الاجتماعات المسجلة\n"
            "٣. قد يكون الاجتماع في مساحة عمل فريق آخر\n\n"
            "يرجى المحاولة:\n"
            "- إعادة صياغة سؤالك\n"
            "- التحقق من تسجيل الاجتماع\n"
            "- التأكد من أنك في مساحة عمل الفريق الصحيح'\n\n"
            f"Question: {query}"
        )
    
    introduction = 'You are a helpful assistant that ALWAYS responds in Arabic. Use the below minutes of meetings to answer the subsequent question. If the answer cannot be found in the summaries, respond in Arabic with: "عذراً، لم أتمكن من العثور على إجابة محددة لسؤالك في محاضر الاجتماعات المتوفرة. هل يمكنك إعادة صياغة سؤالك أو تقديم المزيد من التفاصيل؟"'
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
    user_team_id: int = None,
    model: str = GPT_MODELS[0],
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(client, query, user_team_id, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You are an assistant that ALWAYS responds in Arabic. You answer questions about the minutes of meetings. Even if the question is in English, you must respond in Arabic."},
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
