from psychopy import visual, core, event, data, gui
import random
import string
import csv
from datetime import datetime

info = {'Participant ID': '', 'Age': '', 'Gender': ['Male', 'Female', 'Other', 'Prefer not to say']}
dlg = gui.DlgFromDict(info, title='Participant Information')
if not dlg.OK:
    core.quit()

win = visual.Window(fullscr=True, color='black')
clock = core.Clock()
instructions = visual.TextStim(win, text="Welcome to the experiment.\n\nYou will see some random letters with some color-words mixed in.\n\nAfter each trial you will be asked to report if you saw a color-word.\n\nPress 'Z' for Yes, 'M' for No\n\nPress SPACEBAR to begin.\nPress ESC to quit anytime.", color='white')
fixation = visual.TextStim(win, text="+", color='white')
random_stim = visual.TextStim(win, text="", color='white')
prime = visual.TextStim(win, text="", color='white')
question = visual.TextStim(win, text="Did you see a color word?\n\nPress 'Z' for Yes, 'M' for No", color='white')
break_screen = visual.TextStim(win, text="", color='white')

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

durations_ms = [0, 29, 43, 57, 114, 200]
durations_s = [d / 1000.0 for d in durations_ms]
prime_words = ["GREEN", "RED"]
trials_per_duration = 30

# Generate all trials
trial_list = []
for i, dur_s in enumerate(durations_s):
    for _ in range(trials_per_duration):
        trial_list.append({'duration_s': dur_s,
                           'duration_ms': durations_ms[i],
                           'prime': random.choice(prime_words)})
random.shuffle(trial_list)

# Split into 4 blocks of 45 trials each
num_blocks = 4
trials_per_block = 45
blocks = [trial_list[i*trials_per_block:(i+1)*trials_per_block] for i in range(num_blocks)]

instructions.draw()
win.flip()
event.waitKeys(keyList=['space'])

results = []
escape_pressed = False

for block_num, block_trials in enumerate(blocks):
    if escape_pressed:
        break
    
    for trial_num, trial in enumerate(block_trials):
        if 'escape' in event.getKeys():
            escape_pressed = True
            break

        fixation.draw()
        win.flip()
        core.wait(0.5)

        random_stim.text = generate_random_string()
        random_stim.draw()
        win.flip()
        core.wait(0.5)

        prime.text = trial['prime']
        prime.draw()
        win.flip()
        core.wait(trial['duration_s'])

        random_stim.text = generate_random_string()
        random_stim.draw()
        win.flip()
        core.wait(0.5)

        question.draw()
        win.flip()
        response = event.waitKeys(keyList=['z', 'm', 'escape'])
        if 'escape' in response:
            escape_pressed = True
            break

        results.append({'block': block_num + 1,
                        'trial': trial_num + 1,
                        'prime': trial['prime'],
                        'duration_ms': trial['duration_ms'],
                        'response': response[0]})
    
    # Show break screen after blocks 1, 2, and 3 (not after block 4)
    if block_num < num_blocks - 1 and not escape_pressed:
        break_screen.text = f"End of Block {block_num + 1} of {num_blocks}\n\nTake a short break.\n\n Press SPACEBAR when ready to continue."
        break_screen.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"prime_detection_data_{timestamp}.tsv"

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['block', 'trial', 'prime', 'duration_ms', 'response'], delimiter='\t')
    writer.writeheader()
    writer.writerows(results)

thank_you = visual.TextStim(win, text="Thank you for participating!\n\nPress SPACE to exit.", color='white')
thank_you.draw()
win.flip()
event.waitKeys(keyList=['space'])

win.close()
core.quit()