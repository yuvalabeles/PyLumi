from dataclasses import dataclass
from typing import Any


@dataclass
class LumiAnalysisResult:
    group_results: dict[str, dict[str, Any]]
    full_dfs: list
    groups: dict[str, list[str]]
    config: dict
    complete_df: Any = None
    condensed_df: Any = None
