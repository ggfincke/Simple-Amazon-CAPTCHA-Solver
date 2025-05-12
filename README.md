# 🤖 Simple Amazon CAPTCHA Solver

A Python-based solution for automatically solving Amazon CAPTCHAs using EasyOCR and Selenium. This tool was originally created for my use in high-volume Amazon scraping/crawling. It was designed to help automate processes that frequently trigger Amazon's CAPTCHA system.

## ✨ Features

- 🔍 Automatic CAPTCHA image detection and download
- 🎨 Advanced image preprocessing for better OCR accuracy
- 📝 EasyOCR integration for text recognition
- 🔧 Common OCR error correction
- 🐛 Debug output option for development and troubleshooting
- 👤 Manual intervention fallback option
- 🔄 Support for multiple solving attempts

## 📋 Requirements

- 🐍 Python 3.7+
- 🌐 Selenium
- 👁️ EasyOCR
- 🖼️ OpenCV (cv2)
- 🔢 NumPy
- 🖼️ Pillow
- 🌐 Requests

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/ggfincke/Simple-Amazon-CAPTCHA-Solver.git
cd Simple-Amazon-CAPTCHA-Solver
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Basic Usage

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from captcha_solver import AmazonCaptchaSolver

# Initialize the web driver
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

# Navigate to Amazon page that might show CAPTCHA
driver.get("https://www.amazon.com/errors/validateCaptcha")

# Create CAPTCHA solver instance
solver = AmazonCaptchaSolver(output_dir="captcha_output", save_debug_output=True)

# Solve the CAPTCHA
solved = solver.solve_captcha(driver)

# Check if CAPTCHA was solved successfully
if solved:
    print("CAPTCHA solved successfully!")
else:
    print("Failed to solve CAPTCHA")

# Clean up
driver.quit()
```

## 🧪 Test Scripts

The repository includes two test scripts to help you get started:

### Selenium Test (`selenium_test.py`)
A simple script demonstrating how to use the Selenium-based CAPTCHA solver:
```python
python selenium_test.py
```

### Playwright Test (`playwright_test.py`)
A script showing how to use the Playwright-based CAPTCHA solver:
```python
python playwright_test.py
```

Both test scripts:
- Launch a browser instance
- Navigate to Amazon's CAPTCHA page
- Attempt to solve the CAPTCHA
- Save debug output (if enabled)
- Clean up resources

These scripts are for testing/showcasing the solver's functionality and can serve as templates for your own implementations.

## ⚙️ Configuration

The `AmazonCaptchaSolver` class accepts the following parameters:

- `output_dir` (str): Directory to save debug output (default: "captcha_failures")
- `save_debug_output` (bool): Whether to save debug images and screenshots (default: False)

## 🔧 How It Works

1. **Image Detection**: The solver locates the CAPTCHA image on the page using Selenium.
2. **Image Preprocessing**: The image undergoes several preprocessing steps:
   - Grayscale conversion
   - Contrast enhancement
   - Noise reduction
   - Thresholding
   - Character connection and noise removal
3. **OCR Processing**: EasyOCR is used to recognize the text in the preprocessed image.
4. **Error Correction**: Common OCR errors are corrected using predefined rules.
5. **Verification**: The solution is submitted and verified.

## 🐛 Debug Output

When `save_debug_output` is enabled, the solver saves:
- Original CAPTCHA image
- Preprocessed image
- Screenshots of failed attempts
- Manual intervention screenshots (if used)

## ⚠️ Limitations

- Success rate depends on CAPTCHA complexity and image quality
- May require manual intervention for difficult CAPTCHAs
- Performance may vary based on system resources

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please use responsibly and in accordance with Amazon's terms of service. 