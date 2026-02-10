import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة مؤشرات الحرف", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl=2)

# --- إعدادات الوقت الديناميكية ---
arabic_months = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}
target_date = datetime.today() - timedelta(days=20)
current_month_name = arabic_months[target_date.month]
current_year = target_date.year
dynamic_column_name = f"القيمة الفعلية {current_month_name} {current_year}"

# --- هيكلة عهدة المؤشرات ---
OWNER_INDICATORS = {
    "محمد العثمان": ["نسبة إغلاق الطلبات الواردة في منصة أبدع للتراخيص الحرفية", "عدد الرخص المصدرة لـ رخصة ممارس حرفي", "عدد الرخص المصدرة لـ رخصة محل بيع منتجات حرفية تراثية يدوية", "عدد الحرفيين المسجلين في السجل الوطني للحرفيين"],
    "حنان الصحن": ["عدد الكتب عن الحرف اليدوية", "عدد البحوث عن الحرف اليدوية", "عدد الجوائز المتقدم عليها قطاع الحرف", "عدد الجوائز الحاصل عليها قطاع الحرف", "عدد المشاركات البحثية من قبل القطاع"],
    "الهنوف اللعبون": ["عدد البيوت الحرفية النشطة", "عدد القطع الحرفية المنتجة من أعمال البيوت الحرفية", "عدد القطع الحرفية المنتجة من أعمال ومشاريع القطاع (دون البيوت الحرفية)", "عدد التصاميم الصادرة من مشاريع البيوت الحرفية", "عدد التصاميم الصادرة من كافة مشاريع قطاع الحرف (دون البيوت الحرفية)"],
    "ديما الحمودي": ["عدد الدورات التدريبية وورش العمل للبيوت الحرفية فقط", "عدد المستفيدين الحاليين من الدورات التدريبية المقدمة للبيوت الحرفية فقط (لا يستثني التكرار)", "عدد المتدربين خلال بداية مرحلة تدريبية للبيوت القائمة (مرة واحدة فقط ببداية المرحلة التدريبية)", "عدد الخريجين من الدورات التدريبية المقدمة من البيوت الحرفية فقط (مرتبط بالشهادة)", "عدد الدورات التدريبية وورش العمل لكافة المشاريع دون البيوت الحرفية", "عدد المستفيدين من الدورات التدريبية المقدمة لكافة المشاريع دون البيوت الحرفية", "عدد الدورات التدريبية وورش العمل للأطفال", "عدد المستفيدين من الدورات التدريبية وورش العمل المقدمة للأطفال"],
    "ريف الحميد": ["عدد المعارض والفعاليات الدولية", "عدد الحرفيين المشاركين في المعارض والمهرجانات الدولية"],
    "مها الغانمي": ["عدد المعارض والفعاليات المحلية", "عدد الحرفيين المشاركين في المعارض والمهرجانات المحلية"],
    "صالح بن دريهم": ["عدد الحرفيين المدعومين لوجستياً"],
    "عبدالله الربيّع": ["عدد القطاعات الغير ربحية المستفيدة من اعمال ومشاريع ادارة الحرف"],
    "منال الراجحي": ["عدد الحرفيين المستفيدين من الدعم المالي المقدم من قبل قطاع الحرف", "قيمة الدعم المالي المقدم للحرفيين المستفيدين", "عدد الحرفيين المستفيدين من الدعم المالي المقدم في الفعاليات والمشاركات من قبل قطاع الحرف", "قيمة الدعم المالي المقدم للحرفيين المستفيدين من خلال الفعاليات والمشاركات", "عدد الكيانات والمنشآت المستفيدة من الدعم المالي المقدم من قبل قطاع الحرف", "قيمة الدعم المالي المقدم للكيانات والمنشآت المستفيدة"]
}

OWNERS = list(OWNER_INDICATORS.keys())
ALL_IND_LIST = [ind for sublist in OWNER_INDICATORS.values() for ind in sublist]
FOLLOW_UP_MAPPING = {ind: ("تراكمي" if "تراكمي" in ind or "عدد الرخص" in ind else "شهري") for ind in ALL_IND_LIST}

