from src.cleaning import clean_text, make_dedup_key


def test_clean_text_html_and_spaces():
    raw = "<p>Python&nbsp;&amp;  SQL</p>\n\n\n\nR&eacute;sum&eacute;"
    assert clean_text(raw) == "Python & SQL \n\nRésumé"


def test_clean_text_empty():
    assert clean_text(None) is None
    assert clean_text("") == ""


def test_dedup_key_ignores_case_accents_punctuation():
    a = make_dedup_key("Développeur Python (H/F)", "ACME", "75 - Paris")
    b = make_dedup_key("developpeur python h f", "Acme", "75 paris")
    assert a == b