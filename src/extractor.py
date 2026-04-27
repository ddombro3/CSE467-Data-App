

import re
from keywords import DATA_KEYWORDS


def split_into_sentences(text):

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def keyword_in_sentence(keyword, sentence_lower):

    keyword_lower = keyword.lower().strip()

    pattern = r"(?<!\w)" + re.escape(keyword_lower) + r"(?!\w)"

    return re.search(pattern, sentence_lower) is not None


def find_keyword_matches(sentence):

    matches = []
    sentence_lower = sentence.lower()

    for category, keywords in DATA_KEYWORDS.items():
        for keyword in keywords:
            if keyword_in_sentence(keyword, sentence_lower):
                matches.append({
                    "data_category": category,
                    "keyword": keyword
                })

    return matches


def extract_privacy_data(platform, source_name, source_url, source_file, text):

    results = []
    sentences = split_into_sentences(text)

    seen_rows = set()

    for sentence in sentences:
        matches = find_keyword_matches(sentence)

        for match in matches:
            row_key = (
                platform,
                source_name,
                match["data_category"],
                match["keyword"],
                sentence,
            )

            # Avoid duplicate rows.
            if row_key in seen_rows:
                continue

            seen_rows.add(row_key)

            results.append({
                "platform": platform,
                "source_name": source_name,
                "source_url": source_url,
                "source_file": source_file,
                "data_category": match["data_category"],
                "keyword": match["keyword"],
                "matching_sentence": sentence
            })

    return results