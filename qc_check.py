"""Run a small metadata and pixel check on pydicom's public MRI test image."""

# Import the small set of libraries used by this demo.
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydicom
from pydicom.data import get_testdata_file


# Keep the made-up example protocol in one place so it is easy to explain.
EXAMPLE_PROTOCOL = {
    "Modality": {"expected": "MR"},
    "Manufacturer": {"expected": "TOSHIBA_MEC"},
    "Rows": {"expected": 64, "tolerance": 0},
    "Columns": {"expected": 64, "tolerance": 0},
    "PixelSpacing": {"expected": [0.3125, 0.3125], "tolerance": [0.01, 0.01]},
    "SliceThickness": {"expected": 0.8, "tolerance": 0.5},
    "RepetitionTime": {"expected": 4000.0, "tolerance": 1000.0},
    "EchoTime": {"expected": 240.0, "tolerance": 50.0},
    "MagneticFieldStrength": {"expected": 1.5, "tolerance": 0.1},
}


# Read a DICOM tag and use MISSING when the file does not contain it.
def read_value(dataset, tag):
    value = getattr(dataset, tag, None)
    if value is None:
        return "MISSING"
    if tag == "PixelSpacing":
        return list(value)
    return value


# Compare one metadata value with the expected example value and tolerance.
def check_value(value, rule):
    if value == "MISSING":
        return "MISSING"

    expected = rule["expected"]
    tolerance = rule.get("tolerance", 0)
    if isinstance(expected, list):
        actual_values = list(value)
        if len(actual_values) != len(expected):
            return "FAIL"
        for index, actual in enumerate(actual_values):
            if abs(float(actual) - expected[index]) > tolerance[index]:
                return "FAIL"
        return "PASS"

    try:
        matches = abs(float(value) - float(expected)) <= tolerance
    except (TypeError, ValueError):
        matches = str(value) == str(expected)
    return "PASS" if matches else "FAIL"


# Turn pixel values into simple statistics and an unvalidated demo SNR estimate.
def image_statistics(image):
    height, width = image.shape
    center = image[height // 4:3 * height // 4, width // 4:3 * width // 4]
    corner_size = max(1, min(height, width) // 4)
    corners = np.concatenate([
        image[:corner_size, :corner_size].ravel(),
        image[:corner_size, -corner_size:].ravel(),
        image[-corner_size:, :corner_size].ravel(),
        image[-corner_size:, -corner_size:].ravel(),
    ])
    corner_noise = float(np.std(corners))
    snr = float(np.mean(center) / corner_noise) if corner_noise else float("nan")
    return {
        "pixel_min": float(np.min(image)),
        "pixel_max": float(np.max(image)),
        "pixel_mean": float(np.mean(image)),
        "pixel_std": float(np.std(image)),
        "demo_snr_estimate": snr,
    }


# Draw the image and its pixel histogram into one PNG file.
def save_figure(image, snr, output_path):
    figure, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].imshow(image, cmap="gray")
    axes[0].set_title("MR_small.dcm image")
    axes[0].axis("off")
    axes[1].hist(image.ravel(), bins=30, color="steelblue")
    axes[1].set_title("Raw pixel histogram")
    axes[1].set_xlabel("Pixel value")
    axes[1].set_ylabel("Count")
    figure.suptitle(f"Demo SNR estimate: {snr:.3f} (not validated)")
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


# Read the small public MRI example that ships with the installed pydicom package.
def main():
    input_path = get_testdata_file("MR_small.dcm")
    if input_path is None:
        raise FileNotFoundError("pydicom could not provide its MR_small.dcm test file")
    dataset = pydicom.dcmread(input_path)

    # Record each requested metadata field and its example-protocol status.
    metadata = {tag: read_value(dataset, tag) for tag in EXAMPLE_PROTOCOL}
    checks = {tag: check_value(metadata[tag], rule)
              for tag, rule in EXAMPLE_PROTOCOL.items()}

    # Calculate statistics from the raw decoded pixel array.
    image = np.asarray(dataset.pixel_array, dtype=float)
    stats = image_statistics(image)

    # Save the report and figure in the repository's results folder.
    os.makedirs("results", exist_ok=True)
    row = {f"metadata_{key}": str(value) for key, value in metadata.items()}
    row.update({f"check_{key}": value for key, value in checks.items()})
    row.update(stats)
    row["file"] = os.path.basename(input_path)
    row["overall"] = "PASS" if all(value == "PASS" for value in checks.values()) else "FAIL"
    columns = ["file"] + [f"metadata_{key}" for key in metadata]
    columns += [f"check_{key}" for key in checks] + list(stats) + ["overall"]
    pd.DataFrame([row], columns=columns).to_csv(
        "results/qc_report.csv", index=False, float_format="%.6f"
    )
    save_figure(image, stats["demo_snr_estimate"], "results/mr_small_qc.png")

    # Print a short summary without implying this demo is clinical QC.
    passed = list(checks.values()).count("PASS")
    failed = list(checks.values()).count("FAIL")
    missing = list(checks.values()).count("MISSING")
    print(f"{os.path.basename(input_path)}: {row['overall']} "
          f"({passed} pass, {failed} fail, {missing} missing)")
    print("Protocol: EXAMPLE only; SNR: rough demo estimate, not validated.")


# Start the demo when this file is run directly by Python.
if __name__ == "__main__":
    main()
