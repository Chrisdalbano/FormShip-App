import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..utils import parse_quiz_text
from ..models.quiz import Quiz, SharedQuiz
from ..models.question import Question
from ..models.group import Group
from ..serializers.quiz_serializer import QuizSerializer, SharedQuizSerializer
from ..serializers.question_serializer import QuestionSerializer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(["GET", "POST"])
def list_quizzes(request):
    """
    GET: Lists quizzes for the user’s first account.
    POST: Could create a quiz if you want a single endpoint for both
          (but we keep create_quiz separate by default).
    """
    # Only handle GET in this “old” code;
    # if you want to unify, call create_quiz(request) in the POST block.
    if request.method == "GET":
        # Grab the user’s first associated account:
        account = request.user.accounts.first()
        if not account:
            return Response(
                {"error": "No account associated with the user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter quizzes by this account
        quizzes = Quiz.objects.filter(account=account)

        # Optional group param
        group_id = request.query_params.get("group_id", None)
        if group_id:
            quizzes = quizzes.filter(group__id=group_id)

        # Optional “grouped” param:
        # grouped=true => quizzes w/ group != null
        # grouped=false => quizzes w/ group == null
        grouped = request.query_params.get("grouped", None)
        if grouped is not None:
            if grouped.lower() == "false" or grouped.lower() == "null":
                quizzes = quizzes.filter(group__isnull=True)
            elif grouped.lower() == "true":
                quizzes = quizzes.filter(group__isnull=False)

        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # If you like, you could unify quiz creation here:
    elif request.method == "POST":
        # For the old approach, just respond or delegate:
        return create_quiz(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # old code had authentication for creation
def create_quiz(request):
    """
    Creates a new quiz by generating questions with OpenAI
    if possible.
    """
    try:
        # The user must have an account
        account = request.user.accounts.first()
        if not account:
            return Response(
                {"error": "No account associated with the user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Grab basic fields:
        title = request.data.get("title")
        topic = request.data.get("topic")
        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # Number of questions & options for AI
        question_count = int(request.data.get("question_count", 5))
        option_count = int(request.data.get("option_count", 4))
        difficulty = request.data.get("difficulty", "easy")

        # Possibly a knowledge base string;
        # if None => we still do “basic” generation using just the topic
        knowledge_base = request.data.get("knowledge_base", None)

        # Additional quiz settings from the old code
        display_results = request.data.get("display_results", True)
        require_password = request.data.get("require_password", False)
        password = request.data.get("password", "")
        allow_anonymous = request.data.get("allow_anonymous", False)
        require_name = request.data.get("require_name", False)
        is_timed = request.data.get("is_timed", False)
        quiz_time_limit = (
            int(request.data.get("quiz_time_limit", 0)) if is_timed else None
        )
        are_questions_timed = request.data.get("are_questions_timed", False)
        time_per_question = (
            int(request.data.get("time_per_question", 0))
            if are_questions_timed
            else None
        )
        quiz_type = request.data.get("quiz_type", "multiple-choice")

        # We also used to have an allow_skipping param
        # default True if none is specified:
        skippable_questions = request.data.get("skippable_questions", True)
        # Convert to bool if needed
        skippable_questions = bool(skippable_questions)

        segment_steps = request.data.get("segment_steps", False)
        allow_previous_questions = request.data.get("allow_previous_questions", False)

        # NEW fields for the extended functionality:
        evaluation_type = request.data.get("evaluation_type", "pre")  # pre/hybrid/post
        is_testing = request.data.get("is_testing", False)  # bool
        is_published = request.data.get("is_published", False)  # bool
        access_control = request.data.get(
            "access_control", "public"
        )  # public/invitation/login_required

        # Construct the AI prompt:
        if knowledge_base:
            # If user provided knowledge base => incorporate it
            prompt = (
                f"Based on the following knowledge base, generate {question_count} {difficulty} multiple-choice questions "
                f"about the topic '{topic}', each with exactly {option_count} options labeled A, B, C, D, E if needed. "
                f"Knowledge base: {knowledge_base} "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", '
                f'"D": "...", "E": "..."}}, "correct_answer": "..."}}]}}.'
            )
        else:
            # If no knowledge base => simple generation from just the topic
            prompt = (
                f"Generate {question_count} {difficulty} multiple-choice questions about the topic '{topic}', "
                f"each question has exactly {option_count} options labeled A, B, C, D, E if needed. "
                f"Return valid JSON in the format: "
                f'{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", '
                f'"D": "...", "E": "..."}}, "correct_answer": "..."}}]}}.'
            )

        # Call OpenAI to generate questions.
        # (the old code always did so, whether knowledge_base was set or not)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content.strip()
        print("Generated Text from OpenAI:", generated_text)

        # Parse the returned JSON from the AI:
        questions_data = parse_quiz_text(
            generated_text, "multiple-choice", option_count
        )
        if not questions_data:
            raise ValueError(
                f"Failed to parse questions from OpenAI response: {generated_text}"
            )

        # Create the quiz record
        quiz_obj = Quiz.objects.create(
            account=account,
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
            are_questions_timed=are_questions_timed,
            time_per_question=time_per_question,
            quiz_type=quiz_type,
            skippable_questions=skippable_questions,
            segment_steps=segment_steps,
            allow_previous_questions=allow_previous_questions,
            # Add the new fields:
            evaluation_type=evaluation_type,
            is_testing=is_testing,
            is_published=is_published,
            access_control=access_control,
        )

        # Create each question instance
        question_instances = []
        for q in questions_data:
            question_instance = Question.objects.create(
                quiz=quiz_obj,
                question_text=q["question_text"],
                option_a=q.get("option_a"),
                option_b=q.get("option_b"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                option_e=q.get("option_e"),
                correct_answer=q.get("correct_answer"),
            )
            question_instances.append(question_instance)

        # Serialize & respond
        quiz_serializer = QuizSerializer(quiz_obj)
        question_serializer = QuestionSerializer(question_instances, many=True)
        resp_data = {
            "quiz": quiz_serializer.data,
            "questions": question_serializer.data,
            "id": quiz_obj.id,
        }
        return Response(resp_data, status=status.HTTP_201_CREATED)

    except (APIError, APIConnectionError, RateLimitError) as e:
        return Response(
            {"error": f"OpenAI API error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except ValueError as ve:
        return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        print(f"Unexpected error in create_quiz: {str(ex)}")
        return Response(
            {"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET", "PUT", "DELETE"])
def quiz_detail(request, quiz_id):
    """
    GET: Retrieve a quiz
    PUT: Update quiz
    DELETE: Delete quiz
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "GET":
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

    elif request.method == "PUT":
        # “partial=True” to allow partial updates
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
    """
    Clones an existing quiz and all its questions.
    """
    original_quiz = get_object_or_404(Quiz, id=quiz_id)
    # old code: no permission checks, so we preserve that

    duplicated_quiz = Quiz.objects.create(
        # copy all the fields from original, plus the new ones
        account=original_quiz.account,
        title=f"Copy of {original_quiz.title}",
        topic=original_quiz.topic,
        difficulty=original_quiz.difficulty,
        question_count=original_quiz.question_count,
        quiz_type=original_quiz.quiz_type,
        group=original_quiz.group,
        display_results=original_quiz.display_results,
        require_password=original_quiz.require_password,
        password=original_quiz.password,
        allow_anonymous=original_quiz.allow_anonymous,
        require_name=original_quiz.require_name,
        is_timed=original_quiz.is_timed,
        quiz_time_limit=original_quiz.quiz_time_limit,
        are_questions_timed=original_quiz.are_questions_timed,
        time_per_question=original_quiz.time_per_question,
        skippable_questions=original_quiz.skippable_questions,
        segment_steps=original_quiz.segment_steps,
        allow_previous_questions=original_quiz.allow_previous_questions,
        # new fields:
        evaluation_type=original_quiz.evaluation_type,
        is_testing=original_quiz.is_testing,
        is_published=original_quiz.is_published,
        access_control=original_quiz.access_control,
    )
    for old_q in original_quiz.questions.all():
        Question.objects.create(
            quiz=duplicated_quiz,
            question_text=old_q.question_text,
            option_a=old_q.option_a,
            option_b=old_q.option_b,
            option_c=old_q.option_c,
            option_d=old_q.option_d,
            option_e=old_q.option_e,
            correct_answer=old_q.correct_answer,
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
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_quiz_order(request):
    quiz_orders = request.data.get("quiz_orders", [])
    for quiz_data in quiz_orders:
        quiz_id = quiz_data.get("id")
        quiz_order = quiz_data.get("order")
        if quiz_id is not None and quiz_order is not None:
            try:
                quiz_obj = Quiz.objects.get(id=quiz_id)
                quiz_obj.order = quiz_order
                quiz_obj.save()
            except Quiz.DoesNotExist:
                pass
    return Response(status=status.HTTP_200_OK)
