from django.shortcuts import get_object_or_404
from datetime import datetime
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Group, Quiz, Question, SharedQuiz, UserResult
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    SharedQuizSerializer,
    UserResultSerializer,
    GroupSerializer,
)
import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
import json

# Instantiate the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def parse_quiz_text(generated_text, quiz_type, option_count):
    """
    Parses the generated text from OpenAI into quiz questions.

    Args:
        generated_text (str): JSON formatted string of questions.
        quiz_type (str): Type of quiz, e.g. "multiple-choice".
        option_count (int): Number of options per question.

    Returns:
        list: A list of questions dictionaries or None if parsing fails.
    """
    questions = []
    try:
        # Load the generated text as JSON
        data = json.loads(generated_text)
        if quiz_type == "multiple-choice" and "questions" in data:
            for item in data["questions"]:
                # Extract options dynamically based on option_count
                options = {
                    chr(65 + i): item["options"].get(chr(65 + i), None)
                    for i in range(option_count)
                }

                questions.append(
                    {
                        "question_text": item["question"],
                        "option_a": options.get("A"),
                        "option_b": options.get("B"),
                        "option_c": options.get("C"),
                        "option_d": options.get("D") if option_count > 3 else None,
                        "option_e": options.get("E") if option_count > 4 else None,
                        "correct_answer": item["correct_answer"],
                    }
                )
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing quiz text: {e}")
        return None
    return questions if questions else None


from openai import OpenAI, APIError, APIConnectionError, RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(["POST"])
def create_quiz(request):
    """
    Creates a new quiz by generating questions with OpenAI API or by analyzing user-provided knowledge base.
    """
    try:
        # Extracting fields from request data
        title = request.data.get("title")
        topic = request.data.get("topic")
        question_count = int(request.data.get("question_count", 5))
        option_count = int(request.data.get("option_count", 4))
        difficulty = request.data.get("difficulty", "easy")
        knowledge_base = request.data.get("knowledge_base", None)
        display_results = request.data.get("display_results", True)
        require_password = request.data.get("require_password", False)
        password = request.data.get("password", "")  # Default to empty string if none
        allow_anonymous = request.data.get("allow_anonymous", False)
        require_name = request.data.get("require_name", False)
        is_timed = request.data.get("is_timed", False)
        quiz_time_limit = (
            int(request.data.get("quiz_time_limit", 0)) if is_timed else None
        )
        time_per_question = request.data.get("time_per_question", False)
        question_time_limit = (
            int(request.data.get("question_time_limit", 0))
            if time_per_question
            else None
        )

        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # Create a prompt for the AI using the knowledge base or general context
        if knowledge_base:
            prompt = (
                f"Based on the following knowledge base, generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}' "
                f"with each question having exactly {option_count} options labeled A, B, C, D, E as needed. "
                f"The knowledge base is: {knowledge_base} "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}}, "correct_answer": "..."}}]}}. '
            )
        else:
            prompt = (
                f"Generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}' "
                f"with each question having exactly {option_count} options labeled A, B, C, D, E as needed. "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}}, "correct_answer": "..."}}]}}. '
            )

        # Generate quiz questions via OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content.strip()
        print("Generated Text from OpenAI:", generated_text)  # Debugging line

        # Parse generated questions
        questions = parse_quiz_text(generated_text, "multiple-choice", option_count)
        if not questions:
            raise ValueError(
                f"Failed to parse questions from OpenAI response: {generated_text}"
            )

        # Create a quiz instance and save questions
        quiz = Quiz.objects.create(
            title=title,
            topic=topic,
            difficulty=difficulty,
            question_count=question_count,
            display_results=display_results,
            require_password=require_password,
            password=password,
            allow_anonymous=allow_anonymous,
            require_name=require_name,
            is_timed=is_timed,
            quiz_time_limit=quiz_time_limit,
            time_per_question=time_per_question,
            question_time_limit=question_time_limit,
        )
        for q in questions:
            Question.objects.create(
                quiz=quiz,
                question_text=q["question_text"],
                option_a=q.get("option_a"),
                option_b=q.get("option_b"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                option_e=q.get("option_e"),
                correct_answer=q.get("correct_answer"),
            )
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except (APIError, APIConnectionError, RateLimitError) as e:
        return Response(
            {"error": f"OpenAI API error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Unexpected error in create_quiz: {str(e)}")  # Log unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def list_quizzes(request):
    """
    Lists all quizzes available in the database.
    """
    quizzes = Quiz.objects.all()
    group_id = request.query_params.get("group_id", None)

    if group_id:
        quizzes = quizzes.filter(group__id=group_id)
    else:
        # Handle ungrouped quizzes if requested
        grouped = request.query_params.get("grouped", "true").lower() == "true"
        if not grouped:
            quizzes = quizzes.filter(group__isnull=True)

    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "DELETE"])
