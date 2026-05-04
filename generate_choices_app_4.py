import streamlit as st
import random
import sympy as sp

st.set_page_config(page_title="微分トレーニング（4択・5題セット）", layout="centered")
x = sp.Symbol("x")

# ============================================================
# 既約分数に統一する関数
# ============================================================
def simplify_fraction(expr):
    expr = sp.simplify(expr)
    num, den = sp.fraction(expr)

    num_c = num.as_coeff_Mul()[0]
    den_c = den.as_coeff_Mul()[0]

    frac = sp.Rational(num_c, den_c)

    num_rest = num / num_c
    den_rest = den / den_c

    return sp.simplify(frac * num_rest / den_rest)

# ============================================================
# 高校教科書形式の指数・対数の導関数
# ============================================================
def format_exp_derivative(base, u, du):
    if base == sp.E:
        return simplify_fraction(sp.exp(u) * du)
    else:
        return simplify_fraction(base**u * sp.log(base) * du)

def format_log_derivative(base, u, du):
    if base == sp.E:
        return simplify_fraction(du / u)
    else:
        return simplify_fraction(du / (u * sp.log(base)))

# ============================================================
# 4択生成
# ============================================================
def generate_choices(fp):
    correct = simplify_fraction(fp)
    wrongs = []

    candidates = [
        correct * 2,
        correct / 2,
        -correct,
        correct + 1,
        correct - 1,
    ]

    for w in candidates:
        w_s = simplify_fraction(w)
        if sp.simplify(w_s - correct) != 0 and all(sp.simplify(w_s - ww) != 0 for ww in wrongs):
            wrongs.append(w_s)
        if len(wrongs) == 3:
            break

    k = 2
    while len(wrongs) < 3:
        extra = simplify_fraction(correct + k)
        if sp.simplify(extra - correct) != 0:
            wrongs.append(extra)
        k += 1

    options = [correct] + wrongs
    random.shuffle(options)
    return options, options.index(correct)

# ============================================================
# 多項式
# ============================================================
def gen_poly_linear():
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.randint(-5, 5)
    f = a*x + b
    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, "poly_linear"

def gen_poly_quadratic():
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    f = a*x**2 + b*x + c
    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, "poly_quad"

def gen_poly_cubic_plain():
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    d = random.randint(-5, 5)
    f = a*x**3 + b*x**2 + c*x + d
    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, "poly_cubic_plain"

def gen_poly_cubic_bracket():
    a = random.choice([i for i in range(-3, 4) if i != 0])
    b = random.choice([i for i in range(-3, 4) if i != 0])
    c = random.randint(-5, 5)
    p = random.randint(-3, 3)
    q = random.randint(-3, 3)
    f = a*(x - p)**3 + b*(x - q)**2 + c
    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, "poly_cubic_bracket"

# ============================================================
# 三角関数
# ============================================================
def gen_trig(kind, fixed1=False):
    a = 1 if fixed1 else random.choice([2, 3, 4])
    b = random.randint(-2, 2)
    u = a*x + b

    if kind == "sin":
        f = sp.sin(u)
        fp = sp.diff(f, x)
    elif kind == "cos":
        f = sp.cos(u)
        fp = sp.diff(f, x)
    else:
        f = sp.tan(u)
        fp = sp.diff(f, x)
        fp = fp.rewrite(sp.cos)
        fp = sp.simplify(fp)

    fp = simplify_fraction(fp)
    return f, fp, f"{kind}_ax+b"

# ============================================================
# 指数（高校教科書準拠）
# ============================================================
def gen_exp_correct():
    base_choice = random.choice(["e", "e", "2or5"])

    a = random.choice([1, 2, 3, 4])
    b = random.randint(-2, 2)
    u = a*x + b

    if base_choice == "e":
        f = sp.exp(u)
        fp = format_exp_derivative(sp.E, u, a)
        skey = "exp_e"
    else:
        base = random.choice([2, 5])
        f = base**u
        fp = format_exp_derivative(base, u, a)
        skey = f"exp_{base}"

    return f, fp, skey

# ============================================================
# 対数（高校教科書準拠）
# ============================================================
def gen_log_correct():
    base_choice = random.choice(["ln", "2or3", "a"])

    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a*x + b

    if base_choice == "ln":
        f = sp.log(u)
        fp = format_log_derivative(sp.E, u, a)
        skey = "log"

    elif base_choice == "2or3":
        base = random.choice([2, 3])
        f = sp.log(u, base)
        fp = format_log_derivative(base, u, a)
        skey = f"log_{base}"

    else:
        base = random.randint(2, 5)
        f = sp.log(u, base)
        fp = format_log_derivative(base, u, a)
        skey = "log_a"

    return f, fp, skey

