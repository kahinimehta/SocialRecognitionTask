# Social Recognition Memory Task

This repository contains the full PsychoPy implementation, documentation, and example data outputs for the **Social Recognition Memory with Human–AI Collaboration** experiment.

## Narrative Context

The experiment is framed as a photography studio collaboration task. Participants join a small photography studio where **Amy**, a professional photographer, is preparing images for an upcoming exhibition. Participants help sort through large sets of images and decide which ones truly belong in the collection. During the experiment, participants may work with **Amy** (reliable partner) or **Ben** (another assistant who may rely on different cues, unreliable partner). The task is framed as helping an "in-house curator" score the images, with scoring feedback presented as "The in-house curator scored this image: X points" rather than direct point earnings.

## Repository Contents

### 1. Core Task Code

#### **`social_recognition_memory_task.py`**
Main PsychoPy script for the entire experiment.

- Runs the full procedure:  
  - Instructions  
  - Practice block  
  - 10 experimental blocks (10 trials each)  
  - Study phase → Recognition phase → Switch/Stay decision → Outcome feedback  
  - AI turn-taking (randomized within blocks: AI goes first on 5 random trials out of 10 per block)  
  - AI accuracy manipulation (reliable exactly 75% vs. unreliable exactly 25% using deterministic thresholds)  
  - Leaderboard screen (5 players, participant ranked 2 out of 5; continue button positioned to avoid overlap with text)
- Saves trial-level and block-level data as CSV files.

#### **`localizer.py`**
Localizer task script for category verification.

- Shows all 200 images from the STIMULI folder (100 Image + 100 Lure versions) in random order
- **Image presentation timing**:
  - Starts with a **fixation cross** (jittered 0.25-0.75 seconds)
  - Each image displayed for **0.5 seconds** (fixed duration, no jitter)
  - **Jittered fixation cross** appears between images: **0.25-0.75 seconds** (uniform random distribution)
  - Fixation jitter: `random.uniform(0.25, 0.75)` - each fixation independently drawn
  - Fixation appears before EVERY image, including the first image
  - Questions asked at trials 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200 (every 10th trial)
- At every 10th trial, asks a category question: "Was the last object a [category]?"
- **Question design**: Exactly 50% of questions ask about the correct category (the category of the last object shown), exactly 50% ask about a random incorrect category. Uses pre-generated randomized sequence to ensure exactly 10 correct and 10 random questions (out of 20 total) in randomized order.
- Category names are converted from folder names to natural language (e.g., BIG_ANIMAL → "big animal", smallobject → "small object")
- **Question timing**: **10.0 second timeout** - if participant doesn't respond within 10 seconds, the question times out and the task continues
  - **Note**: This differs from the main task, which uses 7.0 second timeouts for slider and switch/stay decisions
- Records participant responses (YES/NO) and accuracy
- Saves data to CSV file: `localizer_[participant_id]_[timestamp].csv`
- **Example filename**: `localizer_kini_20260130_232131.csv`
- Supports both touch screen and click/mouse input modes
- Skips file saving if "test" is in participant name
- **See `CSV_VARIABLES_DOCUMENTATION.md` for complete variable definitions**

---

### 2. Documentation Files

#### **`TASK_DESCRIPTION.md`**
High-level design document outlining:

- Experimental rationale  
- Block structure  
- Timing and trial flow  
- Stimulus format  
- Human–AI collaboration mechanics  
- Scoring, feedback, and reward structure  
- Survey questions and condition logic  

Use this file to understand the conceptual design.

---

#### **`CSV_VARIABLES_DOCUMENTATION.md`**
Complete dictionary of every variable saved in the output CSVs.

Defines all logged fields, including:

- Trial metadata  
- Participant slider values, RTs, commit times  
- AI responses, RTs, correctness  
- Switch/Stay choices and timings  
- Distances from ground truth  

Use this file when analyzing data.

---

#### **`script.md`**
Experimenter script for running the task with participants.

This file contains:

- **Quick start instructions** for running the main experiment and localizer task
- **Complete script** with all text that appears on screen during the experiment
- **What to say** guidance for experimenters at each stage
- **Troubleshooting tips** and technical notes

The script is organized by screen/phase, showing exactly what participants will see and what experimenters should say. Use this file when conducting sessions to ensure consistent instructions across participants.

---


### 3. Demo / Media (needs to be updated)

#### **`Demo.mp4`**
Short screen recording from early version demonstrating:

- Study trial flow  
- Recognition slider interaction  
- AI slider animation  
- Switch/Stay decision screen  
- Outcome feedback  

---

### 4. Example Data Outputs (needs to be updated)

These are example CSVs produced by running the task with test parameters. Your real participants' files will follow identical formats.

---

#### **`recognition_study_*.csv`**
Study-phase data.  
Each row = one study trial.

---

#### **`recognition_trials_*.csv`**
Recognition-phase (main task) data.  
Each row = one recognition trial.

---

#### **`recognition_summary_*.csv`**
Summary of experiment time

---

#### **`localizer_*.csv`**
Localizer task data.  
- **File naming**: `localizer_[participant_id]_[timestamp].csv`
- **Example**: `localizer_kini_20260130_232131.csv`
- **Structure**: Each row = one image presentation (200 total: 100 Image + 100 Lure)
- **Question trials**: Every 10th trial (trials 10, 20, 30, ..., 200) includes category question data
- **Variables**: Includes stimulus metadata (number, object name, category, stimulus type), presentation timestamps, and question responses (for question trials)
- **See `CSV_VARIABLES_DOCUMENTATION.md` for complete variable definitions**

---

#### **`STIMULI`**
Stimuli used in the task. From the THINGS dataset. Also included with STIMULI: `ImagevsLure.pdf` to visualize all stimuli & manual ratings `Image_Similarity_Rater.csv` of how visually similar the images are.







