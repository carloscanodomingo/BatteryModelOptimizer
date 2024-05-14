import logging
import os
import pickle
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class ModelMetrics:
    non_degradation_metric: Optional[float] = None
    degradation_metrics: Optional[float] = None
    capacity_metric: Optional[float] = None
    experimental_capacity: Optional[float] = None

    def to_dict(self):
        return {
            "non_degradation_metric": self.non_degradation_metric,
            "degradation_metrics": self.degradation_metrics,
            "capacity_metric": self.capacity_metric,
            "experimental_capacity": self.experimental_capacity,
        }


@dataclass
class ModelStatus:
    real_capacity: Optional[float] = None

    def to_dict(self):
        return {"real_capacity": self.real_capacity}


@dataclass
class PybammInfo:
    model_metrics: ModelMetrics = field(default_factory=ModelMetrics)
    model_status: ModelStatus = field(default_factory=ModelStatus)

    def to_dict(self):
        result = self.model_metrics.to_dict()
        result.update(self.model_status.to_dict())
        return result


class ArrayPybammMetrics:
    def __init__(self):
        self.info = deque()
        self._type = PybammInfo

    def set(self, index, value):
        if not isinstance(value, self._type):
            raise TypeError(
                f"Expected type {self._type.__name__}, got {type(value).__name__}"
            )
        elif index < 0:
            raise IndexError(f"Index must be a non-negative integer, got {index}")
        elif index == len(self.info):
            self.info.append(value)
        else:
            raise IndexError(
                (
                    f"Can only set the next immediate index {len(self.info)}"
                    f"attempted to set at {index}"
                )
            )

    def get(self, index) -> PybammInfo:
        """Get the value at a specific index."""
        # Check if the index is within the bounds of the array
        if 0 <= index < len(self.info):
            return self.info[index]
        else:
            # If the index is out of bounds, raise an IndexError
            raise IndexError("Index out of bounds")

    def size(self):
        """Return the number of non-default values stored in the array."""
        return len(self.info)

    def __iter__(self):
        return iter(self.info)

    def __len__(self):
        return self.size()

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    def to_dataframe(self):
        # Convert the deque of PybammMetrics objects into a list of dictionaries
        data = [info.to_dict() for info in self.info]
        # Create a DataFrame from the list of dictionaries
        return pd.DataFrame(data)
