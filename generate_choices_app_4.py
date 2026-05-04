import streamlit as st
import random
import sympy as sp

st.set_page_config(page_title="微分トレーニング（4択・5題セット）", layout="centered")
x = sp.Symbol("x")

# ============================================================
# 既約分数に統一する関数（重要）
# ============================================================
def simplify_fraction(expr):
    expr = sp.simplify(expr)
    num, den = sp.fraction(expr)

    # 係数部分を抽出
    num_c = num.as_coeff_Mul()[0]
    den_c = den.as_coeff_Mul()[0]

    # 係数だけ既約分数に
    frac = sp.Rational(num_c, den_c)

    # 残りの部分（x を含む部分）
    num_rest = num / num_c
    den_rest = den / den_c

    # 再構成して簡単化
    return sp.simplify(frac * num_rest / den_rest)

# ============================================================
# 4択生成（軽量）
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
# 多項式（1次・2次・3次）
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
# 三角関数（tan は必ず cos で表示）
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
# 指数・対数（log を自然対数として扱う）
# ============================================================
def gen_exp(fixed1=False):
    base = random.choice(["e", "2", "10", "a"])
    a = 1 if fixed1 else random.choice([2, 3, 4])
    b = random.randint(-2, 2)

    if base == "e":
        f = sp.exp(a*x + b)
        skey = "exp_e"
    elif base == "2":
        f = 2**(a*x + b)
        skey = "exp_2"
    elif base == "10":
        f = 10**(a*x + b)
        skey = "exp_10"
    else:
        basev = random.randint(2, 5)
        f = basev**(a*x + b)
        skey = "exp_a"

    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, skey

def gen_log():
    base = random.choice(["ln", "2", "10", "a"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a*x + b

    if base == "ln":
        f = sp.log(u)
        skey = "log"
    elif base == "2":
        f = sp.log(u, 2)
        skey = "log_2"
    elif base == "10":
        f = sp.log(u, 10)
        skey = "log_10"
    else:
        basev = random.randint(2, 5)
        f = sp.log(u, basev)
        skey = "log_a"

    fp = simplify_fraction(sp.diff(f, x))
    return f, fp, skey

# ============================================================
# 類似チェックつき問題追加（最大10回）
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
        add_problem(lambda: gen_exp(True), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_exp(False), problems, seen_exact, seen_struct)
        for _ in range(3):
            add_problem(gen_log, problems, seen_exact, seen_struct)

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
