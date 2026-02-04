# Social Recognition Memory Task with Human–AI Collaboration

## Overview

This task examines how participants collaborate with an AI partner during a recognition memory task. Participants study images and then test their memory by rating images as "OLD" (studied) or "NEW" (not studied), while collaborating with an AI partner who also provides ratings.

**Duration**: 35-45 minutes (50-60 minutes for slower participants)  
**Structure**: 5 blocks × 20 trials = 100 total trials  
**Response Timeout**: 7 seconds per response

---

## Task Structure

### Overall Design

- **5 experimental blocks**, each containing:
  - **Study Phase**: View 20 images sequentially (no responses required)
  - **Recognition Phase**: 20 trials testing memory with AI collaboration

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

- **Each block contains exactly 2 items from each of the 10 categories (20 stimuli per block)**
- **No repeats across blocks**: Each of the 100 stimuli appears exactly once across all 5 experimental blocks
- Example: Block 1 might have Apple and Banana (FRUIT), Carrot and Kale (VEGETABLE), Chair and Bench (BIG_OBJECT), etc.
- Example: Block 2 might have Orange and Grape (FRUIT), Pepper and Broccoli (VEGETABLE), Couch and Table (BIG_OBJECT), etc.

### Recognition Trial Distribution

- All 10 studied images from each block appear in the recognition phase
- **50% show the studied image** (original Image version): These are "studied" trials
- **50% show the lure version** (Lure version of the **same object** as the studied item): These are "lure" trials
  - **Important**: Lures correspond to the same category/object as the studied image (e.g., if `Image_041.jpg` was studied, the lure would be `Lure_041.jpg`, not a random lure from a different object)
- Each of the 10 studied images appears exactly once in recognition (5 as studied images, 5 as lures)

### Practice Block Stimuli

- Practice block uses **5 placeholder shape stimuli** from the PLACEHOLDERS folder
- Practice stimuli are not replaced with real stimuli (kept as simple shapes for practice)

---

## Block Structure

### Phase 1: Study Phase

- Participants view **20 images** sequentially
- **No responses required**
- Each image is shown for **1 second**
- **Jittered fixations** (0.25-0.75 seconds) appear between images
- Image presentation timings are recorded (onset, offset, duration, fixation duration)
- Participants are instructed to remember each image carefully

### Phase 2: Recognition Phase

Each of the 20 trials follows this structure:

1. **Pre-trial Fixation Cross**: 0.5 seconds (fixed duration, shown before each image)
2. **Image Presentation**: Shows either the studied image or its lure (50% chance each) for 1.0 second (fixed duration)
   - Image remains visible until participant responds or timeout (7 seconds)
3. **Participant Rating**: Rate memory confidence on a continuous slider
   - Click anywhere on the slider line to set rating (not dragging)
   - Click SUBMIT button to confirm
   - Timeout: 7 seconds (random answer selected if timeout)
4. **AI Partner Rating**: AI partner also rates the image
   - AI RT: Log-normal distribution (mu=0.5, sigma=0.3), capped at 5.0 seconds
   - Animation shows AI's slider clicking and submitting
5. **Collaboration Decision**: Participant decides to STAY or SWITCH
   - Timeout: 7 seconds (random decision selected if timeout)
6. **Outcome Feedback**: Shows correctness and curator scoring
   - "Correct!" (green) or "Incorrect" (red)
   - "The in-house curator scored this image: X points"
   - Display duration: ~1.5 seconds
7. **Jittered Fixation**: 0.25-0.75 seconds (uniform random distribution) between trials
   - Distribution: `random.uniform(0.25, 0.75)` - each jitter independently drawn
   - Shown as fixation cross during inter-trial interval
   - **No jitter after the last trial** in each block
   - **19 jittered fixations per block** (between 20 trials)

---

## Trial Procedure Details

### Participant Rating (Slider Response)

- **Continuous slider** with no midpoint shown
- **Left side** = OLD (studied)
- **Right side** = NEW (not studied)
- Slider position indicates **confidence level**
- Participants must:
  1. Click anywhere on the slider line to set their rating
  2. Click the "SUBMIT" button to confirm
  3. Cannot submit if slider hasn't been clicked (still at center)
