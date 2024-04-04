from nrclex import NRCLex
from webcrawler import parse_blog_article
from convert_sentiments import load_sentiments

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from collections import Counter

import yaml
import json
import re


def remove_markdown_syntax(text):
    # Remove Markdown URL links
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    # Remove inline code and code blocks
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"```[^`]*```", "", text, flags=re.DOTALL)
    # Remove bold, italic, and strikethrough text markers
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)  # Bold
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)  # Italic
    text = re.sub(r"~~(.*?)~~", r"\1", text)  # Strikethrough
    # Remove headers
    text = re.sub(r"\n#+\s*(.*?)\n", r"\n\1\n", text)
    # Remove blockquotes
    text = re.sub(r">\s*(.*?)\n", r"\1\n", text)
    # Remove remaining Markdown syntax artifacts
    text = re.sub(r"\*\*\\", " ", text)  # Specific sequence
    text = re.sub(r"\\", "", text)  # Remove all backslashes
    # Normalize multiple newlines to a single newline
    text = re.sub(r"\n\s*\n", " ", text)
    return text


def parse_markdown_with_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

        # Split the content to separate frontmatter
        parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)

        frontmatter, main_content = {}, ""
        if len(parts) == 3:
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(parts[1])
            main_content = parts[2]
        else:
            main_content = content

        # Extract the first H1 heading
        heading_match = re.search(r"^##\s+(.*)", main_content, flags=re.MULTILINE)
        heading = heading_match.group(1) if heading_match else "Not found"

        # Remove markdown syntax
        main_text = re.sub(r"^#.*$", "", main_content, flags=re.MULTILINE).strip()
        # Remove specific Unicode whitespace and non-breaking space characters
        main_text = re.sub(r"[\u202f\xa0]", " ", main_text)
        # Normalize multiple newlines, possibly followed by backslashes, to a single newline
        main_text = re.sub(r"\n+\\*\n*", " ", main_text)
        # Normalize multiple newlines, possibly followed by backslashes, to a single newline
        main_text = re.sub(r"\*\*\\", " ", main_text)

        main_text = remove_markdown_syntax(main_text)

        return {
            "url": frontmatter["Url"],
            "heading": heading,
            "word_count": len(main_text.split()),
            "char_count": len(main_text),
            "Emotions": NRCLex(main_text).raw_emotion_scores,
        }


def top_ten_frequent_words(text):
    # Tokenize the text into words
    words = word_tokenize(text)

    # Create a frequency distribution
    freq_dist = Counter(words)

    # Find the ten most common words
    top_ten = freq_dist.most_common(10)

    return top_ten


def top_ten_frequent_nouns(text, language="german"):
    # Set the stopwords for the specified language
    stop_words = set(stopwords.words(language))

    # Tokenize the text
    tokens = word_tokenize(text, language=language)

    # Filter out stopwords
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

    # Perform POS tagging on the filtered tokens
    tagged_tokens = pos_tag(filtered_tokens)

    # Filter for nouns (NN for singular noun, NNS for plural nouns, include proper nouns if desired)
    nouns = [word for word, tag in tagged_tokens if tag in ("NN", "NNS", "NNP", "NNPS")]

    # Count and return the ten most common nouns
    freq_dist = Counter(nouns)
    top_ten_nouns = freq_dist.most_common(10)

    return top_ten_nouns


def analyze_text_sentiment(text, lexicon):
    # Tokenize the input text
    tokens = word_tokenize(text, language="german")

    # Initialize a structure to hold aggregated sentiment scores
    sentiment_scores = {}

    # Analyze each token
    for token in tokens:
        if token.lower() in lexicon:
            for sentiment_type, strength in lexicon[token.lower()]:
                if sentiment_type in sentiment_scores:
                    sentiment_scores[sentiment_type] += strength
                else:
                    sentiment_scores[sentiment_type] = strength

    return sentiment_scores


# file_path = "data/Klimaschutzgesetz - Fridays For Future Austria.md"
# result = parse_markdown_with_frontmatter(file_path)
# print(result)


with open("data/sitemaps/fff_sitemap.json", "r", encoding="utf-8") as file:
    data = json.load(file)

urls = data["urlset"]["url"]

results = []

i = 0
for url in urls:
    if i < 10:
        main_text = parse_blog_article(url["loc"])["article"]
        result_dict = {
            "url": url["loc"],
            "emotions": NRCLex(main_text).raw_emotion_scores,
            "ten_most_freuquent_nouns": top_ten_frequent_nouns(main_text),
            "sentiment_analysis": analyze_text_sentiment(main_text, load_sentiments()),
        }
        results.append(result_dict)
        print(result_dict)
        i += 1
    else:
        pass


with open("output.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)
