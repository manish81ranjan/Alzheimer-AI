# import os
# import uuid
# import numpy as np
# from PIL import Image

# from src.config import Config
# from .model_loader import get_model
# from .preprocess import preprocess_image


# def _find_last_conv_layer(model):
#     """
#     Auto-detect the last Conv2D layer for Grad-CAM.
#     """
#     import tensorflow as tf

#     for layer in reversed(model.layers):
#         try:
#             if isinstance(layer, tf.keras.layers.Conv2D):
#                 return layer.name
#         except Exception:
#             continue

#     raise ValueError("No Conv2D layer found for Grad-CAM.")


# def generate_gradcam(image_path: str, model_path: str, pred_index: int = None) -> str:
#     """
#     Generates Grad-CAM heatmap and saves it under backend/src/static/heatmaps.
#     Returns public URL like /static/heatmaps/xxx.png
#     """
#     import tensorflow as tf

#     model = get_model(model_path)
#     img_array = preprocess_image(image_path=image_path, img_size=Config.IMG_SIZE)

#     last_conv_layer_name = _find_last_conv_layer(model)

#     grad_model = tf.keras.models.Model(
#         [model.inputs],
#         [model.get_layer(last_conv_layer_name).output, model.output],
#     )

#     with tf.GradientTape() as tape:
#         conv_outputs, predictions = grad_model(img_array)

#         if pred_index is None:
#             pred_index = tf.argmax(predictions[0])

#         class_channel = predictions[:, pred_index]

#     grads = tape.gradient(class_channel, conv_outputs)
#     pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

#     conv_outputs = conv_outputs[0]
#     heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
#     heatmap = tf.squeeze(heatmap)

#     heatmap = np.maximum(heatmap, 0)
#     max_val = np.max(heatmap) if np.max(heatmap) != 0 else 1e-8
#     heatmap = heatmap / max_val

#     # Convert grayscale source image to RGB for overlay
#     original = Image.open(image_path).convert("RGB")
#     original = original.resize((Config.IMG_SIZE, Config.IMG_SIZE))

#     heatmap_img = Image.fromarray(np.uint8(255 * heatmap)).resize(original.size)
#     heatmap_arr = np.array(heatmap_img)

#     # Create red overlay manually
#     overlay = np.zeros((heatmap_arr.shape[0], heatmap_arr.shape[1], 3), dtype=np.uint8)
#     overlay[..., 0] = heatmap_arr  # red channel

#     original_arr = np.array(original, dtype=np.float32)
#     overlay_arr = overlay.astype(np.float32)

#     alpha = 0.35
#     blended = np.clip((1 - alpha) * original_arr + alpha * overlay_arr, 0, 255).astype(np.uint8)

#     filename = f"gradcam_{uuid.uuid4().hex}.png"
#     save_path = os.path.join(Config.HEATMAP_DIR, filename)

#     Image.fromarray(blended).save(save_path)

#     return f"/static/heatmaps/{filename}"



import os
import uuid
import numpy as np
from PIL import Image

from src.config import Config
from .model_loader import get_model
from .preprocess import preprocess_image


def _find_last_conv_layer_name(model):
    """
    Find the last 2D convolution layer in the model.
    Works for most tf.keras CNN models.
    """
    for layer in reversed(model.layers):
        class_name = layer.__class__.__name__.lower()
        if "conv2d" in class_name:
            return layer.name
    raise ValueError("No Conv2D layer found for Grad-CAM.")


def generate_gradcam(image_path: str, model_path: str, pred_index: int = None) -> str:
    """
    Generate Grad-CAM heatmap overlay and save it.
    Returns public URL: /static/heatmaps/<file>.png
    """
    import tensorflow as tf

    model = get_model(model_path)
    img_array = preprocess_image(image_path=image_path, img_size=Config.IMG_SIZE)

    last_conv_layer_name = _find_last_conv_layer_name(model)

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array, training=False)

        if pred_index is None:
            pred_index = int(tf.argmax(predictions[0]))

        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    if grads is None:
        raise RuntimeError("Failed to compute gradients for Grad-CAM.")

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)

    heatmap = np.maximum(heatmap.numpy(), 0)
    max_val = np.max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    else:
        heatmap = np.zeros_like(heatmap, dtype=np.float32)

    # Original image for overlay
    original = Image.open(image_path).convert("RGB")
    original = original.resize((Config.IMG_SIZE, Config.IMG_SIZE))

    # Resize heatmap to image size
    heatmap_img = Image.fromarray(np.uint8(heatmap * 255)).resize(
        original.size, Image.BILINEAR
    )
    heatmap_arr = np.array(heatmap_img, dtype=np.uint8)

    # Simple red overlay
    overlay = np.zeros((heatmap_arr.shape[0], heatmap_arr.shape[1], 3), dtype=np.uint8)
    overlay[..., 0] = heatmap_arr

    original_arr = np.array(original, dtype=np.float32)
    overlay_arr = overlay.astype(np.float32)

    alpha = 0.38
    blended = np.clip(
        (1.0 - alpha) * original_arr + alpha * overlay_arr,
        0,
        255,
    ).astype(np.uint8)

    os.makedirs(Config.HEATMAP_DIR, exist_ok=True)
    filename = f"gradcam_{uuid.uuid4().hex}.png"
    save_path = os.path.join(Config.HEATMAP_DIR, filename)

    Image.fromarray(blended).save(save_path)

    return f"/static/heatmaps/{filename}"