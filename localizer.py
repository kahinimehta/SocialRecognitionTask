from psychopy import visual, core, event
import os, random, time
import csv
from datetime import datetime

# =========================
#  SETUP
# =========================
# Global variable to store input method preference (set before window creation)
USE_TOUCH_SCREEN = False

def safe_window_close(window):
    """Safely close a window, checking if it's still valid to prevent NoneType errors"""
    try:
        if window is not None:
            # Check if window has a backend and it's not None
            if hasattr(window, 'backend') and window.backend is not None:
                window.close()
            elif hasattr(window, 'close'):
                # Try to close anyway, but catch any errors
                try:
                    window.close()
                except (AttributeError, RuntimeError, Exception):
                    pass  # Window already closed or backend is None
    except (AttributeError, RuntimeError, Exception):
        pass  # Window already dereferenced or closed

def get_input_method():
    """Ask user whether they're using touch screen (1) or click screen (2)"""
    global USE_TOUCH_SCREEN
    
    # Create temporary window - handle partial initialization
    temp_win = None
    print ("temp_win created")
    try:
        # Use explicit size (never use size=None on Surface Pro/touchscreen mode)
        temp_win = visual.Window(size=(1280, 720), color='white', units='height', fullscr=False)
        print ("temp_win created")
        # Ensure window is fully initialized - draw something first to initialize OpenGL context
        dummy = visual.TextStim(temp_win, text='', color='white', pos=(0, 0))
        dummy.draw()
        temp_win.flip()
        core.wait(0.2)
        
        prompt_text = visual.TextStim(
            temp_win,
            text="What input method are you using?\n\n"
                 "Click 1 for TOUCH SCREEN\n"
                 "Click 2 for CLICK/MOUSE",
            color='black',
            height=0.06,
            pos=(0, 0.2),
            wrapWidth=1.4
        )
        
        # Create button 1 (TOUCH SCREEN) - convert all values to Python native types
        btn1_w = float(0.6)
        btn1_h = float(0.25)
        btn1_x = float(-0.3)
        btn1_y = float(-0.1)
        button1 = visual.Rect(
            temp_win, 
            width=btn1_w, 
            height=btn1_h, 
            fillColor='lightgreen', 
            lineColor='black', 
            pos=(btn1_x, btn1_y)
        )
        button1_text = visual.TextStim(temp_win, text="1\nTOUCH SCREEN", color='black', height=0.06, pos=(btn1_x, btn1_y))
        
        # Create button 2 (CLICK/MOUSE) - convert all values to Python native types
        btn2_w = float(0.6)
        btn2_h = float(0.25)
        btn2_x = float(0.3)
        btn2_y = float(-0.1)
        button2 = visual.Rect(
            temp_win, 
            width=btn2_w, 
            height=btn2_h, 
            fillColor='lightblue', 
            lineColor='black', 
            pos=(btn2_x, btn2_y)
        )
        button2_text = visual.TextStim(temp_win, text="2\nCLICK/MOUSE", color='black', height=0.06, pos=(btn2_x, btn2_y))
        
        mouse_temp = event.Mouse(win=temp_win)
        mouse_temp.setVisible(True)
        
        def draw_selection_screen():
            prompt_text.draw()
            button1.draw()
            button1_text.draw()
            button2.draw()
            button2_text.draw()
            temp_win.flip()
        
        draw_selection_screen()
        event.clearEvents()
        selected = None
        prev_mouse_buttons = [False, False, False]
        
        while selected is None:
            try:
                mouse_buttons = mouse_temp.getPressed()
                mouse_pos = mouse_temp.getPos()
                
                # Convert to floats to handle numpy arrays
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                hit_margin = 0.02
                
                # Check button 1
                button1_x, button1_y = -0.3, -0.1
                button1_width, button1_height = 0.6, 0.25
                on_button1 = (button1_x - button1_width/2 - hit_margin <= mouse_x <= button1_x + button1_width/2 + hit_margin and
                             button1_y - button1_height/2 - hit_margin <= mouse_y <= button1_y + button1_height/2 + hit_margin)
                
                # Check button 2
                button2_x, button2_y = 0.3, -0.1
                button2_width, button2_height = 0.6, 0.25
                on_button2 = (button2_x - button2_width/2 - hit_margin <= mouse_x <= button2_x + button2_width/2 + hit_margin and
                             button2_y - button2_height/2 - hit_margin <= mouse_y <= button2_y + button2_height/2 + hit_margin)
                
                # Check for button release (click completed)
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_button1:
                        USE_TOUCH_SCREEN = True
                        selected = 'touch'
                        button1.fillColor = 'green'
                        draw_selection_screen()
                        core.wait(0.3)
                        break
                    elif on_button2:
                        USE_TOUCH_SCREEN = False
                        selected = 'click'
                        button2.fillColor = 'blue'
                        draw_selection_screen()
                        core.wait(0.3)
                        break
                
                # For touch screens, check for press
                if mouse_buttons[0] and not prev_mouse_buttons[0]:
                    if on_button1:
                        USE_TOUCH_SCREEN = True
                        selected = 'touch'
                        button1.fillColor = 'green'
                        draw_selection_screen()
                        core.wait(0.3)
                        break
                    elif on_button2:
                        USE_TOUCH_SCREEN = False
                        selected = 'click'
                        button2.fillColor = 'blue'
                        draw_selection_screen()
                        core.wait(0.3)
                        break
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except Exception as e:
                pass
            
            # Safe event.getKeys() handling - ensure keys is never empty array issue
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:  # Check keys is not empty first
                    return None  # Signal to exit - window will be closed in finally
            except (AttributeError, Exception):
                pass  # Ignore event errors
            
            core.wait(0.01)
        
        # Show confirmation
        confirm_text = visual.TextStim(
            temp_win,
            text=f"Input method set to: {'TOUCH SCREEN' if USE_TOUCH_SCREEN else 'CLICK/MOUSE'}",
            color='black',
            height=0.06,
            pos=(0, 0),
            wrapWidth=1.4
        )
        
        # Create continue button for temp window - use width/height with explicit floats
        cont_w = float(0.3)
        cont_h = float(0.1)
        cont_x = float(0.0)
        cont_y = float(-0.3)
        continue_button = visual.Rect(temp_win, width=cont_w, height=cont_h, fillColor='lightblue', lineColor='black', pos=(cont_x, cont_y))
        continue_text = visual.TextStim(temp_win, text="CONTINUE", color='black', height=0.05, pos=(cont_x, cont_y))
        
        clicked = False
        prev_mouse_buttons_cont = [False, False, False]
        
        while not clicked:
            confirm_text.draw()
            continue_button.draw()
            continue_text.draw()
            temp_win.flip()
            
            try:
                mouse_buttons = mouse_temp.getPressed()
                mouse_pos = mouse_temp.getPos()
                
                # Convert to floats to handle numpy arrays - ensure all values are Python floats
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x = float(mouse_pos[0])
                        mouse_y = float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                # Get button position and dimensions as Python floats - ensure pos is always (x, y) tuple
                try:
                    button_pos = continue_button.pos
                    # Ensure pos is always a length-2 tuple, never empty
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x = float(button_pos[0])
                        button_y = float(button_pos[1])
                    else:
                        # Fallback: ensure we always have valid (x, y)
                        button_x, button_y = 0.0, -0.3
                        continue_button.pos = (button_x, button_y)  # Fix if broken
                except (TypeError, ValueError, IndexError):
                    button_x, button_y = 0.0, -0.3
                    continue_button.pos = (button_x, button_y)  # Fix if broken
                
                try:
                    button_width = float(continue_button.width) if hasattr(continue_button.width, '__float__') else 0.3
                    button_height = float(continue_button.height) if hasattr(continue_button.height, '__float__') else 0.1
                    # Ensure size is always valid
                    if button_width <= 0 or button_height <= 0:
                        button_width, button_height = 0.3, 0.1
                except (TypeError, ValueError):
                    button_width, button_height = 0.3, 0.1
                
                hit_margin = 0.02
                
                # Check if mouse is on button
                on_button = (button_x - button_width/2 - hit_margin <= mouse_x <= button_x + button_width/2 + hit_margin and
                            button_y - button_height/2 - hit_margin <= mouse_y <= button_y + button_height/2 + hit_margin)
                
                # Check for button release (click completed)
                if prev_mouse_buttons_cont[0] and not mouse_buttons[0]:
                    if on_button:
                        clicked = True
                        break
                
                # For touch screens, check for press
                if mouse_buttons[0] and not prev_mouse_buttons_cont[0]:
                    if on_button:
                        clicked = True
                        break
                
                prev_mouse_buttons_cont = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except Exception as e:
                pass
            
            # Safe event.getKeys() handling - ensure keys is never empty array issue
            try:
                keys = event.getKeys(keyList=['space', 'escape'])
                if keys:  # Check keys is not empty first
                    if 'space' in keys:
                        clicked = True
                        break
                    elif 'escape' in keys:
                        return None  # Signal to exit
            except (AttributeError, Exception):
                pass  # Ignore event errors
            core.wait(0.01)
        
        mouse_temp.setVisible(False)
        
        # Small delay before closing
        time.sleep(0.1)
        
        return USE_TOUCH_SCREEN
    
    finally:
        # Close temp window exactly once in finally block
        if temp_win is not None:
            try:
                temp_win.close()
            except Exception:
                pass
        time.sleep(0.5)  # Delay after closing before creating new window

