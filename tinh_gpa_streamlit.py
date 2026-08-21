# -*- coding: utf-8 -*-
"""
Ứng dụng tính số môn/tín tối đa đạt A, B, C còn lại để đạt GPA mục tiêu.
Phiên bản Streamlit — chuyển đổi từ bản Gradio, giữ nguyên toàn bộ
chức năng: thông tin tổng quan, bảng kết quả, biểu đồ trực quan,
thẻ màu phân loại mức độ khả thi và các giá trị mẫu.

Chạy: streamlit run tinh_gpa_streamlit.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # hỗ trợ dấu tiếng Việt

# ==== Hằng số chương trình học ====
TONG_TIN = 137          # tổng số tín chỉ toàn khóa
TIN_KHOA_LUAN = 9       # số tín khóa luận tốt nghiệp
TIN_MOI_MON = 3         # số tín trung bình của một môn thường
THANG_DIEM = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0}

MAU_XANH = "#2e7d32"
MAU_CAM = "#e65100"
MAU_DO = "#c62828"
MAU_NEN_XANH = "#e8f5e9"
MAU_NEN_CAM = "#fff3e0"
MAU_NEN_DO = "#ffebee"


# ==== Hàm tính toán lõi (giữ nguyên logic gốc) ====
def tinh_max_BC(tin_thuong_con_lai, ngan_sach, tin_moi_mon=TIN_MOI_MON):
    """Trả về (max_B_mon, max_C_mon, bang) hoặc None nếu bất khả thi."""
    if ngan_sach < 0:
        return None

    max_B_tin = min(int(ngan_sach // 1.0), tin_thuong_con_lai)
    max_C_tin = min(int(ngan_sach // 2.0), tin_thuong_con_lai)
    max_B_mon = max_B_tin // tin_moi_mon
    max_C_mon = max_C_tin // tin_moi_mon

    bang = []
    for so_C_mon in range(max_C_mon + 1):
        so_C_tin = so_C_mon * tin_moi_mon
        con_lai_ngan_sach = ngan_sach - so_C_tin * 2.0
        tin_con_du = tin_thuong_con_lai - so_C_tin
        so_B_tin = max(min(int(con_lai_ngan_sach // 1.0), tin_con_du), 0)
        so_B_mon = so_B_tin // tin_moi_mon
        bang.append((so_C_mon, so_B_mon, so_B_mon + so_C_mon))

    return max_B_mon, max_C_mon, bang


def format_bang_markdown(nhan, max_B_mon, max_C_mon, bang, tin_moi_mon=TIN_MOI_MON):
    lines = [f"#### 📌 {nhan}"]
    lines.append(f"- Nếu **0 môn C**: tối đa **{max_B_mon} môn B** (≈{max_B_mon * tin_moi_mon} tín)")
    lines.append(f"- Nếu **0 môn B**: tối đa **{max_C_mon} môn C** (≈{max_C_mon * tin_moi_mon} tín)")
    lines.append("")
    lines.append("| Số môn C | Số môn B tối đa | Tổng số môn |")
    lines.append("|:---:|:---:|:---:|")
    for so_C, so_B, tong in bang:
        lines.append(f"| {so_C} | {so_B} | {tong} |")
    lines.append("")
    return "\n".join(lines)


def phan_loai_kha_thi(diem_trung_binh_can, kha_thi):
    """Trả về (nhãn, màu chữ, màu nền) để tô màu mức độ khả thi."""
    if not kha_thi:
        return "🔴 Không khả thi", MAU_DO, MAU_NEN_DO
    if diem_trung_binh_can <= 3.0:
        return "🟢 Dễ đạt được", MAU_XANH, MAU_NEN_XANH
    elif diem_trung_binh_can <= 3.7:
        return "🟠 Cần cố gắng", MAU_CAM, MAU_NEN_CAM
    else:
        return "🔴 Rất khó đạt được", MAU_DO, MAU_NEN_DO


def tao_the_nhan(nhan, mau_chu, mau_nen, mo_ta=""):
    return f"""
    <div style="
        background:{mau_nen};
        border:2px solid {mau_chu};
        border-radius:12px;
        padding:14px 18px;
        text-align:center;
        margin-bottom:8px;">
        <span style="font-size:20px; font-weight:700; color:{mau_chu};">{nhan}</span>
        <div style="color:#555; font-size:13px; margin-top:4px;">{mo_ta}</div>
    </div>
    """


def ve_bieu_do(tin_da_hoc, tin_con_lai, gpa_hien_tai, gpa_muc_tieu):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6))

    # --- Biểu đồ 1: tiến độ tín chỉ (donut) ---
    sizes = [tin_da_hoc, tin_con_lai]
    labels = ["Đã học", "Còn lại"]
    colors = ["#1976d2", "#cfd8dc"]
    wedges, _ = ax1.pie(
        sizes, colors=colors, startangle=90,
        wedgeprops=dict(width=0.38, edgecolor="white")
    )
    phan_tram = tin_da_hoc / TONG_TIN * 100
    ax1.text(0, 0, f"{phan_tram:.0f}%\nhoàn thành", ha="center", va="center",
              fontsize=12, fontweight="bold", color="#1976d2")
    ax1.legend(wedges, [f"{l} ({s} tín)" for l, s in zip(labels, sizes)],
               loc="upper center", bbox_to_anchor=(0.5, -0.02), fontsize=8, frameon=False)
    ax1.set_title("Tiến độ tín chỉ", fontsize=11, fontweight="bold")

    # --- Biểu đồ 2: GPA hiện tại vs mục tiêu ---
    nhan_gpa = ["GPA hiện tại", "GPA mục tiêu"]
    gia_tri = [gpa_hien_tai, gpa_muc_tieu]
    mau_cot = ["#1976d2", "#43a047"]
    bars = ax2.bar(nhan_gpa, gia_tri, color=mau_cot, width=0.5)
    ax2.set_ylim(0, 4.0)
    ax2.set_title("So sánh GPA", fontsize=11, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, gia_tri):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.08, f"{val:.2f}",
                  ha="center", fontsize=10, fontweight="bold")

    fig.tight_layout()
    return fig


# ==== Hàm chính: tính toán và trả về (the_html, bieu_do, thong_tin_md, chi_tiet_md) ====
def tinh_gpa(tin_da_hoc, gpa_hien_tai, gpa_muc_tieu, da_xong_kl):
    tin_da_hoc = int(tin_da_hoc)

    if tin_da_hoc < 0 or tin_da_hoc > TONG_TIN:
        canh_bao = tao_the_nhan("⚠️ Dữ liệu không hợp lệ", MAU_CAM, MAU_NEN_CAM,
                                 f"Số tín đã học phải trong khoảng 0 đến {TONG_TIN}.")
        return canh_bao, None, "", ""
    if not (0.0 <= gpa_hien_tai <= 4.0) or not (0.0 <= gpa_muc_tieu <= 4.0):
        canh_bao = tao_the_nhan("⚠️ Dữ liệu không hợp lệ", MAU_CAM, MAU_NEN_CAM,
                                 "GPA phải nằm trong khoảng 0.0 đến 4.0.")
        return canh_bao, None, "", ""

    tin_con_lai = TONG_TIN - tin_da_hoc
    diem_da_co = gpa_hien_tai * tin_da_hoc
    diem_can_tong = gpa_muc_tieu * TONG_TIN

    bieu_do = ve_bieu_do(tin_da_hoc, tin_con_lai, gpa_hien_tai, gpa_muc_tieu)

    # ---- Thông tin tổng quan ----
    thong_tin = []
    thong_tin.append("### 📊 Thông tin tổng quan")
    thong_tin.append(f"- Tổng số tín chỉ chương trình: **{TONG_TIN}** tín (khóa luận tốt nghiệp {TIN_KHOA_LUAN} tín)")
    thong_tin.append(f"- Số tín đã học: **{tin_da_hoc}** tín ({tin_da_hoc / TONG_TIN * 100:.1f}% chương trình)")
    thong_tin.append(f"- Số tín còn lại: **{tin_con_lai}** tín")
    thong_tin.append(f"- Điểm tích lũy hiện tại (GPA × tín): **{diem_da_co:.2f}**")
    thong_tin.append(f"- Điểm cần đạt tổng cộng để tốt nghiệp GPA {gpa_muc_tieu:.2f}: **{diem_can_tong:.2f}**")
    thong_tin.append(f"- Chênh lệch GPA hiện tại so với mục tiêu: **{gpa_muc_tieu - gpa_hien_tai:+.2f}**")

    ket_qua_md = []

    # ---- Trường hợp đã học hết tín ----
    if tin_con_lai <= 0:
        if gpa_hien_tai >= gpa_muc_tieu:
            nhan_html = tao_the_nhan("🟢 Đã đạt mục tiêu", MAU_XANH, MAU_NEN_XANH,
                                      "Bạn đã hoàn thành đủ tín chỉ và đạt GPA mục tiêu!")
        else:
            nhan_html = tao_the_nhan("🔴 Không thể cải thiện thêm", MAU_DO, MAU_NEN_DO,
                                      "Bạn đã hoàn thành đủ tín chỉ nhưng chưa đạt GPA mục tiêu.")
        return nhan_html, bieu_do, "\n".join(thong_tin), ""

    if da_xong_kl == "Đã có điểm":
        ngan_sach = 4.0 * tin_con_lai - (diem_can_tong - diem_da_co)
        diem_tb_can = (diem_can_tong - diem_da_co) / tin_con_lai
        ket_qua = tinh_max_BC(tin_con_lai, ngan_sach)
        kha_thi = ket_qua is not None
        nhan, mau_chu, mau_nen = phan_loai_kha_thi(diem_tb_can, kha_thi)
        mo_ta = (f"Điểm trung bình cần đạt cho {tin_con_lai} tín còn lại: ~{diem_tb_can:.2f}/4.0"
                  if kha_thi else "Không thể đạt GPA mục tiêu dù toàn bộ tín còn lại đều đạt A.")
        nhan_html = tao_the_nhan(nhan, mau_chu, mau_nen, mo_ta)

        if ket_qua is not None:
            max_B_mon, max_C_mon, bang = ket_qua
            ket_qua_md.append(format_bang_markdown(
                "Kết quả (toàn bộ tín còn lại là môn thường)", max_B_mon, max_C_mon, bang))
    else:
        if tin_con_lai < TIN_KHOA_LUAN:
            nhan_html = tao_the_nhan("⚠️ Kiểm tra lại dữ liệu", MAU_CAM, MAU_NEN_CAM,
                                      f"Số tín còn lại ({tin_con_lai}) nhỏ hơn số tín khóa luận ({TIN_KHOA_LUAN}).")
        else:
            tin_thuong_con_lai = tin_con_lai - TIN_KHOA_LUAN
            thong_tin.append(f"- Trong đó: **{TIN_KHOA_LUAN}** tín khóa luận + **{tin_thuong_con_lai}** tín môn thường")

            ket_qua_theo_grade = {}
            for grade in ['A', 'B', 'C']:
                diem_kl = THANG_DIEM[grade]
                ngan_sach = 4.0 * tin_thuong_con_lai - diem_can_tong + diem_da_co + diem_kl * TIN_KHOA_LUAN
                kq = tinh_max_BC(tin_thuong_con_lai, ngan_sach)
                diem_tb_can = ((diem_can_tong - diem_da_co - diem_kl * TIN_KHOA_LUAN) / tin_thuong_con_lai
                               if tin_thuong_con_lai > 0 else 0)
                ket_qua_theo_grade[grade] = (kq, diem_tb_can)

                if kq is None:
                    ket_qua_md.append(f"#### 📌 Nếu khóa luận đạt {grade}")
                    ket_qua_md.append("🔴 Không thể đạt GPA mục tiêu dù các môn còn lại đều đạt A.")
                    ket_qua_md.append("")
                else:
                    max_B_mon, max_C_mon, bang = kq
                    ket_qua_md.append(format_bang_markdown(
                        f"Nếu khóa luận đạt {grade}", max_B_mon, max_C_mon, bang))

            # Nhãn tổng quan: dựa trên kịch bản khả thi tốt nhất (khóa luận đạt A)
            kq_A, diem_tb_A = ket_qua_theo_grade['A']
            kha_thi_tong = kq_A is not None
            nhan, mau_chu, mau_nen = phan_loai_kha_thi(diem_tb_A, kha_thi_tong)
            if kha_thi_tong:
                mo_ta = f"Trường hợp tốt nhất (khóa luận đạt A): điểm TB cần cho môn thường ~{diem_tb_A:.2f}/4.0"
            else:
                mo_ta = "Ở cả 3 mức điểm khóa luận (A/B/C), mục tiêu GPA vẫn không khả thi."
            nhan_html = tao_the_nhan(nhan, mau_chu, mau_nen, mo_ta)

    return nhan_html, bieu_do, "\n".join(thong_tin), "\n".join(ket_qua_md)


# ================== GIAO DIỆN STREAMLIT ==================
st.set_page_config(page_title="Tính GPA còn lại", page_icon="🎓", layout="wide")

# CSS tối giản để bo góc, tạo khung giống bản Gradio
st.markdown("""
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Công cụ tính GPA cần đạt")
st.markdown(
    "Ứng dụng giúp tính **số môn và số tín tối đa được phép đạt loại A / B / C** "
    "trong số tín còn lại, để bạn đạt được **GPA mục tiêu** khi tốt nghiệp — "
    "kèm biểu đồ trực quan và đánh giá mức độ khả thi.\n\n"
    f"*Chương trình học: {TONG_TIN} tín chỉ (bao gồm khóa luận tốt nghiệp {TIN_KHOA_LUAN} tín, "
    f"môn thường trung bình {TIN_MOI_MON} tín/môn).*"
)

