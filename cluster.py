import re

import nltk
import pandas as pd
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from utils import csv_reader, csv_writer, prepare_csv_file


def preprocess_text(text: str, remove_stopwords: bool) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub("[^A-Za-z]+", " ", text)
    if remove_stopwords:
        tokens = nltk.word_tokenize(text)
        tokens = [w for w in tokens if not w.lower() in stopwords.words("english")]
        text = " ".join(tokens)
    text = text.lower().strip()
    return text


if __name__ == '__main__':
    content_csv_file_path = 'content.csv'
    content_csv_writer = csv_writer(content_csv_file_path)
    content_csv_reader = csv_reader(content_csv_file_path)
    content_csv_rows = prepare_csv_file(content_csv_reader, content_csv_writer, ['repo', 'path', 'content'])
    dummy_csv_file_path = 'dummy.csv'
    dummy_csv_writer = csv_writer(dummy_csv_file_path, mode='w')
    dummy_csv_reader = csv_reader(dummy_csv_file_path)
    dummy_csv_rows = prepare_csv_file(dummy_csv_reader, dummy_csv_writer, ['content', 'cluster'])
    contents = []
    decoded_contents = []
    for row in content_csv_rows:
        path = row[1].lower()
        if path == 'security.md' or path == '.github/security.md' or path == 'docs/security.md':
            if row[2] not in contents:
                contents.append(row[2])
                decoded_contents.append(eval(row[2]).decode('utf-8'))
    df = pd.DataFrame(decoded_contents, columns=['corpus'])
    df['cleaned'] = df['corpus'].apply(lambda x: preprocess_text(x, remove_stopwords=True))
    vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.95)
    x = vectorizer.fit_transform(df['cleaned'])
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(x)
    clusters = kmeans.labels_
    for i in range(len(contents)):
        dummy_csv_writer.writerow([contents[i], clusters[i]])

