"""Structured validation result."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.errors

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_score(self, name: str, value: float) -> None:
        self.scores[name] = max(0.0, min(1.0, float(value)))

    def to_markdown(self) -> str:
        errors = "none" if not self.errors else "; ".join(self.errors)
        warnings = "none" if not self.warnings else "; ".join(self.warnings)
        scores = "\n".join(f"- {name}: {value:.3f}" for name, value in self.scores.items())
        return (
            f"- Passed: {str(self.passed).lower()}\n"
            f"- Errors: {errors}\n"
            f"- Warnings: {warnings}\n"
            f"{scores}"
        ).rstrip()
