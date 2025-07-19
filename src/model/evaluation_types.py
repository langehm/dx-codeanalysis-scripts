from dataclasses import dataclass, asdict


@dataclass
class LanguageDistribution:
    language: str
    bytes: int
    percentage: float

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class RepositoryCategoryResult:
    repository_name: str
    category: str

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class CategoryDistribution:
    category: str
    count: int
    percentage: float
    normalized_percentage: float

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class LanguageWrapper:
    language: str

    def to_dict(self) -> dict:
        return asdict(self)