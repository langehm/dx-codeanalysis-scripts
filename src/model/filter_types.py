from dataclasses import dataclass
from typing import Optional, Dict, Set


@dataclass
class RepositoryFilterOptions:
    include_forks: Optional[bool] = None
    include_archived: Optional[bool] = None
    include_disabled: Optional[bool] = None
    include_template: Optional[bool] = None


@dataclass
class RepositoryCategoryConfig:
    threshold_percent: int
    categories: Dict[str, Set[str]]