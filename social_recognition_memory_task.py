from psychopy import visual, core, event
import os, random, time
import numpy as np
import csv
from datetime import datetime
from PIL import Image, ImageDraw
import math

# =========================
#  SETUP
# =========================
win = visual.Window(size=[1280, 720], color='white', units='height', fullscr=False)

# Force window to front on macOS
try:
    import platform
    if platform.system() == 'Darwin':  # macOS
        try:
            win.winHandle.activate()
        except:
            pass
except:
    pass

# Initial flip to ensure window is ready
win.flip()
core.wait(0.1)

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
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"IMAGE_{pair_num}.png"))
            
            # Create lure (circle)
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.ellipse([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"LURE_{pair_num}.png"))
        else:
            # Normal: circle is studied item, square is lure
            # Create studied item (circle)
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.ellipse([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"IMAGE_{pair_num}.png"))
            
            # Create lure (square)
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 180, 180], fill=color, outline='black', width=3)
            img.save(os.path.join(output_dir, f"LURE_{pair_num}.png"))
    
    print(f"✓ Generated {num_stimuli} placeholder stimuli in {output_dir}/")
    print(f"  - {num_to_swap} pairs swapped (squares=studied, circles=lures)")
    print(f"  - {num_stimuli - num_to_swap} pairs normal (circles=studied, squares=lures)")

# Generate placeholders if they don't exist
PLACEHOLDER_DIR = "PLACEHOLDERS"
# Force regeneration to ensure swap logic is applied
# Check if directory exists and has the right number of files
if not os.path.exists(PLACEHOLDER_DIR) or len([f for f in os.listdir(PLACEHOLDER_DIR) if f.endswith('.png')]) < 200:
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
    
    # If all samples are the same shape, regenerate
    if all_same_shape and first_shape is not None:
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
instr = visual.TextStim(win, text="", color='black', height=0.04, wrapWidth=1.5, pos=(0, 0))
fixation = visual.TextStim(win, text="+", color='black', height=0.08, pos=(0, 0))
feedback_txt = visual.TextStim(win, text="", color='black', height=0.05, pos=(0, 0))
mouse = event.Mouse(win=win)

# =========================
#  HELPER FUNCTIONS
# =========================
def wait_for_space(redraw_func=None):
    """Wait for space key press"""
    event.clearEvents()
    while True:
        try:
            keys = event.getKeys(keyList=['space', 'escape'])
            if 'space' in keys:
                break
            elif 'escape' in keys:
                core.quit()
        except (AttributeError, Exception) as e:
            # Handle macOS event handling errors gracefully
            if 'type' in str(e) or 'ObjCInstance' in str(e):
                # macOS-specific event error - continue waiting
                pass
            else:
                # Other errors - re-raise
                raise
        
        if redraw_func:
            try:
                redraw_func()
            except:
                pass
        
        try:
            core.wait(0.1)
        except (AttributeError, Exception) as e:
            # Handle macOS event dispatch errors gracefully
            if 'type' in str(e) or 'ObjCInstance' in str(e):
                # macOS-specific event error - use alternative wait
                import time
                time.sleep(0.1)
            else:
                raise

def show_instructions(text, header_color='darkblue', body_color='black', header_size=0.07, body_size=0.045):
    """Show instructions with formatted header and body text"""
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
    
    # Create header text stim (larger, colored)
    if header_text:
        header_stim = visual.TextStim(
            win, 
            text=header_text, 
            color=header_color, 
            height=header_size, 
            pos=(0, 0.35),
            wrapWidth=1.5
        )
    else:
        header_stim = None
    
    # Create body text stim
    body_stim = visual.TextStim(
        win, 
        text=body_text, 
        color=body_color, 
        height=body_size, 
        pos=(0, -0.05 if header_stim else 0.2),
        wrapWidth=1.5
    )
    
    def redraw():
        if header_stim:
            header_stim.draw()
        body_stim.draw()
        win.flip()
    
    redraw()
    wait_for_space(redraw_func=redraw)

def show_fixation(duration=1.0):
    fixation.draw()
    win.flip()
    core.wait(duration)

def get_participant_id():
    """Get participant ID from PsychoPy screen input"""
    input_id = ""
    id_prompt = visual.TextStim(win, text="", color='black', height=0.06, wrapWidth=1.4)
    
    display_text = f"Enter Participant ID:\n\n{input_id}_\n\nPress ENTER when done"
    id_prompt.text = display_text
    id_prompt.draw()
    win.flip()
    
    event.clearEvents()
    key_list = ['return', 'backspace', 'space'] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(48, 58)]
    
    while True:
        keys = event.getKeys(keyList=key_list, timeStamped=False)
        if keys:
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
            
            display_text = f"Enter Participant ID:\n\n{input_id}_\n\nPress ENTER when done"
            id_prompt.text = display_text
            id_prompt.draw()
            win.flip()
        core.wait(0.05)
    
    return input_id.strip() or "P001"

def load_image_stimulus(image_path):
    """Load an image stimulus"""
    if os.path.exists(image_path):
        return visual.ImageStim(win, image=image_path, size=(0.3, 0.3))
    else:
        # Fallback: colored rectangle
        return visual.Rect(win, size=(0.3, 0.3), fillColor='gray', lineColor='black')

