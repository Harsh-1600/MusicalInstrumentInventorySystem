"""
SoundCraft Studio Audio Synthesis Engine - Iconic Music & Tracks Generator
Generates studio-quality 16-bit 44.1kHz PCM WAV audio for all 35 instruments in the store,
synthesizing the exact iconic melodies, solos, and rhythms requested by the user.
100% native Python standard library (wave + struct + math + random).
"""

import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100

def write_wav(filename, samples):
    """Encodes sample buffer as 16-bit mono 44.1kHz PCM WAV file."""
    os.makedirs(os.path.join("static", "audio"), exist_ok=True)
    filepath = os.path.join("static", "audio", filename)
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        packed = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            val = int(clamped * 32767.0)
            packed.extend(struct.pack('<h', val))
        f.writeframes(packed)
    print(f"Generated: {filename} ({len(samples)/SAMPLE_RATE:.2f}s)")

# =========================================================================
# HELPER SOUND GENERATORS (PHYSICAL TIMBRE MODELING)
# =========================================================================

def add_tone(buf, start_time, freq, dur=0.4, vol=0.5, timbre='plucked', vibrato=0.0):
    start = int(start_time * SAMPLE_RATE)
    count = int(dur * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        # Vibrato
        f = freq
        if vibrato > 0.0:
            f = freq * (1.0 + 0.015 * math.sin(2.0 * math.pi * 5.8 * t))

        phase = 2.0 * math.pi * f * t

        if timbre == 'electric_lead': # Overdrive guitar
            harm = (math.sin(phase) + 0.6 * math.sin(phase * 2) + 0.4 * math.sin(phase * 3))
            raw = math.tanh(harm * 2.8) # Overdrive clipping
            env = math.exp(-t * 2.2)
            buf[idx] += raw * env * vol

        elif timbre == 'acoustic_guitar': # Warm wooden plucked string
            harm = (math.sin(phase) +
                    0.5 * math.sin(phase * 2.003) +
                    0.25 * math.sin(phase * 3.007) +
                    0.12 * math.sin(phase * 4.01))
            pluck = (random.random() * 2.0 - 1.0) * math.exp(-t * 200.0) * 0.35
            env = math.exp(-t * 3.5)
            buf[idx] += (harm + pluck) * env * vol

        elif timbre == 'violin': # Bowed string with bow friction
            harm = (math.sin(phase) + 0.5 * math.sin(phase * 2) + 0.3 * math.sin(phase * 3) + 0.2 * math.sin(phase * 4))
            friction = (random.random() * 2.0 - 1.0) * math.exp(-t * 60.0) * 0.15
            env = (1.0 - math.exp(-t * 35.0)) * math.exp(-t * 1.5) # Smooth bow attack
            buf[idx] += (harm + friction) * env * vol

        elif timbre == 'cello': # Low bowed string
            harm = (math.sin(phase) + 0.7 * math.sin(phase * 2) + 0.4 * math.sin(phase * 3))
            env = (1.0 - math.exp(-t * 25.0)) * math.exp(-t * 1.2)
            buf[idx] += harm * env * vol

        elif timbre == 'ukulele': # Bright nylon chord chime
            harm = (math.sin(phase) + 0.6 * math.sin(phase * 2) + 0.3 * math.sin(phase * 3))
            env = math.exp(-t * 5.0)
            buf[idx] += harm * env * vol

        elif timbre == 'banjo': # Crisp twangy banjo
            harm = (math.sin(phase) + 0.7 * math.sin(phase * 2) + 0.5 * math.sin(phase * 3) + 0.3 * math.sin(phase * 4))
            twang = math.sin(2.0 * math.pi * f * 4.5 * t) * math.exp(-t * 50.0) * 0.4
            env = math.exp(-t * 6.5)
            buf[idx] += (harm + twang) * env * vol

        elif timbre == 'mandolin': # Rapid double-string mandolin
            f_detune = f * 1.002
            harm = math.sin(phase) + math.sin(2.0 * math.pi * f_detune * t)
            env = math.exp(-t * 5.5)
            buf[idx] += harm * env * vol * 0.6

        elif timbre == 'bass': # Deep sub-bass punch
            harm = math.sin(phase) + 0.4 * math.sin(phase * 2)
            env = math.exp(-t * 3.2)
            buf[idx] += harm * env * vol

        elif timbre == 'sitar': # Meend bend + Javari buzz
            meend = f * (1.0 + 0.04 * math.sin(math.pi * min(1.0, t * 4.0)))
            phase_m = 2.0 * math.pi * meend * t
            buzz = math.sin(phase_m * 3.96) * 0.35 + math.sin(phase_m * 5.92) * 0.2
            harm = math.sin(phase_m) + 0.6 * math.sin(phase_m * 2)
            env = math.exp(-t * 2.8)
            buf[idx] += (harm + buzz) * env * vol

        elif timbre == 'veena': # Deep Carnatic gamaka oscillation
            gamaka = f * (1.0 + 0.03 * math.sin(2.0 * math.pi * 5.0 * t))
            phase_g = 2.0 * math.pi * gamaka * t
            harm = math.sin(phase_g) + 0.5 * math.sin(phase_g * 2) + 0.25 * math.sin(phase_g * 3)
            env = math.exp(-t * 3.0)
            buf[idx] += harm * env * vol

        elif timbre == 'flute': # Breathy bansuri / silver flute
            air = (random.random() * 2.0 - 1.0) * math.exp(-t * 12.0) * 0.12
            harm = math.sin(phase) + 0.2 * math.sin(phase * 2)
            env = (1.0 - math.exp(-t * 30.0)) * math.exp(-t * 1.4)
            buf[idx] += (harm + air) * env * vol

        elif timbre == 'saxophone': # Sultry jazz sax
            harm = math.sin(phase) + 0.5 * math.sin(phase * 2) + 0.3 * math.sin(phase * 3)
            reed = math.tanh(harm * 2.0)
            env = (1.0 - math.exp(-t * 40.0)) * math.exp(-t * 1.3)
            buf[idx] += reed * env * vol

        elif timbre == 'trumpet': # Royal fanfare brass
            harm = math.sin(phase) + 0.7 * math.sin(phase * 2) + 0.5 * math.sin(phase * 3) + 0.3 * math.sin(phase * 4)
            env = (1.0 - math.exp(-t * 60.0)) * math.exp(-t * 1.5)
            buf[idx] += harm * env * vol

        elif timbre == 'clarinet': # Warm liquid clarinet
            harm = math.sin(phase) + 0.6 * math.sin(phase * 3) + 0.15 * math.sin(phase * 5)
            env = (1.0 - math.exp(-t * 45.0)) * math.exp(-t * 1.6)
            buf[idx] += harm * env * vol

        elif timbre == 'harmonica': # Blues / western harmonica with reed bend
            harm = math.sin(phase) + 0.5 * math.sin(phase * 2) + 0.3 * math.sin(phase * 3)
            env = (1.0 - math.exp(-t * 50.0)) * math.exp(-t * 1.8)
            buf[idx] += harm * env * vol

        elif timbre == 'oboe': # Poignant double reed
            harm = math.sin(phase) + 0.8 * math.sin(phase * 2) + 0.6 * math.sin(phase * 3) + 0.4 * math.sin(phase * 4)
            env = (1.0 - math.exp(-t * 40.0)) * math.exp(-t * 1.4)
            buf[idx] += harm * env * vol

        elif timbre == 'trombone': # Brass slide trombone
            harm = math.sin(phase) + 0.6 * math.sin(phase * 2) + 0.4 * math.sin(phase * 3)
            env = (1.0 - math.exp(-t * 40.0)) * math.exp(-t * 1.4)
            buf[idx] += harm * env * vol

        elif timbre == 'tuba': # Deep comical bass tuba
            harm = math.sin(phase) + 0.5 * math.sin(phase * 2)
            env = math.exp(-t * 2.5)
            buf[idx] += harm * env * vol

        elif timbre == 'piano': # Grand piano hammer click + decay
            p1 = math.sin(phase)
            p2 = 0.5 * math.sin(phase * 2.002)
            p3 = 0.25 * math.sin(phase * 3.006)
            hammer = math.exp(-t * 300.0) * 0.25 * (random.random() * 2.0 - 1.0)
            env = math.exp(-t * 2.8)
            buf[idx] += (p1 + p2 + p3 + hammer) * env * vol

        elif timbre == 'digital_piano': # Bright Yiruma digital piano
            p1 = math.sin(phase)
            p2 = 0.6 * math.sin(phase * 2.001)
            env = math.exp(-t * 2.4)
            buf[idx] += (p1 + p2) * env * vol

        elif timbre == 'synth': # Alan Walker Faded supersaw
            raw = (math.sin(phase) + 0.7 * math.sin(phase * 1.01) + 0.7 * math.sin(phase * 0.99))
            env = math.exp(-t * 3.0)
            buf[idx] += raw * env * vol * 0.5

        elif timbre == 'accordion': # Parisian French musette
            f_tremolo = f * 1.008
            reed = math.sin(phase) + math.sin(2.0 * math.pi * f_tremolo * t)
            env = (1.0 - math.exp(-t * 40.0)) * math.exp(-t * 1.6)
            buf[idx] += reed * env * vol * 0.55

        elif timbre == 'organ': # Gothic pipe organ with mixture stops
            pipe = (math.sin(phase) +
                    0.8 * math.sin(phase * 2) +
                    0.6 * math.sin(phase * 3) +
                    0.5 * math.sin(phase * 4))
            env = (1.0 - math.exp(-t * 35.0)) * math.exp(-t * 0.8)
            buf[idx] += pipe * env * vol * 0.45

        elif timbre == 'xylophone': # Wooden mallet chime
            bar = math.sin(phase) + 0.4 * math.sin(phase * 3.0)
            mallet = math.exp(-t * 450.0) * 0.35
            env = math.exp(-t * 8.5)
            buf[idx] += (bar + mallet) * env * vol

        elif timbre == 'triangle': # High orchestral triangle bell ring
            bell = (math.sin(2.0 * math.pi * 6500.0 * t) +
                    0.8 * math.sin(2.0 * math.pi * 9800.0 * t) +
                    0.4 * math.sin(2.0 * math.pi * 14200.0 * t))
            env = math.exp(-t * 2.5)
            buf[idx] += bell * env * vol

        elif timbre == 'tambourine': # Sleighbell / jingle cluster
            jingle = (random.random() * 2.0 - 1.0) * math.exp(-t * 35.0)
            metal = (math.sin(2.0 * math.pi * 8500.0 * t) + math.sin(2.0 * math.pi * 11000.0 * t)) * 0.3
            env = math.exp(-t * 25.0)
            buf[idx] += (jingle + metal) * env * vol

        else:
            buf[idx] += math.sin(phase) * math.exp(-t * 3.0) * vol

# Percussion element helpers
def add_drum_kick(buf, start_time, vol=0.9):
    start = int(start_time * SAMPLE_RATE)
    count = int(0.28 * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        freq = 45.0 + 115.0 * math.exp(-t * 28.0)
        click = math.sin(2.0 * math.pi * 900.0 * t) * math.exp(-t * 120.0) * 0.4
        env = math.exp(-t * 12.0)
        buf[idx] += (math.sin(2.0 * math.pi * freq * t) + click) * env * vol

def add_drum_snare(buf, start_time, vol=0.8):
    start = int(start_time * SAMPLE_RATE)
    count = int(0.22 * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        body = math.sin(2.0 * math.pi * 185.0 * t) * math.exp(-t * 18.0) * 0.5
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 16.0) * 0.6
        buf[idx] += (body + noise) * vol

def add_drum_hihat(buf, start_time, vol=0.45):
    start = int(start_time * SAMPLE_RATE)
    count = int(0.08 * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 45.0)
        metal = (math.sin(2.0 * math.pi * 8400.0 * t) + math.sin(2.0 * math.pi * 10200.0 * t)) * 0.3
        buf[idx] += (noise + metal) * math.exp(-t * 50.0) * vol

def add_tabla_bayan(buf, start_time, vol=0.85): # Ghe / Dha
    start = int(start_time * SAMPLE_RATE)
    count = int(0.38 * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        freq = 65.0 + 75.0 * math.exp(-t * 14.0) # Pitch glide
        env = math.exp(-t * 7.5)
        buf[idx] += math.sin(2.0 * math.pi * freq * t) * env * vol

def add_tabla_dayan(buf, start_time, pitch=320.0, vol=0.75): # Dhin / Ta
    start = int(start_time * SAMPLE_RATE)
    count = int(0.35 * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        f1 = math.sin(2.0 * math.pi * pitch * t)
        f2 = math.sin(2.0 * math.pi * pitch * 2.89 * t) * 0.45
        env = math.exp(-t * 8.0)
        buf[idx] += (f1 + f2) * env * vol

def add_djembe_hit(buf, start_time, hit_type='bass', vol=0.8):
    start = int(start_time * SAMPLE_RATE)
    dur = 0.35 if hit_type == 'bass' else 0.18
    count = int(dur * SAMPLE_RATE)
    for i in range(count):
        idx = start + i
        if idx >= len(buf): break
        t = i / SAMPLE_RATE
        if hit_type == 'bass':
            f = 85.0 * math.exp(-t * 12.0)
            buf[idx] += math.sin(2.0 * math.pi * f * t) * math.exp(-t * 8.0) * vol
        elif hit_type == 'open':
            f = 220.0
            buf[idx] += math.sin(2.0 * math.pi * f * t) * math.exp(-t * 16.0) * vol
        else: # slap
            noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 30.0)
            tone = math.sin(2.0 * math.pi * 380.0 * t) * math.exp(-t * 22.0)
            buf[idx] += (noise * 0.6 + tone * 0.4) * vol


# =========================================================================
# ALL 35 ICONIC TRACK BUILDERS
# =========================================================================

TRACK_DEFINITIONS = {}

# 1. 101 - Gibson Les Paul -> Sweet Child O' Mine
def track_sweet_child_o_mine(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Riff: D4 - D5 - A4 - G4 - G5 - A4 - F#5 - A4
    notes = [
        (0.00, 293.66), (0.24, 587.33), (0.48, 440.00), (0.72, 392.00),
        (0.96, 783.99), (1.20, 440.00), (1.44, 739.99), (1.68, 440.00)
    ]
    if not is_preview:
        notes += [
            (1.92, 293.66), (2.16, 587.33), (2.40, 440.00), (2.64, 392.00),
            (2.88, 783.99), (3.12, 440.00), (3.36, 739.99), (3.60, 440.00)
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.35, vol=0.55, timbre='electric_lead')
    return buf
TRACK_DEFINITIONS['101'] = ('Sweet Child O\' Mine', track_sweet_child_o_mine)

# 2. INS001 - Guitar -> Hotel California
def track_hotel_california(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Bm arpeggio -> F# arpeggio
    notes = [
        (0.00, 246.94), (0.22, 293.66), (0.44, 369.99), (0.66, 493.88), # B3 - D4 - F#4 - B4
        (0.95, 185.00), (1.17, 233.08), (1.39, 277.18), (1.61, 369.99)  # F#3 - A#3 - C#4 - F#4
    ]
    if not is_preview:
        notes += [
            (2.00, 220.00), (2.22, 277.18), (2.44, 329.63), (2.66, 440.00), # A3 - C#4 - E4 - A4
            (2.95, 164.81), (3.17, 207.65), (3.39, 246.94), (3.61, 329.63)  # E3 - G#3 - B3 - E4
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.65, vol=0.5, timbre='acoustic_guitar')
    return buf
TRACK_DEFINITIONS['INS001'] = ('Hotel California', track_hotel_california)

# 3. INS003 - Violin -> Canon in D
def track_canon_in_d(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 739.99, 0.48), # F#5
        (0.50, 659.25, 0.48), # E5
        (1.00, 587.33, 0.48), # D5
        (1.50, 554.37, 0.48)  # C#5
    ]
    if not is_preview:
        notes += [
            (2.00, 493.88, 0.48), # B4
            (2.50, 440.00, 0.48), # A4
            (3.00, 493.88, 0.48), # B4
            (3.50, 554.37, 0.60)  # C#5
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.5, timbre='violin', vibrato=0.02)
    return buf
TRACK_DEFINITIONS['INS003'] = ('Canon in D', track_canon_in_d)

# 4. INS007 - Ukulele -> Somewhere Over the Rainbow
def track_over_the_rainbow(is_preview=False):
    length = 2.2 if is_preview else 4.0
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 261.63, 0.5), # C4 (Some-)
        (0.55, 523.25, 0.6), # C5 (-where)
        (1.20, 493.88, 0.4), # B4 (o-)
        (1.60, 392.00, 0.4)  # G4 (-ver)
    ]
    if not is_preview:
        notes += [
            (2.10, 440.00, 0.35), # A4 (the)
            (2.50, 493.88, 0.40), # B4 (rain-)
            (3.00, 523.25, 0.80)  # C5 (-bow)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='ukulele')
    return buf
TRACK_DEFINITIONS['INS007'] = ('Somewhere Over the Rainbow', track_over_the_rainbow)

# 5. INS010 - Cello -> The Swan (Le Cygne)
def track_the_swan(is_preview=False):
    length = 2.4 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 196.00, 0.7), # G3
        (0.75, 293.66, 0.7), # D4
        (1.50, 246.94, 0.8)  # B3
    ]
    if not is_preview:
        notes += [
            (2.30, 261.63, 0.6), # C4
            (2.95, 293.66, 0.6), # D4
            (3.55, 329.63, 0.6)  # E4
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='cello', vibrato=0.02)
    return buf
TRACK_DEFINITIONS['INS010'] = ('The Swan', track_the_swan)

# 6. INS015 - Banjo -> Dueling Banjos
def track_dueling_banjos(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 493.88), (0.20, 523.25), (0.40, 587.33), (0.60, 493.88),
        (0.85, 523.25), (1.05, 440.00), (1.30, 493.88), (1.55, 392.00)
    ]
    if not is_preview:
        notes += [
            (1.90, 440.00), (2.10, 293.66), (2.40, 392.00), (2.70, 493.88),
            (3.00, 587.33), (3.30, 392.00)
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.3, vol=0.55, timbre='banjo')
    return buf
