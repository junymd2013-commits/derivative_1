import streamlit as st
import random
import sympy as sp

st.set_page_config(page_title="微分トレーニングアプリ", layout="centered")

x = sp.Symbol("x")

# -----------------------------
# 問題生成
# -----------------------------
def generate_polynomial():
    # 三次まで・かっこ付き
    a = random.randint(-3, 3) or 1
    b = random.randint(-3, 3)
    c = random.randint(-3, 3)
    p = random.randint(-3, 3)
    q = random.randint(-3, 3)
    f = a * (x - p) ** 3 + b * (x - q) ** 2 + c
    return sp.simplify(f), sp.diff(f, x)

def generate_exponential():
    base_type = random.choice(["e", "2", "10", "a"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    if base_type == "e":
        f = sp.exp(a * x + b)
    elif base_type == "2":
        f = 2 ** (a * x + b)
    elif base_type == "10":
        f = 10 ** (a * x + b)
    else:
        base = random.randint(2, 5)
        f = base ** (a * x + b)
    return sp.simplify(f), sp.diff(f, x)

def generate_log():
    base_type = random.choice(["ln", "2", "10", "a"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a * x + b
    if base_type == "ln":
        f = sp.log(u)
    elif base_type == "2":
        f = sp.log(u, 2)
    elif base_type == "10":
        f = sp.log(u, 10)
    else:
        base = random.randint(2, 5)
        f = sp.log(u, base)
    return sp.simplify(f), sp.diff(f, x)

def generate_trig():
    kind = random.choice(["sin", "cos", "tan"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a * x + b
    if kind == "sin":
        f = sp.sin(u)
    elif kind == "cos":
        f = sp.cos(u)
    else:
        f = sp.tan(u)
    return sp.simplify(f), sp.diff(f, x)

def generate_problem_set(mode, n=5):
    problems = []
    seen = set()
    while len(problems) < n:
        if mode == "多項式":
            f, fp = generate_polynomial()
        elif mode == "指数関数":
            f, fp = generate_exponential()
        elif mode == "対数関数":
            f, fp = generate_log()
        else:
            f, fp = generate_trig()
        key = sp.srepr(f)
        if key in seen:
            continue
        seen.add(key)
        problems.append((f, fp))
    return problems

# -----------------------------
# 初期化
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "多項式"
if "problems" not in st.session_state:
    st.session_state.problems = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "checked" not in st.session_state:
    st.session_state.checked = False
if "set_id" not in st.session_state:
    st.session_state.set_id = 0
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "total_count" not in st.session_state:
    st.session_state.total_count = 0

# -----------------------------
# UI：上部ゾーン
# -----------------------------
st.title("微分トレーニングアプリ（5題セット）")

st.markdown("### 1. 関数の種類を選んでください")

mode = st.selectbox(
    "関数の種類",
    ["多項式", "指数関数", "対数関数", "三角関数"],
    key="mode_select",
)

col_gen1, col_gen2 = st.columns([2, 1])
with col_gen1:
    if st.button("5題を生成する", use_container_width=True):
        st.session_state.problems = generate_problem_set(mode, n=5)
        st.session_state.answers = ["" for _ in range(5)]
        st.session_state.checked = False
        st.session_state.set_id += 1
with col_gen2:
    st.write("　")  # 余白

# -----------------------------
# 問題表示ゾーン
# -----------------------------
if st.session_state.problems:
    st.markdown("### 2. 問題に答えましょう（f'(x) を求める）")

    with st.expander("答え方の例（クリックで開く）"):
        st.markdown(
            """
- `3x^2 - 4x + 1`
- `2*e^(3x+1)`
- `2^(x-1)*ln(2)`
- `10^(2x)*2*ln(10)`
- `3/(3x+1)`
- `2x/((x^2+1)*ln(2))`
- `cos(2x+1)*2`
- `-4*sin(3x)*3`
- `2*sec(x-1)^2`
"""
        )

    for i, (f, fp) in enumerate(st.session_state.problems):
        st.markdown(
            f"<span style='color:#1E88E5; font-size:18px; font-weight:bold;'>【問題 {i+1}】</span>",
            unsafe_allow_html=True,
        )
        st.latex(rf"f(x) = {sp.latex(f)}")
        st.session_state.answers[i] = st.text_input(
            f"f'(x) の式を入力してください（問題 {i+1}）",
            value=st.session_state.answers[i],
            key=f"ans_{st.session_state.set_id}_{i}",
            placeholder="例：3x^2 - 4x + 1, 2*e^(3x+1) など",
        )
        st.markdown("<hr style='border:0.5px solid #ddd;'>", unsafe_allow_html=True)

    # -----------------------------
    # 採点・結果ゾーン
    # -----------------------------
    col_check1, col_check2 = st.columns([1, 1])
    with col_check1:
        if st.button("採点する", use_container_width=True):
            st.session_state.checked = True
    with col_check2:
        if st.button("次の5題に進む", use_container_width=True):
            st.session_state.problems = generate_problem_set(mode, n=5)
            st.session_state.answers = ["" for _ in range(5)]
            st.session_state.checked = False
            st.session_state.set_id += 1

    if st.session_state.checked:
        st.markdown("### 3. 採点結果・解説")

        correct = 0
        for i, (f, fp) in enumerate(st.session_state.problems):
            user_str = st.session_state.answers[i]
            st.markdown(
                f"<span style='font-weight:bold;'>【問題 {i+1}】</span>",
                unsafe_allow_html=True,
            )
            try:
                user_expr = sp.simplify(user_str)
                if sp.simplify(user_expr - fp) == 0:
                    st.success("正解！")
                    correct += 1
                else:
                    st.error("不正解")
                    st.markdown(
                        f"**正しい答え：**  \n"
                        f"\\( f'(x) = {sp.latex(fp)} \\)"
                    )
            except Exception:
                st.error("式が正しく読み取れませんでした。")
                st.markdown(
                    f"**正しい答え：**  \n"
                    f"\\( f'(x) = {sp.latex(fp)} \\)"
                )
            st.markdown("<hr style='border:0.5px solid #eee;'>", unsafe_allow_html=True)

        st.session_state.correct_count += correct
        st.session_state.total_count += len(st.session_state.problems)

        st.markdown(
            f"### 正答数：{correct} / {len(st.session_state.problems)}  "
        )
        if st.session_state.total_count > 0:
            acc = st.session_state.correct_count / st.session_state.total_count * 100
            st.markdown(f"**累計正答率：{acc:.1f}%**")

        # 数学III 微分公式（参考）
        with st.expander("数学Ⅲ 微分公式（参考）"):
            st.latex(r"\frac{d}{dx}(x^n)=nx^{n-1}")
            st.latex(r"\frac{d}{dx}(e^{u})=e^{u}u'")
            st.latex(r"\frac{d}{dx}(a^{u})=a^{u}\ln(a)u'")
            st.latex(r"\frac{d}{dx}(\ln u)=\frac{u'}{u}")
            st.latex(r"\frac{d}{dx}(\log_a u)=\frac{u'}{u\ln a}")
            st.latex(r"\frac{d}{dx}(\sin u)=\cos u\,u'")
            st.latex(r"\frac{d}{dx}(\cos u)=-\sin u\,u'")
            st.latex(r"\frac{d}{dx}(\tan u)=\sec^2 u\,u'")
            st.latex(r"\frac{d}{dx}(f(g(x)))=f'(g(x))g'(x)")

        col_retry, col_end = st.columns(2)
        with col_retry:
            if st.button("同じ種類でもう一度挑戦する", use_container_width=True):
                st.session_state.problems = generate_problem_set(mode, n=5)
                st.session_state.answers = ["" for _ in range(5)]
                st.session_state.checked = False
                st.session_state.set_id += 1
        with col_end:
            if st.button("終了する", use_container_width=True):
                st.markdown("学習お疲れさまでした。")
                st.stop()
else:
    st.info("「5題を生成する」ボタンを押して問題セットを作成してください。")
