import os
import json
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Attachment, FileContent, FileName, FileType, Disposition
import base64

# Load variables
sendgrid_api_key = os.environ["SENDGRID_API_KEY"]
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
template_id = os.environ["SENDGRID_TEMPLATE_ID"]
receiver_emails = [email.strip() for email in receiver_email.split(",")]

# Dynamic content for the template
template_data = {
    "subject": os.environ.get("EMAIL_SUBJECT", "GitHub Actions Notification Email"),
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "commit": os.environ.get("GITHUB_SHA", ""),
    "branch": os.environ.get("GITHUB_REF_NAME", ""),
    "actor": os.environ.get("GITHUB_ACTOR", ""),
    "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
    "link": os.environ.get("GITHUB_RUNNER_LINK", ""),
}

# Optionally add server_url (for smoke test success emails)
server_url = os.getenv("SERVER_URL", "")
if server_url:
    template_data["server_url"] = server_url

# Initialize SendGrid
sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
# Build the email
message = Mail(
    from_email=Email(sender_email, name="FSC Trace"),
    to_emails=receiver_emails,
)

message.template_id = template_id
message.dynamic_template_data = template_data

# Attach files (for unit test)
files_to_attach = os.environ.get("FILES_TO_ATTACH", "[]")
try:
    file_paths = json.loads(files_to_attach)  # This gives a list
    if file_paths: # This is True only if the list is not empty
        for file_path in file_paths:
            print(file_path)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    data = f.read()
                    encoded_file = base64.b64encode(data).decode()
                    attachment = Attachment(
                        FileContent(encoded_file),
                        FileName(os.path.basename(file_path)),
                        FileType("application/octet-stream"),
                        Disposition("attachment")
                    )
                    message.add_attachment(attachment)
except json.JSONDecodeError:
    print("FILES_TO_ATTACH is not a valid JSON list.")                    

# Send email
try:
    response = sg.send(message)
    print(f"✅Email sent successfully !")
except Exception as e:
    print(f"❌Failed to send email: {str(e)}")
