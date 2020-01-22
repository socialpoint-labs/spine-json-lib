class SpineParsingException(Exception):
    def __init__(self, message, code_error=None, *args, **kwargs):
        self.message = message
        self.code_error = code_error

        super(SpineParsingException, self).__init__(*args, **kwargs)

    def __str__(self):
        return str(self.message)


class SpineJsonEditorError(Exception):
    def __init__(self, message, code_error=None, *args, **kwargs):
        self.message = message
        self.code_error = code_error

        super(SpineJsonEditorError, self).__init__(*args, **kwargs)

    def __str__(self):
        return str(self.message)