# =========================
#  STIMULI SETUP (Module-level constants)
# =========================
STIMULI_DIR = "STIMULI"

# Category mapping: each category has 10 objects, numbered sequentially
CATEGORY_MAPPING = {
    "BIG_ANIMAL": (1, 10),      # 001-010
    "BIG_OBJECT": (11, 20),     # 011-020
    "BIRD": (21, 30),           # 021-030
    "FOOD": (31, 40),           # 031-040
    "FRUIT": (41, 50),          # 041-050
    "INSECT": (51, 60),         # 051-060
    "SMALL_ANIMAL": (61, 70),   # 061-070
    "SMALL_OBJECT": (71, 80),   # 071-080
    "VEGETABLE": (81, 90),      # 081-090
    "VEHICLE": (91, 100),       # 091-100
}

# Ask for input method first
result = get_input_method()
if result is None:
    core.quit()

def get_category_for_stimulus(stimulus_num):
    """Get the category name for a given stimulus number"""
    for category, (start, end) in CATEGORY_MAPPING.items():
        if start <= stimulus_num <= end:
            return category
    return None

def category_to_question(category_name):
    """Convert category folder name to question text"""
    # Convert BIG_ANIMAL -> "big animal", etc.
    words = category_name.lower().split('_')
    category_text = ' '.join(words)
    
    # Check if category starts with a vowel sound
    vowels = ['a', 'e', 'i', 'o', 'u']
    article = "an" if category_text[0] in vowels else "a"
    
    return f"Was the last object {article} {category_text}?"

