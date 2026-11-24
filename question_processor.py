
import re
from answer_generator import generate_answer


STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of", "in",
    "to", "for", "and", "or", "was", "were", "with",
    "how", "why", "when", "where", "which", "who",
    "do", "does", "did", "can", "could", "would",
    "should", "about", "explain", "describe", "tell",
    "me", "please", "this", "that", "from", "each",
    "list", "provide", "give", "include", "all"
}


TOPICS = {
    "problem_statements": [
        "problem statement", "problem statements",
        "selected problems", "selected problem",
        "problem statement ids"
    ],
    "tools": [
        "tools", "technologies", "technology",
        "software", "framework", "platform"
    ],
    "objectives": [
        "objectives", "objective", "goals", "aims"
    ],
    "limitations": [
        "limitations", "limitation", "drawbacks", "constraints"
    ],
    "features": ["features", "functionalities"],
    "future": ["future", "enhancements", "improvements"],
    "methodology": ["methodology", "implementation"],
    "advantages": ["advantages", "benefits"],
    "conclusion": ["conclusion", "summary"]
}


HEADINGS = {
    "tools": [
        "software stack", "development tooling",
        "tools and technologies", "technologies used",
        "technology stack", "software tools"
    ],
    "objectives": [
        "specific technical objectives",
        "project objectives", "objectives"
    ],
    "limitations": [
        "limitations", "project limitations"
    ],
    "features": [
        "core system features", "project features", "features"
    ],
    "future": [
        "future scope", "future enhancements", "future work"
    ],
    "methodology": [
        "methodology", "implementation methodology"
    ],
    "advantages": ["advantages", "benefits"],
    "conclusion": ["conclusion", "summary"]
}


BULLET_MARKERS = r"[•▪◦●‣⁃➢➤]"


def identify_topic(question):
    question = question.lower()

    for topic, words in TOPICS.items():
        if any(word in question for word in words):
            return topic

    return None


def split_document(text):
    text = text.replace("\r", "\n")
    text = re.sub(BULLET_MARKERS, "\n", text)

    lines = []

    for raw_line in text.split("\n"):
        line = re.sub(r"\s+", " ", raw_line).strip()

        if not line:
            continue

        if re.fullmatch(r"\d+", line):
            continue

        lines.append(line)

    return lines


def is_numbered_heading(line):
    return bool(
        re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Za-z]", line.strip())
    )


def matches_heading(line, topic):
    if topic not in HEADINGS:
        return False

    heading_text = re.sub(
        r"^\d+(?:\.\d+)*\.?\s*", "", line.strip()
    ).lower()

    if len(heading_text) > 100:
        return False

    if re.search(r"[.!?]", heading_text):
        return False

    return any(
        term in heading_text
        for term in HEADINGS[topic]
    )


def find_relevant_section(lines, topic):
    if not topic:
        return []

    result = []
    collecting = False

    for line in lines:
        if matches_heading(line, topic):
            collecting = True
            continue

        if collecting and is_numbered_heading(line):
            break

        if collecting:
            result.append(line)

    return result


def find_problem_statements(lines):
    results = []
    seen = set()

    for index, line in enumerate(lines):

        match = re.search(
            r"\b(SIH\d{5})\b",
            line,
            re.IGNORECASE
        )

        if not match:
            continue

        ps_id = match.group(1).upper()
        title = ""

        # Extract title from a table row.
        if "|" in line:
            columns = [
                part.strip() for part in line.split("|")
            ]

            for column_index, column in enumerate(columns):
                if ps_id in column.upper():
                    if column_index + 1 < len(columns):
                        title = columns[column_index + 1]
                    break

        # Extract title from the following document line.
        if not title:
            for next_line in lines[index + 1:index + 3]:

                if re.search(
                    r"\bSIH\d{5}\b",
                    next_line,
                    re.IGNORECASE
                ):
                    continue

                if next_line.strip():
                    title = next_line.strip()
                    break

        if title:
            result = f"{ps_id} - {title}"

            if result.lower() not in seen:
                seen.add(result.lower())
                results.append(result)

    return results


def extract_keywords(question):
    words = re.findall(
        r"[a-zA-Z0-9]+",
        question.lower()
    )

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]


def find_keyword_matches(lines, question):
    keywords = extract_keywords(question)
    results = []

    for line in lines:
        lower_line = line.lower()

        score = sum(
            1 for word in keywords
            if word in lower_line
        )

        if score > 0:
            results.append((score, line))

    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        line for score, line in results[:20]
    ]


def process_question(question, document_text):

    if not question.strip():
        return "Please enter a question."

    if not document_text or not document_text.strip():
        return "No readable document content found."

    lines = split_document(document_text)
    topic = identify_topic(question)

    if topic == "problem_statements":

        results = find_problem_statements(lines)

        if not results:
            results = find_keyword_matches(
                lines, question
            )

    else:
        results = find_relevant_section(
            lines, topic
        )

        if not results:
            results = find_keyword_matches(
                lines, question
            )

    if not results:
        return "Answer not found in the document."

    return generate_answer(question, results)
