import colander
from colander import null

__name__ = 'Colander'


class ObjectType(colander.Mapping):
    """
    A colander type representing a generic python object
    (uses colander mapping-based serialization).
    """

    def serialize(self, node, appstruct):
        appstruct = appstruct.__dict__
        return super(ObjectType, self).serialize(node, appstruct)

    def deserialize(self, node, cstruct):
        data = super(ObjectType, self).deserialize(node, cstruct)
        appstruct = node.instance.__class__()
        appstruct.__dict__.update(data)
        return appstruct


class ObjectSchema(colander.SchemaNode):
    schema_type = ObjectType
    instance = None

    def serialize(self, appstruct):
        if not self.instance:
            # set the instance on all child schema nodes as they
            # may need to access the instance environment
            self.instance = appstruct
            for subnode in self.children:
                if isinstance(subnode, MethodSchema):
                    setattr(subnode, 'instance', appstruct)
        return super(ObjectSchema, self).serialize(appstruct)

    def deserialize(self, cstruct):
        appstruct = super(ObjectSchema, self).deserialize(cstruct)
        if not self.instance:
            self.instance = appstruct
        return appstruct


class CallableSchema(colander.SchemaNode):
    def serialize(self, appstruct):
        if appstruct is null:
            return null
        appstruct = appstruct()
        return super(CallableSchema, self).serialize(appstruct)

    def deserialize(self, cstruct):
        if cstruct is null:
            return null
        appstruct = super(CallableSchema, self).deserialize(cstruct)
        return lambda: appstruct


class MethodSchema(CallableSchema):
    def serialize(self, appstruct):
        if appstruct is null:
            appstruct = getattr(self.instance, self.name)
        return super(MethodSchema, self).serialize(appstruct)


class Differential(colander.SchemaNode):
    def __init__(self, typ, differential=0):
        self.differential = differential
        super(Differential, self).__init__(typ)

    def serialize(self, appstruct):
        # operator could be overloaded by the appstruct class if necessary
        appstruct += self.differential
        return super(Differential, self).serialize(appstruct)

    def deserialize(self, cstruct):
        # operator could be overloaded by the appstruct class if necessary
        appstruct = super(Differential, self).deserialize(cstruct)
        appstruct -= self.differential
        return appstruct


class ChildSchema(ObjectSchema):
    w = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.String())
    x = Differential(colander.Int(), 10)
    z = colander.SchemaNode(colander.Int())


class ChildListSchema(colander.SequenceSchema):
    sub = ChildSchema()


class ParentSchema(ObjectSchema):
    foo = colander.SchemaNode(colander.String())
    bar = MethodSchema(colander.Int())
    sub = ChildSchema()
    subs = ChildListSchema()


class ParentListSchema(colander.SequenceSchema):
    parents = ParentSchema()


unit_schema = ParentSchema()
seq_schema = ParentListSchema()


def serialization_func(obj, many):
    schema = seq_schema if many else unit_schema
    return schema.serialize(obj)
