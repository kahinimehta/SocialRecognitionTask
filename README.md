# Social Recognition Memory Task

This repository contains the full PsychoPy implementation, documentation, and example data outputs for the **Social Recognition Memory with Human–AI Collaboration** experiment.

## Repository Contents

### 1. Core Task Code

#### **`social_recognition_memory_task.py`**
Main PsychoPy script for the entire experiment.

- Generates placeholder stimuli (colored circles/squares) if actual images are not provided.
- Runs the full procedure:  
  - Instructions  
  - Practice block  
  - 10 experimental blocks  
  - Study phase → Recognition phase → Switch/Stay decision → Outcome feedback  
  - AI turn-taking (participant-first vs. AI-first)  
  - AI accuracy manipulation (~75% vs. ~25%)  
  - Social bonus feedback  
  - Block-end questionnaire  
  - Leaderboard screen
- Saves trial-level, block-level, and questionnaire data as CSV files.

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
Short screen recording demonstrating:

- Study trial flow  
- Recognition slider interaction  
- AI slider animation  
- Switch/Stay decision screen  
- Outcome feedback  

---

### 4. Example Data Outputs

These are example CSVs produced by running the task with test parameters. Your real participants' files will follow identical formats.

---

#### **`recognition_study_isa_20251203_235247.csv`**
Study-phase data.  
Each row = one study trial.

---

#### **`recognition_trials_isa_20251203_235247.csv`**
Recognition-phase (main task) data.  
Each row = one recognition trial.

---

#### **`recognition_questions_kini_20251204_003…csv`**
Block-end questionnaire data.  
Each row = one block.


---
Stimuli used: 
- From the THINGS dataset
- https://drive.google.com/drive/u/1/folders/1sEeXyOnSymaFE0GUYKuhYLn6rYs_XY1A




When running the task, your generated CSVs will follow this format:

