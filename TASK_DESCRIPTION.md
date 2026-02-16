# Social Recognition Memory Task with Human–AI Collaboration

Canonical task specification. CSV fields and neural event mapping: `CSV_VARIABLES_DOCUMENTATION.md`. Experimenter script: `script.md`.

## Overview

This task examines how participants collaborate with an AI partner during a recognition memory task. Participants study images and then test their memory by rating images as "OLD" (studied) or "NEW" (not studied), while collaborating with an AI partner who also provides ratings.

**Duration**: 20-35 minutes (30-40 minutes for slower participants)  
**Structure**: 10 blocks × 10 trials = 100 total trials  
**Response Timeout**: 7 seconds per response (slider and switch/stay decisions)

---

## Task Structure

### Overall Design

- **10 experimental blocks**, each containing:
  - **Study Phase**: View 10 images sequentially (no responses required)
  - **Recognition Phase**: 10 trials testing memory with AI collaboration

- **1 practice block** (3 trials) to familiarize participants with the task

---

## Stimuli

### Stimulus Structure

- **100 unique stimuli** organized into **10 categories** with **10 items per category**:
  - BIG_ANIMAL (e.g., Alligator, Elephant, Giraffe)
  - BIG_OBJECT (e.g., Barrel, Chair, Couch)
  - BIRD (e.g., Chicken, Duck, Owl)
  - FOOD (e.g., Bagel, Pizza, Soup)
  - FRUIT (e.g., Apple, Banana, Orange)
  - INSECT (e.g., Ants, Bee, Butterfly)
  - SMALL_ANIMAL (e.g., Cat, Dog, Mouse)
  - SMALL_OBJECT (e.g., Balloon, Camera, Key)
  - VEGETABLE (e.g., Carrot, Kale, Pepper)
  - VEHICLE (e.g., Airplane, Bike, Car)

- Each item has two versions:
  - **Image version**: The original image (e.g., `Image_041.jpg`)
  - **Lure version**: A similar but distinct version (e.g., `Lure_041.jpg`)

- **Total**: 100 Image files + 100 Lure files = **200 total image files**

### Study Phase Stimulus Selection

- **Each block contains exactly 1 item from each of the 10 categories (10 stimuli per block)**
- **No repeats across blocks**: Each of the 100 stimuli appears exactly once across all 10 experimental blocks
- Example: Block 1 might have Apple (FRUIT), Carrot (VEGETABLE), Chair (BIG_OBJECT), etc.
- Example: Block 2 might have Banana (FRUIT), Kale (VEGETABLE), Bench (BIG_OBJECT), etc.

### Recognition Trial Distribution

- **Exactly 5 studied and 5 lure trials per block** (50/50 split)
- **5 studied trials**: Show the original Image version (OLD)—these are "studied" trials
- **5 lure trials**: Show the Lure version of the **same object** as a studied item (NEW)—these are "lure" trials
  - **Important**: Lures correspond to the same category/object as the studied image (e.g., if `Image_041.jpg` was studied, the lure would be `Lure_041.jpg`, not a random lure from a different object)
- Each of the 10 studied images appears exactly once in recognition—5 as studied images, 5 as lures

### Practice Block Stimuli

- Practice block uses **4 placeholder shape stimuli** from the PLACEHOLDERS folder (3 circles for study + blue square for trial 3 recognition)
- Practice stimuli are not replaced with real stimuli (kept as simple shapes for practice)

---

## Block Structure

### Phase 1: Study Phase

- Participants view **10 images** sequentially
- **No responses required**
- Each image is shown for **1 second**
- **Jittered fixations** (0.25-0.75 seconds) appear before EVERY image, including the first image
- Image presentation timings are recorded (onset, offset, duration, fixation duration)
- Participants are instructed to remember each image carefully

### Phase 2: Recognition Phase

Each of the 10 trials follows this structure:

