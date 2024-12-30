import smtplib
import aiosmtplib
import asyncio
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import yaml

def read_yaml(yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

async def send_email(subject, body, to_email, image_path):
    from_email = read_yaml("creds.yaml")["from_email"]
    from_password = read_yaml("creds.yaml")["from_password"]

    # Connect to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with open(image_path, "rb") as img:
        mime_image = MIMEImage(img.read())
        mime_image.add_header('Content-ID', '<image1>')
        msg.attach(mime_image)

    # server.send_message(msg)
    # server.quit()
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=from_email,
        password=from_password,
    )

async def main():
    html_body = """
    <html>
        <body>
            <h1>I KNOW WHERE YOU SLEEP</h1>
            <p>Just Kidding.</p>
            <p>But I do know where you live.</p>
            <p>And I know where you work.</p>
            <p>And I know what you do in your free time.</p>
            <p>And I know what you eat.</p>
            <p>And I know what you drink.</p>
            <p>And I know what you wear.</p>
            <p>And I also know where you sleep.</p>
            <img src="cid:image1" style="width:300px;height:auto;">
        </body>
    </html>
    """
    image_path = "test_pics/testpic5.jpg"
    csv_file = "contacts.csv"
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)  # Read all rows into a list

    tasks = []
    for row in rows:
        to_email = row["email"]
        tasks.append(send_email("Test Image", html_body, to_email, image_path))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for row, result in zip(rows, results):
        to_email = row["email"]
        if isinstance(result, Exception):
            print(f"Failed to send email to {to_email}: {result}")
        else:
            print(f"Email sent to {to_email}")

if __name__ == "__main__":
    asyncio.run(main())