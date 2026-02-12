# Suppress iohub import errors (numpy/tables compatibility issue)
import warnings
import sys
import os

# Suppress the specific numpy/tables compatibility warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources.*')
warnings.filterwarnings('ignore', message='.*numpy.dtype size changed.*')

# Prevent iohub from being imported (causes numpy/tables compatibility issues)
os.environ['PSYCHOPY_IOHUB'] = '0'

# Monkey-patch to prevent tables import error from crashing
import builtins
_original_import = builtins.__import__

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Import wrapper that catches numpy/tables compatibility errors"""
    if 'tables' in name or 'iohub' in name:
        try:
            return _original_import(name, globals, locals, fromlist, level)
        except (ValueError, ImportError) as e:
            if 'numpy.dtype size changed' in str(e) or 'binary incompatibility' in str(e):
                # Suppress the error and return a dummy module
                import types
                dummy_module = types.ModuleType(name)
                print(f"Warning: Suppressed import error for {name}: {e}", file=sys.stderr)
                return dummy_module
            raise
    return _original_import(name, globals, locals, fromlist, level)

builtins.__import__ = _safe_import

# Suppress stderr temporarily during psychopy import to catch iohub errors
import io
from contextlib import redirect_stderr

# Try importing psychopy with stderr suppressed
stderr_buffer = io.StringIO()
try:
    with redirect_stderr(stderr_buffer):
        from psychopy import visual, core, event
except Exception as e:
    # If import fails, try again without suppression to see the real error
    print(f"Warning: Error importing psychopy: {e}", file=sys.stderr)
    from psychopy import visual, core, event

import random, time, re
import numpy as np
import csv
from datetime import datetime
from PIL import Image, ImageDraw
import math
import sys
import traceback
import platform

# Force stdout to flush after each print
def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

# Use print_flush for critical messages, but keep regular print for compatibility

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
                 "Touch or click the button below:\n\n"
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
        
        exit_btn = visual.Rect(temp_win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=(0.45, 0.47), lineWidth=1, units='height')
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
                
                # Convert mouse position to floats
                try:
                    if hasattr(mouseloc, '__len__') and len(mouseloc) >= 2:
                        mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                    else:
                        mouseloc_x, mouseloc_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Get button positions and sizes
                hit_margin = 150/720*0.75
                button1_x, button1_y = -320/720*0.6, -80/720*0.6
                button1_width, button1_height = 520/720*0.75, 180/720*0.75
                button2_x, button2_y = 320/720*0.6, -80/720*0.6
                button2_width, button2_height = 520/720*0.75, 180/720*0.75
                
                # Check if mouse is over buttons
                on_button1 = (button1_x - button1_width/2 - hit_margin <= mouseloc_x <= button1_x + button1_width/2 + hit_margin and
                              button1_y - button1_height/2 - hit_margin <= mouseloc_y <= button1_y + button1_height/2 + hit_margin)
                on_button2 = (button2_x - button2_width/2 - hit_margin <= mouseloc_x <= button2_x + button2_width/2 + hit_margin and
                              button2_y - button2_height/2 - hit_margin <= mouseloc_y <= button2_y + button2_height/2 + hit_margin)
                exit_margin = 0.04  # Larger hit area for touch reliability
                on_exit = (0.39 - exit_margin <= mouseloc_x <= 0.51 + exit_margin and
                           0.45 - exit_margin <= mouseloc_y <= 0.49 + exit_margin)
                
                # Check for button release (was pressed, now released)
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_exit:
                        return None, None
                    # Button was released - check if it was over a button
                    elif on_button1:
                        USE_TOUCH_SCREEN = True
                        selected = 'touch'
                        button1.fillColor = 'green'
                        draw_selection_screen()
                        core.wait(0.05)
                        break
                    elif on_button2:
                        USE_TOUCH_SCREEN = False
                        selected = 'click'
                        button2.fillColor = 'blue'
                        draw_selection_screen()
                        core.wait(0.05)
                        break
                
                # Also check for button press (for touch screens, press and release happen quickly)
                if mouse_buttons[0] and not prev_mouse_buttons[0]:
                    if on_exit:
                        return None, None
                    elif on_button1:
                        USE_TOUCH_SCREEN = True
                        selected = 'touch'
                        button1.fillColor = 'green'
                        draw_selection_screen()
                        core.wait(0.05)
                        break
                    elif on_button2:
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
                        # Position has changed - check if touch is within button using position calculation
                        hit_margin = 50/720*0.75
                        button_x, button_y = 0.0, -150.0/720*0.6
                        button_width, button_height = 300/720*0.75, 80/720*0.75
                        on_button = (button_x - button_width/2 - hit_margin <= mouseloc_cont_x <= button_x + button_width/2 + hit_margin and
                                     button_y - button_height/2 - hit_margin <= mouseloc_cont_y <= button_y + button_height/2 + hit_margin)
                        
                        if on_button:
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
                    
                    # Convert mouse position to floats
                    try:
                        if hasattr(mouseloc_cont, '__len__') and len(mouseloc_cont) >= 2:
                            mouseloc_cont_x, mouseloc_cont_y = float(mouseloc_cont[0]), float(mouseloc_cont[1])
                        else:
                            mouseloc_cont_x, mouseloc_cont_y = 0.0, 0.0
                    except (TypeError, ValueError):
                        mouseloc_cont_x, mouseloc_cont_y = 0.0, 0.0
                    
                    # Get button bounds
                    hit_margin = 50/720*0.75
                    button_x, button_y = 0.0, -150.0/720*0.6
                    button_width, button_height = 300/720*0.75, 80/720*0.75
                    
                    # Check if mouse is over button
                    on_button = (button_x - button_width/2 - hit_margin <= mouseloc_cont_x <= button_x + button_width/2 + hit_margin and
                                 button_y - button_height/2 - hit_margin <= mouseloc_cont_y <= button_y + button_height/2 + hit_margin)
                    
                    # Check for button release (was pressed, now released)
                    if prev_mouse_buttons_cont[0] and not mouse_buttons_cont[0]:
                        if on_button:
                            continue_click_time = time.time()  # Record exact time of click
                            clicked = True
                            break
                    
                    # Also check for button press (for touch screens, press and release happen quickly)
                    if mouse_buttons_cont[0] and on_button and not prev_mouse_buttons_cont[0]:
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
    print(f"Input method type: {type(result)}")
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
    except:
        pass
    core.quit()
    exit(1)

if result is None:
    print("Input method selection cancelled. Exiting...")
    print("Press Enter to exit...")
    try:
        input()
    except:
        pass
    core.quit()
    exit(0)

print(f"Input method selected: {'TOUCH SCREEN' if result else 'MOUSE/TRACKPAD'}")
print(f"Result value: {result}, Type: {type(result)}")
print("About to create main window...")

# Create main window with appropriate settings - use try/finally pattern
win = None
try:
    print("="*60)
    sys.stdout.flush()
    print("STARTING WINDOW CREATION")
    sys.stdout.flush()
    print("="*60)
    sys.stdout.flush()
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
        test_text = visual.TextStim(win, text=" ", color='black', height=0.04*0.75*1.35, pos=(0, 0))
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
    print("="*60)
    print("WINDOW CREATION SUCCESSFUL")
    print("="*60)
    
    # Don't close temp window - keep it open to prevent PsychoPy from auto-quitting
    # Closing it causes PsychoPy to detect all windows are closed and quit
    # We'll just leave it open (it's behind the main window anyway)
    if temp_win is not None:
        print("DEBUG: Keeping temp window open to prevent PsychoPy auto-quit", file=sys.stderr)
        sys.stderr.flush()
        # Don't close temp_win - leave it open
    
except Exception as e:
    print("="*60)
    print("EXCEPTION CAUGHT IN WINDOW CREATION")
    print("="*60)
    print(f"ERROR creating main window: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("="*60)
    print("CRITICAL ERROR: Failed to create main window")
    print("="*60)
    if win is not None:
        try:
            win.close()
        except Exception as e:
            print(f"ERROR calling win.close(): {repr(e)}", file=sys.stderr)
            traceback.print_exc()
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
except SystemExit:
    print("SystemExit caught - program is exiting")
    raise
except:
    print("="*60)
    print("UNKNOWN EXCEPTION CAUGHT IN WINDOW CREATION")
    print("="*60)
    import traceback
    traceback.print_exc()
    print("="*60)
    if win is not None:
        try:
            win.close()
        except Exception as e:
            print(f"ERROR calling win.close(): {repr(e)}", file=sys.stderr)
            traceback.print_exc()
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

# =========================
#  GENERATE PRACTICE STIMULI
# =========================
def generate_practice_shapes(output_dir="PLACEHOLDERS"):
    """Generate the 3 specific practice shapes: green circle, red circle, blue circle"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Green circle (practice shape 1)
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='green', outline='black', width=3)
    img.save(os.path.join(output_dir, "PRACTICE_GREEN_CIRCLE.png"))
    
    # Red circle (practice shape 2)
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='red', outline='black', width=3)
    img.save(os.path.join(output_dir, "PRACTICE_RED_CIRCLE.png"))
    
    # Blue circle (practice shape 3)
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='blue', outline='black', width=3)
    img.save(os.path.join(output_dir, "PRACTICE_BLUE_CIRCLE.png"))
    
    print(f"✓ Generated 3 practice shapes in {output_dir}/")

