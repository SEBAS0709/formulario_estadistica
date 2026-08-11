class CategoryService:
    @staticmethod
    def list_categories(formulas):
        categories = {}
        for formula in formulas:
            categories.setdefault(formula.category, []).append(formula)
        return ["category", "description"]