# --- نظام الحماية ---
def check_password():
    if "user_role" not in st.session_state: st.session_state["user_role"] = None
    def password_entered():
        pwd = st.session_state["password"]
        if pwd == "1111": st.session_state["user_role"], st.session_state["password_correct"] = "user", True
        elif pwd == "2222": st.session_state["user_role"], st.session_state["password_correct"] = "admin", True
        else: st.session_state["password_correct"] = False
        if "password" in st.session_state: del st.session_state["password"]
    if not st.session_state.get("password_correct"):
        st.text_input("أدخل الرمز السري للدخول", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password(): st.stop()

# --- التصميم الجديد (توزيع الأعمدة) ---
role = st.session_state["user_role"]
if role == "admin": tab1, tab2 = st.tabs(["➕ إضافة بيانات", "📝 عرض وتعديل وإدارة"])
else: tab1, tab2 = st.container(), None

with tab1:
    st.title("📊 نظام إدارة مؤشرات قطاع الحرف")
    st.subheader(f"📅 إدخال بيانات شهر: {current_month_name} {current_year}")
    
    # 1. المداخل الأساسية فوق التقسيم
    selected_owner = st.selectbox("اختر اسمك (مالك المؤشر)", OWNERS)
    available_indicators = OWNER_INDICATORS[selected_owner]
    ind_name = st.selectbox("اسم المؤشر المسؤول عنه", available_indicators)
    
    f_method = FOLLOW_UP_MAPPING.get(ind_name, "شهري")
    st.info(f"طريقة المتابعة: **{f_method}** | الفترة: **{current_month_name}**")
    
    st.divider()

    # 2. تقسيم الصفحة إلى قسمين (الهامش 1 : الأساس 3)
    col_main, col_sidebar = st.columns([3, 2])

    with col_main:
        st.markdown("### 📝 نموذج الإدخال")
        # حساب خط الأساس
        current_data = get_data()
        mask = (current_data['اسم المؤشر'] == ind_name) & (current_data['مالك المؤشر'] == selected_owner)
        if mask.any():
            original_base = current_data.loc[mask, 'خط الأساس 2024'].iloc[0]
            actual_columns = [col for col in current_data.columns if "القيمة الفعلية" in col]
            previous_actuals_sum = current_data.loc[mask, actual_columns].sum(axis=1).iloc[0]
            calculated_base = original_base + previous_actuals_sum
        else: calculated_base = 0.0

        with st.form("add_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.number_input("📈 خط الأساس التراكمي", value=float(calculated_base), disabled=True)
                act_val = st.number_input(f"🔢 {dynamic_column_name}", value=0.0)
            with f_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("📂 افتح Google Drive للرفع", "https://drive.google.com/", use_container_width=True)
                docs_input = st.text_input("🔗 رابط الوثيقة الداعمة", placeholder="ألصق الرابط هنا...")
            
            if st.form_submit_button("حفظ البيانات في السحابة ✅", use_container_width=True):
                with st.spinner('جاري الحفظ...'):
                    new_data = {"اسم المؤشر": ind_name, "مالك المؤشر": selected_owner, "خط الأساس 2024": calculated_base if not mask.any() else original_base, "الوثائق الداعمة": docs_input, "طريقة المتابعة": f_method, dynamic_column_name: act_val}
                    if mask.any(): current_data.loc[mask, dynamic_column_name] = act_val
                    else: current_data = pd.concat([current_data, pd.DataFrame([new_data])], ignore_index=True)
                    conn.update(data=current_data)
                    st.cache_data.clear()
                st.success("تم الحفظ!")
                st.rerun()

    with col_sidebar:
        st.markdown(f"### 🔔 التنبيهات")
        # منطق حالة الإكمال
        if dynamic_column_name in current_data.columns:
            done_list = current_data[(current_data['مالك المؤشر'] == selected_owner) & (current_data[dynamic_column_name].notna())]['اسم المؤشر'].tolist()
        else: done_list = []
        
        required_indicators = OWNER_INDICATORS[selected_owner]
        comp_count = len(done_list)
        req_count = len(required_indicators)

        if comp_count == 0: st.warning(f"⚠️ يا {selected_owner.split()[0]}، لم تدخل بيانات. مطلوب {req_count} مؤشرات.")
        elif comp_count < req_count: st.info(f"⚡ أكملت {comp_count} من {req_count}")
        else: st.success(f"✅ كفيت ووفيت!")

        st.markdown("---")
        # عرض قائمة المؤشرات مع صح أو خطأ (بدون كولابس) كما طلبت في الرسمة
        for ind in required_indicators:
            if ind in done_list: st.write(f"{ind} ✅-")
            else: st.write(f"{ind} ❌-")

    st.divider()
    st.subheader("📋 ملخص البيانات التاريخية")
    st.dataframe(get_data(), use_container_width=True)

if role == "admin" and tab2:
    with tab2:
        st.subheader("⚙️ الإدارة")
        data_to_edit = get_data()
        edited_df = st.data_editor(data_to_edit, num_rows="dynamic", use_container_width=True)
        if st.button("💾 حفظ"):
            conn.update(data=edited_df)
            st.cache_data.clear()
            st.rerun()