# Experimenter Script

## Quick Start Instructions

### For Running the Main Experiment:
1. Open terminal
2. Type `n` when prompted to confirm you want to run the localizer (this skips the localizer)
3. Type `experiment` if you are trying to run the experiment
4. Say `y` to:
   - Running the experiment
   - Uploading the log files (after the experiment completes)

### For Participants Running the Localizer:
1. Open terminal
2. Enter `y` when prompted

This will run the localizer and upload the log files. 

### For Pushing Log Files:
If you only want to push the log files without running anything else, you may open a new *Anaconda PowerShell Prompt Terminal* and enter "n" and enter when prompted to run the localizer. 

### Updating the repo
The code should automatically update every time you open the terminal or run the experiment. If this is not the case, reach out to kahinimehta@hotmail.com

**To exit fullscreen (main experiment):** 
- **Laptop**: Press **ESC** — ESC always works to exit.
- **Touch screen**: Tap the **Exit** button (top-right corner) — the Exit button is only shown sometimes, when you have to make a decision or click a button (e.g., input method, instructions, CONTINUE, slider/SUBMIT, STAY/SWITCH, name entry). It is not shown during fixation crosses, image display, or outcome screens. So on touch screens, you can only exit when the Exit button is visible.
- **Key difference**: Laptop users can exit any time with ESC. Touch screen users can only exit when the Exit button appears (during interactive/decision screens).
- **Localizer**: ESC and Exit work at all times, including during fixation and image presentation.

**Experimenter note**: 
- Before the task starts, tell participants: "To exit, laptop users can press ESC at any time. Touch screen users: the Exit button only appears when you need to make a decision or tap a button—it won't be visible during image display or when the screen is advancing automatically. Exit when you see the button."
- Also make sure to hit all the information in the script below to ensure participants understand the task and its purpose!
- Make sure to emphasize the leaderboard + stress the importance of collaboration so participants engage with the AI!
- Make it clear that some images are very similar to the lures (so participants don't wonder why they're incorrect on some trials in the beginning). 
- Be sure to emphasize that confidence matters so people use the sliding scale. 
- Make sure people CLICK, NOT slide as far as possible. 


---

## Full Experiment Script

### Input Method Screen (first)
**Display says:**
"What input method are you using?

Touch or click the button below:

(Press ESC or tap Exit to leave fullscreen)"

**Display shows:** Two buttons: "TOUCH SCREEN (Double tap with finger)" and "MOUSE/TRACKPAD (Click)". A small **Exit** button (top-right corner).

**What to say:**
"First, double-tap the touch-screen button."


**Exit fullscreen:** **ESC** (laptop) or tap **Exit** (top-right). Same on all screens with CONTINUE/instruction buttons.

---

### Initial Screen
**Display says:**
"Hello & welcome to the social memory game! Pay careful attention to the text on the screen. Some images will be very deceptively similar."

**Display shows:** A BEGIN button (light blue).

**What to say:**
"Welcome! You'll see a welcome message on the screen. Please read it carefully and click BEGIN when you're ready."

---

### Participant ID Screen
**Display says:**
"Enter your first name and last initial with no spaces/capitals:"
(Mouse/trackpad: "Hit Enter when done." also shown.)

**Display shows:** Text field for typing; BACKSPACE and CONTINUE buttons (touch) or type and press Enter (mouse).

**What to say:**
"Enter your first name and last initial, no spaces or capitals. When you're done, click CONTINUE."

---

### Welcome Screen 1 (Practice: Amy's Assistant Carly)
**Display says:**
"Greetings!

You've just joined Amy's photography studio. She's preparing images for an upcoming exhibition.

Carly, her assistant, will walk you through a short practice to get familiar with the task."

**Display shows:** Image of Carly (same as Amy) below the text, CONTINUE button (bottom right).

**What to say:**
"This is Carly, Amy's assistant. She'll walk you through a short practice to learn the task. The actual work will be with Amy. Click CONTINUE when you're ready."

---

### Welcome Screen 2
**Display says:**
"Before you begin the real work, you'll complete a short training round to get familiar with the process.

For now, simply memorize the shapes you're about to see. Click CONTINUE when you're ready to get started!"

**Display shows:** CONTINUE button.

**What to say:**
"You'll start with a practice round to learn how the task works. First, you'll see some shapes—just memorize them. Click CONTINUE when ready."

---

### Practice Phase - Study
**Display shows:**
- Fixation cross (+)
- Shape appears for 1.5 seconds
- This repeats for 3 shapes

---

### Transition Screen (Before Recognition Phase)
**Display says:**
"Now let's see how well you recall the shapes you've seen!"

