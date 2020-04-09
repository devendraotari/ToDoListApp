import random
import string

def generateRandomPassword(stringLength=10):
    """Generate a random string of letters, digits and special characters """

    password_characters = string.ascii_letters + string.digits
    password_characters = ''.join(random.choice(password_characters) for i in range(stringLength))
    return password_characters

