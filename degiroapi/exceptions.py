class DeGiroRequiresTOTP(Exception):
    """This exception is thrown when two factor authentication is enabled but that is not passed onto the login step."""

    pass