# =========================
#  SLIDER FOR OLD-NEW RATING
# =========================
def get_slider_response(prompt_text="Rate your memory:", image_stim=None, trial_num=None, max_trials=10, timeout=7.0):
    """Get slider response from participant using click-and-drag slider with submit button"""
    # Create slider visual elements
    slider_line = visual.Line(
        win,
        start=(-0.4, -0.2),
        end=(0.4, -0.2),
        lineColor='black',
        lineWidth=3
    )
    slider_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        pos=(0, -0.2)  # Start at center
    )
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04, pos=(-0.45, -0.2))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04, pos=(0.45, -0.2))
    
    # Trial number display
    if trial_num is not None:
        trial_text = visual.TextStim(win, text=f"Trial {trial_num} of {max_trials}", color='gray', height=0.03, pos=(0, 0.4))
    
    prompt = visual.TextStim(win, text=prompt_text, color='black', height=0.05, pos=(0, 0.3))
    
    # Submit button
    submit_button = visual.Rect(
        win,
        width=0.15,
        height=0.06,
        fillColor='lightgray',
        lineColor='black',
        pos=(0, -0.35)
    )
    submit_text = visual.TextStim(win, text="SUBMIT", color='black', height=0.04, pos=(0, -0.35))
    
    mouse.setVisible(True)
    # Don't set mouse position on macOS - it causes errors
    # Mouse will start wherever it is
    try:
        mouse.setPos((0, -0.2))  # Start mouse at center
    except (AttributeError, Exception):
        # macOS compatibility - skip setPos if it fails
        pass
    
    slider_value = 0.5  # Start at center (0.5)
    start_time = time.time()
    slider_commit_time = None
    slider_stop_time = None  # Time when slider stops moving
    dragging = False
    prev_dragging = False  # Track previous dragging state
    prev_mouse_buttons = [False, False, False]
    has_moved = False  # Track if slider has been moved from center
    timed_out = False
    mouse_pos = (0, 0)  # Initialize mouse position
    mouse_buttons = [False, False, False]  # Initialize mouse buttons
    
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
                text="Time's up! A random answer was selected.",
                color='red',
                height=0.06,
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
                # Try to reset mouse
                try:
                    mouse.setPos(mouse_pos)  # Keep current position
                except:
                    pass
            except:
                pass
            # Keep using previous mouse state instead of defaulting
            core.wait(0.02)  # Slightly longer wait to let system recover
        
        # Clear events periodically to prevent queue buildup (less frequently)
        if int(elapsed * 5) % 10 == 0:  # Every 2 seconds instead of 0.5
            try:
                # Only clear non-mouse events to preserve click detection
                pass  # Don't clear events too aggressively
            except:
                pass
        
        # Check if mouse is clicking on slider handle or near slider line
        handle_distance = ((mouse_pos[0] - slider_handle.pos[0])**2 + (mouse_pos[1] - slider_handle.pos[1])**2)**0.5
        on_slider_line = abs(mouse_pos[1] - (-0.2)) < 0.05  # Within 0.05 of slider line y-position
        
        # Start dragging if clicked on handle or slider line
        if mouse_buttons[0] and not prev_mouse_buttons[0]:
            if handle_distance < 0.05 or (on_slider_line and -0.4 <= mouse_pos[0] <= 0.4):
                dragging = True
        
        if dragging and mouse_buttons[0]:
            # Constrain to slider line (x from -0.4 to 0.4)
            x_pos = max(-0.4, min(0.4, mouse_pos[0]))
            
            # Convert to slider value (0 to 1)
            slider_value = (x_pos + 0.4) / 0.8  # Map -0.4 to 0.4 -> 0 to 1
            
            # Check if moved from center (0.5)
            if abs(slider_value - 0.5) > 0.01:  # Moved at least 1% from center
                has_moved = True
            
            # Update handle position
            slider_handle.pos = (x_pos, -0.2)
        elif not mouse_buttons[0]:
            dragging = False
        
        # Track when slider stops moving (when dragging transitions from True to False)
        if prev_dragging and not dragging and slider_stop_time is None:
            slider_stop_time = time.time()
        
        prev_dragging = dragging
        
        # Check if submit button is clicked (on mouse release)
        submit_x, submit_y = submit_button.pos
        submit_width, submit_height = submit_button.width, submit_button.height
        submit_clicked = (submit_x - submit_width/2 <= mouse_pos[0] <= submit_x + submit_width/2 and
                         submit_y - submit_height/2 <= mouse_pos[1] <= submit_y + submit_height/2)
        
        # Only allow submit if slider has been moved from center
        if prev_mouse_buttons[0] and not mouse_buttons[0] and submit_clicked and has_moved:
            slider_commit_time = time.time()
            break
        
        # Update submit button color based on whether slider has moved
        if has_moved:
            submit_button.fillColor = 'lightgreen'
        else:
            submit_button.fillColor = 'lightgray'
        
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
        win.flip()
        
        # Check for escape (with error handling)
        try:
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                core.quit()
        except (AttributeError, Exception):
            # Ignore event errors, just continue
            pass
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    slider_rt = slider_commit_time - start_time if slider_commit_time else timeout
    
    return slider_value, slider_rt, slider_commit_time, timed_out, slider_stop_time

