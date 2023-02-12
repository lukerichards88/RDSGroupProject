try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
with open('sports_names.txt') as file:
    sports = list(line.strip() for line in file)
results = {}
for n, sport in enumerate(sports):
    query = f"who are the best {sport} players of all time?"
    x = search(query, tld="co.uk", num=5, stop=10, pause=2)
    results[sport] = list(x)
    print(f"Query for {sport} complete. {n} out of 40.")
with open('who_is_the_best.txt', 'w') as file:
    for sport, result in results.items():
        file.write(f"{sport}\n")
        for link in result:
            file.write(f"{link}\n")
