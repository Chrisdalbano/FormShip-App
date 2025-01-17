import os
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# If you rely on OpenAI for quiz generation:
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from ..models.user import AccountMembership

from ..utils import parse_quiz_text
from ..models.quiz import Quiz, SharedQuiz
from ..models.group import Group
from ..models.question import Question
from ..serializers.quiz_serializer import QuizSerializer, SharedQuizSerializer
from ..serializers.question_serializer import QuestionSerializer

# If you have an InvitedUser model & serializer:
from ..models.quiz_invite import InvitedUser
from ..serializers.quiz_serializer import InvitedUserSerializer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])  # if you want only authenticated users
def list_quizzes(request):
    """
    GET: Lists quizzes belonging to the user's account (with optional group filters).
    POST: Could call create_quiz internally or do the same logic (but usually you'd just call /create/).
    """
    if request.method == "GET":
        account = request.user.accounts.first()
        if not account:
            return Response(
                {"error": "No account associated with this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quizzes = Quiz.objects.filter(account=account)

        # Optional filters:
        group_id = request.query_params.get("group_id", None)
        if group_id:
            quizzes = quizzes.filter(group__id=group_id)

        grouped = request.query_params.get("grouped", None)
        if grouped is not None:
            if grouped.lower() in ["false", "null"]:
                quizzes = quizzes.filter(group__isnull=True)
            elif grouped.lower() == "true":
                quizzes = quizzes.filter(group__isnull=False)

        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        # Optionally just forward to create_quiz
        return create_quiz(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    """
    Creates a new quiz.
    Always attempts AI generation unless user sets question_count=0, etc.
    If 'knowledge_base' is provided, uses it to create a more specialized AI prompt;
    otherwise uses a default prompt.
    """
    try:
        account = request.user.accounts.first()
        if not account:
            return Response(
                {"error": "No account associated with the user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Basic required fields
        title = request.data.get("title", "").strip()
        topic = request.data.get("topic", "").strip()
        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # AI / question generation fields
        question_count = int(request.data.get("question_count", 5))
        option_count = int(request.data.get("option_count", 4))
        difficulty = request.data.get("difficulty", "easy")
        knowledge_base = request.data.get("knowledge_base", None)

        # Additional quiz fields from older code
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
        # If 'skippable_questions' is missing, default to True
        skippable_questions = request.data.get("skippable_questions", True)
        skippable_questions = bool(skippable_questions)
        segment_steps = request.data.get("segment_steps", False)
        allow_previous_questions = request.data.get("allow_previous_questions", False)

        # New fields from "improvements"
        evaluation_type = request.data.get(
            "evaluation_type", "pre"
        )  # pre / hybrid / post
        is_testing = request.data.get("is_testing", False)
        is_published = request.data.get("is_published", False)
        access_control = request.data.get("access_control", "public")

        # 1) Build an OpenAI prompt, with or without knowledge base
        if knowledge_base:
            prompt = (
                f"Based on the following knowledge base, generate {question_count} {difficulty} "
                f"multiple-choice questions about '{topic}' with {option_count} options each. "
                f"Knowledge base: {knowledge_base}. "
                f"Return JSON with 'questions': [{{question, options: {{A, B, ...}}, correct_answer}}]."
            )
        else:
            # Default prompt if user doesn't supply knowledge_base
            prompt = (
                f"Generate {question_count} {difficulty} multiple-choice questions about '{topic}', "
                f"with exactly {option_count} answer options labeled A-E. Return JSON with 'questions' array."
            )

        # 2) If question_count > 0, attempt AI generation
        generated_text = ""
        if question_count > 0:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7,
                )
                generated_text = response.choices[0].message.content.strip()
                print("Generated Text from OpenAI:", generated_text)
            except (APIError, APIConnectionError, RateLimitError) as e:
                # Non-fatal error: user can still create an empty quiz or handle it as needed
                print("OpenAI error, continuing with empty quiz generation:", e)

        # 3) Parse AI questions (if any)
        parsed_questions = []
        if generated_text:
            parsed_questions = parse_quiz_text(
                generated_text, "multiple-choice", option_count
            )
            # If parsing fails, you can decide to let it continue or raise an error
            # e.g. raise ValueError("Failed to parse AI questions...")

        # 4) Create quiz record
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
            evaluation_type=evaluation_type,
            is_testing=is_testing,
            is_published=is_published,
            access_control=access_control,
        )

        # 5) Create question records from parsed AI data
        question_instances = []
        for q in parsed_questions:
            q_obj = Question.objects.create(
                quiz=quiz_obj,
                question_text=q.get("question_text", ""),
                option_a=q.get("option_a"),
                option_b=q.get("option_b"),
                option_c=q.get("option_c"),
                option_d=q.get("option_d"),
                option_e=q.get("option_e"),
                correct_answer=q.get("correct_answer", "A"),
            )
            question_instances.append(q_obj)

        # 6) Serialize the newly created quiz and questions
        quiz_serializer = QuizSerializer(quiz_obj)
        question_serializer = QuestionSerializer(question_instances, many=True)
        data_out = {
            "quiz": quiz_serializer.data,
            "questions": question_serializer.data,
            "id": quiz_obj.id,
        }
        return Response(data_out, status=status.HTTP_201_CREATED)

    except ValueError as ve:
        return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        print(f"Unexpected error in create_quiz: {exc}")
        return Response(
            {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET", "PUT", "DELETE"])
def quiz_detail(request, quiz_id):
    """
    Retrieve, update, or delete a quiz.
    On PUT, can also handle optional "questions" data if you'd like bulk updates.
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    # For update/delete, ensure user is owner or admin in the quiz's account
    if request.method in ["PUT", "DELETE"]:
        # 1) Find membership for request.user in the quiz's account
        membership = AccountMembership.objects.filter(
            account=quiz_obj.account,
            user=request.user
        ).first()

        # 2) If membership doesn't exist or role isn't "owner"/"admin", forbid
        if not membership or membership.role not in ["owner", "admin"]:
            return Response({"error": "Permission denied."}, status=403)

    if request.method == "GET":
        serializer = QuizSerializer(quiz_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        # Update quiz fields
        serializer = QuizSerializer(quiz_obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # Optionally handle question updates if request.data has "questions"
        questions_data = request.data.get("questions", [])
        if questions_data:
            updated_questions = []
            for q_item in questions_data:
                q_id = q_item.get("id")
                if q_id:  # update existing question
                    try:
                        existing_q = quiz_obj.questions.get(id=q_id)
                    except Question.DoesNotExist:
                        continue  # skip or handle differently
                    q_serializer = QuestionSerializer(
                        existing_q, data=q_item, partial=True
                    )
                    if q_serializer.is_valid():
                        q_serializer.save()
                        updated_questions.append(q_serializer.data)
                else:
                    # create new question
                    q_item["quiz"] = quiz_obj.id
                    new_q_serializer = QuestionSerializer(data=q_item)
                    if new_q_serializer.is_valid():
                        new_q_obj = new_q_serializer.save()
                        updated_questions.append(QuestionSerializer(new_q_obj).data)
            # If desired, remove questions not in the new data here

        # Return the updated quiz
        updated_quiz_serializer = QuizSerializer(quiz_obj)
        return Response(updated_quiz_serializer.data, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        quiz_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
def duplicate_quiz(request, quiz_id):
    """
    Duplicate an existing quiz and all its questions.
    Optionally ensure user is the owner or has permission.
    """
    original_quiz = get_object_or_404(Quiz, id=quiz_id)

    # (Optional) check ownership if you want
    # if original_quiz.account.owner != request.user:
    #     return Response({"error": "Permission denied."}, status=403)

    # Create the new quiz
    duplicated_quiz = Quiz.objects.create(
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
        evaluation_type=original_quiz.evaluation_type,
        is_testing=original_quiz.is_testing,
        is_published=original_quiz.is_published,
        access_control=original_quiz.access_control,
    )

    # Duplicate the questions
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
    """
    Example for generating a 'shared quiz' link. Possibly used for external sharing.
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)
    shared_quiz = SharedQuiz.objects.create(quiz=quiz_obj)
    serializer = SharedQuizSerializer(shared_quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def move_quiz_to_group(request, quiz_id):
    """
    Move a quiz to a new group or ungroup it (group_id=null).
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)
    group_id = request.data.get("group_id")

    if group_id:
        group = get_object_or_404(Group, id=group_id)
        quiz_obj.group = group
    else:
        quiz_obj.group = None

    quiz_obj.order = request.data.get("order", quiz_obj.order)
    quiz_obj.save()

    serializer = QuizSerializer(quiz_obj)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_quiz_order(request):
    """
    Batch update quiz .order for drag-and-drop reordering, e.g.:
    {
      "quiz_orders": [
        {"id": 1, "order": 10},
        {"id": 2, "order": 20}
      ]
    }
    """
    quiz_orders = request.data.get("quiz_orders", [])
    for q_item in quiz_orders:
        q_id = q_item.get("id")
        new_order = q_item.get("order")
        if q_id is not None and new_order is not None:
            try:
                quiz_obj = Quiz.objects.get(id=q_id)
                quiz_obj.order = new_order
                quiz_obj.save()
            except Quiz.DoesNotExist:
                pass  # or handle error
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_users_to_quiz(request, quiz_id):
    """
    If a quiz has access_control='invitation', we can invite external emails to it.
    """
    quiz_obj = get_object_or_404(Quiz, id=quiz_id)

    # Check ownership or admin membership, etc.
    if quiz_obj.account.owner != request.user:
        return Response({"error": "No permission."}, status=status.HTTP_403_FORBIDDEN)

    if quiz_obj.access_control != "invitation":
        return Response(
            {"error": "Quiz is not in invitation-only mode."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    emails = request.data.get("emails", [])
    invited = []
    for email in emails:
        # Insert or get an invited user record
        invited_user, _ = InvitedUser.objects.get_or_create(quiz=quiz_obj, email=email)
        invited.append(invited_user)

    serializer = InvitedUserSerializer(invited, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
