import os

from docx import Document

if __name__ == '__main__':
    directory_path = 'C:\Files\\c\\Completed\\'
    my_dict = dict()
    for file_name in os.listdir(directory_path):
        f = open(f'{directory_path}{file_name}', 'rb')
        document = Document(f)
        tables = document.tables
        if len(tables) == 1:
            columns = tables[0].columns
            if len(columns) == 2:
                cells = tables[0].columns[0].cells
                if len(cells) == 1:
                    for key in cells[0].text.split('\n'):
                        if len(key) > 0:
                            if key in my_dict:
                                my_dict[key].add(file_name)
                                # my_dict[key] = my_dict[key] + 1
                            else:
                                my_set = set()
                                my_set.add(file_name)
                                my_dict[key] = my_set
                                # my_dict[key] = 1
        f.close()
    for key in my_dict:
        print(f'\"{key}\",{my_dict[key]}')
        # print(f'\"{key}\",{len(my_dict[key])}')
