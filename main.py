import time
import pyperclip
import ollama

from string import Template
from pynput import keyboard
from pynput.keyboard import Key, Controller

controller = Controller()

PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)

PROMPT_TEMPLATE_PERSONALIZED = Template("$prompt:$text")

PROMPT_TEMPLATE_CODING_ASSISTANT = Template(
    """
    You are a helpful coding assistant that can code in multiple languages. You can help me with the following tasks:
    $prompt
    $text
    """
)

def get_response(prompt):
    try:
        stream = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        response = ""
        for chunk in stream:
            response += chunk["message"]["content"]
            time.sleep(0.05)
        
        # Copy the full response to the clipboard once completed
        pyperclip.copy(response)
        with controller.pressed(Key.cmd):
            controller.tap("v")
        print(response, end="", flush=True)
    except Exception as e:
        print(f"Error during get_response: {e}")

def fix_text(text, prompt=None, response_type="text"):
    if prompt and response_type != "Code":
        prompt = PROMPT_TEMPLATE_PERSONALIZED.substitute(text=text, prompt=prompt)
    elif response_type == "Code":
        prompt = PROMPT_TEMPLATE_CODING_ASSISTANT.substitute(text=text, prompt=prompt)
    else:
        prompt = PROMPT_TEMPLATE.substitute(text=text)
    
    print("Generated Prompt:", prompt)
    get_response(prompt)

def copy_selection():
    # Copy the selected text to the clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")
    time.sleep(0.1)
    return pyperclip.paste()

def fix_selection():
    text = copy_selection()
    if text:
        print("Copied text:", text)
        fix_text(text)

def fix_selection_with_prompt(response_type="text"):
    text = copy_selection()
    if not text:
        return

    try:
        prompt_with_selection = text.split("$$")
        if len(prompt_with_selection) > 1:
            prompt, selected_text = prompt_with_selection[1], prompt_with_selection[0]
        else:
            prompt, selected_text = "", text
    except Exception as e:
        print(f"Error parsing prompt: {e}")
        prompt, selected_text = "", text
    
    print("Prompt:", prompt)
    print("Selected text:", selected_text)
    fix_text(selected_text, prompt, response_type)

def on_f8():
    fix_selection()

def on_f9():
    fix_selection_with_prompt()

def on_f10():
    fix_selection_with_prompt("Code")

if __name__ == "__main__":
    with keyboard.GlobalHotKeys({"<100>": on_f8, "<101>": on_f9, "<109>": on_f10}) as h:
        print("Waiting for key presses now")
        h.join()

# Example Usage on macOS
# 1. Assign the script to run in the background.
# 2. Highlight the text you want to fix.
# 3. Press F8 to fix text directly, F9 to fix with a custom prompt, or F10 for code-related corrections.
# 4. The corrected text will be automatically pasted back in place of the original text.
