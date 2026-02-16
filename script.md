# Experimenter Script

Full task specs: `TASK_DESCRIPTION.md`. CSV format: `CSV_VARIABLES_DOCUMENTATION.md`.

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

This will run the localizer and upload the log files. The localizer uses the same input method screen (Touch Screen or Keyboard). For input selection: press Right Arrow to choose Keyboard. During task: use Return for CONTINUE/BEGIN/EXIT, LEFT for YES, RIGHT for NO on object questions. 

### For Pushing Log Files:
If you only want to push the log files without running anything else, you may open a new *Anaconda PowerShell Prompt Terminal* and enter "n" and enter when prompted to run the localizer. 

### Updating the repo
The code should automatically update every time you open the terminal or run the experiment. If this is not the case, reach out to kahinimehta@hotmail.com

**To exit**: Laptop—ESC anytime. Touch screen—Exit button (top-right) only during decisions/buttons, not during fixation or image display. Localizer: ESC and Exit work anytime.

**Experimenter note**: Tell participants the above. Emphasize leaderboard, collaboration, subtle image differences, confidence matters. 


---

## Full Experiment Script

### Input Method Screen (first)
**Display says:**
"What input method are you using?

Double tap for touch screen, or press Right Arrow for keyboard:

(Press ESC or tap Exit to leave fullscreen)"

**Display shows:** Two buttons: "TOUCH SCREEN (Double tap)" and "KEYBOARD (Press Right Arrow)" (text may wrap to two lines per button). A small **Exit** button (top-right corner).

**What to say:**
- **Touch screen:** "First, double-tap the Touch Screen button."
- **Keyboard (laptop):** "Or press the Right Arrow key for Keyboard if you're using a laptop with the keyboard."

**After selection:** Display confirms "Input method set to: TOUCH SCREEN" or "Input method set to: KEYBOARD. Use Return for all buttons." with a CONTINUE button.

**Exit fullscreen:** **ESC** (laptop) or tap **Exit** (top-right). Same on all screens with CONTINUE/instruction buttons.

---

### Participant ID Screen (first)
**Display says:**
"Enter your first name and last initial with no spaces/capitals:"
(Keyboard mode: "Hit Enter when done." also shown.)

**Display shows:** Text field for typing; BACKSPACE and CONTINUE buttons (touch screen) or type and press Enter (keyboard).

**What to say:**
"Enter your first name and last initial, no spaces or capitals. When you're done, press Enter" — *keyboard* — "or tap CONTINUE" — *touch screen* — "."

*Note: Name entry happens first (like localizer). Photodiode/TTL is off during name entry; after name is submitted, photodiode is on for every subsequent screen change, stimulus, and response.*

---

### Initial Screen (BEGIN)
**Display says:**
"Hello & welcome to the social memory game! Pay careful attention to the text on the screen. Some images will be very deceptively similar."

**Display shows:** A BEGIN button (light blue).

**What to say:**
"Welcome! You'll see a welcome message on the screen. Please read it carefully. When you're ready, press Return" — *keyboard* — "or tap BEGIN" — *touch screen* — "to continue."

---

### Welcome Screen 1 (Practice: Amy's Assistant Carly)
**Display says:**
"Greetings!

You've just joined Amy's photography studio. She's preparing images for an upcoming exhibition.

Carly, her assistant, will walk you through a short practice to get familiar with the task."

**Display shows:** Image of Carly (same as Amy) below the text, CONTINUE button (bottom right).

**What to say:**
"This is Carly, Amy's assistant. She'll walk you through a short practice to learn the task. The actual work will be with Amy. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — "when you're ready."

---

### Welcome Screen 2
**Display says:**
"Before you begin the real work, you'll complete a short training round to get familiar with the process.

For now, simply memorize the shapes you're about to see. Continue when you're ready to get started!"

**Display shows:** CONTINUE button.

