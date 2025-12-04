# Social Recognition Memory Task with Human–AI Collaboration

## Overview

This task examines how participants collaborate with an AI partner during a recognition memory task. Participants study images and then test their memory by rating images as "OLD" (studied) or "NEW" (not studied), while collaborating with an AI partner who also provides ratings.

**Duration**: 35-45 minutes (50-60 minutes for slower participants)  
**Structure**: 10 blocks × 10 trials = 100 total trials  
**Response Timeout**: 7 seconds per response

---

## Task Structure

### Overall Design

- **10 experimental blocks**, each containing:
  - **Study Phase**: View 10 images sequentially (no responses required)
  - **Recognition Phase**: 10 trials testing memory with AI collaboration

- **1 practice block** (5 trials) to familiarize participants with the task

---

## Stimuli

### Image Pairs

- Each block uses **10 studied images**, each paired with a corresponding **lure version**
  - Example: `IMAGE_1.png` pairs with `LURE_1.png`
  - Each image appears exactly once across all 10 experimental blocks (100 unique images total)

### Placeholder Stimuli (Development Phase)

- **100 distinct colored shapes** generated as placeholders
- **Studied items**: Circles (50% of pairs)
- **Lure items**: Squares (50% of pairs)
- **Swapped pairs**: For 50% of pairs, squares are studied items and circles are lures
- Final stimuli will be provided by Nuttida and replace placeholders

### Recognition Trial Distribution

- **50% studied images** (targets): Original images from study phase
- **50% lure images**: Similar but not identical versions
- Each of the 10 studied images from a block appears exactly once in recognition (5 as studied, 5 as lures)

---

## Block Structure

### Phase 1: Study Phase

- Participants view **10 images** sequentially
- **No responses required**
- Images appear one at a time
- Participants are instructed to remember each image carefully

### Phase 2: Recognition Phase

Each of the 10 trials follows this structure:

1. **Image Presentation**: Shows either the studied image or its lure (50% chance each)
2. **Participant Rating**: Rate memory confidence on a continuous slider
3. **AI Partner Rating**: AI partner also rates the image
4. **Collaboration Decision**: Participant decides to STAY or SWITCH
5. **Outcome Feedback**: Shows correctness and points earned

---

## Trial Procedure Details

### Participant Rating (Slider Response)

- **Continuous slider** with no midpoint shown
- **Left side** = OLD (studied)
- **Right side** = NEW (not studied)
- Slider position indicates **confidence level**
- Participants must:
  1. Click and drag the slider handle
  2. Click the "SUBMIT" button to confirm
  3. Cannot submit if slider hasn't moved from center
- **Timeout**: 7 seconds (random answer selected if timeout)

### AI Partner Rating

- AI partner also rates each image on the same slider
- **AI Response Time (RT)**: Drawn from a log-normal distribution (jittered)
- **AI Confidence**: Drawn from a Gaussian distribution
- **AI Accuracy**: Varies by block (see below)
- Animation shows AI's slider moving and clicking submit

### Turn-Taking Manipulation

Blocks alternate which agent responds first:

- **Block Type A** (5 blocks): **Participant responds first**
- **Block Type B** (5 blocks): **AI responds first**

This creates two social-decision conditions to examine how turn order affects collaboration.

### AI Accuracy Manipulation

- **Overall accuracy**: ~50% across all blocks
- **Block-level variation**:
  - **High accuracy blocks**: ~75% correct (5 blocks)
  - **Low accuracy blocks**: ~25% correct (5 blocks)
- Accuracy is randomized across blocks and co-occurs with turn-taking manipulation
- **Note**: Not fully counterbalanced (some combinations may occur more frequently)

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

### Bonus Points

- **Social Collaboration Bonus**: 0.5 bonus points
- **Condition**: Awarded 50% of the time when participant switches (randomly determined)
- **Independent of correctness**: Bonus can be awarded even if switching leads to incorrect answer

### Point Display

- **After each trial**: Shows points earned for that trial only
- **End of each block**: Shows total points earned / maximum possible points
  - Maximum excludes social feedback bonus
  - Total includes correctness points + social feedback bonuses

---

## Outcome Screen

### Trial Outcome

1. **Correctness Feedback**: 
   - "Correct!" (green) or "Incorrect" (red)
   - Points earned this trial displayed

2. **Social Reinforcement** (50% chance if switched):
   - Separate screen: "Thanks for working with your partner! You receive a 0.5 bonus point!"
   - Shown regardless of whether switching made the answer correct or incorrect

---

## Data Collection

### Data Recorded Each Trial

