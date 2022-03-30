from flask import Flask, request, jsonify, make_response, request, render_template, session, flash
import jwt
from datetime import datetime, timedelta
from functools import wraps

# app.config['SECRET_KEY'] = '8454e5a14e6c4a3490e85f8cd0737fa0'
# how to get a secret key
# In your command line >>> access Python >>> then type:

# OS Approach
# import os
# os.urandom(14)

# UUID Approach
# import uuid
# uuid.uuid4().hex

# Secrets [ only for Python 3.6 + ]
#import secrets
# secrets.token_urlsafe(14)


def token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

