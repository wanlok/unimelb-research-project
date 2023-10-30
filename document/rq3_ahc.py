import difflib
import os

import numpy as np
from matplotlib import pyplot as plt
from nltk import corpus
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from document.hierarchical_agglomerative_clustering import write_csv, read_csv, plot_dendrogram, get_tree, \
    get_largest_gaps, traverse, flatten_list
from document.rq3 import get_contents, cccc, longest_common_subsequence, get_tf_list, get_idf_dict
from utils import csv_reader, csv_writer, sort_by_descending_values
import scipy.cluster.hierarchy as sch


def get_change_tf_idf_list(changes):
    change_tf_idf_list = []
    sentences = [x[3] for x in changes]
    tf_list = get_tf_list(sentences)
    idf_dict = get_idf_dict(sentences)
    for i in range(len(changes)):
        tf_idf_list = [(word, tf_list[i][word] * idf_dict[word]) for word in tf_list[i]]
        tf_idf_list = list(filter(lambda x: len(x[0]) > 1 and x[1] > 0, tf_idf_list))
        tf_idf_list.sort(key=lambda x: x[1], reverse=True)
        change_tf_idf_list.append([changes[i][0], changes[i][1], changes[i][2], tf_idf_list])
    return change_tf_idf_list


def get_clusters(changes):
    names = []
    new_contents = []
    content_dict = dict()
    for file_name, date_time_string, tf_idf_list in changes:
        content = ' '.join([x[0] for x in tf_idf_list])
        if content in content_dict:
            content_dict[content].append((file_name, date_time_string))
        else:
            content_dict[content] = [(file_name, date_time_string)]
    for key in content_dict:
        name = f'"{content_dict[key]}"'
        names.append(name)
        new_contents.append((name, key))
    write_csv(names, new_contents)
    X = read_csv()
    plot_dendrogram(X)
    if len(X) > 0:
        names = list(map(lambda x: eval(eval(x)), names))
        if sum(sum(X)) > 1:
            tree_nodes = [[x[0], x[1], x[3]] for x in sch.dendrogram(sch.linkage(X, method='single'))['dcoord']]
            tree_root_node = None
            for tree_node in tree_nodes:
                if tree_root_node is None or tree_node[1] > tree_root_node[1]:
                    tree_root_node = tree_node
            clusters = []
            tree = get_tree(tree_root_node, [] + tree_nodes)
            traverse(tree, get_largest_gaps(tree), clusters)
            for i in range(len(names)):
                for j in range(len(names[i])):
                    names[i][j] = (names[i][j], clusters[i], max(clusters) + 1)
        else:
            for i in range(len(names)):
                for j in range(len(names[i])):
                    names[i][j] = (names[i][j], 0, 1)
        clusters = flatten_list(names)
    else:
        clusters = []
    return clusters


def elbow():
    changes = []
    for file_name, date_time_string, content in csv_reader(csv_file_path):
        content = [x[0] for x in eval(content)]
        print(content)
        changes.append((file_name, date_time_string, ' '.join(content)))

    # for change in changes:
    #     print(change)

    documents = [x[2] for x in changes]

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    # svd = TruncatedSVD(n_components=2).fit(documents)
    # reduced = svd.transform(documents)
    #
    # print(corpus[np.argmax(reduced)])

    # WCSS values for different numbers of clusters
    wcss = []

    # Try different values of K (number of clusters)
    K = 32
    for i in range(1, K):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(tfidf_matrix)
        wcss.append(kmeans.inertia_)  # Inertia is the WCSS value

    # Plot the elbow method graph
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, K), wcss, marker='o', linestyle='-', color='b')
    plt.title('Elbow Method for Optimal K')
    plt.xlabel('Number of Clusters (K)')
    plt.ylabel('WCSS (Within-Cluster Sum of Squares)')
    plt.grid()
    plt.show()


csv_file_path = 'C:\\Files\\preprocess_4.csv'