**What to say:**
"You'll start with a practice round to learn how the task works. First, you'll see some shapes—just memorize them. Continue when ready."

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
- Prompt varies by mode:
  - **Keyboard:** "Press LEFT or RIGHT arrow keys repeatedly to move the slider (holding won't work). How close you are to either side indicates how CONFIDENT you are. Press Return when done."
  - **Touch screen:** "CLICK ONCE on the sliding bar to show how confident you are you've seen this before (i.e., it is \"old\"). How close you are to either side indicates how CONFIDENT you are in your answer."
- Slider with OLD on left, NEW on right
- SUBMIT button

**What to say:**

- **Keyboard:** "Now you'll see images one at a time. For each one, decide if you've seen it before (OLD) or if it's new (NEW). Press the LEFT and RIGHT arrow keys repeatedly to move the slider—you have to press multiple times, holding the key won't work. Press Return when you're ready to submit."
- **Touch screen:** ***Make sure they know to CLICK/TAP ONCE, not DRAG the slider.*** "Now you'll see images one at a time. For each one, decide if you've seen it before (OLD) or if it's new (NEW). Use the slider—CLICK or TAP ONCE, not slide, anywhere on the line to set your rating, then tap SUBMIT. How far you tap shows how confident you are."

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
- Slider with black dots marking each rating position:
  - Participant's dot with "you" label (green text) below the scale
  - Partner's dot with partner name label (blue text): "Carly" during practice, "Amy" or "Ben" during experimental blocks
- Text: "Do you want to STAY with your answer or SWITCH to [partner's] answer?" (Carly during practice, Amy or Ben during experimental blocks). Keyboard adds: "(Press LEFT for STAY, RIGHT for SWITCH)"
- STAY button (light blue)
- SWITCH button (light coral)

**What to say:**
"You can see both your rating and your partner's rating on the slider. The green marker shows your choice, and the blue marker shows your partner's choice. You can STAY with your answer or SWITCH to your partner's answer. For keyboard users: press LEFT for STAY, RIGHT for SWITCH. Even if you both agree on OLD or NEW, you can still switch to match their confidence level."

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

**Display shows:** CONTINUE button.

**What to say:**
"Great! The practice is done. Now we'll start the actual task. There will be brief instructions coming up."

---

### Instructions - Task Overview
**Display says:**
"Task Overview:
Remember which photos belong in each collection.

