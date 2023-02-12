# Import the gensim library to use word2vec
import pickle
import json
import gensim
import os
import hashlib

"""
# Download Google's pre-trained word2vec model if it doesn't exist
import os
if not os.path.exists('GoogleNews-vectors-negative300.bin'):
    import urllib.request
    url = "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
    filename = "GoogleNews-vectors-negative300.bin.gz"
    urllib.request.urlretrieve(url, filename)
    # Import the gzip library to unzip the downloaded file
    import gzip

# Unzip the file
    with gzip.open("GoogleNews-vectors-negative300.bin.gz", "rb") as f_in:
        with open("GoogleNews-vectors-negative300.bin", "wb") as f_out:
            f_out.write(f_in.read())"""
# print("Loading the model.")
# Load the pre-trained word2vec model
# model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# print("Model loaded.")
# Tokenize the index webpage at https://www.britishswimming.org/browse-sport/swimming/olympic-swimming/
import requests
from bs4 import BeautifulSoup


def get_tokens(url: str):
    filename = hashlib.md5(url.encode('utf-8')).hexdigest()
    filename = f"pickles/{filename}"
    print(filename)
    if not os.path.exists(filename):
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            # Get all the text from the page
            text = soup.get_text()
            # Tokenize the text into words
            output_tokens = text.split()
            with open(filename, 'wb') as p:
                pickle.dump(output_tokens, p)
            return output_tokens
        except requests.exceptions.ConnectionError:
            print(f"Connection error: {url}")
            return []
    with open(filename, 'rb') as p:
        output_tokens = pickle.load(p)
        with open(f"{filename}.txt", 'w') as f:
            f.write(f"{url}\n")
            f.write('\n'.join(output_tokens))
    return output_tokens


def count_similarity_threshold(test_word: str, tokens, threshold: float) -> int:
    answer = 0
    for word in tokens:
        try:
            answer += (model.similarity(word, test_word) > threshold)
        except KeyError:
            continue
    return answer


def calculate_average_similarity(test_word: str, tokens):
    # Calculate a single score for the semantic similarity for the words on the website to the word 'male'
    # Initialize a sum to keep track of the total similarity score
    similarity_sum = 0
    # Loop through each word in the tokens list
    for word in tokens:
        try:
            # Calculate the similarity between the word and the target word 'male'
            similarity = model.similarity(word, test_word)
            similarity_sum += similarity
        except KeyError:
            # If the word is not in the vocabulary, skip it
            continue
    # Divide the similarity sum by the number of words to get the average similarity score
    average_similarity = similarity_sum / len(tokens)
    return average_similarity


def get_pronoun_count(page_tokens):
    male_pronouns = ('he', 'him', 'his')
    female_pronounds = ('she', 'her', 'hers')
    pronouns = zip(male_pronouns, female_pronounds)
    male_count = 0
    female_count = 0
    for m, f in pronouns:
        male_count += page_tokens.count(m)
        female_count += page_tokens.count(f)
    return male_count, female_count


def get_links(file):
    links = {}
    for line in file:
        line = line.strip()
        if 'http' not in line:
            links[line] = []
            sport_name = line
        else:
            links[sport_name].append(line)
    return links


def get_pronouns_for_each_link(links_dict: dict):
    progressive_pronoun_count = {}
    for sport, links in links_dict.items():
        progressive_pronoun_count[sport] = []
        for link in links:
            tokens = get_tokens(link)
            tokens = list(t.lower().strip() for t in tokens)
            progressive_pronoun_count[sport].append([*get_pronoun_count(tokens), len(tokens)])
    return progressive_pronoun_count


def designate_pages_male_female(ppc, sports):
    pronoun_biases = {}
    for sport in sports:
        male_bias = 0
        female_bias = 0
        ties = 0
        print(sport)
        for n, pc in enumerate(ppc[sport]):
            [male_bias, female_bias][pc[1] > pc[0]] += 1
            ties += (pc[0] == pc[1])
            if pc[1] > pc[0]:
                print("*******************")
            print(n + 1, pc[1] - pc[0], pc[2], pc)
        pronoun_biases[sport] = (male_bias, female_bias, ties)
    return pronoun_biases


with open("who_is_the_best.txt", 'r') as file:
    sports_links = get_links(file)
    sports = sports_links.keys()
    ppc = get_pronouns_for_each_link(sports_links)
    pronoun_bias_stats = designate_pages_male_female(ppc, sports)

exit()
with open('who_is_the_best.txt', 'r') as file:
    tokens = False
    n = 1
    for line in file:
        line = line.strip()
        if "http" in line:
            if page_count > 4:
                continue
            page_tokens = get_tokens(line)
            page_tokens = list(t.lower() for t in page_tokens)
            if page_tokens:
                print(f"PAGE {page_count + 1}:")
                for threshold in [0.9]:
                    male_words = count_similarity_threshold('male', page_tokens, threshold)
                    female_words = count_similarity_threshold('female', page_tokens, threshold)
                    if female_words + male_words > 0:
                        print(threshold, female_words, male_words, female_words - male_words)
                male_count, female_count = get_pronoun_count(page_tokens)
                print(male_count, female_count, female_count - male_count)
                s_tokens = page_tokens
                average_male_similarity = calculate_average_similarity('male', s_tokens)
                average_female_similarity = calculate_average_similarity('female', s_tokens)
                print(average_female_similarity - average_male_similarity)
            tokens += page_tokens
            page_count += 1
        else:
            if tokens:
                print("TOP 5 PAGES:")
                for threshold in [0.9]:
                    male_words = count_similarity_threshold('male', tokens, threshold)
                    female_words = count_similarity_threshold('female', tokens, threshold)
                    print(threshold, female_words, male_words, female_words - male_words)
                male_count, female_count = get_pronoun_count(tokens)
                print(male_count, female_count, female_count - male_count)
                average_male_similarity = calculate_average_similarity('male', tokens)
                average_female_similarity = calculate_average_similarity('female', tokens)
                # print(average_female_similarity - average_male_similarity)
            tokens = []
            page_count = 0
            print(n, line)
            n += 1
