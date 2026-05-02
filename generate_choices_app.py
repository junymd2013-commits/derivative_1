import streamlit as st
import random
import sympy as sp

st.set_page_config(page_title="微分トレーニングアプリ（4択・5題セット）", layout="centered")
x = sp.Symbol("x")

# -----------------------------
# 4択生成
# -----------------------------
def generate_choices(fp):
    correct = sp.simplify(fp)
    wrongs = []
    candidates = [correct * 2, correct / 2, -correct]

    for w in candidates:
        w_s = sp.simplify(w)
        if sp.simplify(w_s - correct) != 0 and all(sp.simplify(w_s - ww) != 0 for ww in wrongs):
            wrongs.append(w_s)
        if len(wrongs) == 3:
            break

    while len(wrongs) < 3:
        extra = sp.simplify(correct + (len(wrongs) + 1))
        if sp.simplify(extra - correct) != 0 and all(sp.simplify(extra - ww) != 0 for ww in wrongs):
            wrongs.append(extra)

    options = [correct] + wrongs
    random.shuffle(options)
    correct_index = options.index(correct)
    return options, correct_index

# -----------------------------
# 問題生成（多項式）
# -----------------------------
def gen_poly_bracket():
    a = random.choice([i for i in range(-3, 4) if i not in [0]])
    b = random.choice([i for i in range(-3, 4) if i not in [0]])
    c = random.randint(-5, 5)
    p = random.randint(-3, 3)
    q = random.randint(-3, 3)
    f = a * (x - p) ** 3 + b * (x - q) ** 2 + c
    fp = sp.diff(f, x)
    structure = "poly_bracket"
    return f, fp, structure

def gen_poly_plain():
    a = random.choice([i for i in range(-3, 4) if i not in [0]])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    d = random.randint(-5, 5)
    f = a * x**3 + b * x**2 + c * x + d
    fp = sp.diff(f, x)
    structure = "poly_plain"
    return f, fp, structure

# -----------------------------
# 問題生成（指数）
# -----------------------------
def gen_exp(fixed_coeff1=False):
    base_type = random.choice(["e", "2", "10", "a"])
    if fixed_coeff1:
        a = 1
    else:
        a = random.choice([2, 3, 4])
    b = random.randint(-2, 2)

    if base_type == "e":
        f = sp.exp(a * x + b)
        structure = "exp_e_ax+b"
    elif base_type == "2":
        f = 2 ** (a * x + b)
        structure = "exp_2_ax+b"
    elif base_type == "10":
        f = 10 ** (a * x + b)
        structure = "exp_10_ax+b"
    else:
        base = random.randint(2, 5)
        f = base ** (a * x + b)
        structure = "exp_a_ax+b"

    fp = sp.diff(f, x)
    return f, fp, structure

