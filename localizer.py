from psychopy import visual, core, event
import os, random, time
import csv
from datetime import datetime
import sys
import traceback
import platform

# Set up exception hook to catch all unhandled exceptions
def exception_handler(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("="*60)
    print("UNHANDLED EXCEPTION!")
    print("="*60)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("="*60)
    print("Press Enter to exit...")
    try:
        input()
    except:
        pass

sys.excepthook = exception_handler

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
                except Exception as e:
                    print(f"ERROR in safe_window_close (inner): {repr(e)}", file=sys.stderr)
                    traceback.print_exc()
    except Exception as e:
        print(f"ERROR in safe_window_close (outer): {repr(e)}", file=sys.stderr)
        traceback.print_exc()

def get_input_method():
    """Ask user whether they're using touch screen (1) or click screen (2)"""
    global USE_TOUCH_SCREEN
    
    # Create temporary window - handle partial initialization
    temp_win = None
    try:
        # Create windowed window
        # Add waitBlanking=False and useFBO=False to prevent hanging
        temp_win = visual.Window(
            size=(1400, 900),
            color='white',
            units='height',
            fullscr=False,
            allowGUI=True,
            waitBlanking=False,  # Prevent blocking on display sync
            useFBO=False  # Disable framebuffer objects to prevent hangs
        )
        temp_win.flip()
        
        prompt_text = visual.TextStim(
            temp_win,
            text="What input method are you using?\n\n"
                 "Touch or click the button below:",
            color='black',
            height=30/720*0.75,
            pos=(0, 200/720*0.6),
            wrapWidth=1000/720*0.75,
            units='height'
        )
        
        # Create button 1 (TOUCH SCREEN) - height units
        button1 = visual.Rect(
            temp_win,
            width=520/720*0.75,
            height=180/720*0.75,
            fillColor='lightgreen',
            lineColor='black',
            pos=(-320/720*0.6, -80/720*0.6),
            lineWidth=1/720*0.75,
            units='height'
        )
        button1_text = visual.TextStim(
            temp_win, 
            text="TOUCH SCREEN\n(Double tap with finger)", 
            color='black', 
            height=24/720*0.75, 
            pos=(-320/720*0.6, -80/720*0.6),
            units='height'
        )
        
        # Create button 2 (MOUSE/TRACKPAD) - height units
        button2 = visual.Rect(
            temp_win,
            width=520/720*0.75,
            height=180/720*0.75,
            fillColor='lightblue',
            lineColor='black',
            pos=(320/720*0.6, -80/720*0.6),
            lineWidth=1/720*0.75,
            units='height'
        )
        button2_text = visual.TextStim(
            temp_win, 
            text="MOUSE/TRACKPAD\n(Click)", 
            color='black', 
            height=24/720*0.75, 
            pos=(320/720*0.6, -80/720*0.6),
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
        # Clear events BEFORE loop starts, not inside loop
        event.clearEvents()
        selected = None
        
        # BUTTON PRESS DETECTION: Track button state for press/release detection
        prev_mouse_buttons = [False, False, False]
        
        while selected is None:
            # Check for escape key FIRST, before clearing events
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:
                    return None, None  # Signal to exit - window will be closed in exception handler
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking escape key: {e}", file=sys.stderr)
            
            # Redraw screen
            draw_selection_screen()
            
            try:
                mouse_buttons = mouse_temp.getPressed()
                mouseloc = mouse_temp.getPos()
                
                # Check for button release (was pressed, now released)
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    # Button was released - check if it was over a button
                    # Check button 1 (TOUCH SCREEN)
                    try:
                        if button1.contains(mouseloc):
                            USE_TOUCH_SCREEN = True
                            selected = 'touch'
                            button1.fillColor = 'green'
                            draw_selection_screen()
                            core.wait(0.05)
                            break
                    except Exception as e:
                        # Fallback to manual calculation
                        print(f"ERROR in button1.contains() fallback: {repr(e)}", file=sys.stderr)
                        traceback.print_exc()
                        try:
                            mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                        except:
                            mouseloc_x, mouseloc_y = 0.0, 0.0
                        hit_margin = 150/720*0.75
                        button1_x, button1_y = -320/720*0.6, -80/720*0.6
                        button1_width, button1_height = 520/720*0.75, 180/720*0.75
                        if (button1_x - button1_width/2 - hit_margin <= mouseloc_x <= button1_x + button1_width/2 + hit_margin and
                            button1_y - button1_height/2 - hit_margin <= mouseloc_y <= button1_y + button1_height/2 + hit_margin):
                            USE_TOUCH_SCREEN = True
                            selected = 'touch'
                            button1.fillColor = 'green'
                            draw_selection_screen()
                            core.wait(0.05)
                            break
                    
                    # Check button 2
                    if selected is None:
                        try:
                            if button2.contains(mouseloc):
                                USE_TOUCH_SCREEN = False
                                selected = 'click'
                                button2.fillColor = 'blue'
                                draw_selection_screen()
                                core.wait(0.05)
                                break
                        except Exception as e:
                            # Fallback to manual calculation
                            print(f"ERROR in button2.contains() fallback: {repr(e)}", file=sys.stderr)
                            traceback.print_exc()
                            try:
                                mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                            except:
                                mouseloc_x, mouseloc_y = 0.0, 0.0
                            hit_margin = 150/720*0.75
                            button2_x, button2_y = 320/720*0.6, -80/720*0.6
                            button2_width, button2_height = 520/720*0.75, 180/720*0.75
                            if (button2_x - button2_width/2 - hit_margin <= mouseloc_x <= button2_x + button2_width/2 + hit_margin and
                                button2_y - button2_height/2 - hit_margin <= mouseloc_y <= button2_y + button2_height/2 + hit_margin):
                                USE_TOUCH_SCREEN = False
                                selected = 'click'
                                button2.fillColor = 'blue'
                                draw_selection_screen()
                                core.wait(0.05)
                                break
                
                # Update previous button state
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except Exception as e:
                pass
            
            # Clear events only once per loop iteration, after all checks
            event.clearEvents()
            
            # Reduced polling delay for faster touch response
            core.wait(0.001)  # Very fast polling
        
        # Show confirmation - use height units to match temp window
        confirm_text = visual.TextStim(
            temp_win,
            text=f"Input method set to:\n{'TOUCH SCREEN' if USE_TOUCH_SCREEN else 'CLICK/MOUSE'}",
            color='black',
            height=40/720*0.75,
            pos=(0, 100/720*0.6),
            wrapWidth=1000/720*0.75,
            units='height'
        )
        
        # Create continue button for temp window - use height units
        cont_w = 300/720*0.75
        cont_h = 80/720*0.75
        cont_x = 0
        cont_y = -150/720*0.6
        continue_button = visual.Rect(temp_win, width=cont_w, height=cont_h, fillColor='lightblue', lineColor='black', pos=(cont_x, cont_y), units='height')
        continue_text = visual.TextStim(temp_win, text="CONTINUE", color='black', height=30/720*0.75, pos=(cont_x, cont_y), units='height')
        
        clicked = False
        continue_click_time = None  # Record when continue is clicked
        
        if USE_TOUCH_SCREEN:
            # POSITION-CHANGE DETECTION for touch screen
            mouserec_cont = mouse_temp.getPos()
            try:
                mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
            except (ValueError, TypeError, IndexError) as e:
                print(f"Warning: Could not parse initial continue button mouse position: {e}", file=sys.stderr)
                mouserec_cont_x, mouserec_cont_y = 0.0, 0.0
            
            minRT_cont = 0.05  # Minimum response time
            clock_cont = core.Clock()
            clock_cont.reset()
            
            while not clicked:
                # Check for escape key FIRST
                try:
                    keys = event.getKeys(keyList=['escape'])
                    if keys and 'escape' in keys:
                        return None, None
                except (AttributeError, RuntimeError) as e:
                    print(f"Warning: Error checking escape key in continue loop: {e}", file=sys.stderr)
                
                confirm_text.draw()
                continue_button.draw()
                continue_text.draw()
                temp_win.flip()
                
                try:
                    mouseloc_cont = mouse_temp.getPos()
                    try:
                        mouseloc_cont_x, mouseloc_cont_y = float(mouseloc_cont[0]), float(mouseloc_cont[1])
                    except (ValueError, TypeError, IndexError) as e:
                        print(f"Warning: Could not parse continue button mouse position: {e}", file=sys.stderr)
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
                                    continue_click_time = time.time()  # Record exact time of click
                                    clicked = True
                                    break
                                else:
                                    mouserec_cont = mouse_temp.getPos()
                                    try:
                                        mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
                                    except (ValueError, TypeError, IndexError) as e:
                                        print(f"Warning: Could not parse mouse position after continue button check: {e}", file=sys.stderr)
                                        mouserec_cont_x, mouserec_cont_y = mouseloc_cont_x, mouseloc_cont_y
                        except (AttributeError, RuntimeError) as e:
                            # Fallback to manual calculation if .contains() fails
                            print(f"Warning: continue_button.contains() failed, using fallback: {e}", file=sys.stderr)
                            hit_margin = 50/720*0.75
                            button_x, button_y = 0.0, -150.0/720*0.6
                            button_width, button_height = 300/720*0.75, 80/720*0.75
                            if (button_x - button_width/2 - hit_margin <= mouseloc_cont_x <= button_x + button_width/2 + hit_margin and
                                button_y - button_height/2 - hit_margin <= mouseloc_cont_y <= button_y + button_height/2 + hit_margin):
                                if t_cont > minRT_cont:
                                    continue_click_time = time.time()  # Record exact time of click
                                    clicked = True
                                    break
                                else:
                                    mouserec_cont = mouse_temp.getPos()
                                    try:
                                        mouserec_cont_x, mouserec_cont_y = float(mouserec_cont[0]), float(mouserec_cont[1])
                                    except (ValueError, TypeError, IndexError) as e:
                                        print(f"Warning: Could not parse mouse position in continue button fallback: {e}", file=sys.stderr)
                                        mouserec_cont_x, mouserec_cont_y = mouseloc_cont_x, mouseloc_cont_y
                except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                    # Log specific errors instead of silently ignoring
                    print(f"Warning: Error in continue button loop: {e}", file=sys.stderr)
                
                # Check for space key (escape already checked at start of loop)
                try:
                    keys = event.getKeys(keyList=['space'])
                    if keys and 'space' in keys:
                        continue_click_time = time.time()  # Record exact time of space key press
                        clicked = True
                        break
                except (AttributeError, RuntimeError) as e:
                    print(f"Warning: Error checking space key: {e}", file=sys.stderr)
                
                # Clear events AFTER checking keys
                event.clearEvents()
                
                # Reduced polling delay for faster touch response
                core.wait(0.005)  # Faster polling for touch screens
        else:
            # BUTTON PRESS/RELEASE DETECTION for mouse/click mode
            prev_mouse_buttons_cont = [False, False, False]
            
            while not clicked:
                # Check for escape key FIRST
                try:
                    keys = event.getKeys(keyList=['escape'])
                    if keys and 'escape' in keys:
                        return None, None
                except (AttributeError, RuntimeError) as e:
                    print(f"Warning: Error checking escape key in continue loop: {e}", file=sys.stderr)
                
                confirm_text.draw()
                continue_button.draw()
                continue_text.draw()
                temp_win.flip()
                
                try:
                    mouse_buttons_cont = mouse_temp.getPressed()
                    mouseloc_cont = mouse_temp.getPos()
                    
                    # Check for button release (was pressed, now released)
                    if prev_mouse_buttons_cont[0] and not mouse_buttons_cont[0]:
                        # Button was released - check if it was over the continue button
                        try:
                            if continue_button.contains(mouseloc_cont):
                                continue_click_time = time.time()  # Record exact time of click
                                clicked = True
                                break
                        except Exception as e:
                            # Fallback to manual calculation
                            print(f"ERROR in button.contains() fallback: {repr(e)}", file=sys.stderr)
                            traceback.print_exc()
                            try:
                                mouseloc_cont_x, mouseloc_cont_y = float(mouseloc_cont[0]), float(mouseloc_cont[1])
                            except:
                                mouseloc_cont_x, mouseloc_cont_y = 0.0, 0.0
                            hit_margin = 50/720*0.75
                            button_x, button_y = 0.0, -150.0/720*0.6
                            button_width, button_height = 300/720*0.75, 80/720*0.75
                            if (button_x - button_width/2 - hit_margin <= mouseloc_cont_x <= button_x + button_width/2 + hit_margin and
                                button_y - button_height/2 - hit_margin <= mouseloc_cont_y <= button_y + button_height/2 + hit_margin):
                                continue_click_time = time.time()  # Record exact time of click
                                clicked = True
                                break
                    
                    # Update previous button state
                    prev_mouse_buttons_cont = mouse_buttons_cont.copy() if hasattr(mouse_buttons_cont, 'copy') else list(mouse_buttons_cont)
                except Exception as e:
                    pass
                
                # Check for space key (escape already checked at start of loop)
                try:
                    keys = event.getKeys(keyList=['space'])
                    if keys and 'space' in keys:
                        continue_click_time = time.time()  # Record exact time of space key press
                        clicked = True
                        break
                except (AttributeError, RuntimeError) as e:
                    print(f"Warning: Error checking space key: {e}", file=sys.stderr)
                
                # Clear events AFTER checking keys
                event.clearEvents()
                
                # Reduced polling delay for faster touch response
                core.wait(0.001)  # Very fast polling
        
        mouse_temp.setVisible(False)
        
        # Show a brief transition message before closing
        transition_text = visual.TextStim(
            temp_win,
            text="Loading...",
            color='black',
            height=50/720*0.75,
            pos=(0, 0),
            units='height'
        )
        transition_text.draw()
        temp_win.flip()
        
        # Calculate remaining time to reach 0.4 seconds total from continue click
        if continue_click_time is not None:
            elapsed = time.time() - continue_click_time
            remaining = 0.4 - elapsed
            if remaining > 0:
                time.sleep(remaining)  # Wait exactly 0.4 seconds from continue click
        else:
            # Fallback if time wasn't recorded (shouldn't happen)
            time.sleep(0.4)
        
        print(f"DEBUG: About to return USE_TOUCH_SCREEN = {USE_TOUCH_SCREEN}", file=sys.stderr)
        sys.stderr.flush()
        # Return both the result and the temp window reference
        # Don't close temp window here - close it after main window is created
        return USE_TOUCH_SCREEN, temp_win
    
    except Exception as e:
        # If there's an error, close temp window in exception handler
        print(f"ERROR in get_input_method: {e}", file=sys.stderr)
        sys.stderr.flush()
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        if temp_win is not None:
            try:
                temp_win.close()
            except:
                pass
        return None, None
    
    finally:
        # Don't close temp window here - it will be closed after main window creation
        # This prevents PsychoPy from quitting when all windows are closed
        pass

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
result = None
temp_win = None
try:
    print("DEBUG: About to call get_input_method()...", file=sys.stderr)
    sys.stderr.flush()
    result, temp_win = get_input_method()
    print(f"DEBUG: get_input_method() returned: result={result}, temp_win={temp_win}", file=sys.stderr)
    sys.stderr.flush()
    print(f"Input method result: {result}")
    sys.stdout.flush()
except Exception as e:
    print(f"ERROR in get_input_method(): {e}", file=sys.stderr)
    sys.stderr.flush()
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    traceback.print_exc()
    print(f"ERROR in get_input_method(): {e}")
    # Close temp window if it exists
    if temp_win is not None:
        try:
            temp_win.close()
        except:
            pass
    print("Press Enter to exit...")
    try:
        input()
    except Exception as e:
        print(f"ERROR in get_input_method() exception handler: {repr(e)}", file=sys.stderr)
        traceback.print_exc()
    try:
        core.quit()
    except Exception as e:
        print(f"ERROR calling core.quit(): {repr(e)}", file=sys.stderr)
        traceback.print_exc()
    exit(1)

if result is None:
    print("Input method selection cancelled. Exiting...")
    print("Press Enter to exit...")
    try:
        input()
    except Exception as e:
        print(f"ERROR in input() call: {repr(e)}", file=sys.stderr)
        traceback.print_exc()
    try:
        core.quit()
    except Exception as e:
        print(f"ERROR calling core.quit(): {repr(e)}", file=sys.stderr)
        traceback.print_exc()
    exit(0)

print(f"Input method selected: {'TOUCH SCREEN' if result else 'MOUSE/TRACKPAD'}")
sys.stdout.flush()
sys.stderr.flush()
print(f"Result value: {result}, Type: {type(result)}")
sys.stdout.flush()
sys.stderr.flush()
print("About to create main window...")
sys.stdout.flush()
sys.stderr.flush()
print("DEBUG: About to define helper functions before window creation", file=sys.stderr)
sys.stderr.flush()

def get_category_for_stimulus(stimulus_num):
    """Get the category name for a given stimulus number"""
    for category, (start, end) in CATEGORY_MAPPING.items():
        if start <= stimulus_num <= end:
            return category
    return None

def category_to_question(category_name):
    """Convert category name to question text
    
    Handles multiple formats:
    - BIG_ANIMAL -> "big animal"
    - biganimal -> "big animal" (splits camelCase-like names)
    - BIRD -> "bird"
    """
    # First, map back to standard format if needed (for display purposes)
    # The category_name might be the mapped folder name or the original category name
    category_mapping_reverse = {
        "biganimal": "BIG_ANIMAL",
        "bigobject": "BIG_OBJECT",
        "smallanimal": "SMALL_ANIMAL",
        "smallobject": "SMALL_OBJECT",
    }
    
    # If it's a mapped folder name, convert to standard format
    if category_name.lower() in category_mapping_reverse:
        category_name = category_mapping_reverse[category_name.lower()]
    
    # Convert to lowercase and split on underscore
    words = category_name.lower().split('_')
    
    # If no underscore, try to split camelCase-like names (e.g., "smallobject" -> "small object")
    if len(words) == 1 and len(words[0]) > 0:
        # Try to detect word boundaries in camelCase-like names
        text = words[0]
        # Insert space before capital letters (if any) or before common word boundaries
        # For names like "smallobject", we need to detect where "small" ends and "object" begins
        # Simple heuristic: look for common word patterns
        common_words = ['big', 'small', 'animal', 'object', 'bird', 'food', 'fruit', 
                       'insect', 'vegetable', 'vehicle']
        result_words = []
        remaining = text
        while remaining:
            found = False
            for word in common_words:
                if remaining.lower().startswith(word):
                    result_words.append(word)
                    remaining = remaining[len(word):]
                    found = True
                    break
            if not found:
                # If no match, take the whole thing
                result_words.append(remaining)
                break
        if len(result_words) > 1:
            words = result_words
    
    category_text = ' '.join(words)
    
    # Check if category starts with a vowel sound
    vowels = ['a', 'e', 'i', 'o', 'u']
    article = "an" if category_text[0] in vowels else "a"
    
    return f"Was the last object {article} {category_text}?"

def get_log_directory():
    """Get the directory for log files - always saves to ../LOG_FILES"""
    log_dir = "../LOG_FILES"
    # Create directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def is_test_participant(participant_id):
    """Check if participant ID contains 'test' (case-insensitive)"""
    if participant_id is None:
        return False
    return "test" in participant_id.lower()

def load_all_stimuli():
    """Load all 100 Image files and 100 Lure files from STIMULI directory (200 total)"""
    stimuli_list = []
    found_images = set()  # Track which stimulus numbers have Image files
    found_lures = set()   # Track which stimulus numbers have Lure files
    
    # Map category names to actual folder names (handle case/underscore differences)
    category_folder_map = {
        "BIG_ANIMAL": "biganimal",
        "BIG_OBJECT": "bigobject",
        "SMALL_ANIMAL": "smallanimal",
        "SMALL_OBJECT": "smallobject",
        # These match exactly
        "BIRD": "BIRD",
        "FOOD": "FOOD",
        "FRUIT": "FRUIT",
        "INSECT": "INSECT",
        "VEGETABLE": "VEGETABLE",
        "VEHICLE": "VEHICLE",
    }
    
    for category in CATEGORY_MAPPING.keys():
        # Use mapped folder name if available, otherwise use category name as-is
        folder_name = category_folder_map.get(category, category)
        category_dir = os.path.join(STIMULI_DIR, folder_name)
        if os.path.exists(category_dir):
            # List all object folders
            object_folders = [f for f in os.listdir(category_dir) 
                             if os.path.isdir(os.path.join(category_dir, f))]
            
            for obj_folder in sorted(object_folders):
                obj_path = os.path.join(category_dir, obj_folder)
                # Look for both Image_XXX.jpg and Lure_XXX.jpg files
                for filename in os.listdir(obj_path):
                    if (filename.startswith("Image_") or filename.startswith("Lure_")) and filename.endswith(".jpg"):
                        # Extract stimulus number from filename (e.g., Image_001.jpg -> 1, Lure_001.jpg -> 1)
                        try:
                            stimulus_num = int(filename.split("_")[1].split(".")[0])
                            is_lure = filename.startswith("Lure_")
                            full_path = os.path.join(obj_path, filename)
                            if os.path.exists(full_path):
                                stimuli_list.append({
                                    'path': full_path,
                                    'number': stimulus_num,
                                    'category': category,
                                    'object_name': obj_folder,
                                    'is_lure': is_lure,
                                    'stimulus_type': 'Lure' if is_lure else 'Image'
                                })
                                # Track which stimulus numbers we found
                                if is_lure:
                                    found_lures.add(stimulus_num)
                                else:
                                    found_images.add(stimulus_num)
                        except (ValueError, IndexError):
                            continue
    
    # Sort by stimulus number, then by type (Image first, then Lure) to ensure consistent ordering
    stimuli_list.sort(key=lambda x: (x['number'], x['is_lure']))
    
    # Provide detailed information if not all stimuli found
    if len(stimuli_list) != 200:
        num_images = len(found_images)
        num_lures = len(found_lures)
        print(f"Warning: Expected 200 stimuli (100 Image + 100 Lure), found {len(stimuli_list)}")
        print(f"  - Found {num_images} unique Image files (expected 100)")
        print(f"  - Found {num_lures} unique Lure files (expected 100)")
        print(f"  - Missing Image files for stimulus numbers: {sorted(set(range(1, 101)) - found_images)}")
        print(f"  - Missing Lure files for stimulus numbers: {sorted(set(range(1, 101)) - found_lures)}")
    
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
            id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.045*0.75, wrapWidth=1.4*0.75, pos=(0, 0.35*0.6))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75, pos=(0, 0.25*0.6))
            print("input_display created")
        else:
            print("Creating mouse/trackpad text stimuli...")
            id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.045*0.75, wrapWidth=1.4*0.75, pos=(0, 0.3*0.6))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75, pos=(0, 0.1*0.6))
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
            start_y = -0.15*0.6  # Move keyboard lower to avoid overlap with buttons
            row_spacing = 0.12*0.75
            button_spacing = 0.015  # Spacing between buttons (increased for better visibility)
            
            print(f"Creating {len(keyboard_rows)} keyboard rows...")
            for row_idx, row in enumerate(keyboard_rows):
                print(f"Creating row {row_idx} with {len(row)} keys...")
                row_buttons = []
                num_keys = len(row)
                button_width = 0.07*0.75  # Match the actual button width
                start_x = -(num_keys - 1) * (button_width + button_spacing) / 2
                
                for col_idx, key in enumerate(row):
                    x_pos = start_x + col_idx * (button_width + button_spacing)
                    y_pos = start_y - row_idx * row_spacing
                    
                    button = visual.Rect(win, width=button_width, height=0.08*0.75, fillColor='lightgray', 
                                        lineColor='black', pos=(x_pos, y_pos))
                    text = visual.TextStim(win, text=key, color='black', height=0.04*0.75, pos=(x_pos, y_pos))
                    row_buttons.append((button, text, key, x_pos, y_pos))
                
                keyboard_buttons.append(row_buttons)
            
            print("Creating special buttons...")
            # Special buttons - arranged horizontally between input and keyboard
            button_y_pos = 0.05*0.6  # Position between input (0.25) and keyboard start (-0.15)
            backspace_button = visual.Rect(win, width=0.2*0.75, height=0.1*0.75, fillColor='lightcoral', 
                                          lineColor='black', lineWidth=2*0.75, pos=(-0.25*0.6, button_y_pos))
            backspace_text = visual.TextStim(win, text="BACKSPACE", color='black', height=0.025*0.75, pos=(-0.25*0.6, button_y_pos))
            
            continue_button = visual.Rect(win, width=0.3*0.75, height=0.1*0.75, fillColor='lightgreen', 
                                          lineColor='black', lineWidth=2*0.75, pos=(0.25*0.6, button_y_pos))
            continue_text = visual.TextStim(win, text="CONTINUE", color='black', height=0.025*0.75, pos=(0.25*0.6, button_y_pos))
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
    # Clear events BEFORE loop starts, not inside loop
    event.clearEvents()
    
    # POSITION-CHANGE DETECTION: Store initial mouse position
    mouserec = mouse.getPos()
    try:
        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
    except (ValueError, TypeError, IndexError) as e:
        print(f"Warning: Could not parse initial mouse position in get_participant_id: {e}", file=sys.stderr)
        mouserec_x, mouserec_y = 0.0, 0.0
    
    minRT = 0.05  # Minimum response time (reduced for faster response)
    clock = core.Clock()
    clock.reset()
    
    while True:
        # Check for escape key FIRST, before clearing events
        try:
            keys = event.getKeys(keyList=['escape'], timeStamped=False)
            if keys and 'escape' in keys:
                return None
        except (AttributeError, RuntimeError) as e:
            print(f"Warning: Error checking escape key in get_participant_id: {e}", file=sys.stderr)
        
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
                    except Exception as e:
                        # Fallback to manual calculation
                        print(f"ERROR in backspace/continue button.contains() fallback: {repr(e)}", file=sys.stderr)
                        traceback.print_exc()
                        hit_margin = 0.08*0.75
                        backspace_x, backspace_y = -0.35*0.6, (start_y + 0.2)*0.6
                        backspace_width, backspace_height = 0.2*0.75, 0.1*0.75
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
            # Clear events only once per loop iteration, after all checks
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
        width=0.3*0.75,
        height=0.1*0.75,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.35*0.6)
    )
    continue_text = visual.TextStim(
        win,
        text=button_text,
        color='black',
        height=0.05*0.75,
        pos=(0, -0.35*0.6)
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
                        hit_margin = 0.02*0.75
                        button_x, button_y = 0.0, -0.35*0.6
                        button_width, button_height = 0.3*0.75, 0.1*0.75
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
                                except (ValueError, TypeError, IndexError) as e:
                                    print(f"Warning: Could not parse mouse position in wait_for_button: {e}", file=sys.stderr)
                                    mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_screen()
                core.wait(0.001)  # Very fast polling
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                # Log specific errors instead of silently ignoring
                print(f"Warning: Error in wait_for_button touch screen loop: {e}", file=sys.stderr)
            
            # Check keys AFTER processing touch, BEFORE clearing events
            try:
                keys = event.getKeys(keyList=['space'], timeStamped=False)  # escape already checked at start
                if keys and 'space' in keys:
                    clicked = True
                    break
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking space key in wait_for_button: {e}", file=sys.stderr)
            
            # Clear events AFTER checking keys
            event.clearEvents()
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
                        button_x, button_y = 0.0, -0.35*0.6
                        continue_button.pos = (button_x, button_y)
                except (TypeError, ValueError, IndexError):
                    button_x, button_y = 0.0, -0.35*0.6
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
    """Ask category question and return (answer, timed_out, response_time, answer_click_time) tuple
    
    Args:
        category_name: Category name for the question
        last_object_name: Name of the last object shown
        timeout: Timeout in seconds (default 10.0)
    
    Returns:
        tuple: (answer: bool or None, timed_out: bool, response_time: float, answer_click_time: float or None)
    """
    question_text = category_to_question(category_name)
    
    # Create question display
    question_stim = visual.TextStim(
        win,
        text=question_text,
        color='black',
        height=0.06*0.75,
        pos=(0, 0.2*0.6),
        wrapWidth=1.4*0.75
    )
    
    # Create YES and NO buttons
    yes_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.1*0.75,
        fillColor='lightgreen',
        lineColor='black',
        pos=(-0.3*0.6, -0.2*0.6)
    )
    yes_text = visual.TextStim(
        win,
        text="YES",
        color='black',
        height=0.05*0.75,
        pos=(-0.3*0.6, -0.2*0.6)
    )
    
    no_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.1*0.75,
        fillColor='lightcoral',
        lineColor='black',
        pos=(0.3*0.6, -0.2*0.6)
    )
    no_text = visual.TextStim(
        win,
        text="NO",
        color='black',
        height=0.05*0.75,
        pos=(0.3*0.6, -0.2*0.6)
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
    answer_click_time = None  # Absolute timestamp when answer was clicked
    
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
                                answer_click_time = time.time()  # Record absolute timestamp
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
                                answer_click_time = time.time()  # Record absolute timestamp
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
                            answer_click_time = time.time()  # Record absolute timestamp
                            yes_button.fillColor = 'green'
                            draw_question()
                            core.wait(0.3)
                            answered = True
                            break
                        elif on_no and t > minRT:
                            answer = False
                            response_time = clock.getTime()
                            answer_click_time = time.time()  # Record absolute timestamp
                            no_button.fillColor = 'red'
                            draw_question()
                            core.wait(0.3)
                            answered = True
                            break
                        elif on_yes or on_no:
                            mouserec = mouse.getPos()
                            try:
                                mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                            except (ValueError, TypeError, IndexError) as e:
                                print(f"Warning: Could not parse mouse position in ask_category_question: {e}", file=sys.stderr)
                                mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_question()
                core.wait(0.001)  # Very fast polling
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                # Log specific errors instead of silently ignoring
                print(f"Warning: Error in ask_category_question touch screen loop: {e}", file=sys.stderr)
            
            # Check keys AFTER processing touch, BEFORE clearing events (escape already checked at start)
            try:
                keys = event.getKeys(keyList=['y', 'n'], timeStamped=False)
                if keys:
                    if 'y' in keys:
                        answer = True
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        answered = True
                        break
                    elif 'n' in keys:
                        answer = False
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        answered = True
                        break
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking y/n keys in ask_category_question: {e}", file=sys.stderr)
            
            # Clear events AFTER checking keys
            event.clearEvents()
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
                yes_x, yes_y = -0.3*0.6, -0.2*0.6
                yes_width, yes_height = 0.25*0.75, 0.1*0.75
                on_yes = (yes_x - yes_width/2 <= mouse_x <= yes_x + yes_width/2 and
                         yes_y - yes_height/2 <= mouse_y <= yes_y + yes_height/2)
                
                # Check NO button
                no_x, no_y = 0.3*0.6, -0.2*0.6
                no_width, no_height = 0.25*0.75, 0.1*0.75
                on_no = (no_x - no_width/2 <= mouse_x <= no_x + no_width/2 and
                        no_y - no_height/2 <= mouse_y <= no_y + no_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_yes:
                        answer = True
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        yes_button.fillColor = 'green'
                        draw_question()
                        core.wait(0.3)
                        answered = True
                        break
                    elif on_no:
                        answer = False
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        no_button.fillColor = 'red'
                        draw_question()
                        core.wait(0.3)
                        answered = True
                        break
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                # Log specific errors instead of silently ignoring
                print(f"Warning: Error in ask_category_question mouse button handling: {e}", file=sys.stderr)
            
            # Safe event.getKeys() handling
            try:
                keys = event.getKeys(keyList=['y', 'n', 'escape'], timeStamped=False)
                if keys:
                    if 'y' in keys:
                        answer = True
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        answered = True
                        break
                    elif 'n' in keys:
                        answer = False
                        response_time = clock.getTime()
                        answer_click_time = time.time()  # Record absolute timestamp
                        answered = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking keys in ask_category_question: {e}", file=sys.stderr)
            
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
    
    return (answer, timed_out, response_time, answer_click_time)

# Create main window with appropriate settings - use try/finally pattern
print("DEBUG: About to start window creation block", file=sys.stderr)
sys.stderr.flush()
win = None
try:
    print("DEBUG: Inside try block, about to print STARTING WINDOW CREATION", file=sys.stderr)
    sys.stderr.flush()
    print("="*60)
    sys.stdout.flush()
    sys.stderr.flush()
    print("STARTING WINDOW CREATION")
    sys.stdout.flush()
    sys.stderr.flush()
    print("="*60)
    sys.stdout.flush()
    sys.stderr.flush()
    
    import time
    # Window creation happens exactly 0.4 seconds after continue was clicked
    # (delay already handled in get_input_method function)
    # Add delay to ensure temp window is fully closed
    print("Waiting before creating main window...")
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(0.2)  # Longer delay to ensure temp window is fully closed
    
    print("Creating main window (1400x900)...")
    sys.stdout.flush()
    sys.stderr.flush()
    # Create windowed window
    try:
        print("DEBUG: About to call visual.Window()...", file=sys.stderr)
        sys.stderr.flush()
        
        # Ensure events are cleared before window creation
        event.clearEvents()
        
        print("DEBUG: Calling visual.Window(size=(1400, 900), fullscr=False)...", file=sys.stderr)
        sys.stderr.flush()
        
        win = visual.Window(
            size=(1400, 900), 
            color='white', 
            units='height',
            fullscr=False,
            waitBlanking=False,  # Prevent blocking on display sync
            allowGUI=True,  # Ensure GUI is available
            useFBO=False  # Disable framebuffer objects to prevent hangs
        )
        
        print("DEBUG: visual.Window() call completed successfully", file=sys.stderr)
        sys.stderr.flush()
        print("Window object created, about to flip...", file=sys.stderr)
        sys.stderr.flush()
        
        # Ensure window is ready before proceeding
        try:
            # Immediately flip to ensure window is ready
            win.flip()
            print("Window flip successful", file=sys.stderr)
            sys.stderr.flush()
        except Exception as flip_error:
            print(f"Warning: Initial flip failed: {flip_error}", file=sys.stderr)
            sys.stderr.flush()
            # Try to continue anyway - window might still be usable
        
        print("Windowed window created successfully")
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Don't close temp window yet - wait until main window is fully set up
    except Exception as e:
        # If window creation fails, show error
        import traceback
        print("="*60, file=sys.stderr)
        print("WINDOW CREATION FAILED", file=sys.stderr)
        print("="*60, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        traceback.print_exc()
        print(f"Window creation failed: {e}")
        sys.stdout.flush()
        print("Press Enter to exit...")
        try:
            input()
        except Exception as e:
            print(f"ERROR in input() call: {repr(e)}", file=sys.stderr)
            traceback.print_exc()
        try:
            core.quit()
        except Exception as e:
            print(f"ERROR calling core.quit(): {repr(e)}", file=sys.stderr)
            traceback.print_exc()
        # Close temp window if it still exists
        if temp_win is not None:
            try:
                temp_win.close()
            except:
                pass
        exit(1)
    
    # Verify window was created successfully
    if win is None:
        error_msg = "ERROR: Failed to create main window - win is None"
        print("="*60, file=sys.stderr)
        print(error_msg, file=sys.stderr)
        print("="*60, file=sys.stderr)
        sys.stderr.flush()
        print("="*60)
        print("ERROR: Failed to create main window - win is None")
        print("="*60)
        print("Press Enter to exit...")
        sys.stdout.flush()
        try:
            input()
        except:
            pass
        try:
            core.quit()
        except:
            pass
        exit(1)
    
    print(f"Window created successfully: {win}")
    sys.stdout.flush()
    
    # Ensure window is visible and ready
    try:
        win.flip()
        core.wait(0.1)  # Brief wait to ensure window is fully ready
        print("Main window created successfully")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error preparing window: {e}")
        import traceback
        traceback.print_exc()
        core.quit()
        exit(1)
    
    # Force window to front on macOS
    try:
        if platform.system() == 'Darwin':  # macOS
            try:
                win.winHandle.activate()
            except Exception as e:
                print(f"Warning: Could not activate window on macOS: {e}", file=sys.stderr)
                # This is not critical, continue anyway
    except Exception as e:
        print(f"Warning: Error checking platform for window activation: {e}", file=sys.stderr)
        # This is not critical, continue anyway

    # Initial flip to ensure window is ready
    print("Performing initial window flip...")
    sys.stdout.flush()
    try:
        win.flip()
        print("Initial flip successful")
        sys.stdout.flush()
    except Exception as e:
        print(f"ERROR during initial flip: {e}")
        sys.stdout.flush()
        raise
    core.wait(0.1)
    
    # Test that window can draw something simple
    print("Testing window with simple draw...")
    sys.stdout.flush()
    try:
        test_text = visual.TextStim(win, text=" ", color='black', height=0.05*0.75, pos=(0, 0))
        test_text.draw()
        win.flip()
        print("Window draw test successful")
        sys.stdout.flush()
        core.wait(0.1)
    except Exception as e:
        print(f"ERROR during window draw test: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        raise
    
    # Verify window is ready before continuing
    if win is None:
        print("="*60)
        print("CRITICAL ERROR: win is None after window creation attempt")
        print("="*60)
        raise RuntimeError("Main window creation failed - win is None")
    
    print("Window verification complete, proceeding to experiment...")
    sys.stdout.flush()
    print(f"Window object: {win}")
    sys.stdout.flush()
    print(f"Window type: {type(win)}")
    sys.stdout.flush()
    print("Main window setup complete. Window is ready.")
    sys.stdout.flush()
    print("="*60)
    sys.stdout.flush()
    print("WINDOW CREATION SUCCESSFUL")
    sys.stdout.flush()
    print("="*60)
    sys.stdout.flush()
    
    # Don't close temp window - keep it open to prevent PsychoPy from auto-quitting
    # Closing it causes PsychoPy to detect all windows are closed and quit
    # We'll just leave it open (it's behind the main window anyway)
    if temp_win is not None:
        print("DEBUG: Keeping temp window open to prevent PsychoPy auto-quit", file=sys.stderr)
        sys.stderr.flush()
        # Don't close temp_win - leave it open
    
    # =========================
    #  MAIN EXPERIMENT
    # =========================

    # Create fixation cross
    fixation = visual.TextStim(win, text="+", color='black', height=0.08*0.75, pos=(0, 0))
    
    def show_fixation(duration=1.0):
        """Display fixation cross for specified duration"""
        fixation.draw()
        win.flip()
        core.wait(duration)

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
            except Exception as e:
                print(f"ERROR calling win.close(): {repr(e)}", file=sys.stderr)
                traceback.print_exc()
        core.quit()
        exit(1)

    # Load all stimuli
    print("Loading stimuli...")
    all_stimuli = load_all_stimuli()

    if len(all_stimuli) != 200:
        print(f"Warning: Expected 200 stimuli (100 Image + 100 Lure), found {len(all_stimuli)}")
        print(f"  The localizer will proceed with the available {len(all_stimuli)} stimuli.")
        print(f"  Check the detailed output above to see which stimulus files are missing.")

    if len(all_stimuli) == 0:
        print("ERROR: No stimuli found! Cannot proceed with localizer task.")
        print("Please check that the STIMULI directory exists and contains image files.")
        if win is not None:
            try:
                win.close()
            except:
                pass
        core.quit()
        exit(1)

    # Randomize order
    random.shuffle(all_stimuli)

    # Show instructions
    instructions = visual.TextStim(
        win,
        text="LOCALIZER TASK\n\n"
             "You will see 200 images one at a time.\n\n"
             "Every few images, you will be asked a question\n"
             "about the previous image.\n\n"
             "Please pay attention to each image.",
        color='black',
        height=0.05*0.75,
        pos=(0, 0),
        wrapWidth=1.4*0.75
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
            'stimulus_type', 'is_lure', 'image_path', 'presentation_time', 
            'fixation_onset_time', 'fixation_offset_time', 'fixation_duration',
            'image_onset_time', 'image_offset_time', 'is_question_trial', 
            'question_category', 'question_text', 'question_onset_time', 
            'answer', 'correct_answer', 'correct', 'timed_out', 'response_time', 'answer_click_time'
        ]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_file.flush()
        csv_initialized = True
        print(f"✓ Created localizer CSV file: {csv_file_path}")

    # Show images
    # Start with a fixation cross before the first image
    fixation_duration_first = random.uniform(0.25, 0.75)
    fixation_onset_first = time.time()
    show_fixation(fixation_duration_first)
    fixation_offset_first = time.time()
    
    for idx, stimulus in enumerate(all_stimuli, 1):
        # Record presentation time
        presentation_time = datetime.now()
        presentation_timestamp = presentation_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Show jittered fixation between images (except before first image, which was already shown)
        if idx > 1:
            fixation_duration = random.uniform(0.25, 0.75)
            fixation_onset = time.time()
            show_fixation(fixation_duration)
            fixation_offset = time.time()
        else:
            # First image uses the initial fixation
            fixation_duration = fixation_duration_first
            fixation_onset = fixation_onset_first
            fixation_offset = fixation_offset_first
        
        # Load and display image
        try:
            img = visual.ImageStim(win, image=stimulus['path'], size=(0.8*0.75, 0.8*0.75))
            img.draw()
            win.flip()
            
            # Record image onset time
            image_onset_time = time.time()
            
            # Show image for exactly 0.5 seconds (fixed duration)
            core.wait(0.5)
            
            # Record image offset time
            image_offset_time = time.time()
            
            # Check if this is the 10th image (or every 10th after the first)
            is_question_trial = (idx % 10 == 0)
            
            question_onset_time = None
            
            if is_question_trial:
                # Ask category question about the image we just showed (the 10th, 20th, 30th, etc.)
                current_stimulus = stimulus
                correct_category = current_stimulus['category']
                
                # 50% chance to ask about correct category, 50% chance to ask about random category
                ask_about_correct = random.choice([True, False])
                
                if ask_about_correct:
                    # Ask about the actual category of the last object
                    question_category = correct_category
                    correct_answer = True
                else:
                    # Ask about a random category (different from the actual category)
                    all_categories = list(CATEGORY_MAPPING.keys())
                    # Remove the correct category from options
                    wrong_categories = [c for c in all_categories if c != correct_category]
                    question_category = random.choice(wrong_categories)
                    correct_answer = False
                
                # Record question onset time
                question_onset_time = time.time()
                
                # Ask the question
                answer, timed_out, response_time, answer_click_time = ask_category_question(question_category, current_stimulus['object_name'])
                
                # Calculate correct only if not timed out
                is_correct = (answer == correct_answer) if not timed_out else None
                
                # Record data with question fields
                trial_data = {
                    'participant_id': participant_id,
                    'trial': idx,
                    'stimulus_number': current_stimulus['number'],
                    'object_name': current_stimulus['object_name'],
                    'category': current_stimulus['category'],
                    'stimulus_type': current_stimulus['stimulus_type'],
                    'is_lure': current_stimulus['is_lure'],
                    'image_path': current_stimulus['path'],
                    'presentation_time': presentation_timestamp,
                    'fixation_onset_time': fixation_onset,
                    'fixation_offset_time': fixation_offset,
                    'fixation_duration': fixation_duration,
                    'image_onset_time': image_onset_time,
                    'image_offset_time': image_offset_time,
                    'is_question_trial': True,
                    'question_category': question_category,
                    'question_text': category_to_question(question_category),
                    'question_onset_time': question_onset_time,
                    'answer': answer if not timed_out else 'TIMEOUT',
                    'correct_answer': correct_answer,
                    'correct': is_correct,
                    'timed_out': timed_out,
                    'response_time': response_time if response_time is not None else None,
                    'answer_click_time': answer_click_time
                }
            else:
                # Record data for non-question trials
                trial_data = {
                    'participant_id': participant_id,
                    'trial': idx,
                    'stimulus_number': stimulus['number'],
                    'object_name': stimulus['object_name'],
                    'category': stimulus['category'],
                    'stimulus_type': stimulus['stimulus_type'],
                    'is_lure': stimulus['is_lure'],
                    'image_path': stimulus['path'],
                    'presentation_time': presentation_timestamp,
                    'fixation_onset_time': fixation_onset,
                    'fixation_offset_time': fixation_offset,
                    'fixation_duration': fixation_duration,
                    'image_onset_time': image_onset_time,
                    'image_offset_time': image_offset_time,
                    'is_question_trial': False,
                    'question_category': None,
                    'question_text': None,
                    'question_onset_time': None,
                    'answer': None,
                    'correct_answer': None,
                    'correct': None,
                    'timed_out': None,
                    'response_time': None,
                    'answer_click_time': None
                }
            
            localizer_data.append(trial_data)
            
            # Write current trial to CSV
            if csv_writer is not None:
                csv_writer.writerow(trial_data)
                csv_file.flush()  # Ensure data is written immediately
                
        except Exception as e:
            print(f"Error loading image {stimulus['path']}: {e}")
            continue

    # Show completion message
    completion_text = visual.TextStim(
        win,
        text="LOCALIZER TASK COMPLETE!\n\n"
             "Thank you for your participation.",
        color='black',
        height=0.06*0.75,
        pos=(0, 0),
        wrapWidth=1.4*0.75
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
    sys.stdout.flush()
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    try:
        core.quit()
    except:
        pass

except SystemExit as se:
    print("SystemExit caught in main experiment", file=sys.stderr)
    sys.stderr.flush()
    print(f"SystemExit value: {se}", file=sys.stderr)
    sys.stderr.flush()
    print("SystemExit caught in main experiment")
    sys.stdout.flush()
    raise
except Exception as e:
    # Catch any unhandled exceptions in the main experiment
    print("="*60)
    sys.stdout.flush()
    print("EXCEPTION CAUGHT IN MAIN EXPERIMENT BLOCK")
    sys.stdout.flush()
    print("="*60)
    sys.stdout.flush()
    print(f"Exception: {e}")
    sys.stdout.flush()
    print(f"Error type: {type(e).__name__}")
    sys.stdout.flush()
    print(f"Window state: win = {win}")
    sys.stdout.flush()
    import traceback
    print("Full traceback:")
    sys.stdout.flush()
    traceback.print_exc()
    print("="*60)
    sys.stdout.flush()
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
    try:
        core.quit()
    except:
        pass
    exit(1)
except BaseException as be:
    print("="*60, file=sys.stderr)
    print("UNKNOWN EXCEPTION CAUGHT IN MAIN EXPERIMENT BLOCK", file=sys.stderr)
    print(f"Exception type: {type(be).__name__}", file=sys.stderr)
    print(f"Exception value: {be}", file=sys.stderr)
    print("="*60, file=sys.stderr)
    sys.stderr.flush()
    print("="*60)
    sys.stdout.flush()
    print("UNKNOWN EXCEPTION CAUGHT IN MAIN EXPERIMENT BLOCK")
    sys.stdout.flush()
    print("="*60)
    sys.stdout.flush()
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    traceback.print_exc()
    print("="*60)
    sys.stdout.flush()
    if win is not None:
        try:
            win.close()
        except Exception:
            pass
    print("Press Enter to exit...")
    try:
        input()
    except:
        pass
    try:
        core.quit()
    except:
        pass
    exit(1)
finally:
    # Cleanup - this block always executes
    # Window and core.quit() are handled in the try/except blocks above
    pass
