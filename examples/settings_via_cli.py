db.define_table(
    "person",
    Field(
        "name",
        "string",
        nullable=False,
    ),
    Field("age", "integer", default=18),
    Field("float", "decimal(2,3)"),
    Field("nicknames", "list:string"),
    Field("obj", "json"),
)

db.define_table("empty")

tables = ["person"]
