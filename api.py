from typing import Union, List, Tuple
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from mysql.connector import Error
import db
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import shutil
import os
from fastapi.responses import JSONResponse
from fastapi import Query
from fastapi import Path
from datetime import datetime
from typing import List, Optional

  # module kết nối cơ sở dữ liệu của bạn

app = FastAPI()

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/getAllMauSac")
def get_all_mau_sac():
    try:
        # Kết nối DB
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM MauSac"
            cursor.execute(sql)
            result = cursor.fetchall()

            cursor.close()
            conn.close()

            return result if result else {"message": "Không có màu sắc nào trong hệ thống."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.post("/addMauSac")
def add_mau_sac(
    ten_mau: str ,
    ma_hex: str   # Mã màu HEX như "#FFFFFF"
):
    try:
        # Kết nối DB
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            sql = """
                INSERT INTO MauSac (ten_mau, ma_hex)
                VALUES (%s, %s)
            """
            values = (ten_mau, ma_hex)

            cursor.execute(sql, values)
            conn.commit()
            new_id = cursor.lastrowid

            cursor.close()
            conn.close()

            return {
                "message": "Thêm màu sắc thành công",
                "ma_mau": new_id
            }
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.delete("/xoaMauSac")
def xoa_mau_sac(ma_mau: int = Query(..., description="Mã màu cần xóa")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            # Kiểm tra màu có tồn tại
            cursor.execute("SELECT * FROM MauSac WHERE ma_mau = %s", (ma_mau,))
            result = cursor.fetchone()
            if not result:
                cursor.close()
                conn.close()
                return {"message": f"Màu có mã {ma_mau} không tồn tại."}

            # Thực hiện xóa
            cursor.execute("DELETE FROM MauSac WHERE ma_mau = %s", (ma_mau,))
            conn.commit()

            cursor.close()
            conn.close()
            return {"message": f"Đã xóa thành công màu có mã {ma_mau}."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

class MauModel(BaseModel):
    ma_mau: int
    ten_mau: str

@app.get("/getMauTheoSanPham", response_model=List[MauModel])
def get_mau(maSanPham: int = Query(...)):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT ms.ma_mau, ms.ten_mau
            FROM BienTheSanPham bt
            JOIN MauSac ms ON bt.ma_mau = ms.ma_mau
            WHERE bt.ma_san_pham = %s
        """, (maSanPham,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

from datetime import datetime

@app.post("/themDanhMuc")
def them_danh_muc(ten_danh_muc: str):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM DanhMuc WHERE ten_danh_muc = %s", (ten_danh_muc,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {"message": f"Danh mục '{ten_danh_muc}' đã tồn tại."}

            current_time = datetime.now()  # ✅ Đúng
            cursor.execute(
                "INSERT INTO DanhMuc (ten_danh_muc, ngay_tao) VALUES (%s, %s)",
                (ten_danh_muc, current_time)
            )
            conn.commit()

            ma_danh_muc_moi = cursor.lastrowid
            cursor.close()
            conn.close()

            return {
                "message": "Thêm danh mục thành công.",
                "ma_danh_muc": ma_danh_muc_moi,
                "ten_danh_muc": ten_danh_muc,
                "ngay_tao": current_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

# @app.post("/themDanhMuc")
# def them_danh_muc(
#     ten_danh_muc: str 
# ):
#     try:
#         # Kết nối DB
#         conn = db.connect_to_database()
#         if not isinstance(conn, Error):
#             cursor = conn.cursor()

#             # Kiểm tra tên danh mục đã tồn tại chưa (tuỳ chọn)
#             check_sql = "SELECT * FROM DanhMuc WHERE ten_danh_muc = %s"
#             cursor.execute(check_sql, (ten_danh_muc,))
#             if cursor.fetchone():
#                 cursor.close()
#                 conn.close()
#                 return {"message": f"Danh mục '{ten_danh_muc}' đã tồn tại."}

#             # Thêm mới
#             insert_sql = "INSERT INTO DanhMuc (ten_danh_muc) VALUES (%s)"
#             cursor.execute(insert_sql, (ten_danh_muc,))
#             conn.commit()

#             ma_danh_muc_moi = cursor.lastrowid

#             cursor.close()
#             conn.close()

#             return {
#                 "message": "Thêm danh mục thành công.",
#                 "ma_danh_muc": ma_danh_muc_moi
#             }
#         else:
#             raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    


@app.get("/getDanhMuc")
def get_danh_muc(ma_danh_muc: int = Query(..., description="Mã danh mục cần tìm")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM DanhMuc WHERE ma_danh_muc = %s"
            cursor.execute(sql, (ma_danh_muc,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": f"Không tìm thấy danh mục với mã {ma_danh_muc}."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    



@app.delete("/xoaDanhMuc")
def xoa_danh_muc(ma_danh_muc: int = Query(..., description="Mã danh mục cần xoá")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            # Kiểm tra tồn tại
            cursor.execute("SELECT * FROM DanhMuc WHERE ma_danh_muc = %s", (ma_danh_muc,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"message": f"Danh mục có mã {ma_danh_muc} không tồn tại."}

            # Xoá danh mục
            cursor.execute("DELETE FROM DanhMuc WHERE ma_danh_muc = %s", (ma_danh_muc,))
            conn.commit()

            cursor.close()
            conn.close()
            return {"message": f"Đã xoá danh mục có mã {ma_danh_muc} thành công."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

@app.put("/danh-muc/{ma_danh_muc}")
def sua_danh_muc(
    ma_danh_muc: int = Path(..., description="Mã danh mục cần sửa"),
    ten_moi: str = Form(..., description="Tên danh mục mới")
):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được database")
        
        cursor = conn.cursor()
        cursor.execute("UPDATE DanhMuc SET ten_danh_muc = %s WHERE ma_danh_muc = %s", (ten_moi, ma_danh_muc))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy danh mục để cập nhật")

        cursor.close()
        conn.close()
        return {"message": "Cập nhật danh mục thành công"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getAllMaDanhMuc")
def get_all_ma_danh_muc():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            # Lấy cả ngày tạo
            sql = "SELECT ma_danh_muc, ten_danh_muc, ngay_tao FROM DanhMuc"
            cursor.execute(sql)
            result = cursor.fetchall()

            # Format lại ngày tạo nếu cần
            for item in result:
                if item.get("ngay_tao") and isinstance(item["ngay_tao"], datetime):
                    item["ngay_tao"] = item["ngay_tao"].strftime("%Y-%m-%d %H:%M:%S")

            cursor.close()
            conn.close()

            if result:
                return {"danh_sach_danh_muc": result}
            else:
                return {"message": "Không có danh mục nào trong hệ thống."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

# @app.get("/getAllMaDanhMuc")
# def get_all_ma_danh_muc():
#     try:
#         conn = db.connect_to_database()
#         if not isinstance(conn, Error):
#             cursor = conn.cursor(dictionary=True)

#             sql = "SELECT ma_danh_muc, ten_danh_muc FROM DanhMuc"
#             cursor.execute(sql)
#             result = cursor.fetchall()

#             cursor.close()
#             conn.close()

#             if result:
#                 return {"danh_sach_danh_muc": result}
#             else:
#                 return {"message": "Không có danh mục nào trong hệ thống."}
#         else:
#             raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.post("/themSanPham")
def them_san_pham(
    ten_san_pham: str ,
    mo_ta: str ,
    gia: float ,
    ma_danh_muc: int ,
    file: UploadFile = File(...)
):
    try:
        # Lưu ảnh sản phẩm
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        anh_san_pham_url = f"/{UPLOAD_FOLDER}{file.filename}"

        # Kết nối DB
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            sql = """
                INSERT INTO SanPham (ten_san_pham, mo_ta, gia, ma_danh_muc, anh_san_pham)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (ten_san_pham, mo_ta, gia, ma_danh_muc, anh_san_pham_url)

            cursor.execute(sql, values)
            conn.commit()

            new_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return {
                "message": "Thêm sản phẩm thành công.",
                "ma_san_pham": new_id,
                "anh_san_pham": anh_san_pham_url
            }
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@app.get("/getallSanPham")
def get_all_san_pham():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM SanPham"
            cursor.execute(sql)
            result = cursor.fetchall()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": "Không có sản phẩm nào trong hệ thống."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

@app.delete("/xoaSanPham")
def xoa_san_pham(ma_san_pham: int = Query(..., description="Mã sản phẩm cần xóa")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            # Kiểm tra sản phẩm có tồn tại không
            check_sql = "SELECT * FROM SanPham WHERE ma_san_pham = %s"
            cursor.execute(check_sql, (ma_san_pham,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"message": f"Không tìm thấy sản phẩm với mã {ma_san_pham}."}

            # Xoá sản phẩm
            delete_sql = "DELETE FROM SanPham WHERE ma_san_pham = %s"
            cursor.execute(delete_sql, (ma_san_pham,))
            conn.commit()

            cursor.close()
            conn.close()
            return {"message": f"Đã xoá sản phẩm có mã {ma_san_pham} thành công."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/getSanPham/{maSanPham}")
def get_san_pham(maSanPham: int):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM SanPham WHERE ma_san_pham = %s"
            cursor.execute(sql, (maSanPham,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": f"Không tìm thấy sản phẩm với mã {maSanPham}."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.post("/themAnhBienThe")
def them_anh_bien_the(
    ma_san_pham: int = Form(...),
    ma_mau: int = Form(...),
    files: list[UploadFile] = File(...)
):
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        duong_dan_list = []

        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            for file in files:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # Tạo đường dẫn để lưu vào DB
                anh_url = f"/{UPLOAD_FOLDER}{file.filename}"
                duong_dan_list.append(anh_url)

                # Ghi vào bảng AnhBienThe
                cursor.execute("""
                    INSERT INTO AnhBienThe (ma_san_pham, ma_mau, duong_dan)
                    VALUES (%s, %s, %s)
                """, (ma_san_pham, ma_mau, anh_url))

            conn.commit()
            cursor.close()
            conn.close()

            return {
                "message": "Đã thêm tất cả ảnh biến thể thành công.",
                "ma_mau": ma_mau,
                "duong_dan_anh": duong_dan_list
            }

        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

    

@app.get("/getallAnhBienThe")
def get_all_anh_bien_the():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM AnhBienThe"
            cursor.execute(sql)
            result = cursor.fetchall()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": "Không có ảnh biến thể nào trong hệ thống."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/getDanhSachAnhBienThe")
def get_danh_sach_anh_bien_the(ma_san_pham: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")

        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM AnhBienThe WHERE ma_san_pham = %s"
        cursor.execute(sql, (ma_san_pham,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result  # ✅ Trả trực tiếp list ảnh biến thể (dạng mảng)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.post("/xoaAnhBienTheTheoSanPhamVaMau")
def xoa_anh_theo_san_pham_va_mau(
    ma_san_pham: int = Form(...),
    ma_mau: int = Form(...)
):
    try:
        conn = db.connect_to_database()
        if not conn:
            raise HTTPException(status_code=500, detail="Không kết nối được database.")
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM AnhBienThe
            WHERE ma_san_pham = %s AND ma_mau = %s
        """, (ma_san_pham, ma_mau))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Đã xóa ảnh biến thể theo mã sản phẩm và màu thành công."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/themBienTheSanPham")
# def them_bien_the_san_pham(
#     ma_san_pham: int = Form(...),
#     kich_thuoc: str = Form(...),
#     ma_mau: int = Form(...),
#     so_luong_ton: int = Form(...)
# ):
#     try:
#         # Kết nối DB
#         conn = db.connect_to_database()
#         if isinstance(conn, Error):
#             raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

#         cursor = conn.cursor()

#         # Kiểm tra sản phẩm có tồn tại không
#         cursor.execute("SELECT 1 FROM SanPham WHERE ma_san_pham = %s", (ma_san_pham,))
#         if not cursor.fetchone():
#             cursor.close()
#             conn.close()
#             raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")

#         # Kiểm tra màu sắc có tồn tại không
#         cursor.execute("SELECT 1 FROM MauSac WHERE ma_mau = %s", (ma_mau,))
#         if not cursor.fetchone():
#             cursor.close()
#             conn.close()
#             raise HTTPException(status_code=404, detail="Không tìm thấy màu sắc.")

#         # Thêm biến thể sản phẩm
#         sql = """
#             INSERT INTO BienTheSanPham (ma_san_pham, kich_thuoc, ma_mau, so_luong_ton)
#             VALUES (%s, %s, %s, %s)
#         """
#         values = (ma_san_pham, kich_thuoc, ma_mau, so_luong_ton)
#         cursor.execute(sql, values)
#         conn.commit()
#         new_id = cursor.lastrowid

#         cursor.close()
#         conn.close()

#         return {
#             "message": "Thêm biến thể sản phẩm thành công.",
#             "ma_bien_the": new_id
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
@app.post("/themBienTheSanPham")
def them_bien_the_san_pham(
    ma_san_pham: int = Form(...),
    kich_thuoc: str = Form(...),
    ma_mau: int = Form(...),
    so_luong_ton: int = Form(...)
):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

        cursor = conn.cursor()

        # Kiểm tra sản phẩm và màu
        cursor.execute("SELECT 1 FROM SanPham WHERE ma_san_pham = %s", (ma_san_pham,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")

        cursor.execute("SELECT 1 FROM MauSac WHERE ma_mau = %s", (ma_mau,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy màu sắc.")

        # Kiểm tra biến thể đã tồn tại chưa
        cursor.execute("""
            SELECT ma_bien_the, so_luong_ton 
            FROM BienTheSanPham 
            WHERE ma_san_pham = %s AND kich_thuoc = %s AND ma_mau = %s
        """, (ma_san_pham, kich_thuoc, ma_mau))

        bien_the = cursor.fetchone()

        if bien_the:
            # Nếu đã tồn tại, cộng dồn số lượng
            ma_bien_the, so_luong_hien_tai = bien_the
            tong_so_luong = so_luong_hien_tai + so_luong_ton

            cursor.execute("""
                UPDATE BienTheSanPham 
                SET so_luong_ton = %s 
                WHERE ma_bien_the = %s
            """, (tong_so_luong, ma_bien_the))
            conn.commit()

            return {
                "message": "Biến thể đã tồn tại, đã cập nhật số lượng tồn.",
                "ma_bien_the": ma_bien_the,
                "so_luong_moi": tong_so_luong
            }

        else:
            # Nếu chưa tồn tại, thêm mới
            cursor.execute("""
                INSERT INTO BienTheSanPham (ma_san_pham, kich_thuoc, ma_mau, so_luong_ton)
                VALUES (%s, %s, %s, %s)
            """, (ma_san_pham, kich_thuoc, ma_mau, so_luong_ton))
            conn.commit()

            new_id = cursor.lastrowid
            return {
                "message": "Thêm biến thể sản phẩm thành công.",
                "ma_bien_the": new_id
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

from fastapi import Query

@app.get("/getBienTheTheoSanPham")
def get_bien_the_theo_san_pham(ma_san_pham: int = Query(..., description="Mã sản phẩm")):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")

        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT 
                b.ma_bien_the,
                b.kich_thuoc,
                b.so_luong_ton,
                ms.ten_mau,
                ms.ma_hex,
                ms.ma_mau
            FROM BienTheSanPham b
            LEFT JOIN MauSac ms ON b.ma_mau = ms.ma_mau
            WHERE b.ma_san_pham = %s
        """
        cursor.execute(sql, (ma_san_pham,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        if result:
            return result
        else:
            return {"message": f"Không có biến thể nào cho sản phẩm mã {ma_san_pham}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/getAllBienTheSanPham")
def get_all_bien_the_san_pham():
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT 
                b.ma_bien_the,
                sp.ten_san_pham,
                b.kich_thuoc,
                ms.ten_mau,
                ms.ma_hex,
                b.so_luong_ton
            FROM BienTheSanPham b
            JOIN SanPham sp ON b.ma_san_pham = sp.ma_san_pham
            LEFT JOIN MauSac ms ON b.ma_mau = ms.ma_mau
            ORDER BY b.ma_bien_the DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        if result:
            return result
        else:
            return {"message": "Không có biến thể sản phẩm nào."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.delete("/xoaBienTheSanPham")
def xoa_bien_the_san_pham(ma_bien_the: int = Query(..., description="Mã biến thể cần xóa")):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

        cursor = conn.cursor()

        # Kiểm tra biến thể có tồn tại không
        cursor.execute("SELECT * FROM BienTheSanPham WHERE ma_bien_the = %s", (ma_bien_the,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Không tìm thấy biến thể với mã đã cho")

        # Tiến hành xóa
        cursor.execute("DELETE FROM BienTheSanPham WHERE ma_bien_the = %s", (ma_bien_the,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": f"Đã xóa biến thể sản phẩm với mã {ma_bien_the} thành công."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
 
    
# @app.delete("/xoaUser")
# def xoa_user(ma_nguoi_dung: int = Query(..., description="Mã người dùng cần xóa")):
#     try:
#         conn = db.connect_to_database()
#         if not isinstance(conn, Error):
#             cursor = conn.cursor()

#             # Kiểm tra người dùng tồn tại không
#             check_sql = "SELECT * FROM NguoiDung WHERE ma_nguoi_dung = %s"
#             cursor.execute(check_sql, (ma_nguoi_dung,))
#             if not cursor.fetchone():
#                 cursor.close()
#                 conn.close()
#                 return {"message": f"Không tìm thấy người dùng với mã {ma_nguoi_dung}."}

#             # Xóa người dùng
#             delete_sql = "DELETE FROM NguoiDung WHERE ma_nguoi_dung = %s"
#             cursor.execute(delete_sql, (ma_nguoi_dung,))
#             conn.commit()

#             cursor.close()
#             conn.close()

#             return {"message": f"Đã xóa người dùng có mã {ma_nguoi_dung} thành công."}
#         else:
#             raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
@app.delete("/xoaUser")
def xoa_user(ma_nguoi_dung: int = Query(..., description="Mã người dùng cần xóa")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            # Kiểm tra người dùng tồn tại
            check_sql = "SELECT * FROM NguoiDung WHERE ma_nguoi_dung = %s"
            cursor.execute(check_sql, (ma_nguoi_dung,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": f"Không tìm thấy người dùng với mã {ma_nguoi_dung}."
                }

            # Thực hiện xóa
            delete_sql = "DELETE FROM NguoiDung WHERE ma_nguoi_dung = %s"
            cursor.execute(delete_sql, (ma_nguoi_dung,))
            conn.commit()

            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": f"Đã xóa người dùng có mã {ma_nguoi_dung} thành công."
            }
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.get("/getUser")
def get_user(ma_nguoi_dung: int = Query(..., description="Mã người dùng cần tìm")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM NguoiDung WHERE ma_nguoi_dung = %s"
            cursor.execute(sql, (ma_nguoi_dung,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": f"Không tìm thấy người dùng với mã {ma_nguoi_dung}."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.get("/getallUser")
def get_all_user():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM NguoiDung"
            cursor.execute(sql)
            result = cursor.fetchall()

            cursor.close()
            conn.close()

            if result:
                return result
            else:
                return {"message": "Không có người dùng nào trong hệ thống."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")



@app.get("/getUserByEmail")
def get_user_by_email(email: str = Query(...)):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM NguoiDung WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return {"message": "Thành công", "user": result}
            else:
                return {"message": "Không tìm thấy người dùng"}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

@app.post("/login")
def login_user(
    email: str = Form(...),
    mat_khau: str = Form(...)
):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            # Tùy chọn: nếu bạn mã hóa mật khẩu bằng SHA256
            # mat_khau = hashlib.sha256(mat_khau.encode()).hexdigest()

            sql = "SELECT * FROM NguoiDung WHERE email = %s AND mat_khau = %s"
            cursor.execute(sql, (email, mat_khau))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                return {
                    "message": "Đăng nhập thành công.",
                    "user": user
                }
            else:
                raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/kiemTraVaiTroAdmin")
def kiem_tra_vai_tro_admin(ma_nguoi_dung: int = Query(..., description="Mã người dùng cần kiểm tra")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT vai_tro FROM NguoiDung WHERE ma_nguoi_dung = %s"
            cursor.execute(sql, (ma_nguoi_dung,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                if result["vai_tro"].lower() == "admin":
                    return {"message": "Người dùng là Admin", "vai_tro": result["vai_tro"]}
                else:
                    return {"message": "Người dùng không phải là Admin", "vai_tro": result["vai_tro"]}
            else:
                return {"message": f"Không tìm thấy người dùng với mã {ma_nguoi_dung}."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.post("/themYeuThich")
def them_yeu_thich(
    ma_nguoi_dung: int = Form(...),
    ma_san_pham: int = Form(...)
):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor()

        # Kiểm tra trùng
        check_sql = """
            SELECT ma_yeu_thich FROM DanhSachYeuThich 
            WHERE ma_nguoi_dung = %s AND ma_san_pham = %s
        """
        cursor.execute(check_sql, (ma_nguoi_dung, ma_san_pham))
        if cursor.fetchone():
            return JSONResponse(content={"message": "Sản phẩm đã có trong yêu thích"}, status_code=200)

        # Thêm mới
        sql = """
            INSERT INTO DanhSachYeuThich (ma_nguoi_dung, ma_san_pham)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (ma_nguoi_dung, ma_san_pham))
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Đã thêm vào danh sách yêu thích"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")



@app.get("/yeuThichTheoNguoiDung")
def lay_yeu_thich_theo_nguoi_dung(ma_nguoi_dung: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                sp.ma_san_pham,
                sp.ten_san_pham,
                sp.gia,
                sp.anh_san_pham,
                sp.ma_danh_muc
            FROM DanhSachYeuThich yt
            JOIN SanPham sp ON yt.ma_san_pham = sp.ma_san_pham
            WHERE yt.ma_nguoi_dung = %s
        """, (ma_nguoi_dung,))
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


from fastapi import Query

@app.delete("/xoaYeuThich")
def xoa_yeu_thich(
    ma_nguoi_dung: int = Query(...),
    ma_san_pham: int = Query(...)
):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM DanhSachYeuThich
            WHERE ma_nguoi_dung = %s AND ma_san_pham = %s
        """, (ma_nguoi_dung, ma_san_pham))
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Đã xóa yêu thích thành công."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@app.post("/themVaoGioHang")
def them_vao_gio_hang(
    ma_nguoi_dung: int = Form(...),
    ma_bien_the: int = Form(...),
    so_luong: int = Form(1)
):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được database.")
        cursor = conn.cursor(dictionary=True)

        # Tìm mã sản phẩm và màu của biến thể
        cursor.execute("""
            SELECT ma_san_pham, ma_mau FROM BienTheSanPham WHERE ma_bien_the = %s
        """, (ma_bien_the,))
        bien_the = cursor.fetchone()
        if not bien_the:
            raise HTTPException(status_code=404, detail="Không tìm thấy biến thể sản phẩm.")

        ma_san_pham = bien_the["ma_san_pham"]
        ma_mau = bien_the["ma_mau"]

        # Lấy ảnh đầu tiên theo màu đó
        cursor.execute("""
            SELECT duong_dan FROM AnhBienThe
            WHERE ma_san_pham = %s AND ma_mau = %s
            ORDER BY ma_anh ASC LIMIT 1
        """, (ma_san_pham, ma_mau))
        img = cursor.fetchone()
        duong_dan_anh = img["duong_dan"] if img else ""

        # Nếu đã có => cập nhật số lượng
        cursor.execute("""
            SELECT so_luong FROM GioHang WHERE ma_nguoi_dung = %s AND ma_bien_the = %s
        """, (ma_nguoi_dung, ma_bien_the))
        row = cursor.fetchone()
        if row:
            so_luong_moi = row["so_luong"] + so_luong
            cursor.execute("""
                UPDATE GioHang SET so_luong = %s WHERE ma_nguoi_dung = %s AND ma_bien_the = %s
            """, (so_luong_moi, ma_nguoi_dung, ma_bien_the))
        else:
            cursor.execute("""
                INSERT INTO GioHang (ma_nguoi_dung, ma_bien_the, so_luong, duong_dan_anh)
                VALUES (%s, %s, %s, %s)
            """, (ma_nguoi_dung, ma_bien_the, so_luong, duong_dan_anh))

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Thêm vào giỏ hàng thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/themVaoGioHang")
# def them_vao_gio_hang(
#     ma_nguoi_dung: int = Form(...),
#     ma_bien_the: int = Form(...),
#     so_luong: int = Form(1)
# ):
#     try:
#         conn = db.connect_to_database()
#         if conn is None:
#             raise HTTPException(status_code=500, detail="Không kết nối được database.")
#         cursor = conn.cursor()

#         # Kiểm tra nếu đã có trong giỏ hàng => cộng dồn
#         cursor.execute("""
#             SELECT so_luong FROM GioHang WHERE ma_nguoi_dung = %s AND ma_bien_the = %s
#         """, (ma_nguoi_dung, ma_bien_the))
#         row = cursor.fetchone()
#         if row:
#             so_luong_moi = row[0] + so_luong
#             cursor.execute("""
#                 UPDATE GioHang SET so_luong = %s WHERE ma_nguoi_dung = %s AND ma_bien_the = %s
#             """, (so_luong_moi, ma_nguoi_dung, ma_bien_the))
#         else:
#             cursor.execute("""
#                 INSERT INTO GioHang (ma_nguoi_dung, ma_bien_the, so_luong)
#                 VALUES (%s, %s, %s)
#             """, (ma_nguoi_dung, ma_bien_the, so_luong))

#         conn.commit()
#         cursor.close()
#         conn.close()
#         return {"message": "Thêm vào giỏ hàng thành công"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.get("/getGioHangTheoNguoiDung")
def lay_gio_hang(ma_nguoi_dung: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                gh.ma_gio_hang,
                gh.so_luong,
                b.ma_bien_the,
                b.kich_thuoc,
                ms.ten_mau,
                sp.ma_san_pham,
                sp.ten_san_pham,
                sp.gia,
                IFNULL(gh.duong_dan_anh, sp.anh_san_pham) AS anh_san_pham,
                b.so_luong_ton,
                sp.ma_danh_muc  -- ✅ thêm dòng này
            FROM GioHang gh
            JOIN BienTheSanPham b ON gh.ma_bien_the = b.ma_bien_the
            JOIN MauSac ms ON b.ma_mau = ms.ma_mau
            JOIN SanPham sp ON b.ma_san_pham = sp.ma_san_pham
            WHERE gh.ma_nguoi_dung = %s
        """, (ma_nguoi_dung,))

        
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result if result else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/suaBienTheSanPham")
def sua_bien_the_san_pham(
    ma_bien_the: int = Form(...),
    kich_thuoc: str = Form(...),
    ma_mau: int = Form(...),
    so_luong_ton: int = Form(...)
):
    try:
        conn = db.connect_to_database()
        if not conn:
            raise HTTPException(status_code=500, detail="Không kết nối được cơ sở dữ liệu")

        cursor = conn.cursor()

        # Kiểm tra biến thể có tồn tại
        cursor.execute("SELECT * FROM BienTheSanPham WHERE ma_bien_the = %s", (ma_bien_the,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Biến thể không tồn tại.")

        # Cập nhật
        cursor.execute("""
            UPDATE BienTheSanPham
            SET kich_thuoc = %s, ma_mau = %s, so_luong_ton = %s
            WHERE ma_bien_the = %s
        """, (kich_thuoc, ma_mau, so_luong_ton, ma_bien_the))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Cập nhật biến thể sản phẩm thành công."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
# @app.get("/getGioHangTheoNguoiDung")
# def lay_gio_hang(ma_nguoi_dung: int = Query(...)):
#     try:
#         conn = db.connect_to_database()
#         if conn is None:
#             raise HTTPException(status_code=500, detail="Không kết nối được DB")
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT 
#                 gh.ma_gio_hang,
#                 gh.so_luong,
#                 b.kich_thuoc,
#                 ms.ten_mau,
#                 sp.ten_san_pham,
#                 sp.gia,
#                 sp.anh_san_pham
#             FROM GioHang gh
#             JOIN BienTheSanPham b ON gh.ma_bien_the = b.ma_bien_the
#             JOIN MauSac ms ON b.ma_mau = ms.ma_mau
#             JOIN SanPham sp ON b.ma_san_pham = sp.ma_san_pham
#             WHERE gh.ma_nguoi_dung = %s
#         """, (ma_nguoi_dung,))
        
#         result = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         return result if result else []

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/xoaGioHang")
def xoa_gio_hang(ma_gio_hang: int = Form(...)):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không thể kết nối DB")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM GioHang WHERE ma_gio_hang = %s", (ma_gio_hang,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Đã xóa khỏi giỏ hàng thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import Query

@app.delete("/xoaAnhBienThe")
def xoa_anh_bien_the(ma_anh: int = Query(..., description="Mã ảnh cần xóa")):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            # Lấy đường dẫn ảnh trước khi xóa (nếu muốn xóa cả file trên ổ cứng)
            cursor.execute("SELECT duong_dan FROM AnhBienThe WHERE ma_anh = %s", (ma_anh,))
            row = cursor.fetchone()

            if not row:
                cursor.close()
                conn.close()
                return {"message": f"Không tìm thấy ảnh với mã {ma_anh}."}

            # Xóa bản ghi trong DB
            cursor.execute("DELETE FROM AnhBienThe WHERE ma_anh = %s", (ma_anh,))
            conn.commit()

            cursor.close()
            conn.close()

            # (Tùy chọn) Xóa ảnh khỏi ổ cứng
            file_path = row["duong_dan"].lstrip("/")  # bỏ dấu / đầu nếu có
            if os.path.exists(file_path):
                os.remove(file_path)

            return {"message": f"Đã xóa ảnh mã {ma_anh} thành công."}
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/getAnhTheoMau")
def get_anh_theo_mau(ma_san_pham: int = Query(...), ma_mau: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT duong_dan FROM AnhBienThe
                WHERE ma_san_pham = %s AND ma_mau = %s
            """, (ma_san_pham, ma_mau))
            result = cursor.fetchall()

            cursor.close()
            conn.close()

            return result if result else []
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.put("/suaSanPham")
# def sua_san_pham(
#     ma_san_pham: int = Form(...),
#     ten_san_pham: str = Form(...),
#     mo_ta: str = Form(...),
#     gia: float = Form(...),
#     ma_danh_muc: int = Form(...),
#     file: UploadFile = File(None)  # Không bắt buộc gửi ảnh mới
# ):
#     try:
#         conn = db.connect_to_database()
#         if isinstance(conn, Error):
#             raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")

#         cursor = conn.cursor()

#         # Nếu có file ảnh mới thì lưu lại
#         anh_san_pham_url = None
#         if file:
#             file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#             anh_san_pham_url = f"/{UPLOAD_FOLDER}{file.filename}"

#         # Câu lệnh UPDATE
#         sql = """
#             UPDATE SanPham
#             SET ten_san_pham = %s,
#                 mo_ta = %s,
#                 gia = %s,
#                 ma_danh_muc = %s
#         """

#         values = [ten_san_pham, mo_ta, gia, ma_danh_muc]

#         if anh_san_pham_url:
#             sql += ", anh_san_pham = %s"
#             values.append(anh_san_pham_url)

#         sql += " WHERE ma_san_pham = %s"
#         values.append(ma_san_pham)

#         cursor.execute(sql, tuple(values))
#         conn.commit()

#         cursor.close()
#         conn.close()

#         return {
#             "message": "Cập nhật sản phẩm thành công.",
#             "ma_san_pham": ma_san_pham
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException


@app.post("/suaSanPham")
async def sua_san_pham(
    request: Request,
    ma_san_pham: int = Form(...),
    ten_san_pham: str = Form(...),
    mo_ta: str = Form(...),
    gia: float = Form(...),
    ma_danh_muc: int = Form(...),
    file: UploadFile = File(None)
):
    form = await request.form()
    method = form.get("_method", "").upper()
    
    if method != "PUT":
        raise HTTPException(status_code=400, detail="Phải gửi _method=PUT để cập nhật.")

    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")

        cursor = conn.cursor()

        anh_san_pham_url = None
        if file:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Tạo thư mục nếu chưa có
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            anh_san_pham_url = f"/{UPLOAD_FOLDER}{file.filename}"

        sql = """
            UPDATE SanPham
            SET ten_san_pham = %s,
                mo_ta = %s,
                gia = %s,
                ma_danh_muc = %s
        """
        values = [ten_san_pham, mo_ta, gia, ma_danh_muc]

        if anh_san_pham_url:
            sql += ", anh_san_pham = %s"
            values.append(anh_san_pham_url)

        sql += " WHERE ma_san_pham = %s"
        values.append(ma_san_pham)

        cursor.execute(sql, tuple(values))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm để cập nhật.")

        cursor.close()
        conn.close()

        return {
            "message": "Cập nhật sản phẩm thành công.",
            "ma_san_pham": ma_san_pham
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

# from fastapi import HTTPException
# from typing import Optional
# from pydantic import BaseModel

# class DiaChiCreate(BaseModel):
#     ma_nguoi_dung: int
#     so_dien_thoai: str
#     dia_chi: str
#     mac_dinh: Optional[bool] = False

# class DiaChiUpdate(BaseModel):
#     so_dien_thoai: str
#     dia_chi: str
#     mac_dinh: Optional[bool] = False




# @app.get("/dia-chi/{ma_nguoi_dung}")
# def get_dia_chi(ma_nguoi_dung: int):
#     conn = db.connect_to_database()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT * FROM DiaChiNguoiDung 
#         WHERE ma_nguoi_dung = %s 
#         ORDER BY mac_dinh DESC, id DESC
#     """, (ma_nguoi_dung,))
#     return cursor.fetchall()


@app.get("/admin/getAllDonHang")
def get_all_don_hang_admin():
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                dh.ma_don_hang,
                dh.ma_nguoi_dung,
                nd.ten_nguoi_dung,
                dh.ten_nguoi_nhan,
                dh.so_dien_thoai,
                dh.dia_chi_giao_hang,
                dh.tong_tien,
                dh.trang_thai,
                dh.ngay_tao,
                dh.voucher_id
            FROM DonHang dh
            LEFT JOIN NguoiDung nd ON dh.ma_nguoi_dung = nd.ma_nguoi_dung
            ORDER BY dh.ngay_tao DESC
        """)

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel

class CapNhatTrangThaiRequest(BaseModel):
    ma_don_hang: int
    trang_thai_moi: str

@app.put("/capNhatTrangThaiDonHang")
def cap_nhat_trang_thai_don_hang(request: CapNhatTrangThaiRequest):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")

        cursor = conn.cursor()

        # Danh sách trạng thái hợp lệ
        trang_thai_hop_le = {
            "Chờ xác nhận", 
            "Chờ lấy hàng", 
            "Chờ giao hàng", 
            "Đã giao", 
            "Đã hủy"
        }

        if request.trang_thai_moi not in trang_thai_hop_le:
            raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")

        # Kiểm tra đơn hàng tồn tại
        cursor.execute("SELECT * FROM DonHang WHERE ma_don_hang = %s", (request.ma_don_hang,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

        # Cập nhật trạng thái
        cursor.execute("""
            UPDATE DonHang
            SET trang_thai = %s
            WHERE ma_don_hang = %s
        """, (request.trang_thai_moi, request.ma_don_hang))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Cập nhật trạng thái thành công"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# class DiaChiModel(BaseModel):
#     id: Optional[int]
#     ma_nguoi_dung: int
#     ten_nguoi_nhan: str
#     so_dien_thoai: str
#     dia_chi: str
#     mac_dinh: Optional[bool] = False
#     ngay_tao: Optional[datetime]


# @app.get("/diachi", response_model=List[DiaChiModel])
# def get_danh_sach_dia_chi(ma_nguoi_dung: int):
#     try:
#         conn = db.connect_to_database()
#         if isinstance(conn, Error):
#             raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE ma_nguoi_dung = %s ORDER BY ngay_tao DESC", (ma_nguoi_dung,))
#         results = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         return results
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


# @app.get("/diachi/macdinh", response_model=DiaChiModel)
# def get_mac_dinh(ma_nguoi_dung: int):
#     try:
#         conn = db.connect_to_database()
#         if isinstance(conn, Error):
#             raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE ma_nguoi_dung = %s AND mac_dinh = TRUE", (ma_nguoi_dung,))
#         result = cursor.fetchone()

#         cursor.close()
#         conn.close()

#         if not result:
#             raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ mặc định")

#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")



class DiaChiModel(BaseModel):
    id: Optional[int] = None
    ma_nguoi_dung: int
    ten_nguoi_nhan: str
    so_dien_thoai: str
    dia_chi: str
    mac_dinh: Optional[bool] = False
    ngay_tao: Optional[datetime] = None

@app.post("/themdiachi", response_model=DiaChiModel)
def them_dia_chi(address: DiaChiModel):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor(dictionary=True)

        if address.mac_dinh:
            cursor.execute("UPDATE DiaChiNguoiDung SET mac_dinh = FALSE WHERE ma_nguoi_dung = %s", (address.ma_nguoi_dung,))

        cursor.execute("""
            INSERT INTO DiaChiNguoiDung (ma_nguoi_dung, ten_nguoi_nhan, so_dien_thoai, dia_chi, mac_dinh)
            VALUES (%s, %s, %s, %s, %s)
        """, (address.ma_nguoi_dung, address.ten_nguoi_nhan, address.so_dien_thoai, address.dia_chi, address.mac_dinh))

        conn.commit()
        new_id = cursor.lastrowid

        cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE id = %s", (new_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=500, detail="Không thể lấy địa chỉ vừa tạo")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@app.get("/danhsachdiachi", response_model=List[DiaChiModel])
def get_danh_sach_dia_chi(ma_nguoi_dung: int):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM DiaChiNguoiDung 
            WHERE ma_nguoi_dung = %s 
            ORDER BY ngay_tao DESC
        """, (ma_nguoi_dung,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


class DiaChiUpdateModel(BaseModel):
    ten_nguoi_nhan: Optional[str]
    so_dien_thoai: Optional[str]
    dia_chi: Optional[str]
    mac_dinh: Optional[bool] = False


@app.put("/capnhatdiachi/{id}")
def cap_nhat_dia_chi(id: int = Path(..., gt=0), diachi: DiaChiUpdateModel = None):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE id = %s", (id,))
        old_data = cursor.fetchone()
        if not old_data:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")

        if diachi.mac_dinh:
            cursor.execute("UPDATE DiaChiNguoiDung SET mac_dinh = FALSE WHERE ma_nguoi_dung = %s", (old_data['ma_nguoi_dung'],))

        cursor.execute("""
            UPDATE DiaChiNguoiDung
            SET ten_nguoi_nhan = %s,
                so_dien_thoai = %s,
                dia_chi = %s,
                mac_dinh = %s
            WHERE id = %s
        """, (
            diachi.ten_nguoi_nhan or old_data['ten_nguoi_nhan'],
            diachi.so_dien_thoai or old_data['so_dien_thoai'],
            diachi.dia_chi or old_data['dia_chi'],
            diachi.mac_dinh,
            id
        ))

        conn.commit()
        cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE id = %s", (id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")





@app.delete("/diachi/{id}")
def xoa_dia_chi(id: int):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")

        cursor.execute("DELETE FROM DiaChiNguoiDung WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Đã xóa địa chỉ thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@app.put("/diachi/macdinh")
def dat_mac_dinh(ma_nguoi_dung: int, id: int):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM DiaChiNguoiDung WHERE id = %s AND ma_nguoi_dung = %s", (id, ma_nguoi_dung))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")

        cursor.execute("UPDATE DiaChiNguoiDung SET mac_dinh = FALSE WHERE ma_nguoi_dung = %s", (ma_nguoi_dung,))
        cursor.execute("UPDATE DiaChiNguoiDung SET mac_dinh = TRUE WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Đã đặt làm địa chỉ mặc định"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.get("/sanpham_lienquan")
def lay_sanpham_lien_quan(ma_danh_muc: int, ma_san_pham: int):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ma_san_pham, ten_san_pham, gia, anh_san_pham
            FROM SanPham
            WHERE ma_danh_muc = %s AND ma_san_pham != %s
            LIMIT 10
        """, (ma_danh_muc, ma_san_pham))

        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@app.post("/themPhuongThucVanChuyen")
def them_phuong_thuc_van_chuyen(
    ten_phuong_thuc: str = Form(...),
    chi_phi: float = Form(...),
    trang_thai: str = Form('hoat_dong')  # mặc định là 'hoat_dong'
):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Không thể kết nối CSDL")

        cursor = conn.cursor()

        sql = """
            INSERT INTO PhuongThucVanChuyen (ten_phuong_thuc, chi_phi, trang_thai)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (ten_phuong_thuc, chi_phi, trang_thai))
        conn.commit()

        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return {
            "message": "Thêm phương thức vận chuyển thành công.",
            "id": new_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.get("/getAllPhuongThucVanChuyen")
def get_all_phuong_thuc_van_chuyen():
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Không thể kết nối CSDL")

        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM PhuongThucVanChuyen WHERE trang_thai = 'hoat_dong'"
        cursor.execute(sql)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.post("/themVoucher")
def them_voucher(
    ma_voucher: str = Form(...),
    mo_ta_hien_thi: str = Form(...),
    loai: str = Form(...),  # 'ship' hoặc 'order'
    kieu_giam: str = Form(...),  # 'phan_tram' hoặc 'tien_mat'
    gia_tri: float = Form(...),
    dieu_kien_ap_dung: float = Form(0),
    so_luong: int = Form(1),
    ngay_bat_dau: str = Form(...),  # format: 'YYYY-MM-DD HH:MM:SS'
    ngay_ket_thuc: str = Form(...),
    hien_thi_auto: bool = Form(False),
    trang_thai: str = Form("hoat_dong"),
    nguoi_tao: int = Form(...),
    hinh_anh: UploadFile = File(...)
):
    try:
        # Lưu hình ảnh
        file_path = os.path.join(UPLOAD_FOLDER, hinh_anh.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(hinh_anh.file, buffer)
        hinh_anh_url = f"/{UPLOAD_FOLDER}{hinh_anh.filename}"

        # Kết nối CSDL
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")
        cursor = conn.cursor()

        sql = """
            INSERT INTO voucher (
                ma_voucher, mo_ta_hien_thi, loai, kieu_giam, gia_tri,
                dieu_kien_ap_dung, so_luong, ngay_bat_dau, ngay_ket_thuc,
                hinh_anh, hien_thi_auto, trang_thai, nguoi_tao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            ma_voucher,
            mo_ta_hien_thi,
            loai,
            kieu_giam,
            gia_tri,
            dieu_kien_ap_dung,
            so_luong,
            ngay_bat_dau,
            ngay_ket_thuc,
            hinh_anh_url,
            hien_thi_auto,
            trang_thai,
            nguoi_tao
        )

        cursor.execute(sql, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return {
            "message": "Thêm voucher thành công",
            "id": new_id,
            "hinh_anh": hinh_anh_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

@app.get("/getAllVoucher")
def get_all_voucher():
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                id,
                ma_voucher,
                mo_ta_hien_thi,
                loai,
                kieu_giam,
                gia_tri,
                dieu_kien_ap_dung,
                so_luong,
                ngay_bat_dau,
                ngay_ket_thuc,
                hinh_anh,
                hien_thi_auto,
                trang_thai,
                ngay_tao,
                ngay_cap_nhat
            FROM voucher
        """)

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        if result:
            return result
        else:
            return JSONResponse(content={"message": "Không có voucher nào"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

# API 1: Lấy tất cả voucher theo loại
# @app.get("/layVoucherTheoLoai")
# def lay_voucher_theo_loai(loai: str = Query(...)):
#     try:
#         conn = db.connect_to_database()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT * FROM voucher
#             WHERE loai = %s AND trang_thai = 'hoat_dong'
#             AND ngay_bat_dau <= NOW() AND ngay_ket_thuc >= NOW()
#         """, (loai,))
#         return cursor.fetchall()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.get("/getVoucherTheoLoai")
def get_voucher_theo_loai(loai: str = Query(...)):
    try:
        conn = db.connect_to_database()
        if isinstance(conn, Error):
            raise HTTPException(status_code=500, detail="Lỗi kết nối CSDL")

        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT * FROM voucher
            WHERE loai = %s 
              AND trang_thai = 'hoat_dong'
              AND hien_thi_auto = 1
              AND NOW() BETWEEN ngay_bat_dau AND ngay_ket_thuc
              AND so_luong > 0
        """

        cursor.execute(sql, (loai,))
        vouchers = cursor.fetchall()
        cursor.close()
        conn.close()

        return vouchers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API 2: Kiểm tra mã voucher
@app.get("/kiemTraVoucher")
def kiem_tra_voucher(ma_voucher: str, ma_nguoi_dung: int):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM voucher
            WHERE ma_voucher = %s AND trang_thai = 'hoat_dong'
            AND ngay_bat_dau <= NOW() AND ngay_ket_thuc >= NOW()
        """, (ma_voucher,))
        voucher = cursor.fetchone()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher không tồn tại hoặc đã hết hạn")

        cursor.execute("""
            SELECT * FROM NguoiDungVoucher
            WHERE ma_nguoi_dung = %s AND voucher_id = %s
        """, (ma_nguoi_dung, voucher['id']))
        if cursor.fetchone():
            return {"message": "Voucher đã tồn tại"}

        return voucher
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API 3: Áp dụng voucher cho người dùng
class LuuVoucherRequest(BaseModel):
    ma_nguoi_dung: int
    voucher_id: int

@app.post("/luuVoucherNguoiDung")
def luu_voucher(request: LuuVoucherRequest):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NguoiDungVoucher (ma_nguoi_dung, voucher_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE da_su_dung = FALSE
        """, (request.ma_nguoi_dung, request.voucher_id))
        conn.commit()
        return {"message": "Lưu voucher thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API 4: Hiển thị các voucher chưa sử dụng
@app.get("/voucherNguoiDungChuaDung")
def get_voucher_chua_dung(ma_nguoi_dung: int = Query(...)):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)
        
        # Trả đầy đủ các trường cần thiết, không thiếu ngày/thông tin ảnh
        cursor.execute("""
            SELECT 
                v.id,
                v.ma_voucher,
                v.mo_ta_hien_thi,
                v.loai,
                v.kieu_giam,
                v.gia_tri,
                v.dieu_kien_ap_dung,
                v.ngay_bat_dau,
                v.ngay_ket_thuc,
                v.hinh_anh,
                v.hien_thi_auto,
                v.trang_thai
            FROM NguoiDungVoucher nv
            JOIN voucher v ON nv.voucher_id = v.id
            WHERE nv.ma_nguoi_dung = %s 
              AND nv.da_su_dung = FALSE
              AND v.trang_thai = 'hoat_dong'
              AND v.ngay_bat_dau <= NOW()
              AND v.ngay_ket_thuc >= NOW()
        """, (ma_nguoi_dung,))
        
        return cursor.fetchall()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/adminGetAllDonHang")
def admin_get_all_don_hang():
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                dh.ma_don_hang,
                dh.ten_nguoi_nhan,
                dh.so_dien_thoai,
                dh.dia_chi_giao_hang,
                dh.tong_tien,
                dh.trang_thai,
                dh.ngay_tao,
                dh.voucher_order_id,
                dh.voucher_ship_id,
                vc1.ma_voucher AS voucher_order,
                vc2.ma_voucher AS voucher_ship,
                ptvc.ten_phuong_thuc,
                ptvc.chi_phi AS chi_phi_van_chuyen,
                nd.ten_nguoi_dung AS ten_nguoi_dung
            FROM DonHang dh
            LEFT JOIN voucher vc1 ON dh.voucher_order_id = vc1.id
            LEFT JOIN voucher vc2 ON dh.voucher_ship_id = vc2.id
            LEFT JOIN PhuongThucVanChuyen ptvc ON dh.phuong_thuc_id = ptvc.id
            LEFT JOIN NguoiDung nd ON dh.ma_nguoi_dung = nd.ma_nguoi_dung
            ORDER BY dh.ngay_tao DESC
        """)

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/tongquan")
def get_dashboard_tong_quan():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)

            # Đơn hàng
            cursor.execute("SELECT COUNT(*) AS so_don FROM DonHang")
            so_don = cursor.fetchone()['so_don']

            # Tổng doanh thu
            cursor.execute("SELECT COALESCE(SUM(tong_tien), 0) AS tong_doanh_thu FROM DonHang")
            tong_doanh_thu = cursor.fetchone()['tong_doanh_thu']

            # Người dùng
            cursor.execute("SELECT COUNT(*) AS so_nguoi_dung FROM NguoiDung")
            so_nguoi_dung = cursor.fetchone()['so_nguoi_dung']

            # Sản phẩm
            cursor.execute("SELECT COUNT(*) AS so_san_pham FROM SanPham")
            so_san_pham = cursor.fetchone()['so_san_pham']

            cursor.close()
            conn.close()

            return {
                "so_don": so_don,
                "tong_doanh_thu": tong_doanh_thu,
                "so_nguoi_dung": so_nguoi_dung,
                "so_san_pham": so_san_pham
            }

        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@app.get("/dashboard/doanhthu-theo-thang")
def get_doanh_thu_theo_thang():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    MONTH(ngay_tao) AS thang, 
                    SUM(tong_tien) AS doanh_thu
                FROM DonHang
                WHERE YEAR(ngay_tao) = YEAR(NOW()) AND trang_thai = 'đã giao'
                GROUP BY MONTH(ngay_tao)
                ORDER BY thang
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/dashboard/trangthai-donhang")
def get_thong_ke_trang_thai_don_hang():
    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT trang_thai, COUNT(*) AS so_luong
                FROM DonHang
                GROUP BY trang_thai
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@app.put("/autoUpdateTrangThaiVoucher")
def auto_update_voucher_trang_thai():
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Tạm ngưng nếu đã hết hạn
        cursor.execute("""
            UPDATE voucher 
            SET trang_thai = 'tam_ngung' 
            WHERE ngay_ket_thuc IS NOT NULL 
                AND ngay_ket_thuc < %s 
                AND trang_thai != 'tam_ngung'
        """, (now,))

        # Hoạt động lại nếu đang trong thời gian hợp lệ
        cursor.execute("""
            UPDATE voucher 
            SET trang_thai = 'hoat_dong' 
            WHERE ngay_bat_dau <= %s 
                AND (ngay_ket_thuc IS NULL OR ngay_ket_thuc > %s)
                AND trang_thai != 'hoat_dong'
        """, (now, now))

        conn.commit()
        conn.close()

        return {"message": "Đã cập nhật trạng thái voucher tự động"}

    except Exception as e:
        return {"error": str(e)}  # Trả lỗi chi tiết để debug
    
class VoucherUpdateTime(BaseModel):
    id: int
    ngay_bat_dau: datetime
    ngay_ket_thuc: datetime

@app.post("/capnhatThoiGianVoucher")
def capnhat_thoi_gian_voucher(data: VoucherUpdateTime):
    conn = db.connect_to_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE voucher 
            SET ngay_bat_dau = %s, ngay_ket_thuc = %s
            WHERE id = %s
        """, (data.ngay_bat_dau, data.ngay_ket_thuc, data.id))

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy voucher cần cập nhật")

        return {"message": "Cập nhật thành công"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

import email_utils
import random, string
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
otp_storage = {}  # Tạm thời lưu OTP trong RAM, key = email
from email_utils import send_otp_email
otp_verified_emails = set()

@app.post("/guiOTP")
def gui_otp(email: str = Form(...)):
    try:
        otp_code = ''.join(random.choices(string.digits, k=6))
        email_utils.send_otp_email(email, otp_code)

        otp_storage[email] = {
            "otp": otp_code,
            "expires_at": datetime.utcnow() + timedelta(seconds=3000)
        }

        return {"message": "Mã OTP đã được gửi"}
    except Exception as e:
        print(f"[ERROR] gửi OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/xacThucOTP")
def xac_thuc_otp(email: str = Form(...), otp: str = Form(...)):
    if email not in otp_storage:
        raise HTTPException(status_code=400, detail="Chưa gửi mã OTP")

    otp_info = otp_storage[email]
    if datetime.utcnow() > otp_info["expires_at"]:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")

    if otp != otp_info["otp"]:
        raise HTTPException(status_code=400, detail="Mã OTP không đúng")

    # ✅ Lưu vào danh sách đã xác thực
    otp_verified_emails.add(email)
    del otp_storage[email]

    return {"message": "Xác thực OTP thành công"}


from fastapi import Body

class UserCreate(BaseModel):
    ten_nguoi_dung: str
    email: str
    mat_khau: str
    sdt: str
    dia_chi_mac_dinh: str
    vai_tro: str = "user"



@app.post("/themUser")
def them_user(user: UserCreate = Body(...)):
    if user.email not in otp_verified_emails:
        raise HTTPException(status_code=400, detail="Bạn cần xác thực OTP trước khi đăng ký!")

    try:
        conn = db.connect_to_database()
        if not isinstance(conn, Error):
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM NguoiDung WHERE email = %s", (user.email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {"message": f"Email '{user.email}' đã tồn tại."}

            sql = """
                INSERT INTO NguoiDung (ten_nguoi_dung, email, mat_khau, sdt, dia_chi_mac_dinh, vai_tro)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                user.ten_nguoi_dung,
                user.email,
                user.mat_khau,
                user.sdt,
                user.dia_chi_mac_dinh,
                user.vai_tro
            )
            cursor.execute(sql, values)
            conn.commit()
            user_id = cursor.lastrowid

            cursor.close()
            conn.close()

            otp_verified_emails.discard(user.email)

            return {
                "message": "Thêm người dùng thành công.",
                "ma_nguoi_dung": user_id
            }
        else:
            raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    


class DonHangItem(BaseModel):
    ma_gio_hang: int
    ma_bien_the: int
    so_luong: int

class DonHangRequest(BaseModel):
    ma_nguoi_dung: int
    ten_nguoi_nhan: str
    so_dien_thoai: str
    dia_chi_giao_hang: str
    thanh_toan: str
    phuong_thuc_id: int  
    voucher_order_id: Optional[int] = None
    voucher_ship_id: Optional[int] = None
    san_pham: List[DonHangItem]


from email_utils import send_order_email




@app.post("/taoDonHang")
def tao_don_hang(request: DonHangRequest):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)

        # Tính tổng tiền hàng
        tong_tien = 0
        for item in request.san_pham:
            cursor.execute("""
                SELECT s.gia FROM BienTheSanPham b
                JOIN SanPham s ON b.ma_san_pham = s.ma_san_pham
                WHERE b.ma_bien_the = %s
            """, (item.ma_bien_the,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy biến thể")
            tong_tien += row['gia'] * item.so_luong

        # Tạo đơn hàng
        cursor.execute("""
            INSERT INTO DonHang (
                ma_nguoi_dung, ten_nguoi_nhan, so_dien_thoai, dia_chi_giao_hang,
                tong_tien, trang_thai, ngay_tao,
                voucher_order_id, voucher_ship_id, phuong_thuc_id
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
        """, (
            request.ma_nguoi_dung,
            request.ten_nguoi_nhan,
            request.so_dien_thoai,
            request.phuong_thuc_id,
            tong_tien,
            "Chờ xác nhận",
            request.voucher_order_id,
            request.voucher_ship_id,
            request.phuong_thuc_id
        ))

        ma_don_hang = cursor.lastrowid

        # Chi tiết đơn hàng
        for item in request.san_pham:
            cursor.execute("""
                SELECT s.gia FROM BienTheSanPham b
                JOIN SanPham s ON b.ma_san_pham = s.ma_san_pham
                WHERE b.ma_bien_the = %s
            """, (item.ma_bien_the,))
            gia = cursor.fetchone()['gia']

            cursor.execute("""
                INSERT INTO ChiTietDonHang (ma_don_hang, ma_bien_the, so_luong, gia)
                VALUES (%s, %s, %s, %s)
            """, (ma_don_hang, item.ma_bien_the, item.so_luong, gia))

            cursor.execute("""
                UPDATE BienTheSanPham SET so_luong_ton = so_luong_ton - %s
                WHERE ma_bien_the = %s
            """, (item.so_luong, item.ma_bien_the))

            cursor.execute("DELETE FROM GioHang WHERE ma_gio_hang = %s", (item.ma_gio_hang,))
        # Trừ số lượng và đánh dấu đã dùng cho voucher_order_id
        # Nếu có voucher đơn hàng → trừ số lượng và đánh dấu đã sử dụng
        if request.voucher_order_id:
            cursor.execute("""
                UPDATE voucher SET so_luong = so_luong - 1 WHERE id = %s AND so_luong > 0
            """, (request.voucher_order_id,))
            cursor.execute("""
                UPDATE NguoiDungVoucher 
                SET da_su_dung = TRUE, ngay_su_dung = NOW()
                WHERE voucher_id = %s AND ma_nguoi_dung = %s
            """, (request.voucher_order_id, request.ma_nguoi_dung))

        # Nếu có voucher ship → trừ số lượng và đánh dấu đã sử dụng
        if request.voucher_ship_id:
            cursor.execute("""
                UPDATE voucher SET so_luong = so_luong - 1 WHERE id = %s AND so_luong > 0
            """, (request.voucher_ship_id,))
            cursor.execute("""
                UPDATE NguoiDungVoucher 
                SET da_su_dung = TRUE, ngay_su_dung = NOW()
                WHERE voucher_id = %s AND ma_nguoi_dung = %s
            """, (request.voucher_ship_id, request.ma_nguoi_dung))

       # ✅ Sau khi đơn hàng được tạo thành công
        # 2. Gửi email cảm ơn người dùng
        # Sau khi insert đơn hàng và lấy được ma_don_hang

# Truy vấn email người dùng từ bảng NguoiDung
        # Truy vấn lấy email người dùng
# Lấy email người dùng để gửi
        cursor.execute("SELECT email FROM NguoiDung WHERE ma_nguoi_dung = %s", (request.ma_nguoi_dung,))
        user = cursor.fetchone()
        if user:
            email = user["email"]
            subject = f"Xác nhận đơn hàng #{ma_don_hang}"
            content = f"""
            <h3>Xin chào {request.ten_nguoi_nhan},</h3>
            <p>Cảm ơn bạn đã đặt hàng tại DoubleH Store.</p>
            <p>Mã đơn hàng của bạn là <strong>#{ma_don_hang}</strong>.</p>
            <p>Chúng tôi sẽ xử lý đơn hàng trong thời gian sớm nhất.</p>
            <br>
            <p>Thân mến,<br>DoubleH Team</p>
            """
            try:
                send_order_email(email, request.ten_nguoi_nhan, ma_don_hang, tong_tien)
            except Exception as mail_err:
                print(f"[EMAIL ERROR] Không gửi được email: {mail_err}")
                # Không raise lỗi ở đây để không làm hỏng đơn hàng

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Tạo đơn hàng thành công", "ma_don_hang": ma_don_hang}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/getAllDonHang")
def get_all_don_hang(ma_nguoi_dung: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
           SELECT 
            dh.ma_don_hang,
            dh.ten_nguoi_nhan,
            dh.so_dien_thoai,
            dc.dia_chi AS dia_chi_giao_hang,
            dh.tong_tien,
            dh.trang_thai,
            dh.ngay_tao,
            vo.ma_voucher AS voucher_order,
            vs.ma_voucher AS voucher_ship,
            ptvc.ten_phuong_thuc,
            ptvc.chi_phi AS chi_phi_van_chuyen
          FROM DonHang dh
          LEFT JOIN voucher vo ON dh.voucher_order_id = vo.id
          LEFT JOIN voucher vs ON dh.voucher_ship_id = vs.id
          LEFT JOIN phuongthucvanchuyen ptvc ON dh.phuong_thuc_id = ptvc.id
          LEFT JOIN DiaChiNguoiDung dc ON dh.dia_chi_giao_hang = dc.id
          WHERE dh.ma_nguoi_dung = %s
          ORDER BY dh.ngay_tao DESC
        """, (ma_nguoi_dung,))

        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result if result else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ---------------------------------------------------------------------------------------------------------------
@app.get("/getChiTietDonHang")
def get_chi_tiet_don_hang(ma_don_hang: int = Query(...)):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")
        
        cursor = conn.cursor(dictionary=True)

        # Lấy thông tin đơn hàng kèm địa chỉ giao hàng và phương thức
        cursor.execute("""
            SELECT 
                dh.ma_don_hang,
                dh.ma_nguoi_dung,
                dh.tong_tien,
                dh.voucher_order_id,
                dh.voucher_ship_id,
                dh.phuong_thuc_id,
                dh.trang_thai,
                dh.ngay_tao,
                dc.ten_nguoi_nhan,
                dc.so_dien_thoai,
                dc.dia_chi AS dia_chi_giao_hang,
                ptvc.ten_phuong_thuc,
                ptvc.chi_phi AS chi_phi_van_chuyen
            FROM DonHang dh
            LEFT JOIN DiaChiNguoiDung dc ON dh.dia_chi_giao_hang = dc.id
            LEFT JOIN PhuongThucVanChuyen ptvc ON dh.phuong_thuc_id = ptvc.id
            WHERE dh.ma_don_hang = %s
        """, (ma_don_hang,))
        don_hang_info = cursor.fetchone()
        if not don_hang_info:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

        # Lấy chi tiết sản phẩm trong đơn hàng
        cursor.execute("""
            SELECT 
                sp.ten_san_pham,
                ms.ten_mau,
                b.kich_thuoc,
                ct.so_luong,
                ct.gia,
                IFNULL(ab.duong_dan, sp.anh_san_pham) AS hinh_anh
            FROM ChiTietDonHang ct
            JOIN BienTheSanPham b ON ct.ma_bien_the = b.ma_bien_the
            JOIN SanPham sp ON b.ma_san_pham = sp.ma_san_pham
            JOIN MauSac ms ON b.ma_mau = ms.ma_mau
            LEFT JOIN (
                SELECT ma_san_pham, ma_mau, MIN(ma_anh) AS ma_anh
                FROM AnhBienThe
                GROUP BY ma_san_pham, ma_mau
            ) first_ab ON first_ab.ma_san_pham = sp.ma_san_pham AND first_ab.ma_mau = ms.ma_mau
            LEFT JOIN AnhBienThe ab ON ab.ma_anh = first_ab.ma_anh
            WHERE ct.ma_don_hang = %s
        """, (ma_don_hang,))
        chi_tiet = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "don_hang": don_hang_info,
            "chi_tiet": chi_tiet
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/huyDonHang")
def huy_don_hang(ma_don_hang: int = Form(...)):
    try:
        conn = db.connect_to_database()
        if conn is None:
            raise HTTPException(status_code=500, detail="Không kết nối được DB")

        cursor = conn.cursor()
        # Chỉ được hủy nếu trạng thái hiện tại là "Chờ xác nhận"
        cursor.execute("SELECT trang_thai FROM DonHang WHERE ma_don_hang = %s", (ma_don_hang,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        if row[0] != "Chờ xác nhận":
            raise HTTPException(status_code=400, detail="Không thể hủy đơn hàng đã xử lý")

        cursor.execute("UPDATE DonHang SET trang_thai = %s WHERE ma_don_hang = %s", ("Đã hủy", ma_don_hang))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Đã hủy đơn hàng thành công"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/chi-tiet-don-hang/{ma_don_hang}")
# async def get_order_detail(ma_don_hang: int):
#     try:
#         conn = db.connect_to_database()
#         cursor = conn.cursor(dictionary=True)

#         # Lấy thông tin đơn hàng
#         cursor.execute("SELECT * FROM donhang WHERE ma_don_hang = %s", (ma_don_hang,))
#         don_hang = cursor.fetchone()

#         if not don_hang:
#             return JSONResponse(status_code=404, content={"message": "Không tìm thấy đơn hàng"})

#         # Lấy địa chỉ người nhận
#         cursor.execute("SELECT * FROM dia_chi WHERE id = %s", (don_hang['id_dia_chi'],))
#         dia_chi = cursor.fetchone()

#         # Lấy chi tiết sản phẩm
#         cursor.execute("""
#             SELECT ct.*, sp.ten_san_pham, bt.hinh_anh, ms.ten_mau, kt.kich_thuoc
#             FROM donhang_chitiet ct
#             JOIN bien_the_san_pham bt ON ct.id_bien_the = bt.id
#             JOIN sanpham sp ON bt.id_san_pham = sp.id
#             LEFT JOIN mau_sac ms ON bt.ma_mau = ms.ma_mau
#             LEFT JOIN kich_thuoc kt ON bt.ma_kich_thuoc = kt.ma_kich_thuoc
#             WHERE ct.ma_don_hang = %s
#         """, (ma_don_hang,))
#         chi_tiet_san_pham = cursor.fetchall()

#         return {
#             "don_hang": don_hang,
#             "dia_chi": dia_chi,
#             "san_pham": chi_tiet_san_pham
#         }

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"message": f"Lỗi server: {e}"})





@app.get("/nguoidung/{id}")
def get_user_by_id(id: int):
    conn = db.connect_to_database()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id AS ma_nguoi_dung, 
               hoTen AS ten_nguoi_dung, 
               email, 
               soDienThoai AS sdt, 
               diaChiMacDinh AS dia_chi_mac_dinh,
               vaiTro AS vai_tro
        FROM nguoidung
        WHERE id = %s
    """
    cursor.execute(query, (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")




@app.post("/capnhat-thong-tin")
async def cap_nhat_thong_tin(
    ma_nguoi_dung: int = Form(...),
    ten_nguoi_dung: str = Form(...),
    sdt: str = Form(...)
):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor()

        sql = """
            UPDATE nguoidung
            SET ten_nguoi_dung = %s, sdt = %s
            WHERE ma_nguoi_dung = %s
        """
        cursor.execute(sql, (ten_nguoi_dung, sdt, ma_nguoi_dung))
        conn.commit()

        return {"message": "Cập nhật thành công"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Cập nhật thất bại: {e}"})
    
#------------------Chi tiết nhập kho ----------------------------

# ----- SCHEMA -----
class ChiTietNhap(BaseModel):
    ma_san_pham: int
    ma_mau: int
    kich_thuoc: str
    so_luong: int

class TaoPhieuNhap(BaseModel):
    nguoi_nhap: str
    ngay_nhap: datetime
    chi_tiet: List[ChiTietNhap]

# ----- API -----
@app.post("/nhap-kho")
def nhap_kho(data: TaoPhieuNhap):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor()

        tong_so_luong = sum(item.so_luong for item in data.chi_tiet)

        # 1. Thêm phiếu nhập
        cursor.execute("""
            INSERT INTO PhieuNhap (nguoi_nhap, ngay_nhap, tong_so_luong)
            VALUES (%s, %s, %s)
        """, (data.nguoi_nhap, data.ngay_nhap, tong_so_luong))
        ma_phieu_nhap = cursor.lastrowid

        # 2 & 3: Chi tiết và cập nhật tồn kho
        for item in data.chi_tiet:
            # Thêm vào ChiTietPhieuNhap
            cursor.execute("""
                INSERT INTO ChiTietPhieuNhap
                (ma_phieu_nhap, ma_san_pham, ma_mau, kich_thuoc, so_luong)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                ma_phieu_nhap, item.ma_san_pham, item.ma_mau, item.kich_thuoc, item.so_luong
            ))

            # Cập nhật hoặc thêm vào BienTheSanPham
            cursor.execute("""
                INSERT INTO BienTheSanPham (ma_san_pham, ma_mau, kich_thuoc, so_luong_ton)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE so_luong_ton = so_luong_ton + VALUES(so_luong_ton)
            """, (
                item.ma_san_pham, item.ma_mau, item.kich_thuoc, item.so_luong
            ))

        conn.commit()
        return {"message": "Nhập kho thành công", "ma_phieu_nhap": ma_phieu_nhap}

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi DB: {str(e)}")

    finally:
        cursor.close()
        conn.close()

class PhieuNhapOut(BaseModel):
    ma_phieu_nhap: int
    nguoi_nhap: str
    ngay_nhap: datetime
    tong_so_luong: int

@app.get("/getAllPhieuNhap", response_model=List[PhieuNhapOut])
def get_all_phieu_nhap():
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM PhieuNhap ORDER BY ngay_nhap DESC")
        rows = cursor.fetchall()

        return rows

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn DB: {str(e)}")

    finally:
        cursor.close()
        conn.close()

# ----- SCHEMA -----
class ChiTietPhieuNhapOut(BaseModel):
    ma_san_pham: int
    ten_san_pham: str
    ma_mau: int
    ten_mau: str
    kich_thuoc: str
    so_luong: int

# ----- API GET -----
@app.get("/phieu-nhap/{ma_phieu_nhap}", response_model=List[ChiTietPhieuNhapOut])
def get_chi_tiet_phieu(ma_phieu_nhap: int):
    try:
        conn = db.connect_to_database()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT c.ma_san_pham, sp.ten_san_pham, c.ma_mau, m.ten_mau, c.kich_thuoc, c.so_luong
            FROM ChiTietPhieuNhap c
            JOIN SanPham sp ON c.ma_san_pham = sp.ma_san_pham
            JOIN MauSac m ON c.ma_mau = m.ma_mau
            WHERE c.ma_phieu_nhap = %s
        """, (ma_phieu_nhap,))
        rows = cursor.fetchall()

        return rows

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Lỗi DB: {str(e)}")
    finally:
        cursor.close()
        conn.close()