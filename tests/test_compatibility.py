def test_legacy_serializers_import_on_supported_python():
    from subjects import loli, tmarsh

    assert loli.name == 'Lollipop'
    assert tmarsh.name == 'Toasted Marshmallow'