# =========================
#  GENERATE PLACEHOLDER STIMULI
# =========================
def generate_placeholder_stimuli(num_stimuli=100, output_dir="PLACEHOLDERS"):
    """Generate placeholder stimuli: circles (studied) and squares (lures)
    
    For 50% of pairs, swap so squares are studied items and circles are lures.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate distinct colors for each stimulus
    colors = []
    for i in range(num_stimuli):
        # Generate distinct colors using HSV
        hue = (i * 137.508) % 360  # Golden angle for good distribution
        saturation = 0.7 + (i % 3) * 0.1
        value = 0.6 + (i % 2) * 0.3
        
        # Convert HSV to RGB
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue/360, saturation, value)
        colors.append((int(r*255), int(g*255), int(b*255)))
    
    # Randomly select 50% of pairs to swap (squares become studied, circles become lures)
    num_to_swap = num_stimuli // 2
    pairs_to_swap = set(random.sample(range(1, num_stimuli + 1), num_to_swap))
    
    # Create studied items and lures
    for i in range(num_stimuli):
        pair_num = i + 1
        color = colors[i]
        
        # Determine if this pair should be swapped
        is_swapped = pair_num in pairs_to_swap
        
        if is_swapped:
            # Swapped: square is studied item, circle is lure
            # Create studied item (square)
            img = Image.new('RGB', (200, 200), color='lightgray')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"IMAGE_{pair_num}.png"))
            
            # Create lure (circle)
            img = Image.new('RGB', (200, 200), color='lightgray')
            draw = ImageDraw.Draw(img)
            draw.ellipse([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"LURE_{pair_num}.png"))
        else:
            # Normal: circle is studied item, square is lure
            # Create studied item (circle)
            img = Image.new('RGB', (200, 200), color='lightgray')
            draw = ImageDraw.Draw(img)
            draw.ellipse([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"IMAGE_{pair_num}.png"))
            
            # Create lure (square)
            img = Image.new('RGB', (200, 200), color='lightgray')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"LURE_{pair_num}.png"))
    
    print(f"✓ Generated {num_stimuli} placeholder stimuli in {output_dir}/")
    print(f"  - {num_to_swap} pairs swapped (squares=studied, circles=lures)")
    print(f"  - {num_stimuli - num_to_swap} pairs normal (circles=studied, squares=lures)")

# =========================
#  LOAD REAL STIMULI
# =========================
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULI_DIR = os.path.join(SCRIPT_DIR, "STIMULI")
PLACEHOLDER_DIR = os.path.join(SCRIPT_DIR, "PLACEHOLDERS")

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

CATEGORY_NAMES = list(CATEGORY_MAPPING.keys())

# Map category names to actual folder names (handle case/underscore differences)
CATEGORY_FOLDER_MAP = {
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

def get_stimulus_path(stimulus_num, is_lure=False, use_real_stimuli=True):
    """Get path to stimulus image
    
    Args:
        stimulus_num: Stimulus number (1-100)
        is_lure: True for lure, False for image
        use_real_stimuli: True to use real stimuli, False for placeholders
    
    Returns:
        Full path to image file
    """
    if use_real_stimuli:
        # Build expected filename
        if is_lure:
            filename = f"Lure_{stimulus_num:03d}.jpg"
        else:
            filename = f"Image_{stimulus_num:03d}.jpg"
        
        # Find which category this stimulus belongs to
        for category, (start, end) in CATEGORY_MAPPING.items():
            if start <= stimulus_num <= end:
                # Use mapped folder name if available, otherwise use category name as-is
                folder_name = CATEGORY_FOLDER_MAP.get(category, category)
                category_dir = os.path.join(STIMULI_DIR, folder_name)
                if os.path.exists(category_dir):
                    # List all object folders and search through them (like localizer does)
                    object_folders = [f for f in os.listdir(category_dir) 
                                     if os.path.isdir(os.path.join(category_dir, f))]
                    
                    # Search through all object folders to find the file with matching stimulus number
                    for obj_folder in sorted(object_folders):
                        obj_path = os.path.join(category_dir, obj_folder)
                        file_path = os.path.join(obj_path, filename)
                        if os.path.exists(file_path):
                            return file_path
        
        # Fallback: search all categories (like localizer does)
        for category in CATEGORY_NAMES:
            # Use mapped folder name if available, otherwise use category name as-is
            folder_name = CATEGORY_FOLDER_MAP.get(category, category)
            category_dir = os.path.join(STIMULI_DIR, folder_name)
            if os.path.exists(category_dir):
                for obj_folder in os.listdir(category_dir):
                    obj_path = os.path.join(category_dir, obj_folder)
                    if os.path.isdir(obj_path):
                        file_path = os.path.join(obj_path, filename)
                        if os.path.exists(file_path):
                            return file_path
        
        # If not found, fall back to placeholder
        print(f"Warning: Real stimulus {stimulus_num} not found, using placeholder")
        use_real_stimuli = False
    
    # Use placeholder
    if is_lure:
        return os.path.join(PLACEHOLDER_DIR, f"LURE_{stimulus_num}.png")
    else:
        return os.path.join(PLACEHOLDER_DIR, f"IMAGE_{stimulus_num}.png")

def get_stimuli_by_category():
    """Get all stimuli organized by category
    
    Returns:
        dict: {category_name: [list of stimulus numbers]}
    """
    stimuli_by_category = {}
    for category, (start, end) in CATEGORY_MAPPING.items():
        stimuli_by_category[category] = list(range(start, end + 1))
    return stimuli_by_category

def select_study_stimuli_one_per_category():
    """Select 10 stimuli for study phase: one from each category
    
    Returns:
        list: 10 stimulus numbers (one from each category)
    """
    stimuli_by_category = get_stimuli_by_category()
    selected = []
    for category, stimulus_nums in stimuli_by_category.items():
        # Randomly select one from this category
        selected.append(random.choice(stimulus_nums))
    return selected

def assign_stimuli_to_blocks():
    """Assign 100 stimuli to 10 blocks ensuring:
    - Each block has exactly 1 item from each of the 10 categories (10 stimuli per block)
    - No stimulus appears more than once across all blocks
    
    Returns:
        list: List of 10 lists, each containing 10 stimulus numbers
    """
    # Get all stimuli organized by category
    stimuli_by_category = get_stimuli_by_category()
    
    # Shuffle items within each category
    for category in stimuli_by_category:
        random.shuffle(stimuli_by_category[category])
    
    # Assign to blocks: each block gets 1 item from each category
    # This ensures no repeats (since we use each category's items exactly once)
    blocks = []
    category_names = list(CATEGORY_MAPPING.keys())
    
    for block_num in range(10):
        block_stimuli = []
        for category in category_names:
            # Get 1 item from this category for this block
            # Block 0 uses item 0, block 1 uses item 1, etc.
            item_index = block_num
            stimulus_num = stimuli_by_category[category][item_index]
            block_stimuli.append(stimulus_num)
        
        # Shuffle the order within the block for randomization
        random.shuffle(block_stimuli)
        blocks.append(block_stimuli)
    
    return blocks

# Generate practice shapes first
generate_practice_shapes(PLACEHOLDER_DIR)

# Generate placeholders if they don't exist (for practice block)
# Skip generation if placeholders already exist
# Check if directory exists and has the right number of files
placeholder_files = []
if os.path.exists(PLACEHOLDER_DIR):
    placeholder_files = [f for f in os.listdir(PLACEHOLDER_DIR) if f.endswith('.png')]

if not os.path.exists(PLACEHOLDER_DIR) or len(placeholder_files) < 200:
    print("Generating placeholder stimuli...")
    # Remove old files if they exist
    if os.path.exists(PLACEHOLDER_DIR):
        for f in os.listdir(PLACEHOLDER_DIR):
            if f.endswith('.png'):
                try:
                    os.remove(os.path.join(PLACEHOLDER_DIR, f))
                except:
                    pass
    generate_placeholder_stimuli(100, PLACEHOLDER_DIR)
else:
    print(f"Placeholder stimuli already exist ({len(placeholder_files)} files). Skipping generation.")
    # Verify that we have both circles and squares by checking a sample
    # If all checked images are the same shape, regenerate
    sample_indices = [1, 25, 50, 75]
    all_same_shape = True
    first_shape = None
    
    for i in sample_indices:
        img_path = os.path.join(PLACEHOLDER_DIR, f"IMAGE_{i}.png")
        if os.path.exists(img_path):
            try:
                from PIL import Image as PILImage
                img = PILImage.open(img_path)
                pixels = img.load()
                width, height = img.size
                
                # Quick check: compare corner to center
                corner = pixels[10, 10]
                center = pixels[width//2, height//2]
                
                def rgb_avg(rgb):
                    if isinstance(rgb, int):
                        return rgb
                    return sum(rgb[:3]) / len(rgb[:3]) if len(rgb) >= 3 else rgb
                
                corner_avg = rgb_avg(corner)
                center_avg = rgb_avg(center)
                diff = abs(corner_avg - center_avg)
                is_square = diff < 100  # Square if corners similar to center
                
                if first_shape is None:
                    first_shape = is_square
                elif is_square != first_shape:
                    all_same_shape = False
                    break
            except:
                pass
    
    # If all samples are the same shape, regenerate (only if placeholders don't already exist)
    if all_same_shape and first_shape is not None:
        # Check if we have the expected number of files before regenerating
        existing_files = [f for f in os.listdir(PLACEHOLDER_DIR) if f.endswith('.png')] if os.path.exists(PLACEHOLDER_DIR) else []
        if len(existing_files) >= 200:
            print("Placeholder stimuli already exist. Skipping shape verification regeneration.")
        else:
            print("Detected all images are the same shape. Regenerating with swap logic...")
            if os.path.exists(PLACEHOLDER_DIR):
                for f in os.listdir(PLACEHOLDER_DIR):
                    if f.endswith('.png'):
                        try:
                            os.remove(os.path.join(PLACEHOLDER_DIR, f))
                        except:
                            pass
            generate_placeholder_stimuli(100, PLACEHOLDER_DIR)

# =========================
#  BASIC VISUAL ELEMENTS
# =========================
print("="*60)
print("STARTING BASIC VISUAL ELEMENTS CREATION")
print("="*60)
instr = None
fixation = None
feedback_txt = None
mouse = None

try:
    print(f"Checking win before creating elements: win = {win}, type = {type(win)}")
    if win is None:
        raise RuntimeError("Cannot create visual elements - win is None")
    
    print(f"Window status: {win}, type: {type(win)}")
    print("Creating instr...")
    instr = visual.TextStim(win, text="", color='black', height=0.04*0.75*1.35, wrapWidth=1.5*0.75, pos=(0, 0))
    print("instr created")
    print("Creating fixation...")
    fixation = visual.TextStim(win, text="+", color='black', height=0.08*0.75*1.35, pos=(0, 0))
    print("fixation created")
    print("Creating feedback_txt...")
    feedback_txt = visual.TextStim(win, text="", color='black', height=0.04*0.75*1.35, pos=(0, 0))
    print("feedback_txt created")
    print("Creating mouse...")
    mouse = event.Mouse(win=win)
    print("mouse created")
    print("Basic visual elements created successfully")
    print("="*60)
    print("BASIC VISUAL ELEMENTS CREATION SUCCESSFUL")
    print("="*60)
except Exception as e:
    print("="*60)
    print("EXCEPTION CAUGHT IN BASIC VISUAL ELEMENTS CREATION")
    print("="*60)
    print(f"ERROR creating basic visual elements: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("="*60)
    print("Press Enter to exit...")
    try:
        input()
    except:
        pass
    if win is not None:
        try:
            win.close()
        except Exception as e:
            print(f"ERROR calling win.close(): {repr(e)}", file=sys.stderr)
            traceback.print_exc()
    try:
        core.quit()
    except:
        pass
    exit(1)
except SystemExit:
    print("SystemExit caught in visual elements creation")
    raise
except:
    print("="*60)
    print("UNKNOWN EXCEPTION CAUGHT IN BASIC VISUAL ELEMENTS CREATION")
    print("="*60)
    import traceback
    traceback.print_exc()
    print("="*60)
    if win is not None:
        try:
            win.close()
        except Exception as e:
            print(f"ERROR calling win.close(): {repr(e)}", file=sys.stderr)
            traceback.print_exc()
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

# =========================
#  HELPER FUNCTIONS
# =========================
def safe_wait(duration):
    """Wrapper for core.wait() that handles macOS event dispatch errors (e.g. NSTrackingArea/NSConcreteNotification has no attribute 'type')"""
    try:
        core.wait(duration)
    except AttributeError as e:
        err_str = str(e)
        # Known macOS/pyglet Cocoa event dispatch issues - skip and continue
        if ("type" in err_str and ("ObjCInstance" in err_str or "NSConcreteNotification" in err_str or "NSTrackingArea" in err_str)):
            pass
        else:
            raise
    except Exception:
        # Ignore other non-critical wait errors
        pass

def wait_for_button(redraw_func=None, button_text="CONTINUE", button_y=None):
    """Wait for button click/touch instead of space key - button should be included in redraw_func. button_y: optional y position for button (default -0.4*0.6)."""
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    if button_y is None:
        button_y = -0.4*0.6
    # Create continue button
    continue_button = visual.Rect(
        win,
        width=0.3*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, button_y)
    )
    continue_text = visual.TextStim(
        win,
        text=button_text,
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
        pos=(0, button_y)
    )
    
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    # Draw initial screen once (button should be included in redraw_func)
    def draw_screen():
        if redraw_func:
            try:
                redraw_func()
            except:
                pass
        continue_button.draw()
        continue_text.draw()
        exit_btn.draw()
        exit_text.draw()
        win.flip()
    
    draw_screen()
    
    clicked = False
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    draw_screen()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    try:
                        button_pos = continue_button.pos
                        if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                            button_x, button_y = float(button_pos[0]), float(button_pos[1])
                        else:
                            button_x, button_y = 0.0, button_y  # Use same y as button creation
                    except (TypeError, ValueError):
                        button_x, button_y = 0.0, button_y
                    
                    try:
                        button_width = float(continue_button.width)
                        button_height = float(continue_button.height)
                    except (TypeError, ValueError):
                        button_width, button_height = 0.3*0.75, 0.1*0.75
                    
                    # For touch screens, use larger hit area (at least button size, or larger)
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                              EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    
                    if on_exit:
                        core.quit()
                    elif on_button:
                        # Visual feedback (no color change in touch screen mode)
                        draw_screen()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_screen()
                core.wait(0.01)  # Fast polling
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
                
                try:
                    button_pos = continue_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x, button_y = float(button_pos[0]), float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, button_y  # Use same y as button creation
                except (TypeError, ValueError):
                    button_x, button_y = 0.0, button_y
                
                try:
                    button_width = float(continue_button.width)
                    button_height = float(continue_button.height)
                except (TypeError, ValueError):
                    button_width, button_height = 0.3*0.75, 0.1*0.75  # Match actual button size
                
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_exit:
                        core.quit()
                    elif on_button:
                        if not USE_TOUCH_SCREEN:
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
            
            # Also check for space key as backup
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
            
            safe_wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()

def wait_for_space(redraw_func=None):
    """Wait for button click (replaces space key press)"""
    wait_for_button(redraw_func=redraw_func)

def show_instructions(text, header_color='darkblue', body_color='black', header_size=0.07*1.35, body_size=0.045*1.35):
    """Show instructions with formatted header and body text, with continue button"""
    # Split text into lines
    lines = text.split('\n')
    
    # Find header (usually first line or line with all caps ending with :)
    header_text = ""
    body_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check if this looks like a header (all caps, ends with :, or short and prominent)
        if stripped and (stripped.isupper() or stripped.endswith(':') or 
                        (i == 0 and len(stripped) < 50 and not stripped.startswith("Press"))):
            if not header_text:  # Take first match
                header_text = stripped
                continue
        body_lines.append(line)
    
    # If no clear header found, use first line as header if it's short
    if not header_text and lines:
        first_line = lines[0].strip()
        if len(first_line) < 60 and not first_line.startswith("Press"):
            header_text = first_line
            body_lines = lines[1:]
        else:
            header_text = ""
            body_lines = lines
    
    body_text = '\n'.join(body_lines)
    
    # Create header text stim (larger, colored) - position lower to avoid top overlap
    if header_text:
        header_stim = visual.TextStim(
            win, 
            text=header_text, 
            color=header_color, 
            height=header_size, 
            pos=(0, 0.25),
            wrapWidth=1.5
        )
    else:
        header_stim = None
    
    # Create body text stim - adjust position to leave room for button
    # Calculate approximate text height to avoid overlap
    body_lines = len(body_text.split('\n'))
    estimated_text_height = body_lines * body_size * 1.2  # Approximate line spacing
    # Position body text lower to avoid header overlap and leave room for button
    body_y_pos = 0.0 if header_stim else 0.15
    if estimated_text_height > 0.5:  # If text is very long, move it down more
        body_y_pos = -0.05 if header_stim else 0.1
    
    body_stim = visual.TextStim(
        win, 
        text=body_text, 
        color=body_color, 
        height=body_size, 
        pos=(0, body_y_pos),
        wrapWidth=1.5
    )
    
    # Create continue button - positioned higher for better balance with text
    continue_button = visual.Rect(
        win,
        width=0.3,
        height=0.1*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.25)
    )
    continue_text = visual.TextStim(
        win,
        text="CONTINUE",
        color='black',
        height=0.04*1.35,  # Reduced to ensure text fits within button
        pos=(0, -0.25)
    )
    
    # Draw function that includes button
    def redraw():
        if header_stim:
            header_stim.draw()
        body_stim.draw()
        continue_button.draw()
        continue_text.draw()
        win.flip()
    
    # Draw initial screen
    redraw()
    
    # Wait for button click
    mouse_btn = event.Mouse(win=win)
    mouse_btn.setVisible(True)
    clicked = False
    last_hover_state = None
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse_btn.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse_btn.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    redraw()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    try:
                        button_pos = continue_button.pos
                        if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                            button_x, button_y = float(button_pos[0]), float(button_pos[1])
                        else:
                            button_x, button_y = 0.0, -0.25  # Fallback to match button position
                    except (TypeError, ValueError):
                        button_x, button_y = 0.0, -0.25
                    
                    try:
                        button_width = float(continue_button.width)
                        button_height = float(continue_button.height)
                    except (TypeError, ValueError):
                        button_width, button_height = 0.3, 0.1
                    
                    # For touch screens, use larger hit area (at least button size, or larger)
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    
                    if on_button:
                        # Visual feedback (no color change in touch screen mode)
                        redraw()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse_btn.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                redraw()
            except (AttributeError, Exception):
                pass
            
            # Check for space key as backup
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        
        while not clicked:
            try:
                mouse_buttons = mouse_btn.getPressed()
                mouse_pos = mouse_btn.getPos()
                
                # Convert to floats
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                try:
                    button_pos = continue_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x, button_y = float(button_pos[0]), float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, -0.5  # Updated to match new button position
                except (TypeError, ValueError):
                    button_x, button_y = 0.0, -0.35  # Match actual button position
                
                try:
                    button_width = float(continue_button.width)
                    button_height = float(continue_button.height)
                except (TypeError, ValueError):
                    button_width, button_height = 0.3, 0.1  # Match actual button size
                
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_button:
                        if not USE_TOUCH_SCREEN:
                            continue_button.fillColor = 'lightgreen'
                        redraw()
                        core.wait(0.2)
                        clicked = True
                        break
                
                if on_button != last_hover_state:
                    if on_button:
                        continue_button.fillColor = 'lightcyan'
                    else:
                        continue_button.fillColor = 'lightblue'
                    redraw()
                    last_hover_state = on_button
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
            # Check for space key as backup
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    
    mouse_btn.setVisible(False)
    event.clearEvents()

def show_fixation(duration=1.0):
    fixation.draw()
    win.flip()
    core.wait(duration)

def get_participant_id():
    """Get participant ID from PsychoPy screen input with on-screen keyboard for touch screens"""
    input_id = ""
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    # Create text display - adjust positions for touch screen to avoid overlap
    # Layout: prompt at top, input below, buttons below input, keyboard at bottom
    if USE_TOUCH_SCREEN:
        id_prompt = visual.TextStim(win, text="", color='black', height=0.045*0.75*1.35, wrapWidth=1.4*0.75, pos=(0, 0.42*0.6))
        input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75*1.35, pos=(0, 0.25*0.6))
    else:
        id_prompt = visual.TextStim(win, text="", color='black', height=0.045*0.75*1.35, wrapWidth=1.4*0.75, pos=(0, 0.3*0.6))
        input_display = visual.TextStim(win, text="", color='black', height=0.06*0.75*1.35, pos=(0, 0.1*0.6))
    
    # Create on-screen keyboard if touch screen (no number row)
    keyboard_buttons = []
    keyboard_layout = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', '_', '-']
    ]
    
    if USE_TOUCH_SCREEN:
        # Create keyboard buttons
        button_width = 0.08*0.75
        button_height = 0.08*0.75
        start_y = -0.15*0.6  # Move keyboard lower to avoid overlap with buttons
        row_spacing = 0.12*0.75  # Increased spacing between rows to prevent overlap
        button_spacing = 0.02  # Increased spacing between buttons to prevent overlap
        
        for row_idx, row in enumerate(keyboard_layout):
            row_width = len(row) * button_width + (len(row) - 1) * button_spacing
            start_x = -row_width / 2 + button_width / 2
            
            for col_idx, char in enumerate(row):
                x_pos = start_x + col_idx * (button_width + button_spacing)
                y_pos = start_y - row_idx * row_spacing
                
                button = visual.Rect(
                    win,
                    width=button_width,
                    height=button_height,
                    fillColor='lightgray',
                    lineColor='black',
                    pos=(x_pos, y_pos)
                )
                button_text = visual.TextStim(
                    win,
                    text=char.upper(),
                    color='black',
                    height=0.04*0.75*1.35,
                    pos=(x_pos, y_pos)
                )
                keyboard_buttons.append((button, button_text, char))
        
        # Special buttons: Backspace, Continue (positioned between input and keyboard)
        special_y = 0.05*0.6  # Position between input (0.25) and keyboard start (-0.15)
        backspace_button = visual.Rect(win, width=0.3*0.75, height=0.1*0.75*1.35, fillColor='lightcoral', lineColor='black', lineWidth=2*0.75, pos=(-0.25*0.6, special_y))
        backspace_text = visual.TextStim(win, text="BACKSPACE", color='black', height=0.025*0.75*1.35, pos=(-0.25*0.6, special_y))
        
        continue_button = visual.Rect(win, width=0.3*0.75, height=0.1*0.75*1.35, fillColor='lightgreen', lineColor='black', lineWidth=2*0.75, pos=(0.25*0.6, special_y))
        continue_text = visual.TextStim(win, text="CONTINUE", color='black', height=0.025*0.75*1.35, pos=(0.25*0.6, special_y))
        exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
        exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    # Key list for keyboard input (non-touch)
    key_list = ['return', 'backspace', 'space'] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(48, 58)]
    
    def redraw():
        if USE_TOUCH_SCREEN:
            id_prompt.text = "Enter your first name and last initial with no spaces/capitals:"
        else:
            id_prompt.text = "Enter your first name and last initial with no spaces/capitals:\n\nHit Enter when done."
        input_display.text = f"{input_id}_"
        
        id_prompt.draw()
        input_display.draw()
        
        if USE_TOUCH_SCREEN:
            for button, button_text, _ in keyboard_buttons:
                button.draw()
                button_text.draw()
            backspace_button.draw()
            backspace_text.draw()
            continue_button.draw()
            continue_text.draw()
            exit_btn.draw()
            exit_text.draw()
        
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
        # Check for escape key FIRST, before any processing
        try:
            keys = event.getKeys(keyList=['escape'], timeStamped=False)
            if keys and 'escape' in keys:
                core.quit()
        except (AttributeError, RuntimeError):
            pass
        
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
                # Position has changed - check if touch is within any button using position calculation
                # Check Exit button FIRST (top-right, always clickable)
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                if on_exit:
                    core.quit()  # Exit always responsive (no minRT)
                # Check keyboard buttons - use smaller hit margin to prevent overlap
                hit_margin_keyboard = 0.01  # Small margin to prevent overlap between keyboard buttons
                if not on_exit:
                    for button, button_text, char in keyboard_buttons:
                        try:
                            button_x, button_y = button.pos
                            button_width, button_height = button.width, button.height
                        except:
                            continue
                        
                        # Use exact button bounds with minimal margin to prevent overlap
                        on_button = (button_x - button_width/2 - hit_margin_keyboard <= mouseloc_x <= button_x + button_width/2 + hit_margin_keyboard and
                                     button_y - button_height/2 - hit_margin_keyboard <= mouseloc_y <= button_y + button_height/2 + hit_margin_keyboard)
                        
                        if on_button:
                            if t > minRT:  # Minimum time has passed
                                input_id += char
                                # No color change in touch screen mode
                                if not USE_TOUCH_SCREEN:
                                    button.fillColor = 'lightgreen'
                                redraw()
                                core.wait(0.05)
                                if not USE_TOUCH_SCREEN:
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
                
                if not clicked:
                    # Check backspace button using position calculation - larger margin for special buttons
                    hit_margin_special = 0.05
                    try:
                        button_x, button_y = backspace_button.pos
                        button_width, button_height = backspace_button.width, backspace_button.height
                    except:
                        button_x, button_y = 0.0, 0.0
                        button_width, button_height = 0.3*0.75, 0.1*0.75
                    
                    on_backspace = (button_x - button_width/2 - hit_margin_special <= mouseloc_x <= button_x + button_width/2 + hit_margin_special and
                                    button_y - button_height/2 - hit_margin_special <= mouseloc_y <= button_y + button_height/2 + hit_margin_special)
                    
                    if on_backspace:
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
                
                if not clicked:
                    # Check continue button using position calculation - larger margin for special buttons
                    try:
                        button_x, button_y = continue_button.pos
                        button_width, button_height = continue_button.width, continue_button.height
                    except:
                        button_x, button_y = 0.0, 0.0
                        button_width, button_height = 0.3, 0.1
                    
                    on_continue = (button_x - button_width/2 - hit_margin_special <= mouseloc_x <= button_x + button_width/2 + hit_margin_special and
                                    button_y - button_height/2 - hit_margin_special <= mouseloc_y <= button_y + button_height/2 + hit_margin_special)
                    
                    if on_continue:
                        if t > minRT:
                            if input_id.strip():
                                # No color change in touch screen mode
                                if not USE_TOUCH_SCREEN:
                                    continue_button.fillColor = 'green'
                                redraw()
                                core.wait(0.05)
                                mouse.setVisible(False)
                                event.clearEvents()
                                break  # Break from loop, will return below
                            else:
                                # No color change in touch screen mode
                                if not USE_TOUCH_SCREEN:
                                    continue_button.fillColor = 'red'
                                redraw()
                                core.wait(0.1)
                                if not USE_TOUCH_SCREEN:
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
            # Check keys BEFORE clearing events
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'space' in keys:
                        clicked = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Error checking keys in get_participant_id: {e}", file=sys.stderr)
            # Check escape again before clearing (clearEvents can wipe keys pressed during redraw)
            try:
                keys = event.getKeys(keyList=['escape'], timeStamped=False)
                if keys and 'escape' in keys:
                    core.quit()
            except (AttributeError, RuntimeError):
                pass
            # Clear events AFTER checking keys
            event.clearEvents()
            safe_wait(0.001)  # Very fast polling
        else:
            # Click/mouse mode: keyboard input only
            keys = event.getKeys(keyList=key_list + ['escape'], timeStamped=False)
            if keys:
                if 'escape' in keys:
                    core.quit()
                key = keys[0]
                if key == 'return':
                    if input_id.strip():
                        break
                elif key == 'backspace':
                    input_id = input_id[:-1] if input_id else ""
                elif key == 'space':
                    input_id += ' '
                elif len(key) == 1 and (key.isalnum() or key in ['_', '-']):
                    input_id += key
                
                redraw()
        
        safe_wait(0.01)
    
    mouse.setVisible(False)
    return input_id.strip() or "P001"

def load_image_stimulus(image_path, maintain_aspect_ratio=False):
    """Load an image stimulus
    
    Args:
        image_path: Path to image file
        maintain_aspect_ratio: If True, maintain aspect ratio (for partner images like Amy.png, Ben.png)
    """
    if os.path.exists(image_path):
        if maintain_aspect_ratio:
            # Load image to get dimensions
            from PIL import Image as PILImage
            img = PILImage.open(image_path)
            img_width, img_height = img.size
            
            # Calculate size maintaining aspect ratio
            # Use height as reference (0.3) and scale width proportionally
            aspect_ratio = img_width / img_height
            height = 0.3 * 1.35  # 35% bigger
            width = height * aspect_ratio
            
            return visual.ImageStim(win, image=image_path, size=(width, height))
        else:
            return visual.ImageStim(win, image=image_path, size=(0.3*1.35, 0.3*1.35))  # 35% bigger
    else:
        # Fallback: colored rectangle
        return visual.Rect(win, size=(0.3, 0.3), fillColor='gray', lineColor='black')

# =========================
#  SLIDER FOR OLD-NEW RATING
# =========================
SLIDER_Y_POS_PRACTICE = -0.35*0.6
SLIDER_Y_POS_ACTUAL = -0.42*0.6   # Slightly lower for actual task

def get_slider_response(prompt_text="Rate your memory:", image_stim=None, trial_num=None, max_trials=10, timeout=7.0):
    """Get slider response from participant using slider with submit button
    Works with both touch screen and mouse input - click/tap anywhere on the slider line to set value"""
    # Create slider visual elements; use lower position for actual task (trial_num set), higher for practice
    slider_y_pos = SLIDER_Y_POS_ACTUAL if trial_num is not None else SLIDER_Y_POS_PRACTICE
    slider_line = visual.Line(
        win,
        start=(-0.4*0.6, slider_y_pos),
        end=(0.4*0.6, slider_y_pos),
        lineColor='black',
        lineWidth=3
    )
    slider_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        pos=(0, slider_y_pos)  # Start at center
    )
    # Move labels farther from line and lower to avoid overlap with slider circle
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04*0.75*1.35, pos=(-0.5*0.6, slider_y_pos - 0.08))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04*0.75*1.35, pos=(0.5*0.6, slider_y_pos - 0.08))
    
    # Image number display
    if trial_num is not None:
        trial_text = visual.TextStim(win, text=f"Image {trial_num} of {max_trials}", color='gray', height=0.04*0.75*1.35, pos=(0, 0.65*0.6))  # Moved higher
    
    # Use smaller text height for longer instructions (practice trials)
    # Images are now 35% bigger (0.3*1.35 = 0.405 height), so move text higher to avoid overlap
    text_height = 0.04*0.75*1.35  # Standardized text size
    prompt = visual.TextStim(win, text=prompt_text, color='black', height=text_height, pos=(0, 0.5*0.6), wrapWidth=1.4)  # Move higher to avoid overlap
    
    # Submit button (positioned below slider; actual trials use smaller offset so button stays above dock)
    submit_y = slider_y_pos - (0.08 if trial_num is not None else 0.12)
    submit_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.06*0.75*1.35,  # Shorter
        fillColor='lightgreen',
        lineColor='black',
        pos=(0, submit_y)
    )
    submit_text = visual.TextStim(win, text="SUBMIT", color='black', height=0.035*0.75*1.35, pos=(0, submit_y))
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    mouse.setVisible(True)
    
    slider_value = 0.5  # Start at center (0.5)
    start_time = time.time()
    slider_commit_time = None
    slider_stop_time = None  # Time when slider value is set (clicked)
    slider_decision_onset_time = None  # First time participant clicks/taps the slider bar (decision onset)
    slider_click_times = []  # List of all times participant clicks/taps the slider bar (for touch screens)
    prev_mouse_buttons = [False, False, False]
    has_moved = False  # Track if slider has been moved from center
    timed_out = False
    mouse_pos = (0, 0)  # Initialize mouse position
    mouse_buttons = [False, False, False]  # Initialize mouse buttons
    
    # For touch screens, use position-change detection
    if USE_TOUCH_SCREEN:
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
    
    while True:
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            # Timeout - pick random value (not center) and show alert
            # Pick random value between 0-0.4 (OLD) or 0.6-1.0 (NEW)
            if random.random() < 0.5:
                slider_value = random.uniform(0.0, 0.4)  # OLD side
            else:
                slider_value = random.uniform(0.6, 1.0)  # NEW side
            
            slider_commit_time = time.time()
            
            # Show timeout alert
            timeout_alert = visual.TextStim(
                win,
                    text="Time's up! A random answer was selected. This will be logged as an invalid trial.",
                color='red',
                height=0.06*0.75*1.35,
                pos=(0, 0)
            )
            if image_stim:
                image_stim.draw()
            timeout_alert.draw()
            win.flip()
            core.wait(1.5)
            
            timed_out = True
            break
        
        # Get mouse position and button state (with error handling for macOS)
        try:
            new_mouse_pos = mouse.getPos()
            new_mouse_buttons = mouse.getPressed()
            mouse_pos = new_mouse_pos
            mouse_buttons = new_mouse_buttons
        except (AttributeError, Exception) as e:
            # Handle macOS event handling issues - try to recover
            try:
                event.clearEvents()
            except:
                pass
            # Keep using previous mouse state instead of defaulting
            core.wait(0.02)  # Slightly longer wait to let system recover
        
        # Check if clicking/tapping on slider line (mouse mode allows dragging, touch screen uses tap-to-set)
        on_slider_line = abs(mouse_pos[1] - slider_y_pos) < 0.05*0.75  # Within 0.05 of slider line y-position
        on_slider_x_range = -0.4*0.6 <= mouse_pos[0] <= 0.4*0.6  # Within slider x range
        
        if USE_TOUCH_SCREEN:
            # Position-change detection for touch screens (NO minimum RT delay for task responses)
            try:
                mouseloc_x, mouseloc_y = float(mouse_pos[0]), float(mouse_pos[1])
            except:
                mouseloc_x, mouseloc_y = 0.0, 0.0
            
            # Check if position has changed
            if mouseloc_x != mouserec_x or mouseloc_y != mouserec_y:
                # Check Exit button FIRST (top-right, always clickable)
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                if on_exit:
                    core.quit()
                # Position changed - check if touch is on slider line
                elif on_slider_line and on_slider_x_range:
                    # Touched on slider line - set value based on x position
                    x_pos = max(-0.4*0.6, min(0.4*0.6, mouseloc_x))
                    slider_value = (x_pos + 0.4*0.6) / (0.8*0.6)  # Map -0.4*0.6 to 0.4*0.6 -> 0 to 1
                    slider_handle.pos = (x_pos, slider_y_pos)
                    
                    # Record decision onset time (first click on slider bar)
                    click_time = time.time()
                    if slider_decision_onset_time is None:
                        slider_decision_onset_time = click_time  # First click = decision onset
                    slider_click_times.append(click_time)  # Log all clicks
                    
                    # Check if moved from center (0.5)
                    if abs(slider_value - 0.5) > 0.01:  # Moved at least 1% from center
                        has_moved = True
                        slider_stop_time = click_time  # Record when value was set immediately
                
                # Check if submit button is touched (keyboard method - respond immediately on position change)
                submit_x, submit_y = submit_button.pos
                submit_width, submit_height = submit_button.width, submit_button.height
                # For touch screens, use larger hit area (at least button size, or larger)
                if USE_TOUCH_SCREEN:
                    submit_hit_margin_x = max(submit_width * 0.5, 0.08)
                    submit_hit_margin_y = max(submit_height * 0.5, 0.04)
                else:
                    submit_hit_margin_x = 0.0
                    submit_hit_margin_y = 0.0
                
                submit_clicked = (submit_x - submit_width/2 - submit_hit_margin_x <= mouseloc_x <= submit_x + submit_width/2 + submit_hit_margin_x and
                               submit_y - submit_height/2 - submit_hit_margin_y <= mouseloc_y <= submit_y + submit_height/2 + submit_hit_margin_y)
                
                if submit_clicked:
                    if has_moved:
                        slider_commit_time = time.time()  # Record immediately, no delay
                        break
                    else:
                        # Show message: "please select an answer first"
                        error_message = visual.TextStim(
                            win,
                            text="Please select an answer first.",
                            color='red',
                            height=0.04*0.75*1.35,
                            pos=(0, slider_y_pos - 0.2)
                        )
                        # Draw everything with error message
                        if image_stim:
                            image_stim.draw()
                        if trial_num is not None:
                            trial_text.draw()
                        prompt.draw()
                        slider_line.draw()
                        old_label.draw()
                        new_label.draw()
                        slider_handle.draw()
                        submit_button.draw()
                        submit_text.draw()
                        error_message.draw()
                        win.flip()
                        core.wait(1.0)  # Show error message for 1 second
                        # Continue loop (don't break)
                
                # Update recorded position
                mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
            
        else:
            # Mouse/click mode: allow dragging the slider
            # Check if mouse button is pressed and mouse is over slider line (enables dragging)
            if mouse_buttons[0] and on_slider_line and on_slider_x_range:
                # Mouse button is pressed and over slider line - update slider value (allows dragging)
                x_pos = max(-0.4*0.6, min(0.4*0.6, mouse_pos[0]))
                slider_value = (x_pos + 0.4*0.6) / (0.8*0.6)  # Map -0.4*0.6 to 0.4*0.6 -> 0 to 1
                slider_handle.pos = (x_pos, slider_y_pos)
                
                # Record decision onset time (first time mouse button is pressed on slider)
                click_time = time.time()
                if slider_decision_onset_time is None:
                    slider_decision_onset_time = click_time  # First press = decision onset
                    slider_click_times.append(click_time)  # Log first click
                
                # Check if moved from center (0.5)
                if abs(slider_value - 0.5) > 0.01:  # Moved at least 1% from center
                    has_moved = True
                    slider_stop_time = click_time  # Update stop time while dragging
            
            # Also handle click on slider line (for single clicks, not just dragging)
            if prev_mouse_buttons[0] and not mouse_buttons[0]:
                # Button was just released - check if it was on slider line
                if on_slider_line and on_slider_x_range:
                    # Clicked on slider line - set value based on x position
                    x_pos = max(-0.4*0.6, min(0.4*0.6, mouse_pos[0]))
                    slider_value = (x_pos + 0.4*0.6) / (0.8*0.6)  # Map -0.4*0.6 to 0.4*0.6 -> 0 to 1
                    slider_handle.pos = (x_pos, slider_y_pos)
                    
                    # For mouse/computer version, decision onset = slider stop time (same as when they click)
                    click_time = time.time()
                    if slider_decision_onset_time is None:
                        slider_decision_onset_time = click_time  # First click = decision onset (same as stop time for mouse)
                    slider_click_times.append(click_time)  # Log all clicks
                    
                    # Check if moved from center (0.5)
                    if abs(slider_value - 0.5) > 0.01:  # Moved at least 1% from center
                        has_moved = True
                        slider_stop_time = click_time  # Record when value was set
            
            # Check if submit button is clicked/touched (on mouse/touch release)
            submit_x, submit_y = submit_button.pos
            submit_width, submit_height = submit_button.width, submit_button.height
            submit_clicked = (submit_x - submit_width/2 <= mouse_pos[0] <= submit_x + submit_width/2 and
                             submit_y - submit_height/2 <= mouse_pos[1] <= submit_y + submit_height/2)
            
            # Check if Exit button is clicked (mouse mode)
            on_exit_mouse = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_pos[0] <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                            EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_pos[1] <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
            if prev_mouse_buttons[0] and not mouse_buttons[0] and on_exit_mouse:
                core.quit()
            # Check if submit button is clicked
            elif prev_mouse_buttons[0] and not mouse_buttons[0] and submit_clicked:
                if has_moved:
                    slider_commit_time = time.time()
                    break
                else:
                    # Show message: "please select an answer first"
                    error_message = visual.TextStim(
                        win,
                        text="Please select an answer first.",
                        color='red',
                        height=0.04*0.75*1.35,
                        pos=(0, slider_y_pos - 0.2)
                    )
                    # Draw everything with error message
                    if image_stim:
                        image_stim.draw()
                    if trial_num is not None:
                        trial_text.draw()
                    prompt.draw()
                    slider_line.draw()
                    old_label.draw()
                    new_label.draw()
                    slider_handle.draw()
                    submit_button.draw()
                    submit_text.draw()
                    error_message.draw()
                    win.flip()
                    core.wait(1.0)  # Show error message for 1 second
                    # Continue loop (don't break)
        
        # Update submit button color based on whether slider has moved (only for click mode)
        if not USE_TOUCH_SCREEN:
            if has_moved:
                submit_button.fillColor = 'lightgreen'
            else:
                submit_button.fillColor = 'lightgray'
        # Touch screen mode: no color changes - button keeps default color
        
        prev_mouse_buttons = mouse_buttons.copy()
        
        # Draw everything
        if image_stim:
            image_stim.draw()
        if trial_num is not None:
            trial_text.draw()
        prompt.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        slider_handle.draw()
        submit_button.draw()
        submit_text.draw()
        exit_btn.draw()
        exit_text.draw()
        win.flip()
        
        # Check for escape (with error handling)
        try:
            # Safe event.getKeys() handling - ensure keys is never empty array issue
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:  # Check keys is not empty first
                    core.quit()
            except (AttributeError, Exception):
                pass  # Ignore event errors
        except (AttributeError, Exception):
            # Ignore event errors, just continue
            pass
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    slider_rt = slider_commit_time - start_time if slider_commit_time else timeout
    
    # For mouse/computer version, if decision onset wasn't set, set it to slider_stop_time
    if slider_decision_onset_time is None and slider_stop_time is not None:
        slider_decision_onset_time = slider_stop_time
    
    # Ensure slider_click_times is a list (even if empty)
    if slider_click_times is None:
        slider_click_times = []
    
    return slider_value, slider_rt, slider_commit_time, timed_out, slider_stop_time, slider_decision_onset_time, slider_click_times

# =========================
#  AI COLLABORATOR
# =========================
class AICollaborator:
    def __init__(self, accuracy_rate=0.5, num_trials=20):
        """
        AI collaborator for recognition memory task
        accuracy_rate: Overall accuracy (0.5 = 50%, 0.75 = 75%, 0.25 = 25%)
        num_trials: Number of trials in the block (default 20)
        """
        self.accuracy_rate = accuracy_rate
        self.num_trials = num_trials
        
        # Pre-generate randomized sequence of correct/Incorrect trials
        # This ensures deterministic accuracy while randomizing the order
        num_correct = int(round(accuracy_rate * num_trials))
        num_Incorrect = num_trials - num_correct
        
        # Create list: True for correct, False for Incorrect
        self.correctness_sequence = [True] * num_correct + [False] * num_Incorrect
        random.shuffle(self.correctness_sequence)  # Randomize the order
        
        # Track current trial index
        self.trial_index = 0
    
    def generate_rt(self):
        """Generate AI RT from log-normal distribution"""
        # Log-normal: mean around 1.5-2.5 seconds
        mu = 0.5  # Mean of underlying normal
        sigma = 0.3  # Std of underlying normal
        rt = np.random.lognormal(mu, sigma)
        return min(rt, 5.0)  # Cap at 5 seconds
    
    def generate_confidence(self, is_studied, ground_truth_correct):
        """Generate AI confidence: random but definitely high when correct, definitely low when incorrect"""
        # When correct: random in higher range (0.65-0.95)
        # When incorrect: random in lower range (0.05-0.35)
        if ground_truth_correct:
            confidence = np.random.uniform(0.65, 0.95)
        else:
            confidence = np.random.uniform(0.05, 0.35)
        
        # If studied item, bias toward OLD; if lure, bias toward NEW
        if is_studied:
            # Bias toward OLD (lower values)
            if ground_truth_correct:
                confidence = confidence * 0.5  # OLD side
            else:
                confidence = 0.5 + (confidence * 0.5)  # NEW side (Incorrect)
        else:
            # Bias toward NEW (higher values)
            if ground_truth_correct:
                confidence = 0.5 + (confidence * 0.5)  # NEW side
            else:
                confidence = confidence * 0.5  # OLD side (Incorrect)
        
        return confidence
    
    def make_decision(self, is_studied, trial_type):
        """
        Make AI decision with deterministic accuracy and randomized order
        is_studied: True if this is a studied item, False if lure
        trial_type: "studied" or "lure"
        
        Uses pre-generated randomized sequence to ensure exactly the target accuracy rate
        while randomizing which trials are correct/Incorrect:
        - 75% accuracy: approximately 7-8 out of 10 trials correct (randomized order)
        - 25% accuracy: approximately 2-3 out of 10 trials correct (randomized order)
        """
        # Ground truth: studied items should be rated OLD, lures should be rated NEW
        if is_studied:
            ground_truth = 0.0  # OLD
        else:
            ground_truth = 1.0  # NEW
        
        # Get correctness from pre-generated randomized sequence
        if self.trial_index < len(self.correctness_sequence):
            should_be_correct = self.correctness_sequence[self.trial_index]
            self.trial_index += 1
        else:
            # Fallback if we exceed the sequence (shouldn't happen, but safety check)
            should_be_correct = random.random() < self.accuracy_rate
        
        ai_correct = should_be_correct
        
        # Generate confidence
        ai_confidence = self.generate_confidence(is_studied, ai_correct)
        
        # Generate RT
        ai_rt = self.generate_rt()
        
        return ai_confidence, ai_rt, ai_correct, ground_truth

# =========================
#  STUDY PHASE
# =========================
def run_study_phase(studied_images, block_num):
    """
    Show study phase: images back-to-back with jittered fixations
    NOTE: Study phase ONLY shows studied images (IMAGE_X.png), never lures
    """
    study_data = []
    image_duration = 1.0  # Show each image for 1 second
    
    # ALWAYS start study phase with a fixation cross
    fixation_duration_first = random.uniform(0.25, 0.75)
    fixation_onset_first = time.time()
    show_fixation(fixation_duration_first)
    fixation_offset_first = time.time()
    
    for i, img_path in enumerate(studied_images, 1):
        # Jittered fixation between images (0.25-0.75 seconds)
        if i > 1:  # Additional fixations between images
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
        img_stim = load_image_stimulus(img_path)
        img_stim.draw()
        win.flip()
        
        image_onset = time.time()
        core.wait(image_duration)  # Show each image for 1 second
        image_offset = time.time()
        
        study_data.append({
            "block": block_num,
            "phase": "study",
            "trial": i,
            "image_path": img_path,
            "image_onset": image_onset,
            "image_offset": image_offset,
            "image_duration": image_duration,
            "fixation_onset": fixation_onset,
            "fixation_offset": fixation_offset,
            "fixation_duration": fixation_duration
        })
    
    # Final fixation after last image
    show_fixation(1.0)
    return study_data

# =========================
#  RECOGNITION TRIAL
# =========================
def extract_stimulus_number(image_path):
    """Extract stimulus number from image path (handles both real and placeholder paths)
    
    Args:
        image_path: Path to image file (e.g., "STIMULI/FRUIT/Apple/Image_041.jpg" or "PLACEHOLDERS/IMAGE_41.png")
    
    Returns:
        int: Stimulus number (1-100)
    """
    basename = os.path.basename(image_path)
    # Try to extract number from filename patterns like Image_041.jpg, IMAGE_41.png, Lure_041.jpg, etc.
    # Match patterns like Image_041, IMAGE_41, Lure_041, LURE_41
    match = re.search(r'(?:Image|IMAGE|Lure|LURE)[_ ]*(\d+)', basename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Fallback: try to extract any number from filename
    match = re.search(r'(\d+)', basename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not extract stimulus number from path: {image_path}")

def run_recognition_trial(trial_num, block_num, studied_image_path, is_studied, 
                         participant_first, ai_collaborator, stimuli_dir, experiment_start_time=None, max_trials=10, total_points=0.0, block_start_time=None, partner_name="Amy"):
    """
    Run a single recognition trial
    NOTE: Recognition phase shows BOTH studied images (Image_XXX.jpg) AND lures (Lure_XXX.jpg)
    - If is_studied=True: shows Image_XXX.jpg
    - If is_studied=False: shows Lure_XXX.jpg (corresponding lure)
    """
    trial_data = {}
    
    # Extract stimulus number from the studied image path
    stimulus_num = extract_stimulus_number(studied_image_path)
    
    # Determine which image to show (studied or lure)
    # Check if we're using real stimuli (path contains STIMULI) or placeholders
    use_real_stimuli = STIMULI_DIR in os.path.abspath(studied_image_path) or (
        stimuli_dir and STIMULI_DIR in os.path.abspath(stimuli_dir)
    )
    
    if is_studied:
        image_path = studied_image_path  # Shows Image_XXX.jpg or IMAGE_XXX.png
        trial_type = "studied"
    else:
        # Get corresponding lure - shows Lure_XXX.jpg or LURE_XXX.png
        image_path = get_stimulus_path(stimulus_num, is_lure=True, use_real_stimuli=use_real_stimuli)
        trial_type = "lure"
    
    # Load image
    img_stim = load_image_stimulus(image_path)
    
    # Show image
    show_fixation(0.5)
    img_stim.draw()
    win.flip()
    image_onset = time.time()
    core.wait(1.0)  # Show image for 1 second
    
    # Keep image on screen - don't clear it
    # Determine order: participant first or partner first
    if participant_first:
        # P1: Participant responds first (image stays on screen)
        participant_value, participant_rt, participant_commit_time, participant_slider_timeout, participant_slider_stop_time, participant_slider_decision_onset_time, participant_slider_click_times = get_slider_response(
            "Rate your memory: OLD or NEW?", image_stim=img_stim, trial_num=trial_num, max_trials=max_trials, timeout=7.0
        )
        
        # P2: Partner responds (show animated slider)
        ai_start_time = time.time()
        ai_confidence, ai_rt, ai_correct, ground_truth = ai_collaborator.make_decision(is_studied, trial_type)
        
        # Animate partner's slider tapping and clicking submit
        ai_decision_time = time.time()
        ai_slider_display_time, ai_final_slider_display_time = show_animated_partner_slider(ai_confidence, ai_rt, image_stim=img_stim, partner_name=partner_name, slider_y_pos=SLIDER_Y_POS_ACTUAL)
        
        # Go straight to switch/stay screen (question + image + scores + buttons all at once)
        # Switch/Stay decision (keep image on screen, show euclidean distance)
        switch_decision, switch_rt, switch_commit_time, switch_timeout, decision_onset_time = get_switch_stay_decision(
            image_stim=img_stim, participant_value=participant_value, partner_value=ai_confidence, timeout=7.0, partner_name=partner_name, slider_y_pos=SLIDER_Y_POS_ACTUAL
        )
        
        # Determine final answer
        if switch_decision == "switch":
            final_answer = ai_confidence
            used_ai_answer = True
        else:
            final_answer = participant_value
            used_ai_answer = False
        
        # Calculate accuracy
        if is_studied:
            correct_answer = 0.0  # OLD
        else:
            correct_answer = 1.0  # NEW
        
        participant_accuracy = abs(final_answer - correct_answer) < 0.5  # Within 0.5 of correct
        
        # Record trial data
        trial_data = {
            "block": block_num,
            "trial": trial_num,
            "phase": "recognition",
            "trial_type": trial_type,
            "is_studied": is_studied,
            "image_path": image_path,
            "image_onset": image_onset,
            "participant_first": True,
            "participant_slider_value": participant_value,
            "participant_rt": participant_rt,
            "participant_commit_time": participant_commit_time,
            "participant_slider_timeout": participant_slider_timeout,
            "participant_slider_stop_time": participant_slider_stop_time,
            "participant_slider_decision_onset_time": participant_slider_decision_onset_time,
            "participant_slider_click_times": participant_slider_click_times,
            "ai_slider_value": ai_confidence,
            "ai_rt": ai_rt,
            "ai_decision_time": ai_decision_time,
            "ai_slider_display_time": ai_slider_display_time,
            "ai_final_slider_display_time": ai_final_slider_display_time,
            "ai_correct": ai_correct,
            "ai_reliability": ai_collaborator.accuracy_rate,
            "switch_stay_decision": switch_decision,
            "switch_rt": switch_rt,
            "switch_commit_time": switch_commit_time,
            "switch_timeout": switch_timeout,
            "decision_onset_time": decision_onset_time,
            "final_answer": final_answer,
            "used_ai_answer": used_ai_answer,
            "ground_truth": correct_answer,
            "participant_accuracy": participant_accuracy,
            "euclidean_participant_to_truth": abs(participant_value - correct_answer),
            "euclidean_ai_to_truth": abs(ai_confidence - correct_answer),
            "euclidean_participant_to_ai": abs(participant_value - ai_confidence),
            "outcome_time": np.nan,  # Will be set after show_trial_outcome
            "points_earned": np.nan,  # Will be set after show_trial_outcome
            "block_start_time": np.nan,  # Will be set by update_block_timing_in_csv
            "block_end_time": np.nan,  # Will be set by update_block_timing_in_csv
            "block_duration_seconds": np.nan,  # Will be set by update_block_timing_in_csv
            "block_duration_minutes": np.nan  # Will be set by update_block_timing_in_csv
        }
    else:
        # Partner responds first (show animated slider)
        ai_start_time = time.time()
        ai_confidence, ai_rt, ai_correct, ground_truth = ai_collaborator.make_decision(is_studied, trial_type)
        
        # Animate partner's slider tapping and clicking submit
        ai_decision_time = time.time()
        ai_slider_display_time, ai_final_slider_display_time = show_animated_partner_slider(ai_confidence, ai_rt, image_stim=img_stim, partner_name=partner_name, slider_y_pos=SLIDER_Y_POS_ACTUAL)
        
        # P1: Participant responds (image stays on screen)
        participant_value, participant_rt, participant_commit_time, participant_slider_timeout, participant_slider_stop_time, participant_slider_decision_onset_time, participant_slider_click_times = get_slider_response(
            "Rate your memory: OLD or NEW?", image_stim=img_stim, trial_num=trial_num, max_trials=max_trials, timeout=7.0
        )
        
        # Go straight to switch/stay screen (question + image + scores + buttons all at once)
        # Switch/Stay decision (keep image on screen, show euclidean distance)
        switch_decision, switch_rt, switch_commit_time, switch_timeout, decision_onset_time = get_switch_stay_decision(
            image_stim=img_stim, participant_value=participant_value, partner_value=ai_confidence, timeout=7.0, partner_name=partner_name, slider_y_pos=SLIDER_Y_POS_ACTUAL
        )
        
        # Determine final answer
        if switch_decision == "switch":
            final_answer = ai_confidence
            used_ai_answer = True
        else:
            final_answer = participant_value
            used_ai_answer = False
        
        # Calculate accuracy
        if is_studied:
            correct_answer = 0.0
        else:
            correct_answer = 1.0
        
        participant_accuracy = abs(final_answer - correct_answer) < 0.5
        
        # Record trial data
        trial_data = {
            "block": block_num,
            "trial": trial_num,
            "phase": "recognition",
            "trial_type": trial_type,
            "is_studied": is_studied,
            "image_path": image_path,
            "image_onset": image_onset,
            "participant_first": False,
            "participant_slider_value": participant_value,
            "participant_rt": participant_rt,
            "participant_commit_time": participant_commit_time,
            "participant_slider_timeout": participant_slider_timeout,
            "participant_slider_stop_time": participant_slider_stop_time,
            "participant_slider_decision_onset_time": participant_slider_decision_onset_time,
            "participant_slider_click_times": participant_slider_click_times,
            "ai_slider_value": ai_confidence,
            "ai_rt": ai_rt,
            "ai_decision_time": ai_decision_time,
            "ai_slider_display_time": ai_slider_display_time,
            "ai_final_slider_display_time": ai_final_slider_display_time,
            "ai_correct": ai_correct,
            "ai_reliability": ai_collaborator.accuracy_rate,
            "switch_stay_decision": switch_decision,
            "switch_rt": switch_rt,
            "switch_commit_time": switch_commit_time,
            "switch_timeout": switch_timeout,
            "decision_onset_time": decision_onset_time,
            "final_answer": final_answer,
            "used_ai_answer": used_ai_answer,
            "ground_truth": correct_answer,
            "participant_accuracy": participant_accuracy,
            "euclidean_participant_to_truth": abs(participant_value - correct_answer),
            "euclidean_ai_to_truth": abs(ai_confidence - correct_answer),
            "euclidean_participant_to_ai": abs(participant_value - ai_confidence),
            "outcome_time": None,  # Will be set after show_trial_outcome
            "points_earned": None,  # Will be set after show_trial_outcome
            "block_start_time": None,  # Will be set by update_block_timing_in_csv
            "block_end_time": None,  # Will be set by update_block_timing_in_csv
            "block_duration_seconds": None,  # Will be set by update_block_timing_in_csv
            "block_duration_minutes": None  # Will be set by update_block_timing_in_csv
        }
    
    # Show outcome
    outcome_time = time.time()
    # Calculate points based on euclidean distance (passed to show_trial_outcome)
    points_earned = show_trial_outcome(final_answer, correct_answer, switch_decision, used_ai_answer, total_points=total_points)
    trial_data["outcome_time"] = outcome_time
    trial_data["points_earned"] = points_earned  # Keep CSV field name for compatibility
    
    return trial_data, points_earned

def show_animated_partner_slider(partner_value, partner_rt, image_stim=None, partner_name="Amy", slider_y_pos=None):
    """Animate partner's slider tapping (not sliding) and clicking submit. slider_y_pos must match get_slider_response (use SLIDER_Y_POS_ACTUAL for actual task)."""
    if slider_y_pos is None:
        slider_y_pos = SLIDER_Y_POS_PRACTICE
    # Create slider visualization
    slider_line = visual.Line(
        win,
        start=(-0.4*0.6, slider_y_pos),
        end=(0.4*0.6, slider_y_pos),
        lineColor='black',
        lineWidth=3
    )
    partner_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        pos=(0, slider_y_pos)  # Will be set to target position on tap
    )
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04*0.75*1.35, pos=(-0.5*0.6, slider_y_pos - 0.08))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04*0.75*1.35, pos=(0.5*0.6, slider_y_pos - 0.08))
    partner_text = visual.TextStim(win, text=f"{partner_name} is rating...", color='blue', height=0.04*0.75*1.35, pos=(0, 0.45))  # Move higher to avoid overlap with larger images
    
    # Submit button: same size and same relative position as main task (below slider, never covering it)
    submit_y = slider_y_pos - 0.12
    submit_button = visual.Rect(
        win,
        width=0.25*0.75,
        height=0.06*0.75*1.35,
        fillColor='lightgreen',
        lineColor='black',
        pos=(0, submit_y)
    )
    submit_text = visual.TextStim(win, text="SUBMIT", color='black', height=0.035*0.75*1.35, pos=(0, submit_y))
    
    # Calculate target position
    target_x = -0.4*0.6 + (partner_value * 0.8*0.6)  # Target position
    
    # Wait for most of RT (70%) before showing the tap
    # This maintains RT distribution while showing tap instead of slide
    wait_before_tap = partner_rt * 0.7
    elapsed_wait = 0.0
    start_time = time.time()
    
    # Show slider without handle (partner thinking/deciding)
    while elapsed_wait < wait_before_tap:
        if image_stim:
            image_stim.draw()
        partner_text.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        # Don't draw handle yet - partner hasn't tapped
        submit_button.draw()
        submit_text.draw()
        win.flip()
        
        elapsed_wait = time.time() - start_time
        if elapsed_wait < wait_before_tap:
            core.wait(0.05)
    
    # Show tap animation: create a tap indicator (ripple/highlight) at tap position
    tap_time = time.time()
    tap_indicator = visual.Circle(
        win,
        radius=0.03,
        fillColor='lightblue',
        lineColor='blue',
        lineWidth=2,
        pos=(target_x, slider_y_pos),
        opacity=0.8
    )
    
    # Show tap effect: ripple appears briefly at tap position
    for i in range(3):
        # Tap indicator grows and fades
        tap_indicator.radius = 0.03 + (i * 0.01)
        tap_indicator.opacity = 0.8 - (i * 0.3)
        
        if image_stim:
            image_stim.draw()
        partner_text.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        tap_indicator.draw()  # Show tap indicator
        submit_button.draw()
        submit_text.draw()
        win.flip()
        
        core.wait(0.05)  # Quick tap animation
    
    # Handle appears at target position (tap completed)
    partner_handle.pos = (target_x, slider_y_pos)
    slider_display_time = time.time()  # Time when handle appears at final position
    
    # Brief visual feedback: handle appears with slight highlight
    for i in range(2):
        # Make handle slightly larger/brighten to show tap completion
        partner_handle.fillColor = 'lightblue' if i == 0 else 'blue'
        partner_handle.radius = 0.025 if i == 0 else 0.02
        
        if image_stim:
            image_stim.draw()
        partner_text.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        partner_handle.draw()
        submit_button.draw()
        submit_text.draw()
        win.flip()
        
        core.wait(0.1)
    
    # Wait remaining RT time before submit
    remaining_rt = partner_rt - (time.time() - start_time)
    if remaining_rt > 0:
        core.wait(remaining_rt)
    
    # Animate clicking submit button (highlight button)
    final_slider_display_time = time.time()  # Time when submit button is clicked
    for i in range(3):
        submit_button.fillColor = 'darkgray'
        if image_stim:
            image_stim.draw()
        partner_text.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        partner_handle.draw()
        submit_button.draw()
        submit_text.draw()
        win.flip()
        
        core.wait(0.1)
        
        submit_button.fillColor = 'lightgray'
        if image_stim:
            image_stim.draw()
        partner_text.draw()
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        partner_handle.draw()
        submit_button.draw()
        submit_text.draw()
        win.flip()
        core.wait(0.1)
    
    # Show final result briefly
    if partner_value < 0.5:
        label = "OLD"
    else:
        label = "NEW"
    partner_text.text = f"{partner_name} rates: {label}"
    
    if image_stim:
        image_stim.draw()
    partner_text.draw()
    slider_line.draw()
    old_label.draw()
    new_label.draw()
    partner_handle.draw()
    win.flip()
    core.wait(0.5)
    
    return slider_display_time, final_slider_display_time

