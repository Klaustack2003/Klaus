import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import re

load_dotenv()

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.display_name = os.getenv("EMAIL_DISPLAY_NAME")

    def send_email(self, recipient, subject, body):
        """Send an email with the given parameters"""
        try:
            # Validate email format
            if not self._validate_email(recipient):
                return False, "Invalid email address format"

            # Create message container
            msg = MIMEMultipart()
            msg['From'] = f'{self.display_name} <{self.email_address}>'
            msg['To'] = recipient
            msg['Subject'] = subject

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Connect to server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
        
        except smtplib.SMTPAuthenticationError:
            return False, "Email authentication failed"
        except smtplib.SMTPException as e:
            return False, f"Email sending error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def _validate_email(self, email):
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None