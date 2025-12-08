import streamlit as st
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Image Transform Playground (PyTorch)",
    page_icon="",
    layout="centered"
)

st.title("Simple Image Transform Playground")
st.write("Using **PyTorch torchvision.transforms** + Streamlit")

# -----------------------------
# Sidebar: Choose transforms
# -----------------------------
st.sidebar.header("Transform Options")

do_gray = st.sidebar.checkbox("Convert to Grayscale", value=False)
do_flip = st.sidebar.checkbox("Horizontal Flip", value=False)
do_random_crop = st.sidebar.checkbox("Random Crop (80%)", value=False)
do_color_jitter = st.sidebar.checkbox("Color Jitter", value=False)

if do_color_jitter:
    brightness = st.sidebar.slider("Brightness", 0.0, 2.0, 1.0, 0.1)
    contrast = st.sidebar.slider("Contrast", 0.0, 2.0, 1.0, 0.1)
    saturation = st.sidebar.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
    hue = st.sidebar.slider("Hue", -0.5, 0.5, 0.0, 0.05)
else:
    brightness = contrast = saturation = 1.0
    hue = 0.0

uploaded_file = st.file_uploader("Upload an image (jpg/png)", type=["jpg", "jpeg", "png"])

# -----------------------------
# Build transform pipeline
# -----------------------------
def build_transform_pipeline():
    t_list = []
    if do_gray:
        t_list.append(transforms.Grayscale(num_output_channels=3))
    if do_flip:
        t_list.append(transforms.RandomHorizontalFlip(p=1.0))
    if do_random_crop:
        t_list.append(transforms.RandomResizedCrop(size=224, scale=(0.8, 1.0)))
    else:
        t_list.append(transforms.Resize((224, 224)))
    if do_color_jitter:
        t_list.append(
            transforms.ColorJitter(
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                hue=hue
            )
        )
    return transforms.Compose(t_list)

if uploaded_file is not None:
    original_image = Image.open(uploaded_file).convert("RGB")

    st.subheader("Original Image")
    st.image(original_image, use_container_width=True)

    # Apply transforms
    transform_pipeline = build_transform_pipeline()
    transformed = transform_pipeline(original_image)

    st.subheader("Transformed Image")
    st.image(transformed, use_container_width=True)

    # Show tensors shape
    to_tensor = transforms.ToTensor()
    original_tensor = to_tensor(original_image)
    transformed_tensor = to_tensor(transformed)

    st.write("### Tensor Shapes")
    st.write(f"Original: {tuple(original_tensor.shape)} (C, H, W)")
    st.write(f"Transformed: {tuple(transformed_tensor.shape)} (C, H, W)")
else:
    st.info("👆 Please upload an image to see transforms.")
