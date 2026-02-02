# Social Recognition Memory Task

This repository contains the full PsychoPy implementation, documentation, and example data outputs for the **Social Recognition Memory with Human–AI Collaboration** experiment.

## Repository Contents

### 1. Core Task Code

#### **`social_recognition_memory_task.py`**
Main PsychoPy script for the entire experiment.

- Runs the full procedure:  
  - Instructions  
  - Practice block  
  - 5 experimental blocks (20 trials each)  
  - Study phase → Recognition phase → Switch/Stay decision → Outcome feedback  
  - AI turn-taking (participant-first vs. AI-first)  
  - AI accuracy manipulation (reliable ~75% vs. unreliable ~25%)  
  - Social bonus feedback  
  - Block-end questionnaire  
  - Leaderboard screen
- Saves trial-level, block-level, and questionnaire data as CSV files.

#### **`localizer.py`**
Localizer task script for category verification.

- Shows all 200 images from the STIMULI folder (100 Image + 100 Lure versions) in random order
- **Image presentation timing**:
  - Each image displayed for **1.0 second** (fixed duration)
  - **0.5 second pause** between images (no jitter)
  - Questions asked at trials 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200 (every 10th trial)
- At every 10th trial, asks a category question: "Was the last object a [category]?"
- Category is inferred from the folder name (e.g., BIG_ANIMAL → "big animal")
- **Question timing**: No timeout - participant must respond (YES/NO buttons)
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
- Social feedback  
- Block-level survey responses  

Use this file when analyzing data.

---


### 3. Demo / Media

#### **`Demo.mp4`**
Short screen recording from early version demonstrating:

- Study trial flow  
- Recognition slider interaction  
- AI slider animation  
- Switch/Stay decision screen  
- Outcome feedback  

---

### 4. Example Data Outputs

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

#### **`recognition_questions_*.csv`**
Block-end questionnaire data.  
Each row = one block.

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
Stimuli used in the task. From the THINGS dataset







