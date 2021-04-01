# Base Exception taken from https://github.com/python-gitlab/python-gitlab/blob/master/gitlab/exceptions.py
# Copyright (C) 2013-2017 Gauvain Pocentek <gauvain@pocentek.net>
class ZenodoGitLabException(Exception):
    def __init__(self, error_message="", response_code=None, response_body=None):

        Exception.__init__(self, error_message)
        # Http status code
        self.response_code = response_code
        # Full http response
        self.response_body = response_body
        # Parsed error message from gitlab
        try:
            # if we receive str/bytes we try to convert to unicode/str to have
            # consistent message types (see #616)
            self.error_message = error_message.decode()
        except Exception:
            self.error_message = error_message

    def __str__(self):
        if self.response_code is not None:
            return "{0}: {1}".format(self.response_code, self.error_message)
        else:
            return "{0}".format(self.error_message)


class NoSuchSourceArchiveException(ZenodoGitLabException):
    ...
