# Raised when the model is invalid
class ModelStaticError(Exception):
  pass

# Raised when an error is encountered during model execution
class ModelRuntimeError(Exception):
  pass