def quiz_detail(request, quiz_id):
    """
    Handles GET, PUT, DELETE requests for a single quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "GET":
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
            group=original_quiz.group,
        )

        for question in original_questions:
            Question.objects.create(
                quiz=duplicated_quiz,
                question_text=question.question_text,
                option_a=question.option_a,
                option_b=question.option_b,
                option_c=question.option_c,
                option_d=question.option_d,
                option_e=question.option_e,
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


logger = logging.getLogger(__name__)


@api_view(["POST"])
def submit_quiz_results(request):
    try:
        # Log the request for debugging
        print("Request data received:", request.data)

        # Extract and validate required fields
        user_name = request.data.get("user_name")
        quiz_id = request.data.get("quiz_id")
        user_answers = request.data.get("user_answers")
        start_time_str = request.data.get("quiz_start_time")

        if not all([user_name, quiz_id, user_answers]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(user_answers, dict):
            return Response(
                {"error": "user_answers must be a dictionary"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.questions.all()

        # Validate total time limit if applicable
        if quiz.is_timed and quiz.quiz_time_limit and start_time_str:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds() / 60

            if elapsed_time > quiz.quiz_time_limit:
                return Response(
                    {"error": "Time limit for the quiz exceeded"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate per-question timing if applicable
        score = 0
        for question in questions:
            user_answer = user_answers.get(str(question.id))

            if quiz.time_per_question:
                question_start_time_str = request.data.get(
                    f"question_{question.id}_start_time"
                )
                if question_start_time_str:
                    question_start_time = datetime.strptime(
                        question_start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    question_elapsed_time = (
                        datetime.now() - question_start_time
                    ).total_seconds()

                    if question_elapsed_time > quiz.time_per_question:
                        continue

            if user_answer == question.correct_answer:
                score += 1

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
        print(f"Unexpected error in submit_quiz_results: {str(e)}")
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


@api_view(["GET", "POST"])
def group_list(request):
    if request.method == "GET":
        groups = Group.objects.all().order_by("order")
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def group_detail(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # Allow deleting an empty group
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["PUT"])
def move_quiz_to_group(request, quiz_id):
    try:
        quiz = get_object_or_404(
            Quiz, id=quiz_id
        )  # Use get_object_or_404 for clarity in errors
        group_id = request.data.get("group_id", None)

        if group_id:
            group = get_object_or_404(Group, id=group_id)
            quiz.group = group
        else:
            quiz.group = None  # Remove from group

        # Update order
        quiz.order = request.data.get("order", quiz.order)
        quiz.save()

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in move_quiz_to_group: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def update_quiz_order(request):
    try:
        quiz_orders = request.data.get("quiz_orders", [])
        for quiz_data in quiz_orders:
            quiz = Quiz.objects.get(id=quiz_data["id"])
            quiz.order = quiz_data["order"]
            quiz.save()
        return Response(status=status.HTTP_200_OK)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating quiz order: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def update_group_order(request):
    """
    Updates the order of groups.
    """
    try:
        group_orders = request.data.get("group_orders", [])
        for group_data in group_orders:
            group = Group.objects.get(id=group_data["id"])
            group.order = group_data["order"]
            group.save()
        return Response(status=status.HTTP_200_OK)
    except Group.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
