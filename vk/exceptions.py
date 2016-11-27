class VkApiError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        if code == 100:
            raise CommunityDoesNotExist(code, message)
        super().__init__(message)

    def __str__(self):
        return("CODE: {}, {}".format(self.code, self.message))


class CommunityDoesNotExist(VkApiError):
    def __init__(self, code, message):
        self.code = code
        self.message = message
