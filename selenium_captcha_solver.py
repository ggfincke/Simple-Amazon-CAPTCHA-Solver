# selenium_captcha_solver.py

import cv2
import numpy as np

# disable nnpack so it can run on ARM Macs
import torch
torch.backends.nnpack.enabled = False

import easyocr
from io import BytesIO
import requests
from selenium.webdriver.common.by import By
import time
import os
import logging

logger = logging.getLogger(__name__)

# Selenium captcha solver using EasyOCR
class SeleniumCaptchaSolver:
    def __init__(self, output_dir="captcha_failures", save_debug_output=False):
        self.output_dir = output_dir
        self.save_debug_output = save_debug_output
        
        # create output directory (if it doesn't exist) & enable debug output
        if self.save_debug_output and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        try:
            # init EasyOCR w/ English only
            self.reader = easyocr.Reader(['en'], gpu=True)
            logger.info("EasyOCR initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing EasyOCR: {e}")
            logger.warning("Please install EasyOCR: pip install easyocr")
            self.reader = None
    
    # download captcha image from page
    def _download_captcha_image(self, driver):
        try:
            # locate captcha image
            captcha_img = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]")
            image_url = captcha_img.get_attribute('src')
            
            # download image
            response = requests.get(image_url)
            
            # save debug output
            if self.save_debug_output:
                temp_img_path = os.path.join(self.output_dir, "temp_captcha.png")
                with open(temp_img_path, "wb") as f:
                    f.write(response.content)
                return temp_img_path
            else:
                # if not saving debug output, process image directly from memory
                return BytesIO(response.content)
            
        except Exception as e:
            logger.error(f"Error downloading captcha image: {e}")
            return None
    
    # preprocess the captcha image to improve OCR accuracy (processes image to a nupmy array)
    def _preprocess_image(self, image_path):
        try:
            # read image - handle both file paths and BytesIO objects
            if isinstance(image_path, BytesIO):
                # convert BytesIO to numpy array
                nparr = np.frombuffer(image_path.getvalue(), np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                image = cv2.imread(image_path)
            
            # convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # increasing contrast using histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast = clahe.apply(gray)
            
            # applying gaussian blur to reduce noise
            blur = cv2.GaussianBlur(contrast, (3, 3), 0)
            
            # applying threshold to get a binary image
            _, binary = cv2.threshold(blur, 170, 255, cv2.THRESH_BINARY_INV)
            
            # dilate to connect broken parts of characters
            kernel = np.ones((2, 2), np.uint8)
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # erode to reduce noise
            eroded = cv2.erode(dilated, np.ones((1, 1), np.uint8), iterations=1)
            
            # invert for OCR
            inverted = cv2.bitwise_not(eroded)
            
            # save preprocessing result for debugging if enabled
            if self.save_debug_output:
                preprocessed_path = os.path.join(self.output_dir, "preprocessed_captcha.png")
                cv2.imwrite(preprocessed_path, inverted)
            
            return inverted
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
            
    # performing OCR on the preprocessed captcha image using EasyOCR
    def _recognize_captcha(self, image):
        if self.reader is None:
            logger.error("EasyOCR not properly initialized")
            return ""
        
        try:
            # EasyOCR recognition (only allowing alphanumeric characters)
            results = self.reader.readtext(image, detail=0, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            
            # join results & convert to uppercase
            text = ''.join(results).upper().strip()
            
            # fixing common errors (see func below)
            text = self._fix_common_errors(text)
            
            logger.info(f"EasyOCR recognized: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return ""
        
    # fix common OCR errors in captcha text (may need adjustments) 
    def _fix_common_errors(self, text):
        # remove spaces & non-alphanumeric characters
        text = ''.join(char for char in text if char.isalnum()).upper()
        
        # common substitutions for OCR errors in Amazon captchas
        replacements = {
            '0': 'O',  
            '1': 'I', 
            '5': 'S', 
            '8': 'B', 
        }
        
        # apply replacements - needs better tuning based on observations of actual Amazon captcha behavior
        for error, correction in replacements.items():
            text = text.replace(error, correction)
            
        return text
        
    # solve the captcha on the current page; true if solved, false if not 
    def solve_captcha(self, driver, max_attempts=3):
        # check if EasyOCR is available
        if self.reader is None:
            logger.error("EasyOCR not available. Cannot solve captcha.")
            return False
        
        # loop until max attempts reached or captcha is solved 
        attempt = 0
        while attempt < max_attempts:
            try:
                # try to locate captcha input field to confirm on a captcha page
                try:
                    input_field = driver.find_element(By.ID, "captchacharacters")
                except:
                    # no captcha needed
                    logger.info("No captcha detected on current page.")
                    return True
                
                # download captcha image
                image_path = self._download_captcha_image(driver)
                if not image_path:
                    logger.error("Could not download captcha image.")
                    attempt += 1
                    continue
                
                # take a screenshot of the original captcha (for manual analysis if OCR fails)
                if self.save_debug_output:
                    screenshot_path = os.path.join(self.output_dir, f"captcha_screenshot_{attempt}.png")
                    driver.save_screenshot(screenshot_path)
                
                # preprocess image & perform OCR
                preprocessed = self._preprocess_image(image_path)
                if preprocessed is None:
                    logger.error("Failed to preprocess image.")
                    attempt += 1
                    continue
                    
                captcha_text = self._recognize_captcha(preprocessed)
                
                # log attempt
                logger.info(f"Attempt {attempt+1}: OCR result: '{captcha_text}'")
                
                # if OCR returned an empty string / very short text, try another image
                if len(captcha_text) < 4:
                    logger.warning("OCR result too short, trying again.")
                    self._try_different_image(driver)
                    attempt += 1
                    continue
                
                # enter the captcha text
                input_field.clear()
                input_field.send_keys(captcha_text)
                
                # click continue
                submit_button = driver.find_element(By.XPATH, "//button[contains(., 'Continue shopping')]")
                submit_button.click()
                
                # wait for page to load
                time.sleep(3)
                
                # check if we still on the captcha page
                try:
                    driver.find_element(By.ID, "captchacharacters")
                    logger.warning("Still on captcha page, solution failed.")
                    
                    # try a different image
                    self._try_different_image(driver)
                    
                    attempt += 1
                    continue
                except:
                    logger.info("Successfully solved captcha!")
                    # clean up successful attempt files
                    self._cleanup_files(attempt, success=True)
                    return True
                    
            except Exception as e:
                logger.error(f"Error solving captcha: {e}")
                attempt += 1
                
        logger.error(f"Failed to solve captcha after {max_attempts} attempts")
        # keep the failed captcha files for analysis
        return False
        
    # click the 'Try different image' link to get a new captcha image
    def _try_different_image(self, driver):
        try:
            link = driver.find_element(By.LINK_TEXT, "Try different image")
            link.click()
            # wait for the new image to load
            time.sleep(1) 
        except:
            logger.warning("Could not click 'Try different image' link")