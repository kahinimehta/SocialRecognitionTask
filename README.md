# Social Recognition Memory Task

This repository contains the full PsychoPy implementation, documentation, and example data outputs for the **Social Recognition Memory with Human–AI Collaboration** experiment.

**Documentation**: `TASK_DESCRIPTION.md` is the canonical task specification. `CSV_VARIABLES_DOCUMENTATION.md` documents all CSV fields and neural event mapping. `script.md` is the experimenter script.

## Narrative Context

The experiment is framed as a photography studio collaboration task. It is **Amy's shop**; she is the professional photographer preparing images for an exhibition. **Carly** is Amy's assistant and **only appears during the practice block**—she walks participants through the training (using the same image as Amy). The **experimental blocks** use **Amy** (reliable partner) or **Ben** (another assistant who may rely on different cues, unreliable partner). Participants help sort through large sets of images and decide which ones truly belong in the collection. The task is framed as helping an "in-house curator" score the images, with scoring feedback presented as "The in-house curator scored this image: X points" rather than direct point earnings.

## Repository Contents

### 1. Core Task Code

#### **`social_recognition_memory_task.py`**
Main PsychoPy script for the entire experiment.

#### **`localizer.py`**
Localizer task script for object verification.

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
Complete dictionary of every variable saved in all CSVs (6 task output files + 1 reference file).

Defines all logged fields: trial metadata, participant slider values, RTs, commit times, AI responses, switch/stay decisions, distances from ground truth, and neural data (photodiode/TTL triggers). Covers `recognition_study`, `recognition_trials`, `recognition_summary`, `recognition_ttl_events`, `localizer`, `localizer_ttl_events`, and `Image_Similarity_Rater.csv`. All output CSVs are written incrementally with flush to disk, preserving data if the task is interrupted.

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

Example CSVs (`recognition_study_*`, `recognition_trials_*`, `recognition_summary_*`, `recognition_ttl_events_*`, `localizer_*`, `localizer_ttl_events_*`) produced by running the task with test parameters. During runs, data saves to `../LOG_FILES/`. See `CSV_VARIABLES_DOCUMENTATION.md` for column definitions, file structure, and neural event mapping.

### 5. Stimuli

**`STIMULI`** folder: THINGS dataset (Image + Lure versions). Includes `ImagevsLure.pdf` and `Image_Similarity_Rater.csv` (reference file documenting stimulus pair similarity). Stimulus structure: `TASK_DESCRIPTION.md`.

**`PLACEHOLDERS`** folder: Practice shapes (green/red/blue circles, blue square) and fallback placeholder images used when full stimuli are unavailable or for practice trials. 






