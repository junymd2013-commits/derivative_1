import streamlit as st
import random
import sympy as sp

st.set_page_config(page_title="微分トレーニング（4択・難易度順）", layout="centered")
x = sp.Symbol("x")

# ============================================================
# 4択生成（教科書風の式）
# ============================================================
def generate_choices(fp):
    correct = sp.simplify(fp)
    wrongs = []

    candidates = [
        correct * 2,
        correct / 2,
        -correct,
        correct + 1,
        correct - 1,
    ]

    for w in candidates:
        w_s = sp.simplify(w)
        if sp.simplify(w_s - correct) != 0 and all(sp.simplify(w_s - ww) != 0 for ww in wrongs):
            wrongs.append(w_s)
        if len(wrongs) == 3:
            break

    while len(wrongs) < 3:
        extra = correct + (len(wrongs) + 2)
        if sp.simplify(extra - correct) != 0:
            wrongs.append(sp.simplify(extra))

    options = [correct] + wrongs
    random.shuffle(options)
    correct_index = options.index(correct)
    return options, correct_index

# ============================================================
# 多項式（1次・2次・3次かっこ付き）
# ============================================================
def gen_poly_linear():
    a = random.choice([i for i in range(-5, 6) if i not in [0]])
    b = random.randint(-5, 5)
    f = a*x + b
    return f, sp.diff(f, x), "poly_linear"

def gen_poly_quadratic():
    a = random.choice([i for i in range(-5, 6) if i not in [0]])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    f = a*x**2 + b*x + c
    return f, sp.diff(f, x), "poly_quad"

def gen_poly_cubic_bracket():
    a = random.choice([i for i in range(-3, 4) if i not in [0]])
    b = random.choice([i for i in range(-3, 4) if i not in [0]])
    c = random.randint(-5, 5)
    p = random.randint(-3, 3)
    q = random.randint(-3, 3)
    f = a*(x-p)**3 + b*(x-q)**2 + c
    return f, sp.diff(f, x), "poly_cubic_bracket"

# ============================================================
# 三角関数（sin → cos → tan の順）
# ============================================================
def gen_trig(kind, fixed1=False):
    if fixed1:
        a = 1
    else:
        a = random.choice([2, 3, 4])
    b = random.randint(-2, 2)
    u = a*x + b

    if kind == "sin":
        f = sp.sin(u)
    elif kind == "cos":
        f = sp.cos(u)
    else:
        f = sp.tan(u)

    return f, sp.diff(f, x), f"{kind}_ax+b"

# ============================================================
# 指数・対数（合わせて5問）
# ============================================================
def gen_exp(fixed1=False):
    base = random.choice(["e", "2", "10", "a"])
    if fixed1:
        a = 1
    else:
        a = random.choice([2, 3, 4])
    b = random.randint(-2, 2)

    if base == "e":
        f = sp.exp(a*x + b)
    elif base == "2":
        f = 2**(a*x + b)
    elif base == "10":
        f = 10**(a*x + b)
    else:
        basev = random.randint(2, 5)
        f = basev**(a*x + b)

    return f, sp.diff(f, x), f"exp_{base}_ax+b"

def gen_log():
    base = random.choice(["ln", "2", "10", "a"])
    a = random.randint(1, 3)
    b = random.randint(-2, 2)
    u = a*x + b

    if base == "ln":
        f = sp.log(u)
    elif base == "2":
        f = sp.log(u, 2)
    elif base == "10":
        f = sp.log(u, 10)
    else:
        basev = random.randint(2, 5)
        f = sp.log(u, basev)

    return f, sp.diff(f, x), f"log_{base}_ax+b"

# ============================================================
# 類似チェックつき問題追加
# ============================================================
def add_problem(gen_func, problems, seen_exact, seen_struct, *args):
    last = None
    for attempt in range(10):
        f, fp, skey = gen_func(*args)
        ekey = sp.srepr(f)
        if ekey not in seen_exact and skey not in seen_struct:
            seen_exact.add(ekey)
            seen_struct.add(skey)
            opts, idx = generate_choices(fp)
            problems.append({"f": f, "fp": fp, "opts": opts, "idx": idx})
            return
        last = (f, fp, skey)

    # 10回失敗 → 類似でも採用
    f, fp, skey = last
    ekey = sp.srepr(f)
    seen_exact.add(ekey)
    seen_struct.add(skey)
    opts, idx = generate_choices(fp)
    problems.append({"f": f, "fp": fp, "opts": opts, "idx": idx})

# ============================================================
# 5題セット生成（難易度順）
# ============================================================
def build_set(mode):
    problems = []
    seen_exact = set()
    seen_struct = set()

    if mode == "多項式":
        add_problem(gen_poly_linear, problems, seen_exact, seen_struct)
        add_problem(gen_poly_quadratic, problems, seen_exact, seen_struct)
        add_problem(gen_poly_cubic_bracket, problems, seen_exact, seen_struct)
        for _ in range(2):
            add_problem(gen_poly_quadratic, problems, seen_exact, seen_struct)

    elif mode == "三角関数":
        add_problem(lambda: gen_trig("sin", True), problems, seen_exact, seen_struct)
        add_problem(lambda: gen_trig("cos", False), problems, seen_exact, seen_struct)
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
    st.session_state.selects = [None]*5
if "checked" not in st.session_state:
    st.session_state.checked = False
if "set_id" not in st.session_state:
    st.session_state.set_id = 0

# ============================================================
# UI
# ============================================================
st.title("微分トレーニング（4択・難易度順）")

mode = st.selectbox("問題の種類を選んでください", ["多項式", "三角関数", "指数・対数"])
st.session_state.mode = mode

if st.button("5題を生成する"):
    st.session_state.problems = build_set(mode)
    st.session_state.selects = [None]*5
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
            format_func=lambda j: labels[j],
            index=None,
            key=f"choice_{st.session_state.set_id}_{i}",
        )
        st.session_state.selects[i] = choice

    if st.button("採点する"):
        st.session_state.checked = True

    if st.session_state.checked:
        st.markdown("## 採点結果")

        correct = 0
        for i, p in enumerate(probs):
            user = st.session_state.selects[i]
            st.markdown(f"### 【問題 {i+1}】")
            if user == p["idx"]:
                st.success("正解")
                correct += 1
            else:
                st.error("不正解")
            st.latex(rf"正しい答え：\ f'(x) = {sp.latex(p['fp'])}")

        st.markdown(f"## 正答数：{correct} / 5")

        if st.button("次の問題セットへ"):
            st.session_state.problems = build_set(mode)
            st.session_state.selects = [None]*5
            st.session_state.checked = False
            st.session_state.set_id += 1

else:
    st.info("「5題を生成する」を押してください。")
