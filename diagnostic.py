import platform
import os
import sys

print(f"Python Version: {sys.version}")
print(f"Architecture: {platform.architecture()}")
print(f"Machine: {platform.machine()}")

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium import webdriver
    
    print("\nAttempting to install driver with webdriver_manager...")
    driver_path = ChromeDriverManager().install()
    print(f"Driver Path: {driver_path}")
    
    if os.path.exists(driver_path):
        print(f"Driver file exists. Size: {os.path.getsize(driver_path)} bytes")
    else:
        print("Driver path does not exist!")

    print("\nAttempting to launch driver...")
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    print("Driver launched successfully!")
    driver.quit()

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
