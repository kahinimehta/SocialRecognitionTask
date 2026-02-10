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

### Initial Screen
**Display says:**
"Hello & welcome to the social memory game! Pay careful attention to the text on the screen."

**What to say:**
"Welcome! You'll see a welcome message on the screen. Please read it carefully and click CONTINUE when you're ready."

---

### Welcome Screen 1
**Display says:**
"Greetings!

You've just joined a small photography studio.

Amy, a professional photographer, is preparing images for an upcoming exhibition.

She needs help sorting through large sets of images and deciding which ones truly belong. Will you be her employee of the month?"

[Image of Amy appears below]

**What to say:**
"This is Amy, your partner for this task. You'll be helping her sort through images for an exhibition. Click CONTINUE when you're ready."

---

### Welcome Screen 2
**Display says:**
"Before you begin the real work, you'll complete a short training round to get familiar with the process.

For now, simply memorize the shapes you're about to see. Click continue when you're ready to get started!"

**What to say:**
"You'll start with a practice round to learn how the task works. First, you'll see some shapes - just memorize them. Click CONTINUE when ready."

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
- Slider with both arrows showing:
  - Green arrow pointing to participant's choice (labeled "Your choice" above)
  - Blue arrow pointing to Amy's choice (labeled "Amy's choice" below)
- Text: "Do you want to STAY with your answer or SWITCH to Amy's answer?"
- STAY button (light blue)
- SWITCH button (light coral)

**What to say:**
"You can see both your rating and Amy's rating on the slider. The green arrow shows your choice, and the blue arrow shows Amy's choice. You can STAY with your answer or SWITCH to Amy's answer. Even if you both agree on OLD or NEW, you can still switch to match Amy's confidence level."

---

### Outcome Screen
**Display shows:**
- Feedback about the score (e.g., "The in-house curator scored this image: X points")

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
Remember which images belong in each collection.

Rate each image: OLD (belongs) or NEW (doesn't belong).
Click on the slider, then SUBMIT."

**What to say:**
"Read these instructions carefully. You'll need to remember which photos belong in each collection. These will be more complex images -- like animals, objects, etc. Use the slider to rate each image - OLD means it belongs, NEW means it doesn't. Click on the slider line to set your rating, then click SUBMIT."

---

### Instructions - Working with Amy
**Display says:**
"Working with Amy:
Amy will also rate each image. You can STAY with your answer or SWITCH to hers.

You can switch even if you both agree, to match her confidence level."

**What to say:**
"Amy will rate each image too. After you both rate, you can STAY with your answer or SWITCH to Amy's answer. You can switch even if you both agree, to match her confidence level."

---

### Instructions - Scoring
**Display says:**
"Scoring:
Confidence matters. A curator scores based on accuracy and confidence.

10 collections, 10 images each. Time limit per decision."

**What to say:**
"The scoring system considers both accuracy and confidence. If you are confident but wrong, you lose more points than if you are not confident and wrong. If you are right but not confident, you will not get as many points as if you were both right and confident. There are 10 collections total, with 10 images in each. You'll have a time limit for each decision."

---

### Amy Introduction Before Collections
**Display shows:**
"Work with Amy to sort this collection.

Sometimes she goes first, sometimes you do."

[Image of Amy appears]

**What to say:**
"This is Amy again. Remember, sometimes she'll rate first, sometimes you will. Click CONTINUE when ready."

---

## Notes for Experimenters

- **Timing**: Participants have 7 seconds to respond to each slider and switch/stay decision
- **Touch Screen Mode**: If using a touch screen, participants tap or drag on the slider line to set their rating
- **Mouse Mode**: If using a mouse, participants can click or drag the slider
- **Button Positions**: All buttons are positioned away from screen edges for better clickability
- **Arrow Labels**: On the decision screen, "Your choice" appears above the green arrow, and "Amy's choice" or "Ben's choice" appears below the blue arrow
- **Practice vs. Real**: The practice block uses simple shapes (green circle, red circle, blue square). The real experiment uses photographs from the THINGS dataset

---

## Troubleshooting

- If a participant times out, the task will automatically select a random response and continue
- If the participant accidentally minimizes the screen, navigate to the psychopy tab in the corner 
- If there are any unexpected bugs, quit the terminal and restart the task again
- If the participant has trouble with clicking, make sure they are set up in a position where they aren't accidentally touching multiple points at the same time!
- If there are technical issues, close the terminal window to exit
- All data is saved automatically after each trial
- Log files are saved to the `../LOG_FILES/` directory
- Email kahinimehta@hotmail.com for any issues
