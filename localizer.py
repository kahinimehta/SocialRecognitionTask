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

# Exit button: always top-right, consistent position and hit area for touch screens
EXIT_BTN_POS = (0.45, 0.47)  # Top-right corner (units='height')
EXIT_HIT_MARGIN = 0.05  # Larger margin for reliable touch registration

# Photodiode detector: black rectangle in bottom-left (0.5" x 1"), drawn on each flip except input/name screens
PHOTODIODE_ACTIVE = True  # Set False during get_input_method (temp_win) and get_participant_id
photodiode_patch = None  # Created after main window exists
_last_photodiode_ttl_timestamp = [None]  # Set at exact moment of photodiode flash + TTL (for CSV alignment)

# TTL trigger: parallel port pulse when photodiode appears (Windows/Linux; no-op on macOS)
_ttl_parallel = None  # Lazy-init
def _send_ttl_trigger():
    """Send a brief TTL pulse via parallel port when photodiode appears. Fails silently if unavailable."""
    global _ttl_parallel
    try:
        if _ttl_parallel is False:
            return  # Previously failed to init
        if _ttl_parallel is None:
            try:
                from psychopy import parallel
                addr = int(os.environ.get('PARALLEL_PORT_ADDRESS', '0x0378'), 16)
                parallel.setPortAddress(addr)
                _ttl_parallel = parallel
            except Exception:
                _ttl_parallel = False
                return
        if _ttl_parallel:
            _ttl_parallel.setData(255)
            core.wait(0.01)
            _ttl_parallel.setData(0)
    except Exception:
        pass

def safe_wait(duration):
    """Wrapper for core.wait() that handles macOS event dispatch errors (e.g. NSTrackingArea)"""
    try:
        core.wait(duration)
    except AttributeError as e:
        err_str = str(e)
        if "type" in err_str and ("ObjCInstance" in err_str or "NSConcreteNotification" in err_str or "NSTrackingArea" in err_str):
            pass
        else:
            raise
    except Exception:
        pass

