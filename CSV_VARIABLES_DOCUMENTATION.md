# CSV Variables Documentation

Complete reference for CSV output and neural event mapping. Task design and experimental logic: `TASK_DESCRIPTION.md`. Experimenter script: `script.md`.

## Neural Data Logging (Photodiode & TTL)

Photodiode (0.03 × 0.01): **Touch screen** at (-0.70, -0.48); **keyboard** at (-0.75, -0.48). **Present in both tasks** (main experiment and localizer). **White baseline** when nothing is happening. At each event the patch **flashes black** (TTL sent) **then white**—a quick transition via `win.flip()`; it does not stay black. **Every flash is accompanied by a TTL trigger** via parallel port (Windows/Linux; default 0x0378; `PARALLEL_PORT_ADDRESS` to override).

**When photodiode is active** (main task and localizer): Photodiode is **off only during participant name entry**. After name entry, photodiode and TTL are **on for every screen change, stimulus change, and response**—same as localizer. BEGIN screen, instruction onsets, CONTINUE clicks, block summaries, etc. all trigger flashes.

**Keyboard mode only**: A 17 ms (~1 frame at 60 Hz) delay is inserted between the black and white flips for every photodiode event. This ensures the black frame is actually displayed and prevents vsync coalescing. Touch screen mode skips this delay.

**TTL timing**: TTL is sent via PsychoPy `callOnFlip` at the exact moment of each black flip (when the photodiode patch flashes black). Every flash event triggers exactly one TTL pulse.

**TTL event logging**: Every TTL trigger is logged to a dedicated CSV file (`recognition_ttl_events_*.csv` for the main task, `localizer_ttl_events_*.csv` for the localizer). Each row contains `timestamp` (Unix time when TTL fired) and `event_type` (string matching the CSV variable name, e.g., `study_fixation_onset_trigger`, `participant_commit_trigger`). These files provide a complete chronological record of all neural triggers for alignment with recording equipment. **All CSV files (including TTL) are written incrementally** (one row per event/trial) with immediate flush to disk, so data is preserved if the task is interrupted.

### Complete Photodiode Flash Events (Main Task)

| Event | CSV Variable | File |
|-------|--------------|------|
| BEGIN screen onset | `start_task_onset` | TTL events |
| BEGIN button click | `begin_click` | TTL events |
| Fixation onset | `study_fixation_onset_trigger`, `recognition_fixation_onset_trigger` | study, trials |
| Fixation offset | `study_fixation_offset_trigger`, `recognition_fixation_offset_trigger` | study, trials |
| Study image onset | `study_image_onset_trigger` | study |
| Study image offset | `study_image_offset_trigger` | study |
| Recognition image onset | `recognition_image_onset_trigger` | trials |
| Recognition image offset | `recognition_image_offset_trigger` | trials |
| Partner "[Name] is rating..." (AI starts deciding) | `partner_rating_onset_trigger` | trials |
| Partner slider handle appears at final position (AI has settled, before submit) | `partner_slider_settled_trigger` | trials |
| Partner "[Name] rates: OLD/NEW" | `partner_rating_complete_trigger` | trials |
| Participant slider submit | `participant_commit_trigger` | trials |
| Switch/stay screen onset | `switch_stay_trigger` | trials |
| Participant STAY/SWITCH click | `switch_stay_response_trigger` | trials |
| Outcome screen | `outcome_trigger` | trials |
| Timeout warning "Time's up!" onset | `timeout_warning_onset` | TTL events |
| Timeout warning offset (warning removed) | `timeout_warning_offset` | TTL events |

All listed events trigger photodiode+TTL and are logged to `recognition_ttl_events_*.csv`. Per-trial CSVs log only trial-associated triggers.

### Complete Photodiode Flash Events (Localizer)

| Event | CSV Variable | File |
|-------|--------------|------|
| Fixation onset | `localizer_fixation_onset_trigger` | localizer |
| Fixation offset | `localizer_fixation_offset_trigger` | localizer |
| Image onset | `localizer_image_onset_trigger` | localizer |
| Image offset | `localizer_image_offset_trigger` | localizer |
| Question screen onset | `question_trigger` | localizer |
| Participant YES/NO answer | `question_answer_trigger` | localizer |
| Timeout warning "Time's up!" onset | `timeout_warning_onset` | TTL events |
| Timeout warning offset (warning removed) | `timeout_warning_offset` | TTL events |

