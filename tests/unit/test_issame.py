from utils.utils import is_same

def test_is_same_true():
    description_A = "This is a description of a task"
    description_B = "This is a description of a task with more words"

    assert is_same(description_A, description_B) == True


def test_is_same_false():
    description_A = "Each Lunch"
    description_B = "Prepare a presentation"

    assert is_same(description_A, description_B) == False
