                                                      Differential Equation Solver

An advanced AI-powered ODE Solver that supports full SymPy Derivative(...) notation, symbolic & numeric solving, fast plotting, and an AI-generated step-by-step explanation engine.

Built using:
          Streamlit
          
          SymPy
          NumPy / SciPy
          Matplotlib
          Ollama (Qwen 2.5 – 1.5B)
          Python 3.10+

🚀 Features

🔹 1. Solve ANY ODE written in Derivative(...) form

Supports:

    First-order ODEs

    Higher-order ODEs

    Non-homogeneous equations

    Trigonometric, exponential, logarithmic functions

    Polynomial ODEs

    Euler–Cauchy type

    Mixed nonlinear ODEs

    Numeric fallback when symbolic fails

Example input:

    Derivative(y(x), x, x) + 2*Derivative(y(x), x) + y(x) = exp(x)

🔹 2. Ultra-Fast Plotting (0.1 seconds)

Plotting is optimized using:

lambdify() for symbolic fast evaluation

250-point dynamic mesh

numeric fallback via scipy.solve_ivp

🔹 3. AI-Generated Explanations

Two modes:

✔ Simple Explanation

Summarizes the solution in 3 short steps.

✔ Step-by-Step Engine

AI solves the equation step by step:

Start Step-by-Step

Generate More Steps

Stops automatically after Verification

Easy to read, no long paragraphs

Powered by Ollama + Qwen 2.5 (1.5B) (local AI model).

🔹 4. Clean UI

Built with Streamlit:

Simple input box

Real-time progress indicator

Fast / Exact plot mode

Complete explanation section

🧠 Example Screenshot

(Add your own screenshot here)

![App Screenshot](screenshot.png)

🛠 Installation
1. Clone the repository
git clone https://github.com/Rohith-techdev/Differential-Equation-Solver.git
cd Differential-Equation-Solver

2. Install required libraries
pip install -r requirements.txt

3. Install Ollama (for AI explanations)

Download Ollama:
👉 https://ollama.com/

Pull the model:

ollama pull qwen2.5:1.5b

▶ Run the App
streamlit run app.py


The browser will open automatically.

📚 How It Works
1️⃣ Parse equation

Reads Derivative(y(x), x, ...) and converts it to SymPy expression.

2️⃣ Detect ODE order

Automatically detects 1st, 2nd, 3rd… order.

3️⃣ Solve Symbolically

Uses dsolve() when possible.

4️⃣ Numeric Fallback

If symbolic fails, converts ODE → system → integrates using solve_ivp.

5️⃣ Plotting

Uses ultra-fast lambdify plotting.

6️⃣ AI Explanation

AI breaks the solution into steps.

🧩 Supported Equation Examples
Derivative(y(x), x) + y(x) = 0
Derivative(y(x), x) - 3*y(x) = exp(x)
Derivative(y(x), x, x) + y(x) = cos(x)
Derivative(y(x), x, x, x) + 2*Derivative(y(x), x, x) + y(x) = 0
x^2*Derivative(y(x), x, x) + x*Derivative(y(x), x) + y(x) = 0
Derivative(y(x), x, x) + 2*Derivative(y(x), x) + y(x) = exp(x)

📦 Project Structure
Differential-Equation-Solver/
│── app.py
│── requirements.txt
│── README.md
└── .gitignore