def get_log_directory():
    """Get the directory for log files based on input method"""
    if USE_TOUCH_SCREEN:
        log_dir = "../LOG_FILES"
        # Create directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir
    else:
        return "."  # Current directory for click/mouse

def is_test_participant(participant_id):
    """Check if participant ID contains 'test' (case-insensitive)"""
    if participant_id is None:
        return False
    return "test" in participant_id.lower()

def load_all_stimuli():
    """Load all 100 Image files from STIMULI directory"""
    stimuli_list = []
    
    for category in CATEGORY_MAPPING.keys():
        category_dir = os.path.join(STIMULI_DIR, category)
        if os.path.exists(category_dir):
            # List all object folders
            object_folders = [f for f in os.listdir(category_dir) 
                             if os.path.isdir(os.path.join(category_dir, f))]
            
            for obj_folder in sorted(object_folders):
                obj_path = os.path.join(category_dir, obj_folder)
                # Look for Image_XXX.jpg files
                for filename in os.listdir(obj_path):
                    if filename.startswith("Image_") and filename.endswith(".jpg"):
                        # Extract stimulus number from filename (e.g., Image_001.jpg -> 1)
                        try:
                            stimulus_num = int(filename.split("_")[1].split(".")[0])
                            full_path = os.path.join(obj_path, filename)
                            if os.path.exists(full_path):
                                stimuli_list.append({
                                    'path': full_path,
                                    'number': stimulus_num,
                                    'category': category,
                                    'object_name': obj_folder
                                })
                        except (ValueError, IndexError):
                            continue
    
    # Sort by stimulus number to ensure we have all 100
    stimuli_list.sort(key=lambda x: x['number'])
    return stimuli_list

