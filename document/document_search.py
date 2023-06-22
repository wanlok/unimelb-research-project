import os
import sys

sys.path.append('C:\\Files\\Projects\\unimelb-research-project')

from utils import contain_string

from docx import Document

from document_utils import get_lines, directory_paths, ignored_file_names, get_categories, get_headers_and_paragraphs


if __name__ == '__main__':
    # text = 'take the security of our software products and services seriously'
    # text = 'consider vulnerabilities leading to the compromise'
    # text = 'threat model'
    # text = 'process is to reduce the total time users are vulnerable to publicly known exploits'
    if len(sys.argv) > 2:
        mode = int(sys.argv[1])
        text = ' '.join(sys.argv[2:])
        file_number = 0
        for directory_path in directory_paths:
            for file_name in os.listdir(directory_path):
                if file_name not in ignored_file_names:
                    file_path = f'{directory_path}{file_name}'
                    f = open(file_path, 'rb')
                    table = Document(f).tables[0]
                    category_lines = get_lines(table, 0)
                    content_lines = get_lines(table, 1)
                    if mode == 0 and text.lower() in category_lines.lower():
                        file_number = file_number + 1
                        print(f'{file_number} {file_path}')
                    elif mode == 1 and text.lower() in content_lines.lower():
                        file_number = file_number + 1
                        print(f'{file_number} {file_path}')
                    else:
                        categories = get_categories(category_lines)
                        headers, paragraphs = get_headers_and_paragraphs(content_lines)
                        if mode == 2:
                            for i in range(len(categories)):
                                if contain_string(text, categories[i], True) and len(categories[i]) == 1:
                                    file_number = file_number + 1
                                    print(f'{file_number} {file_path} {categories[i]}')
                        elif mode == 3:
                            found = False
                            for i in range(len(paragraphs)):
                                if text.lower() in paragraphs[i].lower():
                                    found = True
                                    break
                            if found:
                                file_number = file_number + 1
                                print(f'{file_number} {file_path} {categories[i]}')

                        elif mode == 4:
                            found = False
                            for i in range(len(categories)):
                                first = False
                                paragraph = paragraphs[i]
                                for j in range(len(categories[i])):
                                    if text.lower() in categories[i][j].lower():
                                        if len(categories[i]) > 1:
                                            print(f'{file_path} {categories[i]}')
                                        # print()
                                        # print(f'{header}')
                                        # print(f'{paragraph}')
                                        # print()
                                        found = True
                                        # break
                            # if found:
                            #     file_number = file_number + 1
                            #     print(f'{file_number} {file_path}')

                    f.close()
