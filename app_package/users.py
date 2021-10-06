from app_package import app
# re provides support for regular expressions
import re

@app.route('/api/users')
def api_users():
    return "Hello World"


# Regular expression for email string
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
def check_email(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False