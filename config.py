from fastapi_mail import ConnectionConfig, FastMail

conf = ConnectionConfig(
   MAIL_USERNAME="virendrasinghrawat3112@gmail.com",
   MAIL_PASSWORD="unvdaczsfyqwbhph",
   MAIL_PORT=587,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_STARTTLS=True,
   MAIL_SSL_TLS=False,
   MAIL_FROM="virendrasinghrawat3112@gmail.com"
)

fast_mail = FastMail(conf)
