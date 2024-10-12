from django.shortcuts import get_object_or_404
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


@api_view(["POST"])
def create_quiz(request):
    """
    Creates a new quiz by generating questions with OpenAI API or by analyzing user-provided knowledge base.
    """
    try:
        # Get user input from the request
        title = request.data.get("title")
        topic = request.data.get("topic")
        question_count = int(request.data.get("question_count", 5))
        option_count = int(request.data.get("option_count", 4))
        difficulty = request.data.get("difficulty", "easy")
        quiz_type = request.data.get("quiz_type", "multiple-choice")
        knowledge_base = request.data.get("knowledge_base", None)
        display_results = request.data.get("display_results", True)
        require_password = request.data.get("require_password", False)
        password = request.data.get("password", None)
        allow_anonymous = request.data.get("allow_anonymous", False)
        require_name = request.data.get("require_name", False)
        group_id = request.data.get("group_id", None)

        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # Assign quiz_type if not explicitly provided
        if not quiz_type:
            quiz_type = "multiple-choice" if option_count > 1 else "single-choice"

        # Create prompt for the AI based on whether a knowledge base is provided
        if knowledge_base:
            # Use the provided knowledge base to generate the quiz questions
            prompt = (
                f"Based on the following knowledge base, generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}' "
                f"with each question having exactly {option_count} options labeled A, B, C, D, E as needed. "
                f"The knowledge base is: {knowledge_base} "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}}, "correct_answer": "..."}}]}}. '
                f"Ensure that there are only {option_count} options per question, even if some are empty."
            )
        else:
            # Generate quiz questions using OpenAI API (ChatCompletion)
            prompt = (
                f"Generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}' "
                f"with each question having exactly {option_count} options labeled A, B, C, D, E as needed. "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}}, "correct_answer": "..."}}]}}. '
                f"Ensure that there are only {option_count} options per question, even if some are empty."
            )

        # Make request to OpenAI to generate questions
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
        questions = parse_quiz_text(generated_text, quiz_type, option_count)

        if not questions:
            raise ValueError("Failed to parse questions from OpenAI response.")

        # Create a new quiz instance
        group = None
        if group_id:
            group = Group.objects.get(id=group_id)

        quiz = Quiz.objects.create(
            title=title,
            topic=topic,
            difficulty=difficulty,
            question_count=question_count,
            quiz_type=quiz_type,
            allow_anonymous=allow_anonymous,
            require_password=require_password,
            password=password,
            require_name=require_name,
            display_results=display_results,
            group=group,
        )

        # Create questions and associate them with the quiz
        for q in questions:
            Question.objects.create(
                quiz=quiz,
                question_text=q["question_text"],
                option_a=q.get("option_a"),
                option_b=q.get("option_b"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                option_e=q.get("option_e"),
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

    except Group.DoesNotExist:
        return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # General exception for unexpected errors
        print(f"General Error: {str(e)}")
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
        quizzes = quizzes.filter(group__isnull=True)

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
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    group_id = request.data.get("group_id", None)

    if group_id:
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND
            )
        quiz.group = group
    else:
        # Remove from group if no group_id is provided
        quiz.group = None

    quiz.save()
    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_quiz_order(request):
    """
    Updates the order of quizzes.
    """
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
