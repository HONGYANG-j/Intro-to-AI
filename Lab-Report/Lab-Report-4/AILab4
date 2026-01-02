import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(page_title="Activation Function Visualizer", layout="wide")

st.title("Neural Network Activation Functions Visualizer")
st.markdown("""
This application visualizes the three key activation functions used in neural networks:
**ReLU**, **Sigmoid**, and **Hyperbolic Tangent (Tanh)**.
""")

# --- Sidebar for Selection ---
st.sidebar.header("Settings")
function_choice = st.sidebar.radio(
    "Select Activation Function:",
    ("Rectified Linear Unit (ReLU)", "Sigmoid", "Hyperbolic Tangent (Tanh)")
)

# --- Input Range Settings ---
st.sidebar.subheader("Graph Settings")
x_min = st.sidebar.slider("Min X value", -10.0, -1.0, -10.0)
x_max = st.sidebar.slider("Max X value", 1.0, 10.0, 10.0)
resolution = 100

# Generate input data (x values)
x = np.linspace(x_min, x_max, resolution)

# --- Define Functions ---
def relu(x):
    return np.maximum(0, x)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def tanh(x):
    return np.tanh(x)

# --- Visualization Logic ---
if function_choice == "Rectified Linear Unit (ReLU)":
    st.header("1. Rectified Linear Unit (ReLU)")
    y = relu(x)
    formula = r"f(x) = \max(0, x)"
    description = """
    **ReLU** is the most widely used activation function in deep learning. 
    It outputs the input directly if it is positive, otherwise, it outputs zero.
    * **Range:** [0, ∞)
    * **Pros:** Computationally efficient, reduces vanishing gradient problem.
    """

elif function_choice == "Sigmoid":
    st.header("2. Sigmoid Function")
    y = sigmoid(x)
    formula = r"f(x) = \frac{1}{1 + e^{-x}}"
    description = """
    **Sigmoid** transforms values into a range between 0 and 1. 
    It is historically used for binary classification.
    * **Range:** (0, 1)
    * **Pros:** Smooth gradient, prevents "jumps" in output values.
    * **Cons:** Prone to vanishing gradient problem.
    """

elif function_choice == "Hyperbolic Tangent (Tanh)":
    st.header("3. Hyperbolic Tangent (Tanh)")
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
    
    # Interactive Point Checker
    st.markdown("---")
    test_val = st.number_input("Enter a test value for x:", value=0.0)
    
    if function_choice == "Rectified Linear Unit (ReLU)":
        res_val = relu(test_val)
    elif function_choice == "Sigmoid":
        res_val = sigmoid(test_val)
    else:
        res_val = tanh(test_val)
        
    st.write(f"**Result f({test_val}):** {res_val:.4f}")

with col2:
    st.subheader("Visualization Graph")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the main function
    ax.plot(x, y, label=function_choice, color='blue', linewidth=2)
    
    # Add grid and axes lines
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(0, color='black', linewidth=1, linestyle='--')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Highlight the test point if within range
    if x_min <= test_val <= x_max:
        ax.plot(test_val, res_val, 'ro', label=f"Point ({test_val}, {res_val:.2f})")
    
    ax.set_title(f"{function_choice} Curve", fontsize=14)
    ax.set_xlabel("Input (x)")
    ax.set_ylabel("Activation Output (y)")
    ax.legend()
    
    st.pyplot(fig)

# --- Footer ---
st.markdown("---")
st.caption("Developed for BSD3513: Intro to AI | Lab 4")
