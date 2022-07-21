from .db import db, ma

# create a database table Video


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.Text, unique=True, nullable=False)
    path = db.Column(db.Text, unique=True, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    vid_duration = db.Column(db.Float, nullable=False)
    vid_size = db.Column(db.Float, nullable=False)
    vid_type = db.Column(db.Text, nullable=False)

# create a schema for json which import properties from db table video


class VideoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Video
