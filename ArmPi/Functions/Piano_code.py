
# Notes from sheet music
pre_chorous= 'd c d d d d d d c d e d d d d d e d d d d a g f e f e f e f f f d e e e e d g f '
chorous = 'f f d s d d g f d d e e d f d e d e f e d e e d f d e d e d f e d e d f e d d e f e f e f e f f e d'
pre_chorous_notes= pre_chorous.split(' ')
chorous_notes = chorous.split(' ')

#types of notes from sheet music
pre_chorous_type = [8, 8 ,8, 8, 8, 4, 8, 8, 8, 4, 4, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 4, 2 ]
chorous_type = [8, 4, 8, 4, 8, 8, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 4, 8, 8, 4, 8, 8, 8, 8, 8, 8, 4, 8, 8, 4]
play_time_pc= []
play_time_c = []

#equate note type to time
def bpm_to_time (music,array):
    for i in music:
        if i == 8:
            t = .25
        elif i == 4: 
            t = .5
        elif i == 2:
            t = 1
        elif i == 3:
            t = 1.5
        array.append(t)

bpm_to_time (pre_chorous_type,play_time_pc)
bpm_to_time(chorous_type,play_time_c)


# print(f'pc notes {len(pre_chorous_notes)}')
# print(f'pc time {len(play_time_pc)}')
# print(f'c notes {len(chorous_notes)}')
# print(f'c time {len(play_time_c)}')


pre_chorous_notes, chorous_notes, play_time_pc, play_time_c = perception.get_music()

for i in chorous_notes: 
    note = chorous_notes[i]
    press = play_time_c[i]


    # Notes from sheet music
def get_music(self):
    pre_chorous= 'd c d d d d d d c d e d d d d d e d d d d a g f e f e f e f f f d e e e e d g f '
    chorous = 'f f d s d d g f d d e e d f d e d e f e d e e d f d e d e d f e d e d f e d d e f e f e f e f f e d'
    pre_chorous_notes= pre_chorous.split(' ')
    chorous_notes = chorous.split(' ')
    c_colors = []
    pc_colors = []

    #types of notes from sheet music
    pre_chorous_type = [8, 8 ,8, 8, 8, 4, 8, 8, 8, 4, 4, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 8, 4, 4, 4, 2 ]
    chorous_type = [8, 4, 8, 4, 8, 8, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4, 4, 8, 8, 8, 8, 8, 8, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 4, 8, 8, 4, 8, 8, 8, 8, 8, 8, 4, 8, 8, 4]
    play_time_pc= []
    play_time_c = []
    self.bpm_to_time (pre_chorous_type,play_time_pc)
    self.bpm_to_time(chorous_type,play_time_c)
    self.notes_to_color(pre_chorous_notes,pc_colors)
    self.notes_to_color(chorous_notes,c_colors)

    return pc_colors, c_colors, play_time_pc, play_time_c

#equate note type to time
def bpm_to_time (self, music,array):
    for i in music:
        if i == 8:
            t = .25
        elif i == 4: 
            t = .5
        elif i == 2:
            t = 1
        elif i == 3:
            t = 1.5
        array.append(t)
def notes_to_color (self,music,array):
    for i in music:
        if i == 'd':
            color = 'green'
        elif i == 'e':
            color = 'yellow'
        elif i == 'f':
            color = 'blue'
        elif i == 'g':
            color = 'red'
        array.append(color)