def get_participant_id():
    """Get participant ID from PsychoPy screen input with on-screen keyboard for touch screens"""
    input_id = ""
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)

    id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.06, wrapWidth=1.4, pos=(0, 0.3))
    input_display = visual.TextStim(win, text="", color='black', height=0.08, pos=(0, 0.1))

    if USE_TOUCH_SCREEN:
        # On-screen keyboard layout
        keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        ]
        
        keyboard_buttons = []
        start_y = -0.1
        row_spacing = 0.12
        
        for row_idx, row in enumerate(keyboard_rows):
            row_buttons = []
            num_keys = len(row)
            start_x = -(num_keys - 1) * 0.08 / 2
            
            for col_idx, key in enumerate(row):
                x_pos = start_x + col_idx * 0.08
                y_pos = start_y - row_idx * row_spacing
                
                button = visual.Rect(win, width=0.07, height=0.08, fillColor='lightgray', 
                                    lineColor='black', pos=(x_pos, y_pos))
                text = visual.TextStim(win, text=key, color='black', height=0.04, pos=(x_pos, y_pos))
                row_buttons.append((button, text, key, x_pos, y_pos))
            
            keyboard_buttons.append(row_buttons)
        
        # Special buttons
        del_button = visual.Rect(win, width=0.15, height=0.08, fillColor='lightcoral', 
                                lineColor='black', pos=(-0.3, start_y - 4 * row_spacing))
        del_text = visual.TextStim(win, text="DEL", color='black', height=0.04, pos=(-0.3, start_y - 4 * row_spacing))
        
        space_button = visual.Rect(win, width=0.3, height=0.08, fillColor='lightgray', 
                                  lineColor='black', pos=(0, start_y - 4 * row_spacing))
        space_text = visual.TextStim(win, text="SPACE", color='black', height=0.04, pos=(0, start_y - 4 * row_spacing))
        
        enter_button = visual.Rect(win, width=0.15, height=0.08, fillColor='lightgreen', 
                                   lineColor='black', pos=(0.3, start_y - 4 * row_spacing))
        enter_text = visual.TextStim(win, text="ENTER", color='black', height=0.04, pos=(0.3, start_y - 4 * row_spacing))

    def redraw():
        id_prompt.draw()
        input_display.text = input_id if input_id else "_"
        input_display.draw()
        
        if USE_TOUCH_SCREEN:
            for row in keyboard_buttons:
                for button, text, _, _, _ in row:
                    button.draw()
                    text.draw()
            del_button.draw()
            del_text.draw()
            space_button.draw()
            space_text.draw()
            enter_button.draw()
            enter_text.draw()
        
        win.flip()

    redraw()
    event.clearEvents()

    while True:
        if USE_TOUCH_SCREEN:
            mouse_buttons = mouse.getPressed()
            if mouse_buttons[0]:
                mouse_pos = mouse.getPos()
                try:
                    mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                hit_margin = 0.02
                clicked = False
                
                # Check keyboard buttons
                for row in keyboard_buttons:
                    for button, text, key, x_pos, y_pos in row:
                        if (x_pos - 0.035 - hit_margin <= mouse_x <= x_pos + 0.035 + hit_margin and
                            y_pos - 0.04 - hit_margin <= mouse_y <= y_pos + 0.04 + hit_margin):
                            input_id += key
                            button.fillColor = 'yellow'
                            redraw()
                            core.wait(0.2)
                            button.fillColor = 'lightgray'
                            clicked = True
                            break
                    if clicked:
                        break
                
                if not clicked:
                    # Check DEL button
                    if (-0.3 - 0.075 - hit_margin <= mouse_x <= -0.3 + 0.075 + hit_margin and
                        (start_y - 4 * row_spacing) - 0.04 - hit_margin <= mouse_y <= (start_y - 4 * row_spacing) + 0.04 + hit_margin):
                        input_id = input_id[:-1] if input_id else ""
                        del_button.fillColor = 'red'
                        redraw()
                        core.wait(0.2)
                        del_button.fillColor = 'lightcoral'
                    
                    # Check SPACE button
                    elif (-0.15 - hit_margin <= mouse_x <= 0.15 + hit_margin and
                          (start_y - 4 * row_spacing) - 0.04 - hit_margin <= mouse_y <= (start_y - 4 * row_spacing) + 0.04 + hit_margin):
                        input_id += " "
                        space_button.fillColor = 'yellow'
                        redraw()
                        core.wait(0.2)
                        space_button.fillColor = 'lightgray'
                    
                    # Check ENTER button
                    elif (0.3 - 0.075 - hit_margin <= mouse_x <= 0.3 + 0.075 + hit_margin and
                          (start_y - 4 * row_spacing) - 0.04 - hit_margin <= mouse_y <= (start_y - 4 * row_spacing) + 0.04 + hit_margin):
                        if input_id.strip():
                            mouse.setVisible(False)
                            event.clearEvents()
                            return input_id.strip()
                
                core.wait(0.1)  # Prevent multiple clicks
        else:
            # Standard keyboard input for click mode - safe handling of empty keys
            try:
                keys = event.getKeys(keyList=None, timeStamped=False)
                if keys:  # Only process if keys is not empty
                    for key in keys:
                        if key == 'return' or key == 'enter':
                            if input_id.strip():
                                mouse.setVisible(False)
                                event.clearEvents()
                                return input_id.strip()
                        elif key == 'backspace':
                            input_id = input_id[:-1] if input_id else ""
                            input_display.text = input_id if input_id else "_"
                            redraw()
                        elif len(key) == 1:
                            input_id += key
                            input_display.text = input_id if input_id else "_"
                            redraw()
                        elif key == 'escape':
                            core.quit()
            except (AttributeError, Exception):
                pass  # Ignore event errors
        
        core.wait(0.01)

