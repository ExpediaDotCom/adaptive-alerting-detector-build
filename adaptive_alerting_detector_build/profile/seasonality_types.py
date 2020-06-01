from dataclasses import dataclass


@dataclass
class SeasonalityResult:
    is_seasonal: bool
    period: int

@dataclass
class SeasonalityReport:
    is_seasonal: bool
    seasonality_display: str
    test_seasonal_display: str