def show_both_responses(participant_value, partner_value, participant_first, partner_name="Amy", slider_y_pos=None, image_stim=None):
    """Show both participant and partner responses with sliders. slider_y_pos must match get_slider_response (use SLIDER_Y_POS_ACTUAL for actual task). Draws image if provided so scores don't appear before the image."""
    if slider_y_pos is None:
        slider_y_pos = SLIDER_Y_POS_PRACTICE
    # Create slider visualization for both (dots on same height as scale)
    slider_line = visual.Line(
        win,
        start=(-0.4*0.6, slider_y_pos),
        end=(0.4*0.6, slider_y_pos),
        lineColor='black',
        lineWidth=3
    )
    
    # Participant dot (black) - on scale line
    p_x_pos = -0.4*0.6 + (participant_value * 0.8*0.6)
    p_dot = visual.Circle(win, radius=0.02, fillColor='black', lineColor='black', pos=(p_x_pos, slider_y_pos))
    
    # Partner dot (black) - on same scale line
    a_x_pos = -0.4*0.6 + (partner_value * 0.8*0.6)
    a_dot = visual.Circle(win, radius=0.02, fillColor='black', lineColor='black', pos=(a_x_pos, slider_y_pos))
    
    # Labels below dots, vertical (90°), colored: "you" (green) and partner name (Carly in practice, Amy/Ben in experimental) (blue)
    # Actual trials: labels slightly higher so they stay visible and above dock
    is_actual_scale = (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005)
    label_y = slider_y_pos - (0.05 if is_actual_scale else 0.06)  # Below dots, not hidden
    p_label_text = visual.TextStim(
        win,
        text="you",
        color='green',
        height=0.032*0.75*1.35,
        pos=(p_x_pos, label_y),
        ori=90
    )
    
    a_label_text = visual.TextStim(
        win,
        text=partner_name,  # "Carly" (practice), "Amy" or "Ben" (experimental)
        color='blue',
        height=0.032*0.75*1.35,
        pos=(a_x_pos, label_y),
        ori=90
    )
    
    # Move labels farther from line to avoid overlap
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04*0.75*1.35, pos=(-0.5*0.6, slider_y_pos - 0.08))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04*0.75*1.35, pos=(0.5*0.6, slider_y_pos - 0.08))
    
    # Draw image first (so it appears with the scores, not after)
    if image_stim is not None:
        image_stim.draw()
    slider_line.draw()
    old_label.draw()
    new_label.draw()
    p_label_text.draw()
    a_label_text.draw()
    p_dot.draw()
    a_dot.draw()
    win.flip()

