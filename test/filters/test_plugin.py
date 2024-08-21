from geant_argus.geant_argus.filters.plugin import FilterSerializer


def test_filter_serializer():
    serializer = FilterSerializer(data={"name": "bla", "filter": {"some": "filter"}})
    assert serializer.is_valid()
    assert serializer.data["filter"] == {"some": "filter"}
