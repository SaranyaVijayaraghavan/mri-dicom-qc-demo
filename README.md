# MRI DICOM QC Demo

A small beginner-level example for an imaging specialist portfolio. The script reads the public `MR_small.dcm` test image provided by pydicom, checks selected metadata against an example protocol, calculates basic raw-pixel statistics, and saves a CSV report and PNG figure.

## How to run it

1. Clone this repository and open its folder:

   ```bash
   git clone https://github.com/SaranyaVijayaraghavan/mri-dicom-qc-demo.git
   cd mri-dicom-qc-demo
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows, run `.venv\Scripts\activate`. On macOS or Linux, run `source .venv/bin/activate`.

3. Install the pinned libraries and run the check:

   ```bash
   python -m pip install -r requirements.txt
   python qc_check.py
   ```

The script creates or replaces the report files in `results/`.

## Outputs

- `results/qc_report.csv` has one row for the test image. It includes the extracted metadata, one PASS/FAIL/MISSING column for each protocol check, raw pixel minimum, maximum, mean and standard deviation, the demo SNR estimate, and the overall result. A missing required value makes the overall result FAIL.
- `results/mr_small_qc.png` shows the image and a histogram of its raw pixel values. The title labels the SNR as a demo estimate.

The example protocol values are defined near the top of `qc_check.py`. The requirements file pins the library versions for Python 3.10–3.13 and Python 3.14 or newer.

## Limitations

- This is a demo on a public pydicom test file, not a clinical dataset.
- The protocol is an example I made up for this demo and is not a site or trial protocol.
- SNR is a rough estimate from a central region and corner region. It is not a validated measurement.
- This code is not for clinical use and does not replace a validated imaging QC workflow.