# On switch/stay screen only: move content up to avoid overlap with labels/buttons; STAY/SWITCH buttons stay put
SWITCH_STAY_CONTENT_OFFSET = 0.10

def get_switch_stay_decision(image_stim=None, participant_value=None, partner_value=None, timeout=7.0, partner_name="Amy", slider_y_pos=None):
    """Get switch/stay decision from participant using clickable buttons. slider_y_pos must match get_slider_response (use SLIDER_Y_POS_ACTUAL for actual task)."""
    if slider_y_pos is None:
        slider_y_pos = SLIDER_Y_POS_PRACTICE
    # Move scale/labels/image up on this screen only; buttons stay at slider_y_pos - offset
    line_y = slider_y_pos + SWITCH_STAY_CONTENT_OFFSET
    # Calculate euclidean distance
    euclidean_dist = abs(participant_value - partner_value) if (participant_value is not None and partner_value is not None) else None
    
    # Create slider visualization (dots on scale line; line moved up)
    slider_line = visual.Line(
        win,
        start=(-0.4*0.6, line_y),
        end=(0.4*0.6, line_y),
        lineColor='black',
        lineWidth=3
    )
    
    # Participant dot (black) - on scale line
    p_dot = None
    p_x_pos = None
    p_label_text = None
    a_x_pos = None  # Initialize for distance calculation
    if participant_value is not None:
        p_x_pos = -0.4*0.6 + (participant_value * 0.8*0.6)
        p_dot = visual.Circle(win, radius=0.02, fillColor='black', lineColor='black', pos=(p_x_pos, line_y))
    
    # Partner dot (black) - on same scale line
    a_dot = None
    a_label_text = None
    if partner_value is not None:
        a_x_pos = -0.4*0.6 + (partner_value * 0.8*0.6)
        a_dot = visual.Circle(win, radius=0.02, fillColor='black', lineColor='black', pos=(a_x_pos, line_y))
    
    # Actual trials: smaller offsets so labels stay visible
    is_actual_scale = (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005)
    label_y = line_y - (0.05 if is_actual_scale else 0.06)  # Below dots, not hidden
    if participant_value is not None and p_x_pos is not None:
        p_label_text = visual.TextStim(
            win,
            text="you",
            color='green',
            height=0.032*0.75*1.35,
            pos=(p_x_pos, label_y),
            ori=90
        )
    
    if partner_value is not None and a_x_pos is not None:
        a_label_text = visual.TextStim(
            win,
            text=partner_name,  # "Carly" (practice), "Amy" or "Ben" (experimental)
            color='blue',
            height=0.032*0.75*1.35,
            pos=(a_x_pos, label_y),
            ori=90
        )
    
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04*0.75*1.35, pos=(-0.5*0.6, line_y - 0.08))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04*0.75*1.35, pos=(0.5*0.6, line_y - 0.08))
    
    # Buttons stay at original offset from slider (not moved up)
    button_y_pos = slider_y_pos - (0.10 if is_actual_scale else 0.14)
    stay_button = visual.Rect(
        win,
        width=0.2*0.75,
        height=0.06*0.75*1.35,  # Shorter
        fillColor='lightblue',
        lineColor='black',
        pos=(-0.25*0.6, button_y_pos)
    )
    stay_text = visual.TextStim(win, text="STAY", color='black', height=0.035*0.75*1.35, pos=(-0.25*0.6, button_y_pos))
    
    switch_button = visual.Rect(
        win,
        width=0.28*0.75,  # Wider SWITCH button
        height=0.06*0.75*1.35,  # Shorter
        fillColor='lightcoral',
        lineColor='black',
        pos=(0.28*0.6, button_y_pos)
    )
    switch_text = visual.TextStim(win, text="SWITCH", color='black', height=0.035*0.75*1.35, pos=(0.28*0.6, button_y_pos))
    
    decision_prompt = visual.TextStim(
        win,
        text=f"Do you want to STAY with your answer or SWITCH to {partner_name}'s answer?",
        color='black',
        height=0.04*0.75*1.35,
        wrapWidth=2.5,  # Wide so text stays on one line
        pos=(0, 0.35)   # Slightly higher
    )
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    mouse.setVisible(True)
    decision_onset_time = None  # Will be set when screen first appears
    start_time = None  # Will be set after first flip
    decision_commit_time = None
    decision = None
    decision_rt = None
    prev_mouse_buttons = [False, False, False]
    timed_out = False  # Initialize timeout flag
    first_draw = True  # Track if this is the first draw
    mouse_pos = (0, 0)  # Initialize mouse position
    mouse_buttons = [False, False, False]  # Initialize mouse buttons
    
    # For touch screens, use keyboard method (position-change detection)
    if USE_TOUCH_SCREEN:
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
    
    while True:
        # Check timeout (only after screen has appeared)
        if start_time is not None:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                # Timeout - pick random decision and show alert
                decision = random.choice(["stay", "switch"])
                decision_rt = timeout
                decision_commit_time = time.time()
                timed_out = True
                
                # Show timeout alert
                timeout_alert = visual.TextStim(
                    win,
                    text="Time's up! A random decision was selected.",
                    color='red',
                    height=0.06*1.35,
                    pos=(0, -0.35)  # Lower to avoid overlap with buttons
                )
                decision_prompt.draw()
                if image_stim:
                    # Position image higher on switch/stay screen to avoid overlap
                    image_stim.pos = (0, SWITCH_STAY_CONTENT_OFFSET)
                    image_stim.draw()
                slider_line.draw()
                old_label.draw()
                new_label.draw()
                # Draw labels above arrows
                if participant_value is not None and p_label_text is not None:
                    p_label_text.draw()
                if partner_value is not None and a_label_text is not None:
                    a_label_text.draw()
                if participant_value is not None and p_dot is not None:
                    p_dot.draw()
                if partner_value is not None and a_dot is not None:
                    a_dot.draw()
                timeout_alert.draw()
                win.flip()
                core.wait(1.5)
                break
        
        # Get mouse position and button state (with error handling for macOS)
        try:
            new_mouse_pos = mouse.getPos()
            new_mouse_buttons = mouse.getPressed()
            # Convert mouse position to floats for accurate comparison
            try:
                if hasattr(new_mouse_pos, '__len__') and len(new_mouse_pos) >= 2:
                    mouse_x, mouse_y = float(new_mouse_pos[0]), float(new_mouse_pos[1])
                else:
                    mouse_x, mouse_y = 0.0, 0.0
            except (TypeError, ValueError):
                mouse_x, mouse_y = 0.0, 0.0
            mouse_pos = (mouse_x, mouse_y)  # Store as tuple for compatibility
            mouse_buttons = new_mouse_buttons
        except (AttributeError, Exception) as e:
            # Handle macOS event handling issues - try to recover
            try:
                event.clearEvents()
                # Try to reset mouse (only for non-touch screens)
                if not USE_TOUCH_SCREEN:
                    try:
                        mouse.setPos(mouse_pos)  # Keep current position
                    except:
                        pass
            except:
                pass
            # Keep using previous mouse state instead of defaulting
            core.wait(0.02)  # Slightly longer wait to let system recover
        
        # Clear events periodically to prevent queue buildup (only after screen has appeared, less frequently)
        if start_time is not None:
            elapsed = time.time() - start_time
            if int(elapsed * 5) % 10 == 0:  # Every 2 seconds instead of 0.5
                try:
                    # Don't clear events too aggressively - preserve click detection
                    pass
                except:
                    pass
        
        if USE_TOUCH_SCREEN:
            # Use keyboard method (position-change detection) for touch screens
            # Check if mouse position has changed (touch moved)
            if mouse_x == mouserec_x and mouse_y == mouserec_y:
                # Position hasn't changed, just continue (will redraw below)
                pass
            else:
                # Position changed - check if touch is within buttons using position calculation
                # Check Exit button FIRST (top-right, always clickable)
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                if on_exit:
                    core.quit()
                # Check stay button
                try:
                    stay_pos = stay_button.pos
                    if hasattr(stay_pos, '__len__') and len(stay_pos) >= 2:
                        stay_x, stay_y = float(stay_pos[0]), float(stay_pos[1])
                    else:
                        _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                        stay_x, stay_y = -0.25*0.6, slider_y_pos - _by
                except (TypeError, ValueError, AttributeError):
                    _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                    stay_x, stay_y = -0.25*0.6, slider_y_pos - _by
                
                try:
                    stay_width = float(stay_button.width) if stay_button.width else 0.2*0.75
                    stay_height = float(stay_button.height) if stay_button.height else 0.06*0.75
                except (TypeError, ValueError, AttributeError):
                    stay_width, stay_height = 0.2*0.75, 0.08*0.75
                
                stay_hit_margin_x = max(stay_width * 0.5, 0.08)
                stay_hit_margin_y = max(stay_height * 0.5, 0.04)
                
                stay_clicked = (stay_x - stay_width/2 - stay_hit_margin_x <= mouse_x <= stay_x + stay_width/2 + stay_hit_margin_x and
                               stay_y - stay_height/2 - stay_hit_margin_y <= mouse_y <= stay_y + stay_height/2 + stay_hit_margin_y)
                
                # Check switch button
                try:
                    switch_pos = switch_button.pos
                    if hasattr(switch_pos, '__len__') and len(switch_pos) >= 2:
                        switch_x, switch_y = float(switch_pos[0]), float(switch_pos[1])
                    else:
                        _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                        switch_x, switch_y = 0.28*0.6, slider_y_pos - _by
                except (TypeError, ValueError, AttributeError):
                    _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                    switch_x, switch_y = 0.28*0.6, slider_y_pos - _by
                
                try:
                    switch_width = float(switch_button.width) if switch_button.width else 0.2*0.75
                    switch_height = float(switch_button.height) if switch_button.height else 0.06*0.75
                except (TypeError, ValueError, AttributeError):
                    switch_width, switch_height = 0.2*0.75, 0.08*0.75
                
                switch_hit_margin_x = max(switch_width * 0.5, 0.08)
                switch_hit_margin_y = max(switch_height * 0.5, 0.04)
                
                switch_clicked = (switch_x - switch_width/2 - switch_hit_margin_x <= mouse_x <= switch_x + switch_width/2 + switch_hit_margin_x and
                                 switch_y - switch_height/2 - switch_hit_margin_y <= mouse_y <= switch_y + switch_height/2 + switch_hit_margin_y)
                
                if stay_clicked:
                    decision = "stay"
                    decision_rt = time.time() - start_time
                    decision_commit_time = time.time()
                    break
                elif switch_clicked:
                    decision = "switch"
                    decision_rt = time.time() - start_time
                    decision_commit_time = time.time()
                    break
                
                # Update recorded position
                mouserec = mouse.getPos()
                try:
                    mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                except:
                    mouserec_x, mouserec_y = mouse_x, mouse_y
        else:
            # Standard mouse click detection for non-touch screens
            # Check stay button (convert positions to floats for accurate comparison)
            try:
                stay_pos = stay_button.pos
                if hasattr(stay_pos, '__len__') and len(stay_pos) >= 2:
                    stay_x, stay_y = float(stay_pos[0]), float(stay_pos[1])
                else:
                    _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                    stay_x, stay_y = -0.25*0.6, slider_y_pos - _by
            except (TypeError, ValueError, AttributeError):
                _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                stay_x, stay_y = -0.25*0.6, slider_y_pos - _by
            
            try:
                stay_width = float(stay_button.width) if stay_button.width else 0.2*0.75
                stay_height = float(stay_button.height) if stay_button.height else 0.06*0.75
            except (TypeError, ValueError, AttributeError):
                stay_width, stay_height = 0.2*0.75, 0.08*0.75
            
            stay_clicked = (stay_x - stay_width/2 <= mouse_x <= stay_x + stay_width/2 and
                           stay_y - stay_height/2 <= mouse_y <= stay_y + stay_height/2)
            
            # Check switch button (convert positions to floats for accurate comparison)
            try:
                switch_pos = switch_button.pos
                if hasattr(switch_pos, '__len__') and len(switch_pos) >= 2:
                    switch_x, switch_y = float(switch_pos[0]), float(switch_pos[1])
                else:
                    _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                    switch_x, switch_y = 0.28*0.6, slider_y_pos - _by
            except (TypeError, ValueError, AttributeError):
                _by = 0.10 if (slider_y_pos <= SLIDER_Y_POS_ACTUAL + 0.005) else 0.14
                switch_x, switch_y = 0.28*0.6, slider_y_pos - _by
            
            try:
                switch_width = float(switch_button.width) if switch_button.width else 0.2*0.75
                switch_height = float(switch_button.height) if switch_button.height else 0.06*0.75
            except (TypeError, ValueError, AttributeError):
                switch_width, switch_height = 0.2*0.75, 0.08*0.75
            
            switch_clicked = (switch_x - switch_width/2 <= mouse_x <= switch_x + switch_width/2 and
                             switch_y - switch_height/2 <= mouse_y <= switch_y + switch_height/2)
            
            # Check for mouse button release on buttons
            on_exit_mouse = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                            EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
            if prev_mouse_buttons[0] and not mouse_buttons[0]:
                if on_exit_mouse:
                    core.quit()
                elif stay_clicked:
                    # Button was clicked - change color for visual feedback
                    stay_button.fillColor = 'lightgreen'
                    decision = "stay"
                    decision_rt = time.time() - start_time
                    decision_commit_time = time.time()
                    break
                elif switch_clicked:
                    # Button was clicked - change color for visual feedback
                    switch_button.fillColor = 'lightgreen'
                    decision = "switch"
                    decision_rt = time.time() - start_time
                    decision_commit_time = time.time()
                    break
            
            # Highlight buttons on hover (only for click mode)
            if stay_clicked:
                stay_button.fillColor = 'lightgreen'
            else:
                stay_button.fillColor = 'lightblue'
            
            if switch_clicked:
                switch_button.fillColor = 'lightgreen'
            else:
                switch_button.fillColor = 'lightcoral'
        
        prev_mouse_buttons = mouse_buttons.copy()
        
        # Draw everything in correct order
        decision_prompt.draw()
        
        # Draw image above slider (moved up on this screen to avoid overlap)
        if image_stim:
            image_stim.pos = (0, SWITCH_STAY_CONTENT_OFFSET)
            image_stim.draw()
        
        # Draw slider visualization below image (with arrows showing both ratings)
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        # Draw labels above arrows
        if participant_value is not None and p_label_text is not None:
            p_label_text.draw()
        if partner_value is not None and a_label_text is not None:
            a_label_text.draw()
        if participant_value is not None and p_dot is not None:
            p_dot.draw()
        if partner_value is not None and a_dot is not None:
            a_dot.draw()
        
        # Draw buttons below slider
        stay_button.draw()
        stay_text.draw()
        switch_button.draw()
        switch_text.draw()
        exit_btn.draw()
        exit_text.draw()
        win.flip()
        
        # Record decision onset time on first draw (when screen appears with all info)
        if first_draw:
            decision_onset_time = time.time()
            start_time = time.time()  # Start timing from when screen appears
            first_draw = False
        
        # Check for escape (with error handling)
        try:
            # Safe event.getKeys() handling - ensure keys is never empty array issue
            try:
                keys = event.getKeys(keyList=['escape'])
                if keys and 'escape' in keys:  # Check keys is not empty first
                    core.quit()
            except (AttributeError, Exception):
                pass  # Ignore event errors
        except (AttributeError, Exception):
            # Ignore event errors, just continue
            pass
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    return decision, decision_rt, decision_commit_time, timed_out, decision_onset_time

