# Experimenter Script

## Quick Start Instructions

### For Running the Main Experiment:
1. Open terminal
2. Type `n` when prompted to confirm you want to run the localizer (this skips the localizer)
3. Type `experiment` when prompted
4. Say `y` to:
   - Running the experiment
   - Uploading the log files

### For Participants Running the Localizer:
1. Open terminal
2. Enter `y` when prompted

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
"Now you'll see images one at a time. For each one, decide if you've seen it before (OLD) or if it's new (NEW). Use the slider - click anywhere on the line to set your rating, then click SUBMIT."

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
"Read these instructions carefully. You'll need to remember which images belong in each collection. Use the slider to rate each image - OLD means it belongs, NEW means it doesn't. Click on the slider line to set your rating, then click SUBMIT."

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
"The scoring system considers both accuracy and confidence. There are 10 collections total, with 10 images in each. You'll have a time limit for each decision."

---

### Amy Introduction Before Collections
**Display shows:**
"Work with Amy to sort this collection.

Sometimes she goes first, sometimes you do."

[Image of Amy appears]

**What to say:**
"This is Amy again. Remember, sometimes she'll rate first, sometimes you will. Click CONTINUE when ready."

---

### Collection Start Screen
**Display says:**
"Let's get started on collection 1!"

**What to say:**
"Here we go! Collection 1 is starting."

---

### Ready to Start Screen (Before Each Block)
**Display shows:**
"Ready to start sorting?

[X] collections remaining"

[BEGIN button]

**What to say:**
"You'll see how many collections are left. Click BEGIN when you're ready to start this collection."

---

### Study Phase
**Display shows:**
- Fixation cross (+)
- Image appears for 1.5 seconds
- Repeats for 10 images

**What to say:**
"Watch carefully. You'll see 10 images one at a time. Memorize which images belong in this collection."

---

### Transition Screen (Study to Recognition)
**Display says:**
"STUDYING COLLECTION IMAGES COMPLETE!

Now switching to the sorting phase.

You will see MORE images again and rate them with [Amy/Ben]."

**What to say:**
"Great! You've finished studying. Now you'll see more images and rate them together with your partner."

---

### Recognition Phase - Participant Goes First
**Display shows:**
- Image
- Slider (OLD left, NEW right)
- SUBMIT button

**What to say:**
"Now rate this image. Is it OLD (part of the collection) or NEW (not part of the collection)? Click on the slider to set your rating, then click SUBMIT."

---

### Recognition Phase - Amy Goes First
**Display shows:**
- Message: "Amy is rating..."
- Image
- Amy's slider animation (she taps and submits)
- Then participant's slider appears

**What to say:**
"Amy is rating first. Watch what she does, then it will be your turn."

---

### Collection Complete Screen
**Display says:**
"Collection [X] Complete!

The in-house curator scored this collection [X.X] points out of a total of [X] points!"

**What to say:**
"Great job! You've completed this collection. The curator has scored it. Click CONTINUE to move on."

---

### Partner Switch Screen (Block 4)
**Display shows:**
"A quick update.

Amy has stepped away to prepare for her exhibition.

While she's gone, you'll be working with Ben—another assistant in the studio.

Ben is helping sort the same set of images, but he has trained differently than you.

As always, focus on making the best judgment you can. Click to start sorting!"

[Image of Ben appears]

**What to say:**
"Amy has stepped away, and now you'll be working with Ben. He's another assistant who may have different training. Just continue making your best judgments. Click CONTINUE when ready."

---

### Partner Switch Screen (Block 6)
**Display shows:**
"Amy is back!

You'll be working with Amy again for the next collections.

Click to start sorting!"

[Image of Amy appears]

**What to say:**
"Amy is back! You'll be working with her again. Click CONTINUE when ready."

---

### Partner Switch Screen (Block 8)
**Display shows:**
"Amy has stepped away again.

You'll be working with Ben for the remaining collections.

Click to start sorting!"

[Image of Ben appears]

**What to say:**
"Amy has stepped away again. You'll finish with Ben. Click CONTINUE when ready."

---

### Final Summary Screen
**Display shows:**
"The in-house curator scored all your collections [X.X] points out of a total of [X] points!"

**What to say:**
"Excellent work! You've completed all 10 collections. The curator has scored everything. Click CONTINUE to see the leaderboard."

---

### Leaderboard Screen
**Display shows:**
A leaderboard showing:
- Rank 1: [Fake participant name]
- Rank 2: [Your participant ID] (you)
- Rank 3-7: [Other fake participant names]

**What to say:**
"Here's how you ranked compared to other participants. You're ranked [X] out of 7. Click CONTINUE to finish."

---

## Notes for Experimenters

- **Timing**: Participants have 7 seconds to respond to each slider and switch/stay decision
- **Touch Screen Mode**: If using a touch screen, participants tap on the slider line to set their rating
- **Mouse Mode**: If using a mouse, participants can click or drag the slider
- **Button Positions**: All buttons are positioned away from screen edges for better clickability
- **Arrow Labels**: On the decision screen, "Your choice" appears above the green arrow, and "Amy's choice" or "Ben's choice" appears below the blue arrow
- **Practice vs. Real**: The practice block uses simple shapes (green circle, red circle, blue square). The real experiment uses photographs from the THINGS dataset

---

## Troubleshooting

- If a participant times out, the task will automatically select a random response and continue
- If there are technical issues, press ESCAPE to exit
- All data is saved automatically after each trial
- Log files are saved to the `../LOG_FILES/` directory
