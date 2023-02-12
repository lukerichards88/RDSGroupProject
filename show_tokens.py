import hashlib
import pickle
with open('who_is_the_best.txt') as file:
    for line in file:
        if 'http' not in line:
            print(line.strip())
        else:
            filename = f"pickles/{hashlib.md5(line.strip().encode('utf-8')).hexdigest()}"
            try:
                with open(filename, 'rb') as p:
                    print()
                    TOKENS = pickle.load(p)
                    print(' '.join(TOKENS))
                    print(TOKENS.count('he'))
            except FileNotFoundError:
                print(f"{line.strip()} not found")
                continue

