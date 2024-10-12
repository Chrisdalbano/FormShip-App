# backend/api/views.py

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question, SharedQuiz, UserResult
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    SharedQuizSerializer,
    UserResultSerializer,
)
import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
import json

# Instantiate the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def parse_quiz_text(generated_text, quiz_type):
    """
    Parses the generated text from OpenAI into quiz questions.

    Args:
        generated_text (str): JSON formatted string of questions.
        quiz_type (str): Type of quiz, e.g. "multiple-choice".

    Returns:
        list: A list of questions dictionaries or None if parsing fails.
    """
    questions = []
    try:
        # Load the generated text as JSON
        data = json.loads(generated_text)
        if quiz_type == "multiple-choice" and "questions" in data:
            for item in data["questions"]:
                questions.append(
                    {
                        "question_text": item["question"],
                        "option_a": item["options"].get("A"),
                        "option_b": item["options"].get("B"),
                        "option_c": item["options"].get("C"),
                        "correct_answer": item["correct_answer"],
                    }
                )
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing quiz text: {e}")
        return None
    return questions if questions else None


@api_view(["GET"])
def list_quizzes(request):
    """
    Lists all quizzes available in the database.
    """
    quizzes = Quiz.objects.all()
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "DELETE"])
def quiz_detail(request, quiz_id):
    """
    Handles GET, PUT, DELETE requests for a single quiz.

    Args:
        request: The HTTP request object.
        quiz_id (int): ID of the quiz to retrieve, update, or delete.

    Returns:
        Response: JSON serialized quiz object or an error message.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "GET":
        # Return the quiz data
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        # Update the quiz details
        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # Delete the quiz
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def create_quiz(request):
    """
    Creates a new quiz by generating questions with OpenAI API.
    """
    try:
        # Get user input from the request
        title = request.data.get("title")
        topic = request.data.get("topic")
        question_count = int(request.data.get("question_count", 5))
        difficulty = request.data.get("difficulty", "easy")
        quiz_type = request.data.get("quiz_type", "multiple-choice")

        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # Generate quiz questions using OpenAI API (ChatCompletion)
        prompt = (
            f"Generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}' as a JSON array. "
            f"Each question should include: 'question', 'options' with keys 'A', 'B', 'C' (optional), and 'correct_answer'. "
            f'Return only valid JSON in the following format: {{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "..."}}, "correct_answer": "..."}}]}}'
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a quiz generator."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        generated_text = response.choices[0].message.content.strip()

        # Parse the generated text to extract questions
        questions = parse_quiz_text(generated_text, quiz_type)

        if not questions:
            raise ValueError("Failed to parse questions from OpenAI response.")

        # Create a new quiz instance
        quiz = Quiz.objects.create(
            title=title,
            topic=topic,
            difficulty=difficulty,
            question_count=question_count,
            quiz_type=quiz_type,
        )

        # Create questions and associate them with the quiz
        for q in questions:
            Question.objects.create(
                quiz=quiz,
                question_text=q["question_text"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q.get("option_c"),
                correct_answer=q["correct_answer"],
            )

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except (APIError, APIConnectionError, RateLimitError) as e:
        # Handle OpenAI API errors
        print(f"OpenAI API Error: {str(e)}")
        return Response(
            {"error": f"OpenAI API error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValueError as e:
        # Handle validation errors
        print(f"Validation Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # General exception for unexpected errors
        print(f"General Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def delete_quiz(request, quiz_id):
    """
    Deletes a quiz by its ID.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        quiz.delete()
        return Response(
            {"message": "Quiz deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def duplicate_quiz(request, quiz_id):
    """
    Duplicates a quiz by its ID.
    """
    try:
        original_quiz = Quiz.objects.get(id=quiz_id)
        original_questions = original_quiz.questions.all()

        duplicated_quiz = Quiz.objects.create(
            title=f"Copy of {original_quiz.title}",
            topic=original_quiz.topic,
            difficulty=original_quiz.difficulty,
            question_count=original_quiz.question_count,
            quiz_type=original_quiz.quiz_type,
        )

        for question in original_questions:
            Question.objects.create(
                quiz=duplicated_quiz,
                question_text=question.question_text,
                option_a=question.option_a,
                option_b=question.option_b,
                option_c=question.option_c,
                correct_answer=question.correct_answer,
            )

        serializer = QuizSerializer(duplicated_quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def share_quiz(request, quiz_id):
    """
    Shares a quiz by creating a shared link.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        shared_quiz = SharedQuiz.objects.create(quiz=quiz)
        serializer = SharedQuizSerializer(shared_quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_quiz(request, quiz_id):
    """
    Fetches a quiz by its ID.

    Args:
        request: The HTTP request object.
        quiz_id (int): ID of the quiz to retrieve.

    Returns:
        Response: JSON serialized quiz object or an error message.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def submit_quiz_results(request):
    """
    Submits quiz results and calculates the user's score.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON serialized user result or an error message.
    """
    try:
        user_name = request.data.get("user_name")
        quiz_id = request.data.get("quiz_id")
        user_answers = request.data.get("user_answers")

        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.questions.all()

        # Calculate the score
        score = 0
        for question in questions:
            user_answer = user_answers.get(str(question.id))
            if user_answer == question.correct_answer:
                score += 1

        # Create UserResult instance
        result = UserResult.objects.create(
            quiz=quiz,
            user_name=user_name,
            score=score,
            total_questions=questions.count(),
        )

        serializer = UserResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_quiz_result(request, result_id):
    """
    Gets the quiz result by result ID.

    Args:
        request: The HTTP request object.
        result_id: ID of the quiz result to retrieve.

    Returns:
        Response: JSON serialized quiz result or an error message.
    """
    try:
        result = UserResult.objects.get(id=result_id)
        serializer = UserResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserResult.DoesNotExist:
        return Response({"error": "Result not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT", "DELETE"])
def question_detail(request, question_id):
    """
    Handles PUT and DELETE requests for a single question.
    """
    question = get_object_or_404(Question, id=question_id)

    if request.method == "PUT":
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def create_question(request, quiz_id):
    """
    Creates a new question for a given quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(quiz=quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
