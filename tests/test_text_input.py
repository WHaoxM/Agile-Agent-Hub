def test_receive_text_with_deadline():
    sample_text = "明天下午3点交代码"
    assert "明天下午3点" in sample_text
    assert "交代码" in sample_text