# ============================================================
# 類似チェックつき問題追加
# ============================================================
def add_problem(gen_func, problems, seen_exact, seen_struct, *args):
    last = None
    for _ in range(10):
        f, fp, skey = gen_func(*args)
        ekey = sp.srepr(f)
        if ekey not in seen_exact and skey not in seen_struct:
            seen_exact.add(ekey)
            seen_struct.add(skey)
            opts, idx = generate_choices(fp)
            problems.append({"f": f, "fp": fp, "opts": opts, "idx": idx})
            return
        last = (f, fp, skey)

    f, fp, skey = last
    ekey = sp.srepr(f)
    seen_exact.add(ekey)
    seen_struct.add(skey)
    opts, idx = generate_choices(fp)
    problems.append({"f": f, "fp": fp, "opts": opts, "idx": idx})

# ============================================================
# 5題セット生成
# ============================================================
def build_set(mode):
    problems = []
    seen_exact = set()
    seen_struct = set()

    if mode == "多項式":
        add_problem(gen_poly_linear, problems, seen_exact, seen_struct)
        add_problem(gen_poly_quadratic, problems, seen_exact, seen_struct)
        add_problem(gen_poly_quadratic, problems, seen_exact, seen_struct)
        add_problem(gen_poly_cubic_plain, problems, seen_exact, seen_struct)
        add_problem(gen_poly_cubic_bracket, problems, seen_exact, seen_struct)

    elif mode == "三角関数":
        add_problem(lambda: gen_trig("sin", True), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_trig("cos", True), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_trig("tan", False), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_trig("sin", False), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_trig("cos", False), problems, seen_exact, seen_struct)

    elif mode == "指数・対数":
        add_problem(gen_exp_correct, problems, seen_exact, seen_struct)
        add_problem(gen_exp_correct, problems, seen_exact, seen_struct)
        add_problem(gen_exp_correct, problems, seen_exact, seen_struct)
        add_problem(gen_log_correct, problems, seen_exact, seen_struct)
        add_problem(gen_log_correct, problems, seen_exact, seen_struct)

    return problems

# ============================================================
# セッション管理
# ============================================================
if "mode" not in st.session_state:
    st.session_state.mode = "多項式"
if "problems" not in st.session_state:
    st.session_state.problems = []
if "selects" not in st.session_state:
    st.session_state.selects = [None] * 5
if "checked" not in st.session_state:
    st.session_state.checked = False
if "set_id" not in st.session_state:
    st.session_state.set_id = 0

# ============================================================
# UI
# ============================================================
st.title("微分トレーニング（4択・5題セット）")

mode = st.selectbox("問題の種類を選んでください", ["多項式", "三角関数", "指数・対数"])
st.session_state.mode = mode

if st.button("5題を生成する"):
    st.session_state.problems = build_set(mode)
    st.session_state.selects = [None] * 5
    st.session_state.checked = False
    st.session_state.set_id += 1

probs = st.session_state.problems

if probs:
    st.markdown("### 問題に答えてください（正しい導関数を選択）")

    for i, p in enumerate(probs):
        st.markdown(f"#### 【問題 {i+1}】")
        st.latex(rf"f(x) = {sp.latex(p['f'])}")

        labels = [f"$f'(x) = {sp.latex(opt)}$" for opt in p["opts"]]

        choice = st.radio(
            f"選択肢（問題 {i+1}）",
            options=list(range(4)),
            format_func=lambda j, labels=labels: labels[j],
            index=None,
            key=f"choice_{st.session_state.set_id}_{i}",
        )
        st.session_state.selects[i] = choice

    if st.button("採点する"):
        st.session_state.checked = True

    if st.session_state.checked:
        st.markdown("## 採点結果")

        correct_now = 0
        for i, p in enumerate(probs):
            user = st.session_state.selects[i]
            st.markdown(f"### 【問題 {i+1}】")
            if user == p["idx"]:
                st.success("正解")
                correct_now += 1
            else:
                st.error("不正解")
            st.latex(rf"正しい答え：\ f'(x) = {sp.latex(p['fp'])}")

        st.markdown(f"## このセットの正答数：{correct_now} / 5")

        if st.button("次の問題セットへ"):
            st.session_state.problems = build_set(mode)
            st.session_state.selects = [None] * 5
            st.session_state.checked = False
            st.session_state.set_id += 1

else:
    st.info("「5題を生成する」を押してください。")
