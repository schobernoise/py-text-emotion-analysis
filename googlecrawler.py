from googlesearch import search

results = search("site:derstandard.at klima", lang="de", advanced=True)

print(results)


for x in results:
    print(x)
