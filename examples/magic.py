
my_method = SomeClass()['first']

db.define_table(
    "person",
    Field(
        "name",
        "string",
        nullable=False,
        default=my_method.new_uuid()
    ),
    Field("birthday", "datetime", default=datetime.datetime.utcnow()),
)

db_type = "sqlite"
