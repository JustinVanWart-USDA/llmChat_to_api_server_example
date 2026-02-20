"""
Selenium-based fallback client for chat websites (browser automation)
Use this if HTTP reverse-engineering doesn't work.
"""
import time
import uuid
import os
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatSeleniumClient:
    """
    Generic Selenium-based client for chat websites - browser automation fallback.
    More reliable but slower than HTTP requests.
    """
    
    def __init__(self, headless: bool = False, base_url: Optional[str] = None):
        """
        Initialize Selenium WebDriver
        
        Args:
            headless: Run browser in headless mode
            base_url: Base URL of the chat website (from .env if not provided)
        """
        self.base_url = base_url or os.getenv("CHAT_WEBSITE_URL", "https://example-chat.com")
        self.headless = headless or os.getenv("SELENIUM_HEADLESS", "false").lower() == "true"
        self.driver = None
        self.messages_history: List[Dict[str, str]] = []
        logger.info(f"Initialized Selenium client for: {self.base_url}")
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.base_url)
        
        # Wait for page to load
        time.sleep(3)
        logger.info("Driver initialized and page loaded")
    
    def send_message(self, user_message: str, timeout: int = 120) -> Dict[str, str]:
        """
        Send a message via browser and wait for response
        
        Args:
            user_message: The user's message
            timeout: Maximum time to wait for response in seconds
        
        Returns:
            Dictionary with 'role' and 'content' keys
        """
        try:
            logger.info(f"Sending message via Selenium: {user_message[:100]}...")
            
            # Find and interact with chat input
            self._send_input_message(user_message)
            
            # Wait for response
            response_text = self._wait_for_response(timeout)
            
            # Store in history
            self.messages_history.append({
                "role": "user",
                "content": user_message
            })
            
            self.messages_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            logger.info(f"Received response: {response_text[:100]}...")
            
            return {
                "role": "assistant",
                "content": response_text
            }
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    def _send_input_message(self, message: str):
        """
        Find the chat input field and send the message
        These selectors may need adjustment based on actual website structure
        """
        try:
            # Try different input field selectors
            input_selectors = [
                "textarea[placeholder*='message' i]",
                "input[type='text'][placeholder*='message' i]",
                "textarea",
                "input[type='text']",
                "[contenteditable='true']"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found input with selector: {selector}")
                    break
                except:
                    continue
            
            if not input_element:
                raise Exception("Could not find input element")
            
            # Clear and send message
            input_element.clear()
            input_element.send_keys(message)
            
            # Find and click send button
            send_selectors = [
                "button[type='submit']",
                "button:has-text('Send')",
                "button[aria-label*='send' i]",
                "button[class*='send' i]",
                "button svg[class*='send' i]"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_displayed():
                        logger.info(f"Found send button with selector: {selector}")
                        break
                except:
                    continue
            
            if send_button:
                send_button.click()
            else:
                # Try Enter key as fallback
                input_element.send_keys("\n")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error sending input: {e}")
            raise
    
    def _wait_for_response(self, timeout: int) -> str:
        """Wait for AI response to appear"""
        start_time = time.time()
        last_response_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Look for message elements
                message_selectors = [
                    ".message.assistant",
                    "[class*='assistant']",
                    "[class*='bot']",
                    "[class*='response']",
                    "div[role='article']"
                ]
                
                for selector in message_selectors:
                    try:
                        messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if len(messages) > last_response_count:
                            # New message appeared
                            latest = messages[-1]
                            response_text = latest.text.strip()
                            
                            if response_text and not self._is_loading_text(response_text):
                                return response_text
                            
                            last_response_count = len(messages)
                    except:
                        continue
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error waiting for response: {e}")
                time.sleep(0.5)
        
        raise TimeoutError(f"No response received within {timeout} seconds")
    
    def _is_loading_text(self, text: str) -> bool:
        """Check if text indicates loading state"""
        loading_indicators = ["loading", "thinking", "typing", "...", "please wait"]
        return any(indicator in text.lower() for indicator in loading_indicators)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history"""
        return self.messages_history.copy()
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages_history = []
        # Optionally refresh the page
        self.driver.refresh()
        time.sleep(2)
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")