# =========================
#  AI COLLABORATOR
# =========================
class AICollaborator:
    def __init__(self, accuracy_rate=0.5):
        """
        AI collaborator for recognition memory task
        accuracy_rate: Overall accuracy (0.5 = 50%)
        """
        self.accuracy_rate = accuracy_rate
    
    def generate_rt(self):
        """Generate AI RT from log-normal distribution"""
        # Log-normal: mean around 1.5-2.5 seconds
        mu = 0.5  # Mean of underlying normal
        sigma = 0.3  # Std of underlying normal
        rt = np.random.lognormal(mu, sigma)
        return min(rt, 5.0)  # Cap at 5 seconds
    
    def generate_confidence(self, is_studied, ground_truth_correct):
        """Generate AI confidence from Gaussian distribution"""
        # If correct, higher confidence; if incorrect, lower confidence
        if ground_truth_correct:
            mean = 0.7  # Higher confidence when correct
            std = 0.15
        else:
            mean = 0.3  # Lower confidence when incorrect
            std = 0.15
        
        confidence = np.random.normal(mean, std)
        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        # If studied item, bias toward OLD; if lure, bias toward NEW
        if is_studied:
            # Bias toward OLD (lower values)
            if ground_truth_correct:
                confidence = confidence * 0.5  # OLD side
            else:
                confidence = 0.5 + (confidence * 0.5)  # NEW side (incorrect)
        else:
            # Bias toward NEW (higher values)
            if ground_truth_correct:
                confidence = 0.5 + (confidence * 0.5)  # NEW side
            else:
                confidence = confidence * 0.5  # OLD side (incorrect)
        
        return confidence
    
    def make_decision(self, is_studied, trial_type):
        """
        Make AI decision
        is_studied: True if this is a studied item, False if lure
        trial_type: "studied" or "lure"
        
        AI accuracy: roughly 50% correct on items
        """
        # Ground truth: studied items should be rated OLD, lures should be rated NEW
        if is_studied:
            ground_truth = 0.0  # OLD
        else:
            ground_truth = 1.0  # NEW
        
        # Determine if AI should be correct (50% chance for each type)
        # This ensures 50% correct on studied items AND 50% correct on lures
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
    Show study phase: images back-to-back
    NOTE: Study phase ONLY shows studied images (IMAGE_X.png), never lures
    """
    study_data = []
    
    for i, img_path in enumerate(studied_images, 1):
        show_fixation(0.5)
        
        # Load and display image
        img_stim = load_image_stimulus(img_path)
        img_stim.draw()
        win.flip()
        
        onset_time = time.time()
        core.wait(2.0)  # Show each image for 2 seconds
        
        study_data.append({
            "block": block_num,
            "phase": "study",
            "trial": i,
            "image_path": img_path,
            "onset_time": onset_time
        })
    
    show_fixation(1.0)
    return study_data

# =========================
#  RECOGNITION TRIAL
# =========================
def run_recognition_trial(trial_num, block_num, studied_image_path, is_studied, 
                         participant_first, ai_collaborator, placeholder_dir, experiment_start_time=None, max_trials=10, total_points=0.0):
    """
    Run a single recognition trial
    NOTE: Recognition phase shows BOTH studied images (IMAGE_X.png) AND lures (LURE_X.png)
    - If is_studied=True: shows IMAGE_X.png
    - If is_studied=False: shows LURE_X.png (corresponding lure)
    """
    trial_data = {}
    
    # Determine which image to show (studied or lure)
    if is_studied:
        image_path = studied_image_path  # Shows IMAGE_X.png
        trial_type = "studied"
    else:
        # Get corresponding lure - shows LURE_X.png
        img_num = os.path.basename(studied_image_path).replace('IMAGE_', '').replace('.png', '')
        image_path = os.path.join(placeholder_dir, f"LURE_{img_num}.png")
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
        participant_value, participant_rt, participant_commit_time, participant_slider_timeout, participant_slider_stop_time = get_slider_response(
            "Rate your memory: OLD or NEW?", image_stim=img_stim, trial_num=trial_num, max_trials=max_trials, timeout=7.0
        )
        
        # P2: Partner responds (show animated slider)
        ai_start_time = time.time()
        ai_confidence, ai_rt, ai_correct, ground_truth = ai_collaborator.make_decision(is_studied, trial_type)
        
        # Animate partner's slider moving and clicking submit
        ai_decision_time = time.time()
        ai_slider_display_time = show_animated_partner_slider(ai_confidence, ai_rt, image_stim=img_stim)
        
        # Show both responses
        show_both_responses(participant_value, ai_confidence, participant_first=True)
        
        # Wait a bit to see both responses
        core.wait(2.0)
        
        # Switch/Stay decision (keep image on screen, show euclidean distance)
        switch_decision, switch_rt, switch_commit_time, switch_timeout, decision_onset_time = get_switch_stay_decision(
            image_stim=img_stim, participant_value=participant_value, partner_value=ai_confidence, timeout=7.0
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
            "ai_slider_value": ai_confidence,
            "ai_rt": ai_rt,
            "ai_decision_time": ai_decision_time,
            "ai_slider_display_time": ai_slider_display_time,
            "ai_correct": ai_correct,
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
            "euclidean_participant_to_ai": abs(participant_value - ai_confidence)
        }
    else:
        # Partner responds first (show animated slider)
        ai_start_time = time.time()
        ai_confidence, ai_rt, ai_correct, ground_truth = ai_collaborator.make_decision(is_studied, trial_type)
        
        # Animate partner's slider moving and clicking submit
        ai_decision_time = time.time()
        ai_slider_display_time = show_animated_partner_slider(ai_confidence, ai_rt, image_stim=img_stim)
        
        # P1: Participant responds (image stays on screen)
        participant_value, participant_rt, participant_commit_time, participant_slider_timeout, participant_slider_stop_time = get_slider_response(
            "Rate your memory: OLD or NEW?", image_stim=img_stim, trial_num=trial_num, max_trials=max_trials, timeout=7.0
        )
        
        # Show both responses
        show_both_responses(participant_value, ai_confidence, participant_first=False)
        core.wait(2.0)
        
        # Switch/Stay decision (keep image on screen, show euclidean distance)
        switch_decision, switch_rt, switch_commit_time, switch_timeout, decision_onset_time = get_switch_stay_decision(
            image_stim=img_stim, participant_value=participant_value, partner_value=ai_confidence, timeout=7.0
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
            "ai_slider_value": ai_confidence,
            "ai_rt": ai_rt,
            "ai_decision_time": ai_decision_time,
            "ai_slider_display_time": ai_slider_display_time,
            "ai_correct": ai_correct,
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
            "euclidean_participant_to_ai": abs(participant_value - ai_confidence)
        }
    
    # Show outcome (50% social feedback if switched, regardless of correctness)
    # Bonus points are awarded 50% of the time when switching, independent of whether
    # switching made them correct or incorrect
    outcome_time = time.time()
    # Only show social feedback 50% of the time when they switch (regardless of correctness)
    if switch_decision == "switch":
        show_social = random.random() < 0.5
    else:
        show_social = False
    # Calculate points based on euclidean distance (passed to show_trial_outcome)
    points_earned, social_feedback_time = show_trial_outcome(final_answer, correct_answer, switch_decision, used_ai_answer, show_social_feedback=show_social, total_points=total_points)
    trial_data["outcome_time"] = outcome_time
    trial_data["coins_earned"] = points_earned  # Keep CSV field name for compatibility
    trial_data["social_feedback"] = show_social
    trial_data["social_feedback_time"] = social_feedback_time
    
    return trial_data, points_earned

def show_animated_partner_slider(partner_value, partner_rt, image_stim=None):
    """Animate partner's slider moving and clicking submit"""
    # Create slider visualization
    slider_line = visual.Line(
        win,
        start=(-0.4, -0.2),
        end=(0.4, -0.2),
        lineColor='black',
        lineWidth=3
    )
    partner_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        pos=(0, -0.2)  # Start at center
    )
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04, pos=(-0.45, -0.2))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04, pos=(0.45, -0.2))
    partner_text = visual.TextStim(win, text="Your partner is rating...", color='blue', height=0.05, pos=(0, 0.3))
    
    # Submit button
    submit_button = visual.Rect(
        win,
        width=0.15,
        height=0.06,
        fillColor='lightgray',
        lineColor='black',
        pos=(0, -0.35)
    )
    submit_text = visual.TextStim(win, text="SUBMIT", color='black', height=0.04, pos=(0, -0.35))
    
    # Animate slider moving from center to target position
    start_pos = 0.0  # Center
    target_x = -0.4 + (partner_value * 0.8)  # Target position
    animation_duration = partner_rt * 0.7  # Use 70% of RT for animation
    num_steps = int(animation_duration / 0.05)  # Update every 50ms
    
    slider_display_time = None
    
    for step in range(num_steps + 1):
        # Interpolate position
        progress = step / num_steps if num_steps > 0 else 1.0
        current_x = start_pos + (target_x - start_pos) * progress
        partner_handle.pos = (current_x, -0.2)
        
        # Draw everything
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
        
        core.wait(0.05)
    
    # Show handle at final position briefly
    partner_handle.pos = (target_x, -0.2)
    
    # Animate clicking submit button (highlight button)
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
        
        # Record commit time on first submit button click (when AI commits)
        if i == 0:
            slider_display_time = time.time()
        
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
    partner_text.text = f"Your partner rates: {label}"
    
    if image_stim:
        image_stim.draw()
    partner_text.draw()
    slider_line.draw()
    old_label.draw()
    new_label.draw()
    partner_handle.draw()
    win.flip()
    core.wait(0.5)
    
    return slider_display_time

def show_both_responses(participant_value, partner_value, participant_first):
    """Show both participant and partner responses with sliders"""
    # Create slider visualization for both
    slider_line = visual.Line(
        win,
        start=(-0.4, -0.1),
        end=(0.4, -0.1),
        lineColor='black',
        lineWidth=3
    )
    
    # Participant handle (green)
    p_x_pos = -0.4 + (participant_value * 0.8)
    p_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='green',
        lineColor='black',
        pos=(p_x_pos, -0.1)
    )
    
    # Partner handle (blue)
    a_x_pos = -0.4 + (partner_value * 0.8)
    a_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        pos=(a_x_pos, -0.1)
    )
    
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04, pos=(-0.45, -0.1))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04, pos=(0.45, -0.1))
    
    # Labels
    if participant_value < 0.5:
        p_label = "OLD"
    else:
        p_label = "NEW"
    
    if partner_value < 0.5:
        a_label = "OLD"
    else:
        a_label = "NEW"
    
    both_text = visual.TextStim(
        win,
        text=f"Your rating: {p_label} (green)\n\nYour partner's rating: {a_label} (blue)",
        color='black',
        height=0.05,
        pos=(0, 0.2),
        wrapWidth=1.2
    )
    
    both_text.draw()
    slider_line.draw()
    old_label.draw()
    new_label.draw()
    p_handle.draw()
    a_handle.draw()
    win.flip()

