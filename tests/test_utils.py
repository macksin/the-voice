import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app


def test_fix_all_hyphenation_order():
    text = "This is a hy-\nphenated line."  # hyphenation across newline
    # Using the all-fix pathway
    data = {"text": text, "fix_type": "all"}
    with app.app.test_client() as client:
        response = client.post('/fix_text', json=data)
        fixed = response.get_json()['fixed_text']

    assert fixed == "This is a hyphenated line."
