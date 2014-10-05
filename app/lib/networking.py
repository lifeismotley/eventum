from flask import make_response
import json

def response_from_json(data, code):
    """Return a :class:`flask.Response` object ``data`` in the body, JSON
    encoding it if necessary.

    :param data: The data to be put in the response body.
    :type data: str or dict
    :param int code: The HTTP status code for the response.

    :returns: the response object
    :rtype: :class:`flask.Response`
    """

    response = make_response(json.dumps(data), code)
    response.headers['Content-Type'] = 'application/json'
    return response