# -----------------------------
# 問題生成（対数）
# -----------------------------
def gen_log():
    base_type = random.choice(["ln", "2", "10", "a"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a * x + b

    if base_type == "ln":
        f = sp.log(u)
        structure = "log_ln_ax+b"
    elif base_type == "2":
        f = sp.log(u, 2)
        structure = "log_2_ax+b"
    elif base_type == "10":
        f = sp.log(u, 10)
        structure = "log_10_ax+b"
    else:
        base = random.randint(2, 5)
        f = sp.log(u, base)
        structure = "log_a_ax+b"

    fp = sp.diff(f, x)
    return f, fp, structure

# -----------------------------
# 問題生成（三角）
# -----------------------------
def gen_trig(fixed_coeff1=False):
    kind = random.choice(["sin", "cos", "tan"])
    if fixed_coeff1:
        a = 1
    else:
        a = random.choice([2, 3, 4])
    b = random.randint(-2, 2)
    u = a * x + b

    if kind == "sin":
        f = sp.sin(u)
        structure = "sin_ax+b"
    elif kind == "cos":
        f = sp.cos(u)
        structure = "cos_ax+b"
    else:
        f = sp.tan(u)
        structure = "tan_ax+b"

    fp = sp.diff(f, x)
    return f, fp, structure

# -----------------------------
# 5題セット生成
# -----------------------------
def build_problem_set(mode):
    problems = []
    seen_exact = set()
    seen_struct = set()

    def add_problem(gen_func, *args, force=False):
        nonlocal problems, seen_exact, seen_struct
        last_f = last_fp = last_struct = None
        for attempt in range(10):
            f, fp, struct = gen_func(*args)
            key_exact = sp.srepr(f)
            if key_exact not in seen_exact and struct not in seen_struct:
                seen_exact.add(key_exact)
                seen_struct.add(struct)
                options, correct_idx = generate_choices(fp)
                problems.append(
                    {
                        "f": f,
                        "fp": fp,
                        "options": options,
                        "correct_idx": correct_idx,
                    }
                )
                return
            last_f, last_fp, last_struct = f, fp, struct
        # 10回失敗したら類似でも採用
        if last_f is not None:
            key_exact = sp.srepr(last_f)
            seen_exact.add(key_exact)
            seen_struct.add(last_struct)
            options, correct_idx = generate_choices(last_fp)
            problems.append(
                {
                    "f": last_f,
                    "fp": last_fp,
                    "options": options,
                    "correct_idx": correct_idx,
                }
            )

    if mode == "多項式":
        add_problem(gen_poly_bracket)  # かっこ付き1題
        for _ in range(4):
            add_problem(gen_poly_plain)

    elif mode == "指数関数":
        add_problem(gen_exp, True)  # 係数1の問題1題
        for _ in range(4):
            add_problem(gen_exp, False)

    elif mode == "三角関数":
        add_problem(gen_trig, True)  # 係数1の問題1題
        for _ in range(4):
            add_problem(gen_trig, False)

    elif mode == "対数関数":
        for _ in range(5):
            add_problem(gen_log)

    return problems

# -----------------------------
# セッション初期化
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "多項式"
if "problems" not in st.session_state:
    st.session_state.problems = []
if "selections" not in st.session_state:
    st.session_state.selections = [None] * 5
if "checked" not in st.session_state:
    st.session_state.checked = False
if "set_id" not in st.session_state:
    st.session_state.set_id = 0
if "correct_total" not in st.session_state:
    st.session_state.correct_total = 0
if "question_total" not in st.session_state:
    st.session_state.question_total = 0

# -----------------------------
# UI：上部
# -----------------------------
st.title("微分トレーニングアプリ（4択・5題セット）")

st.markdown("### 1. 関数の種類を選んでください")
mode = st.selectbox(
    "関数の種類",
    ["多項式", "指数関数", "対数関数", "三角関数"],
    key="mode_select",
)
st.session_state.mode = mode

col_gen1, _ = st.columns([2, 1])
with col_gen1:
    if st.button("5題を生成する", use_container_width=True):
        st.session_state.problems = build_problem_set(mode)
        st.session_state.selections = [None] * 5
        st.session_state.checked = False
        st.session_state.set_id += 1

# -----------------------------
# 問題表示
# -----------------------------
if st.session_state.problems:
    st.markdown("### 2. 問題に答えましょう（正しい f'(x) を選ぶ）")

    for i, prob in enumerate(st.session_state.problems):
        f = prob["f"]
        options = prob["options"]

        st.markdown(
            f"<span style='color:#1E88E5; font-size:18px; font-weight:bold;'>【問題 {i+1}】</span>",
            unsafe_allow_html=True,
        )
        st.latex(rf"f(x) = {sp.latex(f)}")

        labels = [f"選択肢 {j+1}: $f'(x) = {sp.latex(opt)}$" for j, opt in enumerate(options)]
        default_idx = st.session_state.selections[i] if st.session_state.selections[i] is not None else 0

        choice = st.radio(
            f"f'(x) の正しい式を選んでください（問題 {i+1}）",
            options=list(range(4)),
            format_func=lambda j, labels=labels: labels[j],
            index=default_idx,
            key=f"choice_{st.session_state.set_id}_{i}",
        )
        st.session_state.selections[i] = choice
        st.markdown("<hr style='border:0.5px solid #ddd;'>", unsafe_allow_html=True)

    col_check1, col_check2 = st.columns(2)
    with col_check1:
        if st.button("採点する", use_container_width=True):
            st.session_state.checked = True
    with col_check2:
        if st.button("次の5題に進む", use_container_width=True):
            st.session_state.problems = build_problem_set(mode)
            st.session_state.selections = [None] * 5
            st.session_state.checked = False
            st.session_state.set_id += 1

    # -----------------------------
    # 採点・解説
    # -----------------------------
    if st.session_state.checked:
        st.markdown("### 3. 採点結果・解説")

        correct_now = 0
        for i, prob in enumerate(st.session_state.problems):
            f = prob["f"]
            fp = prob["fp"]
            correct_idx = prob["correct_idx"]
            user_idx = st.session_state.selections[i]

            st.markdown(
                f"<span style='font-weight:bold;'>【問題 {i+1}】</span>",
                unsafe_allow_html=True,
            )
            if user_idx == correct_idx:
                st.success("正解！")
                correct_now += 1
            else:
                st.error("不正解")
            st.markdown(
                f"**正しい答え：**  \n"
                f"\\( f'(x) = {sp.latex(fp)} \\)"
            )
            st.markdown("<hr style='border:0.5px solid #eee;'>", unsafe_allow_html=True)

        st.session_state.correct_total += correct_now
        st.session_state.question_total += len(st.session_state.problems)

        st.markdown(f"### このセットの正答数：{correct_now} / {len(st.session_state.problems)}")
        if st.session_state.question_total > 0:
            acc = st.session_state.correct_total / st.session_state.question_total * 100
            st.markdown(f"**累計正答率：{acc:.1f}%**")

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
                st.session_state.problems = build_problem_set(mode)
                st.session_state.selections = [None] * 5
                st.session_state.checked = False
                st.session_state.set_id += 1
        with col_end:
            if st.button("終了する", use_container_width=True):
                st.markdown("学習お疲れさまでした。")
                st.stop()
else:
    st.info("「5題を生成する」ボタンを押して問題セットを作成してください。")
