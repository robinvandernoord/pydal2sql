
my_method = SomeClass()['first']

db.define_table(
    "person",
    Field(
        "name",
        "string",
        notnull=True,
        default=my_method.new_uuid()
    ),
    Field("birthday", "datetime", default=datetime.datetime.utcnow()),
)

db.define_table("empty")

db_type = "sqlite"
