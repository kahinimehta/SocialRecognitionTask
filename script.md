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

---

## Full Experiment Script

### Input Method Screen (first)
**Display says:**
"What input method are you using?

Touch or click the button below:"

**Display shows:** Two buttons: "TOUCH SCREEN (Double tap with finger)" and "MOUSE/TRACKPAD (Click)"

**What to say:**
"First, choose how you'll respond—touch screen or mouse/trackpad. Touch or click the matching button."

---

### Initial Screen
**Display says:**
"Hello & welcome to the social memory game! Pay careful attention to the text on the screen."

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
"Enter your first name and last initial, no spaces or capitals. When you're done, click CONTINUE [or press Enter]."

---

### Welcome Screen 1
**Display says:**
"Greetings!

You've just joined a small photography studio.

Amy, a professional photographer, is preparing images for an upcoming exhibition.

She needs help sorting through large sets of images and deciding which ones truly belong. Will you be her employee of the month?"

**Display shows:** Image of Amy below the text, "Amy" label under the image, CONTINUE button (bottom right).

**What to say:**
"This is Amy, your partner for this task. You'll be helping her sort through images for an exhibition. Click CONTINUE when you're ready."

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

**What to say:**
"Watch the screen. You'll see some shapes appear one at a time. Just memorize them - you don't need to do anything yet."

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
- Slider with OLD on left, NEW on right
- SUBMIT button

**What to say:**

***Make sure they know to CLICK, not DRAG the slider.***
"Now you'll see images one at a time. For each one, decide if you've seen it before (OLD) or if it's new (NEW). Use the slider - CLICK anywhere on the line to set your rating, then click SUBMIT."

---

### Practice Phase - Recognition Trial 2
**Display shows:**
- Message: "Amy is confident she's seen this before!"
- Red circle appears
- Amy's slider animation (she clicks all the way OLD)
- Then participant's slider appears

**What to say:**
"Amy will also rate each image. Sometimes she'll go first, sometimes you will. In this practice trial, Amy went first and rated it as OLD. Now it's your turn to rate it."

---

### Practice Phase - Recognition Trial 3
**Display shows:**
- Blue square
- Participant rates first
- Then Amy rates (she selects OLD but not very confident)
- Then decision screen appears

**What to say:**
"In this trial, you'll rate first, then Amy will rate. After you both rate, you'll see both of your choices and decide whether to STAY with your answer or SWITCH to Amy's answer."

---

### Decision Screen (Switch/Stay)
**Display shows:**
- Image
- Slider with markers (dots) showing each rating:
  - Green marker for participant's choice (labeled "you" below the scale)
  - Blue marker for partner's choice (labeled "Amy" or "Ben" below the scale)
- Text: "Do you want to STAY with your answer or SWITCH to Amy's answer?" (or "Ben's answer" when with Ben)
- STAY button (light blue)
- SWITCH button (light coral)

**What to say:**
"You can see both your rating and your partner's rating on the slider. The green marker shows your choice, and the blue marker shows your partner's choice. You can STAY with your answer or SWITCH to your partner's answer. Even if you both agree on OLD or NEW, you can still switch to match their confidence level."

---

### Outcome Screen
**Display shows:**
- "Correct." or "Incorrect." (green or red)
- "The in-house curator scored this image: X points based on image & your confidence."
- Screen advances automatically after ~1.5 seconds.

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
"Read these instructions carefully. You'll need to remember which photos belong in each collection. These will be more complex images—like animals, objects, etc. Use the slider to rate each image—OLD means it belongs, NEW means it doesn't. Click on the slider line to set your rating, then click SUBMIT."

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
"The scoring system considers both accuracy and confidence. If you are confident but wrong, you lose more points than if you are not confident and wrong. If you are right but not confident, you will not get as many points as if you were both right and confident. There are 10 collections total, with 10 images in each. You'll have a time limit for each decision."

---

### Amy Introduction Before Collections
**Display says:**
"Work with Amy to sort this collection.

