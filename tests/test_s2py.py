from s2py import S2Client


def test_s2_client():
    cli = S2Client()

    paper = cli.fetch_from_arxiv_id("1805.09547")
    assert (
        paper.title
        == "Interpretable and Compositional Relation Learning by Joint Training with an Autoencoder"
    )
    assert paper.authors[0] == "Ryo Takahashi"

    paper_by_s2id = cli.fetch_from_s2_id("d0d084fb94c54a9d7cb468cacb6f69d257d3ca49")
    assert paper == paper_by_s2id

    paper_by_exact_search = cli.search_exact(
        "Interpretable and Compositional Relation Learning by Joint Training with an Autoencoder",
        "Ryo Takahashi",
    )
    assert paper == paper_by_exact_search

    paper_by_best_search = cli.search_best(
        "Interpretable and Compositional Relation Learning"
    )
    assert paper == paper_by_best_search