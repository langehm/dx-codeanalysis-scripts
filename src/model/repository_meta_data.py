from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class LinguisticData:
    language_distribution: Dict[str, int] = field(default_factory=dict)

    def total_lines(self) -> float:
        """Berechnet die Gesamtanzahl an Codezeilen."""
        return sum(self.language_distribution.values())

    def get_percentage(self, language: str) -> float:
        """Gibt den prozentualen Anteil einer Sprache zurück (0.0–100.0)."""
        total = self.total_lines()
        if total == 0:
            return 0.0
        return (self.language_distribution.get(language, 0.0) / total) * 100


@dataclass
class RepositoryMetaData:
    repository_name: str
    repository_owner: str
    repository_id: int
    repository_http_url: str
    repository_size: int
    linguistic_data: Dict[str, int] = field(default_factory=dict)

    def __str__(self):
        return f'{self.repository_name} {self.repository_http_url} {self.repository_size}'

    def repository_size_mb(self) -> float:
        return RepositoryMetaData.repository_size_convert_mb(self.repository_size)

    @staticmethod
    def repository_size_convert_mb(repository_size: int) -> float:
        return round(repository_size / 1024, 2)