def wait_with_escape(duration):
    """Wait for duration, checking for ESC every 0.05s. If ESC pressed, quit immediately."""
    elapsed = 0.0
    chunk = 0.05
    while elapsed < duration:
        # Check ESC FIRST before any wait (event.getKeys is destructive)
        try:
            keys = event.getKeys(keyList=['escape'])
            if keys and 'escape' in keys:
                core.quit()
        except (AttributeError, RuntimeError):
            pass
        remaining = min(chunk, duration - elapsed)
        if remaining > 0:
            safe_wait(remaining)
        elapsed += remaining

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
            color='lightgray',
            units='height',
            fullscr=True,
            allowGUI=True,
            waitBlanking=False,  # Prevent blocking on display sync
            useFBO=False  # Disable framebuffer objects to prevent hangs
        )
        temp_win.flip()
        
        prompt_text = visual.TextStim(
            temp_win,
            text="What input method are you using?\n\n"
                 "Double tap for touch screen, or press Right Arrow for keyboard:\n\n"
                 "(Press ESC or tap Exit to leave fullscreen)",
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
            text="TOUCH SCREEN\n(Double tap)", 
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
            text="KEYBOARD\n(Press Right Arrow)", 
            color='black', 
            height=24/720*0.75, 
            pos=(320/720*0.6, -80/720*0.6),
            units='height'
        )
        
        # Exit button (top-right): for touch screen to leave fullscreen; ESC works on laptop
        exit_btn = visual.Rect(
            temp_win,
            width=0.12,
            height=0.04,
            fillColor=[0.95, 0.85, 0.85],
            lineColor='darkred',
            pos=(0.45, 0.47),
            lineWidth=1,
            units='height'
        )
        exit_text = visual.TextStim(temp_win, text="Exit", color='darkred', height=0.025, pos=(0.45, 0.47), units='height')
        
        mouse_temp = event.Mouse(win=temp_win)
        mouse_temp.setVisible(True)
        
        def draw_selection_screen():
            prompt_text.draw()
            button1.draw()
            button1_text.draw()
            button2.draw()
            button2_text.draw()
            exit_btn.draw()
            exit_text.draw()
            temp_win.flip()
        
        draw_selection_screen()
        # Clear events BEFORE loop starts, not inside loop
        event.clearEvents()
        selected = None
        
        # BUTTON PRESS DETECTION: Track button state for press/release detection
        prev_mouse_buttons = [False, False, False]
        
        while selected is None:
            # Check for keys FIRST with explicit keyList for reliable registration
            try:
                keys = event.getKeys(keyList=['escape', '1', '2', 'right', 'num_1', 'num_2'])
                if keys:
                    if 'escape' in keys:
                        return None, None  # Signal to exit - window will be closed in exception handler
                    if '1' in keys or 'num_1' in keys:
                        USE_TOUCH_SCREEN = True
                        selected = 'touch'
                        break
                    # Right arrow (preferred) or 2 for keyboard - more reliable than 2 alone
                    if 'right' in keys or '2' in keys or 'num_2' in keys:
                        USE_TOUCH_SCREEN = False
                        selected = 'click'
                        break
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking keys: {e}", file=sys.stderr)
            
            # Redraw screen
            draw_selection_screen()
            
            try:
                mouse_buttons = mouse_temp.getPressed()
                mouseloc = mouse_temp.getPos()
                
                # Check for button release (was pressed, now released)
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    # Button was released - check if it was over Exit button first
                    try:
                        if exit_btn.contains(mouseloc):
                            return None, None
                    except Exception:
                        pass
                    try:
                        mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                    except (TypeError, ValueError, IndexError):
                        mouseloc_x, mouseloc_y = 0.0, 0.0
                    exit_margin = 0.04  # Larger hit area for touch
                    if 0.39 - exit_margin <= mouseloc_x <= 0.51 + exit_margin and 0.45 - exit_margin <= mouseloc_y <= 0.49 + exit_margin:
                        return None, None
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
            
            # Do NOT clear events every iteration - preserves key presses for reliable registration
            core.wait(0.02)  # 20 ms polling - allows key to register before next check
        
        # Show confirmation - use height units to match temp window
        confirm_text = visual.TextStim(
            temp_win,
            text=f"Input method set to:\n{'TOUCH SCREEN' if USE_TOUCH_SCREEN else 'KEYBOARD'}\n\n{'Use Return for all buttons.' if not USE_TOUCH_SCREEN else ''}",
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
            # KEYBOARD mode: wait for Return key press (no mouse)
            while not clicked:
                try:
                    keys = event.getKeys(keyList=['escape', 'return'])
                    if keys and 'escape' in keys:
                        return None, None
                    if keys and 'return' in keys:
                        continue_click_time = time.time()
                        clicked = True
                        break
                except (AttributeError, RuntimeError) as e:
                    print(f"Warning: Error checking keys in continue loop: {e}", file=sys.stderr)
                
                confirm_text.draw()
                continue_button.draw()
                continue_text.draw()
                temp_win.flip()
                
                event.clearEvents()
                core.wait(0.01)
        
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

def object_to_question(object_name):
    """Convert object name to question text.
    
    E.g., 'Giraffe' -> "Was the last object a giraffe?"
    E.g., 'Elephant' -> "Was the last object an elephant?"
    """
    if not object_name:
        return "Was the last object shown?"
    obj_lower = object_name.lower().strip()
    if not obj_lower:
        return "Was the last object shown?"
    vowels = ['a', 'e', 'i', 'o', 'u']
    article = "an" if obj_lower[0] in vowels else "a"
    return f"Was the last object {article} {obj_lower}?"

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
    global PHOTODIODE_ACTIVE
    PHOTODIODE_ACTIVE = False  # Exclude name entry from photodiode
    
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
            id_prompt = visual.TextStim(win, text="Enter participant ID:", color='black', height=0.045*0.75*1.35, wrapWidth=1.4*0.75, pos=(0, 0.42*0.6))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75*1.35, pos=(0, 0.25*0.6))
            print("input_display created")
        else:
            print("Creating mouse/trackpad text stimuli...")
            id_prompt = visual.TextStim(win, text="Enter participant ID:\n\nHit Enter when done.", color='black', height=0.045*0.75*1.35, wrapWidth=1.4*0.75, pos=(0, 0.3*0.6))
            print("id_prompt created")
            input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75*1.35, pos=(0, 0.1*0.6))
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
                    
                    button = visual.Rect(win, width=button_width, height=0.08*0.75*1.35, fillColor='lightgray', 
                                        lineColor='black', pos=(x_pos, y_pos))
                    text = visual.TextStim(win, text=key, color='black', height=0.04*0.75*1.35, pos=(x_pos, y_pos))
                    row_buttons.append((button, text, key, x_pos, y_pos))
                
                keyboard_buttons.append(row_buttons)
            
            print("Creating special buttons...")
            # Special buttons - arranged horizontally between input and keyboard
            button_y_pos = 0.05*0.6  # Position between input (0.25) and keyboard start (-0.15)
            backspace_button = visual.Rect(win, width=0.3*0.75, height=0.1*0.75*1.35, fillColor='lightcoral', 
                                          lineColor='black', lineWidth=2*0.75, pos=(-0.25*0.6, button_y_pos))
            backspace_text = visual.TextStim(win, text="BACKSPACE", color='black', height=0.025*0.75*1.35, pos=(-0.25*0.6, button_y_pos))
            
            continue_button = visual.Rect(win, width=0.3*0.75, height=0.1*0.75*1.35, fillColor='lightgreen', 
                                          lineColor='black', lineWidth=2*0.75, pos=(0.25*0.6, button_y_pos))
            continue_text = visual.TextStim(win, text="CONTINUE", color='black', height=0.025*0.75*1.35, pos=(0.25*0.6, button_y_pos))
            exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
            exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
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
            exit_btn.draw()
            exit_text.draw()
        
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
                core.quit()
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
                # Check Exit button FIRST (top-right, always clickable)
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                if on_exit:
                    core.quit()  # Exit always responsive (no minRT)
                # Check keyboard buttons
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
                        backspace_width, backspace_height = 0.3*0.75, 0.1*0.75
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
                                        PHOTODIODE_ACTIVE = True
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
                                        PHOTODIODE_ACTIVE = True
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
            # Check escape again before clearing (clearEvents can wipe keys pressed during redraw)
            try:
                keys = event.getKeys(keyList=['escape'], timeStamped=False)
                if keys and 'escape' in keys:
                    core.quit()
            except (AttributeError, RuntimeError):
                pass
            # Clear events only once per loop iteration, after all checks
            event.clearEvents()
            core.wait(0.001)  # Very fast polling
        else:
            # Standard keyboard input for click mode - safe handling of empty keys
            try:
                keys = event.getKeys(keyList=None, timeStamped=False)
                if keys:  # Only process if keys is not empty
                    if 'escape' in keys:
                        core.quit()
                    for key in keys:
                        if key == 'escape':
                            continue  # Already handled above
                        elif key == 'return' or key == 'enter':
                            if input_id.strip():
                                mouse.setVisible(False)
                                event.clearEvents()
                                PHOTODIODE_ACTIVE = True
                                return input_id.strip()
                        elif key == 'backspace':
                            input_id = input_id[:-1] if input_id else ""
                            input_display.text = input_id if input_id else "_"
                            redraw()
                        elif len(key) == 1:
                            input_id += key
                            input_display.text = input_id if input_id else "_"
                            redraw()
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
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.5*0.6)  # Moved even closer to bottom
    )
    display_button_text = button_text
    continue_text = visual.TextStim(
        win,
        text=display_button_text,
        color='black',
        height=0.05*0.75*1.35,
        pos=(0, -0.5*0.6)  # Moved even closer to bottom
    )
    
    # Exit button (top-right): tap to leave fullscreen on touch screen; ESC on laptop
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    first_draw_done = [False]
    def draw_content():
        if additional_stimuli:
            for stim in additional_stimuli:
                stim.draw()
        continue_button.draw()
        continue_text.draw()
        exit_btn.draw()
        exit_text.draw()
    def draw_screen():
        if not first_draw_done[0]:
            _do_photodiode_flash(draw_content)  # Instruction/continue onset: black (TTL), white
            first_draw_done[0] = True
        else:
            draw_content()
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
            # Check for escape key
            try:
                keys = event.getKeys(keyList=['escape'], timeStamped=False)
                if keys and 'escape' in keys:
                    core.quit()
            except (AttributeError, RuntimeError):
                pass
            
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                t = clock.getTime()
                
                # Check if mouse position has changed (touch moved)
                if mouseloc_x != mouserec_x or mouseloc_y != mouserec_y:
                    # Position has changed - check if touch is within button
                    # Exit button: use explicit bounds for reliable touch registration
                    on_exit_btn = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                  EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    try:
                        if (on_exit_btn or exit_btn.contains(mouseloc)):
                            core.quit()
                        elif continue_button.contains(mouseloc):
                            if t > minRT:
                                _do_photodiode_flash(draw_content)  # Participant response: black (TTL), white
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
                        # Fallback to manual calculation (including exit button)
                        if on_exit_btn:
                            core.quit()
                        hit_margin = 0.02*0.75
                        button_x, button_y = 0.0, -0.5*0.6  # Updated to match new button position
                        button_width, button_height = 0.3*0.75, 0.1*0.75
                        if (button_x - button_width/2 - hit_margin <= mouseloc_x <= button_x + button_width/2 + hit_margin and
                            button_y - button_height/2 - hit_margin <= mouseloc_y <= button_y + button_height/2 + hit_margin):
                            if t > minRT:
                                _do_photodiode_flash(draw_content)  # Participant response: black (TTL), white
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
                
                # Redraw once per iteration (avoids double-flip that could cause photodiode flicker)
                draw_screen()
                safe_wait(0.016)  # ~60 Hz to reduce photodiode flicker on touch
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                # Log specific errors instead of silently ignoring
                print(f"Warning: Error in wait_for_button touch screen loop: {e}", file=sys.stderr)
            
            # Check keys AFTER processing touch, BEFORE clearing events
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'escape' in keys:
                        core.quit()
                    elif 'space' in keys:
                        _do_photodiode_flash(draw_content)  # Participant response: black (TTL), white
                        clicked = True
                        break
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking space key in wait_for_button: {e}", file=sys.stderr)
            
            # Clear events AFTER checking keys
            event.clearEvents()
    else:
        # Keyboard mode: wait for Return key press (no mouse)
        while not clicked:
            draw_screen()
            try:
                keys = event.getKeys(keyList=['return', 'escape'], timeStamped=False)
                if keys:
                    if 'return' in keys:
                        _do_photodiode_flash(draw_content)  # Participant response: black (TTL), white
                        clicked = True
                        break
                    if 'escape' in keys:
                        core.quit()
            except (AttributeError, RuntimeError):
                pass
            safe_wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()

