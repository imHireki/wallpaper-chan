from image import editor


def test_editor_options():
    resize_options = {"size": (512, 512), "resample": 2, "reducing_gap": 2}
    save_options = {"quality": 75, "format": "WEBP"}

    editor_options = editor.EditorOptions(**resize_options, **save_options)

    assert editor_options.resize_options == resize_options
    assert editor_options.save_options == save_options
