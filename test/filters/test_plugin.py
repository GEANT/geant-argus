from geant_argus.geant_argus.filters.plugin import FilterSerializer


def test_filter_serializer():
    filter_data = {
        "version": "v1",
        "type": "rule",
        "field": "some field",
        "operator": "op",
        "value": "val",
    }
    serializer = FilterSerializer(
        data={
            "name": "bla",
            "filter": filter_data,
        }
    )
    assert serializer.is_valid()
    assert serializer.data["filter"] == filter_data