1. **Pre-trial Fixation Cross**: 0.5 seconds (fixed duration, shown before each image)
2. **Image Presentation**: Shows either the studied image or its lure (50% chance each) for 1.0 second (fixed)
3. **Participant Rating**: Rate memory confidence on continuous slider (tap or arrow keys; 7 s timeout)
4. **AI Partner Rating**: AI partner also rates the image
   - AI RT: Log-normal distribution (mu=0.5, sigma=0.3), capped at 5.0 seconds
   - Animation shows AI's slider clicking and submitting
5. **Collaboration Decision**: Participant decides to STAY or SWITCH
   - Timeout: 7 seconds (random decision selected if timeout)
6. **Outcome Feedback**: Shows correctness and curator scoring
   - "Correct" (green) or "Incorrect" (red)
   - "The in-house curator scored this image: X points"
   - Display duration: 2 seconds
7. **Jittered Fixation**: 0.25-0.75 seconds (uniform random distribution) between trials
   - Distribution: `random.uniform(0.25, 0.75)` - each jitter independently drawn
   - Shown as fixation cross during inter-trial interval
   - **No jitter after the last trial** in each block
   - **9 jittered fixations per block** (between 10 trials)

---

## Trial Procedure Details

### Participant Rating (Slider Response)

- **Continuous slider** (left = OLD, right = NEW); position indicates confidence
- **Touch screen**: Tap once on the slider line to set rating, then tap SUBMIT
- **Keyboard (computer)**: Press LEFT/RIGHT arrow keys repeatedly (holding won't work), Return to submit
- Cannot submit until slider has been moved from center; "Please select an answer first" if attempted
- **Timeout**: 7 seconds (random answer selected if timeout)

### AI Partner Rating

- AI partner also rates each image on the same slider
- **AI Response Time (RT)**: Drawn from a log-normal distribution (jittered)
- **AI Confidence**:
  - **Amy (reliable blocks)**: Confidence correlated with correctness. When correct, high confidence—0.75–1.0 on the correct side (uniform random). When wrong, moderate confidence—0.5–0.75 if she said NEW (but correct was OLD), or 0.25–0.5 if she said OLD (but correct was NEW). Confidence is informative about accuracy.
  - **Ben (unreliable blocks)**: Random within chosen category (0–0.25 for OLD, 0.75–1.0 for NEW)—confidence is uninformative about correctness
- **AI Accuracy**: Block-level target rate (0.75 Amy, 0.35 Ben, 0.5 practice). With 10 trials, achieved rates are 80% (8/10) and 40% (4/10) due to rounding. Per-trial correctness is pre-generated per block; see AI Accuracy Manipulation below.
- Animation shows AI's slider clicking (handle appears at chosen position) and clicking submit

### Turn-Taking Manipulation

- **Turn order is randomized within each block**: AI goes first on a **random 5 out of 10 trials** in each block
- The 5 trials where AI goes first are randomly selected for each block (different randomization per block)
- Participant goes first on the remaining 5 trials in each block
- The `participant_first` field in the CSV logs who goes first for each trial (True = participant first, False = AI first)

### AI Accuracy Manipulation

- **Reliable blocks**: Target 75% (Blocks 1-3 and 6-7, Amy)—**80% achieved** (8 correct per 10-trial block, from `round(0.75×10)`)
- **Unreliable blocks**: Target 35% (Blocks 4-5 and 8-10, Ben)—**40% achieved** (4 correct per 10-trial block, from `round(0.35×10)`)
- **Block structure**:
  - Blocks 1-3, 6-7: Reliable (Amy), 80% achieved
  - Blocks 4-5, 8-10: Unreliable (Ben), 40% achieved
  - Turn order randomized within each block (AI first on 5 random trials)

**Implementation details**: The AI uses `int(round(accuracy_rate * num_trials))` per block. With 10 trials: 0.75→8 correct (80%), 0.35→4 correct (40%). CSV: `ai_correct` = per-trial correctness; `ai_reliability` = block target (0.75, 0.35, or 0.5).

### Collaboration Decision (STAY/SWITCH)

After seeing both ratings, participants choose:

- **STAY**: Keep their original confidence rating
- **SWITCH**: Adopt the AI partner's confidence rating

**Important**: Even if both agree on OLD or NEW, participants can still switch to match the AI's confidence level.

- **Timeout**: 7 seconds (random decision selected if timeout)
- Both ratings are displayed visually (green for participant, blue for AI)

---

## Scoring System

### Points Calculation

Points are earned based on **Euclidean distance** between the final answer and the correct answer:

- **Formula**: `Points = 1.0 - distance`
- **Maximum**: 1.0 point (exactly correct)
- **Minimum**: 0.0 points (completely wrong)

### Scoring Rules

- **Confident + Correct**: Earn MORE points (closer to 1.0)
- **Confident + Wrong**: LOSE more points (closer to 0.0)
- **Less confident**: Moderate point loss/gain

The closer the final answer is to the correct answer, the more points earned.

### Point Display (Curator Scoring Framing)

All scoring is framed as "in-house curator" evaluations:

- **After each trial**: "Correct/Incorrect" plus "The in-house curator scored this image: X points based on image & your confidence."
- **End of each block**: "The in-house curator scored this collection X points out of a total of 10 points!"
- **End of experiment**: "The in-house curator scored all your collections X points out of a total of 100 points!"

Points = 1.0 − Euclidean distance from correct answer (range 0.0–1.0 per trial). Display rounded to 1 decimal place; CSV logs full precision.

---

## Data Collection

Participant RTs, slider values, switch/stay decisions, accuracy, AI responses, and trial metadata are logged trial-by-trial. Photodiode/TTL timestamps align with neural recordings. See `CSV_VARIABLES_DOCUMENTATION.md` for all variable definitions, file structure, and saving locations.

### Neural Data Logging (Photodiode & TTL)

Photodiode (0.03 × 0.01) at (-0.70, -0.48) touch / (-0.75, -0.48) keyboard. Off only during name entry; thereafter every screen change, stimulus, and response triggers a black flash (TTL) then white. Keyboard mode: 17 ms delay between black and white flips to prevent vsync coalescing; touch screen skips this delay. See `CSV_VARIABLES_DOCUMENTATION.md` for event list and TTL timing.

---

## Practice Block

### Structure

- **3 trials** (practice only)
- **4 shape stimuli**: Green circle, red circle, blue circle (for sequential presentation), and blue square (for trial 3 recognition)
- **Practice recognition trials**:
  - Trial 1: Green circle (participant rates only)
  - Trial 2: Red circle (AI rates first, then participant rates)
  - Trial 3: Blue square (full trial: participant rates, AI rates, switch/stay decision)
- **Practice flow**:
  1. Welcome message: Amy's studio, Carly (her assistant) will walk through practice; Carly's picture (same image as Amy)
  2. Sequential presentation of 3 shapes (green circle, red circle, blue circle), each for 1.5 seconds with fixations between
  3. Transition screen: "Now let's see how well you recall the shapes you've seen!"
  4. Trial 1: Green circle—participant rates only
  5. Trial 2: Red circle—shows "Carly is confident she's seen this before", AI clicks "all the way on the old" side, then participant rates
  6. Trial 3: Blue square (NEW; not the blue circle from encoding)—shows "Now, work with Carly", participant rates, then AI selects OLD but not very confident (slider at 0.4) incorrectly (it's a new square), then participant performs switch/stay decision, outcome shown
- **Note**: Carly (Amy's assistant) appears only in practice; same image as Amy.
- **Outcome explanations**: Practice trials 1–2 show just "Correct" or "Incorrect". Practice trial 3 shows "Correct/Incorrect. Based off your answer and confidence, your points are X."
- **Slider instruction**: Touch screen—tap once to set rating. Keyboard (computer)—press LEFT/RIGHT repeatedly (holding won't work), Return to submit.

### Purpose

- Familiarize participants with task mechanics (slider, collaboration, curator scoring)
- **Note**: Practice stimuli are simple shapes, not replaced with final stimuli

---

## Additional Features

### Instructions

- **Comprehensive instructions** broken into digestible sections:
  - Welcome and overview
  - How it works (study and recognition phases)
  - Slider usage
  - Collaboration mechanics
  - Scoring system (2 pages)
- **Rules reminder** before experimental blocks (3 pages: Task Overview, Working with Amy, Scoring)
- **Color-coded headers** for easy navigation
- **Formatted text** with emphasis on key concepts

### Leaderboard

- **Displayed at end of experiment**
- Shows participant ranked 2 out of 5 (fixed rank)
- **Anonymized participant names**: P01-P05
- Participant shown as "[ID] (you)" at their rank
- **No scores displayed** - only rank and participant names

### Transition Screens

- **Task flow**: Participant enters name first (photodiode off); then BEGIN screen and all subsequent screens have photodiode/TTL for every change.
- **Initial screen**: "Hello & welcome to the social memory game! Pay careful attention to the text on the screen. Some images will be very deceptively similar."
- **Before practice**: Welcome message—Amy's studio; Carly (her assistant) will walk through practice (same image as Amy)
- **After practice**: Transition message explaining the real work begins with Amy organizing photographs
- **Before each block**: "Ready to start sorting?" screen showing collections remaining count with BEGIN button
- **Between blocks**: Partner switch messages when partner changes (Amy ↔ Ben), or brief break message
- **Final screen**: Shows cumulative curator scoring, leaderboard (without scores), total task time, and thank you message

---

#### Localizer Task

Separate task for object verification. Participants view 200 images (100 Image + 100 Lure) in random order.

- **Object questions** (not category): At every 10th trial, asks "Was the last object a [object]?" (e.g., "Was the last object a giraffe?")
- **Question design (50/50 split)**: 
  - 50% of trials (10 questions): Ask about the correct object shown (correct answer = YES)
  - 50% of trials (10 questions): Ask about a **random incorrect object** drawn from all other objects in the stimulus set (correct answer = NO)
  - Pre-generated sequence ensures exactly 10 correct and 10 incorrect questions in randomized order
- **Feedback**: No per-trial feedback. Accuracy summary ("Your accuracy: X/20 (Y%)") shown at the very end only.
- **Question timeout**: 10.0 seconds (differs from main task's 7.0 second timeouts)

**Timing**:
- **Fixation cross**: Jittered 0.25-0.75 seconds before each image (`random.uniform(0.25, 0.75)`), 200 fixations total
- **Image duration**: 0.5 seconds per image (fixed)
- **Question timing**: Asked at trials 10, 20, 30, ..., 200 (20 questions total)
- **Total duration**: Approximately 3-5 minutes

**Neural data**: Same as main task (fixation onset/offset, image onset/offset). YES/NO question onset (`question_trigger`) and participant answer tap/key (`question_answer_trigger`) trigger flashes; both logged in localizer CSV. Every TTL trigger is also logged to `localizer_ttl_events_[participant_id]_[timestamp].csv`.


### Window and Display

- **Window**: Fullscreen on both laptop and touch screen
- **Exit (main task)**: Laptop—ESC anytime. Touch screen—Exit button (top-right) when visible (input/instructions/decisions). Not shown during fixation, image display, or outcome.
- **Localizer**: ESC and Exit available at all times
- **Window focus**: Automatically activated on macOS
- **Initial screen**: "Hello & welcome to the social memory game! ..." with BEGIN button

### File Management

- **Placeholder stimuli**: Generated automatically if missing or incorrect
- **Data files**: Saved to `../LOG_FILES/` with participant ID and timestamp. Main task: recognition_study, recognition_trials, recognition_summary, recognition_ttl_events. Localizer: localizer, localizer_ttl_events.
- **Incremental saving**: All CSVs written incrementally (trial-by-trial or event-by-event); data preserved if task is interrupted.

---

## Summary

This task examines social decision-making in a memory recognition context, where participants collaborate with an AI partner whose accuracy and turn order vary across blocks. The design allows investigation of how these factors influence collaboration strategies, trust, and performance optimization.