def get_switch_stay_decision(image_stim=None, participant_value=None, partner_value=None, timeout=7.0):
    """Get switch/stay decision from participant using clickable buttons"""
    # Calculate euclidean distance
    euclidean_dist = abs(participant_value - partner_value) if (participant_value is not None and partner_value is not None) else None
    
    # Create slider visualization showing both choices (like show_both_responses)
    slider_line = visual.Line(
        win,
        start=(-0.4, 0.05),
        end=(0.4, 0.05),
        lineColor='black',
        lineWidth=3
    )
    
    # Participant handle (green)
    if participant_value is not None:
        p_x_pos = -0.4 + (participant_value * 0.8)
        p_handle = visual.Circle(
            win,
            radius=0.02,
            fillColor='green',
            lineColor='black',
            pos=(p_x_pos, 0.05)
        )
    
    # Partner handle (blue)
    if partner_value is not None:
        a_x_pos = -0.4 + (partner_value * 0.8)
        a_handle = visual.Circle(
            win,
            radius=0.02,
            fillColor='blue',
            lineColor='black',
            pos=(a_x_pos, 0.05)
        )
    
    old_label = visual.TextStim(win, text='OLD', color='black', height=0.04, pos=(-0.45, 0.05))
    new_label = visual.TextStim(win, text='NEW', color='black', height=0.04, pos=(0.45, 0.05))
    
    # Labels
    if participant_value is not None:
        if participant_value < 0.5:
            p_label = "OLD"
        else:
            p_label = "NEW"
    
    if partner_value is not None:
        if partner_value < 0.5:
            a_label = "OLD"
        else:
            a_label = "NEW"
    
    # Create buttons
    stay_button = visual.Rect(
        win,
        width=0.2,
        height=0.08,
        fillColor='lightblue',
        lineColor='black',
        pos=(-0.3, -0.2)
    )
    stay_text = visual.TextStim(win, text="STAY", color='black', height=0.05, pos=(-0.3, -0.2))
    
    switch_button = visual.Rect(
        win,
        width=0.2,
        height=0.08,
        fillColor='lightcoral',
        lineColor='black',
        pos=(0.3, -0.2)
    )
    switch_text = visual.TextStim(win, text="SWITCH", color='black', height=0.05, pos=(0.3, -0.2))
    
    decision_prompt = visual.TextStim(
        win,
        text="Do you want to STAY with your answer or SWITCH to your partner's answer?",
        color='black',
        height=0.05,
        wrapWidth=1.4,
        pos=(0, 0.4)  # Higher to leave room for image
    )
    
    # Show labels for the slider
    if participant_value is not None and partner_value is not None:
        slider_labels = visual.TextStim(
            win,
            text=f"Your rating: {p_label} (green)  |  Partner's rating: {a_label} (blue)",
            color='black',
            height=0.04,
            pos=(0, 0.25),  # Below question, above slider
            wrapWidth=1.4
        )
    
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
                    height=0.06,
                    pos=(0, -0.35)  # Lower to avoid overlap with buttons
                )
                decision_prompt.draw()
                if image_stim:
                    # Position image between slider and buttons
                    image_stim.pos = (0, -0.05)
                    image_stim.size = (0.15, 0.15)
                    image_stim.draw()
                slider_line.draw()
                old_label.draw()
                new_label.draw()
                if participant_value is not None:
                    p_handle.draw()
                if partner_value is not None:
                    a_handle.draw()
                if participant_value is not None and partner_value is not None:
                    slider_labels.draw()
                timeout_alert.draw()
                win.flip()
                core.wait(1.5)
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
                # Try to reset mouse
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
        
        # Check stay button
        stay_x, stay_y = stay_button.pos
        stay_width, stay_height = stay_button.width, stay_button.height
        stay_clicked = (stay_x - stay_width/2 <= mouse_pos[0] <= stay_x + stay_width/2 and
                       stay_y - stay_height/2 <= mouse_pos[1] <= stay_y + stay_height/2)
        
        # Check switch button
        switch_x, switch_y = switch_button.pos
        switch_width, switch_height = switch_button.width, switch_button.height
        switch_clicked = (switch_x - switch_width/2 <= mouse_pos[0] <= switch_x + switch_width/2 and
                         switch_y - switch_height/2 <= mouse_pos[1] <= switch_y + switch_height/2)
        
        # Check for mouse button release on buttons
        if prev_mouse_buttons[0] and not mouse_buttons[0]:
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
        
        # Highlight buttons on hover
        if stay_clicked:
            stay_button.fillColor = 'lightgreen'
        else:
            stay_button.fillColor = 'lightblue'
        
        if switch_clicked:
            switch_button.fillColor = 'lightgreen'
        else:
            switch_button.fillColor = 'lightcoral'
        
        prev_mouse_buttons = mouse_buttons.copy()
        
        # Draw everything
        decision_prompt.draw()
        if image_stim:
            # Position image between slider and buttons (centered horizontally)
            image_stim.pos = (0, -0.05)  # Between slider (y=0.05) and buttons (y=-0.2)
            image_stim.size = (0.15, 0.15)  # Keep size reasonable
            image_stim.draw()
        
        # Draw slider visualization
        slider_line.draw()
        old_label.draw()
        new_label.draw()
        if participant_value is not None:
            p_handle.draw()
        if partner_value is not None:
            a_handle.draw()
        if participant_value is not None and partner_value is not None:
            slider_labels.draw()
        
        stay_button.draw()
        stay_text.draw()
        switch_button.draw()
        switch_text.draw()
        win.flip()
        
        # Record decision onset time on first draw (when screen appears with all info)
        if first_draw:
            decision_onset_time = time.time()
            start_time = time.time()  # Start timing from when screen appears
            first_draw = False
        
        # Check for escape (with error handling)
        try:
            keys = event.getKeys(keyList=['escape'])
            if 'escape' in keys:
                core.quit()
        except (AttributeError, Exception):
            # Ignore event errors, just continue
            pass
        
        core.wait(0.01)
    
    mouse.setVisible(False)
    return decision, decision_rt, decision_commit_time, timed_out, decision_onset_time

def show_block_summary(block_num, total_points, max_points):
    """Show block summary with total points earned over max possible"""
    summary_text = visual.TextStim(
        win,
        text=f"Block {block_num} Complete!\n\n"
             f"Total points: {total_points:.2f} / {max_points:.2f}\n\n"
             "Press SPACE to continue.",
        color='black',
        height=0.05,
        pos=(0, 0),
        wrapWidth=1.2
    )
    
    def redraw():
        summary_text.draw()
        win.flip()
    
    redraw()
    wait_for_space(redraw_func=redraw)

