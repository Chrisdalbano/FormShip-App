from http import client
import os
from openai import APIConnectionError, APIError, RateLimitError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..utils import parse_quiz_text

from ..models.quiz import Quiz, SharedQuiz
from ..models.group import Group
from ..models.question import Question
from ..serializers.quiz_serializer import QuizSerializer, SharedQuizSerializer
from ..serializers.question_serializer import QuestionSerializer
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


@api_view(["GET", "POST"])
def list_quizzes(request):
    quizzes = Quiz.objects.all()
    group_id = request.query_params.get("group_id", None)
    grouped = request.query_params.get("grouped", None)

    if group_id:
        quizzes = quizzes.filter(group__id=group_id)

    if grouped is not None:
        if grouped.lower() == "false" or "null":
            quizzes = quizzes.filter(group__isnull=True)
        elif grouped.lower() == "true":
            quizzes.quizzes.filter(group__isnull=False)

    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


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
        quiz_type = request.data.get(
            "quiz_type", "multiple-choice"
        )  # Extract quiz type
        skippable_questions = request.data.get(
            "skippable_questions", True
        )  # Default to True
        segment_steps = request.data.get(
            "segment_steps", False
        )  # Extract segment_steps for stepwise

        # Validate title and topic
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
                f"with each question having exactly {option_count} options labeled A, B, C, D, E if needed. "
                f"Ensure that each question includes a 'question' field, an 'options' dictionary with keys A, B, C, D, E, and a 'correct_answer' key "
                f"with one of the options as the value. "
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

        # Create a quiz instance
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
            quiz_type=quiz_type,  # Correctly set quiz type from the request
            skippable_questions=skippable_questions,  # Add skippable questions for stepwise
            segment_steps=segment_steps,  # Set if the quiz is segmented by steps (one question at a time)
        )

        # Create question instances and attach to the quiz
        question_instances = []
        for q in questions:
            question_instance = Question.objects.create(
                quiz=quiz,
                question_text=q["question_text"],
                option_a=q.get("option_a"),
                option_b=q.get("option_b"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                option_e=q.get("option_e"),
                correct_answer=q.get("correct_answer"),
            )
            question_instances.append(question_instance)

        # Serialize the created quiz and questions
        quiz_serializer = QuizSerializer(quiz)
        question_serializer = QuestionSerializer(question_instances, many=True)

        # Prepare the response data
        response_data = {
            "quiz": quiz_serializer.data,
            "questions": question_serializer.data,
            "id": quiz.id,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

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


@api_view(["GET", "PUT", "DELETE"])
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "GET":
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def duplicate_quiz(request, quiz_id):
    original_quiz = get_object_or_404(Quiz, id=quiz_id)
    duplicated_quiz = Quiz.objects.create(
        title=f"Copy of {original_quiz.title}",
        topic=original_quiz.topic,
        difficulty=original_quiz.difficulty,
        question_count=original_quiz.question_count,
        quiz_type=original_quiz.quiz_type,
        group=original_quiz.group,
    )
    for question in original_quiz.questions.all():
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


@api_view(["POST"])
def share_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    shared_quiz = SharedQuiz.objects.create(quiz=quiz)
    serializer = SharedQuizSerializer(shared_quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def move_quiz_to_group(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    group_id = request.data.get("group_id", None)

    if group_id:
        group = get_object_or_404(Group, id=group_id)
        quiz.group = group
    else:
        quiz.group = None

    quiz.order = request.data.get("order", quiz.order)
    quiz.save()

    serializer = QuizSerializer(quiz)
    return Response(serializer.data)


@api_view(["PUT"])
def update_quiz_order(request):
    quiz_orders = request.data.get("quiz_orders", [])
    for quiz_data in quiz_orders:
        quiz = Quiz.objects.get(id=quiz_data["id"])
        quiz.order = quiz_data["order"]
        quiz.save()
    return Response(status=status.HTTP_200_OK)
