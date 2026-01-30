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
    try:
        # Use height units for fullscreen compatibility
        temp_win = visual.Window(
            size=(1280, 720),
            color='white',
            units='height',
            fullscr=True,
            allowGUI=True
        )
        temp_win.flip()
        
        prompt_text = visual.TextStim(
            temp_win,
            text="What input method are you using?\n\n"
                 "Touch or click the button below:",
            color='black',
            height=30/720,
            pos=(0, 200/720),
            wrapWidth=1000/720,
            units='height'
        )
        
        # Create button 1 (TOUCH SCREEN) - height units
        button1 = visual.Rect(
            temp_win,
            width=520/720,
            height=180/720,
            fillColor='lightgreen',
            lineColor='black',
            pos=(-320/720, -80/720),
            lineWidth=1/720,
            units='height'
        )
        button1_text = visual.TextStim(
            temp_win, 
            text="TOUCH SCREEN\n(Tap with finger)", 
            color='black', 
            height=24/720, 
            pos=(-320/720, -80/720),
            units='height'
        )
        
        # Create button 2 (MOUSE/TRACKPAD) - height units
        button2 = visual.Rect(
            temp_win,
            width=520/720,
            height=180/720,
            fillColor='lightblue',
            lineColor='black',
            pos=(320/720, -80/720),
            lineWidth=1/720,
            units='height'
        )
        button2_text = visual.TextStim(
            temp_win, 
            text="MOUSE/TRACKPAD\n(Click or tap)", 
            color='black', 
            height=24/720, 
            pos=(320/720, -80/720),
            units='height'
        )
        
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
        
        # POSITION-CHANGE DETECTION: Store initial mouse position
        mouserec = mouse_temp.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        minRT = 0.05  # Minimum response time
        clock = core.Clock()
        clock.reset()
        
        while selected is None:
            try:
                mouseloc = mouse_temp.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                t = clock.getTime()
                event.clearEvents()
                
                # Check if mouse position has changed (touch moved)
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    draw_selection_screen()
                else:
                    # Position has changed - check if touch is within any button
                    # Check button 1
                    try:
                        if button1.contains(mouseloc):
                            if t > minRT:
                                USE_TOUCH_SCREEN = True
                                selected = 'touch'
                                button1.fillColor = 'green'
                                draw_selection_screen()
                                core.wait(0.05)
                                break
                            else:
                                mouserec = mouse_temp.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    except:
                        # Fallback to manual calculation
                        hit_margin = 150
                        button1_x, button1_y = -320, -80
                        button1_width, button1_height = 520, 180
                        if (button1_x - button1_width/2 - hit_margin <= mouseloc_x <= button1_x + button1_width/2 + hit_margin and
                            button1_y - button1_height/2 - hit_margin <= mouseloc_y <= button1_y + button1_height/2 + hit_margin):
                            if t > minRT:
                                USE_TOUCH_SCREEN = True
                                selected = 'touch'
                                button1.fillColor = 'green'
                                draw_selection_screen()
                                core.wait(0.05)
                                break
                            else:
                                mouserec = mouse_temp.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    
                    # Check button 2
                    if selected is None:
                        try:
                            if button2.contains(mouseloc):
                                if t > minRT:
                                    USE_TOUCH_SCREEN = False
                                    selected = 'click'
                                    button2.fillColor = 'blue'
                                    draw_selection_screen()
                                    core.wait(0.05)
                                    break
                                else:
                                    mouserec = mouse_temp.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                        except:
                            # Fallback to manual calculation
                            hit_margin = 150/720
                            button2_x, button2_y = 320/720, -80/720
                            button2_width, button2_height = 520/720, 180/720
                            if (button2_x - button2_width/2 - hit_margin <= mouseloc_x <= button2_x + button2_width/2 + hit_margin and
                                button2_y - button2_height/2 - hit_margin <= mouseloc_y <= button2_y + button2_height/2 + hit_margin):
                                if t > minRT:
                                    USE_TOUCH_SCREEN = False
                                    selected = 'click'
                                    button2.fillColor = 'blue'
                                    draw_selection_screen()
                                    core.wait(0.05)
                                    break
                                else:
                                    mouserec = mouse_temp.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
            except Exception as e:
                pass
            
            # Safe event.getKeys() handling - ensure keys is never empty array issue
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:  # Check keys is not empty first
                    return None  # Signal to exit - window will be closed in finally
            except (AttributeError, Exception):
                pass  # Ignore event errors
            
            # Reduced polling delay for faster touch response
            core.wait(0.001)  # Very fast polling
        
        # Show confirmation - use height units to match temp window
        confirm_text = visual.TextStim(
            temp_win,
            text=f"Input method set to:\n{'TOUCH SCREEN' if USE_TOUCH_SCREEN else 'CLICK/MOUSE'}",
            color='black',
            height=40/720,
            pos=(0, 100/720),
            wrapWidth=1000/720,
            units='height'
        )
        
        # Create continue button for temp window - use height units
        cont_w = 300/720
        cont_h = 80/720
        cont_x = 0
        cont_y = -150/720
        continue_button = visual.Rect(temp_win, width=cont_w, height=cont_h, fillColor='lightblue', lineColor='black', pos=(cont_x, cont_y), units='height')
        continue_text = visual.TextStim(temp_win, text="CONTINUE", color='black', height=30/720, pos=(cont_x, cont_y), units='height')
        
        clicked = False
        
        # POSITION-CHANGE DETECTION: Store initial mouse position
        mouserec_cont = mouse_temp.getPos()
        try:
            mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
        except:
            mouserec_cont_x, mouserec_cont_y = 0.0, 0.0
        
        minRT_cont = 0.05  # Minimum response time
        clock_cont = core.Clock()
        clock_cont.reset()
        
        while not clicked:
            confirm_text.draw()
            continue_button.draw()
            continue_text.draw()
            temp_win.flip()
            
            try:
                mouseloc_cont = mouse_temp.getPos()
                try:
                    mouseloc_cont_x, mouseloc_cont_y = float(mouseloc_cont[0]), float(mouseloc_cont[1])
                except:
                    mouseloc_cont_x, mouseloc_cont_y = 0.0, 0.0
                
                t_cont = clock_cont.getTime()
                
                # Check if mouse position has changed (touch moved)
                if mouseloc_cont_x == mouserec_cont_x and mouseloc_cont_y == mouserec_cont_y:
                    # Position hasn't changed, continue loop
                    pass
                else:
                    # Position has changed - check if touch is within button
                    try:
                        if continue_button.contains(mouseloc_cont):
                            if t_cont > minRT_cont:
                                clicked = True
                                break
                            else:
                                mouserec_cont = mouse_temp.getPos()
                                try:
                                    mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
                                except:
                                    mouserec_cont_x, mouserec_cont_y = mouseloc_cont_x, mouseloc_cont_y
                    except:
                        # Fallback to manual calculation
                        hit_margin = 50/720
                        button_x, button_y = 0.0, -150.0/720
                        button_width, button_height = 300/720, 80/720
                        if (button_x - button_width/2 - hit_margin <= mouseloc_cont_x <= button_x + button_width/2 + hit_margin and
                            button_y - button_height/2 - hit_margin <= mouseloc_cont_y <= button_y + button_height/2 + hit_margin):
                            if t_cont > minRT_cont:
                                clicked = True
                                break
                            else:
                                mouserec_cont = mouse_temp.getPos()
                                try:
                                    mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
                                except:
                                    mouserec_cont_x, mouserec_cont_y = mouseloc_cont_x, mouseloc_cont_y
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
            # Reduced polling delay for faster touch response
            core.wait(0.005)  # Faster polling for touch screens
        
        mouse_temp.setVisible(False)
        
        # Show a brief transition message before closing
        transition_text = visual.TextStim(
            temp_win,
            text="Loading...",
            color='black',
            height=50/720,
            pos=(0, 0),
            units='height'
        )
        transition_text.draw()
        temp_win.flip()
        
        # Minimal delay before closing for touch screens
        if USE_TOUCH_SCREEN:
            time.sleep(0.05)  # Very short delay for touch screens
        else:
            time.sleep(0.1)  # Slightly longer for mouse/trackpad
        
        return USE_TOUCH_SCREEN
    
    finally:
        # Close temp window exactly once in finally block
        if temp_win is not None:
            try:
                temp_win.close()
            except Exception:
                pass
        # Minimal delay - main window creation will happen immediately after
        time.sleep(0.05)  # Minimized delay for fastest transition

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
print("Getting input method...")
try:
    result = get_input_method()
    print(f"Input method result: {result}")
    print(f"Input method type: {type(result)}")
