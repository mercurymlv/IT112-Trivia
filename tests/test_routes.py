import pytest
from app import app
from app import load_questions


@pytest.fixture
def client():
    # set up test client
    app.testing = True
    return app.test_client()


# easy peasy test - make sure index is up
def test_home_route(client):
    # test home route
    response = client.get('/')
    assert response.status_code == 200

# check login for SQL injection attacks
def test_sql_inject_login(client):
    inject_text = "' OR '1'='1'; --"
    response = client.post("/", data={"username": "admin", "password": inject_text}, follow_redirects=True)
    print(response.data.decode())
    # The login should fail
    # page load should be fine (200) but display flash message
    assert response.status_code == 200
    assert b"Sign up here" in response.data


# check that the db returns questions and in right format
def test_load_questions_returns_data():
    questions = load_questions()
    
    # should return a list
    assert isinstance(questions, list)
    
    # check the key values from dict
    if questions:
        first = questions[0]
        expected_keys = {"quest_id", "quest_type", "quest_text", "quest_ans", "options"}
        assert expected_keys.issubset(first.keys())
        


