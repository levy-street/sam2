import io
from pathlib import Path

import numpy as np
from flask import Flask, request, send_file, send_from_directory
from PIL import Image

from sam2.build_sam import build_sam2_hf, build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

app = Flask(__name__, static_folder='.', static_url_path='')

# Available checkpoints. The MOSE finetune path is expected to exist locally.
CHECKPOINTS = {
    'facebook/sam2-hiera-base-plus': {'hf_id': 'facebook/sam2-hiera-base-plus'},
    'facebook/sam2-hiera-large': {'hf_id': 'facebook/sam2-hiera-large'},
    'mose_finetune': {
        'config': 'sam2_logs/configs/sam2.1_training/sam2.1_hiera_b+_MOSE_finetune.yaml/config.yaml',
        'ckpt': 'checkpoints/mose_finetune.pt'
    },
    'eco-index-finetune': {
        'config': 'sam2_logs/configs/sam2.1_training/sam2.1_hiera_b+_single_frame.yaml/config.yaml',
        'ckpt': 'sam2_logs/configs/sam2.1_training/sam2.1_hiera_b+_single_frame.yaml/checkpoints/checkpoint.pt'
    }
}

_models = {}

def get_predictor(name: str) -> SAM2ImagePredictor:
    if name not in _models:
        info = CHECKPOINTS[name]
        if 'hf_id' in info:
            predictor = SAM2ImagePredictor.from_pretrained(info['hf_id'])
        else:
            model = build_sam2(info['config'], ckpt_path=info['ckpt'])
            predictor = SAM2ImagePredictor(model)
        _models[name] = predictor
    return _models[name]


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    image_file = request.files.get('image')
    checkpoint = request.form.get('checkpoint', 'facebook/sam2-hiera-base-plus')
    print(f"Prediction request received for image: {image_file.name} and checkpoint: {checkpoint}")
    if image_file is None:
        return 'No image', 400
    image = Image.open(image_file.stream).convert('RGB')
    predictor = get_predictor(checkpoint)
    mask_generator = SAM2AutomaticMaskGenerator(predictor.model)
    masks = mask_generator.generate(np.array(image))
    union = np.zeros((image.height, image.width), dtype=bool)
    for m in masks:
        union |= m['segmentation']
    img_np = np.array(image)
    overlay = img_np.copy()
    overlay[union] = (0.5 * img_np[union] + 0.5 * np.array([0, 255, 0])).astype(np.uint8)
    out = Image.fromarray(overlay)
    buf = io.BytesIO()
    out.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)