except Exception as e:
    print(f"ERROR in get_input_method(): {e}")
    import traceback
    traceback.print_exc()
    core.quit()
    exit(1)

if result is None:
    print("Input method selection cancelled. Exiting...")
    core.quit()
    exit(0)
print(f"Input method selected: {'TOUCH SCREEN' if result else 'MOUSE/TRACKPAD'}")

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
    print("Inside get_participant_id() - checking win...")
    if win is None:
        raise RuntimeError("win is None when get_participant_id() is called!")
    print(f"win is valid: {win}")
    
    input_id = ""
    try:
        mouse = event.Mouse(win=win)
        mouse.setVisible(True)
        print("Mouse created successfully")
    except Exception as e:
        print(f"Error creating mouse: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Adjust positions for touch screen to avoid overlap
    # Layout: prompt at top, input below, buttons below input, keyboard at bottom
    print("Creating text stimuli...")
    try:
        if USE_TOUCH_SCREEN:
            print("Creating touch screen text stimuli...")
            id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.045, wrapWidth=1.4, pos=(0, 0.35))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06, pos=(0, 0.25))
            print("input_display created")
        else:
            print("Creating mouse/trackpad text stimuli...")
            id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.045, wrapWidth=1.4, pos=(0, 0.3))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06, pos=(0, 0.1))
            print("input_display created")
    except Exception as e:
        print(f"ERROR creating text stimuli: {e}")
        import traceback
        traceback.print_exc()
        raise

    if USE_TOUCH_SCREEN:
        print("Creating keyboard buttons...")
        try:
            # On-screen keyboard layout (no number row)
            keyboard_rows = [
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
            ]
            
            keyboard_buttons = []
            start_y = -0.15  # Move keyboard lower to avoid overlap with buttons
            row_spacing = 0.12
            
            print(f"Creating {len(keyboard_rows)} keyboard rows...")
            for row_idx, row in enumerate(keyboard_rows):
                print(f"Creating row {row_idx} with {len(row)} keys...")
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
            
            print("Creating special buttons...")
            # Special buttons - arranged horizontally between input and keyboard
            button_y_pos = 0.05  # Position between input (0.25) and keyboard start (-0.15)
            backspace_button = visual.Rect(win, width=0.2, height=0.1, fillColor='lightcoral', 
                                          lineColor='black', lineWidth=2, pos=(-0.25, button_y_pos))
            backspace_text = visual.TextStim(win, text="BACKSPACE", color='black', height=0.025, pos=(-0.25, button_y_pos))
            
            continue_button = visual.Rect(win, width=0.3, height=0.1, fillColor='lightgreen', 
                                          lineColor='black', lineWidth=2, pos=(0.25, button_y_pos))
            continue_text = visual.TextStim(win, text="CONTINUE", color='black', height=0.025, pos=(0.25, button_y_pos))
            print("All keyboard buttons created successfully")
        except Exception as e:
            print(f"ERROR creating keyboard buttons: {e}")
            import traceback
            traceback.print_exc()
            raise

    def redraw():
        id_prompt.draw()
        input_display.text = input_id if input_id else "_"
        input_display.draw()
        
        if USE_TOUCH_SCREEN:
            for row in keyboard_buttons:
                for button, text, _, _, _ in row:
                    button.draw()
                    text.draw()
            backspace_button.draw()
            backspace_text.draw()
            continue_button.draw()
            continue_text.draw()
        
        win.flip()

    # Initial redraw to ensure buttons are visible
    redraw()
    event.clearEvents()
    
    # POSITION-CHANGE DETECTION: Store initial mouse position
    mouserec = mouse.getPos()
    try:
        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
    except:
        mouserec_x, mouserec_y = 0.0, 0.0
    
    minRT = 0.05  # Minimum response time (reduced for faster response)
    clock = core.Clock()
    clock.reset()
    
    while True:
        if USE_TOUCH_SCREEN:
            mouseloc = mouse.getPos()
            try:
                mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
            except:
                mouseloc_x, mouseloc_y = 0.0, 0.0
            
            t = clock.getTime()
            clicked = False
            
            # Check if mouse position has changed (touch moved)
            if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                # Position hasn't changed, just redraw
                redraw()
            else:
                # Position has changed - check if touch is within any button
                # Check keyboard buttons first
                for row in keyboard_buttons:
                    for button, text, key, x_pos, y_pos in row:
                        try:
                            if button.contains(mouseloc):
                                if t > minRT:  # Minimum time has passed
                                    input_id += key
                                    button.fillColor = 'yellow'
                                    redraw()
                                    core.wait(0.05)
                                    button.fillColor = 'lightgray'
                                    redraw()
                                    clicked = True
                                    mouserec = mouse.getPos()  # Update reference position
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                    clock.reset()  # Reset timer
                                    break
                                else:
                                    mouserec = mouse.getPos()  # Update reference position
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                        except:
                            # Fallback to manual calculation
                            hit_margin = 0.08
                            if (x_pos - 0.035 - hit_margin <= mouseloc_x <= x_pos + 0.035 + hit_margin and
                                y_pos - 0.04 - hit_margin <= mouseloc_y <= y_pos + 0.04 + hit_margin):
                                if t > minRT:
                                    input_id += key
                                    button.fillColor = 'yellow'
                                    redraw()
                                    core.wait(0.05)
                                    button.fillColor = 'lightgray'
                                    redraw()
                                    clicked = True
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                    clock.reset()
                                    break
                                else:
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    if clicked:
                        break
                
                if not clicked:
                    # Check BACKSPACE button
                    try:
                        if backspace_button.contains(mouseloc):
                            if t > minRT:
                                input_id = input_id[:-1] if input_id else ""
                                backspace_button.fillColor = 'red'
                                redraw()
                                core.wait(0.05)
                                backspace_button.fillColor = 'lightcoral'
                                redraw()
                                clicked = True
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                clock.reset()
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    except:
                        # Fallback to manual calculation
                        hit_margin = 0.08
                        backspace_x, backspace_y = -0.35, start_y + 0.2
                        backspace_width, backspace_height = 0.2, 0.1
                        if (backspace_x - backspace_width/2 - hit_margin <= mouseloc_x <= backspace_x + backspace_width/2 + hit_margin and
                            backspace_y - backspace_height/2 - hit_margin <= mouseloc_y <= backspace_y + backspace_height/2 + hit_margin):
                            if t > minRT:
                                input_id = input_id[:-1] if input_id else ""
                                backspace_button.fillColor = 'red'
                                redraw()
                                core.wait(0.05)
                                backspace_button.fillColor = 'lightcoral'
                                redraw()
                                clicked = True
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                clock.reset()
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    
                    # Check CONTINUE button
                    if not clicked:
                        try:
                            if continue_button.contains(mouseloc):
                                if t > minRT:
                                    if input_id.strip():
                                        mouse.setVisible(False)
                                        event.clearEvents()
                                        return input_id.strip()
                                    # If empty, show feedback
                                    continue_button.fillColor = 'darkgreen'
                                    redraw()
                                    core.wait(0.1)
                                    continue_button.fillColor = 'lightgreen'
                                    redraw()
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                    clock.reset()
                                else:
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                        except:
                            # Fallback to manual calculation
                            hit_margin = 0.08
                            continue_x, continue_y = 0.25, 0.12  # Match button_y_pos
                            continue_width, continue_height = 0.3, 0.1
                            if (continue_x - continue_width/2 - hit_margin <= mouseloc_x <= continue_x + continue_width/2 + hit_margin and
                                continue_y - continue_height/2 - hit_margin <= mouseloc_y <= continue_y + continue_height/2 + hit_margin):
                                if t > minRT:
                                    if input_id.strip():
                                        mouse.setVisible(False)
                                        event.clearEvents()
                                        return input_id.strip()
                                    continue_button.fillColor = 'darkgreen'
                                    redraw()
                                    core.wait(0.1)
                                    continue_button.fillColor = 'lightgreen'
                                    redraw()
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                                    clock.reset()
                                else:
                                    mouserec = mouse.getPos()
                                    try:
                                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                    except:
                                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
            
            # Redraw every frame
            redraw()
            event.clearEvents()
            core.wait(0.001)  # Very fast polling
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
    """Wait for button click/touch using position-change detection for touchscreens
    
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
        pos=(0, -0.35)
    )
    continue_text = visual.TextStim(
        win,
        text=button_text,
        color='black',
        height=0.05,
        pos=(0, -0.35)
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
    
    if USE_TOUCH_SCREEN:
        # Position-change detection for touchscreens
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        minRT = 0.2  # Minimum response time
        clock = core.Clock()
        clock.reset()
        
        while not clicked:
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                t = clock.getTime()
                
                # Check if mouse position has changed (touch moved)
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    draw_screen()
                else:
                    # Position has changed - check if touch is within button
                    try:
                        if continue_button.contains(mouseloc):
                            if t > minRT:
                                continue_button.fillColor = 'lightgreen'
                                draw_screen()
                                core.wait(0.2)
                                clicked = True
                                break
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    except:
                        # Fallback to manual calculation
                        hit_margin = 0.02
                        button_x, button_y = 0.0, -0.35
                        button_width, button_height = 0.3, 0.1
                        if (button_x - button_width/2 - hit_margin <= mouseloc_x <= button_x + button_width/2 + hit_margin and
                            button_y - button_height/2 - hit_margin <= mouseloc_y <= button_y + button_height/2 + hit_margin):
                            if t > minRT:
                                continue_button.fillColor = 'lightgreen'
                                draw_screen()
                                core.wait(0.2)
                                clicked = True
                                break
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_screen()
                event.clearEvents()
                core.wait(0.001)  # Very fast polling
            except Exception:
                pass
            
            # Safe event.getKeys() handling
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'space' in keys:
                        clicked = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, Exception):
                pass
    else:
        # Standard mouse click detection for non-touch screens
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
                
                # Get button position
                try:
                    button_pos = continue_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x = float(button_pos[0])
                        button_y = float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, -0.35
                        continue_button.pos = (button_x, button_y)
                except (TypeError, ValueError, IndexError):
                    button_x, button_y = 0.0, -0.35
                    continue_button.pos = (button_x, button_y)
                
                # Get button dimensions
                try:
                    button_width = float(continue_button.width)
                    button_height = float(continue_button.height)
                    if button_width <= 0 or button_height <= 0:
                        button_width, button_height = 0.3, 0.1
                except (TypeError, ValueError):
                    button_width, button_height = 0.3, 0.1
                
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_button:
                        continue_button.fillColor = 'lightgreen'
                        draw_screen()
                        core.wait(0.2)
                        clicked = True
                        break
                
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
            
            # Safe event.getKeys() handling
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'space' in keys:
                        clicked = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, Exception):
                pass
            
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
    clock = core.Clock()
    clock.reset()
    response_time = None
    
    if USE_TOUCH_SCREEN:
        # Position-change detection for touchscreens
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        minRT = 0.2  # Minimum response time
        
        while not answered:
            # Check for timeout
            elapsed_time = clock.getTime()
            if elapsed_time >= timeout:
                timed_out = True
                response_time = timeout
                answered = True
                break
            
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                t = clock.getTime()
                
                # Check if mouse position has changed (touch moved)
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    draw_question()
                else:
                    # Position has changed - check if touch is within buttons
                    try:
                        # Check YES button
                        if yes_button.contains(mouseloc):
                            if t > minRT:
                                answer = True
                                response_time = clock.getTime()
                                yes_button.fillColor = 'green'
                                draw_question()
                                core.wait(0.3)
                                answered = True
                                break
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                        # Check NO button
                        elif no_button.contains(mouseloc):
                            if t > minRT:
                                answer = False
                                response_time = clock.getTime()
                                no_button.fillColor = 'red'
                                draw_question()
                                core.wait(0.3)
                                answered = True
                                break
                            else:
                                mouserec = mouse.getPos()
                                try:
                                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                                except:
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                    except:
                        # Fallback to manual calculation
                        hit_margin = 0.02
                        yes_x, yes_y = -0.3, -0.2
                        yes_width, yes_height = 0.25, 0.1
                        no_x, no_y = 0.3, -0.2
                        no_width, no_height = 0.25, 0.1
                        
                        on_yes = (yes_x - yes_width/2 - hit_margin <= mouseloc_x <= yes_x + yes_width/2 + hit_margin and
                                 yes_y - yes_height/2 - hit_margin <= mouseloc_y <= yes_y + yes_height/2 + hit_margin)
                        on_no = (no_x - no_width/2 - hit_margin <= mouseloc_x <= no_x + no_width/2 + hit_margin and
                                no_y - no_height/2 - hit_margin <= mouseloc_y <= no_y + no_height/2 + hit_margin)
                        
                        if on_yes and t > minRT:
                            answer = True
                            response_time = clock.getTime()
                            yes_button.fillColor = 'green'
                            draw_question()
                            core.wait(0.3)
                            answered = True
                            break
                        elif on_no and t > minRT:
                            answer = False
                            response_time = clock.getTime()
                            no_button.fillColor = 'red'
                            draw_question()
                            core.wait(0.3)
                            answered = True
                            break
                        elif on_yes or on_no:
                            mouserec = mouse.getPos()
                            try:
                                mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                            except:
                                mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_question()
                event.clearEvents()
                core.wait(0.001)  # Very fast polling
            except Exception:
                pass
            
            # Safe event.getKeys() handling
            try:
                keys = event.getKeys(keyList=['y', 'n', 'escape'], timeStamped=False)
                if keys:
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
                pass
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        
        while not answered:
            # Check for timeout
            elapsed_time = clock.getTime()
            if elapsed_time >= timeout:
                timed_out = True
                response_time = timeout
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
                
                # Check YES button
                yes_x, yes_y = -0.3, -0.2
                yes_width, yes_height = 0.25, 0.1
                on_yes = (yes_x - yes_width/2 <= mouse_x <= yes_x + yes_width/2 and
                         yes_y - yes_height/2 <= mouse_y <= yes_y + yes_height/2)
                
                # Check NO button
                no_x, no_y = 0.3, -0.2
                no_width, no_height = 0.25, 0.1
                on_no = (no_x - no_width/2 <= mouse_x <= no_x + no_width/2 and
                        no_y - no_height/2 <= mouse_y <= no_y + no_height/2)
                
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
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
            # Safe event.getKeys() handling
            try:
                keys = event.getKeys(keyList=['y', 'n', 'escape'], timeStamped=False)
                if keys:
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
                pass
            
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
    # Brief delay to ensure temp window is fully closed
    time.sleep(0.1)  # Small delay to ensure clean transition
    
    print("Creating main window...")
    
    # Create window in windowed mode with larger size for better visibility
    # Use explicit size (never use size=None on Surface Pro/touchscreen mode)
    # Explicitly set viewPos to prevent broadcasting errors on hi-DPI Windows setups
    try:
        win = visual.Window(size=(1280, 720), color='white', units='height', fullscr=True, viewPos=(0, 0))
        # Immediately flip to ensure window is ready
        win.flip()
    except Exception as e:
        # If window creation fails, try with alternative explicit size
        import traceback
        traceback.print_exc()
        print("Trying with alternative size (1280, 720)...")
        time.sleep(0.1)  # Reduced delay
        try:
            win = visual.Window(size=(1280, 720), color='white', units='height', fullscr=True, viewPos=(0, 0))
            win.flip()
            print("Main window created with size (1280, 720)")
        except Exception as e2:
            print(f"Error: Could not create window ({e2})")
            import traceback
            traceback.print_exc()
            print("Exiting...")
            core.quit()
            exit(1)
    
    # Verify window was created successfully
    if win is None:
        print("Error: Failed to create main window - win is None")
        core.quit()
        exit(1)
    
    # Ensure window is visible and ready
    try:
        win.flip()
        core.wait(0.1)  # Brief wait to ensure window is fully ready
        print("Main window created successfully and ready")
    except Exception as e:
        print(f"Error preparing window: {e}")
        import traceback
        traceback.print_exc()
        if win is not None:
            try:
                win.close()
            except:
                pass
        core.quit()
        exit(1)
    
    # Verify window is ready before continuing
    if win is None:
        print("Error: Window is None after creation - cannot continue")
        core.quit()
        exit(1)
    
    print("Window verification complete, proceeding to experiment...")
    print(f"Window object: {win}")
    print(f"Window type: {type(win)}")
    
    # =========================
    #  MAIN EXPERIMENT
    # =========================

    # Get participant ID
    print("About to call get_participant_id()...")
    print(f"USE_TOUCH_SCREEN = {USE_TOUCH_SCREEN}")
    try:
        print("Entering get_participant_id() function...")
        participant_id = get_participant_id()
        print(f"Got participant ID: {participant_id}")
    except Exception as e:
        print(f"ERROR in get_participant_id(): {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("This error was caught - will exit now")
        if win is not None:
            try:
                win.close()
            except:
                pass
        core.quit()
        exit(1)

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
    
    # Clean up on successful completion
    print("Experiment completed successfully")
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    core.quit()

except Exception as e:
    # Catch any unhandled exceptions in the main experiment
    print(f"\n{'='*60}")
    print(f"CAUGHT EXCEPTION in main experiment block!")
    print(f"Exception: {e}")
    print(f"Error type: {type(e).__name__}")
    print(f"Window state: win = {win}")
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    print(f"{'='*60}\n")
    print("Press Enter to see error details...")
    try:
        input()
    except:
        pass
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    core.quit()
    exit(1)
finally:
    # Cleanup - this block always executes
    # Window and core.quit() are handled in the try/except blocks above
    pass
