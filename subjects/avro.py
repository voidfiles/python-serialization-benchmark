import avro.schema
from avro.io import DatumWriter

__name__ = 'Avro'

class NullWriter(object):
    def write(self, *args, **kwargs):
        pass

    def write_utf8(self, *args, **kwargs):
        self.write(args, kwargs)

    def write_int(self, *args, **kwargs):
        self.write(args, kwargs)

    def write_long(self, *args, **kwargs):
        self.write(args, kwargs)

schema_name_tracker = avro.schema.Names()

child_test_object_schema = avro.schema.SchemaFromJSONData({
    "namespace": "benchmark.avro",
    "type": "record",
    "name": "childTestObject",
    "fields": [
        {"name": "w", "type": "int"},
        {"name": "x", "type": "int"},
        {"name": "y", "type": "string"},
        {"name": "z", "type": "int"}
    ]
}, names=schema_name_tracker)

parent_test_object_schema = avro.schema.SchemaFromJSONData({
    "namespace": "benchmark.avro",
    "type": "record",
    "name": "parentTestObject",
    "fields": [
        {"name": "foo", "type": "string"},
        {"name": "sub", "type": "childTestObject"},
        {
            "name": "subs",
            "type": {
                "type": "array",
                "items": "childTestObject"
            }
        }
    ]
}, names=schema_name_tracker)

datum_writer = DatumWriter(writer_schema=parent_test_object_schema)
null_binary_writer = NullWriter()

# Avro for Python can't directly serialize a class, it must be a dictionary.
def nested_class_to_dict(obj):
    if not hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(nested_class_to_dict(item))
        else:
            element = nested_class_to_dict(val)
        result[key] = element
    return result

def serialization_func(to_serialize, many):
    if many:
        return [datum_writer.write(nested_class_to_dict(obj), null_binary_writer) for obj in to_serialize]
    else:
        return datum_writer.write(nested_class_to_dict(to_serialize), null_binary_writer)
