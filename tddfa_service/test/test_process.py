from ..main import process_video


def test_process_frames_count():
    matrices = process_video('./resources/test13.mp4')
    # 5 sec, 10 fps
    assert len(matrices) == 50