- **Timeout**: 7 seconds (random answer selected if timeout)

### AI Partner Rating

- AI partner also rates each image on the same slider
- **AI Response Time (RT)**: Drawn from a log-normal distribution (jittered)
- **AI Confidence**: Drawn from a Gaussian distribution
- **AI Accuracy**: Varies by block (see below)
- Animation shows AI's slider clicking (handle appears at chosen position) and clicking submit

### Turn-Taking Manipulation

- **Participant always goes first** in all blocks
- The AI partner responds after the participant in every trial

### AI Accuracy Manipulation

- **Reliable blocks**: ~75% correct (Blocks 1 and 4)
- **Unreliable blocks**: ~25% correct (Blocks 2, 3, and 5)
- **Block structure**:
  - Block 1: Reliable (0.75), Participant first
  - Block 2: Unreliable (0.25), Participant first
  - Block 3: Unreliable (0.25), Participant first
  - Block 4: Reliable (0.75), Participant first
  - Block 5: Unreliable (0.25), Participant first

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

- **After each trial**: "The in-house curator scored this image: X points"
  - Points are based on Euclidean distance from correct answer (1.0 - distance)
  - Range: 0.0 to 1.0 points per trial

- **End of each block**: "The in-house curator scored this collection X points out of a total of 10 points!"
  - Block points are scaled from the block's maximum (20 trials × 1.0 max = 20) to a 10-point scale
  - Formula: `(block_points / 20) × 10`

- **End of experiment**: "The in-house curator scored this collection X points out of a total of 10 points!"
  - Total experiment points are scaled from maximum (100 trials × 1.0 max = 100) to a 10-point scale
  - Formula: `(total_points / 100) × 10`

---

## Outcome Screen

### Trial Outcome

1. **Correctness Feedback**: 
   - "Correct!" (green) or "Incorrect" (red)
   - Points earned this trial displayed

2. **Social Reinforcement** (50% chance if switched):
   - Separate screen: "Thanks for working with [partner name]! You receive a [X] bonus point!"
   - The partner name (Amy or Ben) is dynamically displayed based on the current block
   - The bonus amount (0.50-0.75) is randomly determined each time
   - Shown regardless of whether switching made the answer correct or incorrect

---

## Data Collection

### Data Recorded Each Trial

#### Participant Data
- **Response Time (RT)**: Time to click on slider and submit
- **Decision Commitment Time**: Time when submit button is clicked
- **Slider Stop Time**: Time when slider value is set (clicked)
- **Old-New Slider Value**: Final slider position (0.0 = OLD, 1.0 = NEW)
- **Switch/Stay Decision**: Choice made
- **Switch/Stay RT**: Time to make decision
- **Decision Onset Time**: Time when switch/stay screen appears
- **Accuracy Outcome**: Whether final answer was correct
- **Euclidean Distance**: Participant slider to ground truth

#### AI Partner Data
- **AI RT**: Response time (log-normal distribution)
- **AI Decision Time**: Time when AI "commits" to rating
- **AI Slider Value**: AI's confidence rating
- **AI Accuracy**: Whether AI was correct or incorrect
- **Euclidean Distance**: AI slider to ground truth

#### Interaction Data
- **Euclidean Distance**: Between participant and AI slider values
- **Outcome Time**: Time when outcome screen appears
- **Timeout Flags**: Whether participant timed out on slider or switch/stay decision

#### Trial Metadata
- **Block Number**: Which block (0 = practice, 1-5 = experimental)
- **Trial Number**: Trial within block
- **Trial Type**: "studied" or "lure"
- **Image Path**: Which image was shown
- **Participant First**: Always True (participant always responds first)
- **Time from Experiment Start**: Elapsed time since experiment began

### Data Storage

- **CSV files updated after each trial** (not each block)
- **Study Phase Data**: Saved to `recognition_study_[participant_id]_[timestamp].csv`
- **Trial Data**: Saved to `recognition_trials_[participant_id]_[timestamp].csv`
- **Summary Data**: Total task time saved to `recognition_summary_[participant_id]_[timestamp].csv`

