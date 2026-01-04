import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(page_title="Tanh Visualizer", layout="wide")

st.title("Activation Function: Hyperbolic Tangent (Tanh)")
st.markdown("This application visualizes the **Tanh** activation function.")

# --- Sidebar Settings ---
st.sidebar.header("Graph Settings")
x_min = st.sidebar.slider("Min X value", -10.0, -1.0, -10.0)
x_max = st.sidebar.slider("Max X value", 1.0, 10.0, 10.0)
resolution = 100

# Generate input data
x = np.linspace(x_min, x_max, resolution)

# --- Define Function ---
def tanh(x):
    return np.tanh(x)

# --- Logic & Description ---
y = tanh(x)
formula = r"f(x) = \tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}"
description = """
**Tanh** is similar to Sigmoid but outputs values between -1 and 1. 
It is zero-centered, making it often easier to model inputs that have strong negative, neutral, and positive values.
* **Range:** (-1, 1)
* **Pros:** Zero-centered, generally works better than Sigmoid in hidden layers.
"""

# --- Display Content ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Formula & Properties")
    st.latex(formula)
    st.info(description)

    st.markdown("---")
    test_val = st.number_input("Enter a test value for x:", value=0.0)
    res_val = tanh(test_val)
    st.write(f"**Result f({test_val}):** {res_val:.4f}")

with col2:
    st.subheader("Visualization Graph")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x, y, label="Tanh", color='red', linewidth=2)
    
    # Grid and axes
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(0, color='black', linewidth=1, linestyle='--')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Highlight point
    if x_min <= test_val <= x_max:
        ax.plot(test_val, res_val, 'ro', label=f"Point ({test_val}, {res_val:.2f})")

    ax.set_title("Hyperbolic Tangent (Tanh) Curve", fontsize=14)
    ax.set_xlabel("Input (x)")
    ax.set_ylabel("Activation Output (y)")
    ax.legend()
    
    st.pyplot(fig)

st.markdown("---")
st.caption("Developed for BSD3513: Intro to AI | Lab 4 - App 3")
