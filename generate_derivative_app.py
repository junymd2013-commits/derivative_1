import streamlit as st
import random
import sympy as sp

# -----------------------------
# 微分問題の自動生成
# -----------------------------
def generate_derivative_problem(mode):
    x = sp.Symbol('x')

    if mode == "一次関数":
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        f = a*x + b

    elif mode == "二次関数":
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        c = random.randint(-5, 5)
        f = a*x**2 + b*x + c

    elif mode == "三次関数":
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        c = random.randint(-3, 3)
        d = random.randint(-3, 3)
        f = a*x**3 + b*x**2 + c*x + d

    elif mode == "指数関数":
        a = random.randint(1, 5)
        k = random.randint(1, 5)
        f = a * sp.exp(k*x)

    else:  # 三角関数
        a = random.randint(1, 5)
        f = a * sp.sin(x)

    fprime = sp.diff(f, x)

    return sp.simplify(f), sp.simplify(fprime)


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("微分の自動問題生成アプリ（5題セット）")

mode = st.selectbox(
    "関数の種類を選んでください",
    ["一次関数", "二次関数", "三次関数", "指数関数", "三角関数"]
)

# 初期化
if "problems" not in st.session_state:
    st.session_state.problems = []
if "answers" not in st.session_state:
    st.session_state.answers = [""] * 5
if "checked" not in st.session_state:
    st.session_state.checked = False

# 新しい問題セットを生成
if st.button("5題を生成する"):
    st.session_state.problems = [generate_derivative_problem(mode) for _ in range(5)]
    st.session_state.answers = [""] * 5
    st.session_state.checked = False

# 問題が生成されている場合のみ表示
if st.session_state.problems:

    st.subheader("【問題】微分せよ")

    for i, (f, fprime) in enumerate(st.session_state.problems):
        st.latex(f"({i+1})\quad f(x) = {sp.latex(f)}")
        st.session_state.answers[i] = st.text_input(
            f"答え {i+1}（f'(x)= ?）",
            value=st.session_state.answers[i],
            key=f"ans_{i}"
        )

    # 採点
    if st.button("採点する"):
        st.session_state.checked = True

    # 採点結果
    if st.session_state.checked:
        st.subheader("【採点結果】")

        correct = 0
        for i, (f, fprime) in enumerate(st.session_state.problems):
            user = st.session_state.answers[i]
            try:
                user_expr = sp.simplify(user)
                if sp.simplify(user_expr - fprime) == 0:
                    st.success(f"{i+1}：正解！")
                    correct += 1
                else:
                    st.error(f"{i+1}：不正解。正しい答えは {sp.latex(fprime)}")
            except:
                st.error(f"{i+1}：式が読み取れません。正しい答えは {sp.latex(fprime)}")

        st.write(f"正答数：{correct} / 5")

        # 再挑戦・終了ボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("もう一度挑戦する"):
                st.session_state.problems = [generate_derivative_problem(mode) for _ in range(5)]
                st.session_state.answers = [""] * 5
                st.session_state.checked = False

        with col2:
            if st.button("終了する"):
                st.write("お疲れさまでした！")
                st.stop()
