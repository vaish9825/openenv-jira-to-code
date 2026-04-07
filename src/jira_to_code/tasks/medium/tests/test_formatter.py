from formatter import format_user_data

def test_format_full_data():
    data = {"first_name": "john", "last_name": "doe", "age": 30}
    assert format_user_data(data) == "DOE, John (Age: 30)"

def test_format_missing_age():
    data = {"first_name": "alice", "last_name": "smith"}
    assert format_user_data(data) == "SMITH, Alice (Age: Unknown)"