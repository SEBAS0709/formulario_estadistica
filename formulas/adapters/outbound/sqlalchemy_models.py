from shared.adapters.outbound.database import db

class Formula(db.Model):
    __tablename__ = "formulas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    expression = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    variables = db.Column(db.Text, nullable=False)
    inputs = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=True)
    favorite = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "expression": self.expression,
            "description": self.description,
            "purpose": self.purpose,
            "variables": self.variables,
            "inputs": self.inputs,
            "example": self.example,
            "favorite": self.favorite,
        }
