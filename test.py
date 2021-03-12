from s2py import S2Client

cli = S2Client()
paper = cli.search_best("Interpretable and Compositional Relation Learning")
print(paper)