#### Participant Data
- **Response Time (RT)**: Time to move slider and submit
- **Decision Commitment Time**: Time when submit button is clicked
- **Slider Stop Time**: Time when slider handle is released
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
- **Social Feedback**: Whether bonus was given (True/False)
- **Social Feedback Time**: Time when social feedback screen appears
- **Outcome Time**: Time when outcome screen appears
- **Timeout Flags**: Whether participant timed out on slider or switch/stay decision

#### Trial Metadata
- **Block Number**: Which block (0 = practice, 1-10 = experimental)
- **Trial Number**: Trial within block
- **Trial Type**: "studied" or "lure"
- **Image Path**: Which image was shown
- **Participant First**: Whether participant or AI responded first
- **Time from Experiment Start**: Elapsed time since experiment began

### Data Storage

- **CSV files updated after each trial** (not each block)
- **Study Phase Data**: Saved to `recognition_study_[participant_id]_[timestamp].csv`
- **Trial Data**: Saved to `recognition_trials_[participant_id]_[timestamp].csv`
- **Questions Data**: Saved to `recognition_questions_[participant_id]_[timestamp].csv`
- **Summary Data**: Total task time saved to `recognition_summary_[participant_id]_[timestamp].csv`

---

## Practice Block

### Structure

- **5 trials** (instead of 10)
- **5 shape stimuli** from PLACEHOLDERS folder
- Same task structure as experimental blocks:
  - Study phase (5 images)
  - Recognition phase (5 trials)
  - Collaboration with AI partner
  - Outcome feedback

### Purpose

- Familiarize participants with task mechanics
- Practice using the slider
- Understand collaboration decisions
- **Note**: Practice stimuli will not be replaced with final stimuli

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

### Block-End Questions

After each block (including practice), participants answer 2 questions:

1. **Multiple Choice** (7 seconds):
   - "What were you trying to maximize?"
   - Options: Correctness, Bonus points, Both, Other

2. **Slider Question** (7 seconds):
   - "How much did you trust your partner?"
   - Scale: "Not at all" (left) to "Completely" (right)
   - 0.0 to 1.0 value recorded

### Leaderboard

- **Displayed at end of experiment**
- Shows participant ranked 1-5 out of 10 (randomly assigned rank)
- **Anonymized participant names**: P01-P10
- Participant shown as "[ID] (you)" at their rank
- Based on total points earned across all experimental blocks

### Transition Screens

- **Between study and recognition phases**: "STUDY PHASE COMPLETE! Now switching to the recognition phase..."
- **Between blocks**: "Block X complete! Take a short break."
- **Final screen**: Shows total task time and thank you message

---

## Randomization and Counterbalancing

### Stimulus Randomization

- **100 stimuli** shuffled and divided into 10 unique groups (10 per block)
- Each stimulus appears exactly once across all experimental blocks
- **First recognition image** is never the same as the last study image

### Trial Randomization

- **Studied vs. lure**: Each of the 10 block images appears once in recognition (5 studied, 5 lures)
- **Trial order**: Randomized within each block
- **Image assignments**: Randomly assigned to studied/lure conditions

### Block Counterbalancing

- **Turn-taking**: 5 blocks participant-first, 5 blocks AI-first (randomized order)
- **AI Accuracy**: 5 blocks high accuracy (~75%), 5 blocks low accuracy (~25%)
- **Co-occurrence**: Both manipulations randomized together (not fully counterbalanced)

### AI Behavior Randomization

- **AI RT**: Log-normal distribution (mu=0.5, sigma=0.3, capped at 5.0s)
- **AI Confidence**: Gaussian distribution
  - Mean = 0.7 if correct, 0.3 if incorrect
  - Std = 0.15
  - Biased toward OLD/NEW based on ground truth
- **AI Accuracy**: Controlled at block level (0.75 or 0.25)

---

## Technical Details

### Response Timeouts

- **Slider response**: 7 seconds
- **Switch/Stay decision**: 7 seconds
- **Block-end questions**: 7 seconds each
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
- **Social feedback**: Randomly awarded (50% chance), not tied to actual performance

---

## Instructions for Participants

### Key Points Emphasized

1. **Confidence matters**: Slider position indicates confidence level
2. **Points = accuracy + confidence**: More confident + correct = more points
3. **Collaboration**: Can switch even if both agree (to match confidence levels)
4. **Bonus points**: Randomly awarded 50% of the time when switching
5. **Questions**: Quick questions at end of each block
6. **Leaderboard**: See how you compare to others at the end

### Practice Instructions

- "This is just for practice, but go as quick as you can!"
- Practice uses 5 shape stimuli
- Same mechanics as experimental blocks

---

## Summary

This task examines social decision-making in a memory recognition context, where participants collaborate with an AI partner whose accuracy and turn order vary across blocks. The design allows investigation of how these factors influence collaboration strategies, trust, and performance optimization.