def wait_for_button(button_text="CONTINUE", additional_stimuli=None):
    """Wait for button click/touch
    
    Args:
        button_text: Text to display on button
        additional_stimuli: List of visual stimuli to draw before the button (e.g., instructions)
    """
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    continue_button = visual.Rect(
        win,
        width=0.3,
        height=0.1,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.45)
    )
    continue_text = visual.TextStim(
        win,
        text=button_text,
        color='black',
        height=0.05,
        pos=(0, -0.45)
    )
    
    def draw_screen():
        # Draw additional stimuli first (e.g., instructions)
        if additional_stimuli:
            for stim in additional_stimuli:
                stim.draw()
        continue_button.draw()
        continue_text.draw()
        win.flip()
    
    draw_screen()
    
    clicked = False
    prev_mouse_buttons = [False, False, False]
    last_hover_state = None
    
    while not clicked:
        try:
            mouse_buttons = mouse.getPressed()
            mouse_pos = mouse.getPos()
            
            try:
                if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                    mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                else:
                    mouse_x, mouse_y = 0.0, 0.0
            except (TypeError, ValueError):
                mouse_x, mouse_y = 0.0, 0.0
            
            # Get button position - ensure pos is always (x, y) tuple, never empty
            try:
                button_pos = continue_button.pos
                if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                    button_x = float(button_pos[0])
                    button_y = float(button_pos[1])
                else:
                    # Fallback: ensure we always have valid (x, y)
                    button_x, button_y = 0.0, -0.45
                    continue_button.pos = (button_x, button_y)  # Fix if broken
            except (TypeError, ValueError, IndexError):
                button_x, button_y = 0.0, -0.45
                continue_button.pos = (button_x, button_y)  # Fix if broken
            
            # Get button dimensions - ensure they're always valid
            try:
                button_width = float(continue_button.width)
                button_height = float(continue_button.height)
                # Ensure size is always valid (positive)
                if button_width <= 0 or button_height <= 0:
                    button_width, button_height = 0.3, 0.1
            except (TypeError, ValueError):
                button_width, button_height = 0.3, 0.1
            
            hit_margin = 0.02 if USE_TOUCH_SCREEN else 0.0
            
            on_button = (button_x - button_width/2 - hit_margin <= mouse_x <= button_x + button_width/2 + hit_margin and
                        button_y - button_height/2 - hit_margin <= mouse_y <= button_y + button_height/2 + hit_margin)
            
            if prev_mouse_buttons[0] and not mouse_buttons[0]:
                if on_button:
                    continue_button.fillColor = 'lightgreen'
                    draw_screen()
                    core.wait(0.2)
                    clicked = True
                    break
            
            if mouse_buttons[0] and on_button and not prev_mouse_buttons[0]:
                if USE_TOUCH_SCREEN:
                    continue_button.fillColor = 'lightgreen'
                    draw_screen()
                    core.wait(0.2)
                    clicked = True
                    break
            
            if not USE_TOUCH_SCREEN:
                if on_button != last_hover_state:
                    if on_button:
                        continue_button.fillColor = 'lightcyan'
                    else:
                        continue_button.fillColor = 'lightblue'
                    draw_screen()
                    last_hover_state = on_button
            
            prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
        except (AttributeError, Exception):
            pass
        
        # Safe event.getKeys() handling - ensure keys is never empty array issue
        try:
            keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
            if keys:  # Check keys is not empty first
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
        except (AttributeError, Exception):
            pass  # Ignore event errors
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()

