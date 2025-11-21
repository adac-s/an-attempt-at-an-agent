import torch
from transformers import pipeline

from selenium import webdriver
from selenium.webdriver.common.by import By

import matches 

def new_command(pipe, context, driver, command, attempts=5):
    for _ in range(attempts):
        driver.get_screenshot_as_file("./temp.png")
        new_ctx = context + [{"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": "Based on this image, " + command}
        ]}]
        response = pipe(text=new_ctx, images=["./temp.png"], max_new_tokens=512)
        instructions = response[0]["generated_text"][-1]["content"]

        has_error = False
        for i in instructions.split('\n'):
            print(i)
            has_error = not matches.match_instructions(i, driver)
            if has_error: break
        if has_error: continue
        break
    return

def main():

    consent = input("""This application will access your web browser and can perform arbitrary actions on your web browser.
    There is a risk that this program will not do as instructed.
    Do you want to continue running? [N/y]""")

    if consent[0] != 'y':
        return
    
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(2)
    driver.get_screenshot_as_file("./temp.png")

    pipe = pipeline(
        task="image-text-to-text",
        model="google/gemma-3-4b-it",
        device=0,
        temperature=0.9,
        num_additional_image_tokens=0,
        dtype=torch.bfloat16
    )

    ctx = [
        {"role": "user", "content": [
            {"type": "text", "text": """You are playing a game where, when receiving a command to act on a website, you describe the steps needed to do the task following set rules. DO NOT DEVIATE FROM THESE RULES.
            Rule 1: Be as concise as possible while maintaining accuracy. Do not add any additional commentary beyond the instructions.
            Rule 2: When a task requires that a user go to a particular website, phrase it as \"Go to <website>\" where <website> is the full URL of the requested website (e.g. https://www.youtube.com). 
            Rule 3: When a task requires that a user click on something, phrase it as \"Click <label>\" where <label> is the label on the area to be clicked.
            Rule 4: When a task requires that a user hover over an area and NOT CLICK, phrase it as \"Hover <label>\" where <label> is the label on the area to be hovered over.
            Rule 5: When a task requires that a user enter text, like a form or search bar, phrase it as \"Type <text> into <label>\" where <label> is the label on the text box and <text> is the desired input.
            """}
        ]},
        {"role": "assistant", "content": [{"type": "text", "text": "ack"}]},
    ]

    

    
    while True:
        val = input("\nWhat do you want to do: ")

        if val == "/EXIT":
            break

        new_command(pipe, ctx, driver, val)
    driver.quit()

if __name__ == "__main__":
    main()
