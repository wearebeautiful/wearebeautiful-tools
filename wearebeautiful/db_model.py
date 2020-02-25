from peewee import *
import dateutil.parser
from wearebeautiful.manifest import make_code

db = SqliteDatabase(None)

def create_from_manifest(manifest):
    return DBModel.create(
        model_id = manifest['id'],
        code = make_code(manifest=manifest).split('-')[1],
        created = dateutil.parser.parse(manifest['created']),
        processed = dateutil.parser.parse(manifest['processed']),
        released = dateutil.parser.parse(manifest['released']),
        gender = manifest['gender'],
        gender_comment = manifest.get('gender_comment', ''),
        body_type = manifest['body_type'],
        body_part = manifest['body_part'],
        pose = manifest['pose'],
        mother = manifest['mother'],
        arrangement = manifest['arrangement'],
        excited = manifest['excited'],
        tags = ",".join(manifest.get('tags', '')),
        modification = ",".join(manifest.get('modification', '')),
        comment = manifest.get('comment', "")
    )


class DBModel(Model):
    """
    Manifest metadata about a 3D model
    """

    class Meta:
        database = db
        table_name = "model"

    id = AutoField()
    model_id = TextField()
    code = TextField()
    created = DateField()
    released = DateField()
    processed = DateField()
    gender = TextField()
    gender_comment = TextField(null = False)
    body_type = TextField()
    body_part = TextField()
    pose = TextField()
    mother = TextField()
    arrangement = TextField()
    excited = TextField()
    tags = TextField(null = False)
    modification = TextField(null = False)
    comment = TextField(null = False)

    def __repr__(self):
        return "<DBModel(%s-%s)>" % (self.code, str(self.processed))