def ask_object_question(object_name, timeout=10.0):
    """Ask object question and return (answer, timed_out, response_time, answer_click_time, question_trigger) tuple
    
    Args:
        object_name: Object name for the question (e.g., "Giraffe", "Elephant")
        timeout: Timeout in seconds (default 10.0)
    
    Returns:
        tuple: (answer: bool or None, timed_out: bool, response_time: float, answer_click_time: float or None)
    """
    question_text = object_to_question(object_name)
    if not USE_TOUCH_SCREEN:
        question_text += "\n\n(Press LEFT for YES, RIGHT for NO)"
    
    # Create question display
    question_stim = visual.TextStim(
        win,
        text=question_text,
        color='black',
        height=0.06*0.75*1.35,
        pos=(0, 0.4*0.6),  # Move higher to avoid overlap with larger images
        wrapWidth=1.4*0.75
    )
    
    # Create YES and NO buttons
    yes_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightgreen',
        lineColor='black',
        pos=(-0.3*0.6, -0.2*0.6)
    )
    yes_text = visual.TextStim(
        win,
        text="YES",
        color='black',
        height=0.05*0.75*1.35,
        pos=(-0.3*0.6, -0.2*0.6)
    )
    
    no_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightcoral',
        lineColor='black',
        pos=(0.3*0.6, -0.2*0.6)
    )
    no_text = visual.TextStim(
        win,
        text="NO",
        color='black',
        height=0.05*0.75*1.35,
        pos=(0.3*0.6, -0.2*0.6)
    )
    
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    def draw_question():
        question_stim.draw()
        yes_button.draw()
        yes_text.draw()
        no_button.draw()
        no_text.draw()
        exit_btn.draw()
        exit_text.draw()
        win.flip()
    
    draw_question()
    question_trigger = time.time()
    
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
            # Check for escape FIRST, before any other processing
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:
                    core.quit()
            except (AttributeError, RuntimeError):
                pass
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
                    on_exit_btn = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                  EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    try:
                        if (on_exit_btn or exit_btn.contains(mouseloc)):
                            core.quit()
                        # Check YES button
                        elif yes_button.contains(mouseloc):
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
                        # Fallback to manual calculation (including exit button)
                        if on_exit_btn:
                            core.quit()
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
            
            # Check keys AFTER processing touch, BEFORE clearing events
            try:
                keys = event.getKeys(keyList=['y', 'n', 'escape'], timeStamped=False)
                if keys:
                    if 'escape' in keys:
                        core.quit()
                    elif 'y' in keys:
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
        # Keyboard mode: LEFT = YES, RIGHT = NO
        while not answered:
            # Check for timeout first
            elapsed_time = clock.getTime()
            if elapsed_time >= timeout:
                timed_out = True
                response_time = timeout
                answered = True
                break
            
            draw_question()
            try:
                keys = event.getKeys(keyList=['left', 'right', 'escape'], timeStamped=False)
                if keys:
                    if 'escape' in keys:
                        core.quit()
                    if 'left' in keys:
                        answer = True
                        response_time = clock.getTime()
                        answer_click_time = time.time()
                        answered = True
                        break
                    if 'right' in keys:
                        answer = False
                        response_time = clock.getTime()
                        answer_click_time = time.time()
                        answered = True
                        break
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking keys in ask_object_question: {e}", file=sys.stderr)
            
            safe_wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()
    
    # Show timeout message if timed out
    if timed_out:
        timeout_message = visual.TextStim(
            win,
            text="Time's up! We've moved on to the next image.",
            color='red',
            height=0.06*1.35,
            pos=(0, 0),
            wrapWidth=1.4
        )
        timeout_message.draw()
        win.flip()
        wait_with_escape(2.0)  # Show message for 2 seconds. ESC works during wait.
    
    return (answer, timed_out, response_time, answer_click_time, question_trigger)

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
        
        print("DEBUG: Calling visual.Window(size=(1400, 900), fullscr=True)...", file=sys.stderr)
        sys.stderr.flush()
        
        win = visual.Window(
            size=(1400, 900), 
            color='lightgray', 
            units='height',
            fullscr=True,
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
        
        # Photodiode created AFTER name entry (see below) - not during window creation
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
        test_text = visual.TextStim(win, text=" ", color='black', height=0.05*0.75*1.35, pos=(0, 0))
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
    fixation = visual.TextStim(win, text="+", color='black', height=0.08*0.75*1.35, pos=(0, 0))
    
    def show_fixation(duration=1.0, return_onset=False, return_offset_trigger=False):
        """Display fixation cross for specified duration. Photodiode stays white; flashes black (TTL) then white at onset/offset."""
        _do_photodiode_flash(lambda: fixation.draw())  # Onset: black (TTL), white
        onset_trigger = _last_photodiode_ttl_timestamp[0] if _last_photodiode_ttl_timestamp[0] is not None else time.time()
        wait_with_escape(duration)
        _do_photodiode_flash(lambda: _blank_rect.draw())  # Offset: black (TTL), white
        offset_trigger = _last_photodiode_ttl_timestamp[0] if _last_photodiode_ttl_timestamp[0] is not None else time.time()
        if return_onset and return_offset_trigger:
            return onset_trigger, offset_trigger
        return onset_trigger if return_onset else None

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

    # Create photodiode and install wrapper AFTER name is submitted. White baseline; flashes black (TTL) then white per event.
    PHOTODIODE_ACTIVE = True  # Re-enable for main task
    _blank_rect = visual.Rect(win, width=3, height=3, fillColor='lightgray', lineColor=None, pos=(0, 0), units='height')
    try:
        photodiode_patch = visual.Rect(
            win, width=0.03, height=0.01,  # 1/4 exit button size
            fillColor='white', lineColor=None,
            pos=(-0.49, -0.45),  # Extreme left of screen
            units='height'
        )
        _photodiode_signal_next_flip = [False]
        def _signal_photodiode_event():
            _photodiode_signal_next_flip[0] = True
        def _do_photodiode_flash(draw_func):
            """Signal photodiode, then flip black (TTL) then white. No artificial delays—timestamps align to screen change."""
            _signal_photodiode_event()
            if draw_func:
                draw_func()
            win.flip()  # Black flash, TTL
            if draw_func:
                draw_func()
            win.flip()  # White (baseline)
        _orig_flip = win.flip
        def _wrapped_flip(*args, **kwargs):
            did_flash = False
            if PHOTODIODE_ACTIVE and photodiode_patch is not None:
                # Always start white (baseline). Flash black only when explicitly signaled.
                photodiode_patch.fillColor = 'white'
                if _photodiode_signal_next_flip[0]:
                    photodiode_patch.fillColor = 'black'
                    _photodiode_signal_next_flip[0] = False
                    did_flash = True
                photodiode_patch.draw()
            # TTL at exact flip moment – callOnFlip fires when screen changes, same time as photodiode flash
            if PHOTODIODE_ACTIVE and photodiode_patch is not None and did_flash:
                def _on_flash():
                    _last_photodiode_ttl_timestamp[0] = time.time()
                    _send_ttl_trigger()
                win.callOnFlip(_on_flash)
            result = _orig_flip(*args, **kwargs)
            return result
        win.flip = _wrapped_flip
    except Exception as e:
        print(f"Warning: Could not create photodiode patch: {e}", file=sys.stderr)

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

    # Build list of all unique object names (for wrong-object questions)
    all_object_names = sorted(set(s['object_name'] for s in all_stimuli))

    # Pre-generate randomized sequence for question objects (exactly 50% correct, 50% random)
    # There are 20 questions total (every 10th trial out of 200 trials)
    num_questions = 20
    num_correct_questions = num_questions // 2  # Exactly 10 correct, 10 random
    question_sequence = [True] * num_correct_questions + [False] * (num_questions - num_correct_questions)
    random.shuffle(question_sequence)  # Randomize the order
    question_index = 0  # Track which question we're on

    # Show instructions
    instructions = visual.TextStim(
        win,
        text="LOCALIZER TASK\n\n"
             "You will see 200 images one at a time.\n"
             "Every few images, you will be asked a question about the previous image.\n"
             "Your total score will be shown at the end of the task.\n",
        color='black',
        height=0.05*0.75*1.35,
        pos=(0, 0),
        wrapWidth=1.4*0.75
    )

    def draw_instructions():
        instructions.draw()
    _do_photodiode_flash(draw_instructions)  # First instruction onset: black (TTL), white
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
            'localizer_fixation_onset_trigger', 'localizer_fixation_offset_trigger', 'fixation_duration',
            'localizer_image_onset_trigger', 'localizer_image_offset_trigger', 'is_question_trial', 
            'question_object', 'question_text', 'question_trigger', 
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
    localizer_fixation_onset_trigger_first, localizer_fixation_offset_trigger_first = show_fixation(fixation_duration_first, return_onset=True, return_offset_trigger=True)
    
    for idx, stimulus in enumerate(all_stimuli, 1):
        # Record presentation time
        presentation_time = datetime.now()
        presentation_timestamp = presentation_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Show jittered fixation between images (except before first image, which was already shown)
        if idx > 1:
            fixation_duration = random.uniform(0.25, 0.75)
            localizer_fixation_onset_trigger, localizer_fixation_offset_trigger = show_fixation(fixation_duration, return_onset=True, return_offset_trigger=True)
        else:
            fixation_duration = fixation_duration_first
            localizer_fixation_onset_trigger = localizer_fixation_onset_trigger_first
            localizer_fixation_offset_trigger = localizer_fixation_offset_trigger_first
        
        # Load and display image; photodiode flashes at fixation onset/offset, image onset/offset
        try:
            img = visual.ImageStim(win, image=stimulus['path'], size=(0.8*0.75*1.35, 0.8*0.75*1.35))
            _do_photodiode_flash(lambda: img.draw())  # Image onset: black (TTL), white
            localizer_image_onset_trigger = _last_photodiode_ttl_timestamp[0] if _last_photodiode_ttl_timestamp[0] is not None else time.time()
            
            # Show image for exactly 0.5 seconds (fixed duration). ESC works during wait.
            wait_with_escape(0.5)
            _do_photodiode_flash(lambda: _blank_rect.draw())  # Image offset: black (TTL), white
            localizer_image_offset_trigger = _last_photodiode_ttl_timestamp[0] if _last_photodiode_ttl_timestamp[0] is not None else time.time()
            
            # Check if this is the 10th image (or every 10th after the first)
            is_question_trial = (idx % 10 == 0)
            
            if is_question_trial:
                # Ask object question about the image we just showed (the 10th, 20th, 30th, etc.)
                current_stimulus = stimulus
                correct_object = current_stimulus['object_name']
                
                # Use pre-generated randomized sequence to ensure exactly 50% correct, 50% random
                if question_index < len(question_sequence):
                    ask_about_correct = question_sequence[question_index]
                    question_index += 1
                else:
                    ask_about_correct = random.choice([True, False])
                
                if ask_about_correct:
                    question_object = correct_object
                    correct_answer = True
                else:
                    # 50% of trials: ask about a random incorrect object (from all other objects)
                    wrong_objects = [o for o in all_object_names if o != correct_object]
                    question_object = random.choice(wrong_objects) if wrong_objects else correct_object
                    correct_answer = False
                
                answer, timed_out, response_time, answer_click_time, question_trigger = ask_object_question(question_object, timeout=10.0)
                is_correct = (answer == correct_answer) if not timed_out else None
                
                # No per-trial feedback; feedback shown at end only
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
                    'localizer_fixation_onset_trigger': localizer_fixation_onset_trigger,
                    'localizer_fixation_offset_trigger': localizer_fixation_offset_trigger,
                    'fixation_duration': fixation_duration,
                    'localizer_image_onset_trigger': localizer_image_onset_trigger,
                    'localizer_image_offset_trigger': localizer_image_offset_trigger,
                    'is_question_trial': True,
                    'question_object': question_object,
                    'question_text': object_to_question(question_object),
                    'question_trigger': question_trigger,
                    'answer': answer if not timed_out else 'TIMEOUT',
                    'correct_answer': correct_answer,
                    'correct': is_correct,
                    'timed_out': timed_out,
                    'response_time': response_time if response_time is not None else None,
                    'answer_click_time': answer_click_time
                }
            else:
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
                    'localizer_fixation_onset_trigger': localizer_fixation_onset_trigger,
                    'localizer_fixation_offset_trigger': localizer_fixation_offset_trigger,
                    'fixation_duration': fixation_duration,
                    'localizer_image_onset_trigger': localizer_image_onset_trigger,
                    'localizer_image_offset_trigger': localizer_image_offset_trigger,
                    'is_question_trial': False,
                    'question_object': None,
                    'question_text': None,
                    'question_trigger': None,
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

    # Calculate accuracy for question trials
    question_trials = [trial for trial in localizer_data if trial.get('is_question_trial', False)]
    if question_trials:
        correct_count = sum(1 for trial in question_trials if trial.get('correct') is True)
        total_questions = len(question_trials)
        accuracy_percent = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        accuracy_text = f"Your accuracy: {correct_count}/{total_questions} ({accuracy_percent:.1f}%)"
    else:
        accuracy_text = "No questions answered"
    
    # Show accuracy message
    accuracy_display = visual.TextStim(
        win,
        text=accuracy_text,
        color='black',
        height=0.06*0.75*1.35,
        pos=(0, 0.1),
        wrapWidth=1.4*0.75
    )
    
    # Show completion message
    completion_text = visual.TextStim(
        win,
        text="LOCALIZER TASK COMPLETE!\n\n"
             "Thank you for your participation.",
        color='black',
        height=0.06*0.75*1.35,
        pos=(0, -0.1),
        wrapWidth=1.4*0.75
    )

    accuracy_display.draw()
    completion_text.draw()
    win.flip()
    wait_for_button("EXIT", additional_stimuli=[accuracy_display, completion_text])

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
