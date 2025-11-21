from selenium import webdriver
from selenium.webdriver.common.by import By

import re
import sys

GoTo = re.compile(r"[G|g]o [T|t]o (\S+)")

Click = re.compile(r"[C|c]lick (.+)")

Type = re.compile(r"[T|t]ype (.+?) [I|i]nto (.+)")

def match_instructions(instr: str, driver: webdriver.Firefox | webdriver.Chrome) -> bool: 
    gt_match = GoTo.match(instr)
    if gt_match:
        try:
            driver.get(gt_match.group(1))
        except:
            print(repr(sys.exception()))
            return False
        return True

    click_match = Click.match(instr)
    if click_match:
        try:
            driver.find_element(By.PARTIAL_LINK_TEXT, click_match.group(1)).click()
        except:
            try:
                driver.find_element(By.CSS_SELECTOR, "[aria-label=\'{name}\']".format(name=click_match.group(1))).click()
            except:
                print(repr(sys.exception()))
                return False
        return True

    type_match = Type.match(instr)
    if type_match:
        try:
            text_box = driver.find_element(By.PARTIAL_LINK_TEXT, type_match.group(2))
            text_box.clear()
            text_box.send_keys(type_match.group(1))
        except:
            try:
                text_box = driver.find_element(By.CSS_SELECTOR, "[placeholder=\'{name}\']".format(name=type_match.group(2)))
                text_box.clear()
                text_box.send_keys(type_match.group(1))
            except:
                print(repr(sys.exception()))
                return False
        return True
    return False