Rate each image: OLD (belongs) or NEW (doesn't belong).
Press LEFT/RIGHT arrow keys repeatedly to move the slider (holding won't work—press multiple times), then Return to submit." — *keyboard*
"Click on the slider, then SUBMIT." — *touch screen*

**Display shows:** CONTINUE button.

**What to say:**
"Read these instructions carefully. You'll need to remember which photos belong in each collection. Important: For each collection, you will only be sorting the 10 images you just saw for that collection—nothing from prior collections. These will be more complex images—like animals, objects, etc. Use the slider to rate each image—OLD means it belongs, NEW means it doesn't. Keyboard: press LEFT/RIGHT repeatedly to move the slider—holding won't work. Then Return. Touch screen: tap the slider to set your rating, then SUBMIT."

---

### Instructions - Working with Amy
**Display says:**
"Working with Amy:
Amy will also rate each photo. You can STAY with your answer or SWITCH to hers.

You can switch even if you both agree, to match her confidence level."

**Display shows:** CONTINUE button.

**What to say:**
"Amy will rate each image too. After you both rate, you can STAY with your answer or SWITCH to Amy's answer. You can switch even if you both agree, to match her confidence level. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — " to continue."

---

### Instructions - Scoring
**Display says:**
"Scoring:
Confidence matters. An in-house curator scores based on accuracy and confidence.

10 collections, 10 images each. Time limit per decision."

**Display shows:** CONTINUE button.

**What to say:**
"The scoring system considers both accuracy and confidence. If you are confident but wrong, you lose more points than if you are not confident and wrong. If you are right but not confident, you will not get as many points as if you were both right and confident. There are 10 collections total, with 10 images in each. You'll have a time limit for each decision. Some of the image differences will be extremely, extremely subtle, so pay close attention! *You will see how you compared against other anonymous players at the end via a leaderboard!*"

---

### Amy Introduction (Blocks 1–3, 6–7)
**Display says:**
"Work with Amy to sort this collection.

Sometimes she goes first, sometimes you do."

**Display shows:** Image of Amy, CONTINUE button (bottom right).

**What to say:**
"Work with Amy to sort this collection. Sometimes she'll rate first, sometimes you will. Remember that Amy treasures collaboration in her coworkers, and likes them to work together on these images rather than independently. Remember, you are only responsible for remembering the last 10 images you saw before sorting—nothing from prior collections. Each collection has a different set of images. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — " when ready to get started."

---

### Partner Switch to Ben (Before Block 4)
**Display says:**
"A quick update.

Amy has stepped away to prepare for her exhibition.

While she's gone, you'll be working with Ben—another assistant in the studio.

Click CONTINUE to start sorting!"

**Display shows:** Image of Ben, CONTINUE button.

**What to say:**
"Amy has stepped away for a bit. You'll now work with Ben, another assistant. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — " when ready."

---

### Partner Switch to Ben Again (Before Block 8)
**Display says:**
"Amy has to step away again! You will work with Ben again for the last collections."

**Display shows:** Image of Ben, CONTINUE button.

**What to say:**
"You'll work with Ben again for the remaining collections. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — " when ready."

---

### Return to Amy (Before Block 6)
**Display says:**
"Amy is back for a day!

She's returning to help you with exhibition preparation."

**Display shows:** Image of Amy, CONTINUE button (bottom right).

**What to say:**
"Amy is back. You'll work with her again for this collection. Press Return" — *keyboard* — "or tap CONTINUE" — *touch screen* — " when ready."

---

### Ready to Start (Before Each Block)
**Display says:**
"Ready to start sorting?

X collection(s) remaining"

**Display shows:** BEGIN button. (Number of collections remaining updates each block.)

**What to say:**
"When you see this screen, press Return" — *keyboard* — "or tap BEGIN" — *touch screen* — " when you're ready to start the next collection."

---
***Important:***
Make sure participants get all the way to the end of the task. If they do, there should be no more buttons and the screen should close on its own. If this does not happen, the data will not get pushed.

## Notes for Experimenters

- **Timing**: 7 s per slider and switch/stay
- **Controls**: Touch — tap once on slider, SUBMIT. Keyboard — LEFT/RIGHT repeatedly (holding won't work), Return. Switch/stay: LEFT = STAY, RIGHT = SWITCH
- **Blocks**: 1–3, 6–7 = Amy; 4–5, 8–10 = Ben. Partner switches before blocks 4, 6, 8
- **Practice**: 3 shapes, Carly only. Real task: Amy/Ben, THINGS photos
- **Localizer** (if run): 200 images, 20 questions (trials 10, 20, …). "Enter participant ID". LEFT = YES, RIGHT = NO. 10 s timeout. See `TASK_DESCRIPTION.md`.

---

## Troubleshooting

- **Photodiode/TTL**: See `CSV_VARIABLES_DOCUMENTATION.md`.
- The task should not quit if they accidentally turn the Surface Pro off, but be sure to log this if it happens. 
- If a participant times out, the task will automatically select a random response and continue.
- If the participant accidentally minimizes the screen, navigate to the PsychoPy tab in the corner and click on the screen where the task is displayed to continue. Make sure to log this if it happens!
- If there are any unexpected bugs, quit the terminal and restart the task again. Sometimes (only on the computer version) the task lags and gets stuck on "begin". For Windows, you should be able to navigate away. For Mac, hit Cmd+Opt+Esc for 3 seconds to force quit. After you restart, it should work normally again. 
- If the participant has trouble with clicking, make sure they are set up in a position where they aren't accidentally touching multiple points at the same time!
- **Force quit**: Close terminal window if needed.
- Data saved to `../LOG_FILES/`. See `CSV_VARIABLES_DOCUMENTATION.md`.
- If you can no longer push/pull to LOG_FILES, delete the directory and re-clone it into the same location using: `git clone https://github.com/SocialTask12/LOG_FILES`
- Email kahinimehta@hotmail.com for any issues.