# ---- Giá trị mẫu (tương đương gr.Examples) ----
VI_DU_MAU = {
    "-- Chọn ví dụ mẫu --": None,
    "Ví dụ 1: 100 tín, GPA 3.0 → mục tiêu 3.8": (100, 3.0, 3.8, "Chưa có điểm"),
    "Ví dụ 2: 70 tín, GPA 2.7 → mục tiêu 3.2": (70, 2.7, 3.2, "Chưa có điểm"),
    "Ví dụ 3: 128 tín, GPA 3.55 → mục tiêu 3.6 (đã có điểm KL)": (128, 3.55, 3.6, "Đã có điểm"),
    "Ví dụ 4: 40 tín, GPA 2.3 → mục tiêu 3.0": (40, 2.3, 3.0, "Chưa có điểm"),
}

# Giá trị mặc định lưu trong session_state để nút ví dụ có thể cập nhật
if "tin_da_hoc" not in st.session_state:
    st.session_state.tin_da_hoc = 100
if "gpa_hien_tai" not in st.session_state:
    st.session_state.gpa_hien_tai = 3.0
if "gpa_muc_tieu" not in st.session_state:
    st.session_state.gpa_muc_tieu = 3.8
if "da_xong_kl" not in st.session_state:
    st.session_state.da_xong_kl = "Chưa có điểm"


