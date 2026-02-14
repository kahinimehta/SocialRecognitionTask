# Social Recognition Memory Task

This repository contains the full PsychoPy implementation, documentation, and example data outputs for the **Social Recognition Memory with Human–AI Collaboration** experiment.

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
Complete dictionary of every variable saved in the output CSVs.

Defines all logged fields, including:

- Trial metadata  
- Participant slider values, RTs, commit times (all variables written for analysis flexibility)  
- AI responses, RTs, correctness  
- Switch/Stay choices and timings  
- Distances from ground truth  
- **Neural data triggers**: Photodiode (0.03 × 0.01) at far left (-0.75, -0.48); in both tasks and both modes; white baseline, flashes black (TTL) then white per event. Off only during name entry; after name, **every screen change, stimulus change, and response** triggers photodiode+TTL (same as localizer). TTL sent at exact flip moment via `callOnFlip` (triggers and diode change simultaneously). All triggers logged to `recognition_ttl_events_*.csv` and `localizer_ttl_events_*.csv`. See `CSV_VARIABLES_DOCUMENTATION.md` for complete event list.  

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

#### **`recognition_ttl_events_*.csv`**
Chronological log of every TTL trigger (timestamp + event_type) for neural data alignment.

---

#### **`localizer_*.csv`**
Localizer task data (object questions every 10th trial, 50/50 correct/random incorrect object, feedback at end only).

---

#### **`localizer_ttl_events_*.csv`**
Chronological log of every TTL trigger (timestamp + event_type) for the localizer task.

---

#### **`STIMULI`**
Stimuli used in the task. From the THINGS dataset. Also included with STIMULI: `ImagevsLure.pdf` to visualize all stimuli & manual ratings of stimulus similarity by Kahini: `Image_Similarity_Rater.csv`. Lures were AI generated via OpenAI, and aimed to keep difficulty at a medium level across all images as far as possible, but a fairly balanced mix of high/low/medium similarity was obtained. 






