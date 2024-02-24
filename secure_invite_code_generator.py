import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Initialize Flask application
app = Flask(__name__)

# Externalize database configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///yourdatabase.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your InviteCode model here
class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_invite_code(expiration_days, token_length):
    """Generates a secure invite code with an expiration date."""
    try:
        code_exists = True
        while code_exists:
            code = secrets.token_urlsafe(token_length)
            if not InviteCode.query.filter_by(code=code).first():
                code_exists = False
        
        expiration_date = datetime.utcnow() + timedelta(days=expiration_days)
        new_code = InviteCode(code=code, expiration_date=expiration_date)
        db.session.add(new_code)
        db.session.commit()
        return code
    except IntegrityError:
        logging.error("Integrity error, attempting to generate a new code.")
        db.session.rollback()
        return create_invite_code(expiration_days, token_length)  # Attempt to generate a new code on collision
    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
        db.session.rollback()
        return None
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return None

def main(number_of_codes, expiration_days, token_length):
    """Generates and securely outputs the specified number of invite codes."""
    codes = []
    for _ in range(number_of_codes):
        code = create_invite_code(expiration_days, token_length)
        if code:
            codes.append(code)
        else:
            logging.error("Failed to generate an invite code.")
    
    # Implement secure handling and distribution of these codes
    logging.info(f"Invite codes generated successfully: {len(codes)} codes.")
    for code in codes:
        print(code)

if __name__ == "__main__":
    try:
        db.create_all()  # Ensure tables are created
        number_of_codes = int(input("Enter the number of invite codes to generate: "))
        expiration_days = int(os.getenv('INVITE_CODE_EXPIRATION_DAYS', 365))
        token_length = int(os.getenv('INVITE_CODE_TOKEN_LENGTH', 16))
        main(number_of_codes, expiration_days, token_length)
    except ValueError:
        logging.error("Invalid input. Please enter a valid number of invite codes to generate.")
