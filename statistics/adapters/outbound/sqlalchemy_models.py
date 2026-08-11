from datetime import datetime
from shared.adapters.outbound.database import db

class CalculationHistory(db.Model):
    __tablename__ = "calculation_history"
    id = db.Column(db.Integer, primary_key=True)
    formula_name = db.Column(db.String(120), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "formula_name": self.formula_name,
            "input_data": self.input_data,
            "result": self.result,
            "created_at": self.created_at.isoformat(),
        }
