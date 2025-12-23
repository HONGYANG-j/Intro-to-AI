import pandas as pd
import barcode
from barcode.writer import ImageWriter
import os

# 1. Load your dataset
df = pd.read_csv("Customer.csv")

# 2. Pick 5 random samples to test
samples = df.sample(5)
print("Generating barcodes for the following orders:")
print(samples[['Order ID', 'Customer Name', 'City', 'State']])

# 3. Generate Images
if not os.path.exists("test_barcodes"):
    os.makedirs("test_barcodes")

code128 = barcode.get_barcode_class('code128')

for index, row in samples.iterrows():
    order_id = row['Order ID']
    # Create barcode image
    my_code = code128(order_id, writer=ImageWriter())
    filename = f"test_barcodes/{order_id}"
    my_code.save(filename)
    print(f"✅ Generated: {filename}.png")

print("\nDONE! Check the 'test_barcodes' folder for images to upload.")
