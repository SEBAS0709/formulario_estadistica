import json

class Formula:
    def __init__(self, id, name, category, expression, description, purpose, variables, inputs, example=None, favorite=False):
        self.id = id
        self.name = name
        self.category = category
        self.expression = expression
        self.description = description
        self.purpose = purpose
        self.variables = variables
        self.inputs = inputs
        self.example = example
        self.favorite = favorite

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

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            category=data.get("category"),
            expression=data.get("expression"),
            description=data.get("description"),
            purpose=data.get("purpose"),
            variables=data.get("variables", []),
            inputs=data.get("inputs", []),
            example=data.get("example"),
            favorite=data.get("favorite", False),
        )
