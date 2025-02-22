from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from interface.utils import answer_query


@csrf_exempt
@api_view(['POST'])
def ask(request):
    # Check if the request body contains the expected data
    if 'query' not in request.data:
        return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Get the string from the request body
    query = request.data['query']
    message, result = answer_query(query)

    # Optionally, you can process the string or do something with it
    # For example, you can return the string back in the response
    return Response({"answer": message}, status=status.HTTP_200_OK)