**Between-trial events** (instruction onset, BEGIN): Photodiode flashes but not logged to per-image CSV.

### CSV Trigger Variables

All `*_trigger` variables record the **Unix timestamp** when the photodiode flashed black (TTL fired). All trial-associated flashes are logged. Use these to align behavioral data with neural recordings:

| Task | Variables | Event |
|------|-----------|-------|
| **Study** | `study_fixation_onset_trigger` | Fixation appeared (photodiode/TTL) |
| **Study** | `study_fixation_offset_trigger` | Fixation removed (photodiode/TTL) |
| **Study** | `study_image_onset_trigger` | Study image appeared (photodiode/TTL) |
| **Study** | `study_image_offset_trigger` | Study image removed (photodiode/TTL) |
| **Recognition** | `recognition_fixation_onset_trigger` | Pre-trial fixation appeared |
| **Recognition** | `recognition_fixation_offset_trigger` | Pre-trial fixation removed |
| **Recognition** | `recognition_image_onset_trigger` | Recognition image appeared |
| **Recognition** | `recognition_image_offset_trigger` | Recognition image removed (before slider) |
| **Recognition** | `partner_rating_onset_trigger` | "[Partner] is rating..." appeared (AI starts deciding) |
| **Recognition** | `partner_slider_settled_trigger` | Partner's slider handle appeared at final position (AI settled on decision, before submit) |
| **Recognition** | `partner_rating_complete_trigger` | "[Partner] rates: OLD/NEW" appeared |
| **Recognition** | `participant_commit_trigger` | Participant submitted slider (photodiode/TTL) |
| **Recognition** | `switch_stay_trigger` | Switch/stay decision screen onset |
| **Recognition** | `switch_stay_response_trigger` | Participant clicked STAY or SWITCH (photodiode/TTL) |
| **Recognition** | `outcome_trigger` | Outcome feedback onset |
| **Localizer** | `localizer_fixation_onset_trigger` | Fixation appeared (photodiode/TTL) |
| **Localizer** | `localizer_fixation_offset_trigger` | Fixation removed (photodiode/TTL) |
| **Localizer** | `localizer_image_onset_trigger` | Image appeared (photodiode/TTL) |
| **Localizer** | `localizer_image_offset_trigger` | Image removed (photodiode/TTL) |
| **Localizer** | `question_trigger` | Question screen onset (photodiode/TTL) |
| **Localizer** | `question_answer_trigger` | Participant answered YES/NO (photodiode/TTL at tap or key press) |

### TTL Events CSV (recognition_ttl_events, localizer_ttl_events)

The TTL events files list every photodiode/TTL trigger in chronological order. **Columns**: `timestamp`, `event_type`

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | Float (Unix) | Time when TTL fired (same as photodiode black flash) |
| `event_type` | String | Event identifier (matches CSV variable names where applicable) |

**Main task event types**: `study_fixation_onset_trigger`, `study_fixation_offset_trigger`, `study_image_onset_trigger`, `study_image_offset_trigger`, `recognition_fixation_onset_trigger`, `recognition_fixation_offset_trigger`, `recognition_image_onset_trigger`, `recognition_image_offset_trigger`, `participant_commit_trigger`, `switch_stay_trigger`, `switch_stay_response_trigger`, `outcome_trigger`, `instruction_onset`, `instruction_continue`, `block_summary_onset`, `block_summary_continue`, `start_task_onset`, `begin_click`, `welcome_onset`, `motor_response`, `practice_fixation_onset`, `practice_fixation_offset`, `partner_rating_onset`, `partner_slider_settled_trigger`, `partner_rating_complete`, `timeout_warning_onset`, `timeout_warning_offset`

**Localizer event types**: `localizer_fixation_onset_trigger`, `localizer_fixation_offset_trigger`, `localizer_image_onset_trigger`, `localizer_image_offset_trigger`, `question_trigger`, `question_answer_trigger`, `instruction_onset`, `instruction_continue`, `timeout_warning_onset`, `timeout_warning_offset`

### When the Photodiode Is *Not* Shown

- Input method selection screen (`temp_win`)
- Participant name entry screen (photodiode enabled immediately after name is submitted)
- Any screen before the main experiment window is active

---

## File Structure