def ask_category_question(category_name, last_object_name, timeout=10.0):
    """Ask category question and return (answer, timed_out, response_time) tuple
    
    Args:
        category_name: Category name for the question
        last_object_name: Name of the last object shown
        timeout: Timeout in seconds (default 10.0)
    
    Returns:
        tuple: (answer: bool or None, timed_out: bool, response_time: float)
    """
    question_text = category_to_question(category_name)
    
    # Create question display
    question_stim = visual.TextStim(
        win,
        text=question_text,
        color='black',
        height=0.06,
        pos=(0, 0.2),
        wrapWidth=1.4
    )
    
    # Create YES and NO buttons
    yes_button = visual.Rect(
        win,
        width=0.25,
        height=0.1,
        fillColor='lightgreen',
        lineColor='black',
        pos=(-0.3, -0.2)
    )
    yes_text = visual.TextStim(
        win,
        text="YES",
        color='black',
        height=0.05,
        pos=(-0.3, -0.2)
    )
    
    no_button = visual.Rect(
        win,
        width=0.25,
        height=0.1,
        fillColor='lightcoral',
        lineColor='black',
        pos=(0.3, -0.2)
    )
    no_text = visual.TextStim(
        win,
        text="NO",
        color='black',
        height=0.05,
        pos=(0.3, -0.2)
    )
    
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    def draw_question():
        question_stim.draw()
        yes_button.draw()
        yes_text.draw()
        no_button.draw()
        no_text.draw()
        win.flip()
    
    draw_question()
    
    answered = False
    answer = None
    timed_out = False
    prev_mouse_buttons = [False, False, False]
    clock = core.Clock()
    clock.reset()
    response_time = None
    
    while not answered:
        # Check for timeout
        elapsed_time = clock.getTime()
        if elapsed_time >= timeout:
            timed_out = True
            response_time = timeout  # Record timeout as response time
            answered = True
            break
        try:
            mouse_buttons = mouse.getPressed()
            mouse_pos = mouse.getPos()
            
            try:
                if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                    mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                else:
                    mouse_x, mouse_y = 0.0, 0.0
            except (TypeError, ValueError):
                mouse_x, mouse_y = 0.0, 0.0
            
            hit_margin = 0.02 if USE_TOUCH_SCREEN else 0.0
            
            # Check YES button
            yes_x, yes_y = -0.3, -0.2
            yes_width, yes_height = 0.25, 0.1
            on_yes = (yes_x - yes_width/2 - hit_margin <= mouse_x <= yes_x + yes_width/2 + hit_margin and
                     yes_y - yes_height/2 - hit_margin <= mouse_y <= yes_y + yes_height/2 + hit_margin)
            
            # Check NO button
            no_x, no_y = 0.3, -0.2
            no_width, no_height = 0.25, 0.1
            on_no = (no_x - no_width/2 - hit_margin <= mouse_x <= no_x + no_width/2 + hit_margin and
                    no_y - no_height/2 - hit_margin <= mouse_y <= no_y + no_height/2 + hit_margin)
            
            if prev_mouse_buttons[0] and not mouse_buttons[0]:
                if on_yes:
                    answer = True
                    response_time = clock.getTime()
                    yes_button.fillColor = 'green'
                    draw_question()
                    core.wait(0.3)
                    answered = True
                    break
                elif on_no:
                    answer = False
                    response_time = clock.getTime()
                    no_button.fillColor = 'red'
                    draw_question()
                    core.wait(0.3)
                    answered = True
                    break
            
            if mouse_buttons[0] and not prev_mouse_buttons[0]:
                if USE_TOUCH_SCREEN:
                    if on_yes:
                        answer = True
                        response_time = clock.getTime()
                        yes_button.fillColor = 'green'
                        draw_question()
                        core.wait(0.3)
                        answered = True
                        break
                    elif on_no:
                        answer = False
                        response_time = clock.getTime()
                        no_button.fillColor = 'red'
                        draw_question()
                        core.wait(0.3)
                        answered = True
                        break
            
            prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
        except (AttributeError, Exception):
            pass
        
        # Safe event.getKeys() handling - ensure keys is never empty array issue
        try:
            keys = event.getKeys(keyList=['y', 'n', 'escape'], timeStamped=False)
            if keys:  # Check keys is not empty first
                if 'y' in keys:
                    answer = True
                    answered = True
                    break
                elif 'n' in keys:
                    answer = False
                    answered = True
                    break
                elif 'escape' in keys:
                    core.quit()
        except (AttributeError, Exception):
            pass  # Ignore event errors
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()
    
    # Show timeout message if timed out
    if timed_out:
        timeout_message = visual.TextStim(
            win,
            text="Time's up! We've moved on to the next image.",
            color='red',
            height=0.06,
            pos=(0, 0),
            wrapWidth=1.4
        )
        timeout_message.draw()
        win.flip()
        core.wait(2.0)  # Show message for 2 seconds
    
    return (answer, timed_out, response_time)