def get_modification(diff):
    # Initialize a flag to track whether the first '-' or '+' is encountered
    first_change_encountered = False

    # Initialize a list to store the sentences
    sentences = []

    # Iterate through the differences
    for line in diff:
        if line.startswith(' '):
            # This is a common line; continue accumulating text
            if first_change_encountered:
                sentences[-1] += " " + line
        elif line.startswith('-') or line.startswith('+'):
            # This is a line with a change
            if not first_change_encountered:
                # Mark that the first change has been encountered
                first_change_encountered = True
            # Append the changed line to the list of sentences
            sentences.append(line)

    return sentences


def data_preprocessing():
    directory_path = 'C:\\Files\\security policies\\'
    writer = csv_writer(csv_file_path, mode='w')
    count = 0
    for file_name in os.listdir(directory_path):
        # if file_name[0] in ['A''] and file_name not in ['ethereum_go-ethereum.csv', 'v2fly_v2ray-core.csv', 'v2ray_v2ray-core.csv']:
        # if file_name not in ['ethereum_go-ethereum.csv', 'v2fly_v2ray-core.csv', 'v2ray_v2ray-core.csv']:
        # if file_name == 'AzureAD_microsoft-authentication-library-for-js.csv':
        # if file_name[0] in ['a']:
        if True:
            changes = []
            contents = get_contents(directory_path, file_name)
            for i in range(1, len(contents)):
                sha = contents[i][2]
                date_time_string = contents[i][3]
                content = cccc(file_name, contents[i][5])
                changes.append((file_name, sha, date_time_string, content))
            changes = get_change_tf_idf_list(changes)
            for change in changes:
                writer.writerow(change)
    print(count)


def get_changes():
    changes = []
    for file_name, sha, date_time_string, tf_idf_list in csv_reader(csv_file_path):
        tf_idf_list = eval(tf_idf_list)
        changes.append((file_name, sha, date_time_string, tf_idf_list))
    return changes


def bbb(chosen_k):
    changes = get_changes()

    for change in changes:
        print(change)

    documents = [x[2] for x in changes]

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    kmeans = KMeans(n_clusters=chosen_k, init='k-means++', max_iter=300, n_init=10, random_state=0)
    # kmeans.fit(tfidf_matrix)

    pca = PCA(n_components=3)  # You can change n_components to 3 for a 3D plot
    reduced_data = pca.fit_transform(tfidf_matrix.toarray())

    cluster_assignments = kmeans.fit_predict(reduced_data)



    # cluster_assignments = kmeans.predict(tfidf_matrix)

    for i in range(chosen_k):
        cluster_docs = [changes[j] for j in range(len(cluster_assignments)) if cluster_assignments[j] == i]
        print(f"Cluster {i + 1} {len(cluster_docs)}:")
        # if i == 22:
        #     for doc in cluster_docs:
        #         print(doc)
        print("\n")


    # Create a scatter plot
    plt.figure(figsize=(8, 6))
    for cluster in range(chosen_k):
        plt.scatter(reduced_data[cluster_assignments == cluster, 0], reduced_data[cluster_assignments == cluster, 1],
                    label=f'Cluster {cluster + 1}')

    plt.title('K-Means Clustering of Text Data')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend()
    plt.show()


def aaa():
    # data_preprocessing()
    changes = get_changes()
    # keyword_dict = dict()
    # for change in changes:
    #     # print(change)
    #     keywords = change[3]
    #     for keyword in keywords:
    #         keyword = keyword[0]
    #     #     print(keyword)
    #         if keyword in keyword_dict:
    #             keyword_dict[keyword] = keyword_dict[keyword] + 1
    #         else:
    #             keyword_dict[keyword] = 1
    # keyword_dict = sort_by_descending_values(keyword_dict)
    # for keyword in keyword_dict:
    #     print(f'{keyword} {keyword_dict[keyword]}')





    # elbow()
    bbb(3)





    # changes = []
    # for file_name, _, date_time_string, content, _ in csv_reader(csv_file_path):
    #     changes.append((file_name, date_time_string, content))
    #
    # for file_name, date_time_string, tf_idf_list in get_change_tf_idf_list(changes):
    #     tf_idf_list = list(map(lambda x: x[0], tf_idf_list))
    #     print((file_name, date_time_string, ' '.join(tf_idf_list)))
    #
    # clusters = get_clusters(changes)
    # for cluster in clusters:
    #     print(cluster)




if __name__ == '__main__':
    aaa()
