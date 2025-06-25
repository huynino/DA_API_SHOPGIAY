-- Bảng DanhMuc
CREATE TABLE DanhMuc (
    ma_danh_muc INT AUTO_INCREMENT PRIMARY KEY,
    ten_danh_muc VARCHAR(50),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng SanPham
CREATE TABLE SanPham (
    ma_san_pham INT AUTO_INCREMENT PRIMARY KEY,
    ten_san_pham VARCHAR(100),
    mo_ta VARCHAR(255),
    gia DECIMAL(10, 2),
    ma_danh_muc INT,
    anh_san_pham VARCHAR(255),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_danh_muc) REFERENCES DanhMuc(ma_danh_muc) ON DELETE SET NULL
);

-- Bảng MauSac	
CREATE TABLE MauSac (
    ma_mau INT AUTO_INCREMENT PRIMARY KEY,
    ten_mau VARCHAR(50) NOT NULL,
    ma_hex VARCHAR(7)
);

-- Bảng BienTheSanPham
CREATE TABLE BienTheSanPham (
    ma_bien_the INT AUTO_INCREMENT PRIMARY KEY,
    ma_san_pham INT,
    kich_thuoc VARCHAR(255),
    ma_mau INT,
    so_luong_ton INT,
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham) ON DELETE CASCADE,
    FOREIGN KEY (ma_mau) REFERENCES MauSac(ma_mau) ON DELETE SET NULL
);

-- Bảng AnhBienThe
CREATE TABLE AnhBienThe (
    ma_anh INT AUTO_INCREMENT PRIMARY KEY,
    ma_san_pham INT,
    ma_mau INT,
    duong_dan VARCHAR(255),
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham) ON DELETE CASCADE,
    FOREIGN KEY (ma_mau) REFERENCES MauSac(ma_mau) ON DELETE CASCADE
);

-- Bảng GioHang
CREATE TABLE GioHang (
    ma_gio_hang INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT,
    ma_bien_the INT,
    so_luong INT,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_bien_the) REFERENCES BienTheSanPham(ma_bien_the) 
);

-- Bảng DonHang
CREATE TABLE DonHang (
    ma_don_hang INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT,
    dia_chi_giao_hang VARCHAR(255),
    tong_tien DECIMAL(15, 2),
    trang_thai VARCHAR(20),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE SET NULL
);

-- Bảng ChiTietDonHang
CREATE TABLE ChiTietDonHang (
    ma_chi_tiet INT AUTO_INCREMENT PRIMARY KEY,
    ma_don_hang INT,
    ma_bien_the INT,
    so_luong INT,
    gia DECIMAL(10, 2),
    FOREIGN KEY (ma_don_hang) REFERENCES DonHang(ma_don_hang) ON DELETE CASCADE,
    FOREIGN KEY (ma_bien_the) REFERENCES BienTheSanPham(ma_bien_the) ON DELETE CASCADE
);

-- Bảng ThanhToan
CREATE TABLE ThanhToan (
    ma_thanh_toan INT AUTO_INCREMENT PRIMARY KEY,
    ma_don_hang INT,
    phuong_thuc VARCHAR(20),
    trang_thai VARCHAR(20),
    ngay_thanh_toan DATETIME,
    FOREIGN KEY (ma_don_hang) REFERENCES DonHang(ma_don_hang) ON DELETE CASCADE
);

-- Bảng DanhSachYeuThich
CREATE TABLE DanhSachYeuThich (
    ma_yeu_thich INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT,
    ma_san_pham INT,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham) ON DELETE CASCADE
);



-- Bảng NguoiDung
CREATE TABLE NguoiDung (
    ma_nguoi_dung INT AUTO_INCREMENT PRIMARY KEY,
    ten_nguoi_dung VARCHAR(50),
    email VARCHAR(100),
    mat_khau VARCHAR(255),
    sdt VARCHAR(15),
    dia_chi_mac_dinh VARCHAR(255),
    vai_tro VARCHAR(20),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Vouchers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_voucher VARCHAR(50) UNIQUE,
    loai ENUM('ship', 'order') NOT NULL,          -- Loại: giảm ship hay giảm đơn hàng
    kieu_giam ENUM('phan_tram', 'tien_mat') NOT NULL,  -- Giảm theo % hay theo số tiền
    gia_tri DECIMAL(10,2) NOT NULL,               -- Giá trị giảm
    dieu_kien_ap_dung DECIMAL(10,2) DEFAULT 0,    -- Giá trị đơn hàng tối thiểu để áp dụng
    so_luong INT DEFAULT 1,                       -- Số lần còn lại được sử dụng
    ngay_bat_dau DATETIME,
    ngay_ket_thuc DATETIME,
    mo_ta TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE DiaChiNguoiDung (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT,
    ten_nguoi_nhan VARCHAR(100),
    so_dien_thoai VARCHAR(15),
    dia_chi TEXT,
    mac_dinh BOOLEAN DEFAULT FALSE,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE
);


ALTER TABLE GioHang ADD COLUMN duong_dan_anh VARCHAR(255);

ALTER TABLE DonHang
ADD COLUMN voucher_id INT DEFAULT NULL,
ADD CONSTRAINT fk_donhang_voucher FOREIGN KEY (voucher_id) REFERENCES Vouchers(id) ON DELETE SET NULL;
ALTER TABLE Vouchers
ADD COLUMN trang_thai ENUM('hoat_dong', 'tam_ngung', 'het_han') DEFAULT 'hoat_dong';

