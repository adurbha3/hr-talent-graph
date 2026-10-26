from talentgraph.skill_extraction import extract_skills


def test_extracts_exact_phrase_matches():
    skills = extract_skills("I have strong Python and SQL skills, plus data analysis experience.")
    assert "python" in skills
    assert "sql" in skills
    assert "data analysis" in skills


def test_extracts_known_abbreviations():
    skills = extract_skills("I led the team as PM and have some ML background.")
    assert "project management" in skills
    assert "machine learning" in skills


def test_does_not_extract_unrelated_words():
    skills = extract_skills("I enjoy hiking and photography on weekends.")
    assert skills == []


def test_fuzzy_matching_catches_minor_typos():
    skills = extract_skills("I am skilled in pythom programming.")
    assert "python" in skills
