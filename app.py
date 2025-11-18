import streamlit as st
from sympy import (
    symbols, Function, Eq, dsolve, sympify, Derivative, latex, simplify,
    solve as sym_solve, lambdify
)
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import ollama
import time


if "step_text" not in st.session_state:
    st.session_state.step_text = ""

if "step_finished" not in st.session_state:
    st.session_state.step_finished = False

if "step_started" not in st.session_state:
    st.session_state.step_started = False

if "step_prompt" not in st.session_state:
    st.session_state.step_prompt = ""




def warmup():
    try:
        ollama.chat(
            model="qwen2.5:1.5b",
            messages=[{"role": "user", "content": "hello"}]
        )
    except:
        pass

warmup()


def simple_explain(eq, sol):
    prompt = f"""
Summarize this ODE solution in EXACTLY 3 steps.
Equation: {eq}
Solution: {sol}
"""
    r = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 150}
    )
    return r["message"]["content"]



def detect_order(expr):
    ds = expr.atoms(Derivative)
    if not ds:
        return 0
    return max(len(d.args) - 1 for d in ds)




def extract_rhs(expr, order):
    x = symbols('x')
    y = Function('y')(x)
    target = Derivative(y, *([x] * order))

    try:
        sol = sym_solve(Eq(expr, 0), target)
        if sol:
            return sol[0]
    except:
        pass

    if expr.has(target):
        try:
            return simplify(-(expr - target))
        except:
            return None

    return None




def make_rhs_func(rhs_expr):
    x = symbols('x')
    mapping = {}

    for d in rhs_expr.atoms(Derivative):
        order = len(d.args) - 1
        mapping[d] = symbols(f"y{order}")

    mapping[Function('y')(x)] = symbols("y0")

    clean = rhs_expr.xreplace(mapping)

    vars_needed = sorted(
        [s for s in clean.free_symbols if str(s).startswith("y")],
        key=lambda s: int(str(s)[1:])
    )

    args = [x] + vars_needed

    f = lambdify(
        args, clean,
        modules=[{
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log
        }, "numpy"]
    )

    def fast_rhs(t, Y):
        return f(t, *Y)

    return fast_rhs




def build_system(expr, order):
    rhs = extract_rhs(expr, order)
    if rhs is None:
        return None

    fast = make_rhs_func(rhs)
    if fast is None:
        return None

    def system(t, Y):
        dY = np.zeros(order)
        for i in range(order - 1):
            dY[i] = Y[i + 1]
        dY[-1] = fast(t, Y)
        return dY

    return system



def plot_symbolic_fast(sol_rhs, a, b):
    x = symbols('x')
    f = lambdify(x, sol_rhs, "numpy")
    xs = np.linspace(a, b, 250)
    ys = f(xs)

    fig, ax = plt.subplots()
    ax.plot(xs, ys, linewidth=2)
    ax.grid(True)
    return fig




st.set_page_config(page_title="Differential Equation Solver", layout="wide")
st.title("Differential Equation Solver")

eq_input = st.text_area(
    "Enter Derivative to solve (...) format:",
    """
Derivative(y(x), x, x) + 2*Derivative(y(x), x) + y(x) = exp(x)
""",
    height=180
)

explain_choice = st.radio("Explanation Type", ["Simple", "Step-by-Step", "Both"])
mode = st.radio("Plot Mode", ["Fast (recommended)", "Exact Symbolic"])

col1, col2 = st.columns(2)
x_start = col1.number_input("Start x", value=0.0)
x_end = col2.number_input("End x", value=5.0)



if st.button("Solve"):

    st.session_state.step_started = False
    st.session_state.step_text = ""
    st.session_state.step_finished = False

    progress = st.progress(5)
    status = st.empty()

    eq_text = eq_input.strip()

    if "=" in eq_text:
        L, R = eq_text.split("=", 1)
        expr_text = f"({L}) - ({R})"
    else:
        expr_text = eq_text

    expr = sympify(expr_text)
    order = detect_order(expr)

    progress.progress(20)
    status.write(f"Detected ODE Order = {order}")

    
    symbolic_ok = False
    try:
        sol = dsolve(Eq(expr, 0))
        symbolic_ok = True

        st.subheader("📘 Symbolic Solution")
        st.latex(latex(sol))

        sol_rhs = sol.rhs
        for C in sol_rhs.free_symbols:
            if str(C).startswith("C"):
                sol_rhs = sol_rhs.subs(C, 0)

    except:
        symbolic_ok = False

  
    if not symbolic_ok:
        progress.progress(40)
        status.write("Symbolic failed → Numeric solving...")

        system = build_system(expr, order)
        y0 = np.zeros(order)
        y0[0] = 1.0

        sol_ivp = solve_ivp(
            system, [x_start, x_end], y0,
            t_eval=np.linspace(x_start, x_end, 200)
        )
        numeric_sol = sol_ivp
    else:
        numeric_sol = None


    progress.progress(60)
    status.write("⚡ Plotting (fast)...")

    try:
        if symbolic_ok and mode == "Exact Symbolic":
            fig = plot_symbolic_fast(sol_rhs, x_start, x_end)
        elif symbolic_ok:
            fig = plot_symbolic_fast(sol_rhs, x_start, x_end)
        else:
            fig, ax = plt.subplots()
            ax.plot(numeric_sol.t, numeric_sol.y[0], linewidth=2)
            ax.grid(True)

        progress.progress(100)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Plot Error: {e}")

    sol_latex = latex(sol) if symbolic_ok else "Numeric only"

   
    if explain_choice in ["Simple", "Both"]:
        st.subheader("🟢 Simple Explanation")
        st.markdown("```text\n" + simple_explain(eq_text, sol_latex) + "\n```")

    
    st.session_state.step_prompt = f"""
Solve this ODE in numbered mathematical steps.

FORMAT:
Step 1: ...
Step 2: ...
Step 3: ...
...
Verification: ...

NO paragraphs.

Equation:
{eq_text}

Solution:
{sol_latex}

Begin with Step 1.
"""



st.subheader("🔵 Step-by-Step Solution")


if st.button("Start Step-by-Step Explanation"):

    st.session_state.step_started = True
    st.session_state.step_finished = False
    st.session_state.step_text = ""

    r = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[{"role": "user", "content": st.session_state.step_prompt}],
        options={"num_predict": 400}
    )

    first = r["message"]["content"]
    st.session_state.step_text = first

    if "Verification" in first:
        st.session_state.step_finished = True

    st.rerun()



if st.session_state.step_started:

    st.markdown("```text\n" + st.session_state.step_text + "\n```")

    if not st.session_state.step_finished:

        if st.button("➕ Generate More Steps"):

            prompt = """
Continue the next steps; do not repeat any previous step.
Strict format:
Step 5: ...
Step 6: ...
If final, add Verification: ...
"""

            r2 = ollama.chat(
                model="qwen2.5:1.5b",
                messages=[
                    {"role": "assistant", "content": st.session_state.step_text},
                    {"role": "user", "content": prompt}
                ],
                options={"num_predict": 400}
            )

            extra = r2["message"]["content"]
            st.session_state.step_text += "\n" + extra

            if "Verification" in extra:
                st.session_state.step_finished = True

            st.rerun()

    else:
        st.success("🎉 Explanation Complete!")
        st.button("END")