def ap_dung_vi_du():
    lua_chon = st.session_state.chon_vi_du
    if VI_DU_MAU.get(lua_chon):
        t, g1, g2, kl = VI_DU_MAU[lua_chon]
        st.session_state.tin_da_hoc = t
        st.session_state.gpa_hien_tai = g1
        st.session_state.gpa_muc_tieu = g2
        st.session_state.da_xong_kl = kl


col_trai, col_phai = st.columns([1, 2], gap="large")

with col_trai:
    with st.container(border=True):
        st.markdown("### 📝 Thông tin đầu vào")
        tin_da_hoc = st.number_input(
            "Số tín chỉ đã tích lũy",
            help=f"Tính cả khóa luận nếu đã có điểm (tổng toàn khóa: {TONG_TIN} tín)",
            min_value=0, max_value=TONG_TIN, step=1, key="tin_da_hoc"
        )
        gpa_hien_tai = st.number_input(
            "GPA tích lũy hiện tại (thang 4.0)",
            min_value=0.0, max_value=4.0, step=0.01, format="%.2f", key="gpa_hien_tai"
        )
        gpa_muc_tieu = st.number_input(
            "GPA mục tiêu khi tốt nghiệp (thang 4.0)",
            min_value=0.0, max_value=4.0, step=0.01, format="%.2f", key="gpa_muc_tieu"
        )
        da_xong_kl = st.radio(
            "Đã có điểm khóa luận tốt nghiệp chưa?",
            options=["Đã có điểm", "Chưa có điểm"],
            key="da_xong_kl"
        )
        nut_tinh = st.button("🧮 Tính toán", type="primary", use_container_width=True)

    st.markdown("### 💡 Ví dụ mẫu — chọn để thử nhanh")
    st.selectbox(
        "Chọn một ví dụ mẫu",
        options=list(VI_DU_MAU.keys()),
        key="chon_vi_du",
        on_change=ap_dung_vi_du,
        label_visibility="collapsed",
    )

with col_phai:
    if nut_tinh:
        nhan_html, bieu_do, thong_tin_md, chi_tiet_md = tinh_gpa(
            tin_da_hoc, gpa_hien_tai, gpa_muc_tieu, da_xong_kl
        )
        st.markdown(nhan_html, unsafe_allow_html=True)
        if bieu_do is not None:
            st.pyplot(bieu_do, use_container_width=True)
        if thong_tin_md:
            st.markdown(thong_tin_md)
        if chi_tiet_md:
            st.markdown(chi_tiet_md)
    else:
        st.info("👈 Nhập thông tin và bấm **Tính toán** (hoặc chọn một ví dụ mẫu) để xem kết quả.")

st.markdown("---")
st.markdown(
    "**Chú thích thang điểm:** A = 4.0 · B = 3.0 · C = 2.0 · D = 1.0  \n"
    "**Chú thích mức độ khả thi:** 🟢 Dễ đạt được (điểm TB cần ≤ 3.0) · "
    "🟠 Cần cố gắng (điểm TB cần 3.0–3.7) · 🔴 Rất khó / Không khả thi (> 3.7 hoặc bất khả thi)"
)
