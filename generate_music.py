from mido import Message, MidiFile, MidiTrack
import os
import random
import mido

# Definitions for the chords and scales
chords = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus4': [0, 5, 7],
    'sus2': [0, 2, 7],
    '6': [0, 4, 7, 9],
    '9': [0, 4, 7, 14],
    '11': [0, 4, 7, 17],
    '13': [0, 4, 7, 21],
    'dim7': [0, 3, 6, 9],
    'dom9': [0, 4, 7, 10, 14],  # Root, major 3rd, perfect 5th, minor 7th, major 9th
    'dom11': [0, 4, 7, 10, 14, 17],  # Root, major 3rd, perfect 5th, minor 7th, major 9th, perfect 11th
    'dom13': [0, 4, 7, 10, 14, 17, 21],  # Root, major 3rd, perfect 5th, minor 7th, major 9th, perfect 11th, major 13th
}

# Mapping of note names to MIDI note numbers
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_numbers = {name: i + 60 for i, name in enumerate(note_names)}  # C4 (MIDI note 60) to B4


scales = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
}

common_progressions = [
    [1, 4, 5, 4],  # I-IV-V-IV
    [2, 5, 1],  # ii-V-I
    [1, 6, 4, 5],  # I-vi-IV-V
    [1, 4],  # I-IV
    [1, 5],  # I-V
    [4, 5],  # IV-V
    [1, 4, 1, 5],  # I-IV-I-V
    [1, 6, 2, 5],  # I-vi-ii-V
    [1, 5, 6, 4],  # I-V-vi-IV
    [2, 5, 1, 6],  # ii-V-I-vi
    [1, 2, 4, 5],  # I-ii-IV-V
    [1, 3, 4, 5],  # I-iii-IV-V
    [6, 2, 5, 1],  # vi-ii-V-I
    [3, 6, 2, 5, 1]  # iii-vi-ii-V-I
]

roman_numerals = {
    1: 'I',
    2: 'ii',
    3: 'iii',
    4: 'IV',
    5: 'V',
    6: 'vi',
    7: 'vii'
}

roman_numerals_to_chords = {
    'I': 'major',
    'ii': 'minor',
    'iii': 'minor',
    'IV': 'major',
    'V': 'major',
    'vi': 'minor',
    'vii': 'dim'
}

key_names = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B'
}

def generate_chord_progression(key, scale_type, progression, num_bars, tempo=120):
    mid = MidiFile(ticks_per_beat=480)  # Defines the ticks per beat
    track = MidiTrack()
    mid.tracks.append(track)

    ticks_per_note = mid.ticks_per_beat * 4  # A whole note is 4 beats

    track.append(Message('program_change', program=12, time=0))

    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

    scale = scales[scale_type]
    key_number = note_numbers[key]

    # Calculate the MIDI numbers for the scale in the given key
    scale_numbers = [(note_number + key_number) % 12 + 60 for note_number in scale]

    # Create the chords for the progression
    for i in range(num_bars):
        for degree in progression:
            chord_type = roman_numerals_to_chords[roman_numerals[degree]]
            chord_intervals = chords[chord_type]
            chord_numbers = [(note_number + interval) % 12 + 60 for note_number in scale_numbers for interval in chord_intervals]
            
            # Now each note in the chord lasts for one whole note
            for note in chord_numbers:
                track.append(Message('note_on', note=note, velocity=64, time=0))
            track.append(Message('note_off', note=chord_numbers[-1], velocity=64, time=ticks_per_note))

    mid.save(os.path.join(OUTPUT_DIR, f"{key}_{scale_type}_{len(progression)}chords_{num_bars}bars.mid"))


# Generate progression and save it to a MIDI file
def generate_and_save_progression(root, scale_type, progression, folder):
    progression_name = "_".join([roman_numerals[i] for i in progression])
    file_name = os.path.join(folder, f'{key_names[root%12]}_{scale_type.upper()}_{progression_name}.mid')

    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    for degree in progression:
        chord_root = scales[scale_type][(root + degree - 1) % len(scales[scale_type])]
        chord_type = 'major' if degree in [1, 4, 5] else 'minor'
        if degree == 5: chord_type = 'dom7'
        if degree in [1, 4]: chord_type = random.choice(['major', 'maj7'])
        if degree in [2, 3, 6]: chord_type = 'min7'
        chord = chords[chord_type]

        for note in chord:
            track.append(Message('note_on', note=chord_root+note, velocity=64, time=0))
        
        for note in chord:
            track.append(Message('note_off', note=chord_root+note, velocity=64, time=480))

    midi.save(file_name)

def generate_and_save_chord(root, scale_type, chord_type, degree, folder):
    file_name = os.path.join(folder, f'{key_names[root%12]}_{scale_type.upper()}_{roman_numerals[degree]}_{chord_type}.mid')

    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    chord_root = scales[scale_type][(root + degree - 1) % len(scales[scale_type])]
    chord = chords[chord_type]

    for note in chord:
        track.append(Message('note_on', note=chord_root+note, velocity=64, time=0))
        
    for note in chord:
        track.append(Message('note_off', note=chord_root+note, velocity=64, time=480))

    midi.save(file_name)


# Main program
def main():
    OUTPUT_DIR = "Midi Output"
    for root in range(60, 72):
        for scale_type in ['major', 'minor']:
            folder = os.path.join(OUTPUT_DIR, f'{key_names[root%12]}_{scale_type.upper()}')
            os.makedirs(folder, exist_ok=True)

            # Generate progressions
            progression_folder = os.path.join(folder, 'progressions')
            os.makedirs(progression_folder, exist_ok=True)
            for progression in common_progressions:
                generate_and_save_progression(root, scale_type, progression, progression_folder)

            # Generate extended chords
            chord_folder = os.path.join(folder, 'chords')
            os.makedirs(chord_folder, exist_ok=True)
            for degree in range(1, 8):
                if degree in [1, 4]:
                    for chord_type in ['major', 'maj7']:
                        generate_and_save_chord(root, scale_type, chord_type, degree, chord_folder)
                elif degree in [2, 3, 6]:
                    generate_and_save_chord(root, scale_type, 'min7', degree, chord_folder)
                elif degree == 5:
                    for chord_type in ['dom7', 'dom9', 'dom11', 'dom13']:
                        generate_and_save_chord(root, scale_type, chord_type, degree, chord_folder)

if __name__ == '__main__':
    main()
