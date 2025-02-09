from flask import jsonify, Response
from werkzeug.exceptions import HTTPException

def handle_exception(e):
    """
    Handle generic exceptions.
    """
    if isinstance(e, HTTPException):
       
        return handle_http_exception(e)
    else:
       
        return handle_500(e)

def handle_http_exception(e):
    response = {
        "error": e.description,
        "code": e.code
    }
    return jsonify(response), e.code 

def handle_404(e):
    """
    Handle 404 errors.
    """
    response = {
        "error": "Page not found",
        "code": 404
    }
    return jsonify(response), 404

def handle_500(e):
    """
    Handle 500 errors.
    """
    response = {
        "error": "Internal Server Error",
        "code": 500
    }
    return jsonify(response), 500

def register_error_handlers(app):
    """
    Register error handlers for the Flask app.
    """
    app.register_error_handler(HTTPException, handle_http_exception) 
    app.register_error_handler(404, handle_404) 
    app.register_error_handler(500, handle_500)  
    app.register_error_handler(Exception, handle_exception)  