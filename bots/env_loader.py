import os
from dotenv import load_dotenv

# Load the .env file from the project's root directory
load_dotenv()


# Function to get an environment variable with a fallback option
def get_env_variable(var_name: str, default_value: str = None):
    """
    Retrieves the value of an environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default_value (str, optional): A default value to return if the variable is not found.

    Returns:
        str: The value of the environment variable or the default value if not found.

    Raises:
        ValueError: If the variable is not found and no default is provided.
    """
    value = os.getenv(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' is not set.")
    return value
