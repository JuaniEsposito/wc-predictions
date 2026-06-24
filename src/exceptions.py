"""Custom exceptions for the wc-predictions pipeline."""


class WCPredictionsError(Exception):
    """Base exception for wc-predictions pipeline."""


class DataFetchError(WCPredictionsError):
    """Raised when fetching data from an external source fails."""


class DataValidationError(WCPredictionsError):
    """Raised when data does not conform to the expected schema or contract."""


class ModelTrainingError(WCPredictionsError):
    """Raised when model training fails due to insufficient or invalid data."""


class PredictionError(WCPredictionsError):
    """Raised when a prediction cannot be produced."""


class ConfigurationError(WCPredictionsError):
    """Raised when a required configuration value is missing or invalid."""


class PipelineStepError(WCPredictionsError):
    """Raised when a pipeline step fails."""

    def __init__(self, step_name: str, cause: Exception):
        self.step_name = step_name
        self.cause = cause
        super().__init__(f"Pipeline step '{step_name}' failed: {cause}")
