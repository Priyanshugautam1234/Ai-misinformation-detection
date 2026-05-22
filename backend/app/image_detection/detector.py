import io
import os
import base64
import hashlib
import math
from typing import Dict, Any, List
from PIL import Image, ImageChops, ImageEnhance
from PIL.ExifTags import TAGS
import torch
import torch.nn as nn
import numpy as np

STANDARD_CAMERA_TAGS = {
    "Make": "Camera Manufacturer",
    "Model": "Camera Model",
    "DateTimeOriginal": "Original Capture Timestamp",
    "GPSInfo": "GPS Location Geotag",
    "Software": "Image Processing Software",
    "LensModel": "Lens Specification"
}

# ----------------------------------------------------
# Pure-PyTorch ResNet-18 Manual Definition
# ----------------------------------------------------
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out

class ResNet18(nn.Module):
    def __init__(self, block=BasicBlock, layers=[2, 2, 2, 2], num_classes=2):
        super(ResNet18, self).__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv2d(3, self.inplanes, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.inplanes)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        self.fc = nn.Sequential(
            nn.Linear(512 * block.expansion, 128),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(128, num_classes)
        )

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x

# Module-level model load
DEVICE = torch.device("cpu")
image_model = None

try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "models", "image_model.pth")
    if os.path.exists(MODEL_PATH):
        image_model = ResNet18()
        image_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        image_model.to(DEVICE)
        image_model.eval()
        print(f"PyTorch ResNet-18 image forensic classifier successfully loaded from {MODEL_PATH}")
    else:
        print(f"Warning: image_model.pth not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading PyTorch ResNet-18 model: {e}")

