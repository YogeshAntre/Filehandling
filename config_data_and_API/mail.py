from fastapi import FastAPI, UploadFile, File, HTTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import uvicorn

app = FastAPI()

@app.post("/send_email/")
async def send_email_with_attachment(
    email_to: str,
    subject: str,
    body: str,
    attachment: UploadFile = File(...)
):
    # Email configurations
    sender_email = "antretaravasant@gmail.com"  # Update with your email
    sender_password = "tara6625"#"dfvd enhz dgyb kbsx"  # Update with your password

    # Create multipart message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email_to
    msg["Subject"] = subject

    # Attach body
    msg.attach(MIMEText(body, "plain"))

    # Attach Excel file
    attachment_data = await attachment.read()
    attachment_part = MIMEBase("application", "octet-stream")
    attachment_part.set_payload(attachment_data)
    encoders.encode_base64(attachment_part)
    attachment_part.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment.filename}",
    )
    msg.attach(attachment_part)

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # Update with your SMTP server details
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_to, msg.as_string())
        server.quit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
if __name__ == "__main__":
     uvicorn.run(app="mail:app", host="localhost", port=8001, reload=True)
