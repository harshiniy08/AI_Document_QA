
import re


def generate_answer(question, relevant_text):

    if not relevant_text:
        return "Answer not found in the document."

    answer_parts = []
    seen = set()

    for item in relevant_text:

        text = re.sub(r"\s+", " ", str(item)).strip()

        # Remove empty lines and section numbers.
        text = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", text)

        text = text.strip(" -–—:;")

        if len(text) < 3:
            continue

        key = text.lower()

        if key not in seen:
            seen.add(key)
            answer_parts.append(text)

    if not answer_parts:
        return "Answer not found in the document."

    return "\n\n".join(answer_parts)