def analyze_image(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        return {
            "success": False,
            "error": f"Invalid image format or corrupted file: {str(e)}"
        }

    # Gather basic details
    width, height = image.size
    img_format = image.format
    img_mode = image.mode
    size_kb = round(len(image_bytes) / 1024, 2)
    
    # Calculate md5 hash
    md5_hash = hashlib.md5(image_bytes).hexdigest()

    # 1. EXIF Metadata Extraction
    exif_data = {}
    software_detected = None
    creation_date = None
    camera_model = None
    has_gps = False
    
    if hasattr(image, '_getexif') and image._getexif() is not None:
        raw_exif = image._getexif()
        for tag, value in raw_exif.items():
            decoded_tag = TAGS.get(tag, tag)
            
            # Format value safely
            if isinstance(value, bytes):
                try:
                    value = value.decode(errors="replace")
                except Exception:
                    value = repr(value)
            
            val_str = str(value).strip()
            
            if decoded_tag == "Software":
                software_detected = val_str
            elif decoded_tag == "DateTimeOriginal":
                creation_date = val_str
            elif decoded_tag == "DateTime" and not creation_date:
                creation_date = val_str
            elif decoded_tag == "Model":
                camera_model = val_str
            elif decoded_tag == "GPSInfo":
                has_gps = True
                
            exif_data[str(decoded_tag)] = val_str[:150]

    # Map present and missing standard tags
    present_metadata = []
    missing_metadata = []
    
    for tag_name, tag_desc in STANDARD_CAMERA_TAGS.items():
        if tag_name in exif_data:
            present_metadata.append({
                "tag": tag_name,
                "description": tag_desc,
                "value": exif_data[tag_name]
            })
        else:
            missing_metadata.append({
                "tag": tag_name,
                "description": tag_desc
            })

    # 2. Mathematical Error Level Analysis (ELA)
    try:
        # Convert to RGB (JPEG requirement)
        if image.mode != "RGB":
            image_rgb = image.convert("RGB")
        else:
            image_rgb = image

        # Save at quality=95 into memory
        resaved = io.BytesIO()
        image_rgb.save(resaved, format="JPEG", quality=95)
        resaved.seek(0)
        resaved_image = Image.open(resaved)

        # Compute absolute difference
        ela_image = ImageChops.difference(image_rgb, resaved_image)
        
        # Calculate pixel difference statistics
        extrema = ela_image.getextrema()
        max_diff = 0
        if isinstance(extrema[0], tuple):
            max_diff = max(ex[1] for ex in extrema)
        else:
            max_diff = extrema[1]
            
        if max_diff == 0:
            max_diff = 1

        # Rescale the difference image for visualization
        scale = 255.0 / max_diff
        enhanced_ela = ImageEnhance.Brightness(ela_image).enhance(scale)

        # Convert enhanced ELA image to base64 PNG data URL
        buffered = io.BytesIO()
        enhanced_ela.save(buffered, format="PNG")
        buffered.seek(0)
        ela_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        ela_image_data_url = f"data:image/png;base64,{ela_base64}"

        # Get average difference
        gray_ela = ela_image.convert("L")
        pixels_diff = list(gray_ela.getdata())
        avg_diff = sum(pixels_diff) / len(pixels_diff)
        
        # Compute ELA standard deviation
        mean_diff = avg_diff
        variance_diff = sum((p - mean_diff) ** 2 for p in pixels_diff) / len(pixels_diff)
        std_dev_diff = math.sqrt(variance_diff) if variance_diff > 0 else 0.0

        # Grid-based Splicing Anomaly Detection
        grid_cols = 8
        grid_rows = 8
        patch_w = max(1, width // grid_cols)
        patch_h = max(1, height // grid_rows)
        splicing_detected = False
        max_patch_to_mean_ratio = 1.0
        suspicious_patches_count = 0

        for r in range(grid_rows):
            for c in range(grid_cols):
                box = (c * patch_w, r * patch_h, (c + 1) * patch_w, (r + 1) * patch_h)
                patch = gray_ela.crop(box)
                patch_pixels = list(patch.getdata())
                if not patch_pixels:
                    continue
                patch_avg = sum(patch_pixels) / len(patch_pixels)
                if avg_diff > 0.1:
                    ratio = patch_avg / avg_diff
                    if ratio > max_patch_to_mean_ratio:
                        max_patch_to_mean_ratio = ratio
                    # Flag patch if its error level is >3x global average and >5.0
                    if patch_avg > 5.0 and ratio > 3.0:
                        suspicious_patches_count += 1

        if suspicious_patches_count > 0:
            splicing_detected = True

        # Compute ELA anomaly rating (0 to 100 based on standard deviation and average difference)
        ela_rating = min(100.0, (std_dev_diff * 8.0) + (avg_diff * 4.0))
        ela_rating = round(ela_rating, 2)

    except Exception as e:
        ela_image_data_url = ""
        avg_diff = 0.0
        max_diff = 0
        std_dev_diff = 0.0
        splicing_detected = False
        suspicious_patches_count = 0
        ela_rating = 0

    # 3. Local Texture Variance (AI generation indicator)
    pixel_variance = 0.0
    try:
        # Crop 16x16 center patch to measure original local noise variance
        left = max(0, width // 2 - 8)
        top = max(0, height // 2 - 8)
        box = (left, top, left + 16, top + 16)
        patch_orig = image.crop(box).convert("L")
        pixels_orig = list(patch_orig.getdata())
        mean_orig = sum(pixels_orig) / len(pixels_orig)
        variance_orig = sum((p - mean_orig) ** 2 for p in pixels_orig) / len(pixels_orig)
        pixel_variance = round(variance_orig, 2)
    except Exception:
        pixel_variance = 100.0

    # 4. AI PyTorch Model Prediction
    ai_fake_probability = 0.05
    ai_real_probability = 0.95
    ai_prediction = "REAL"
    ai_confidence = 0.95

    if image_model is not None:
        try:
            # Convert to RGB (model was trained on 3-channel images)
            if image.mode != "RGB":
                img_rgb = image.convert("RGB")
            else:
                img_rgb = image

            # Preprocess: resize 128x128 bilinear
            img_resized = img_rgb.resize((128, 128), Image.Resampling.BILINEAR)
            img_np = np.array(img_resized).astype(np.float32) / 255.0
            
            # Form tensor: shape [1, 3, 128, 128]
            img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
            
            # Normalize with ImageNet mean/std
            mean = torch.tensor([0.485, 0.456, 0.406], device=DEVICE).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225], device=DEVICE).view(1, 3, 1, 1)
            img_tensor = (img_tensor - mean) / std

            # Inference
            with torch.no_grad():
                logits = image_model(img_tensor)
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
                
            ai_real_probability = float(probs[0])
            ai_fake_probability = float(probs[1])
        except Exception as ex:
            print(f"AI image classifier prediction error: {ex}")

    # 5. Improved Balanced Forensic Scoring Engine (Reduced False Positives)
    heuristic_score = 100
    risk_factors = []

    # Detect platform-specific signatures
    fn_lower = filename.lower()
    is_whatsapp = "whatsapp" in fn_lower or fn_lower.startswith("wa-") or "whatsapp image" in fn_lower
    is_screenshot = "screenshot" in fn_lower or "screen shot" in fn_lower or "capture" in fn_lower or "prtscr" in fn_lower
    is_low_res = width < 600 or height < 600

    # Mathematical blur detection (variance of high frequency gradient)
    is_blurry = False
    try:
        img_gray = image.convert("L").resize((128, 128))
        arr = np.array(img_gray, dtype=np.float32)
        diff_h = np.abs(arr[:, 1:] - arr[:, :-1])
        diff_v = np.abs(arr[1:, :] - arr[:-1, :])
        edge_score = float(np.mean(diff_h) + np.mean(diff_v))
        if edge_score < 6.0:
            is_blurry = True
    except Exception as e:
        print(f"Error checking blur: {e}")

    # Determine if image is likely blurry or heavily compressed
    is_blurry_or_compressed = is_blurry or is_whatsapp or is_low_res or ((not splicing_detected) and (not software_detected))

    # Calculate heuristic anomaly count
    anomaly_count = 0
    if splicing_detected and not is_blurry_or_compressed:
        anomaly_count += 1
    if software_detected:
        # Software detect has editor check
        software_lower = software_detected.lower()
        if any(sw in software_lower for sw in ["photoshop", "gimp", "adobe", "canva", "paint.net", "pixelmator", "lightroom", "affinity"]):
            anomaly_count += 1
    if (ela_rating > 60 or (suspicious_patches_count > 4)) and not is_blurry_or_compressed:
        anomaly_count += 1

    # AI Prediction uncertainty thresholding
    if ai_fake_probability > 0.85 and anomaly_count >= 2:
        ai_prediction = "FAKE"
        ai_confidence = ai_fake_probability
        anomaly_count += 1  # Flags as neural deepfake anomaly
    elif 0.45 <= ai_fake_probability <= 0.85 or (ai_fake_probability > 0.85 and anomaly_count < 2):
        ai_prediction = "SUSPICIOUS"
        ai_confidence = ai_fake_probability
        anomaly_count += 1  # Adds to total anomaly count
    else:
        ai_prediction = "REAL"
        ai_confidence = ai_real_probability

    # Metadata Integrity Metric & Penalty
    metadata_integrity = 100
    if not exif_data:
        metadata_integrity = 50 if (is_screenshot or is_whatsapp) else 20
        if is_screenshot or is_whatsapp:
            penalty = 2
            risk_factors.append("EXIF metadata is absent (standard for screenshots and compressed messaging platform shares).")
        else:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                penalty = 5
                risk_factors.append("Standard camera EXIF headers are entirely missing (Stripped metadata risk).")
            else:
                penalty = 2
                risk_factors.append("No EXIF metadata tags found in file headers.")
        heuristic_score -= penalty
    else:
        missing_fields = []
        for field in ["Make", "Model", "DateTimeOriginal"]:
            if field not in exif_data:
                missing_fields.append(field)
                metadata_integrity -= 5
        if missing_fields:
            penalty = len(missing_fields) if (is_screenshot or is_whatsapp) else len(missing_fields) * 2
            heuristic_score -= penalty
            risk_factors.append(f"Missing standard camera descriptors in EXIF: {', '.join(missing_fields)}")

    # Software edits signature penalty
    has_editor_software = False
    if software_detected:
        software_lower = software_detected.lower()
        if any(sw in software_lower for sw in ["photoshop", "gimp", "adobe", "canva", "paint.net", "pixelmator", "lightroom", "affinity"]):
            has_editor_software = True
            heuristic_score -= 20  # Reduced from 45
            metadata_integrity = max(0, metadata_integrity - 25)
            risk_factors.append(f"Edited metadata signature: modified via processing software ({software_detected})")
        else:
            heuristic_score -= 10  # Reduced from 25
            metadata_integrity = max(0, metadata_integrity - 15)
            risk_factors.append(f"Non-camera processing software tag detected: {software_detected}")

    # Recompression & platform smaller penalties
    if is_whatsapp:
        heuristic_score -= 3  # Reduced from 10
        risk_factors.append("WhatsApp compressed image signature. Compression ratios altered slightly.")
        
    if is_screenshot:
        heuristic_score -= 4  # Reduced from 10
        risk_factors.append("Screenshot image signature detected (lacks camera sensor metadata).")

    if is_low_res:
        heuristic_score -= 2  # Reduced from 5
        risk_factors.append("Low resolution image boundary (limits forensic detail accuracy).")

    if is_blurry:
        heuristic_score -= 2
        risk_factors.append("Image exhibits soft focus or blur, reducing high-frequency detail analysis.")

    # ELA Inconsistencies & Compression validation (Waived/Reduced for blurry/compressed images)
    if ela_rating > 80:
        penalty = 8 if is_blurry_or_compressed else 25  # Reduced from 15/40
        heuristic_score -= penalty
        risk_factors.append("Critical compression inconsistencies identified via Error Level Analysis (high ELA anomaly).")
    elif ela_rating > 50:
        penalty = 4 if is_blurry_or_compressed else 12  # Reduced from 8/25
        heuristic_score -= penalty
        risk_factors.append("Moderate compression inconsistencies detected via Error Level Analysis.")
    elif ela_rating > 30:
        penalty = 1 if is_blurry_or_compressed else 5   # Reduced from 3/10
        heuristic_score -= penalty
        risk_factors.append("Minor recompression variance detected.")

    # Local Splicing validation
    if splicing_detected:
        splicing_penalty = 10 if is_blurry_or_compressed else 20  # Reduced from 35
        heuristic_score -= splicing_penalty
        risk_factors.append(f"Splicing anomaly detected: localized image sectors ({suspicious_patches_count} patches) compress at abnormal rates.")
        if suspicious_patches_count > 0:
            patch_penalty = min(10 if is_blurry_or_compressed else 15, suspicious_patches_count * 2)
            heuristic_score -= patch_penalty

    # Center patch texture validation
    if pixel_variance < 5.0 and filename.lower().endswith(('.jpg', '.jpeg')):
        if not is_blurry_or_compressed:
            heuristic_score -= 8  # Reduced from 15
            risk_factors.append("Extremely low local texture variance (potential synthetic skin smoothing or clone stamp).")
        else:
            risk_factors.append("Low texture variance observed (consistent with blurry/compressed media, no penalty applied).")

    # Anomaly Percentage Metric
    high_diff_pixels = sum(1 for p in pixels_diff if p > 15) if 'pixels_diff' in locals() else 0
    pixel_anomaly_pct = (high_diff_pixels / len(pixels_diff)) * 100.0 if 'pixels_diff' in locals() and len(pixels_diff) > 0 else 0.0
    grid_anomaly_pct = (suspicious_patches_count / 64.0) * 100.0
    anomaly_pct = round(max(pixel_anomaly_pct, grid_anomaly_pct), 2)
    anomaly_pct = min(100.0, max(0.0, anomaly_pct))

    if anomaly_pct > 30.0:
        if not is_blurry_or_compressed:
            heuristic_score -= 8  # Reduced from 15
            risk_factors.append(f"Extremely high ELA anomaly density: {anomaly_pct}% of the image exhibits compression mismatch.")
        else:
            risk_factors.append(f"High compression noise density detected: {anomaly_pct}% pixel recompression variance (consistent with normal user compression).")

    # Dynamic Deepfake Probability based on AI classifier
    deepfake_prob = round(ai_fake_probability * 100, 2)
    if ai_prediction == "FAKE":
        risk_factors.append(f"AI Neural Classifier flags synthetic/manipulated signatures (AI Fake Probability: {deepfake_prob}%).")
    elif ai_prediction == "SUSPICIOUS":
        risk_factors.append(f"AI Neural Classifier indicates moderate uncertainty / possible manipulation (AI Fake Probability: {deepfake_prob}%).")

    # =========================================================
    # IMPROVED HYBRID AI + FORENSIC SCORING ENGINE
    # =========================================================

    ai_real_score = ai_real_probability * 100.0
    ai_fake_score = ai_fake_probability * 100.0

    # CNN dominates more than heuristics
    final_trust_score = round(
        (0.3 * heuristic_score) +
        (0.7 * ai_real_score),
        2
    )

    # ---------------------------------------------------------
    # STRONG AI FAKE PENALTIES
    # ---------------------------------------------------------

    if ai_fake_probability >= 0.95:
        final_trust_score -= 40
        risk_factors.append(
            "Neural classifier detected extremely strong synthetic image signatures."
        )

    elif ai_fake_probability >= 0.90:
        final_trust_score -= 30
        risk_factors.append(
            "Neural classifier detected strong synthetic image indicators."
        )

    elif ai_fake_probability >= 0.80:
        final_trust_score -= 18
        risk_factors.append(
            "Neural classifier detected moderate synthetic generation artifacts."
        )

    # ---------------------------------------------------------
    # PNG SAFEGUARD
    # ---------------------------------------------------------

    if (
        filename.lower().endswith(".png")
        and ai_fake_probability > 0.75
    ):
        final_trust_score -= 10

        risk_factors.append(
            "High-confidence synthetic PNG generation pattern detected."
        )

    # ---------------------------------------------------------
    # UNCERTAINTY HANDLING
    # ---------------------------------------------------------

    if 0.45 <= ai_fake_probability <= 0.75:
        final_trust_score = min(final_trust_score, 65)

    # ---------------------------------------------------------
    # FALSE POSITIVE REDUCTION
    # ---------------------------------------------------------

    if is_blurry_or_compressed and ai_fake_probability < 0.85:
        final_trust_score = max(final_trust_score, 45)

    # ---------------------------------------------------------
    # FINAL BOUNDS
    # ---------------------------------------------------------

    final_trust_score = max(5, min(99, final_trust_score))

    # ---------------------------------------------------------
    # FORENSIC CONFIDENCE
    # ---------------------------------------------------------

    confidence = 70

    if exif_data:
        confidence += 10

    if width >= 1000 and height >= 1000:
        confidence += 10

    if width < 500 or height < 500:
        confidence -= 15

    if 'std_dev_diff' in locals() and std_dev_diff > 1.0:
        confidence += 8

    confidence = max(30, min(98, confidence))

    # ---------------------------------------------------------
    # FINAL THREAT CLASSIFICATION
    # ---------------------------------------------------------

    if ai_fake_probability >= 0.90 and anomaly_count >= 2:
        threat_level = "High Risk"

    elif final_trust_score >= 75 and ai_fake_probability < 0.40:
        threat_level = "Trustworthy"

    else:
        threat_level = "Suspicious"

    # ---------------------------------------------------------
    # FINAL RESPONSE PAYLOAD
    # ---------------------------------------------------------

    return {
        "success": True,
        "filename": filename,
        "format": img_format,
        "resolution": f"{width}x{height}",
        "size_kb": size_kb,
        "mode": img_mode,

        "trust_score": round(final_trust_score, 2),
        "final_trust_score": round(final_trust_score, 2),
        "threat_level": threat_level,

        "ai_fake_probability": round(ai_fake_probability, 4),
        "ai_real_probability": round(ai_real_probability, 4),
        "ai_prediction": ai_prediction,
        "ai_confidence": round(ai_confidence, 4),

        "metadata_integrity_score": metadata_integrity,
        "anomaly_percentage": anomaly_pct,
        "forensic_confidence_score": confidence,

        "ela_image_base64": ela_image_data_url,

        "metadata": {
            "software": software_detected or "None detected",
            "camera": camera_model or "Unknown / Mobile device",
            "date": creation_date or "N/A",
            "gps_present": has_gps,
            "raw_headers_count": len(exif_data),
            "present_metadata": present_metadata,
            "missing_metadata": missing_metadata
        },

        "forensics": {
            "deepfake_probability": round(ai_fake_probability * 100, 2),
            "ela_anomaly_rating": ela_rating,
            "noise_variance": pixel_variance,
            "avg_diff": round(avg_diff, 4),
            "max_diff": max_diff,
            "std_dev_diff": round(std_dev_diff, 4),
            "splicing_detected": splicing_detected,
            "suspicious_patches_count": suspicious_patches_count,
            "anomaly_count": anomaly_count
        },

        "risk_factors": risk_factors
    }