def show_ready_to_start_screen(block_num, total_blocks=10):
    """Show 'ready to start sorting?' screen before each block with collections remaining count"""
    collections_remaining = total_blocks - block_num + 1
    
    ready_text = visual.TextStim(
        win,
        text=f"Ready to start sorting?\n\n"
             f"{collections_remaining} collection{'s' if collections_remaining > 1 else ''} remaining",
        color='black',
        height=0.06*0.75*1.35,
        pos=(0, 0.3),  # Move higher to avoid overlap with larger images
        wrapWidth=1.2
    )
    
    # Create begin button
    begin_button = visual.Rect(
        win,
        width=0.3*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.4*0.6)  # Moved away from edge for better clickability
    )
    begin_text = visual.TextStim(
        win,
        text="BEGIN",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
        pos=(0, -0.4*0.6)  # Moved away from edge for better clickability
    )
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    # Draw initial screen
    def redraw():
        ready_text.draw()
        begin_button.draw()
        begin_text.draw()
        exit_btn.draw()
        exit_text.draw()
        win.flip()
    
    redraw()
    
    # Wait for button click - use same pattern as other touch screen buttons
    mouse_btn = event.Mouse(win=win)
    mouse_btn.setVisible(True)
    clicked = False
    last_hover_state = None
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse_btn.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse_btn.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    redraw()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    try:
                        button_pos = begin_button.pos
                        if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                            button_x, button_y = float(button_pos[0]), float(button_pos[1])
                        else:
                            button_x, button_y = 0.0, -0.4*0.6  # Updated to match new button position
                    except (TypeError, ValueError):
                        button_x, button_y = 0.0, -0.35*0.6
                    
                    try:
                        button_width = float(begin_button.width)
                        button_height = float(begin_button.height)
                    except (TypeError, ValueError):
                        button_width, button_height = 0.3*0.75, 0.1*0.75
                    
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                              EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    
                    if on_exit:
                        core.quit()
                    elif on_button:
                        # Visual feedback (no color change in touch screen mode)
                        redraw()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse_btn.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                redraw()
            except (AttributeError, Exception):
                pass
            
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        
        while not clicked:
            try:
                mouse_buttons = mouse_btn.getPressed()
                mouse_pos = mouse_btn.getPos()
                
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                try:
                    button_pos = begin_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x, button_y = float(button_pos[0]), float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, -0.35*0.6
                except (TypeError, ValueError):
                    button_x, button_y = 0.0, -0.35*0.6
                
                try:
                    button_width = float(begin_button.width)
                    button_height = float(begin_button.height)
                except (TypeError, ValueError):
                    button_width, button_height = 0.3*0.75, 0.1*0.75
                
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_exit:
                        core.quit()
                    elif on_button:
                        begin_button.fillColor = 'lightgreen'
                        redraw()
                        core.wait(0.2)
                        clicked = True
                        break
                
                if on_button != last_hover_state:
                    if on_button:
                        begin_button.fillColor = 'lightcyan'
                    else:
                        begin_button.fillColor = 'lightblue'
                    redraw()
                    last_hover_state = on_button
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
            # Check for space key as backup
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    
    mouse_btn.setVisible(False)
    event.clearEvents()

def show_block_summary(block_num, total_points, max_points):
    """Show block summary with curator scoring"""
    # Show actual points out of max_points (rounded to 1 decimal place for display, full precision maintained in logged data)
    total_points_rounded = round(total_points, 1)
    
    summary_text = visual.TextStim(
        win,
        text=f"Collection {block_num} Complete!\n\n"
             f"The in-house curator scored this collection {total_points_rounded:.1f} points out of a total of {int(max_points)} points!",
        color='black',
        height=0.04*0.75*1.35,
        pos=(0, 0.1),
        wrapWidth=1.2
    )
    
    # Create continue button
    continue_button = visual.Rect(
        win,
        width=0.3,
        height=0.1*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.4)  # Moved away from edge for better clickability
    )
    continue_text = visual.TextStim(
        win,
        text="CONTINUE",
        color='black',
        height=0.04*1.35,  # Reduced to ensure text fits within button
        pos=(0, -0.4)  # Moved away from edge for better clickability
    )
    
    # Draw initial screen
    summary_text.draw()
    continue_button.draw()
    continue_text.draw()
    win.flip()
    
    # Wait for button click - use keyboard method for touch screens
    mouse_btn = event.Mouse(win=win)
    mouse_btn.setVisible(True)
    clicked = False
    last_hover_state = None
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse_btn.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse_btn.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    summary_text.draw()
                    continue_button.draw()
                    continue_text.draw()
                    win.flip()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    try:
                        button_pos = continue_button.pos
                        if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                            button_x, button_y = float(button_pos[0]), float(button_pos[1])
                        else:
                            button_x, button_y = 0.0, -0.4  # Updated to match new button position
                    except (TypeError, ValueError):
                        button_x, button_y = 0.0, -0.35
                    
                    try:
                        button_width = float(continue_button.width)
                        button_height = float(continue_button.height)
                    except (TypeError, ValueError):
                        button_width, button_height = 0.3, 0.1
                    
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    
                    if on_button:
                        # Visual feedback (no color change in touch screen mode)
                        summary_text.draw()
                        continue_button.draw()
                        continue_text.draw()
                        win.flip()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse_btn.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                summary_text.draw()
                continue_button.draw()
                continue_text.draw()
                win.flip()
            except (AttributeError, Exception):
                pass
            
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        
        while not clicked:
            try:
                mouse_buttons = mouse_btn.getPressed()
                mouse_pos = mouse_btn.getPos()
                
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                try:
                    button_pos = continue_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x, button_y = float(button_pos[0]), float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, -0.35
                except (TypeError, ValueError):
                    button_x, button_y = 0.0, -0.35
                
                try:
                    button_width = float(continue_button.width)
                    button_height = float(continue_button.height)
                except (TypeError, ValueError):
                    button_width, button_height = 0.3, 0.1
                
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_button:
                        continue_button.fillColor = 'lightgreen'
                        summary_text.draw()
                        continue_button.draw()
                        continue_text.draw()
                        win.flip()
                        core.wait(0.2)
                        clicked = True
                        break
                
                if on_button != last_hover_state:
                    if on_button:
                        continue_button.fillColor = 'lightcyan'
                    else:
                        continue_button.fillColor = 'lightblue'
                    summary_text.draw()
                    continue_button.draw()
                    continue_text.draw()
                    win.flip()
                    last_hover_state = on_button
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
            # Check for space key as backup
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                elif 'escape' in keys:
                    core.quit()
            except (AttributeError, Exception):
                pass
            
            safe_wait(0.01)
    
    mouse_btn.setVisible(False)
    event.clearEvents()

def show_leaderboard(participant_id, total_points):
    """Show a fake leaderboard with participant ranked 2 out of 5"""
    # Generate fake participant names (P01-P05, excluding current participant)
    all_participants = [f"P{i:02d}" for i in range(1, 6)]
    current_participant_label = participant_id if len(participant_id) <= 10 else participant_id[:10]
    
    # Participant is always ranked 2 out of 5
    participant_rank = 2
    total_players = 5
    
    # Generate fake scores: 1 above participant (rank 1), rest below (ranks 3-5)
    fake_scores = []
    
    # Generate 1 score above participant (for rank 1)
    fake_scores.append(total_points + random.uniform(0.1, 5.0))
    
    # Generate (total_players - participant_rank) scores below participant (ranks 3-5)
    for _ in range(total_players - participant_rank):
        fake_scores.append(total_points - random.uniform(0.1, 15.0))
    
    # Combine all scores and sort
    all_scores = fake_scores + [total_points]
    all_scores = sorted(all_scores, reverse=True)
    
    # Create leaderboard entries
    leaderboard_entries = []
    used_names = set()
    for i, score in enumerate(all_scores[:total_players], 1):
        # At the participant's rank, always show their actual total_points
        if i == participant_rank:
            name = f"{current_participant_label} (you)"
            display_score = total_points  # Always show the actual total_points (out of 100)
            used_names.add(current_participant_label)
        else:
            # Assign fake names, avoiding the current participant's label
            available_names = [p for p in all_participants if p not in used_names and p != current_participant_label]
            if available_names:
                name = available_names[0]
                used_names.add(name)
            else:
                name = f"P{i:02d}"
            display_score = score
        leaderboard_entries.append((i, name, display_score))
    
    # Display leaderboard (without scores)
    leaderboard_text = "AMY'S EMPLOYEE RANKING & LEADERSHIP BOARD\n\n"
    leaderboard_text += f"{'Rank':<6} {'Participant':<20}\n"
    leaderboard_text += "-" * 30 + "\n"
    
    for rank, name, score in leaderboard_entries:
        leaderboard_text += f"{rank:<6} {name:<20}\n"
    
    leaderboard_stim = visual.TextStim(
        win,
        text=leaderboard_text,
        color='black',
        height=0.04*1.35,
        pos=(0, 0.05),  # Lower so full board visible and not cut off at bottom
        wrapWidth=1.6,
        font='Courier New'  # Monospace font for alignment
    )
    
    # Redraw function that only draws the leaderboard (wait_for_button will handle the button)
    def redraw():
        # Always draw leaderboard to ensure it's visible
        leaderboard_stim.draw()
        # Note: wait_for_button will draw its own button and call win.flip()
    
    # Initial draw to show leaderboard immediately
    leaderboard_stim.draw()
    win.flip()
    
    # Use wait_for_button with lower button position to avoid overlap with leaderboard text
    wait_for_button(redraw_func=redraw, button_y=-0.5)

def show_trial_outcome(final_answer, correct_answer, switch_decision, used_ai_answer, total_points=0):
    """Show trial outcome with points based on euclidean distance"""
    # Calculate correctness points based on euclidean distance from correct answer
    # Points = 1 - distance, so closer answers get more points (max 1.0, min 0.0)
    euclidean_distance = abs(final_answer - correct_answer)
    correctness_points = max(0.0, 1.0 - euclidean_distance)  # Closer = more points
    
    # Round to 1 decimal place for display only (full precision kept in logged data)
    correctness_points_rounded = round(correctness_points, 1)
    
    # Determine if answer is correct (within 0.5 of correct answer)
    participant_accuracy = euclidean_distance < 0.5
    
    if participant_accuracy:
        outcome_text = "Correct"
        color = 'green'
    else:
        outcome_text = "Incorrect"
        color = 'red'
    
    # Show outcome with curator scoring (display rounded to 1 decimal place)
    outcome_text_full = f"{outcome_text}.\n\nThe in-house curator scored this image: {correctness_points_rounded:.1f} points based on image & your confidence."
    outcome_stim = visual.TextStim(win, text=outcome_text_full, color=color, height=0.06*1.35, pos=(0, 0), wrapWidth=1.4)
    outcome_stim.draw()
    win.flip()
    core.wait(2.0)  # Show for 2.0 seconds (increased from 1.5)
    
    # Return points earned this trial
    return correctness_points

