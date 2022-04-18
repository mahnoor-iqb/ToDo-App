
def test_new_user(new_user):
    assert new_user.email == "jane.doe@gmail.com"
    
    # Password must be hashed
    assert new_user.password != "ThisIsMyTestPassword."