Sometimes she goes first, sometimes you do."

**Display shows:** Image of Amy, "Amy" label below the image, CONTINUE button (bottom right).

**What to say:**
"Work with Amy to sort this collection. Sometimes she'll rate first, sometimes you will. Click CONTINUE when ready."

---

### Ready to Start (Before Each Block)
**Display says:**
"Ready to start sorting?

X collection(s) remaining"

**Display shows:** BEGIN button. (Number of collections remaining updates each block.)

**What to say:**
"When you see this screen, click BEGIN when you're ready to start the next collection."

---

### Partner Switch Screens

**First time switching to Ben (before Block 4):**
"A quick update.

Amy has stepped away to prepare for her exhibition.

While she's gone, you'll be working with Ben—another assistant in the studio.

Click CONTINUE to start sorting!"
(Image of Ben appears; no label. CONTINUE button.)

**Second time with Ben (before Block 8):**
"Amy has to step away again! You will work with Ben again for the last collections."
(Image of Ben, CONTINUE button.)

**Switching back to Amy (before Block 6):**
"Amy is back for a day!

She's returning to help you with exhibition preparation."
(Image of Amy, CONTINUE button.)

**What to say:**
"Sometimes your partner will change. You'll work with Amy for some collections and Ben for others. Read the message and click CONTINUE."

---

### After All Blocks – Cumulative Score
**Display says:**
"The in-house curator scored all your collections X points out of a total of 100 points!"

**Display shows:** CONTINUE button.

**What to say:**
"This is your total score across all collections. Click CONTINUE to see the leaderboard."

---

### Leaderboard
**Display shows:**
"AMY'S EMPLOYEE RANKING & LEADERSHIP BOARD"

A table with Rank and Participant (P01–P05); participant is shown as "[ID] (you)" at rank 2. No scores shown. CONTINUE button (positioned lower to avoid overlap with text).

**What to say:**
"Here’s how you compare to other participants. Click CONTINUE when you’re done looking."

---

### Final Screen
**Display says:**
"COLLECTION SORTING COMPLETE!

Total time: X minutes (Y seconds)

Amy thanks you for helping sort the collection!"

**Display shows:** CONTINUE button. After clicking, the task closes.

**What to say:**
"Great job! That’s the end of the task. Click CONTINUE to finish."

---
***Important:***
Make sure participants get all the way to the end of the task. If they do, there should be no more buttons and the screen should close on its own. If this does not happen, the data will not get pushed.

## Notes for Experimenters

- **Timing**: Participants have 7 seconds to respond to each slider and switch/stay decision
- **Touch Screen Mode**: If using a touch screen, participants tap or drag on the slider line to set their rating
- **Mouse Mode**: If using a mouse, participants can click or drag the slider
- **Button Positions**: All buttons are positioned away from screen edges for better clickability
- **Decision screen labels**: On the switch/stay screen, "you" (green) and the partner name "Amy" or "Ben" (blue) appear below the scale next to the markers
- **Leaderboard**: Shows 5 players (P01-P05), participant ranked 2; continue button is placed lower to avoid overlap with text
- **Practice vs. Real**: The practice block uses simple shapes (green circle, red circle, blue square). The real experiment uses photographs from the THINGS dataset

---

## Troubleshooting

- The task should not quit if they accidentally turn the Surface Pro off but be sure to log this if it happens. 
- If a participant times out, the task will automatically select a random response and continue
- If the participant accidentally minimizes the screen, navigate to the psychopy tab in the corner and click on the screen where the task is displayed to continue. Make sure to log this if it happens!
- If there are any unexpected bugs, quit the terminal and restart the task again
- If the participant has trouble with clicking, make sure they are set up in a position where they aren't accidentally touching multiple points at the same time!
- If there are technical issues, close the terminal window to exit
- All data is saved automatically after each trial
- Log files are saved to the `../LOG_FILES/` directory
- Email kahinimehta@hotmail.com for any issues