# =========================
#  BLOCK STRUCTURE
# =========================
def run_block(block_num, studied_images, block_start_participant_first, ai_collaborator, stimuli_dir, num_trials=None, experiment_start_time=None, participant_id=None, study_file=None, trial_file=None):
    """Run a single block: study phase + recognition trials
    
    Args:
        stimuli_dir: Directory containing stimuli (STIMULI_DIR for real stimuli, PLACEHOLDER_DIR for practice)
        block_start_participant_first: True if first trial in block has participant first, False if AI first
    """
    all_trial_data = []
    
    # Record block start time
    block_start_time = time.time()
    
    # Determine number of trials (default to number of studied images, or use num_trials if provided)
    if num_trials is None:
        num_trials = len(studied_images)
    
    # Initialize file names for incremental saving (if not provided)
    if participant_id and study_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = get_log_directory()
        study_file = os.path.join(log_dir, f"recognition_study_{participant_id}_{timestamp}.csv")
        trial_file = os.path.join(log_dir, f"recognition_trials_{participant_id}_{timestamp}.csv")
    
    # Phase 1: Study
    study_data = run_study_phase(studied_images, block_num)
    
    # Save study data immediately after study phase
    if participant_id:
        study_file, trial_file = save_data_incremental(
            study_data, [], participant_id,
            study_file=study_file, trial_file=trial_file
        )
    
    # Determine partner name based on block accuracy (Amy = reliable, Ben = unreliable)
    partner_name = "Amy" if ai_collaborator.accuracy_rate == 0.75 else "Ben"
    
    # Transition screen: switching to recognition phase
    show_instructions(
        "STUDYING COLLECTION IMAGES COMPLETE!\n\n"
        "Now switching to the sorting phase.\n\n"
        f"You will see MORE images again and rate them with {partner_name}.",
        header_color='darkblue',
        body_color='black'
    )
    
    # Wait 0.5 seconds between study and retrieval phases
    core.wait(0.5)
    
    # Phase 2: Recognition (num_trials trials total)
    # Each of the studied images appears exactly once (as either studied or lure)
    # Ensure exactly 50% are studied, 50% are lures
    num_studied_trials = num_trials // 2
    num_lure_trials = num_trials - num_studied_trials
    
    # Create trial sequence: each studied image appears exactly once
    # Randomly assign each image to be either studied or lure
    image_assignments = []
    for img_path in studied_images:
        image_assignments.append(img_path)
    
    # Get the last image shown in study phase to avoid it being first in retrieval
    last_study_image = studied_images[-1] if studied_images else None
    
    # Shuffle and assign: first half as studied, second half as lures
    random.shuffle(image_assignments)
    
    trial_sequence = []
    for i, img_path in enumerate(image_assignments):
        if i < num_studied_trials:
            trial_sequence.append((i+1, img_path, True))  # is_studied = True
        else:
            trial_sequence.append((i+1, img_path, False))  # is_studied = False
    
    # Randomize order of trials
    random.shuffle(trial_sequence)
    
    # Ensure first trial is not the same as last study image
    # Check the actual image that will be shown (Image_XXX.jpg for studied, Lure_XXX.jpg for lures)
    if last_study_image and len(trial_sequence) > 1:
        # Get the stimulus number from last study image
        last_study_stim_num = extract_stimulus_number(last_study_image)
        
        # Check first trial - get what image will actually be shown
        first_trial_img_path, first_is_studied = trial_sequence[0][1], trial_sequence[0][2]
        first_trial_stim_num = extract_stimulus_number(first_trial_img_path)
        
        # If first trial shows the same stimulus as last study (regardless of studied/lure), swap it
        if first_trial_stim_num == last_study_stim_num:
            # Find a different trial to swap with (one that doesn't match last study)
            for i in range(1, len(trial_sequence)):
                swap_trial_img_path = trial_sequence[i][1]
                swap_trial_stim_num = extract_stimulus_number(swap_trial_img_path)
                if swap_trial_stim_num != last_study_stim_num:
                    trial_sequence[0], trial_sequence[i] = trial_sequence[i], trial_sequence[0]
                    break
    
    # Renumber trials after shuffling
    trial_sequence = [(i+1, img_path, is_studied) for i, (_, img_path, is_studied) in enumerate(trial_sequence)]
    
    total_points = 0.0  # Track total points (correctness only)
    max_possible_points = float(num_trials)  # Max points from correctness only (1.0 per trial)
    
    # Randomly select 5 trials where AI goes first (out of 10 trials per block)
    # This ensures AI goes first on exactly 5 random trials in each block
    ai_first_trials = set(random.sample(range(num_trials), num_trials // 2))
    
    for trial_idx, (trial_num, img_path, is_studied) in enumerate(trial_sequence):
        # Determine turn order: AI goes first on randomly selected trials, participant goes first on others
        participant_first = trial_idx not in ai_first_trials
        
        trial_data, points_earned = run_recognition_trial(
            trial_num, block_num, img_path, is_studied,
            participant_first, ai_collaborator, stimuli_dir, experiment_start_time, max_trials=num_trials, total_points=total_points,
            block_start_time=block_start_time, partner_name=partner_name
        )
        # Add block timing (end time and duration will be updated at end of block)
        trial_data['block_start_time'] = block_start_time
        trial_data['block_end_time'] = None  # Will be updated at end of block
        trial_data['block_duration_seconds'] = None  # Will be updated at end of block
        trial_data['block_duration_minutes'] = None  # Will be updated at end of block
        
        all_trial_data.append(trial_data)
        total_points += points_earned  # Includes correctness only
        
        # Save data after each trial (not each block)
        if participant_id:
            # Save single trial immediately - update file references
            study_file, trial_file = save_data_incremental(
                [], [trial_data], participant_id,
                study_file=study_file, trial_file=trial_file
            )
        
        # Add jittered fixation between recognition trials (0.25-0.75 seconds)
        # Don't add jitter after the last trial
        if trial_idx < len(trial_sequence) - 1:
            jitter_duration = random.uniform(0.25, 0.75)
            show_fixation(jitter_duration)
    
    # Show block summary with points (total over max possible from correctness)
    show_block_summary(block_num, total_points, max_possible_points)
    
    
    # Record block end time and calculate duration
    block_end_time = time.time()
    block_duration = block_end_time - block_start_time
    
    # Update block timing information in all trial data
    for trial_data in all_trial_data:
        trial_data['block_end_time'] = block_end_time
        trial_data['block_duration_seconds'] = block_duration
        trial_data['block_duration_minutes'] = block_duration / 60.0
    
    # Update the CSV file with block timing for all trials in this block
    if participant_id and trial_file and os.path.exists(trial_file) and not is_test_participant(participant_id):
        update_block_timing_in_csv(trial_file, block_num, block_start_time, block_end_time, block_duration)
    
    return study_data, all_trial_data, study_file, trial_file, total_points

# =========================
#  UPDATE BLOCK TIMING IN CSV
# =========================
def update_block_timing_in_csv(trial_file, block_num, block_start_time, block_end_time, block_duration):
    """Update CSV file with block timing information for all trials in a block"""
    try:
        # Read all rows from CSV
        rows = []
        fieldnames = None
        with open(trial_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # Update rows for this block
        updated_count = 0
        for row in rows:
            # Handle empty string or missing block value
            block_value = row.get('block', '').strip()
            if block_value and block_value != '':
                try:
                    if int(block_value) == block_num:
                        row['block_start_time'] = block_start_time
                        row['block_end_time'] = block_end_time
                        row['block_duration_seconds'] = block_duration
                        row['block_duration_minutes'] = block_duration / 60.0
                        updated_count += 1
                except (ValueError, TypeError):
                    continue
        
        # Write updated rows back to CSV
        if updated_count > 0:
            # Ensure timing fields are in fieldnames
            timing_fields = ['block_start_time', 'block_end_time', 'block_duration_seconds', 'block_duration_minutes']
            if fieldnames:
                for field in timing_fields:
                    if field not in fieldnames:
                        fieldnames.append(field)
            
            with open(trial_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                # Ensure all fields are present and handle NaN values
                for row in rows:
                    complete_row = {}
                    for field in fieldnames:
                        value = row.get(field, '')
                        # Convert empty strings to empty strings (keep as is for CSV)
                        complete_row[field] = value if value != '' else ''
                    writer.writerow(complete_row)
            
            print(f"✓ Updated block {block_num} timing in CSV ({updated_count} trials)")
    except Exception as e:
        print(f"Warning: Could not update block timing in CSV: {e}")

# =========================
#  DATA SAVING
# =========================
def save_data_incremental(all_study_data, all_trial_data, participant_id,
                          study_file=None, trial_file=None):
    """Save data incrementally"""
    # Skip saving if test participant
    if is_test_participant(participant_id):
        print(f"⚠ Test participant detected - skipping file save")
        return None, None
    
    if study_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = get_log_directory()
        study_file = os.path.join(log_dir, f"recognition_study_{participant_id}_{timestamp}.csv")
        trial_file = os.path.join(log_dir, f"recognition_trials_{participant_id}_{timestamp}.csv")
    
    # Save study data
    if all_study_data and len(all_study_data) > 0:
        file_exists = os.path.exists(study_file)
        with open(study_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_study_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_study_data)
            f.flush()
        print(f"✓ Study data saved ({len(all_study_data)} rows)")
    
    # Save trial data
    if all_trial_data and len(all_trial_data) > 0:
        file_exists = os.path.exists(trial_file)
        
        # Get all unique fieldnames from all trial data rows
        all_fieldnames = set()
        for row in all_trial_data:
            all_fieldnames.update(row.keys())
        all_fieldnames = sorted(list(all_fieldnames))
        
        # If file exists, read existing fieldnames and merge
        if file_exists:
            try:
                with open(trial_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    existing_fieldnames = reader.fieldnames or []
                    # Merge fieldnames, preserving order (existing first, then new)
                    all_fieldnames = list(existing_fieldnames) + [f for f in all_fieldnames if f not in existing_fieldnames]
            except Exception as e:
                print(f"Warning: Could not read existing CSV fieldnames: {e}")
        
        with open(trial_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            # Ensure all rows have all fields (fill missing with NaN)
            for row in all_trial_data:
                complete_row = {}
                for field in all_fieldnames:
                    value = row.get(field, np.nan)
                    # Convert NaN to empty string for CSV (standard CSV representation)
                    if isinstance(value, float) and np.isnan(value):
                        complete_row[field] = ''
                    elif isinstance(value, list):
                        # Convert list to comma-separated string for CSV
                        if len(value) == 0:
                            complete_row[field] = ''
                        else:
                            complete_row[field] = ','.join(str(v) for v in value)
                    elif value is None:
                        complete_row[field] = ''
                    elif isinstance(value, bool):
                        # Convert boolean to string for CSV compatibility
                        complete_row[field] = str(value)
                    else:
                        complete_row[field] = value
                writer.writerow(complete_row)
            f.flush()
        print(f"✓ Trial data saved ({len(all_trial_data)} rows)")
    
    return study_file, trial_file

# =========================
#  MAIN EXPERIMENT
# =========================
def run_experiment():
    """Run the full experiment"""
    # Force window to front and ensure it has focus
    try:
        win.winHandle.activate()  # Bring window to front (macOS)
        core.wait(0.2)  # Give window time to activate and gain focus
    except:
        pass
    
    # Clear any existing events before starting
    try:
        event.clearEvents()
    except Exception as e:
        print(f"Warning: Error clearing events at start: {e}", file=sys.stderr)
    
    # Initial click-to-start screen with button
    start_screen = visual.TextStim(
        win,
        text="Hello & welcome to the social memory game! Pay careful attention to the text on the screen. Some images will be very deceptively similar.",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
        pos=(0, 0.4*0.6),  # Moved higher to avoid overlap with button
        wrapWidth=1.4*0.75
    )
    
    start_button = visual.Rect(
        win,
        width=0.3*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0, -0.45*0.6)  # Moved closer to bottom
    )
    start_button_text = visual.TextStim(
        win,
        text="BEGIN",
        color='black',
        height=0.04*0.75*1.35,
        pos=(0, -0.45*0.6)  # Match button position
    )
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    # Create mouse instance for this function (since we assign to mouse later, Python treats it as local)
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    if not USE_TOUCH_SCREEN:
        try:
            mouse.setPos((0, 0))  # Reset mouse position
        except:
            pass  # May fail on some systems
    
    # Draw initial screen
    start_screen.draw()
    start_button.draw()
    start_button_text.draw()
    exit_btn.draw()
    exit_text.draw()
    win.flip()
    
    # Clear any existing events before waiting for click
    event.clearEvents()
    mouse.clickReset()
    
    # Wait for button click
    clicked = False
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    start_screen.draw()
                    start_button.draw()
                    start_button_text.draw()
                    exit_btn.draw()
                    exit_text.draw()
                    win.flip()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                              EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    try:
                        button_pos = start_button.pos
                        if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                            button_x, button_y = float(button_pos[0]), float(button_pos[1])
                        else:
                            button_x, button_y = 0.0, -0.3*0.6
                    except (TypeError, ValueError):
                        button_x, button_y = 0.0, -0.3*0.6
                    
                    try:
                        button_width = float(start_button.width)
                        button_height = float(start_button.height)
                    except (TypeError, ValueError):
                        button_width, button_height = 0.3*0.75, 0.1*0.75
                    
                    # For touch screens, use larger hit area (at least button size, or larger)
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    
                    if on_exit:
                        core.quit()
                    elif on_button:
                        # Visual feedback (no color change in touch screen mode)
                        start_screen.draw()
                        start_button.draw()
                        start_button_text.draw()
                        exit_btn.draw()
                        exit_text.draw()
                        win.flip()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                print(f"Warning: Error in begin button loop: {e}", file=sys.stderr)
            
            # Check for keyboard input as backup
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if 'space' in keys:
                    clicked = True
                    break
                if 'escape' in keys:
                    core.quit()
            except (AttributeError, RuntimeError):
                pass
            
            core.wait(0.01)
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        last_hover_state = None
        
        while not clicked:
            try:
                mouse_buttons = mouse.getPressed()
                mouse_pos = mouse.getPos()
                
                # Convert to floats
                try:
                    if hasattr(mouse_pos, '__len__') and len(mouse_pos) >= 2:
                        mouse_x, mouse_y = float(mouse_pos[0]), float(mouse_pos[1])
                    else:
                        mouse_x, mouse_y = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x, mouse_y = 0.0, 0.0
                
                # Get button bounds
                try:
                    button_pos = start_button.pos
                    if hasattr(button_pos, '__len__') and len(button_pos) >= 2:
                        button_x, button_y = float(button_pos[0]), float(button_pos[1])
                    else:
                        button_x, button_y = 0.0, -0.3
                except (TypeError, ValueError):
                    button_x, button_y = 0.0, -0.3
                
                try:
                    button_width = float(start_button.width)
                    button_height = float(start_button.height)
                except (TypeError, ValueError):
                    button_width, button_height = 0.3, 0.1
                
                # Check if mouse is over button
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                # Check for button release (mouse was pressed on button and now released)
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_exit:
                        core.quit()
                    elif on_button:
                        # Visual feedback (only for click mode, not touch screen)
                        if not USE_TOUCH_SCREEN:
                            start_button.fillColor = 'lightgreen'
                        start_screen.draw()
                        start_button.draw()
                        start_button_text.draw()
                        exit_btn.draw()
                        exit_text.draw()
                        win.flip()
                        core.wait(0.2)
                        clicked = True
                        break
                
                # Hover effect for click mode (only redraw if hover state changes)
                if on_button != last_hover_state:
                    if on_button:
                        start_button.fillColor = 'lightcyan'
                    else:
                        start_button.fillColor = 'lightblue'
                    start_screen.draw()
                    start_button.draw()
                    start_button_text.draw()
                    exit_btn.draw()
                    exit_text.draw()
                    win.flip()
                    last_hover_state = on_button
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
            # Check for keyboard input as backup
            keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
            if 'space' in keys:
                clicked = True
                break
            if 'escape' in keys:
                core.quit()
            
            core.wait(0.01)
    
    mouse.setVisible(False)
    event.clearEvents()
    
    # Small delay to ensure window is ready
    core.wait(0.5)
    
    # Input method was already asked before window creation
    # Record experiment start time
    experiment_start_time = time.time()
    
    participant_id = get_participant_id()
    
    # Initialize file names once for the entire experiment
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = get_log_directory()
    study_file = os.path.join(log_dir, f"recognition_study_{participant_id}_{timestamp}.csv")
    trial_file = os.path.join(log_dir, f"recognition_trials_{participant_id}_{timestamp}.csv")
    
    # New interactive practice block
    practice_study = []
    practice_trials = []
    practice_points = 0.0
    
    # Load and display Carly's picture for practice (uses same image as Amy.png, no label)
    carly_image_path = os.path.join(STIMULI_DIR, "Amy.png")
    if os.path.exists(carly_image_path):
        carly_image = load_image_stimulus(carly_image_path, maintain_aspect_ratio=True)
        # Position Carly's image below the text (closer to text for better spacing)
        if hasattr(carly_image, 'setPos'):
            carly_image.setPos((0, -0.05))  # Closer to text
        elif hasattr(carly_image, 'pos'):
            carly_image.pos = (0, -0.05)  # Closer to text
    else:
        carly_image = None
        print(f"Warning: Amy.png not found at {carly_image_path}", file=sys.stderr)
    
    # Show first welcome screen with Carly's picture (Amy's assistant, practice only; same image as Amy)
    welcome_text_1 = visual.TextStim(
        win,
        text="Greetings!\n\n"
             "You've just joined Amy's photography studio. She's preparing images for an upcoming exhibition.\n\n"
             "Carly, her assistant, will walk you through a short practice to get familiar with the task.",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
        pos=(0, 0.25),  # Moved down for better spacing with image
        wrapWidth=1.2
    )
    
    # Create custom button for this screen (positioned bottom right to avoid icon overlap)
    continue_button_welcome = visual.Rect(
        win,
        width=0.3*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
    )
    continue_text_welcome = visual.TextStim(
        win,
        text="CONTINUE",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
        pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
    )
    exit_btn = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    def redraw_welcome_1():
        welcome_text_1.draw()  # Draw text first
        if carly_image:
            carly_image.draw()
        continue_button_welcome.draw()
        continue_text_welcome.draw()
        exit_btn.draw()
        exit_text.draw()
    
    # Custom wait for button with custom button position
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    def draw_screen():
        redraw_welcome_1()
        win.flip()
    
    draw_screen()
    
    clicked = False
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec = mouse.getPos()
        try:
            mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
        except:
            mouserec_x, mouserec_y = 0.0, 0.0
        
        while not clicked:
            try:
                mouseloc = mouse.getPos()
                try:
                    mouseloc_x, mouseloc_y = float(mouseloc[0]), float(mouseloc[1])
                except:
                    mouseloc_x, mouseloc_y = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x == mouserec_x and mouseloc_y == mouserec_y:
                    # Position hasn't changed, just redraw
                    draw_screen()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    button_x, button_y = 0.4, -0.3  # Updated to match button position
                    button_width, button_height = 0.3*0.75, 0.1*0.75
                    hit_margin_x = max(button_width * 0.5, 0.08)
                    hit_margin_y = max(button_height * 0.5, 0.04)
                    
                    on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                              EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x <= button_x + button_width/2 + hit_margin_x and
                                button_y - button_height/2 - hit_margin_y <= mouseloc_y <= button_y + button_height/2 + hit_margin_y)
                    
                    if on_exit:
                        core.quit()
                    elif on_button:
                        # Visual feedback (no color change in touch screen mode)
                        draw_screen()
                        core.wait(0.2)
                        clicked = True
                        break
                    
                    # Update recorded position
                    mouserec = mouse.getPos()
                    try:
                        mouserec_x, mouserec_y = float(mouserec[0]), float(mouserec[1])
                    except:
                        mouserec_x, mouserec_y = mouseloc_x, mouseloc_y
                
                # Redraw every frame
                draw_screen()
            except (AttributeError, Exception):
                pass
            
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
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons = [False, False, False]
        
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
                
                button_x, button_y = 0.4, -0.3  # Updated to match button position
                button_width, button_height = 0.3*0.75, 0.1*0.75
                
                on_exit = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                          EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                            button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                
                if prev_mouse_buttons[0] and not mouse_buttons[0]:
                    if on_exit:
                        core.quit()
                    elif on_button:
                        continue_button_welcome.fillColor = 'lightgreen'
                        draw_screen()
                        core.wait(0.2)
                        clicked = True
                        break
                
                if on_button:
                    continue_button_welcome.fillColor = 'lightcyan'
                else:
                    continue_button_welcome.fillColor = 'lightblue'
                draw_screen()
                
                prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
            except (AttributeError, Exception):
                pass
            
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
    
    # Show second welcome screen (no image, just text)
    welcome_text_2 = visual.TextStim(
        win,
        text="Before you begin the real work, you'll complete a short training round to get familiar with the process.\n\n"
             "For now, simply memorize the shapes you're about to see. Click CONTINUE when you're ready to get started!",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
        pos=(0, 0.0),
        wrapWidth=1.2
    )
    
    def redraw_welcome_2():
        welcome_text_2.draw()
    
    wait_for_button(redraw_func=redraw_welcome_2)
    
    # Generate practice shapes as placeholder stimuli (IMAGE_1, IMAGE_2, IMAGE_3)
    # Green circle
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='green', outline='black', width=3)
    green_circle_path = os.path.join(PLACEHOLDER_DIR, "IMAGE_1.png")
    img.save(green_circle_path)
    
    # Red circle
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='red', outline='black', width=3)
    red_circle_path = os.path.join(PLACEHOLDER_DIR, "IMAGE_2.png")
    img.save(red_circle_path)
    
    # Blue circle (for encoding/sequential presentation)
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 180, 180], fill='blue', outline='black', width=3)
    blue_circle_path = os.path.join(PLACEHOLDER_DIR, "IMAGE_3_CIRCLE.png")
    img.save(blue_circle_path)
    
    # Blue square (for trial 3 recognition - it's NEW, not seen before)
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 180, 180], fill='blue', outline='black', width=3)
    blue_square_path = os.path.join(PLACEHOLDER_DIR, "IMAGE_3.png")
    img.save(blue_square_path)
    
    # Show shapes sequentially with fixations (like study phase)
    # Use default size from load_image_stimulus (0.3, 0.3) and position (0, 0) to match regular task
    # Show green circle
    show_fixation(0.5)
    green_circle = load_image_stimulus(green_circle_path)
    # Don't set position/size - use defaults (0, 0) and (0.3, 0.3) to match regular task
    if hasattr(green_circle, 'draw'):
        green_circle.draw()
    else:
        green_circle = visual.Circle(win, radius=0.15, fillColor='green', lineColor='black', pos=(0, 0))
        green_circle.draw()
    win.flip()
    core.wait(1.5)  # Show for 1.5 seconds
    
    # Show red circle
    show_fixation(0.5)
    red_circle = load_image_stimulus(red_circle_path)
    # Don't set position/size - use defaults (0, 0) and (0.3, 0.3) to match regular task
    if hasattr(red_circle, 'draw'):
        red_circle.draw()
    else:
        red_circle = visual.Circle(win, radius=0.15, fillColor='red', lineColor='black', pos=(0, 0))
        red_circle.draw()
    win.flip()
    core.wait(1.5)  # Show for 1.5 seconds
    
    # Show blue circle (for encoding - last shape in sequential presentation)
    show_fixation(0.5)
    blue_circle_encoding = load_image_stimulus(blue_circle_path)
    # Use default size from load_image_stimulus (0.3, 0.3) and position (0, 0) to match regular task
    if hasattr(blue_circle_encoding, 'draw'):
        blue_circle_encoding.draw()
    else:
        blue_circle_encoding = visual.Circle(win, radius=0.15, fillColor='blue', lineColor='black', pos=(0, 0))
        blue_circle_encoding.draw()
    win.flip()
    core.wait(1.5)  # Show for 1.5 seconds
    
    
    # Don't set position/size - use defaults from load_image_stimulus (0, 0) and (0.3, 0.3) to match regular task
    
    # Transition screen before recognition phase starts
    transition_text = visual.TextStim(
        win,
        text="Now let's see how well you recall the shapes you've seen!",
        color='black',
        height=0.06*0.75*1.35,
        pos=(0, 0),
        wrapWidth=1.2
    )
    transition_text.draw()
    win.flip()
    core.wait(2.0)  # Show for 2 seconds
    
    # Trial 1: Participant only rates (green circle - it's OLD since we just showed it)
    # Show green circle again for Trial 1 (like a study phase presentation)
    show_fixation(0.5)
    green_circle = load_image_stimulus(green_circle_path)  # Reload to ensure it renders
    # Don't set position/size - use defaults (0, 0) and (0.3, 0.3) to match regular task
    if hasattr(green_circle, 'draw'):
        green_circle.draw()
    else:
        green_circle = visual.Circle(win, radius=0.15, fillColor='green', lineColor='black', pos=(0, 0))
        green_circle.draw()
    win.flip()
    core.wait(1.5)  # Show for 1.5 seconds to match sequential presentation timing
    participant_value_t1, participant_rt_t1, participant_commit_time_t1, participant_slider_timeout_t1, participant_slider_stop_time_t1, participant_slider_decision_onset_time_t1, participant_slider_click_times_t1 = get_slider_response(
        "CLICK ONCE on the sliding bar to show how confident you are you've seen this before (i.e., it is \"old\"). "
        "How close you are to either side indicates how CONFIDENT you are in your answer.",
        image_stim=green_circle, trial_num=None, max_trials=3, timeout=999999.0  # No timeout in practice, no trial number display
    )
    
    # Show outcome for trial 1
    correct_answer_t1 = 0.0  # OLD (we just showed it)
    final_answer_t1 = participant_value_t1
    euclidean_distance_t1 = abs(final_answer_t1 - correct_answer_t1)
    correctness_points_t1 = max(0.0, 1.0 - euclidean_distance_t1)
    participant_accuracy_t1 = euclidean_distance_t1 < 0.5
    
    outcome_text_t1 = "Correct" if participant_accuracy_t1 else "Incorrect"
    color_t1 = 'green' if participant_accuracy_t1 else 'red'
    # Skip in-house curator message in practice - just show correctness
    outcome_stim_t1 = visual.TextStim(win, text=outcome_text_t1, 
                                      color=color_t1, height=0.06*0.75*1.35, pos=(0, 0), wrapWidth=1.2)
    outcome_stim_t1.draw()
    win.flip()
    core.wait(1.5)  # Brief display for practice
    practice_points += correctness_points_t1
    
    # Record trial 1 data - include all fields to match regular trial structure
    image_onset_t1 = time.time()  # Approximate onset time
    trial_data_t1 = {
        'block': 0,
        'trial': 1,
        'phase': 'recognition',
        'trial_type': 'studied',
        'is_studied': True,
        'image_path': green_circle_path,
        'image_onset': image_onset_t1,
        'participant_first': True,
        'participant_slider_value': participant_value_t1,
        'participant_rt': participant_rt_t1,
        'participant_commit_time': participant_commit_time_t1,
        'participant_slider_timeout': participant_slider_timeout_t1,
        'participant_slider_stop_time': participant_slider_stop_time_t1,
        'participant_slider_decision_onset_time': participant_slider_decision_onset_time_t1,
        'participant_slider_click_times': participant_slider_click_times_t1,
        'ai_slider_value': np.nan,
        'ai_rt': np.nan,
        'ai_decision_time': np.nan,
        'ai_slider_display_time': np.nan,
        'ai_final_slider_display_time': np.nan,
        'ai_correct': np.nan,
        'ai_reliability': 0.5,  # Practice block uses 50% reliability
        'switch_stay_decision': np.nan,
        'switch_rt': np.nan,
        'switch_commit_time': np.nan,
        'switch_timeout': np.nan,
        'decision_onset_time': np.nan,
        'final_answer': final_answer_t1,
        'used_ai_answer': False,
        'ground_truth': correct_answer_t1,
        'participant_accuracy': participant_accuracy_t1,
        'euclidean_participant_to_truth': abs(participant_value_t1 - correct_answer_t1),
        'euclidean_ai_to_truth': np.nan,
        'euclidean_participant_to_ai': np.nan,
        'outcome_time': np.nan,
        'points_earned': correctness_points_t1,
        'block_start_time': np.nan,
        'block_end_time': np.nan,
        'block_duration_seconds': np.nan,
        'block_duration_minutes': np.nan
    }
    practice_trials.append(trial_data_t1)
    
    # Show red circle
    show_fixation(0.5)
    red_circle = load_image_stimulus(red_circle_path)  # Reload to ensure it renders
    # Don't set position/size - use defaults (0, 0) and (0.3, 0.3) to match regular task
    if hasattr(red_circle, 'draw'):
        red_circle.draw()
    else:
        red_circle = visual.Circle(win, radius=0.15, fillColor='red', lineColor='black', pos=(0, 0))
        red_circle.draw()
    win.flip()
    core.wait(1.0)
    
    # Trial 2: Show message first, then AI rates (all the way OLD), then participant rates
    # Show message that partner is confident (Carly in practice)
    partner_message = visual.TextStim(win, text="Carly is confident she's seen this before!", 
                                      color='blue', height=0.04*0.75*1.35, pos=(0, 0.4))
    # Show message with red circle (use default positioning - no manual pos/size)
    partner_message.draw()
    red_circle.draw()
    win.flip()
    core.wait(1.5)
    
    # Don't set position/size - use defaults from load_image_stimulus (0, 0) and (0.3, 0.3) to match regular task
    
    # AI rates first (all the way OLD)
    ai_collaborator = AICollaborator(accuracy_rate=0.5, num_trials=3)  # Practice block has 3 trials
    ai_confidence_t2 = 0.0  # All the way OLD
    ai_rt_t2 = 2.0  # Fixed RT for practice
    ai_correct_t2 = True  # It's OLD (we're showing it)
    ground_truth_t2 = 0.0
    
    # Show AI rating (Carly in practice)
    try:
        ai_slider_display_time_t2, ai_final_slider_display_time_t2 = show_animated_partner_slider(ai_confidence_t2, ai_rt_t2, image_stim=red_circle, partner_name="Carly")
    except Exception as e:
        print(f"Warning: Error in show_animated_partner_slider: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Continue anyway - just skip the animation
        ai_slider_display_time_t2 = time.time()
        ai_final_slider_display_time_t2 = time.time()
    
    # Participant rates
    participant_value_t2, participant_rt_t2, participant_commit_time_t2, participant_slider_timeout_t2, participant_slider_stop_time_t2, participant_slider_decision_onset_time_t2, participant_slider_click_times_t2 = get_slider_response(
        "Rate your memory: OLD or NEW?",
        image_stim=red_circle, trial_num=None, max_trials=3, timeout=999999.0  # No timeout in practice, no trial number display
    )
    
    # Show outcome for trial 2
    correct_answer_t2 = 0.0  # OLD
    final_answer_t2 = participant_value_t2
    euclidean_distance_t2 = abs(final_answer_t2 - correct_answer_t2)
    correctness_points_t2 = max(0.0, 1.0 - euclidean_distance_t2)
    participant_accuracy_t2 = euclidean_distance_t2 < 0.5
    
    outcome_text_t2 = "Correct" if participant_accuracy_t2 else "Incorrect"
    color_t2 = 'green' if participant_accuracy_t2 else 'red'
    # Skip in-house curator message in practice - just show correctness
    outcome_stim_t2 = visual.TextStim(win, text=outcome_text_t2, 
                                      color=color_t2, height=0.06*0.75*1.35, pos=(0, 0), wrapWidth=1.2)
    outcome_stim_t2.draw()
    win.flip()
    core.wait(1.5)  # Brief display for practice
    practice_points += correctness_points_t2
    
    # Record trial 2 data - include all fields to match regular trial structure
    image_onset_t2 = time.time()  # Approximate onset time
    ai_decision_time_t2 = time.time()  # Approximate AI decision time
    trial_data_t2 = {
        'block': 0,
        'trial': 2,
        'phase': 'recognition',
        'trial_type': 'studied',
        'is_studied': True,
        'image_path': red_circle_path,
        'image_onset': image_onset_t2,
        'participant_first': True,
        'participant_slider_value': participant_value_t2,
        'participant_rt': participant_rt_t2,
        'participant_commit_time': participant_commit_time_t2,
        'participant_slider_timeout': participant_slider_timeout_t2,
        'participant_slider_stop_time': participant_slider_stop_time_t2,
        'participant_slider_decision_onset_time': participant_slider_decision_onset_time_t2,
        'participant_slider_click_times': participant_slider_click_times_t2,
        'ai_slider_value': ai_confidence_t2,
        'ai_rt': ai_rt_t2,
        'ai_decision_time': ai_decision_time_t2,
        'ai_slider_display_time': ai_slider_display_time_t2,
        'ai_final_slider_display_time': ai_final_slider_display_time_t2,
        'ai_correct': ai_correct_t2,
        'ai_reliability': 0.5,  # Practice block uses 50% reliability
        'switch_stay_decision': np.nan,
        'switch_rt': np.nan,
        'switch_commit_time': np.nan,
        'switch_timeout': np.nan,
        'decision_onset_time': np.nan,
        'final_answer': final_answer_t2,
        'used_ai_answer': False,
        'ground_truth': correct_answer_t2,
        'participant_accuracy': participant_accuracy_t2,
        'euclidean_participant_to_truth': abs(participant_value_t2 - correct_answer_t2),
        'euclidean_ai_to_truth': abs(ai_confidence_t2 - correct_answer_t2),
        'euclidean_participant_to_ai': abs(participant_value_t2 - ai_confidence_t2),
        'outcome_time': np.nan,
        'points_earned': correctness_points_t2,
        'block_start_time': np.nan,
        'block_end_time': np.nan,
        'block_duration_seconds': np.nan,
        'block_duration_minutes': np.nan
    }
    practice_trials.append(trial_data_t2)
    
    # Show message: "now, work with your partner." (Carly in practice)
    work_with_partner_text = visual.TextStim(win, text="Now, work with Carly.", 
                                            color='black', height=0.06*0.75*1.35, pos=(0, 0.2))
    work_with_partner_text.draw()
    win.flip()
    core.wait(2.0)
    
    # Show blue square (it's NEW - not seen before, different from blue circle in encoding)
    show_fixation(0.5)
    blue_square = load_image_stimulus(blue_square_path)  # Reload to ensure it renders
    # Use default position and size (same as regular task) - no manual positioning
    # Default from load_image_stimulus is (0, 0) position and (0.3, 0.3) size
    if hasattr(blue_square, 'draw'):
        blue_square.draw()
    else:
        blue_square = visual.Rect(win, width=0.3, height=0.3*1.35, fillColor='blue', lineColor='black', pos=(0, 0))
        blue_square.draw()
    win.flip()
    safe_wait(1.0)
    
    # Trial 3: Full trial with participant, AI, switch/stay
    # Don't set position/size - use defaults from load_image_stimulus (0, 0) and (0.3, 0.3)
    participant_value_t3, participant_rt_t3, participant_commit_time_t3, participant_slider_timeout_t3, participant_slider_stop_time_t3, participant_slider_decision_onset_time_t3, participant_slider_click_times_t3 = get_slider_response(
        "Rate your memory: OLD or NEW?", image_stim=blue_square, trial_num=None, max_trials=3, timeout=999999.0  # No timeout in practice, no trial number display
    )
    
    # AI rates (selects OLD but not very confident - euclidean distance of 0.4 from left) - it's actually NEW (square), so AI is Incorrect (Carly in practice)
    ai_confidence_t3 = 0.4  # Selects OLD (closer to 0.0) but not very confident - euclidean distance of 0.4 from left (0.0)
    ai_rt_t3 = 2.0
    ai_correct_t3 = False  # It's actually NEW (square), but Carly rates it as OLD (0.4), so AI is Incorrect
    ground_truth_t3 = 1.0  # NEW
    try:
        ai_slider_display_time_t3, ai_final_slider_display_time_t3 = show_animated_partner_slider(ai_confidence_t3, ai_rt_t3, image_stim=blue_square, partner_name="Carly")
    except Exception as e:
        print(f"Warning: Error in show_animated_partner_slider: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Continue anyway - just skip the animation
        ai_slider_display_time_t3 = time.time()
        ai_final_slider_display_time_t3 = time.time()
    
    # Go straight to switch/stay screen (question + image + scores + buttons all at once)
    # Switch/Stay decision (Carly in practice)
    switch_decision_t3, switch_rt_t3, switch_commit_time_t3, switch_timeout_t3, decision_onset_time_t3 = get_switch_stay_decision(
        image_stim=blue_square, participant_value=participant_value_t3, partner_value=ai_confidence_t3, timeout=999999.0, partner_name="Carly"  # No timeout in practice
    )
    
    # Determine final answer
    if switch_decision_t3 == "switch":
        final_answer_t3 = ai_confidence_t3
        used_ai_answer_t3 = True
    else:
        final_answer_t3 = participant_value_t3
        used_ai_answer_t3 = False
    
    # Calculate accuracy and points
    correct_answer_t3 = 1.0  # NEW (it's a square, not seen before)
    euclidean_distance_t3 = abs(final_answer_t3 - correct_answer_t3)
    correctness_points_t3 = max(0.0, 1.0 - euclidean_distance_t3)
    participant_accuracy_t3 = euclidean_distance_t3 < 0.5
    
    # Show outcome with points for practice trial 3 (display rounded to 1 decimal place, full precision kept in logged data)
    correctness_points_rounded_t3 = round(correctness_points_t3, 1)
    if participant_accuracy_t3:
        outcome_text_t3 = f"Correct. Based off your answer and confidence, your points are {correctness_points_rounded_t3:.1f}"
    else:
        outcome_text_t3 = f"Incorrect. Based off your answer and confidence, your points are {correctness_points_rounded_t3:.1f}"
    color_t3 = 'green' if participant_accuracy_t3 else 'red'
    outcome_stim_t3 = visual.TextStim(win, text=outcome_text_t3, 
                                      color=color_t3, height=0.06*0.75*1.35, pos=(0, 0), wrapWidth=1.2)
    outcome_stim_t3.draw()
    win.flip()
    core.wait(2.0)  # Show for 2.0 seconds (same as regular trials)
    practice_points += correctness_points_t3
    
    # Record trial 3 data - include all fields to match regular trial structure
    image_onset_t3 = time.time()  # Approximate onset time
    ai_decision_time_t3 = time.time()  # Approximate AI decision time
    outcome_time_t3 = time.time()  # Outcome time
    trial_data_t3 = {
        'block': 0,
        'trial': 3,
        'phase': 'recognition',
        'trial_type': 'studied',
        'is_studied': False,  # It's actually NEW (blue square)
        'image_path': blue_square_path,
        'image_onset': image_onset_t3,
        'participant_first': True,
        'participant_slider_value': participant_value_t3,
        'participant_rt': participant_rt_t3,
        'participant_commit_time': participant_commit_time_t3,
        'participant_slider_timeout': participant_slider_timeout_t3,
        'participant_slider_stop_time': participant_slider_stop_time_t3,
        'participant_slider_decision_onset_time': participant_slider_decision_onset_time_t3,
        'participant_slider_click_times': participant_slider_click_times_t3,
        'ai_slider_value': ai_confidence_t3,
        'ai_rt': ai_rt_t3,
        'ai_decision_time': ai_decision_time_t3,
        'ai_slider_display_time': ai_slider_display_time_t3,
        'ai_final_slider_display_time': ai_final_slider_display_time_t3,
        'ai_correct': ai_correct_t3,
        'ai_reliability': 0.5,  # Practice block uses 50% reliability
        'switch_stay_decision': switch_decision_t3,
        'switch_rt': switch_rt_t3,
        'switch_commit_time': switch_commit_time_t3,
        'switch_timeout': switch_timeout_t3,
        'decision_onset_time': decision_onset_time_t3,
        'final_answer': final_answer_t3,
        'used_ai_answer': used_ai_answer_t3,
        'ground_truth': correct_answer_t3,
        'participant_accuracy': participant_accuracy_t3,
        'euclidean_participant_to_truth': abs(participant_value_t3 - correct_answer_t3),
        'euclidean_ai_to_truth': abs(ai_confidence_t3 - correct_answer_t3),
        'euclidean_participant_to_ai': abs(participant_value_t3 - ai_confidence_t3),
        'outcome_time': outcome_time_t3,
        'points_earned': correctness_points_t3,
        'block_start_time': np.nan,
        'block_end_time': np.nan,
        'block_duration_seconds': np.nan,
        'block_duration_minutes': np.nan
    }
    practice_trials.append(trial_data_t3)
    
    # Save practice data
    if participant_id:
        study_file, trial_file = save_data_incremental(
            practice_study, practice_trials, participant_id,
            study_file=study_file, trial_file=trial_file
        )
    
    show_instructions(
        "Training complete!\n\n"
        "Now we'll begin the actual work.\n\n",
        header_color='darkgreen',
        body_color='black'
    )
    
    # Rules reminder before starting the actual game - split into 3 pages for better readability
    show_instructions(
        "Task Overview:\n"
        "Remember which photos belong in each collection.\n\n"
        "Rate each image: OLD (belongs) or NEW (doesn't belong).\n"
        "Click on the slider, then SUBMIT.",
        header_color='darkred',
        body_color='black'
    )
    
    show_instructions(
        "Working with Amy:\n"
        "Amy will also rate each photo. You can STAY with your answer or SWITCH to hers.\n\n"
        "You can switch even if you both agree, to match her confidence level.",
        header_color='darkred',
        body_color='black'
    )

    show_instructions(
        "Scoring:\n"
        "Confidence matters. An in-house curator scores based on accuracy and confidence.\n\n"
        "10 collections, 10 images each. Time limit per decision.",
        header_color='darkred',
        body_color='black'
    )

    # Show Amy's introduction before the first collection
    amy_intro_text = visual.TextStim(
        win,
        text="Work with Amy to sort this collection.\n\n"
             "Sometimes she goes first, sometimes you do.",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
        pos=(0, 0.2),  # Adjusted position for better spacing
        wrapWidth=1.2
    )
    
    # Load and display Amy's picture (maintain aspect ratio)
    amy_path = os.path.join(STIMULI_DIR, "Amy.png")
    if os.path.exists(amy_path):
        amy_intro_image = load_image_stimulus(amy_path, maintain_aspect_ratio=True)
        if hasattr(amy_intro_image, 'setPos'):
            amy_intro_image.setPos((0, -0.05))  # Closer to text
        elif hasattr(amy_intro_image, 'pos'):
            amy_intro_image.pos = (0, -0.05)  # Closer to text
    else:
        amy_intro_image = None
        print(f"Warning: Amy.png not found at {amy_path}", file=sys.stderr)
    
    # Label for Amy's image (first time shown before experimental blocks) - below image
    amy_intro_label = visual.TextStim(
        win,
        text="Amy",
        color='black',
        height=0.04*0.75*1.35,
        pos=(0, -0.2)  # Below the image
    )
    
    # Create custom button for this screen (positioned bottom right to avoid icon overlap)
    continue_button_amy_intro = visual.Rect(
        win,
        width=0.3*0.75,
        height=0.1*0.75*1.35,
        fillColor='lightblue',
        lineColor='black',
        pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
    )
    continue_text_amy_intro = visual.TextStim(
        win,
        text="CONTINUE",
        color='black',
        height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
        pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
    )
    exit_btn_amy = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
    exit_text_amy = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
    
    def redraw_amy_intro():
        amy_intro_text.draw()  # Draw text first
        if amy_intro_image:
            amy_intro_image.draw()
        continue_button_amy_intro.draw()
        continue_text_amy_intro.draw()
        exit_btn_amy.draw()
        exit_text_amy.draw()
    
    # Custom wait for button with custom button position
    mouse_amy_intro = event.Mouse(win=win)
    mouse_amy_intro.setVisible(True)
    
    def draw_screen_amy_intro():
        redraw_amy_intro()
        win.flip()
    
    draw_screen_amy_intro()
    
    clicked_amy_intro = False
    
    if USE_TOUCH_SCREEN:
        # Use keyboard method (position-change detection) for touch screens
        mouserec_amy_intro = mouse_amy_intro.getPos()
        try:
            mouserec_x_amy_intro, mouserec_y_amy_intro = float(mouserec_amy_intro[0]), float(mouserec_amy_intro[1])
        except:
            mouserec_x_amy_intro, mouserec_y_amy_intro = 0.0, 0.0
        
        while not clicked_amy_intro:
            try:
                mouseloc_amy_intro = mouse_amy_intro.getPos()
                try:
                    mouseloc_x_amy_intro, mouseloc_y_amy_intro = float(mouseloc_amy_intro[0]), float(mouseloc_amy_intro[1])
                except:
                    mouseloc_x_amy_intro, mouseloc_y_amy_intro = 0.0, 0.0
                
                # Check if mouse position has changed (touch moved) - keyboard method
                if mouseloc_x_amy_intro == mouserec_x_amy_intro and mouseloc_y_amy_intro == mouserec_y_amy_intro:
                    # Position hasn't changed, just redraw
                    draw_screen_amy_intro()
                else:
                    # Position has changed - check if touch is within button using position calculation
                    button_x_amy_intro, button_y_amy_intro = 0.4, -0.3  # Updated to match button position
                    button_width_amy_intro, button_height_amy_intro = 0.3*0.75, 0.1*0.75
                    hit_margin_amy_intro_x = max(button_width_amy_intro * 0.5, 0.08)
                    hit_margin_amy_intro_y = max(button_height_amy_intro * 0.5, 0.04)
                    
                    on_exit_amy = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x_amy_intro <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                  EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y_amy_intro <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                    on_button_amy_intro = (button_x_amy_intro - button_width_amy_intro/2 - hit_margin_amy_intro_x <= mouseloc_x_amy_intro <= button_x_amy_intro + button_width_amy_intro/2 + hit_margin_amy_intro_x and
                                          button_y_amy_intro - button_height_amy_intro/2 - hit_margin_amy_intro_y <= mouseloc_y_amy_intro <= button_y_amy_intro + button_height_amy_intro/2 + hit_margin_amy_intro_y)
                    
                    if on_exit_amy:
                        core.quit()
                    elif on_button_amy_intro:
                        # Visual feedback (no color change in touch screen mode)
                        draw_screen_amy_intro()
                        core.wait(0.2)
                        clicked_amy_intro = True
                        break
                    
                    # Update recorded position
                    mouserec_amy_intro = mouse_amy_intro.getPos()
                    try:
                        mouserec_x_amy_intro, mouserec_y_amy_intro = float(mouserec_amy_intro[0]), float(mouserec_amy_intro[1])
                    except:
                        mouserec_x_amy_intro, mouserec_y_amy_intro = mouseloc_x_amy_intro, mouseloc_y_amy_intro
                
                # Redraw every frame
                draw_screen_amy_intro()
                core.wait(0.01)
            except Exception as e:
                print(f"Error in button wait: {e}", file=sys.stderr)
                core.wait(0.01)
            
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'space' in keys:
                        clicked_amy_intro = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, Exception):
                pass
    else:
        # Standard mouse click detection for non-touch screens
        prev_mouse_buttons_amy_intro = [False, False, False]
        
        while not clicked_amy_intro:
            try:
                mouse_buttons_amy_intro = mouse_amy_intro.getPressed()
                mouse_pos_amy_intro = mouse_amy_intro.getPos()
                
                try:
                    if hasattr(mouse_pos_amy_intro, '__len__') and len(mouse_pos_amy_intro) >= 2:
                        mouse_x_amy_intro, mouse_y_amy_intro = float(mouse_pos_amy_intro[0]), float(mouse_pos_amy_intro[1])
                    else:
                        mouse_x_amy_intro, mouse_y_amy_intro = 0.0, 0.0
                except (TypeError, ValueError):
                    mouse_x_amy_intro, mouse_y_amy_intro = 0.0, 0.0
                
                button_x_amy_intro, button_y_amy_intro = 0.4, -0.3  # Updated to match button position
                button_width_amy_intro, button_height_amy_intro = 0.3*0.75, 0.1*0.75
                
                on_exit_amy = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x_amy_intro <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                              EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y_amy_intro <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                on_button_amy_intro = (button_x_amy_intro - button_width_amy_intro/2 <= mouse_x_amy_intro <= button_x_amy_intro + button_width_amy_intro/2 and
                                      button_y_amy_intro - button_height_amy_intro/2 <= mouse_y_amy_intro <= button_y_amy_intro + button_height_amy_intro/2)
                
                if prev_mouse_buttons_amy_intro[0] and not mouse_buttons_amy_intro[0]:
                    if on_exit_amy:
                        core.quit()
                    elif on_button_amy_intro:
                        continue_button_amy_intro.fillColor = 'lightgreen'
                        draw_screen_amy_intro()
                        core.wait(0.2)
                        clicked_amy_intro = True
                        break
                
                prev_mouse_buttons_amy_intro = list(mouse_buttons_amy_intro)
                core.wait(0.01)
            except Exception as e:
                print(f"Error in button wait: {e}", file=sys.stderr)
                core.wait(0.01)
            
            try:
                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                if keys:
                    if 'space' in keys:
                        clicked_amy_intro = True
                        break
                    elif 'escape' in keys:
                        core.quit()
            except (AttributeError, Exception):
                pass
    
    mouse_amy_intro.setVisible(False)
    event.clearEvents()
    
    # Experimental blocks (10 blocks, 10 trials each)
    all_study_data = []
    all_trial_data = []
    total_experiment_points = 0.0  # Track total points across all experimental blocks
    
    try:
        # Block structure:
        # Blocks 1-3: Amy (Reliable 0.75)
        # Blocks 4-5: Ben (Unreliable 0.25)
        # Blocks 6-7: Amy (Reliable 0.75)
        # Blocks 8-10: Ben (Unreliable 0.25)
        # Turn order is randomized within each block: AI goes first on a random 5 out of 10 trials
        # The 5 trials where AI goes first are randomly selected for each block
        block_conditions = [
            (True, 0.75),   # Block 1: Reliable (Amy) - turn order randomized (AI first on 5 random trials)
            (True, 0.75),   # Block 2: Reliable (Amy) - turn order randomized (AI first on 5 random trials)
            (True, 0.75),   # Block 3: Reliable (Amy) - turn order randomized (AI first on 5 random trials)
            (True, 0.25),   # Block 4: Unreliable (Ben) - turn order randomized (AI first on 5 random trials)
            (True, 0.25),   # Block 5: Unreliable (Ben) - turn order randomized (AI first on 5 random trials)
            (True, 0.75),   # Block 6: Reliable (Amy) - turn order randomized (AI first on 5 random trials)
            (True, 0.75),   # Block 7: Reliable (Amy) - turn order randomized (AI first on 5 random trials)
            (True, 0.25),   # Block 8: Unreliable (Ben) - turn order randomized (AI first on 5 random trials)
            (True, 0.25),   # Block 9: Unreliable (Ben) - turn order randomized (AI first on 5 random trials)
            (True, 0.25),   # Block 10: Unreliable (Ben) - turn order randomized (AI first on 5 random trials)
        ]
        
        # Assign stimuli to blocks: each block has 1 item from each category (10 stimuli), no repeats
        stimulus_assignments = assign_stimuli_to_blocks()
        
        # Track previous block's partner to determine when to show switch messages
        previous_partner_reliable = None  # None for first block
        
        for block_num in range(1, 11):
            # Use pre-assigned stimuli for this block (ensures 2 per category, no repeats)
            selected_indices = stimulus_assignments[block_num - 1]
            # Use real stimuli paths instead of placeholders
            studied_images = [get_stimulus_path(i, is_lure=False, use_real_stimuli=True) for i in selected_indices]
            
            # Get conditions for this block
            block_start_participant_first, block_accuracy = block_conditions[block_num - 1]
            current_partner_reliable = (block_accuracy == 0.75)
            
            # Show partner switch message if partner changed
            if previous_partner_reliable is not None:
                if previous_partner_reliable and not current_partner_reliable:
                    # Switched from Amy (reliable) to Ben (unreliable)
                    # Partner intro image position: below text, above continue button (avoid overlap)
                    BEN_INTRO_IMAGE_Y = -0.2
                    # Check if this is the first switch (Block 4) or second switch (Block 8)
                    if block_num == 4:
                        # First switch to Ben - show long message
                        switch_text = visual.TextStim(
                            win,
                            text="A quick update.\n\n"
                                 "Amy has stepped away to prepare for her exhibition.\n\n"
                                 "While she's gone, you'll be working with Ben—another assistant in the studio.\n\n"
                                 "Click CONTINUE to start sorting!",
                            color='black',
                            height=0.04*0.75*1.35,
                            pos=(0, 0.25),  # Moved down for better spacing with image
                            wrapWidth=1.2
                        )
                        
                        # Load and display Ben's picture (maintain aspect ratio)
                        ben_path = os.path.join(STIMULI_DIR, "Ben.png")
                        if os.path.exists(ben_path):
                            ben_image = load_image_stimulus(ben_path, maintain_aspect_ratio=True)
                            if hasattr(ben_image, 'setPos'):
                                ben_image.setPos((0, BEN_INTRO_IMAGE_Y))
                            elif hasattr(ben_image, 'pos'):
                                ben_image.pos = (0, BEN_INTRO_IMAGE_Y)
                        else:
                            ben_image = None
                            print(f"Warning: Ben.png not found at {ben_path}", file=sys.stderr)
                        
                        ben_label = None  # No label on Ben intro screen
                        
                        # Create custom button for this screen (positioned bottom right to avoid icon overlap)
                        continue_button_ben = visual.Rect(
                            win,
                            width=0.3*0.75,
                            height=0.1*0.75*1.35,
                            fillColor='lightblue',
                            lineColor='black',
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        continue_text_ben = visual.TextStim(
                            win,
                            text="CONTINUE",
                            color='black',
                            height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        
                        def redraw_ben():
                            switch_text.draw()  # Draw text first
                            if ben_image:
                                ben_image.draw()
                            if ben_label is not None:
                                ben_label.draw()
                            continue_button_ben.draw()
                            continue_text_ben.draw()
                        
                        button_x, button_y = 0.4, -0.3  # Updated to match button position
                        continue_button = continue_button_ben
                        continue_text = continue_text_ben
                        
                    elif block_num == 8:
                        # Second switch to Ben - show short message
                        switch_text = visual.TextStim(
                            win,
                            text="Amy has to step away again! You will work with Ben again for the last collections.",
                            color='black',
                            height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
                            pos=(0, 0.25),  # Moved down for better spacing with image
                            wrapWidth=1.2
                        )
                        
                        # Load and display Ben's picture (same low position as first intro so never over text)
                        ben_path = os.path.join(STIMULI_DIR, "Ben.png")
                        if os.path.exists(ben_path):
                            ben_image = load_image_stimulus(ben_path, maintain_aspect_ratio=True)
                            if hasattr(ben_image, 'setPos'):
                                ben_image.setPos((0, BEN_INTRO_IMAGE_Y))
                            elif hasattr(ben_image, 'pos'):
                                ben_image.pos = (0, BEN_INTRO_IMAGE_Y)
                        else:
                            ben_image = None
                            print(f"Warning: Ben.png not found at {ben_path}", file=sys.stderr)
                        
                        # No label needed for second time showing Ben
                        ben_label = None
                        
                        # Create custom button for this screen (positioned bottom right to avoid icon overlap)
                        continue_button_ben_continue = visual.Rect(
                            win,
                            width=0.3*0.75,
                            height=0.1*0.75*1.35,
                            fillColor='lightblue',
                            lineColor='black',
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        continue_text_ben_continue = visual.TextStim(
                            win,
                            text="CONTINUE",
                            color='black',
                            height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        
                        def redraw_ben():
                            switch_text.draw()  # Draw text first
                            if ben_image:
                                ben_image.draw()
                            continue_button_ben_continue.draw()
                            continue_text_ben_continue.draw()
                        
                        button_x, button_y = 0.4, -0.3
                        continue_button = continue_button_ben_continue
                        continue_text = continue_text_ben_continue
                    else:
                        # Should not happen, but skip if it does
                        switch_text = None
                        ben_image = None
                        ben_label = None
                        continue_button = None
                        continue_text = None
                        button_x, button_y = 0, 0
                    
                    # Only show Ben screen if we have valid text (Block 4 or Block 8)
                    if switch_text is not None:
                        exit_btn_ben = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
                        exit_text_ben = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
                    
                        # Custom wait for button with custom button position
                        mouse = event.Mouse(win=win)
                        mouse.setVisible(True)
                        
                        def draw_screen():
                            redraw_ben()
                            exit_btn_ben.draw()
                            exit_text_ben.draw()
                            win.flip()
                        
                        draw_screen()
                        
                        clicked = False
                        
                        if USE_TOUCH_SCREEN:
                            # Use keyboard method (position-change detection) for touch screens
                            mouserec_ben = mouse.getPos()
                            try:
                                mouserec_x_ben, mouserec_y_ben = float(mouserec_ben[0]), float(mouserec_ben[1])
                            except:
                                mouserec_x_ben, mouserec_y_ben = 0.0, 0.0
                            
                            while not clicked:
                                try:
                                    mouseloc_ben = mouse.getPos()
                                    try:
                                        mouseloc_x_ben, mouseloc_y_ben = float(mouseloc_ben[0]), float(mouseloc_ben[1])
                                    except:
                                        mouseloc_x_ben, mouseloc_y_ben = 0.0, 0.0
                                    
                                    # Check if mouse position has changed (touch moved) - keyboard method
                                    if mouseloc_x_ben == mouserec_x_ben and mouseloc_y_ben == mouserec_y_ben:
                                        # Position hasn't changed, just redraw
                                        draw_screen()
                                    else:
                                        # Position has changed - check if touch is within button using position calculation
                                        button_width, button_height = 0.3*0.75, 0.1*0.75
                                        hit_margin_x = max(button_width * 0.5, 0.08)
                                        hit_margin_y = max(button_height * 0.5, 0.04)
                                        
                                        on_exit_ben = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x_ben <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                                      EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y_ben <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                                        on_button = (button_x - button_width/2 - hit_margin_x <= mouseloc_x_ben <= button_x + button_width/2 + hit_margin_x and
                                                    button_y - button_height/2 - hit_margin_y <= mouseloc_y_ben <= button_y + button_height/2 + hit_margin_y)
                                        
                                        if on_exit_ben:
                                            core.quit()
                                        elif on_button:
                                            # Visual feedback (no color change in touch screen mode)
                                            draw_screen()
                                            core.wait(0.2)
                                            clicked = True
                                            break
                                        
                                        # Update recorded position
                                        mouserec_ben = mouse.getPos()
                                        try:
                                            mouserec_x_ben, mouserec_y_ben = float(mouserec_ben[0]), float(mouserec_ben[1])
                                        except:
                                            mouserec_x_ben, mouserec_y_ben = mouseloc_x_ben, mouseloc_y_ben
                                    
                                    # Redraw every frame
                                    draw_screen()
                                except (AttributeError, Exception):
                                    pass
                                
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
                        else:
                            # Standard mouse click detection for non-touch screens
                            prev_mouse_buttons = [False, False, False]
                            
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
                                    
                                    button_width, button_height = 0.3*0.75, 0.1*0.75
                                    
                                    on_exit_ben = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                                  EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                                    on_button = (button_x - button_width/2 <= mouse_x <= button_x + button_width/2 and
                                                button_y - button_height/2 <= mouse_y <= button_y + button_height/2)
                                    
                                    if prev_mouse_buttons[0] and not mouse_buttons[0]:
                                        if on_exit_ben:
                                            core.quit()
                                        elif on_button:
                                            continue_button.fillColor = 'lightgreen'
                                            draw_screen()
                                            core.wait(0.2)
                                            clicked = True
                                            break
                                    
                                    if on_button:
                                        continue_button.fillColor = 'lightcyan'
                                    else:
                                        continue_button.fillColor = 'lightblue'
                                    draw_screen()
                                    
                                    prev_mouse_buttons = mouse_buttons.copy() if hasattr(mouse_buttons, 'copy') else list(mouse_buttons)
                                except (AttributeError, Exception):
                                    pass
                                
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
                    
                elif not previous_partner_reliable and current_partner_reliable:
                    # Switched from Ben (unreliable) to Amy (reliable)
                    # Check if this is Block 6 (switching back to Amy)
                    if block_num == 6:
                        switch_text = visual.TextStim(
                            win,
                            text="Amy is back for a day!\n\n"
                                 "She's returning to help you with exhibition preparation.\n\n",
                            color='black',
                            height=0.04*0.75*1.35,  # Reduced to ensure buttons are visually larger
                            pos=(0, 0.25),  # Moved down for better spacing with image
                            wrapWidth=1.2
                        )
                        
                        # Load and display Amy's picture (maintain aspect ratio)
                        amy_path = os.path.join(STIMULI_DIR, "Amy.png")
                        if os.path.exists(amy_path):
                            amy_image = load_image_stimulus(amy_path, maintain_aspect_ratio=True)
                            if hasattr(amy_image, 'setPos'):
                                amy_image.setPos((0, -0.1))  # Below text
                            elif hasattr(amy_image, 'pos'):
                                amy_image.pos = (0, -0.1)  # Below text
                        else:
                            amy_image = None
                            print(f"Warning: Amy.png not found at {amy_path}", file=sys.stderr)
                        
                        # Create custom button for this screen (positioned bottom right to avoid icon overlap)
                        continue_button_amy_return = visual.Rect(
                            win,
                            width=0.3*0.75,
                            height=0.1*0.75*1.35,
                            fillColor='lightblue',
                            lineColor='black',
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        continue_text_amy_return = visual.TextStim(
                            win,
                            text="CONTINUE",
                            color='black',
                            height=0.04*0.75*1.35,  # Reduced to ensure text fits within button
                            pos=(0.4, -0.3)  # Bottom right, moved up to avoid dock
                        )
                        exit_btn_amy_return = visual.Rect(win, width=0.12, height=0.04, fillColor=[0.95, 0.85, 0.85], lineColor='darkred', pos=EXIT_BTN_POS, lineWidth=1, units='height')
                        exit_text_amy_return = visual.TextStim(win, text="Exit", color='darkred', height=0.025, pos=EXIT_BTN_POS, units='height')
                        
                        def redraw_amy():
                            switch_text.draw()  # Draw text first
                            if amy_image:
                                amy_image.draw()
                            continue_button_amy_return.draw()
                            continue_text_amy_return.draw()
                            exit_btn_amy_return.draw()
                            exit_text_amy_return.draw()
                        
                        # Custom wait for button with custom button position
                        mouse_amy_return = event.Mouse(win=win)
                        mouse_amy_return.setVisible(True)
                        
                        def draw_screen_amy_return():
                            redraw_amy()
                            win.flip()
                        
                        draw_screen_amy_return()
                        
                        clicked_amy_return = False
                        
                        if USE_TOUCH_SCREEN:
                            # Use keyboard method (position-change detection) for touch screens
                            mouserec_amy_return = mouse_amy_return.getPos()
                            try:
                                mouserec_x_amy_return, mouserec_y_amy_return = float(mouserec_amy_return[0]), float(mouserec_amy_return[1])
                            except:
                                mouserec_x_amy_return, mouserec_y_amy_return = 0.0, 0.0
                            
                            while not clicked_amy_return:
                                try:
                                    mouseloc_amy_return = mouse_amy_return.getPos()
                                    try:
                                        mouseloc_x_amy_return, mouseloc_y_amy_return = float(mouseloc_amy_return[0]), float(mouseloc_amy_return[1])
                                    except:
                                        mouseloc_x_amy_return, mouseloc_y_amy_return = 0.0, 0.0
                                    
                                    # Check if mouse position has changed (touch moved) - keyboard method
                                    if mouseloc_x_amy_return == mouserec_x_amy_return and mouseloc_y_amy_return == mouserec_y_amy_return:
                                        # Position hasn't changed, just redraw
                                        draw_screen_amy_return()
                                    else:
                                        # Position has changed - check if touch is within button using position calculation
                                        button_x_amy_return, button_y_amy_return = 0.4, -0.3  # Updated to match button position
                                        button_width_amy_return, button_height_amy_return = 0.3*0.75, 0.1*0.75
                                        hit_margin_amy_return_x = max(button_width_amy_return * 0.5, 0.08)
                                        hit_margin_amy_return_y = max(button_height_amy_return * 0.5, 0.04)
                                        
                                        on_exit_amy_return = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouseloc_x_amy_return <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                                            EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouseloc_y_amy_return <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                                        on_button_amy_return = (button_x_amy_return - button_width_amy_return/2 - hit_margin_amy_return_x <= mouseloc_x_amy_return <= button_x_amy_return + button_width_amy_return/2 + hit_margin_amy_return_x and
                                                                button_y_amy_return - button_height_amy_return/2 - hit_margin_amy_return_y <= mouseloc_y_amy_return <= button_y_amy_return + button_height_amy_return/2 + hit_margin_amy_return_y)
                                        
                                        if on_exit_amy_return:
                                            core.quit()
                                        elif on_button_amy_return:
                                            # Visual feedback (no color change in touch screen mode)
                                            draw_screen_amy_return()
                                            core.wait(0.2)
                                            clicked_amy_return = True
                                            break
                                        
                                        # Update recorded position
                                        mouserec_amy_return = mouse_amy_return.getPos()
                                        try:
                                            mouserec_x_amy_return, mouserec_y_amy_return = float(mouserec_amy_return[0]), float(mouserec_amy_return[1])
                                        except:
                                            mouserec_x_amy_return, mouserec_y_amy_return = mouseloc_x_amy_return, mouseloc_y_amy_return
                                    
                                    # Redraw every frame
                                    draw_screen_amy_return()
                                    core.wait(0.01)
                                except Exception as e:
                                    print(f"Error in button wait: {e}", file=sys.stderr)
                                    core.wait(0.01)
                            
                            try:
                                keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                                if keys:
                                    if 'space' in keys:
                                        clicked_amy_return = True
                                        break
                                    elif 'escape' in keys:
                                        core.quit()
                            except (AttributeError, Exception):
                                pass
                        else:
                            # Standard mouse click detection for non-touch screens
                            prev_mouse_buttons_amy_return = [False, False, False]
                            
                            while not clicked_amy_return:
                                try:
                                    mouse_buttons_amy_return = mouse_amy_return.getPressed()
                                    mouse_pos_amy_return = mouse_amy_return.getPos()
                                    
                                    try:
                                        if hasattr(mouse_pos_amy_return, '__len__') and len(mouse_pos_amy_return) >= 2:
                                            mouse_x_amy_return, mouse_y_amy_return = float(mouse_pos_amy_return[0]), float(mouse_pos_amy_return[1])
                                        else:
                                            mouse_x_amy_return, mouse_y_amy_return = 0.0, 0.0
                                    except (TypeError, ValueError):
                                        mouse_x_amy_return, mouse_y_amy_return = 0.0, 0.0
                                    
                                    button_x_amy_return, button_y_amy_return = 0.4, -0.3  # Updated to match button position
                                    button_width_amy_return, button_height_amy_return = 0.3*0.75, 0.1*0.75
                                    
                                    on_exit_amy_return = (EXIT_BTN_POS[0] - 0.06 - EXIT_HIT_MARGIN <= mouse_x_amy_return <= EXIT_BTN_POS[0] + 0.06 + EXIT_HIT_MARGIN and
                                                        EXIT_BTN_POS[1] - 0.02 - EXIT_HIT_MARGIN <= mouse_y_amy_return <= EXIT_BTN_POS[1] + 0.02 + EXIT_HIT_MARGIN)
                                    on_button_amy_return = (button_x_amy_return - button_width_amy_return/2 <= mouse_x_amy_return <= button_x_amy_return + button_width_amy_return/2 and
                                                            button_y_amy_return - button_height_amy_return/2 <= mouse_y_amy_return <= button_y_amy_return + button_height_amy_return/2)
                                    
                                    if prev_mouse_buttons_amy_return[0] and not mouse_buttons_amy_return[0]:
                                        if on_exit_amy_return:
                                            core.quit()
                                        elif on_button_amy_return:
                                            continue_button_amy_return.fillColor = 'lightgreen'
                                            draw_screen_amy_return()
                                            core.wait(0.2)
                                            clicked_amy_return = True
                                            break
                                    
                                    prev_mouse_buttons_amy_return = list(mouse_buttons_amy_return)
                                    core.wait(0.01)
                                except Exception as e:
                                    print(f"Error in button wait: {e}", file=sys.stderr)
                                    core.wait(0.01)
                                
                                try:
                                    keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
                                    if keys:
                                        if 'space' in keys:
                                            clicked_amy_return = True
                                            break
                                        elif 'escape' in keys:
                                            core.quit()
                                except (AttributeError, Exception):
                                    pass
                        
                        mouse_amy_return.setVisible(False)
                        event.clearEvents()
                    else:
                        switch_text = None
                    
                elif not previous_partner_reliable and not current_partner_reliable:
                    # Still Ben, but switching blocks (e.g., Block 3 to Block 4, or Block 9 to Block 10)
                    # No message needed - just continue to next block
                    switch_text = None
                elif previous_partner_reliable and current_partner_reliable:
                    # Still Amy, but switching blocks (Block 1 to Block 2, or Block 7 to Block 8)
                    # No message needed - just continue to next block
                    switch_text = None
            
            # Update previous partner for next iteration
            previous_partner_reliable = current_partner_reliable
            
            # Show "ready to start sorting?" screen before each block
            show_ready_to_start_screen(block_num, total_blocks=10)
            
            # Create AI collaborator with block-specific accuracy
            block_ai_collaborator = AICollaborator(accuracy_rate=block_accuracy, num_trials=10)  # Experimental blocks have 10 trials
            reliability = "Reliable" if block_accuracy == 0.75 else "Unreliable"
            partner_name = "Amy" if block_accuracy == 0.75 else "Ben"
            print(f"Block {block_num}: Partner {partner_name} ({reliability}, accuracy = {block_accuracy*100:.0f}%), randomized turn order (AI first on 5 random trials)")
            print(f"  Stimuli: {selected_indices}")
            
            study_data, trial_data, study_file, trial_file, block_points = run_block(
                block_num, studied_images, block_start_participant_first,
                block_ai_collaborator, STIMULI_DIR, num_trials=10,
                experiment_start_time=experiment_start_time, participant_id=participant_id,
                study_file=study_file, trial_file=trial_file
            )
            
            all_study_data.extend(study_data)
            all_trial_data.extend(trial_data)
            total_experiment_points += block_points  # Accumulate points across blocks
            
            # Data is already saved after each trial in run_block
            
            # Break between blocks
            if block_num < 10:
                show_instructions(
                    f"Great job!\n\n"
                    "Take a short break.\n\n"
                    "",
                    header_color='darkgreen',
                    body_color='black'
                )
    except Exception as e:
        print(f"Error in experimental blocks: {e}")
        import traceback
        traceback.print_exc()
        # Show error message to user
        show_instructions(
            f"An error occurred during the experiment.\n\n"
            f"Error: {str(e)}\n\n"
            "Please contact the experimenter.",
            header_color='red',
            body_color='black'
        )
        return  # Window will be closed in finally block
    
    # Record experiment end time and calculate total time
    experiment_end_time = time.time()
    total_task_time = experiment_end_time - experiment_start_time
    
    # Calculate total points (10 blocks * 10 trials = 100 max)
    max_possible_total = 10 * 10.0  # 100 max points across all blocks
    # Round to 1 decimal place for display (full precision maintained in logged data)
    total_experiment_points_rounded = round(total_experiment_points, 1)
    
    # Show cumulative points message
    cumulative_text = visual.TextStim(
        win,
        text=f"The in-house curator scored all your collections {total_experiment_points_rounded:.1f} points out of a total of {int(max_possible_total)} points!",
        color='black',
        height=0.04*0.75*1.35,
        pos=(0, 0),
        wrapWidth=1.2
    )
    
    def redraw_cumulative():
        cumulative_text.draw()
    
    wait_for_button(redraw_func=redraw_cumulative)
    
    # Show leaderboard before final message
    show_leaderboard(participant_id, total_experiment_points)
    
    # Final message with total time
    show_instructions(
        f"COLLECTION SORTING COMPLETE!\n\n"
        f"Total time: {total_task_time/60:.1f} minutes ({total_task_time:.1f} seconds)\n\n"
        "Amy thanks you for helping sort the collection!",
        header_color='darkgreen',
        body_color='black'
    )
    
    # Save total task time to a summary file
    if not is_test_participant(participant_id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = get_log_directory()
        summary_file = os.path.join(log_dir, f"recognition_summary_{participant_id}_{timestamp}.csv")
        with open(summary_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['participant_id', 'experiment_start_time', 'experiment_end_time', 'total_task_time_seconds', 'total_task_time_minutes'])
            writer.writeheader()
            writer.writerow({
                'participant_id': participant_id,
                'experiment_start_time': experiment_start_time,
                'experiment_end_time': experiment_end_time,
                'total_task_time_seconds': total_task_time,
                'total_task_time_minutes': total_task_time / 60.0
            })
        print(f"✓ Summary data saved to {summary_file}")
        print(f"  Total task time: {total_task_time/60:.2f} minutes ({total_task_time:.1f} seconds)")
    else:
        print(f"⚠ Test participant detected - skipping summary file save")
        print(f"  Total task time: {total_task_time/60:.2f} minutes ({total_task_time:.1f} seconds)")
# =========================
#  RUN EXPERIMENT
# =========================
if __name__ == "__main__":
    # Only run experiment if window was successfully created
    print(f"Checking window status before running experiment: win = {win}")
    print(f"Checking basic elements: instr={instr}, fixation={fixation}, mouse={mouse}")
    
    if win is None:
        print("="*60)
        print("ERROR: Cannot run experiment - window was not created successfully")
        print("win is None - window creation must have failed")
        print("="*60)
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
        core.quit()
        exit(1)
    
    if instr is None or fixation is None or mouse is None:
        print("="*60)
        print("ERROR: Basic visual elements were not created successfully")
        print(f"instr={instr}, fixation={fixation}, mouse={mouse}")
        print("="*60)
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
        if win is not None:
            try:
                win.close()
            except:
                pass
        core.quit()
        exit(1)
    
    print("All checks passed. Starting experiment...")
    try:
        run_experiment()
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close window exactly once in finally block
        if win is not None:
            try:
                win.close()
            except Exception:
                pass
        try:
            core.quit()
        except:
            pass

