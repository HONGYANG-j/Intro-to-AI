import streamlit as st
import torch
import torchvision.models as models
from torchvision.models import ResNet18_Weights
from PIL import Image
import pandas as pd

# ---------------------------------------------------------
# Step 1: Create a new Streamlit application configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="CV Image Classifier (CPU)",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🖼️ CPU-Based Image Classification")
st.caption("Powered by PyTorch & ResNet18")

# ---------------------------------------------------------
# Step 3: Configure application to run only on CPU
# ---------------------------------------------------------
device = torch.device("cpu")
st.sidebar.info(f"⚙️ Running on: **{device}**")

# ---------------------------------------------------------
# Step 4: Load pre-trained ResNet18 model
# ---------------------------------------------------------
@st.cache_resource
def load_model():
    # Load model with best available pre-trained weights
    weights = ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    model.to(device)
    model.eval()  # Set to evaluation mode
    return model, weights

try:
    model, weights = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# ---------------------------------------------------------
# Step 5: Apply recommended image preprocessing
# ---------------------------------------------------------
# ResNet18_Weights.DEFAULT.transforms() handles resize, crop, and normalization
preprocess = weights.transforms()

# ---------------------------------------------------------
# Step 6: Design User Interface for upload
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file).convert('RGB')
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    # ---------------------------------------------------------
    # Step 7: Convert to tensor and perform inference
    # ---------------------------------------------------------
    # Preprocess and add batch dimension (unsqueeze)
    input_tensor = preprocess(image).unsqueeze(0)
    input_tensor = input_tensor.to(device)

    with torch.no_grad():  # Disable gradient computation
        output = model(input_tensor)

    # ---------------------------------------------------------
    # Step 8: Apply Softmax and get Top-5
    # ---------------------------------------------------------
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    
    # Get top 5 predictions
    top5_prob, top5_catid = torch.topk(probabilities, 5)

    # Prepare data for visualization
    # Note: Without 'requests', we display Class IDs instead of human-readable names.
    # To get names, you would typically need a local 'imagenet_classes.txt' file.
    results = []
    for i in range(top5_prob.size(0)):
        results.append({
            "Class ID": f"Class {top5_catid[i].item()}",
            "Probability": top5_prob[i].item()
        })
    
    df_results = pd.DataFrame(results)

    # ---------------------------------------------------------
    # Step 9: Visualize prediction probabilities
    # ---------------------------------------------------------
    with col2:
        st.subheader("Top 5 Predictions")
        st.dataframe(df_results.style.format({"Probability": "{:.2%}"}), hide_index=True)
    
    st.subheader("Confidence Chart")
    st.bar_chart(df_results.set_index("Class ID")["Probability"])

# ---------------------------------------------------------
# Step 10: Discussion Section
# ---------------------------------------------------------
st.divider()
st.markdown("### 🧠 Discussion: Level and Process Path")
st.markdown("""
**1. The Level:**
This application operates at the **Application Level** of Computer Vision, utilizing **Transfer Learning**. We employ a pre-trained ResNet18 model, which allows us to perform complex classification tasks on a CPU without the need for extensive training resources or large datasets.

**2. The Process Path:**
1.  **Input:** User uploads an image via Streamlit.
2.  **Preprocessing:** Image is converted to RGB, resized/cropped to 224x224, and normalized (Standardization).
3.  **Inference:** The tensor is passed through the ResNet18 layers (Feature Extraction).
4.  **Output Processing:** The model returns raw logits.
5.  **Softmax:** Logits are converted to probabilities summing to 1.0.
6.  **Visualization:** The top 5 probabilities are extracted and plotted.
""")