**Display shows:** No button—this screen advances automatically after 2 seconds.

**What to say:**
"Now we'll test your memory. You'll see shapes and decide if you've seen them before or if they're new."

---

### Practice Phase - Recognition Trial 1
**Display shows:**
- Green circle
- Prompt: "CLICK ONCE on the sliding bar to show how confident you are you've seen this before (i.e., it is \"old\"). How close you are to either side indicates how CONFIDENT you are in your answer."
- Slider with OLD on left, NEW on right
- SUBMIT button

**What to say:**

***Make sure they know to CLICK, not DRAG the slider.***
"Now you'll see images one at a time. For each one, decide if you've seen it before (OLD) or if it's new (NEW). Use the slider—CLICK, not slide, anywhere on the line to set your rating, then click SUBMIT. How far you click shows how confident you are -- if you're 100% sure you've seen this, click all the way to the left. If you're 100% sure you haven't, click all the way to the right."

---

### Practice Phase - Recognition Trial 2
**Display shows:**
- Message: "Carly is confident she's seen this before!"
- Red circle appears
- Carly's slider animation (she clicks all the way OLD)
- Then participant's slider with prompt "Rate your memory: OLD or NEW?"

**What to say:**
"Carly will also rate each image. Sometimes she'll go first, sometimes you will. In this practice trial, Carly went first and rated it confidently as OLD. Now it's your turn to rate it."

---

### Practice Phase - Recognition Trial 3
**Display shows:**
- Message: "Now, work with Carly."
- Blue square
- Participant rates first (prompt: "Rate your memory: OLD or NEW?")
- Then Carly rates (she selects OLD but not very confident—slider at 0.4)
- Then decision screen appears

**What to say:**
"In this trial, you'll rate first, then Carly will rate. After you both rate, you'll see both of your choices and decide whether to STAY with your answer or SWITCH to Carly's answer."

---

### Decision Screen (Switch/Stay)
**Display shows:**
- Image
- Slider with markers (dots) showing each rating:
  - Green marker for participant's choice (labeled "you" below the scale)
  - Blue marker for partner's choice (labeled "Carly" during practice, "Amy" or "Ben" during experimental blocks)
- Text: "Do you want to STAY with your answer or SWITCH to [partner's] answer?" (Carly during practice, Amy or Ben during experimental blocks)
- STAY button (light blue)
- SWITCH button (light coral)

**What to say:**
"You can see both your rating and your partner's rating on the slider. The green marker shows your choice, and the blue marker shows your partner's choice. You can STAY with your answer or SWITCH to your partner's answer. Even if you both agree on OLD or NEW, you can still switch to match their confidence level."

---

### Outcome Screen
**Display shows:**
- **Practice trials 1–2**: Just "Correct" or "Incorrect" (green or red); advances after 1.5 seconds.
- **Practice trial 3**: "Correct. Based off your answer and confidence, your points are X" or "Incorrect. Based off your answer and confidence, your points are X"; advances after 2 seconds.
- **Experimental trials**: "Correct." or "Incorrect." followed by "The in-house curator scored this image: X points based on image & your confidence."; advances after 2 seconds.

**What to say:**
"You'll see how the curator scored your decision. The scoring takes into account both whether you were correct and how confident you were."

---

### Training Complete Screen
**Display says:**
"Training complete!

Now we'll begin the actual work."

**What to say:**
"Great! The practice is done. Now we'll start the actual task. There will be brief instructions coming up."

---

### Instructions - Task Overview
**Display says:**
"Task Overview:
Remember which photos belong in each collection.