# Create main window with appropriate settings - use try/finally pattern
win = None
try:
    time.sleep(0.5)  # Use time.sleep instead of core.wait since we don't have a window yet
    
    # Create window in windowed mode (not fullscreen)
    # Use explicit size (never use size=None on Surface Pro/touchscreen mode)
    try:
        win = visual.Window(size=(1280, 720), color='white', units='height', fullscr=False)
    except Exception as e:
        # If window creation fails, try with alternative explicit size
        print(f"Warning: Could not create window with size (1280, 720) ({e})")
        print("Trying with alternative size (1024, 768)...")
        time.sleep(0.3)  # Additional delay
        win = visual.Window(size=(1024, 768), color='white', units='height', fullscr=False)
    
    # =========================
    #  MAIN EXPERIMENT
    # =========================

    # Get participant ID
    participant_id = get_participant_id()

    # Load all stimuli
    print("Loading stimuli...")
    all_stimuli = load_all_stimuli()

    if len(all_stimuli) != 100:
        print(f"Warning: Expected 100 stimuli, found {len(all_stimuli)}")

    # Randomize order
    random.shuffle(all_stimuli)

    # Show instructions
    instructions = visual.TextStim(
        win,
        text="LOCALIZER TASK\n\n"
             "You will see 100 images one at a time.\n\n"
             "Every few images, you will be asked a question\n"
             "about the previous image.\n\n"
             "Please pay attention to each image.",
        color='black',
        height=0.05,
        pos=(0, 0),
        wrapWidth=1.4
    )

    instructions.draw()
    win.flip()
    wait_for_button("BEGIN", additional_stimuli=[instructions])

    # Data storage
    localizer_data = []
    csv_file = None
    csv_writer = None
    csv_file_path = None
    fieldnames = None
    csv_initialized = False
    
    # Initialize CSV file before first image
    if not is_test_participant(participant_id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = get_log_directory()
        csv_file_path = os.path.join(log_dir, f"localizer_{participant_id}_{timestamp}.csv")
        csv_file = open(csv_file_path, 'w', newline='')
        # Define fieldnames for all images (will include question fields for every 10th)
        fieldnames = [
            'participant_id', 'trial', 'stimulus_number', 'object_name', 'category',
            'presentation_time', 'is_question_trial', 'question_category', 'question_text',
            'answer', 'correct_answer', 'correct', 'timed_out', 'response_time'
        ]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_file.flush()
        csv_initialized = True
        print(f"✓ Created localizer CSV file: {csv_file_path}")

    # Show images
    for idx, stimulus in enumerate(all_stimuli, 1):
        # Record presentation time
        presentation_time = datetime.now()
        presentation_timestamp = presentation_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Load and display image
        try:
            img = visual.ImageStim(win, image=stimulus['path'], size=(0.8, 0.8))
            img.draw()
            win.flip()
            
            # Show image for exactly 1 second
            core.wait(1.0)
            
            # Check if this is the 10th image (or every 10th after the first)
            is_question_trial = (idx % 10 == 0)
            
            if is_question_trial:
                # Ask category question about the image we just showed (the 10th, 20th, 30th, etc.)
                current_stimulus = stimulus
                correct_category = current_stimulus['category']
                
                # Ask the question about this image's category
                answer, timed_out, response_time = ask_category_question(correct_category, current_stimulus['object_name'])
                
                # The correct answer is always True since we're asking about the category this image belongs to
                correct_answer = True
                
                # Calculate correct only if not timed out
                is_correct = (answer == correct_answer) if not timed_out else None
                
                # Record data with question fields
                trial_data = {
                    'participant_id': participant_id,
                    'trial': idx,
                    'stimulus_number': current_stimulus['number'],
                    'object_name': current_stimulus['object_name'],
                    'category': current_stimulus['category'],
                    'presentation_time': presentation_timestamp,
                    'is_question_trial': True,
                    'question_category': correct_category,
                    'question_text': category_to_question(correct_category),
                    'answer': answer if not timed_out else 'TIMEOUT',
                    'correct_answer': correct_answer,
                    'correct': is_correct,
                    'timed_out': timed_out,
                    'response_time': response_time if response_time is not None else None
                }
            else:
                # Record data for non-question trials
                trial_data = {
                    'participant_id': participant_id,
                    'trial': idx,
                    'stimulus_number': stimulus['number'],
                    'object_name': stimulus['object_name'],
                    'category': stimulus['category'],
                    'presentation_time': presentation_timestamp,
                    'is_question_trial': False,
                    'question_category': None,
                    'question_text': None,
                    'answer': None,
                    'correct_answer': None,
                    'correct': None,
                    'timed_out': None,
                    'response_time': None
                }
            
            localizer_data.append(trial_data)
            
            # Write current trial to CSV
            if csv_writer is not None:
                csv_writer.writerow(trial_data)
                csv_file.flush()  # Ensure data is written immediately
            
            # Brief pause before next image
            core.wait(0.5)
                
        except Exception as e:
            print(f"Error loading image {stimulus['path']}: {e}")
            continue

    # Show completion message
    completion_text = visual.TextStim(
        win,
        text="LOCALIZER TASK COMPLETE!\n\n"
             "Thank you for your participation.",
        color='black',
        height=0.06,
        pos=(0, 0),
        wrapWidth=1.4
    )

    completion_text.draw()
    win.flip()
    wait_for_button("EXIT", additional_stimuli=[completion_text])

    # Close CSV file if it was opened
    if csv_file is not None:
        csv_file.close()
        if csv_file_path:
            print(f"✓ Closed localizer CSV file: {csv_file_path}")
        else:
            print(f"✓ Closed localizer CSV file")

    # Save data (backup - in case CSV wasn't created incrementally)
    if not is_test_participant(participant_id) and not csv_initialized:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = get_log_directory()
        output_file = os.path.join(log_dir, f"localizer_{participant_id}_{timestamp}.csv")
        
        if localizer_data:
            fieldnames = list(localizer_data[0].keys())
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(localizer_data)
            
            print(f"✓ Saved localizer data to {output_file}")
        else:
            print("⚠ No data to save")
    elif is_test_participant(participant_id):
        print(f"⚠ Test participant detected - skipping file save")

finally:
    # Close window exactly once in finally block
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    core.quit()
