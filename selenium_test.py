# selenium_test.py

"""
This script is used to test the selenium captcha solver independently.
"""

from selenium_captcha_solver import AmazonCaptchaSolver

# example for selenium captcha solver independently 
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)
    
    # Amazon captcha page
    driver.get("https://www.amazon.com/errors/validateCaptcha")
    
    # create & use solver w/ debug output enabled
    solver = AmazonCaptchaSolver(output_dir="captcha_output", save_debug_output=True)
    solved = solver.solve_captcha(driver)
    
    if solved:
        print(f"Captcha solved")
    else:
        print("Failed to solve CAPTCHA")
    
    driver.quit()