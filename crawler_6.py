import json

if __name__ == '__main__':
    dummy = json.load(open('secret.json'))
    print(dummy['password'])
