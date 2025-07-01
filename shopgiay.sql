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
    ten_nguoi_nhan VARCHAR(100),       
    so_dien_thoai VARCHAR(15),        
    dia_chi_giao_hang VARCHAR(255),    
    tong_tien DECIMAL(15, 2),
    trang_thai VARCHAR(20),
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    voucher_order_id INT DEFAULT NULL,
    voucher_ship_id INT DEFAULT NULL,
    phuong_thuc_id INT DEFAULT NULL,  
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE SET NULL,
    FOREIGN KEY (voucher_order_id) REFERENCES voucher(id) ON DELETE SET NULL,
    FOREIGN KEY (voucher_ship_id) REFERENCES voucher(id) ON DELETE SET NULL,
    FOREIGN KEY (phuong_thuc_id) REFERENCES PhuongThucVanChuyen(id) ON DELETE SET NULL
);


CREATE TABLE PhuongThucVanChuyen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_phuong_thuc VARCHAR(100) NOT NULL,
    chi_phi DECIMAL(10,2) DEFAULT 0,
    trang_thai ENUM('hoat_dong', 'tam_ngung') DEFAULT 'hoat_dong'
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

CREATE TABLE voucher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_voucher VARCHAR(50) UNIQUE,
    mo_ta_hien_thi VARCHAR(255),
    loai ENUM('ship', 'order') NOT NULL,
    kieu_giam ENUM('phan_tram', 'tien_mat') NOT NULL,
    gia_tri DECIMAL(10,2) NOT NULL,
    dieu_kien_ap_dung DECIMAL(10,2) DEFAULT 0,
    so_luong INT DEFAULT 1,
    ngay_bat_dau DATETIME,
    ngay_ket_thuc DATETIME,
    hinh_anh VARCHAR(255),
    hien_thi_auto BOOLEAN DEFAULT FALSE,
    trang_thai ENUM('hoat_dong', 'tam_ngung', 'het_han') DEFAULT 'hoat_dong',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    nguoi_tao INT,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_tao) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE SET NULL
);


CREATE TABLE NguoiDungVoucher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_nguoi_dung INT,
    voucher_id INT,
    da_su_dung BOOLEAN DEFAULT FALSE,
    ngay_su_dung DATETIME,
    UNIQUE KEY (ma_nguoi_dung, voucher_id),
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (voucher_id) REFERENCES voucher(id) ON DELETE CASCADE
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

CREATE TABLE XacThucOTP (
    email VARCHAR(255) PRIMARY KEY,
    ma_otp VARCHAR(10),
    thoi_gian_gui DATETIME
);
CREATE TABLE PhieuNhap (
    ma_phieu_nhap INT AUTO_INCREMENT PRIMARY KEY,
    nguoi_nhap VARCHAR(100) NOT NULL,
    ngay_nhap DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE ChiTietPhieuNhap (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ma_phieu_nhap INT NOT NULL,
    ma_san_pham INT NOT NULL,
    ma_mau INT NOT NULL,
    kich_thuoc VARCHAR(10) NOT NULL,
    so_luong INT NOT NULL CHECK (so_luong > 0),

    FOREIGN KEY (ma_phieu_nhap) REFERENCES PhieuNhap(ma_phieu_nhap) ON DELETE CASCADE,
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham),
    FOREIGN KEY (ma_mau) REFERENCES MauSac(ma_mau)
);


UPDATE BienTheSanPham b1
JOIN (
    SELECT ma_san_pham, ma_mau, kich_thuoc, MIN(ma_bien_the) AS keep_id, SUM(so_luong_ton) AS tong
    FROM BienTheSanPham
    GROUP BY ma_san_pham, ma_mau, kich_thuoc
    HAVING COUNT(*) > 1
) dup
ON b1.ma_bien_the = dup.keep_id
SET b1.so_luong_ton = dup.tong;

DELETE b2 FROM BienTheSanPham b2
JOIN (
    SELECT ma_san_pham, ma_mau, kich_thuoc, MIN(ma_bien_the) AS keep_id
    FROM BienTheSanPham
    GROUP BY ma_san_pham, ma_mau, kich_thuoc
    HAVING COUNT(*) > 1
) dup
ON b2.ma_san_pham = dup.ma_san_pham
AND b2.ma_mau = dup.ma_mau
AND b2.kich_thuoc = dup.kich_thuoc
AND b2.ma_bien_the != dup.keep_id;


ALTER TABLE BienTheSanPham
ADD CONSTRAINT unique_bien_the UNIQUE (ma_san_pham, ma_mau, kich_thuoc);

ALTER TABLE GioHang ADD COLUMN duong_dan_anh VARCHAR(255);
ALTER TABLE PhieuNhap
ADD tong_so_luong INT DEFAULT 0;



