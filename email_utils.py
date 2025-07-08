import smtplib
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Nạp biến môi trường
load_dotenv(dotenv_path="tkmk.env")

def send_order_email(to_email, customer_name, order_id, total_amount):
    subject = f"Xác nhận đơn hàng #{order_id}"
    body = f"""\
Xin chào {customer_name},

Cảm ơn bạn đã đặt hàng tại hệ thống DoubleH.

🧾 Mã đơn hàng: {order_id}
💰 Tổng tiền: {total_amount:,.0f} VNĐ

Đơn hàng của bạn đang được xử lý và sẽ sớm giao đến bạn.

Trân trọng,
DoubleH Store
"""

    msg = MIMEMultipart()
    from_email = os.getenv("EMAIL_USER", "no-reply@doubleh.vn")
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_PORT", 587))
        smtp_user = os.getenv("EMAIL_USER")
        smtp_pass = os.getenv("EMAIL_PASS")

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"✅ Đã gửi email đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")

#--------------------------------------------


def send_otp_email(to_email, otp_code):
    subject = "Mã xác thực OTP từ DoubleH"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #8A2BE2;">Xác thực tài khoản</h2>
            <p>Xin chào,</p>
            <p>Đây là mã OTP của bạn:</p>
            <h1 style="text-align: center; background-color: #8A2BE2; color: white; padding: 10px; border-radius: 5px;">{otp_code}</h1>
            <p style="color: #555;">Mã có hiệu lực trong vòng <b>1 phút</b>.</p>
            <br>
            <p style="font-size: 13px; color: #888;">Trân trọng,<br>DoubleH Store</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()
        print(f"✅ Đã gửi OTP đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi gửi OTP: {e}")