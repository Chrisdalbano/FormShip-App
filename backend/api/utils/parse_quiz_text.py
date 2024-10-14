# backend/api/utils.py

import json


def parse_quiz_text(generated_text, quiz_type, option_count):
    """
    Parses the generated text from OpenAI into quiz questions.

    Args:
        generated_text (str): JSON formatted string of questions.
        quiz_type (str): Type of quiz, e.g., "multiple-choice".
        option_count (int): Number of options per question.

    Returns:
        list: A list of question dictionaries or None if parsing fails.
    """
    questions = []
    try:
        # Load the generated text as JSON
        data = json.loads(generated_text)

        if quiz_type == "multiple-choice" and "questions" in data:
            for item in data["questions"]:
                # Extract options dynamically based on the option count
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
