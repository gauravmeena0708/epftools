class Number:
    """Simple wrapper that supports addition."""

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        return Number(self.value + other)

    def __repr__(self):
        return f"Number({self.value!r})"