The experiment generates four CSV files:
1. **recognition_study_[participant_id]_[timestamp].csv** - Study phase data
2. **recognition_trials_[participant_id]_[timestamp].csv** - Recognition phase data
3. **recognition_summary_[participant_id]_[timestamp].csv** - Experiment summary (total time)
4. **recognition_ttl_events_[participant_id]_[timestamp].csv** - TTL trigger log (every photodiode flash with timestamp and event type)

The localizer task generates two CSV files (both written incrementally for touch and keyboard modes):
5. **localizer_[participant_id]_[timestamp].csv** - Localizer behavioral data (trial-by-trial)
6. **localizer_ttl_events_[participant_id]_[timestamp].csv** - TTL trigger log (each event written as it occurs)

**File saving locations**:
- All files are saved to `../LOG_FILES/` directory (created automatically if it doesn't exist)
- File saving is skipped if "test" (case-insensitive) is in the participant name

**CSV format notes**:
- Empty cells indicate `None`/missing values
- `image_path` format may vary by OS (Windows: backslashes; macOS/Linux: forward slashes)
- Column order may vary; use headers to identify columns

---

## Study Phase CSV Variables

**Columns (recognition_study)**: `block`, `phase`, `trial`, `image_path`, `study_fixation_onset_trigger`, `study_fixation_offset_trigger`, `fixation_duration`, `study_image_onset_trigger`, `study_image_offset_trigger`, `image_duration`

---

### `block`
- **Type**: Integer
- **Description**: Block number (1-10 only). The study phase CSV contains only experimental blocks; the practice block (block 0) uses a different procedure and does not appear in this file.
- **Example**: `1`, `2`, `10`

### `phase`
- **Type**: String
- **Description**: Phase identifier, always "study" for study phase data
- **Example**: `"study"`

### `trial`
- **Type**: Integer
- **Description**: Trial number within the study phase (1-indexed)
- **Example**: `1`, `2`, `3`

### `image_path`
- **Type**: String
- **Description**: Full path to the studied image file (always IMAGE_X.png, never lures)
- **Example**: `"PLACEHOLDERS/IMAGE_5.png"`

### `study_fixation_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the fixation cross first appeared (photodiode flashed black, TTL fired)
- **Note**: Fixation appears before EVERY image, including the first image
- **Example**: `1764818170.5`

### `study_fixation_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the fixation cross was removed (photodiode flashed black, TTL fired)
- **Example**: `1764818171.0`

### `fixation_duration`
- **Type**: Float (seconds)
- **Description**: Duration of the fixation cross before this image
- **Distribution**: Uniform random between 0.25-0.75 seconds (`random.uniform(0.25, 0.75)`)
- **Jitter**: Each fixation duration is independently drawn from uniform distribution
- **Note**: Fixation appears before EVERY image, including the first image
- **Example**: `0.523456789`, `0.312345`, `0.678901`

### `study_image_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the study image first appeared (photodiode flashed black, TTL fired)
- **Example**: `1764818171.2572181`

### `study_image_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the study image was removed from display (photodiode flashed black, TTL fired)
- **Example**: `1764818172.2572181`

### `image_duration`
- **Type**: Float (seconds)
- **Description**: Duration the image was displayed (always 1.0 second, fixed - no jitter)
- **Example**: `1.0`

---

## Recognition Phase CSV Variables

**Columns (recognition_trials)** — photodiode/trigger variables: `recognition_fixation_onset_trigger`, `recognition_fixation_offset_trigger`, `recognition_image_onset_trigger`, `recognition_image_offset_trigger`, `partner_rating_onset_trigger`, `partner_slider_settled_trigger`, `partner_rating_complete_trigger`, `participant_commit_trigger`, `switch_stay_trigger`, `switch_stay_response_trigger`, `outcome_trigger` (plus existing RTs, accuracy, etc.)

---

### `block`
- **Type**: Integer
- **Description**: Block number (0 = practice block, 1-10 = experimental blocks)
- **Example**: `0`, `1`, `2`, `10`

### `trial`
- **Type**: Integer
- **Description**: Trial number within the recognition phase (1-indexed)
- **Example**: `1`, `2`, `3`

### `phase`
- **Type**: String
- **Description**: Phase identifier, always "recognition" for recognition phase data
- **Example**: `"recognition"`

### `trial_type`
- **Type**: String
- **Description**: Type of trial - either "studied" (original Image version) or "lure" (Lure version of the same object)
- **Example**: `"studied"`, `"lure"`

### `is_studied`
- **Type**: Boolean
- **Description**: True if this is a studied image (original), False if it's a lure
- **Example**: `True`, `False`

### `image_path`
- **Type**: String
- **Description**: Full path to the image shown (Image_XXX.jpg for studied, Lure_XXX.jpg for lures)
  - **Important**: For lures, this is the lure version of the **same object** that was studied (e.g., if `Image_041.jpg` was studied, the lure would be `Lure_041.jpg`, not a random lure from a different object)
  - **Practice block**: Paths point to PLACEHOLDERS (e.g., `PLACEHOLDERS/IMAGE_1.png`)
  - **Path format**: May vary by OS (backslashes on Windows, forward slashes on macOS/Linux)
- **Example**: `"STIMULI/FRUIT/Apple/Image_041.jpg"`, `"STIMULI/FRUIT/Apple/Lure_041.jpg"`, `"PLACEHOLDERS/IMAGE_1.png"`

### `recognition_fixation_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the pre-trial fixation first appeared (photodiode flashed black, TTL fired)
- **Example**: `1764818191.994316`

### `recognition_fixation_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the pre-trial fixation was removed (photodiode flashed black, TTL fired)
- **Example**: `1764818191.994316`

### `recognition_image_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the recognition image first appeared (photodiode flashed black, TTL fired)
- **Example**: `1764818192.494316`

### `recognition_image_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the recognition image was removed before the slider (photodiode flashed black, TTL fired)
- **Example**: `1764818193.494316`

### `participant_first`
- **Type**: Boolean
- **Description**: True if participant responded first in this trial, False if AI responded first. Turn order is randomized within each block (AI goes first on 5 random trials out of 10 per block).
- **Example**: `True`, `False`

---

## Participant Response Variables

### `participant_slider_value`
- **Type**: Float (0.0 to 1.0)
- **Description**: Participant's confidence rating on the slider
  - Values closer to 0.0 = OLD (studied)
  - Values closer to 1.0 = NEW (lure)
  - 0.5 = center/uncertain
- **Example**: `0.3142361111111111`, `0.7890563378785669`

### `participant_rt`
- **Type**: Float (seconds)
- **Description**: Participant's reaction time from when the slider screen appeared to when they clicked SUBMIT. *Not* measured from image onset—the slider appears after the image is shown for 1.0 second (participant-first trials) or after the image + AI animation (AI-first trials).
- **Timeout**: If participant doesn't respond within 7.0 seconds, random answer selected and RT = 7.0
- **Example**: `4.68976616859436`, `2.981760025024414`, `7.0` (timeout)

### `participant_commit_time`
- **Type**: Float (Unix timestamp)
- **Description**: Time when participant clicked the SUBMIT button
- **Example**: `1764818198.3314402`

### `participant_commit_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as the participant submitted their slider rating. Matches the exact screen change for neural alignment. `None` if participant timed out.
- **Example**: `1764818198.3314402`, `None`

### `partner_rating_onset_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as "[Partner name] is rating..." appeared—i.e., when the AI/partner starts making a decision. Use for neural alignment to AI decision onset.
- **Example**: `1764818198.5`, `None`

### `partner_slider_settled_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as the partner's slider handle appeared at its final position—i.e., when the AI has settled on their decision, before the submit button is clicked. Use for neural alignment to AI decision commitment. `None` for practice trial 1 (no AI partner).
- **Example**: `1764818199.5`, `None`

### `partner_rating_complete_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as "[Partner name] rates: OLD/NEW" appeared—i.e., when the AI/partner's final rating was shown.
- **Example**: `1764818200.2`, `None`

### `participant_slider_timeout`
- **Type**: Boolean
- **Description**: True if participant timed out (didn't respond within 7.0 seconds)
- **Timeout duration**: 7.0 seconds (fixed, no jitter)
- **Example**: `True`, `False`

### `participant_slider_stop_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when participant last clicked/tapped on the slider to set their rating (final position). None if they never clicked on the slider. All slider-related variables are written to the CSV for analysis; the **photodiode/TTL fires only on submit** (commit time), not on slider movements.
- **Note**: For touch screens, this may be different from `participant_slider_decision_onset_time` if the participant taps multiple times to adjust their rating.
- **Derived measure**: Time from image onset to last slider click = `participant_slider_stop_time - recognition_image_trigger` (when not None)
- **Example**: `1764818195.5`, `None`

### `participant_slider_decision_onset_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when participant first clicked/tapped on the slider bar (decision onset - when they start making their decision). 
  - **Touch screen version**: First time they tap the slider bar (may be different from `participant_slider_stop_time` if they tap multiple times to adjust)
  - **Computer/mouse version**: Same as `participant_slider_stop_time` (when they click the slider, decision onset equals the click time)
- **Example**: `1764818195.2`, `None`

### `participant_slider_click_times`
- **Type**: String (comma-separated timestamps) or empty string
- **Description**: All times (Unix timestamps) when participant interacted with the slider.
  - **Touch screen**: Each tap on the slider bar; first tap = `participant_slider_decision_onset_time`.
  - **Keyboard**: Each LEFT/RIGHT arrow-key press (participants press repeatedly; holding keys doesn't work).
  - Stored as comma-separated string (quoted in CSV when containing commas). Empty string if none.
- **Example**: `"1764818195.2,1764818195.5,1764818196.1"`, `"1764818195.5"`, `""`

---

## AI/Partner Response Variables

### `ai_slider_value`
- **Type**: Float (0.0 to 1.0) or None
- **Description**: AI/partner's confidence rating on the slider
  - Values closer to 0.0 = OLD (studied)
  - Values closer to 1.0 = NEW (lure)
  - `None` for practice trial 1 (no AI response)
  - **Amy (reliable)**: Confidence correlated with correctness. When correct—0.75–1.0 on correct side (OLD: 0–0.25, NEW: 0.75–1.0); when wrong—0.5–0.75 or 0.25–0.5 depending on wrong side. Uniform random within ranges.
  - **Ben (unreliable)**: Random within chosen category (0–0.25 for OLD, 0.75–1.0 for NEW)—uninformative about correctness
- **Example**: `0.6569413750565093`, `0.3563797294608513`, `None`

### `ai_rt`
- **Type**: Float (seconds)
- **Description**: AI's reaction time (drawn from log-normal distribution, capped at 5 seconds)
- **Distribution**: Log-normal with underlying normal parameters: mu = 0.5, sigma = 0.3
- **Mean RT**: Approximately 1.5-2.5 seconds
- **Maximum RT**: 5.0 seconds (capped)
- **Jitter**: Each trial draws independently from the distribution
- **Formula**: `min(np.random.lognormal(0.5, 0.3), 5.0)`
- **Example**: `2.2821904016769365`, `1.2902461381415058`, `4.5`

### `ai_decision_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when AI internally made its decision (right after make_decision() call)
- **Note**: `None` for practice trial 1 (no AI response)
- **Example**: `1764818198.338135`, `None`

### `ai_slider_display_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when AI's slider handle appears at the final position (when the slider value is visually set)
- **Note**: `None` for practice trial 1 (no AI response)
- **Example**: `1764818200.155891`, `None`

### `ai_final_slider_display_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when AI's submit button was clicked in the animation (visual commit time)
- **Note**: `None` for practice trial 1 (no AI response)
- **Example**: `1764818201.255891`, `None`

### `ai_correct`
- **Type**: Boolean or None
- **Description**: True if the AI's categorical decision (OLD vs NEW, based on slider &lt;0.5 or ≥0.5) matched ground truth for this trial, False otherwise.
- **Implementation**: Determined by the pre-generated block accuracy sequence (see `ai_reliability`). The AI's slider value is generated to match this; i.e., correct trials get confidence on the correct side (OLD: 0–0.25, NEW: 0.75–1.0), incorrect trials on the wrong side.
- **Note**: `None` for practice trial 1 (no AI response)
- **Example**: `True`, `False`, `None`

### `ai_reliability`
- **Type**: Float (0.0 to 1.0)
- **Description**: Block-level target AI accuracy rate (same for all trials within the block). This is the AI partner's configured reliability, not trial-varying.
  - `0.75` = Amy (reliable), 8/10 correct
  - `0.35` = Ben (unreliable), 4/10 correct
  - `0.5` = Practice (Carly)
- **Note**: Block assignment in `TASK_DESCRIPTION.md`. `ai_correct` per trial reflects the pre-generated sequence.
- **Example**: `0.75`, `0.35`, `0.5`

---

## Switch/Stay Decision Variables

### `switch_stay_decision`
- **Type**: String
- **Description**: Participant's decision - "stay" (keep own answer) or "switch" (use partner's answer)
- **Example**: `"stay"`, `"switch"`

### `switch_rt`
- **Type**: Float (seconds) or None
- **Description**: Reaction time from when decision screen appeared to when participant clicked STAY or SWITCH
- **Note**: `None` for practice trials 1 and 2 (no switch/stay decision screen shown)
- **Example**: `2.829475164413452`, `1.4260890483856201`, `None`

### `switch_commit_time`
- **Type**: Float (Unix timestamp)
- **Description**: Time when participant clicked STAY or SWITCH button
- **Example**: `1764818206.231731`

### `switch_timeout`
- **Type**: Boolean or None
- **Description**: True if participant timed out on switch/stay decision (didn't respond within 7.0 seconds)
- **Timeout duration**: 7.0 seconds (fixed, no jitter)
- **Note**: `None` for practice trials 1 and 2 (no switch/stay decision screen shown)
- **Example**: `True`, `False`, `None`

### `switch_stay_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the switch/stay screen first appeared (photodiode/TTL trigger moment — question, image, scale, markers, STAY/SWITCH buttons)
- **Note**: `None` for practice trials 1 and 2 (no switch/stay decision screen shown)
- **Example**: `1764818203.4`, `None`

### `switch_stay_response_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as the participant clicked STAY or SWITCH. Matches the exact screen change for neural alignment. `None` for practice trials 1 and 2, or if participant timed out.
- **Example**: `1764818206.2`, `None`

---

## Final Answer and Accuracy Variables

### `final_answer`
- **Type**: Float (0.0 to 1.0)
- **Description**: Final answer used for scoring (participant's value if stayed, AI's value if switched)
- **Example**: `0.0`, `0.3563797294608513`

### `used_ai_answer`
- **Type**: Boolean
- **Description**: True if final answer came from AI (participant switched), False if from participant (stayed)
- **Example**: `True`, `False`

### `ground_truth`
- **Type**: Float
- **Description**: Correct answer (0.0 for studied/OLD, 1.0 for lure/NEW)
- **Example**: `0.0`, `1.0`

### `participant_accuracy`
- **Type**: Boolean
- **Description**: True if final answer was correct (within 0.5 of ground truth), False otherwise
- **Example**: `True`, `False`

---

## Distance Metrics

### `euclidean_participant_to_truth`
- **Type**: Float
- **Description**: Euclidean distance between participant's slider value and ground truth
  - Lower values = closer to correct answer
- **Example**: `0.3142361111111111`, `0.0`

### `euclidean_ai_to_truth`
- **Type**: Float or None
- **Description**: Euclidean distance between AI's slider value and ground truth
  - Lower values = closer to correct answer
- **Note**: `None` for practice trial 1 (no AI response)
- **Example**: `0.6569413750565093`, `0.0`, `None`

### `euclidean_participant_to_ai`
- **Type**: Float
- **Description**: Euclidean distance between participant's and AI's slider values
  - Lower values = more similar ratings
- **Example**: `0.6569413750565093`, `0.042143618349740175`

---

## Outcome Variables

### `outcome_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the outcome screen (Correct/Incorrect) first appeared (photodiode flashed black, TTL fired).
- **Example**: `1764818206.237804`, `None`

### `block_start_time`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the block started (when study phase began)
- **Example**: `1764818000.0`

### `block_end_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the block ended (after block summary screen)
- **Note**: `None` for practice block (block 0) - practice block timing not tracked
- **Example**: `1764818300.0`, `None`

### `block_duration_seconds`
- **Type**: Float (seconds)
- **Description**: Total duration of the block in seconds (from start of study phase to end of block summary)
- **Example**: `300.5`

### `block_duration_minutes`
- **Type**: Float (minutes) or None
- **Description**: Total duration of the block in minutes
- **Note**: `None` for practice block (block 0) - practice block timing not tracked
- **Example**: `5.008`, `None`

### `points_earned`
- **Type**: Float
- **Description**: Points this trial; formula `1.0 - euclidean_distance(final_answer, ground_truth)`; range 0.0–1.0. Logged at full precision; display rounded to 1 decimal.
- **Example**: `0.6857638888888889`, `0.0`, `1.0`

---

## Summary CSV Variables

The **recognition_summary_[participant_id]_[timestamp].csv** file contains overall experiment summary data.

**Columns (recognition_summary)**: `participant_id`, `experiment_start_time`, `experiment_end_time`, `total_task_time_seconds`, `total_task_time_minutes`

---

### `participant_id`
- **Type**: String
- **Description**: Participant identifier
- **Example**: `"kini"`, `"P001"`

### `experiment_start_time`
- **Type**: Float (Unix timestamp)
- **Description**: Time when experiment started (after initial instructions)
- **Example**: `1764818000.0`

### `experiment_end_time`
- **Type**: Float (Unix timestamp)
- **Description**: Time when experiment ended (after final instructions)
- **Example**: `1764820800.0`

### `total_task_time_seconds`
- **Type**: Float (seconds)
- **Description**: Total duration of the experiment in seconds
- **Example**: `2800.5`

### `total_task_time_minutes`
- **Type**: Float (minutes)
- **Description**: Total duration of the experiment in minutes
- **Example**: `46.675`

---

## Notes

- **Trigger variables**: Every `*_trigger` = Unix timestamp when photodiode flashed black (TTL fired). Slider fires on submit only, not on movement.
- All timestamps: Unix time. Slider values: 0.0 (OLD) to 1.0 (NEW).
- **Timeout settings (Main Task only)**: Timeout variables are True if the participant didn't respond within the time limit:
  - Slider and switch/stay decisions: **7.0 seconds** (fixed)
  - **Note**: The localizer task uses a different timeout (10.0 seconds for questions) - see Localizer Task section below
- The experiment saves data incrementally after each trial, not just at the end
---

## Localizer Task CSV Variables

The **localizer_[participant_id]_[timestamp].csv** file contains data from the localizer task, where participants view 200 images (100 Image + 100 Lure versions) in random order and answer object questions at every 10th image. **Written trial-by-trial incrementally for both touch-screen and keyboard modes**—each row is flushed to disk immediately, preserving data if the task crashes or is interrupted.

### `participant_id`
- **Type**: String
- **Description**: Participant identifier
- **Example**: `"P001"`, `"test_user"`

### `trial`
- **Type**: Integer
- **Description**: Trial number representing the presentation order (1-indexed, 1-200)
- **Presentation order**: Each image is logged in the order it appears (trial 1 = first image shown, trial 2 = second image shown, etc.)
- **Question trials**: Questions are asked at trials 10, 20, 30, ..., 200 (every 10th trial)
- **Example**: `1`, `10`, `20`, `50`, `200`

### `stimulus_number`
- **Type**: Integer (1-100)
- **Description**: The stimulus number of the image that was shown (from Image_001.jpg to Image_100.jpg)
- **Example**: `1`, `42`, `100`

### `object_name`
- **Type**: String
- **Description**: Name of the object folder containing the image (e.g., "Apple", "Car", "Elephant")
- **Example**: `"Apple"`, `"Car"`, `"Elephant"`

### `category`
- **Type**: String
- **Description**: Category folder name that the image belongs to
- **Possible values**: `"BIG_ANIMAL"`, `"BIG_OBJECT"`, `"BIRD"`, `"FOOD"`, `"FRUIT"`, `"INSECT"`, `"SMALL_ANIMAL"`, `"SMALL_OBJECT"`, `"VEGETABLE"`, `"VEHICLE"`
- **Example**: `"FRUIT"`, `"BIG_ANIMAL"`

### `stimulus_type`
- **Type**: String
- **Description**: Type of stimulus shown
- **Possible values**: `"Image"` (original image), `"Lure"` (lure version)
- **Example**: `"Image"`, `"Lure"`

### `is_lure`
- **Type**: Boolean
- **Description**: True if this is a lure stimulus, False if it's an original Image
- **Example**: `True`, `False`

### `image_path`
- **Type**: String
- **Description**: Full path to the image file that was displayed
- **Example**: `"STIMULI/biganimal/Elephant/Image_042.jpg"`, `"STIMULI/smallobject/Key/Lure_042.jpg"`

### `presentation_time`
- **Type**: String (datetime format)
- **Description**: Timestamp when the image was displayed (human-readable format)
- **Format**: `"YYYY-MM-DD HH:MM:SS.ffffff"`
- **Example**: `"2026-01-30 23:21:31.123456"`

### `localizer_fixation_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the fixation cross first appeared (photodiode flashed black, TTL fired)
- **Note**: Fixation appears before EVERY image, including the first image
- **Example**: `1764818170.5`

### `localizer_fixation_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the fixation cross was removed (photodiode flashed black, TTL fired)
- **Example**: `1764818170.75`

### `fixation_duration`
- **Type**: Float (seconds)
- **Description**: Duration the fixation cross was displayed (jittered 0.25-0.75 seconds)
- **Distribution**: `random.uniform(0.25, 0.75)` - each fixation independently drawn
- **Example**: `0.42`, `0.68`, `0.31`

### `localizer_image_onset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the image first appeared (photodiode flashed black, TTL fired)
- **Example**: `1764818171.2572181`

### `localizer_image_offset_trigger`
- **Type**: Float (Unix timestamp)
- **Description**: Time when the image was removed from display (photodiode flashed black, TTL fired)
- **Note**: Images are displayed for exactly 0.5 seconds
- **Example**: `1764818171.7572181`

### `is_question_trial`
- **Type**: Boolean
- **Description**: True if this trial included an object question (trials 10, 20, 30, ..., 200), False otherwise
- **Example**: `True`, `False`

### `question_object`
- **Type**: String or None
- **Description**: The object name that was asked about in the question (e.g., "Giraffe", "Elephant")
- **Question design**: 50% of trials ask about the correct object (matches `object_name`); 50% ask about a **random incorrect object** selected from all other objects in the stimulus set. Pre-generated sequence ensures exactly 10 correct and 10 incorrect questions in randomized order.
- **Example**: `"Giraffe"`, `"Elephant"`, `"Apple"` (may or may not match the actual `object_name` of the image)

### `question_text`
- **Type**: String or None
- **Description**: Full text of the question asked to the participant (only populated for question trials)
- **Format**: "Was the last object a [object]?" or "Was the last object an [object]?" where object name is lowercase
- **Article selection**: Uses "a" or "an" based on whether the object starts with a vowel sound
- **Example**: `"Was the last object a giraffe?"`, `"Was the last object an elephant?"`, `"Was the last object an apple?"`, `None`

### `question_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the object question first appeared (photodiode flashed black, TTL fired)
- **Note**: Only populated for question trials (every 10th trial). `None` for non-question trials.
- **Example**: `1764818180.1234567`, `None`

### `question_answer_trigger`
- **Type**: Float (Unix timestamp) or None
- **Description**: Time when the photodiode flashed black (TTL fired) as the participant answered YES or NO (tap or key press)
- **Note**: Only populated for question trials where participant answered (not timeout). `None` for non-question trials or timeout.
- **Example**: `1764818181.5`, `None`

### `answer`
- **Type**: Boolean, String, or None
- **Description**: Participant's response to the question
- **Possible values**: 
  - `True` (YES) for question trials where participant answered YES
  - `False` (NO) for question trials where participant answered NO
  - `"TIMEOUT"` if participant timed out (10.0 second timeout)
  - Empty/`None` for non-question trials
- **Example**: `True`, `False`, `"TIMEOUT"`, empty

### `correct_answer`
- **Type**: Boolean or None
- **Description**: The correct answer to the question
- **Question design**: 
  - `True` if the question asks about the correct object (matches the actual `object_name` of the image)
  - `False` if the question asks about an incorrect object (does not match the actual `object_name` of the image)
  - `None` for non-question trials
- **Example**: `True`, `False`, `None`

### `correct`
- **Type**: Boolean or None
- **Description**: Whether the participant's answer matches the correct answer
- **Possible values**: `True` (correct), `False` (incorrect), `None` (non-question trial or timeout)
- **Example**: `True`, `False`, `None`

### `timed_out`
- **Type**: Boolean or None
- **Description**: Whether the participant timed out on the question
  - `True` if participant didn't respond within 10.0 seconds
  - `False` if participant responded before timeout
  - `None` for non-question trials
- **Timeout duration**: 10.0 seconds (fixed)
- **Example**: `True`, `False`, `None`

### `response_time`
- **Type**: Float (seconds) or None
- **Description**: Time taken to respond to the question, measured from question_trigger to button press
- **Example**: `1.234`, `2.567`, `None`

### `answer_click_time`
- **Type**: Float (Unix timestamp) or None
- **Description**: Absolute timestamp when the participant clicked their answer (in seconds since epoch, high precision)
- **Note**: Only populated for question trials where participant answered (YES/NO button click or y/n key press). `None` for non-question trials or if participant timed out.
- **Example**: `1764818181.1234567`, `None`

---
