from psychopy import visual, core, event, gui
import random
import string
import csv
from datetime import datetime

#Participant Info
exp_info = {'Participant ID': '', 'Age': '', 'Gender': ['Male', 'Female', 'Other', 'Prefer not to say']}
dlg = gui.DlgFromDict(dictionary=exp_info, title='Stroop Prime Experiment')
if not dlg.OK:
    core.quit()


win = visual.Window(fullscr=True, color='grey', units='pix')
colors = ['green', 'red']
keys = {'green': 'z', 'red': 'm'}
prime_types = ['congruent', 'incongruent', 'neutral']
stroop_types = ['congruent', 'incongruent']
trial_types = ['stroop', 'color_block']


STIMULUS_HEIGHT = 60  

# Random string masks
def generate_random_mask():
    length = random.randint(5, 6)
    consonants = 'BCDFGHJKLMNPQRSTVWXYZ'  
    return ''.join(random.choice(consonants) for _ in range(length))

#Data Storage
data_file = f"stroop_data_{exp_info['Participant ID']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsv"
fieldnames = ['participant_id', 'age', 'gender', 'block', 'trial', 'trial_type', 'prime_type', 'stroop_type',
              'prime_word', 'target_word', 'target_color', 'response', 'rt', 'correct']

with open(data_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

all_data = []


intro_text = """Welcome to the Experiment!

In this experiment, you will see either colored words or colored blocks on the screen.
Your task is to identify the COLOR that word/block is displayed in.

Instructions:
- Press 'Z' if the word/block is displayed in GREEN
- Press 'M' if the word/block is displayed in RED
- Respond as quickly and accurately as possible
- You can press 'ESC' at any time to exit the experiment

First, you will complete a short practice round to familiarize yourself with the task.
The experiment will begin after that. 
There will 8 blocks with 60 trials each.
Feel free to take short breaks between blocks.

Press SPACEBAR to begin the practice round."""

intro_stim = visual.TextStim(win, text=intro_text, color='white', height=30, wrapWidth=800)
intro_stim.draw()
win.flip()
intro_keys = event.waitKeys(keyList=['space', 'escape'])
if intro_keys and 'escape' in intro_keys:
    win.close()
    core.quit()


class StroopTrial:
    def __init__(self, trial_type, prime_type, stroop_type, color, block_num, trial_num, is_practice=False):
        self.trial_type = trial_type 
        self.prime_type = prime_type
        self.stroop_type = stroop_type 
        self.color = color
        self.block_num = block_num
        self.trial_num = trial_num
        self.is_practice = is_practice
        self.prime_word = self.get_prime_word()
       
        if self.trial_type == 'stroop':
            self.target_word, self.target_color = self.get_target()
        else: 
            self.target_word = None
            self.target_color = self.color
       
    def get_prime_word(self):
        if self.is_practice:
            return ''
        if self.prime_type == 'neutral':
            return ''
        elif self.prime_type == 'congruent':
            return self.color.upper()
        elif self.prime_type == 'incongruent':
            other_color = [c for c in colors if c != self.color][0]
            return other_color.upper()
   
    def get_target(self):
        if self.stroop_type == 'congruent':
            return self.color.upper(), self.color
        else:
            other_color = [c for c in colors if c != self.color][0]
            return other_color.upper(), self.color
   
    def run(self):
        event.clearEvents()

        # Fixation cross
        fixation = visual.TextStim(win, text='+', color='white', height=STIMULUS_HEIGHT)
        fixation.draw()
        win.flip()
        core.wait(0.2)
           
        # First mask
        mask_text = generate_random_mask()
        mask = visual.TextStim(win, text=mask_text, color='white', height=STIMULUS_HEIGHT)
        mask.draw()
        win.flip()
        core.wait(0.071)
       
        # Prime
        if self.prime_word:
            prime = visual.TextStim(win, text=self.prime_word, color='white', height=STIMULUS_HEIGHT)
            prime.draw()
            win.flip()
            core.wait(0.043)  
       
        # Second mask
        mask_text = generate_random_mask()
        mask = visual.TextStim(win, text=mask_text, color='white', height=STIMULUS_HEIGHT)
        mask.draw()
        win.flip()
        core.wait(0.071)
       
        # Target stimulus
        if self.trial_type == 'stroop':
            target = visual.TextStim(win, text=self.target_word, color=self.target_color, height=STIMULUS_HEIGHT)
        else: 
            target = visual.Rect(win, width=200, height=100, fillColor=self.target_color, lineColor=self.target_color)
       
        target.draw()
        win.flip()
       
        event.clearEvents()
        
        # Wait for response while target is on screen
        timer = core.Clock()
        keys_pressed = event.waitKeys(keyList=['z', 'm', 'escape'], timeStamped=timer)
        
        # 100ms blank screen after response
        win.flip()  
        core.wait(0.1)
       
        if keys_pressed and any('escape' in key for key in keys_pressed):
            return 'escape'
       
        if keys_pressed:
            response, rt = keys_pressed[0]
            correct = response == keys[self.color]
           
            trial_data = {
                'participant_id': exp_info['Participant ID'],
                'age': exp_info['Age'],
                'gender': exp_info['Gender'],
                'block': self.block_num,
                'trial': self.trial_num,
                'trial_type': self.trial_type,
                'prime_type': self.prime_type if not self.is_practice else 'none',
                'stroop_type': self.stroop_type if self.trial_type == 'stroop' else 'N/A',
                'prime_word': self.prime_word,
                'target_word': self.target_word if self.target_word else 'COLOR_BLOCK',
                'target_color': self.target_color,
                'response': response,
                'rt': rt,
                'correct': correct
            }
           
            if not self.is_practice:
                all_data.append(trial_data)
                with open(data_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                    writer.writerow(trial_data)
           
            print(f"Block {self.block_num}, Trial {self.trial_num} ({self.trial_type}): Target: {self.target_word or 'COLOR_BLOCK'} ({self.target_color}), Response: {response}, RT: {rt:.3f}, Correct: {correct}")
           
            return {'status': 'continue', 'correct': correct, 'rt': rt}
        else:
            return {'status': 'continue', 'correct': False, 'rt': None}

def generate_practice_trials():
    """Generate 5 practice trials without primes"""
    trials = []
    
    trial_specs = [
        ('stroop', 'neutral', 'congruent', 'green'),
        ('stroop', 'neutral', 'incongruent', 'red'),
        ('color_block', 'neutral', 'congruent', 'green'),
        ('stroop', 'neutral', 'congruent', 'red'),
        ('color_block', 'neutral', 'congruent', 'red')
    ]
    
    random.shuffle(trial_specs)
    
    for i, (trial_type, prime_type, stroop_type, color) in enumerate(trial_specs):
        trial_num = i + 1
        trials.append(StroopTrial(trial_type, prime_type, stroop_type, color, 0, trial_num, is_practice=True))
    
    return trials

def generate_block_trials(block_num):
    """Generate 60 trials per block"""
    trials = []
   

    stroop_trials = []
    all_stroop_combinations = []
    for prime in prime_types:  
        for stroop in stroop_types:  
            for color in colors: 
                all_stroop_combinations.append(('stroop', prime, stroop, color))
   
    
    for _ in range(3):   
        stroop_trials.extend(all_stroop_combinations)
    selected_stroop = random.sample(stroop_trials, 30)
   

    color_block_trials = []
    all_colorblock_combinations = []
    for prime in prime_types:  
        for color in colors:  
            all_colorblock_combinations.append(('color_block', prime, 'congruent', color))
   
    for _ in range(5):  
        color_block_trials.extend(all_colorblock_combinations)
   
    all_trial_specs = selected_stroop + color_block_trials
    random.shuffle(all_trial_specs)
   
    for i, (trial_type, prime_type, stroop_type, color) in enumerate(all_trial_specs):
        trial_num = i + 1
        trials.append(StroopTrial(trial_type, prime_type, stroop_type, color, block_num, trial_num))
   
    return trials

experiment_escaped = False

practice_trials = generate_practice_trials()
practice_correct = 0

for trial in practice_trials:
    result = trial.run()
    if result['status'] == 'escape':
        experiment_escaped = True
        break
    if result['correct']:
        practice_correct += 1

#Practice feedback
if not experiment_escaped:
    practice_accuracy = (practice_correct / len(practice_trials)) * 100
    
    practice_feedback = f"""Practice Round Complete!

You got {practice_correct} out of {len(practice_trials)} correct ({practice_accuracy:.1f}% accuracy).

Remember:
- Press 'Z' for GREEN words/blocks
- Press 'M' for RED words/blocks
- Press 'ESC' to exit
- Respond as quickly and accurately as possible

Press SPACEBAR to begin the main experiment."""
    
    feedback_stim = visual.TextStim(win, text=practice_feedback, color='white', height=30, wrapWidth=700)
    feedback_stim.draw()
    win.flip()
    feedback_keys = event.waitKeys(keyList=['space', 'escape'])
    if feedback_keys and 'escape' in feedback_keys:
        experiment_escaped = True

# Main experiment
for block in range(1, 9):  # 8 blocks
    if experiment_escaped:
        break
       
    if block > 1:
        block_text = f"""Starting block {block} of 8

Take a short break if needed.
Remember:
- Press 'Z' for GREEN words/blocks
- Press 'M' for RED words/blocks
- Press 'ESC' to exit

Press SPACEBAR to continue."""
       
        block_stim = visual.TextStim(win, text=block_text, color='white', height=30, wrapWidth=700)
        block_stim.draw()
        win.flip()
        block_keys = event.waitKeys(keyList=['space', 'escape'])
        if block_keys and 'escape' in block_keys:
            experiment_escaped = True
            break
   
    block_trials = generate_block_trials(block)
   
    for trial in block_trials:
        result = trial.run()
        if result['status'] == 'escape':
            experiment_escaped = True
            break
   
    if experiment_escaped:
        break

if not experiment_escaped and all_data:
    all_rts = [trial['rt'] for trial in all_data] 
    correct_trials = [trial for trial in all_data if trial['correct']]
    correct_rts = [trial['rt'] for trial in correct_trials]
   
    if all_rts:
        mean_rt_overall = sum(all_rts) / len(all_rts)
        mean_rt_correct = sum(correct_rts) / len(correct_rts) if correct_rts else 0
        accuracy = len(correct_trials) / len(all_data) * 100
       
        results_text = f"""Experiment Completed!

Your Performance:
- Total Trials: {len(all_data)}
- Accuracy: {accuracy:.1f}%
- Average Reaction Time (Overall): {mean_rt_overall:.3f} seconds
- Average Reaction Time (Correct Only): {mean_rt_correct:.3f} seconds

Thank you for participating in this experiment!
Your data has been saved to: {data_file}

Press any key to exit."""
    else:
        results_text = """Experiment Completed!

Thank you for participating in this experiment!
Your data has been saved.

Press any key to exit."""
   
    results_stim = visual.TextStim(win, text=results_text, color='white', height=30, wrapWidth=700)
    results_stim.draw()
    win.flip()
    event.waitKeys()

elif experiment_escaped:
    thanks_text = """Experiment terminated.

Thank you for your time!

Press any key to exit."""
   
    thanks_stim = visual.TextStim(win, text=thanks_text, color='white', height=30, wrapWidth=700)
    thanks_stim.draw()
    win.flip()
    event.waitKeys()

win.close()
core.quit()