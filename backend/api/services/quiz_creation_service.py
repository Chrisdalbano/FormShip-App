# backend/api/services/quiz_creation_service.py

import uuid
import logging

from django.db import transaction
from openai import APIError, APIConnectionError, RateLimitError
from ..models.quiz import Quiz
from ..models.question import Question
from ..utils import parse_quiz_text

logger = logging.getLogger(__name__)


class QuizCreationError(Exception):
    """
    Custom exception to raise when quiz creation fails
    (e.g., parse errors, AI issues that block creation).
    """

    pass


class QuizCreationService:
    """
    Handles the creation of a Quiz, including optional AI question generation.
    """

    def __init__(self, openai_client):
        """
        openai_client should be an instance of the OpenAI class
        (or a mock/stub for testing).
        """
        self.openai_client = openai_client

    def create_quiz_with_ai(self, account, payload):
        """
        Main method: parse payload -> optionally call AI -> create DB records -> return (quiz_obj, question_objs).
        If you want, wrap in a transaction so if anything fails, it all rolls back.
        """
        # 1) Extract quiz-related fields
        quiz_data = self._parse_quiz_payload(payload)

        # 2) Possibly build AI prompt & call AI
        question_data = []
        if quiz_data["question_count"] > 0:
            generated_text = self._generate_ai_questions(quiz_data)
            # 3) Parse AI text
            if generated_text:
                question_data = self._parse_ai_question_data(
                    generated_text, quiz_data["option_count"]
                )

        # 4) Create the quiz + questions inside a transaction
        quiz_obj, question_objs = self._create_quiz_and_questions(
            account, quiz_data, question_data
        )

        return quiz_obj, question_objs

    def _parse_quiz_payload(self, payload):
        """
        Extracts fields from request data, providing defaults or validations as needed.
        Could raise ValueError if something is missing.
        """
        # Basic required fields
        title = (payload.get("title") or "").strip()
        topic = (payload.get("topic") or "").strip()
        if not title or not topic:
            raise ValueError("Title and topic are required fields.")

        # Example of extracting and converting fields
        question_count = int(payload.get("question_count", 5))
        option_count = int(payload.get("option_count", 4))

        return {
            "title": title,
            "topic": topic,
            "difficulty": payload.get("difficulty", "easy"),
            "knowledge_base": payload.get("knowledge_base", None),
            "question_count": question_count,
            "option_count": option_count,
            "display_results": payload.get("display_results", True),
            "require_password": payload.get("require_password", False),
            "password": payload.get("password", ""),
            "allow_anonymous": payload.get("allow_anonymous", False),
            "require_name": payload.get("require_name", False),
            "is_timed": payload.get("is_timed", False),
            "quiz_time_limit": payload.get("quiz_time_limit", 0),
            "are_questions_timed": payload.get("are_questions_timed", False),
            "time_per_question": payload.get("time_per_question", 0),
            "quiz_type": payload.get("quiz_type", "multiple-choice"),
            "skippable_questions": bool(payload.get("skippable_questions", True)),
            "segment_steps": payload.get("segment_steps", False),
            "allow_previous_questions": payload.get("allow_previous_questions", False),
            "evaluation_type": payload.get("evaluation_type", "pre"),
            "is_testing": payload.get("is_testing", False),
            "is_published": payload.get("is_published", False),
            "access_control": payload.get("access_control", "public"),
        }

    def _generate_ai_questions(self, quiz_data):
        """
        Build the OpenAI prompt from the quiz_data and call the API.
        If AI fails, logs the error and returns empty string
        so we can still create the quiz without questions.
        """
        question_count = quiz_data["question_count"]
        option_count = quiz_data["option_count"]
        difficulty = quiz_data["difficulty"]
        topic = quiz_data["topic"]
        knowledge_base = quiz_data["knowledge_base"]

        # Build prompt
        if knowledge_base:
            prompt = (
                f"Based on the following knowledge base, generate {question_count} {difficulty} "
                f"multiple-choice questions about '{topic}' with {option_count} options each. "
                f"Knowledge base: {knowledge_base}. Return JSON with 'questions' array."
            )
        else:
            prompt = (
                f"Generate {question_count} {difficulty} multiple-choice questions about '{topic}', "
                f"each with {option_count} options labeled A, B, C, etc. Return JSON with 'questions' array."
            )

        generated_text = ""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7,
            )
            generated_text = response.choices[0].message.content.strip()
            logger.info("Generated Text from OpenAI: %s", generated_text)
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.warning("OpenAI error occurred; continuing with empty quiz: %s", e)

        return generated_text

    def _parse_ai_question_data(self, generated_text, option_count):
        """
        Parse the AI response JSON into a list of question dicts.
        If parse fails, we can choose to return empty or raise an error.
        """
        question_data = []
        parsed = parse_quiz_text(generated_text, "multiple-choice", option_count)
        if parsed:
            question_data = parsed
        else:
            logger.warning(
                "Failed to parse AI questions; continuing with no questions."
            )
        return question_data

    @transaction.atomic
    def _create_quiz_and_questions(self, account, quiz_data, question_data):
        """
        Use a DB transaction so that if question creation fails, the quiz won't remain half-created.
        """
        from ..models.quiz import Quiz
        from ..models.question import Question

        # 1) Create Quiz object
        quiz_obj = Quiz.objects.create(
            account=account,
            title=quiz_data["title"],
            topic=quiz_data["topic"],
            difficulty=quiz_data["difficulty"],
            question_count=quiz_data["question_count"],
            display_results=quiz_data["display_results"],
            require_password=quiz_data["require_password"],
            password=quiz_data["password"],
            allow_anonymous=quiz_data["allow_anonymous"],
            require_name=quiz_data["require_name"],
            is_timed=quiz_data["is_timed"],
            quiz_time_limit=(
                int(quiz_data["quiz_time_limit"]) if quiz_data["is_timed"] else None
            ),
            are_questions_timed=quiz_data["are_questions_timed"],
            time_per_question=(
                int(quiz_data["time_per_question"])
                if quiz_data["are_questions_timed"]
                else None
            ),
            quiz_type=quiz_data["quiz_type"],
            skippable_questions=quiz_data["skippable_questions"],
            segment_steps=quiz_data["segment_steps"],
            allow_previous_questions=quiz_data["allow_previous_questions"],
            evaluation_type=quiz_data["evaluation_type"],
            is_testing=quiz_data["is_testing"],
            is_published=quiz_data["is_published"],
            access_control=quiz_data["access_control"],
        )

        # 2) Create question records
        question_objs = []
        for q_dict in question_data:
            # For future: handle "free_text" question type if you want
            # e.g. if 'question_type' in q_dict, store that in the DB
            question = Question.objects.create(
                quiz=quiz_obj,
                question_text=q_dict.get("question_text", ""),
                option_a=q_dict.get("option_a"),
                option_b=q_dict.get("option_b"),
                option_c=q_dict.get("option_c"),
                option_d=q_dict.get("option_d"),
                option_e=q_dict.get("option_e"),
                correct_answer=q_dict.get("correct_answer", "A"),
                # If you want to store images, you might add fields in the model
                # e.g. 'image_url = q_dict.get("image_url")'
            )
            question_objs.append(question)

        return quiz_obj, question_objs
