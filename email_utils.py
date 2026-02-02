import smtplib
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from typing import List

# Nạp biến môi trường
load_dotenv(dotenv_path="tkmk.env")

def send_order_email(
    to_email: str,
    customer_name: str,
    order_id: str,
    total_amount: int,
    dia_chi: str,
    sdt: str,
    san_pham: List[dict],
    giam_gia_order: int = 0,
    giam_gia_ship: int = 0,
    phi_ship: int = 0
):
    subject = f"Xác nhận đơn hàng #{order_id}"
    from_email = os.getenv("EMAIL_USER", "no-reply@doubleh.vn")

    # HTML bảng sản phẩm
    product_rows = ""
    for sp in san_pham:
        product_rows += f"""
            <tr>
                <td>{sp['ten_san_pham']}</td>
                <td>{sp.get('mau_sac', '')}</td>
                <td>{sp.get('kich_thuoc', '')}</td>
                <td>{sp['so_luong']}</td>
                <td>{sp['gia']:,.0f}₫</td>
                <td>{sp['so_luong'] * sp['gia']:,.0f}₫</td>
            </tr>
        """

    # HTML email
    html = f"""
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px; }}
            .container {{ max-width: 700px; margin: auto; background: #fff; border-radius: 10px; padding: 30px; }}
            h2 {{ color: #1a73e8; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #ccc; padding: 12px; text-align: left; }}
            th {{ background-color: #f1f1f1; }}
            .total {{ font-weight: bold; color: #e53935; }}
            .footer {{ margin-top: 30px; font-size: 14px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🎉 Cảm ơn bạn đã đặt hàng tại DoubleH!</h2>
            <p>Xin chào <strong>{customer_name}</strong>,</p>
            <p>Mã đơn hàng: <strong>#{order_id}</strong></p>

            <h3>📦 Thông tin sản phẩm</h3>
            <table>
                <thead>
                    <tr>
                        <th>Sản phẩm</th>
                        <th>Màu</th>
                        <th>Size</th>
                        <th>Số lượng</th>
                        <th>Đơn giá</th>
                        <th>Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    {product_rows}
                </tbody>
            </table>

            <h3>📮 Giao đến</h3>
            <p><strong>Địa chỉ:</strong> {dia_chi}<br>
               <strong>SĐT:</strong> {sdt}</p>

            <h3>💰 Tóm tắt đơn hàng</h3>
            <table>
                <tr><td>Tạm tính:</td><td>{total_amount + giam_gia_order - phi_ship + giam_gia_ship:,.0f}₫</td></tr>
                <tr><td>Giảm giá đơn hàng:</td><td>-{giam_gia_order:,.0f}₫</td></tr>
                <tr><td>Giảm giá vận chuyển:</td><td>-{giam_gia_ship:,.0f}₫</td></tr>
                <tr><td>Phí vận chuyển:</td><td>{phi_ship:,.0f}₫</td></tr>
                <tr class="total"><td>Tổng thanh toán:</td><td>{total_amount:,.0f}₫</td></tr>
            </table>

            <div class="footer">
                <p>👉 Bạn có thể theo dõi trạng thái đơn hàng tại trang quản lý tài khoản.</p>
                <p>📧 Mọi thắc mắc xin liên hệ: <a href="mailto:hotro@doubleh.vn">hotro@doubleh.vn</a> hoặc hotline <strong>1900 1234</strong>.</p>
                <p>❤️ Trân trọng cảm ơn!</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Gửi mail
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html', 'utf-8'))

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
        print(f"✅ Đã gửi email HTML đến {to_email}")
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