Rate each image: OLD (belongs) or NEW (doesn't belong).
Click on the slider, then SUBMIT."

**Display shows:** CONTINUE button.

**What to say:**
"Read these instructions carefully. You'll need to remember which photos belong in each collection. Important: For each collection, you will only be sorting the 10 images you just saw for that collection—nothing from prior collections. These will be more complex images—like animals, objects, etc. Use the slider to rate each image—OLD means it belongs, NEW means it doesn't. Click on the slider line to set your rating, then click SUBMIT."

---

### Instructions - Working with Amy
**Display says:**
"Working with Amy:
Amy will also rate each photo. You can STAY with your answer or SWITCH to hers.

You can switch even if you both agree, to match her confidence level."

**Display shows:** CONTINUE button.

**What to say:**
"Amy will rate each image too. After you both rate, you can STAY with your answer or SWITCH to Amy's answer. You can switch even if you both agree, to match her confidence level."

---

### Instructions - Scoring
**Display says:**
"Scoring:
Confidence matters. An in-house curator scores based on accuracy and confidence.

10 collections, 10 images each. Time limit per decision."

**Display shows:** CONTINUE button.

**What to say:**
"The scoring system considers both accuracy and confidence. If you are confident but wrong, you lose more points than if you are not confident and wrong. If you are right but not confident, you will not get as many points as if you were both right and confident. There are 10 collections total, with 10 images in each. You'll have a time limit for each decision. Some of the image differences will be extremely, extremely subtle, so play close attention! *You will see how you compared against other anonymous players at the end via a leaderboard!*"

---

### Amy Introduction Before Collections
**Display says:**
"Work with Amy to sort this collection.

Sometimes she goes first, sometimes you do."

**Display shows:** Image of Amy, "Amy" label below the image, CONTINUE button (bottom right).

**What to say:**
"Work with Amy to sort this collection. Sometimes she'll rate first, sometimes you will. Remember that Amy *treasures collaboration in her coworkers, and likes them to work together on these images rather than independently. *Remember, you are only responsible for remembering the last 10 images you saw before sorting. You will not be asked to recall images from previous collections while sorting images. Each collection has a different set of images*. Click CONTINUE when ready to get started."

---


### Ready to Start (Before Each Block)
**Display says:**
"Ready to start sorting?

X collection(s) remaining"

**Display shows:** BEGIN button. (Number of collections remaining updates each block.)

**What to say:**
"When you see this screen, click BEGIN when you're ready to start the next collection."

---
***Important:***
Make sure participants get all the way to the end of the task. If they do, there should be no more buttons and the screen should close on its own. If this does not happen, the data will not get pushed.

## Notes for Experimenters

- **Timing**: Participants have 7 seconds to respond to each slider and switch/stay decision
- **Touch Screen Mode**: If using a touch screen, participants tap or drag on the slider line to set their rating
- **Mouse Mode**: If using a mouse, participants can click or drag the slider
- **Button Positions**: All buttons are positioned away from screen edges for better clickability
- **Decision screen labels**: On the switch/stay screen, "you" (green) and the partner name "Amy" or "Ben" (blue) appear below the scale next to the markers
- **Leaderboard**: Shows 5 players (P01-P05), participant ranked 2; CONTINUE button is placed lower to avoid overlap with text
- **Practice vs. Real**: The practice block uses Carly (Amy's assistant; same image as Amy) and 4 simple shapes: green circle, red circle, blue circle (study phase), and blue square (trial 3 recognition—the NEW item). Carly only appears in practice. The real experiment uses Amy or Ben as partners and photographs from the THINGS dataset
- **Amy vs. Ben accuracy**: Amy (reliable blocks): 90% accuracy (9 correct per 10-trial block). Ben (unreliable blocks): 40% accuracy (4 correct per 10-trial block).
- **Amy vs. Ben confidence**: Amy (reliable blocks): Confidence correlated with correctness—when correct, high confidence (0.75–1.0 on correct side); when wrong, moderate confidence (0.5–0.75 or 0.25–0.5 depending on which wrong side). Ben (unreliable blocks): Random within chosen category (0–0.25 for OLD, 0.75–1.0 for NEW)—participants cannot infer accuracy from Ben's confidence.
- **Partner rating text**: When Amy, Ben, or Carly is rating, "[Partner name] is rating..." appears below the slider bar and above the SUBMIT button (in blue).
- **Exit instructions (tell participants before task)**: Laptop users can press ESC any time to exit. Touch screen users: the Exit button only appears when you need to tap a button or make a decision—not during image display, fixation, or outcome screens. Exit when you see it.

---

## Troubleshooting

- The task should not quit if they accidentally turn the Surface Pro off, but be sure to log this if it happens. 
- If a participant times out, the task will automatically select a random response and continue.
- If the participant accidentally minimizes the screen, navigate to the PsychoPy tab in the corner and click on the screen where the task is displayed to continue. Make sure to log this if it happens!
- If there are any unexpected bugs, quit the terminal and restart the task again. Sometimes (only on the computer version) the task lags and gets stuck on "begin". For Windows, you should be able to navigate away. For Mac, hit Cmd+Opt+Esc for 3 seconds to force quit. After you restart, it should work normally again. 
- If the participant has trouble with clicking, make sure they are set up in a position where they aren't accidentally touching multiple points at the same time!
- **To exit the task**: Laptop users press **ESC** (always works). Touch screen users tap the **Exit** button (top-right) when it appears—it is only shown on interactive/decision screens, not during fixation, image display, or outcome screens. If needed, close the terminal window to force quit.
- All data is saved automatically after each trial.
- Log files are saved to the `../LOG_FILES/` directory.
- Email kahinimehta@hotmail.com for any issues.