TRACK_DEFINITIONS['INS015'] = ('Dueling Banjos', track_dueling_banjos)

# 7. INS016 - Mandolin -> Losing My Religion
def track_losing_my_religion(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 440.00), (0.15, 523.25), (0.30, 659.25), (0.45, 523.25),
        (0.60, 440.00), (0.75, 523.25), (0.90, 659.25), (1.05, 523.25),
        (1.20, 392.00), (1.35, 493.88), (1.50, 587.33), (1.65, 493.88)
    ]
    if not is_preview:
        notes += [
            (1.90, 349.23), (2.05, 440.00), (2.20, 523.25), (2.35, 440.00),
            (2.60, 392.00), (2.85, 440.00), (3.10, 523.25), (3.35, 440.00)
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.25, vol=0.5, timbre='mandolin')
    return buf
TRACK_DEFINITIONS['INS016'] = ('Losing My Religion', track_losing_my_religion)

# 8. INS017 - Electric Guitar -> Nothing Else Matters
def track_nothing_else_matters(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # E minor open string arpeggio (E - G - B - E - B - G)
    notes = [
        (0.00, 164.81), (0.28, 196.00), (0.56, 246.94),
        (0.84, 329.63), (1.12, 246.94), (1.40, 196.00)
    ]
    if not is_preview:
        notes += [
            (1.80, 659.25), # High E lead
            (2.35, 587.33), # D
            (2.90, 523.25), # C
            (3.45, 493.88)  # B
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.6, vol=0.55, timbre='electric_lead')
    return buf
TRACK_DEFINITIONS['INS017'] = ('Nothing Else Matters', track_nothing_else_matters)

# 9. INS018 - Bass Guitar -> Another One Bites the Dust
def track_another_one_bites_the_dust(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # E - E - E - E - G - E - A
    notes = [
        (0.00, 82.41, 0.15), (0.22, 82.41, 0.15), (0.44, 82.41, 0.15),
        (0.88, 82.41, 0.18), (1.15, 98.00, 0.22), (1.42, 82.41, 0.20), (1.70, 110.00, 0.35)
    ]
    if not is_preview:
        notes += [
            (2.20, 82.41, 0.15), (2.42, 82.41, 0.15), (2.64, 82.41, 0.15),
            (3.08, 82.41, 0.18), (3.35, 98.00, 0.22), (3.60, 110.00, 0.35)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.7, timbre='bass')
    return buf
TRACK_DEFINITIONS['INS018'] = ('Another One Bites the Dust', track_another_one_bites_the_dust)

# 10. INS027 - Sitar -> Raga Yaman
def track_raga_yaman(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Ni - Re - Ga - Ma(t) - Dha - Ni - Sa
    notes = [
        (0.00, 246.94, 0.5), # Ni
        (0.48, 293.66, 0.5), # Re
        (0.96, 329.63, 0.6), # Ga
        (1.50, 369.99, 0.6)  # Ma (Tivra)
    ]
    if not is_preview:
        notes += [
            (2.10, 440.00, 0.5), # Dha
            (2.60, 493.88, 0.5), # Ni
            (3.10, 523.25, 0.9)  # Sȧ
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='sitar')
    return buf
TRACK_DEFINITIONS['INS027'] = ('Raga Yaman', track_raga_yaman)

# 11. INS028 - Veena -> Vatapi Ganapatim
def track_vatapi_ganapatim(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Hamsadhvani: Sa - Ri - Ga - Pa - Ni - Sȧ
    # "Va-ta-pi Ga-na-pa-tim"
    notes = [
        (0.00, 261.63, 0.35), # Sa
        (0.35, 293.66, 0.35), # Ri
        (0.70, 329.63, 0.40), # Ga
        (1.10, 392.00, 0.45), # Pa
        (1.55, 493.88, 0.45)  # Ni
    ]
    if not is_preview:
        notes += [
            (2.00, 523.25, 0.60), # Sȧ
            (2.60, 493.88, 0.40), # Ni
            (3.00, 392.00, 0.40), # Pa
            (3.40, 329.63, 0.60)  # Ga
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='veena')
    return buf
TRACK_DEFINITIONS['INS028'] = ('Vatapi Ganapatim', track_vatapi_ganapatim)

# 12. 102 - Yamaha YFL-222 Flute -> My Heart Will Go On
def track_my_heart_will_go_on(is_preview=False):
    length = 2.4 if is_preview else 4.4
    buf = [0.0] * int(SAMPLE_RATE * length)
    # F4 - G4 - A4 - G4 - F4 - G4 - C5 - Bb4 - A4 - F4
    notes = [
        (0.00, 349.23, 0.45), (0.45, 392.00, 0.45), (0.90, 440.00, 0.60),
        (1.50, 392.00, 0.40), (1.90, 349.23, 0.40)
    ]
    if not is_preview:
        notes += [
            (2.30, 392.00, 0.45), (2.75, 523.25, 0.65), (3.40, 466.16, 0.40), (3.80, 440.00, 0.50)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='flute', vibrato=0.015)
    return buf
TRACK_DEFINITIONS['102'] = ('My Heart Will Go On', track_my_heart_will_go_on)

# 13. INS005 - Flute -> Titanic Flute Theme
def track_titanic_flute_theme(is_preview=False):
    length = 2.4 if is_preview else 4.4
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 440.00, 0.65), # A4
        (0.70, 493.88, 0.45), # B4
        (1.15, 554.37, 0.65), # C#5
        (1.80, 493.88, 0.50)  # B4
    ]
    if not is_preview:
        notes += [
            (2.30, 440.00, 0.45), # A4
            (2.75, 493.88, 0.45), # B4
            (3.20, 659.25, 0.85)  # E5 (Climax)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='flute', vibrato=0.02)
    return buf
TRACK_DEFINITIONS['INS005'] = ('Titanic Flute Theme', track_titanic_flute_theme)

# 14. INS008 - Saxophone -> Careless Whisper
def track_careless_whisper(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # D5 - B4 - G4 - B4 - D5 - C5 - A4 - F#4
    notes = [
        (0.00, 587.33, 0.28), (0.28, 493.88, 0.28), (0.56, 392.00, 0.28), (0.84, 493.88, 0.28),
        (1.12, 587.33, 0.40), (1.52, 523.25, 0.28), (1.80, 440.00, 0.28)
    ]
    if not is_preview:
        notes += [
            (2.08, 369.99, 0.28), (2.36, 440.00, 0.28), (2.64, 523.25, 0.38),
            (3.02, 493.88, 0.35), (3.37, 392.00, 0.40), (3.77, 329.63, 0.45)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='saxophone', vibrato=0.02)
    return buf
TRACK_DEFINITIONS['INS008'] = ('Careless Whisper', track_careless_whisper)

# 15. INS009 - Trumpet -> The Final Countdown
def track_final_countdown(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # B4 - A4 - B4 - E4 - C5 - B4 - C5 - B4 - A4
    notes = [
        (0.00, 493.88, 0.22), (0.22, 440.00, 0.22), (0.44, 493.88, 0.35), (0.80, 329.63, 0.60),
        (1.45, 523.25, 0.22), (1.68, 493.88, 0.22)
    ]
    if not is_preview:
        notes += [
            (1.90, 523.25, 0.25), (2.15, 493.88, 0.25), (2.40, 440.00, 0.60),
            (3.05, 493.88, 0.35), (3.40, 440.00, 0.40)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='trumpet')
    return buf
TRACK_DEFINITIONS['INS009'] = ('The Final Countdown', track_final_countdown)

# 16. INS013 - Clarinet -> Mozart Clarinet Concerto
def track_mozart_clarinet(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Adagio in A: C#5 - B4 - A4 - G#4 - A4 - B4 - E4
    notes = [
        (0.00, 554.37, 0.65), (0.65, 493.88, 0.45), (1.10, 440.00, 0.55), (1.65, 415.30, 0.45)
    ]
    if not is_preview:
        notes += [
            (2.10, 440.00, 0.45), (2.55, 493.88, 0.50), (3.05, 329.63, 0.90)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='clarinet')
    return buf
TRACK_DEFINITIONS['INS013'] = ('Mozart Clarinet Concerto', track_mozart_clarinet)

# 17. INS014 - Harmonica -> Once Upon a Time in the West
def track_once_upon_a_time(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 392.00, 0.65), # G4
        (0.70, 466.16, 0.55), # Bb4
        (1.25, 523.25, 0.85)  # C5 (with bend)
    ]
    if not is_preview:
        notes += [
            (2.15, 466.16, 0.55), # Bb4
            (2.70, 392.00, 0.65), # G4
            (3.35, 349.23, 0.75)  # F4
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='harmonica', vibrato=0.015)
    return buf
TRACK_DEFINITIONS['INS014'] = ('Once Upon a Time in the West', track_once_upon_a_time)

# 18. INS024 - Oboe -> Gabriel's Oboe
def track_gabriels_oboe(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 293.66, 0.4), (0.40, 369.99, 0.4), (0.80, 440.00, 0.4),
        (1.20, 587.33, 0.7), (1.90, 554.37, 0.4)
    ]
    if not is_preview:
        notes += [
            (2.30, 493.88, 0.4), (2.70, 440.00, 0.5), (3.20, 392.00, 0.4), (3.60, 369.99, 0.5)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='oboe')
    return buf
TRACK_DEFINITIONS['INS024'] = ('Gabriel\'s Oboe', track_gabriels_oboe)

# 19. INS025 - Trombone -> When the Saints Go Marching In
def track_saints_go_marching_in(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # C3 - E3 - F3 - G3
    notes = [
        (0.00, 130.81, 0.25), (0.28, 164.81, 0.25), (0.56, 174.61, 0.25), (0.84, 196.00, 0.65),
        (1.50, 130.81, 0.25), (1.75, 164.81, 0.25)
    ]
    if not is_preview:
        notes += [
            (2.00, 174.61, 0.25), (2.25, 196.00, 0.65),
            (2.95, 164.81, 0.25), (3.20, 130.81, 0.25), (3.45, 146.83, 0.45)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.6, timbre='trombone')
    return buf
TRACK_DEFINITIONS['INS025'] = ('When the Saints Go Marching In', track_saints_go_marching_in)

# 20. INS026 - Tuba -> The Liberty Bell
def track_liberty_bell(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 87.31, 0.25), (0.35, 130.81, 0.25), (0.70, 87.31, 0.25), (1.05, 130.81, 0.25),
        (1.40, 110.00, 0.25), (1.70, 116.54, 0.25)
    ]
    if not is_preview:
        notes += [
            (2.05, 130.81, 0.35), (2.45, 87.31, 0.45),
            (2.95, 87.31, 0.25), (3.30, 130.81, 0.25)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.65, timbre='tuba')
    return buf
TRACK_DEFINITIONS['INS026'] = ('The Liberty Bell', track_liberty_bell)

# 21. 103 - Roland TD-17KVX Electronic Drum -> Believer – Imagine Dragons
def track_believer(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Stomp - Stomp - Clap modern electronic groove
    add_drum_kick(buf, 0.00, vol=1.0)
    add_drum_kick(buf, 0.35, vol=0.9)
    add_drum_snare(buf, 0.70, vol=0.95)
    add_drum_kick(buf, 1.05, vol=1.0)
    add_drum_snare(buf, 1.40, vol=0.9)
    add_drum_hihat(buf, 1.75, vol=0.6)
    if not is_preview:
        add_drum_kick(buf, 2.00, vol=1.0)
        add_drum_kick(buf, 2.35, vol=0.9)
        add_drum_snare(buf, 2.70, vol=0.95)
        add_drum_kick(buf, 3.05, vol=1.0)
        add_drum_snare(buf, 3.40, vol=0.9)
    return buf
TRACK_DEFINITIONS['103'] = ('Believer – Imagine Dragons', track_believer)

# 22. INS004 - Drum Kit -> In the End – Linkin Park
def track_in_the_end(is_preview=False):
    length = 2.0 if is_preview else 4.0
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Kick - Hat - Snare - Kick - Kick - Snare
    add_drum_kick(buf, 0.00, vol=0.9)
    add_drum_hihat(buf, 0.25, vol=0.5)
    add_drum_snare(buf, 0.50, vol=0.85)
    add_drum_hihat(buf, 0.75, vol=0.5)
    add_drum_kick(buf, 1.00, vol=0.9)
    add_drum_kick(buf, 1.25, vol=0.85)
    add_drum_snare(buf, 1.50, vol=0.85)
    add_drum_hihat(buf, 1.75, vol=0.5)
    if not is_preview:
        for bar in [2.0]:
            add_drum_kick(buf, bar + 0.00, vol=0.9)
            add_drum_hihat(buf, bar + 0.25, vol=0.5)
            add_drum_snare(buf, bar + 0.50, vol=0.85)
            add_drum_hihat(buf, bar + 0.75, vol=0.5)
            add_drum_kick(buf, bar + 1.00, vol=0.9)
            add_drum_kick(buf, bar + 1.25, vol=0.85)
            add_drum_snare(buf, bar + 1.50, vol=0.85)
            add_drum_hihat(buf, bar + 1.75, vol=0.5)
    return buf
TRACK_DEFINITIONS['INS004'] = ('In the End – Linkin Park', track_in_the_end)

# 23. 104 - Yamaha P-45 Digital Piano -> River Flows in You
def track_river_flows_in_you(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # A4 - G#4 - A4 - E5 - A4 - D5 - C#5 - B4
    notes = [
        (0.00, 440.00, 0.24), (0.24, 415.30, 0.24), (0.48, 440.00, 0.40), (0.90, 659.25, 0.55),
        (1.48, 440.00, 0.24), (1.72, 587.33, 0.35)
    ]
    if not is_preview:
        notes += [
            (2.10, 554.37, 0.45), (2.60, 493.88, 0.60),
            (3.20, 440.00, 0.40), (3.60, 415.30, 0.45)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='digital_piano')
    return buf
TRACK_DEFINITIONS['104'] = ('River Flows in You', track_river_flows_in_you)

# 24. INS002 - Piano -> Für Elise
def track_fur_elise(is_preview=False):
    length = 2.2 if is_preview else 4.0
    buf = [0.0] * int(SAMPLE_RATE * length)
    # E5 - D#5 - E5 - D#5 - E5 - B4 - D5 - C5 - A4
    notes = [
        (0.00, 659.25, 0.2), (0.20, 622.25, 0.2), (0.40, 659.25, 0.2),
        (0.60, 622.25, 0.2), (0.80, 659.25, 0.2), (1.00, 493.88, 0.2),
        (1.20, 587.33, 0.2), (1.40, 523.25, 0.2), (1.60, 440.00, 0.6)
    ]
    if not is_preview:
        notes += [
            (2.30, 261.63, 0.2), (2.50, 329.63, 0.2), (2.70, 440.00, 0.2), (2.90, 493.88, 0.5)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='piano')
    return buf
TRACK_DEFINITIONS['INS002'] = ('Für Elise', track_fur_elise)

# 25. INS006 - Keyboard -> Faded – Alan Walker
def track_faded(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # D#5 - F#5 - G#5 - D#5 - C#5 - A#4 - B4
    notes = [
        (0.00, 622.25, 0.25), (0.28, 739.99, 0.25), (0.56, 830.61, 0.40),
        (1.00, 622.25, 0.25), (1.30, 554.37, 0.35), (1.68, 466.16, 0.25)
    ]
    if not is_preview:
        notes += [
            (1.95, 493.88, 0.50), (2.50, 622.25, 0.30), (2.85, 739.99, 0.30),
            (3.20, 830.61, 0.55)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='synth')
    return buf
TRACK_DEFINITIONS['INS006'] = ('Faded – Alan Walker', track_faded)

# 26. INS022 - Accordion -> La Vie en Rose
def track_la_vie_en_rose(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # French waltz melody
    notes = [
        (0.00, 392.00, 0.45), (0.45, 440.00, 0.45), (0.90, 493.88, 0.50), (1.45, 523.25, 0.65)
    ]
    if not is_preview:
        notes += [
            (2.15, 493.88, 0.45), (2.60, 440.00, 0.45), (3.05, 392.00, 0.70)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.55, timbre='accordion')
    return buf
TRACK_DEFINITIONS['INS022'] = ('La Vie en Rose', track_la_vie_en_rose)

# 27. INS023 - Organ -> Phantom of the Opera
def track_phantom_of_the_opera(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Dramatic descending chromatic scale: D4 - C#4 - C4 - B3 - Bb3 - A3
    notes = [
        (0.00, 293.66, 0.28), (0.30, 277.18, 0.28), (0.60, 261.63, 0.28),
        (0.90, 246.94, 0.28), (1.20, 233.08, 0.35), (1.58, 220.00, 0.70)
    ]
    if not is_preview:
        notes += [
            (2.40, 293.66, 0.30), (2.75, 277.18, 0.30), (3.10, 261.63, 0.60)
        ]
    for t, f, d in notes:
        add_tone(buf, t, f, dur=d, vol=0.65, timbre='organ')
    return buf
TRACK_DEFINITIONS['INS023'] = ('Phantom of the Opera', track_phantom_of_the_opera)

# 28. INS011 - Tabla -> Taal Teentaal
def track_taal_teentaal(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Dha - Dhin - Dhin - Dha
    beats = [
        (0.00, 'dha'), (0.35, 'dhin'), (0.70, 'dhin'), (1.05, 'dha'),
        (1.45, 'dha'), (1.80, 'tin')
    ]
    if not is_preview:
        beats += [
            (2.15, 'tin'), (2.50, 'ta'), (2.90, 'ta'), (3.25, 'dhin'), (3.60, 'dhin'), (3.95, 'dha')
        ]
    for t, stroke in beats:
        if stroke == 'dha':
            add_tabla_bayan(buf, t, vol=0.85)
            add_tabla_dayan(buf, t, pitch=320.0, vol=0.65)
        elif stroke == 'dhin':
            add_tabla_bayan(buf, t, vol=0.6)
            add_tabla_dayan(buf, t, pitch=320.0, vol=0.75)
        elif stroke == 'tin':
            add_tabla_dayan(buf, t, pitch=340.0, vol=0.65)
        elif stroke == 'ta':
            add_tabla_dayan(buf, t, pitch=420.0, vol=0.85)
    return buf
TRACK_DEFINITIONS['INS011'] = ('Taal Teentaal', track_taal_teentaal)

# 29. INS012 - Mridangam -> Carnatic Thani Avarthanam
def track_thani_avarthanam(is_preview=False):
    length = 2.2 if is_preview else 4.2
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Tha - Dhi - Gi - Na - Thom
    strokes = [
        (0.00, 'tha'), (0.28, 'dhi'), (0.56, 'gi'), (0.84, 'na'), (1.15, 'thom'),
        (1.55, 'tha'), (1.80, 'dhi')
    ]
    if not is_preview:
        strokes += [
            (2.10, 'gi'), (2.35, 'na'), (2.65, 'thom'), (3.10, 'tha'), (3.40, 'thom')
        ]
    for t, s in strokes:
        if s == 'thom':
            add_tabla_bayan(buf, t, vol=0.9) # Deep Thoppi resonance
        elif s == 'dhi':
            add_tabla_dayan(buf, t, pitch=300.0, vol=0.8)
        elif s == 'na':
            add_tabla_dayan(buf, t, pitch=400.0, vol=0.75)
        else: # tha, gi
            add_tabla_dayan(buf, t, pitch=350.0, vol=0.6)
    return buf
TRACK_DEFINITIONS['INS012'] = ('Carnatic Thani Avarthanam', track_thani_avarthanam)

# 30. INS019 - Djembe -> African Drum Rhythm
def track_african_drum_rhythm(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Bass - Open - Slap - Bass - Bass - Slap
    beats = [
        (0.00, 'bass'), (0.30, 'open'), (0.60, 'slap'), (0.90, 'bass'),
        (1.20, 'bass'), (1.50, 'slap')
    ]
    if not is_preview:
        beats += [
            (1.85, 'open'), (2.15, 'open'), (2.45, 'slap'), (2.75, 'bass'),
            (3.05, 'slap'), (3.35, 'open')
        ]
    for t, b in beats:
        add_djembe_hit(buf, t, hit_type=b, vol=0.8)
    return buf
TRACK_DEFINITIONS['INS019'] = ('African Drum Rhythm', track_african_drum_rhythm)

# 31. INS020 - Conga -> Oye Como Va
def track_oye_como_va(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Latin Cha-cha-chá conga tumbao: Tuk - Pak - Tuk - Boom - Boom
    beats = [
        (0.00, 'slap'), (0.25, 'open'), (0.50, 'slap'), (0.75, 'bass'), (1.00, 'bass'),
        (1.25, 'slap'), (1.50, 'open'), (1.75, 'slap')
    ]
    if not is_preview:
        beats += [
            (2.00, 'slap'), (2.25, 'open'), (2.50, 'slap'), (2.75, 'bass'), (3.00, 'bass'),
            (3.25, 'slap'), (3.50, 'open')
        ]
    for t, b in beats:
        add_djembe_hit(buf, t, hit_type=b, vol=0.75)
    return buf
TRACK_DEFINITIONS['INS020'] = ('Oye Como Va', track_oye_como_va)

# 32. INS021 - Xylophone -> Dance of the Sugar Plum Fairy
def track_sugar_plum_fairy(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # B5 - F#5 - D#5 - B4 - G5 - E5 - C5 - A4
    notes = [
        (0.00, 987.77), (0.22, 739.99), (0.44, 622.25), (0.66, 493.88),
        (0.95, 783.99), (1.17, 659.25), (1.39, 523.25), (1.61, 440.00)
    ]
    if not is_preview:
        notes += [
            (1.95, 987.77), (2.17, 739.99), (2.39, 622.25), (2.61, 493.88),
            (2.90, 880.00), (3.15, 739.99), (3.40, 587.33)
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.35, vol=0.55, timbre='xylophone')
    return buf
TRACK_DEFINITIONS['INS021'] = ('Dance of the Sugar Plum Fairy', track_sugar_plum_fairy)

# 33. INS029 - Tambourine -> Jingle Bells
def track_jingle_bells(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    # Jing - Jing - Jing | Jing - Jing - Jing
    beats = [
        0.00, 0.28, 0.56, 1.00, 1.28, 1.56
    ]
    if not is_preview:
        beats += [
            2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50
        ]
    for t in beats:
        add_tone(buf, t, 10000.0, dur=0.15, vol=0.7, timbre='tambourine')
    return buf
TRACK_DEFINITIONS['INS029'] = ('Jingle Bells', track_jingle_bells)

# 34. INS030 - Triangle -> Orchestral Triangle Music
def track_orchestral_triangle(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    strikes = [
        0.00, 0.60, 1.20
    ]
    if not is_preview:
        strikes += [
            1.80, 2.40, 2.70, 3.00, 3.30
        ]
    for t in strikes:
        add_tone(buf, t, 7500.0, dur=0.7, vol=0.65, timbre='triangle')
    return buf
TRACK_DEFINITIONS['INS030'] = ('Orchestral Triangle Music', track_orchestral_triangle)

# 35. 1 - Kavin -> Acoustic Melody
def track_kavin(is_preview=False):
    length = 2.0 if is_preview else 3.8
    buf = [0.0] * int(SAMPLE_RATE * length)
    notes = [
        (0.00, 261.63), (0.28, 329.63), (0.56, 392.00), (0.84, 523.25),
        (1.20, 392.00), (1.50, 329.63)
    ]
    if not is_preview:
        notes += [
            (1.90, 293.66), (2.18, 349.23), (2.46, 440.00), (2.74, 587.33),
            (3.10, 523.25)
        ]
    for t, f in notes:
        add_tone(buf, t, f, dur=0.5, vol=0.5, timbre='acoustic_guitar')
    return buf
TRACK_DEFINITIONS['1'] = ('Acoustic Melody', track_kavin)


# =========================================================================
# MAIN GENERATION PROCESS
# =========================================================================
def generate_all():
    print(f"Beginning synthesis of all {len(TRACK_DEFINITIONS)} iconic music tracks...")

    # Map ID to canonical audio filename
    for inst_id, (track_name, gen_fn) in TRACK_DEFINITIONS.items():
        # 1. Save as track_{id}.wav
        samples_full = gen_fn(is_preview=False)
        write_wav(f"track_{inst_id.lower()}.wav", samples_full)

        samples_prev = gen_fn(is_preview=True)
        write_wav(f"track_{inst_id.lower()}_preview.wav", samples_prev)

    # Also maintain compatibility by linking key names
    key_mapping = {
        'drum_kit': 'INS004',
        'tabla': 'INS011',
        'guitar': 'INS001',
        'electric_guitar': '101',
        'piano': 'INS002',
        'flute': 'INS005',
        'violin': 'INS003',
        'sitar': 'INS027',
        'saxophone': 'INS008',
        'xylophone': 'INS021',
        'ukulele': 'INS007',
        'cello': 'INS010',
        'banjo': 'INS015',
        'mandolin': 'INS016',
        'bass_guitar': 'INS018',
        'veena': 'INS028',
        'trumpet': 'INS009',
        'clarinet': 'INS013',
        'harmonica': 'INS014',
        'oboe': 'INS024',
        'trombone': 'INS025',
        'tuba': 'INS026',
        'accordion': 'INS022',
        'organ': 'INS023',
        'mridangam': 'INS012',
        'djembe': 'INS019'
    }

    import shutil
    for key, source_id in key_mapping.items():
        src_full = os.path.join("static", "audio", f"track_{source_id.lower()}.wav")
        dst_full = os.path.join("static", "audio", f"{key}.wav")
        if os.path.exists(src_full):
            shutil.copyfile(src_full, dst_full)

        src_prev = os.path.join("static", "audio", f"track_{source_id.lower()}_preview.wav")
        dst_prev = os.path.join("static", "audio", f"{key}_preview.wav")
        if os.path.exists(src_prev):
            shutil.copyfile(src_prev, dst_prev)

    print("\n[SUCCESS] All 35 iconic music tracks synthesized and saved to static/audio/!")

if __name__ == '__main__':
    generate_all()