def ask_block_questions(block_num, participant_id, questions_file=None, timeout=7.0):
    """Ask two questions at the end of each block:
    1. Multiple choice: What were you trying to maximize?
    2. Slider: How much did you trust the AI?
    Returns the responses and saves to CSV.
    """
    mouse = event.Mouse(win=win)
    mouse.setVisible(True)
    
    # Question 1: Multiple choice
    question1_text = visual.TextStim(
        win,
        text="What were you trying to maximize?",
        color='black',
        height=0.06,
        pos=(0, 0.3),
        wrapWidth=1.4
    )
    
    options = ["Correctness", "Bonus points", "Both", "Other"]
    option_buttons = []
    option_y_positions = [0.1, -0.05, -0.2, -0.35]
    
    for i, (opt_text, y_pos) in enumerate(zip(options, option_y_positions)):
        button = visual.Rect(
            win,
            width=0.4,
            height=0.08,
            pos=(0, y_pos),
            fillColor='lightgray',
            lineColor='black',
            lineWidth=2
        )
        text = visual.TextStim(
            win,
            text=opt_text,
            color='black',
            height=0.04,
            pos=(0, y_pos)
        )
        option_buttons.append((button, text, opt_text))
    
    selected_option = None
    start_time = time.time()
    q1_elapsed = None
    
    def redraw_q1():
        question1_text.draw()
        for button, text, _ in option_buttons:
            button.draw()
            text.draw()
        win.flip()
    
    redraw_q1()
    
    while selected_option is None:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            # Timeout - select random option
            selected_option = random.choice(options)
            q1_elapsed = elapsed
            break
        
        try:
            mouse_pos = mouse.getPos()
            mouse_buttons = mouse.getPressed()
            
            if mouse_buttons[0]:  # Left click
                for button, text, opt_text in option_buttons:
                    button_pos = button.pos
                    button_size = button.size
                    if (abs(mouse_pos[0] - button_pos[0]) < button_size[0]/2 and
                        abs(mouse_pos[1] - button_pos[1]) < button_size[1]/2):
                        selected_option = opt_text
                        q1_elapsed = elapsed
                        # Visual feedback
                        button.fillColor = 'green'
                        redraw_q1()
                        core.wait(0.3)
                        break
        except:
            pass
        
        redraw_q1()
        core.wait(0.01)
    
    # Brief pause between questions
    core.wait(0.5)
    
    # Question 2: Slider for trust
    question2_text = visual.TextStim(
        win,
        text="How much did you trust your partner?",
        color='black',
        height=0.06,
        pos=(0, 0.3),
        wrapWidth=1.4
    )
    
    slider_line = visual.Line(
        win,
        start=(-0.4, 0),
        end=(0.4, 0),
        lineColor='black',
        lineWidth=3
    )
    
    slider_handle = visual.Circle(
        win,
        radius=0.02,
        fillColor='blue',
        lineColor='black',
        lineWidth=2,
        pos=(0, 0)  # Start at center
    )
    
    left_label = visual.TextStim(
        win,
        text="Not at all",
        color='black',
        height=0.04,
        pos=(-0.4, -0.1)
    )
    
    right_label = visual.TextStim(
        win,
        text="Completely",
        color='black',
        height=0.04,
        pos=(0.4, -0.1)
    )
    
    trust_value = 0.5  # Start at center (0.5)
    slider_dragging = False
    start_time = time.time()
    trust_response_time = None
    
    def redraw_q2():
        question2_text.draw()
        slider_line.draw()
        slider_handle.pos = (-0.4 + trust_value * 0.8, 0)
        slider_handle.draw()
        left_label.draw()
        right_label.draw()
        win.flip()
    
    redraw_q2()
    
    while trust_response_time is None:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            # Timeout - use current value
            trust_response_time = elapsed
            break
        
        try:
            mouse_pos = mouse.getPos()
            mouse_buttons = mouse.getPressed()
            
            if mouse_buttons[0]:  # Mouse button pressed
                # Check if clicking on slider
                handle_x = -0.4 + trust_value * 0.8
                if abs(mouse_pos[0] - handle_x) < 0.1 and abs(mouse_pos[1]) < 0.05:
                    slider_dragging = True
                
                if slider_dragging:
                    # Update slider value based on mouse X position
                    new_value = (mouse_pos[0] + 0.4) / 0.8
                    trust_value = max(0.0, min(1.0, new_value))
            else:
                if slider_dragging:
                    # Mouse released - record response time
                    trust_response_time = time.time() - start_time
                slider_dragging = False
        except:
            pass
        
        redraw_q2()
        core.wait(0.01)
    
    # Save to CSV
    if questions_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        questions_file = f"recognition_questions_{participant_id}_{timestamp}.csv"
    
    file_exists = os.path.exists(questions_file)
    question_data = {
        "participant_id": participant_id,
        "block": block_num,
        "maximize_goal": selected_option,
        "trust_rating": trust_value,
        "trust_rt": trust_response_time if trust_response_time else timeout,
        "question1_timeout": q1_elapsed >= timeout if q1_elapsed else False,
        "question2_timeout": trust_response_time is None or (trust_response_time >= timeout)
    }
    
    with open(questions_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=question_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(question_data)
        f.flush()
    
    print(f"✓ Block {block_num} questions saved")
    
    return question_data, questions_file

def show_leaderboard(participant_id, total_points):
    """Show a fake leaderboard with participant ranked 1-5 out of 10"""
    # Generate fake participant names (P01-P10, excluding current participant)
    all_participants = [f"P{i:02d}" for i in range(1, 11)]
    current_participant_label = participant_id if len(participant_id) <= 10 else participant_id[:10]
    
    # Generate fake scores (higher scores for top ranks)
    # Participant gets rank 1-5 (randomly determined, but ensure they're in top 5)
    participant_rank = random.randint(1, 5)
    
    # Generate scores: top 5 get higher scores, bottom 5 get lower scores
    top_scores = sorted([total_points + random.uniform(-2, 5) for _ in range(4)], reverse=True)
    bottom_scores = sorted([total_points - random.uniform(5, 15) for _ in range(5)], reverse=True)
    
    # Combine scores and insert participant at their rank
    all_scores = top_scores[:participant_rank-1] + [total_points] + top_scores[participant_rank-1:] + bottom_scores
    all_scores = sorted(all_scores, reverse=True)
    
    # Create leaderboard entries
    leaderboard_entries = []
    used_names = set()
    for i, score in enumerate(all_scores[:10], 1):
        if i == participant_rank:
            name = f"{current_participant_label} (you)"
            used_names.add(current_participant_label)
        else:
            # Assign fake names, avoiding the current participant's label
            available_names = [p for p in all_participants if p not in used_names and p != current_participant_label]
            if available_names:
                name = available_names[0]
                used_names.add(name)
            else:
                name = f"P{i:02d}"
        leaderboard_entries.append((i, name, score))
    
    # Display leaderboard
    leaderboard_text = "LEADERBOARD\n\n"
    leaderboard_text += f"{'Rank':<6} {'Participant':<20} {'Score':<10}\n"
    leaderboard_text += "-" * 40 + "\n"
    
    for rank, name, score in leaderboard_entries:
        leaderboard_text += f"{rank:<6} {name:<20} {score:.2f}\n"
    
    leaderboard_stim = visual.TextStim(
        win,
        text=leaderboard_text,
        color='black',
        height=0.04,
        pos=(0, 0),
        wrapWidth=1.6,
        font='Courier New'  # Monospace font for alignment
    )
    
    def redraw():
        leaderboard_stim.draw()
        win.flip()
    
    redraw()
    wait_for_space(redraw_func=redraw)

def show_trial_outcome(final_answer, correct_answer, switch_decision, used_ai_answer, show_social_feedback=False, total_points=0):
    """Show trial outcome with points based on euclidean distance"""
    social_feedback_time = None
    
    # Calculate correctness points based on euclidean distance from correct answer
    # Points = 1 - distance, so closer answers get more points (max 1.0, min 0.0)
    euclidean_distance = abs(final_answer - correct_answer)
    correctness_points = max(0.0, 1.0 - euclidean_distance)  # Closer = more points
    
    # Round to 2 decimal places for display
    correctness_points_rounded = round(correctness_points, 2)
    
    # Determine if answer is correct (within 0.5 of correct answer)
    participant_accuracy = euclidean_distance < 0.5
    
    if participant_accuracy:
        outcome_text = "Correct!"
        color = 'green'
    else:
        outcome_text = "Incorrect"
        color = 'red'
    
    # Calculate social feedback bonus (separate from correctness points)
    social_bonus = 0.5 if show_social_feedback else 0.0
    total_points_this_trial = correctness_points + social_bonus
    
    # Show outcome with points (only show points earned this trial, not total)
    outcome_text_full = f"{outcome_text}\n\nPoints earned this trial: {correctness_points_rounded:.2f}"
    outcome_stim = visual.TextStim(win, text=outcome_text_full, color=color, height=0.06, pos=(0, 0), wrapWidth=1.4)
    outcome_stim.draw()
    win.flip()
    core.wait(1.5)
    
    # Show social reinforcement 50% of the time if they switched (regardless of correctness)
    if show_social_feedback:
        reinforcement_text = visual.TextStim(
            win,
            text="Thanks for working with your partner!\n\nYou receive a 0.5 bonus point!",
            color='blue',
            height=0.06,
            pos=(0, 0),
            wrapWidth=1.2
        )
        reinforcement_text.draw()
        win.flip()
        # Record time right when the feedback screen is displayed
        social_feedback_time = time.time()
        core.wait(2.0)
    
    # Return total points (correctness + social bonus)
    return total_points_this_trial, social_feedback_time

# =========================
#  BLOCK STRUCTURE
# =========================
def run_block(block_num, studied_images, participant_first, ai_collaborator, placeholder_dir, num_trials=None, experiment_start_time=None, participant_id=None, study_file=None, trial_file=None):
    """Run a single block: study phase + recognition trials"""
    all_trial_data = []
    
    # Determine number of trials (default to number of studied images, or use num_trials if provided)
    if num_trials is None:
        num_trials = len(studied_images)
    
    # Initialize file names for incremental saving (if not provided)
    if participant_id and study_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        study_file = f"recognition_study_{participant_id}_{timestamp}.csv"
        trial_file = f"recognition_trials_{participant_id}_{timestamp}.csv"
    
    # Phase 1: Study
    study_data = run_study_phase(studied_images, block_num)
    
    # Save study data immediately after study phase
    if participant_id:
        study_file, trial_file = save_data_incremental(
            study_data, [], participant_id,
            study_file=study_file, trial_file=trial_file
        )
    
    # Transition screen: switching to recognition phase
    show_instructions(
        "STUDY PHASE COMPLETE!\n\n"
        "Now switching to the recognition phase.\n\n"
        "You will see images again and rate them with your partner.\n\n"
        "Press SPACE to continue.",
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
    # Check the actual image that will be shown (IMAGE_X.png for studied, LURE_X.png for lures)
    if last_study_image and len(trial_sequence) > 1:
        # Get the base image number from last study image
        last_study_base = os.path.basename(last_study_image).replace('IMAGE_', '').replace('.png', '')
        
        # Check first trial - get what image will actually be shown
        first_trial_img_path, first_is_studied = trial_sequence[0][1], trial_sequence[0][2]
        first_trial_base = os.path.basename(first_trial_img_path).replace('IMAGE_', '').replace('.png', '')
        
        # If first trial shows the same base image as last study (regardless of studied/lure), swap it
        if first_trial_base == last_study_base:
            # Find a different trial to swap with (one that doesn't match last study)
            for i in range(1, len(trial_sequence)):
                swap_trial_img_path = trial_sequence[i][1]
                swap_trial_base = os.path.basename(swap_trial_img_path).replace('IMAGE_', '').replace('.png', '')
                if swap_trial_base != last_study_base:
                    trial_sequence[0], trial_sequence[i] = trial_sequence[i], trial_sequence[0]
                    break
    
    # Renumber trials after shuffling
    trial_sequence = [(i+1, img_path, is_studied) for i, (_, img_path, is_studied) in enumerate(trial_sequence)]
    
    total_points = 0.0  # Track total points (correctness + social feedback)
    max_possible_points = float(num_trials)  # Max points from correctness only (1.0 per trial)
    
    for trial_num, img_path, is_studied in trial_sequence:
        trial_data, points_earned = run_recognition_trial(
            trial_num, block_num, img_path, is_studied,
            participant_first, ai_collaborator, placeholder_dir, experiment_start_time, max_trials=num_trials, total_points=total_points
        )
        all_trial_data.append(trial_data)
        total_points += points_earned  # Includes correctness + social feedback
        
        # Save data after each trial (not each block)
        if participant_id:
            # Save single trial immediately - update file references
            study_file, trial_file = save_data_incremental(
                [], [trial_data], participant_id,
                study_file=study_file, trial_file=trial_file
            )
    
    # Show block summary with points (total over max possible from correctness)
    show_block_summary(block_num, total_points, max_possible_points)
    
    # Ask block-end questions (for both practice and experimental blocks)
    if participant_id:
        # Use a consistent questions file name (create once, reuse)
        if not hasattr(run_block, 'questions_file'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_block.questions_file = f"recognition_questions_{participant_id}_{timestamp}.csv"
        ask_block_questions(block_num, participant_id, questions_file=run_block.questions_file, timeout=7.0)
    
    return study_data, all_trial_data, study_file, trial_file, total_points

# =========================
#  DATA SAVING
# =========================
def save_data_incremental(all_study_data, all_trial_data, participant_id,
                          study_file=None, trial_file=None):
    """Save data incrementally"""
    if study_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        study_file = f"recognition_study_{participant_id}_{timestamp}.csv"
        trial_file = f"recognition_trials_{participant_id}_{timestamp}.csv"
    
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
        with open(trial_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_trial_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_trial_data)
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
    except:
        pass
    
    # Initial click-to-start screen to ensure window has focus
    start_screen = visual.TextStim(
        win,
        text="Click anywhere on this screen to begin the experiment.",
        color='black',
        height=0.06,
        pos=(0, 0),
        wrapWidth=1.4
    )
    
    mouse.setVisible(True)
    mouse.setPos((0, 0))  # Reset mouse position
    
    # Draw and flip multiple times to ensure window is ready
    for _ in range(3):
        start_screen.draw()
        win.flip()
        core.wait(0.05)
    
    # Wait for mouse click anywhere on screen (more responsive)
    clicked = False
    prev_mouse_buttons = [False, False, False]
    while not clicked:
        try:
            # Check for mouse button release (more reliable than press)
            mouse_buttons = mouse.getPressed()
            # Detect click on release (button was down, now up)
            if prev_mouse_buttons[0] and not mouse_buttons[0]:
                clicked = True
                break
            # Also accept if button is currently pressed
            if mouse_buttons[0]:
                clicked = True
                break
            prev_mouse_buttons = mouse_buttons.copy()
        except (AttributeError, Exception):
            # Handle macOS event errors gracefully
            try:
                event.clearEvents()
            except:
                pass
            prev_mouse_buttons = [False, False, False]
        
        # Also check for space key as backup
        try:
            keys = event.getKeys(keyList=['space', 'escape'], timeStamped=False)
            if 'space' in keys:
                clicked = True
                break
            elif 'escape' in keys:
                core.quit()
        except:
            pass
        
        # Redraw screen periodically to keep it responsive
        start_screen.draw()
        win.flip()
        core.wait(0.02)  # Shorter wait for more responsive detection
    
    mouse.setVisible(False)
    event.clearEvents()
    
    # Small delay to ensure window is ready
    core.wait(0.5)
    
    # Record experiment start time
    experiment_start_time = time.time()
    
    participant_id = get_participant_id()
    
    # Initialize file names once for the entire experiment
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    study_file = f"recognition_study_{participant_id}_{timestamp}.csv"
    trial_file = f"recognition_trials_{participant_id}_{timestamp}.csv"
    
    # Instructions - broken into smaller chunks with formatting
    show_instructions(
        "Welcome to the Social Recognition Memory Task!\n\n"
        "In this task, you will study images and then test your memory\n"
        "by working with a partner.\n\n"
        "Press SPACE to continue.",
        header_color='darkblue',
        body_color='black'
    )
    
    show_instructions(
        "HOW IT WORKS:\n\n"
        "1. STUDY PHASE: You'll see images one at a time.\n"
        "   Try to remember them.\n\n"
        "Press SPACE to continue.",
        header_color='darkgreen',
        body_color='black'
    )
    
    show_instructions(
        "RECOGNITION PHASE:\n\n"
        "You'll see images again.\n\n"
        "Some images will be OLD (from the study phase).\n"
        "Some images will be NEW (you haven't seen them).\n\n"
        "Press SPACE to continue.",
        header_color='darkgreen',
        body_color='black'
    )
    
    show_instructions(
        "RATING WITH THE SLIDER:\n\n"
        "- You'll rate each image on a slider\n"
        "- The slider measures your CONFIDENCE level\n"
        "- Move the slider LEFT for OLD (studied)\n"
        "- Move the slider RIGHT for NEW (not studied)\n"
        "- Where you place it shows how confident you are\n"
        "- Click and drag the slider handle\n"
        "- Click the SUBMIT button when ready\n\n"
        "Press SPACE to continue.",
        header_color='purple',
        body_color='black'
    )
    
    show_instructions(
        "COLLABORATING WITH YOUR PARTNER:\n\n"
        "Your partner will also rate each image on the same slider.\n\n"
        "After you both respond, you'll see both ratings.\n\n"
        "You can decide to:\n"
        "- STAY with your original confidence rating\n"
        "- SWITCH to your partner's confidence rating\n\n"
        "Even if you both say OLD or both say NEW,\n"
        "you can still switch to match their confidence level.\n\n"
        "Press SPACE to continue.",
        header_color='darkorange',
        body_color='black'
    )
    
    # Split scoring instructions into two pages
    show_instructions(
        "SCORING:\n\n"
        "You earn points based on your confidence and accuracy.\n\n"
        "The slider shows your CONFIDENCE level.\n\n"
        "If you're confident and CORRECT:\n"
        "- You earn MORE points (up to 1.0 point)\n\n"
        "If you're confident but WRONG:\n"
        "- You LOSE more points (closer to 0.0 points)\n\n"
        "The closer your final answer is to the correct answer,\n"
        "the more points you earn!\n\n"
        "Press SPACE to continue.",
        header_color='darkgreen',
        body_color='black'
    )
    
    show_instructions(
        "BONUS POINTS & REWARDS:\n\n"
        "If you choose to work with your partner and switch your answer,\n"
        "you will get a 0.5 bonus point 50% of the time (randomly).\n\n"
        "You'll see your points after each trial.\n\n"
        "At the end of each block, you'll be asked 2 quick questions.\n\n"
        "At the end of the game, you'll see a leaderboard showing how\n"
        "you compared to other participants.\n\n"
        "Press SPACE to continue.",
        header_color='darkblue',
        body_color='black'
    )
    
    # Detailed practice instructions
    show_instructions(
        "PRACTICE BLOCK\n\n"
        "You will study 5 images, then test your memory with your partner.\n\n"
        "This is just for practice, but go as quick as you can!\n\n"
        "Press SPACE to begin practice.",
        header_color='darkred',
        body_color='black'
    )
    
    # Generate practice stimuli - ensure both circles and squares appear
    # Check actual image files to find which are circles vs squares
    # Since IMAGE_X.png files can be either circles or squares (depending on swap),
    # we need to examine them to ensure we get both types
    from PIL import Image as PILImage
    
    circle_indices = []
    square_indices = []
    
    # Check images to find circles and squares by examining pixel patterns
    for i in range(1, 101):
        img_path = os.path.join(PLACEHOLDER_DIR, f"IMAGE_{i}.png")
        if os.path.exists(img_path):
            try:
                img = PILImage.open(img_path)
                pixels = img.load()
                width, height = img.size
                
                # Check corners - squares have filled corners, circles have rounded (white) corners
                corner1 = pixels[10, 10]  # top-left corner
                corner2 = pixels[width-10, 10]  # top-right corner
                corner3 = pixels[10, height-10]  # bottom-left corner
                corner4 = pixels[width-10, height-10]  # bottom-right corner
                
                # Check center
                center = pixels[width//2, height//2]
                
                # Calculate average RGB for corners and center
                def rgb_avg(rgb):
                    if isinstance(rgb, int):  # Grayscale
                        return rgb
                    return sum(rgb[:3]) / len(rgb[:3]) if len(rgb) >= 3 else rgb
                
                corner_avg = (rgb_avg(corner1) + rgb_avg(corner2) + rgb_avg(corner3) + rgb_avg(corner4)) / 4
                center_avg = rgb_avg(center)
                
                # Squares: corners are filled (similar color to center, not white)
                # Circles: corners are white/background (very different from center)
                corner_center_diff = abs(corner_avg - center_avg)
                
                # If corners are similar to center (low difference), it's a square
                # If corners are very different from center (high difference), it's a circle
                if corner_center_diff < 100:  # Corners similar to center = square
                    if len(square_indices) < 3:  # Need 3 squares for 5 total (3+2 or 2+3)
                        square_indices.append(i)
                else:  # Corners very different = circle
                    if len(circle_indices) < 3:  # Need 3 circles for 5 total
                        circle_indices.append(i)
                
                if len(circle_indices) >= 2 and len(square_indices) >= 2 and len(circle_indices) + len(square_indices) >= 5:
                    break
            except Exception as e:
                continue
    
    # If we found both types, use them; otherwise fallback
    # Need 5 total: use 3 of one type and 2 of the other (or 2+3)
    if len(circle_indices) >= 2 and len(square_indices) >= 2:
        # Use 3 of one type and 2 of the other
        if len(circle_indices) >= 3:
            practice_indices = circle_indices[:3] + square_indices[:2]
        elif len(square_indices) >= 3:
            practice_indices = circle_indices[:2] + square_indices[:3]
        else:
            practice_indices = circle_indices[:2] + square_indices[:2] + random.sample(
                [i for i in range(1, 101) if i not in circle_indices + square_indices], 1
            )
        random.shuffle(practice_indices)
        practice_indices = practice_indices[:5]  # Ensure exactly 5
        num_circles = sum(1 for i in practice_indices if i in circle_indices)
        num_squares = 5 - num_circles
        print(f"Practice block: Using {num_circles} circles and {num_squares} squares")
    else:
        # Fallback: if we can't find enough of one type, just use what we have plus some from the other
        if len(circle_indices) > 0 and len(square_indices) > 0:
            # Use what we found, fill the rest randomly
            needed = 5 - len(circle_indices) - len(square_indices)
            remaining = [i for i in range(1, 101) if i not in circle_indices + square_indices]
            practice_indices = circle_indices + square_indices + random.sample(remaining, min(needed, len(remaining)))
            practice_indices = practice_indices[:5]
        else:
            # Last resort: use a spread
            practice_indices = [1, 25, 50, 75, 10]
        print(f"Practice block: Using fallback selection (found {len(circle_indices)} circles, {len(square_indices)} squares)")
    
    practice_images = [os.path.join(PLACEHOLDER_DIR, f"IMAGE_{i}.png") for i in practice_indices]
    ai_collaborator = AICollaborator(accuracy_rate=0.5)
    
    try:
        practice_study, practice_trials, study_file, trial_file, practice_points = run_block(
            0, practice_images, participant_first=True, 
            ai_collaborator=ai_collaborator, placeholder_dir=PLACEHOLDER_DIR, num_trials=5,
            experiment_start_time=experiment_start_time, participant_id=participant_id,
            study_file=study_file, trial_file=trial_file
        )
        
        # Practice data is already saved trial-by-trial in run_block
    except Exception as e:
        print(f"Error in practice block: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway with empty practice data
        practice_study = []
        practice_trials = []
        study_file, trial_file = save_data_incremental(
            [], [], participant_id
        )
    
    show_instructions(
        "Practice complete!\n\n"
        "Now we'll begin the experimental blocks.\n\n"
        "Press SPACE to continue.",
        header_color='darkgreen',
        body_color='black'
    )
    
    # Rules reminder before starting the actual game - split into 2 pages
    show_instructions(
        "QUICK REMINDER - KEY RULES (Part 1):\n\n"
        "1. STUDY PHASE: Remember each image carefully\n\n"
        "2. RECOGNITION PHASE:\n"
        "   - Rate your confidence on the slider\n"
        "   - LEFT = OLD (studied), RIGHT = NEW (not studied)\n"
        "   - Click and drag the slider, then click SUBMIT\n\n"
        "3. COLLABORATION:\n"
        "   - Your partner will also rate each image\n"
        "   - You can STAY with your answer or SWITCH to theirs\n"
        "   - Even if you both agree (OLD or NEW),\n"
        "     you can switch to match their confidence level\n\n"
        "Press SPACE to continue.",
        header_color='darkred',
        body_color='black'
    )
    
    show_instructions(
        "QUICK REMINDER - KEY RULES (Part 2):\n\n"
        "4. SCORING:\n"
        "   - Points based on how close your final answer is to correct\n"
        "   - More confident + correct = more points\n"
        "   - More confident + wrong = fewer points\n"
        "   - Bonus: Switch to get 0.5 bonus point (50% chance)\n\n"
        "5. QUESTIONS:\n"
        "   - At the end of each block, you'll answer 2 quick questions\n\n"
        "Press SPACE to begin the experiment.",
        header_color='darkred',
        body_color='black'
    )
    
    show_instructions(
        "EXPERIMENTAL BLOCKS:\n\n"
        "You will complete 10 blocks, each with 10 trials.\n\n"
        "Sometimes your partner will respond first,\n"
        "sometimes you will respond first.\n\n"
        "Press SPACE to begin the first block.",
        header_color='darkblue',
        body_color='black'
    )
    
    # Experimental blocks (10 blocks, 10 trials each)
    all_study_data = []
    all_trial_data = []
    total_experiment_points = 0.0  # Track total points across all experimental blocks
    
    try:
        # Counterbalance two manipulations:
        # 1. Turn-taking: Participant first (True) vs AI first (False) - 5 each
        # 2. AI Accuracy: High (0.75) vs Low (0.25) - 5 each
        # Create all 4 combinations with balanced distribution:
        # - Participant first + High accuracy: 2-3 blocks
        # - Participant first + Low accuracy: 2-3 blocks
        # - AI first + High accuracy: 2-3 blocks
        # - AI first + Low accuracy: 2-3 blocks
        
        # Create list of all 4 combinations
        block_conditions = [
            (True, 0.75),   # Participant first, High accuracy
            (True, 0.75),   # Participant first, High accuracy
            (True, 0.25),   # Participant first, Low accuracy
            (True, 0.25),   # Participant first, Low accuracy
            (True, 0.25),   # Participant first, Low accuracy
            (False, 0.75),  # AI first, High accuracy
            (False, 0.75),  # AI first, High accuracy
            (False, 0.75),  # AI first, High accuracy
            (False, 0.25),  # AI first, Low accuracy
            (False, 0.25),  # AI first, Low accuracy
        ]
        # Shuffle to randomize order
        random.shuffle(block_conditions)
        
        # Ensure each of the 100 stimuli appears exactly once across all 10 blocks
        # Shuffle all 100 stimulus indices and divide into 10 groups of 10
        all_stimulus_indices = list(range(1, 101))  # 1-100
        random.shuffle(all_stimulus_indices)
        
        # Divide into 10 blocks (each with 10 unique stimuli)
        stimulus_assignments = []
        for i in range(10):
            block_stimuli = all_stimulus_indices[i*10:(i+1)*10]
            stimulus_assignments.append(block_stimuli)
        
        for block_num in range(1, 11):
            # Use pre-assigned stimuli for this block (ensures each appears exactly once)
            selected_indices = stimulus_assignments[block_num - 1]
            studied_images = [os.path.join(PLACEHOLDER_DIR, f"IMAGE_{i}.png") for i in selected_indices]
            
            # Get counterbalanced conditions for this block
            participant_first, block_accuracy = block_conditions[block_num - 1]
            
            # Create AI collaborator with block-specific accuracy
            block_ai_collaborator = AICollaborator(accuracy_rate=block_accuracy)
            turn_order = "Participant first" if participant_first else "AI first"
            print(f"Block {block_num}: {turn_order}, AI accuracy = {block_accuracy*100:.0f}%")
            
            study_data, trial_data, study_file, trial_file, block_points = run_block(
                block_num, studied_images, participant_first,
                block_ai_collaborator, PLACEHOLDER_DIR, num_trials=10,
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
                    f"Block {block_num} complete!\n\n"
                    "Take a short break.\n\n"
                    "Press SPACE when ready for the next block.",
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
            "Please contact the experimenter.\n\n"
            "Press SPACE to exit.",
            header_color='red',
            body_color='black'
        )
        win.close()
        return
    
    # Record experiment end time and calculate total time
    experiment_end_time = time.time()
    total_task_time = experiment_end_time - experiment_start_time
    
    # Show leaderboard before final message
    show_leaderboard(participant_id, total_experiment_points)
    
    # Final message with total time
    show_instructions(
        f"EXPERIMENT COMPLETE!\n\n"
        f"Total task time: {total_task_time/60:.1f} minutes ({total_task_time:.1f} seconds)\n\n"
        "Thank you for participating!\n\n"
        "Press SPACE to exit.",
        header_color='darkgreen',
        body_color='black'
    )
    
    # Save total task time to a summary file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"recognition_summary_{participant_id}_{timestamp}.csv"
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
    
    win.close()

# =========================
#  RUN EXPERIMENT
# =========================
if __name__ == "__main__":
    try:
        run_experiment()
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user.")
        win.close()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        win.close()

