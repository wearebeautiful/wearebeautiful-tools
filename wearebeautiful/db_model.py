from peewee import *
import dateutil.parser
from wearebeautiful.manifest import make_code

db = SqliteDatabase(None)

def create_from_manifest(manifest):
    return DBModel.create(
        model_id = manifest['id'],
        code = make_code(manifest=manifest).split('-')[1],
        version = manifest['version'],
        created = manifest['created'],
        released = dateutil.parser.parse(manifest['released']),
        gender = manifest['gender'],
        gender_comment = manifest.get('gender_comment', ''),
        sex = manifest['sex'],
        sex_comment = manifest.get('sex_comment', ''),
        body_type = manifest['body_type'],
        body_part = manifest['body_part'],
        pose = manifest['pose'],
        given_birth = manifest['given_birth'],
        arrangement = manifest['arrangement'],
        excited = manifest['excited'],
        tags = ",".join(manifest.get('tags', '')),
        history = ",".join(manifest.get('history', '')),
        links = " ".join(manifest.get('links', '')),
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
    version = IntegerField()
    code = TextField()
    created = TextField()
    released = DateField()
    gender = TextField()
    gender_comment = TextField(null = False)
    sex = TextField()
    sex_comment = TextField(null = False)
    body_type = TextField()
    body_part = TextField()
    pose = TextField()
    given_birth = TextField()
    arrangement = TextField()
    excited = TextField()
    tags = TextField(null = False)
    history = TextField(null = False)
    links = TextField(null = False)
    comment = TextField(null = False)

    def __repr__(self):
        return "<DBModel(%s-%s)>" % (self.code, str(self.processed))