---

## Practice Block

### Structure

- **3 trials** (practice only)
- **3 shape stimuli**: Green circle, red circle, blue circle (for sequential presentation)
- **Practice recognition trials**:
  - Trial 1: Green circle (participant rates only)
  - Trial 2: Red circle (AI rates first, then participant rates)
  - Trial 3: Blue square (full trial: participant rates, AI rates, switch/stay decision)
- **Practice flow**:
  1. Welcome message with Amy's story and picture
  2. Sequential presentation of 3 shapes (green circle, red circle, blue circle), each for 1.5 seconds with fixations between
  3. Transition screen: "Now let's see how well you recall the objects you've seen!"
  4. Trial 1: Green circle - participant rates only
  5. Trial 2: Red circle - shows "Amy is confident they've seen this before", AI clicks "all the way on the old" side, then participant rates
  6. Trial 3: Blue square - shows "now, work with Amy", participant rates, then AI clicks "all the way on the old" side (incorrectly, as it's a new square), then participant performs switch/stay decision, outcome shown
- **Outcome explanations**: For practice trials, outcomes explicitly explain the score (e.g., "You were 67% incorrect!" for a score of 0.33)
- **Slider instruction**: Explicitly states "Note: You will click (not drag) on the slider to set your rating."

### Purpose

- Familiarize participants with task mechanics
- Practice using the slider (click-only, not dragging)
- Understand collaboration decisions
- Learn about the curator scoring system
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
  - Bonus points and rewards
- **Rules reminder** before experimental blocks (2 pages)
- **Color-coded headers** for easy navigation
- **Formatted text** with emphasis on key concepts

### Leaderboard

- **Displayed at end of experiment**
- Shows participant ranked 1-5 out of 10 (randomly assigned rank)
- **Anonymized participant names**: P01-P10
- Participant shown as "[ID] (you)" at their rank
- Based on total points earned across all experimental blocks

### Transition Screens

- **Initial screen**: "Hello & welcome to the social memory game! Pay careful attention to the text on the screen"
- **Before practice**: Welcome message with Amy's story and picture
- **After practice**: Transition message explaining the real work begins with Amy organizing photographs
- **Between blocks**: Partner switch messages when partner changes (Amy ↔ Ben), or brief break message
- **Final screen**: Shows cumulative curator scoring, leaderboard, total task time, and thank you message

---

## Randomization and Counterbalancing

### Stimulus Randomization

- **100 stimuli** organized by category, with items shuffled within each category
- **Each block contains exactly 2 items from each of the 10 categories (20 stimuli per block)**
- Each stimulus appears exactly once across all experimental blocks
- **First recognition image** is never the same as the last study image
- Items within each block are randomized for presentation order

### Trial Randomization

- **Studied vs. lure**: Each of the 20 block images appears once in recognition (10 studied, 10 lures)
- **Trial order**: Randomized within each block
- **Image assignments**: Randomly assigned to studied/lure conditions

### Block Counterbalancing

- **Turn-taking**: Participant always goes first in all blocks
- **AI Accuracy**: Fixed order - Blocks 1, 4 reliable (~75%); Blocks 2, 3, 5 unreliable (~25%)
- **Structure**: 
  - Block 1: Reliable, Participant first
  - Block 2: Unreliable, Participant first
  - Block 3: Unreliable, Participant first
  - Block 4: Reliable, Participant first
  - Block 5: Unreliable, Participant first

### AI Behavior Randomization

- **AI RT**: Log-normal distribution (mu=0.5, sigma=0.3, capped at 5.0s)
- **AI Confidence**: Gaussian distribution
  - Mean = 0.7 if correct, 0.3 if incorrect
  - Std = 0.15
  - Biased toward OLD/NEW based on ground truth
- **AI Accuracy**: Controlled at block level (0.75 or 0.25)

---

## Technical Details

### Timing Specifications

#### Study Phase Timing
- **Image duration**: 1.0 second per image (fixed, no jitter)
- **Fixation jitter**: 
  - Duration: 0.25-0.75 seconds (uniform random distribution)
  - Distribution: `random.uniform(0.25, 0.75)`
  - Appears between images (after image N, before image N+1)
  - No fixation before first image
  - 9 fixations per block (between 10 images)
- **Total study phase duration**: Approximately 10-14.5 seconds per block
  - 10 images × 1.0 second = 10 seconds
  - 9 fixations × (0.25-0.75 seconds average 0.5) = ~4.5 seconds

#### Recognition Phase Timing
- **Pre-trial fixation**: 0.5 seconds (fixed duration, shown before each image)
- **Image duration**: 1.0 second per image (fixed, no jitter)
  - Image remains visible until participant responds or timeout (7 seconds)
- **Inter-trial jitter**: 
  - Duration: 0.25-0.75 seconds (uniform random distribution)
  - Distribution: `random.uniform(0.25, 0.75)` - each jitter independently drawn
  - Appears between trials (after trial N completes, before trial N+1 starts)
  - Shown as fixation cross during jitter period
  - **No jitter after the last trial** in each block
  - **19 jittered fixations per block** (between 20 trials)

#### Participant Response Timeouts
- **Slider response**: 7.0 seconds (fixed)
  - Image remains visible until timeout or submission
  - Random answer selected if timeout (not center position)
- **Switch/Stay decision**: 7.0 seconds (fixed)
  - Decision screen remains visible until timeout or button click
  - Random decision (STAY or SWITCH) selected if timeout

#### AI Response Timing
- **AI RT distribution**: Log-normal
  - Underlying normal: mu = 0.5, sigma = 0.3
  - Mean RT: ~1.5-2.5 seconds
  - Maximum RT: 5.0 seconds (capped)
  - Formula: `min(np.random.lognormal(0.5, 0.3), 5.0)`

#### Outcome Feedback Timing
- Outcome screen displayed immediately after decision
- Shows correctness ("Correct!" or "Incorrect") and curator scoring message
- Visual feedback duration: ~1.5 seconds (fixed)
- Brief pause before next trial (jittered fixation: 0.25-0.75 seconds)

#### General Timing Notes
- All timeouts: Random answer/decision selected if timeout occurs
- All timeout flags recorded in CSV data
- All reaction times recorded from stimulus onset to response
- Timestamps recorded in Unix time (seconds since epoch)

### Response Timeouts

- **Slider response**: 7 seconds
- **Switch/Stay decision**: 7 seconds
- If timeout: Random answer selected, timeout flag recorded in data

### Window and Display

- **Window size**: 1280×720 pixels
- **Fullscreen**: Disabled during development
- **Window focus**: Automatically activated on macOS
- **Initial screen**: "Click anywhere to begin" ensures window focus

### File Management

- **Placeholder stimuli**: Generated automatically if missing or incorrect
- **Data files**: Created with participant ID and timestamp
- **Incremental saving**: Data saved after each trial for robustness

---

## Experimental Design Considerations

### Manipulations

1. **Turn-Taking**: Who responds first (participant vs. AI)
2. **AI Accuracy**: High (~75%) vs. Low (~25%) accuracy blocks

### Research Questions

- How does turn order affect collaboration decisions?
- How does AI accuracy influence trust and switching behavior?
- What strategies do participants use to maximize points?
- How does confidence level affect point earning?

### Potential Limitations

- **Not fully counterbalanced**: Some manipulation combinations may occur more frequently
- **AI accuracy**: Fixed at block level, not trial level

---

## Instructions for Participants

### Key Points Emphasized

1. **Confidence matters**: Slider position indicates confidence level
2. **Points = accuracy + confidence**: More confident + correct = more points
3. **Collaboration**: Can switch even if both agree (to match confidence levels)
4. **Bonus points**: Randomly awarded 50% of the time when switching
5. **Leaderboard**: See how you compare to others at the end

### Practice Instructions

- "This is just for practice, but go as quick as you can!"
- Practice uses 5 shape stimuli
- Same mechanics as experimental blocks

---

## Summary

This task examines social decision-making in a memory recognition context, where participants collaborate with an AI partner whose accuracy and turn order vary across blocks. The design allows investigation of how these factors influence collaboration strategies, trust, and performance optimization.

