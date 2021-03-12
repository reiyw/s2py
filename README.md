# s2py

Unofficial Python API for Semantic Scholar.

```
pip install s2py
```

```python
>>> from s2py import S2Client
>>> cli = S2Client()
>>> cli.search_best("Interpretable and Compositional Relation Learning")
S2Paper(id='d0d084fb94c54a9d7cb468cacb6f69d257d3ca49', title='Interpretable and Compositional Relation Learning by Joint Training with an Autoencoder', authors=['Ryo Takahashi', 'R. Tian', 'Kentaro Inui'], abstract='Embedding models for entities and relations are extremely useful for recovering missing facts in a knowledge base. Intuitively, a relation can be modeled by a matrix mapping entity vectors. However, relations reside on low dimension sub-manifolds in the parameter space of arbitrary matrices---for one reason, composition of two relations $\\boldsymbol{M}_1,\\boldsymbol{M}_2$ may match a third $\\boldsymbol{M}_3$ (e.g. composition of relations currency_of_country and country_of_film usually matches currency_of_film_budget), which imposes compositional constraints to be satisfied by the parameters (i.e. $\\boldsymbol{M}_1\\cdot \\boldsymbol{M}_2\\approx \\boldsymbol{M}_3$). In this paper we investigate a dimension reduction technique by training relations jointly with an autoencoder, which is expected to better capture compositional constraints. We achieve state-of-the-art on Knowledge Base Completion tasks with strongly improved Mean Rank, and show that joint training with an autoencoder leads to interpretable sparse codings of relations, helps discovering compositional constraints and benefits from compositional training. Our source code is released at this http URL.', year=2018, venue='ACL', url='https://www.semanticscholar.org/paper/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49', arxiv_id='1805.09547', arxiv_url='https://arxiv.org/abs/1805.09547', figure_urls=['https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/1-Figure1-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/6-Figure2-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/8-Figure3-1.png'], table_urls=['https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/6-Table1-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/7-Table2-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/8-Table3-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/9-Table4-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/9-Table5-1.png', 'https://d3i71xaburhd42.cloudfront.net/d0d084fb94c54a9d7cb468cacb6f69d257d3ca49/12-Table6-1.png'])
```
