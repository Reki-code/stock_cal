from abc import ABC, abstractmethod
from typing import Any


class DataLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> dict[str, list[dict[str, Any]]]:
        """Load data from file and return structured data.
        
        Returns:
            dict with keys:
            - 'trades': list of trade records
            - 'dividends': list of dividend records
            - 'withholdings': list of withholding tax records
        """
        pass
