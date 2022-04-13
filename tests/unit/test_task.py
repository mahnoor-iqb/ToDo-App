from datetime import datetime

def test_new_task(new_task):
    assert new_task.title == "Test Task"
    assert new_task.description == "This is a test task."
    assert new_task.creation_date == datetime.strptime(
        "2022-02-20 18:11:41", '%Y-%m-%d %H:%M:%S')
    assert new_task.due_date == datetime.strptime(
        "2022-03-20 18:11:41", '%Y-%m-%d %H:%M:%S')
    assert new_task.completion_date == None
    assert new_task.completion_status == 0
    assert new_task.user_id == 5
