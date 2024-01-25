from typing import Union
import numpy as np


class MetricFormatter:
    """
    TODO: Auto period for large number
    """

    @staticmethod
    def round(number: Union[int, float], decimals: int = 2) -> str:
        return np.round(number, decimals).astype(str)

    @staticmethod
    def percent(number: Union[int, float], decimals: int = 2) -> str:
        return np.round(number * 100, decimals).astype(str) + "%"

    @staticmethod
    def dollar(
        number: Union[int, float], decimals: int = 2, dollar_sign: str = "$"
    ) -> str:
        return (
            ("" if number >= 0 else "-")
            + dollar_sign
            + np.round(abs(number), decimals).astype(str)
        )
