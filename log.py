import os
import logging
import logging.handlers


smtp_creds = (os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
smtp_handler = logging.handlers.SMTPHandler(mailhost=("smtp.gmail.com", 587),
                                            fromaddr=os.getenv("SMTP_USER"),
                                            toaddrs=[os.getenv("SMTP_USER")],
                                            subject="Error in YouTube Analysis",
                                            credentials=smtp_creds,
                                            secure=())
smtp_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(),
        smtp_handler
    ]
)
