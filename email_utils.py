import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Nạp biến môi trường
load_dotenv(dotenv_path="tkmk.env")

def send_order_email(to_email, customer_name, order_id, total_amount):
    subject = f"Xác nhận đơn hàng #{order_id}"
    body = f"""
    Xin chào {customer_name},

    Cảm ơn bạn đã đặt hàng tại hệ thống DoubleH.

    🧾 Mã đơn hàng: {order_id}
    💰 Tổng tiền: {total_amount:,.0f} VNĐ

    Đơn hàng của bạn đang được xử lý và sẽ sớm giao đến bạn.

    Trân trọng,
    DoubleH Store
    """

    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()
        print(f"✅ Đã gửi email đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")

#--------------------------------------------


def send_otp_email(to_email, otp_code):
    subject = "Mã xác thực OTP từ DoubleH"
    body = f"""
    Xin chào,

    Đây là mã OTP của bạn: {otp_code}

    Mã có hiệu lực trong vòng 5 phút.

    Trân trọng,
    DoubleH Store
    """

    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()
        print(f"✅ Đã gửi OTP đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi gửi OTP: {e}")
