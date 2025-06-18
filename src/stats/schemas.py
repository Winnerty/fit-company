from marshmallow import Schema, fields

class WorkoutStatSchema(Schema):
    user_id = fields.Str(required=True)
    date = fields.Str(required=True)
    workout_type = fields.Str(required=True)
    exercises = fields.List(fields.Int(), required=True)
