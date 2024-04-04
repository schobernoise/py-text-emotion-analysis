import os
import csv

# Directory where your sentiment files are located
sentiment_files_dir = "D:\DEV\Python\_external_projects_\german-sentiment-lexicon\data\emotions regularized"


def load_sentiments():
    # Initialize a dictionary to hold the sentiment lexicon
    sentiment_lexicon = {}

    # Iterate over each file in the directory
    for filename in os.listdir(sentiment_files_dir):
        if filename.endswith(".txt"):  # Assuming the files are .txt format
            # Extract sentiment type from the filename (e.g., 'freude.txt' -> 'freude')
            sentiment_type = filename[:-4]

            with open(
                os.path.join(sentiment_files_dir, filename), "r", encoding="utf-8"
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    word, strength = row[0], float(row[1])
                    if word in sentiment_lexicon:
                        sentiment_lexicon[word].append((sentiment_type, strength))
                    else:
                        sentiment_lexicon[word] = [(sentiment_type, strength)]

    return sentiment_lexicon
