from flask import Flask, request, jsonify
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import io

# -------------------------------
# 🔹 Load Model & Processor
# -------------------------------
MODEL_NAME = "microsoft/trocr-small-handwritten"  # or "microsoft/trocr-small-handwritten"
processor = TrOCRProcessor.from_pretrained(MODEL_NAME, use_fast=False)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
model.eval()

# ✅ Ensure config is correct
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.eos_token_id = processor.tokenizer.sep_token_id

# -------------------------------
# 🔹 Flask App
# -------------------------------
app = Flask(__name__)

def predict_text(image: Image.Image):
    """Run OCR prediction on a PIL image."""
    # Preprocess
    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    # Move to device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    pixel_values = pixel_values.to(device)

    # Generate prediction
    with torch.no_grad():
        generated_ids = model.generate(pixel_values, max_length=64)

    # Decode → text
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

@app.route("/predict", methods=["POST"])
def predict():
    """
    Expects an image file via multipart/form-data with key "file".
    Example using curl:
    curl -X POST -F file=@test.png http://localhost:5000/predict
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    try:
        # Read image
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        text = predict_text(image)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# 🔹 Run App
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
