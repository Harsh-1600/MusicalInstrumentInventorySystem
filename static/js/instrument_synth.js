/**
 * SoundCraft Studio Instrument Audio Engine
 * Combines authentic high-fidelity studio WAV audio recordings for every instrument
 * with zero-latency HTML5 Web Audio API synthesis for interactive playable note keys.
 * 100% dependency-free.
 */

const SoundCraftSynth = (function () {
    let audioCtx = null;
    let currentAudio = null;
    let activeTimeouts = [];
    let isPlayingDemo = false;

    // Standard musical note frequencies in Hz (Middle Octave C4 to C5)
    const NOTES = {
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
        'C6': 1046.50
    };

    /**
     * Initializes or resumes the AudioContext on first user interaction
     */
    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            audioCtx = new AudioContextClass();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    /**
     * Complete mapping of each instrument to its specific iconic music track
     */
    const TRACK_INFO_MAP = {
        '1': { track: 'Acoustic Melody', file: 'track_1' },
        '101': { track: "Sweet Child O' Mine", file: 'track_101' },
        '102': { track: 'My Heart Will Go On', file: 'track_102' },
        '103': { track: 'Believer – Imagine Dragons', file: 'track_103' },
        '104': { track: 'River Flows in You', file: 'track_104' },
        'INS001': { track: 'Hotel California', file: 'track_ins001' },
        'INS002': { track: 'Für Elise', file: 'track_ins002' },
        'INS003': { track: 'Canon in D', file: 'track_ins003' },
        'INS004': { track: 'In the End – Linkin Park', file: 'track_ins004' },
        'INS005': { track: 'Titanic Flute Theme', file: 'track_ins005' },
        'INS006': { track: 'Faded – Alan Walker', file: 'track_ins006' },
        'INS007': { track: 'Somewhere Over the Rainbow', file: 'track_ins007' },
        'INS008': { track: 'Careless Whisper', file: 'track_ins008' },
        'INS009': { track: 'The Final Countdown', file: 'track_ins009' },
        'INS010': { track: 'The Swan', file: 'track_ins010' },
        'INS011': { track: 'Taal Teentaal', file: 'track_ins011' },
        'INS012': { track: 'Carnatic Thani Avarthanam', file: 'track_ins012' },
        'INS013': { track: 'Mozart Clarinet Concerto', file: 'track_ins013' },
        'INS014': { track: 'Once Upon a Time in the West', file: 'track_ins014' },
        'INS015': { track: 'Dueling Banjos', file: 'track_ins015' },
        'INS016': { track: 'Losing My Religion', file: 'track_ins016' },
        'INS017': { track: "Sweet Child O' Mine", file: 'track_ins017' },
        'INS018': { track: 'Another One Bites the Dust', file: 'track_ins018' },
        'INS019': { track: 'African Drum Rhythm', file: 'track_ins019' },
        'INS020': { track: 'Oye Como Va', file: 'track_ins020' },
        'INS021': { track: 'Dance of the Sugar Plum Fairy', file: 'track_ins021' },
        'INS022': { track: 'La Vie en Rose', file: 'track_ins022' },
        'INS023': { track: 'Phantom of the Opera', file: 'track_ins023' },
        'INS024': { track: "Gabriel's Oboe", file: 'track_ins024' },
        'INS025': { track: 'When the Saints Go Marching In', file: 'track_ins025' },
        'INS026': { track: 'The Liberty Bell', file: 'track_ins026' },
        'INS027': { track: 'Raga Yaman', file: 'track_ins027' },
        'INS028': { track: 'Vatapi Ganapatim', file: 'track_ins028' },
        'INS029': { track: 'Jingle Bells', file: 'track_ins029' },
        'INS030': { track: 'Orchestral Triangle Music', file: 'track_ins030' }
    };

    /**
     * Gets the iconic track title for any instrument
     */
    function getTrackName(category, name, instrumentId) {
        if (instrumentId) {
            const idKey = String(instrumentId).trim().toUpperCase();
            if (TRACK_INFO_MAP[idKey]) return TRACK_INFO_MAP[idKey].track;
        }
        const n = (name || '').toLowerCase();
        if (n.includes('les paul')) return "Sweet Child O' Mine";
        if (n.includes('hotel california') || n.includes('acoustic guitar') || n === 'guitar') return 'Hotel California';
        if (n.includes('canon')) return 'Canon in D';
        if (n.includes('rainbow') || n.includes('ukulele')) return 'Somewhere Over the Rainbow';
        if (n.includes('swan') || n.includes('cello')) return 'The Swan';
        if (n.includes('banjo')) return 'Dueling Banjos';
        if (n.includes('mandolin')) return 'Losing My Religion';
        if (n.includes('nothing else') || n.includes('electric guitar')) return 'Nothing Else Matters';
        if (n.includes('bites the dust') || n.includes('bass')) return 'Another One Bites the Dust';
        if (n.includes('sitar')) return 'Raga Yaman';
        if (n.includes('veena')) return 'Vatapi Ganapatim';
        if (n.includes('flute') && (n.includes('yamaha') || n.includes('222'))) return 'My Heart Will Go On';
        if (n.includes('flute')) return 'Titanic Flute Theme';
        if (n.includes('sax')) return 'Careless Whisper';
        if (n.includes('trumpet')) return 'The Final Countdown';
        if (n.includes('clarinet')) return 'Mozart Clarinet Concerto';
        if (n.includes('harmonica')) return 'Once Upon a Time in the West';
        if (n.includes('oboe')) return "Gabriel's Oboe";
        if (n.includes('trombone')) return 'When the Saints Go Marching In';
        if (n.includes('tuba')) return 'The Liberty Bell';
        if (n.includes('believer') || n.includes('electronic drum')) return 'Believer – Imagine Dragons';
        if (n.includes('linkin') || n.includes('drum kit') || n.includes('drum set')) return 'In the End – Linkin Park';
        if (n.includes('river flows') || n.includes('digital piano') || n.includes('p-45')) return 'River Flows in You';
        if (n.includes('elise') || n.includes('piano')) return 'Für Elise';
        if (n.includes('faded') || n.includes('keyboard')) return 'Faded – Alan Walker';
        if (n.includes('accordion')) return 'La Vie en Rose';
        if (n.includes('organ')) return 'Phantom of the Opera';
        if (n.includes('tabla')) return 'Taal Teentaal';
        if (n.includes('mridangam')) return 'Carnatic Thani Avarthanam';
        if (n.includes('djembe')) return 'African Drum Rhythm';
        if (n.includes('conga')) return 'Oye Como Va';
        if (n.includes('xylophone')) return 'Dance of the Sugar Plum Fairy';
        if (n.includes('tambourine')) return 'Jingle Bells';
        if (n.includes('triangle')) return 'Orchestral Triangle Music';
        return `${name || category} Live Solo`;
    }

    /**
     * Maps each instrument to its authentic studio audio file
     */
    function getAudioFileKey(category, name, instrumentId) {
        if (instrumentId) {
            const idKey = String(instrumentId).trim().toUpperCase();
            if (TRACK_INFO_MAP[idKey]) return TRACK_INFO_MAP[idKey].file;
        }

        const n = (name || '').toLowerCase();
        const c = (category || '').toLowerCase();

        // Specific named models
        if (n.includes('les paul')) return 'track_101';
        if (n.includes('electronic drum') || (c.includes('electronic') && n.includes('drum'))) return 'track_103';
        if (n.includes('digital piano') || n.includes('p-45')) return 'track_104';
        if (n.includes('flute') && (n.includes('yamaha') || n.includes('222'))) return 'track_102';

        // Direct instrument associations
        if (n.includes('drum kit') || n.includes('drum set')) return 'track_ins004';
        if (n.includes('tabla')) return 'track_ins011';
        if (n.includes('mridangam')) return 'track_ins012';
        if (n.includes('djembe')) return 'track_ins019';
        if (n.includes('conga')) return 'track_ins020';
        if (n.includes('xylophone')) return 'track_ins021';
        if (n.includes('tambourine')) return 'track_ins029';
        if (n.includes('triangle')) return 'track_ins030';
        if (n.includes('sitar')) return 'track_ins027';
        if (n.includes('veena')) return 'track_ins028';
        if (n.includes('bass guitar') || (c.includes('string') && n.includes('bass'))) return 'track_ins018';
        if (n.includes('electric guitar')) return 'track_ins017';
        if (n.includes('ukulele')) return 'track_ins007';
        if (n.includes('banjo')) return 'track_ins015';
        if (n.includes('mandolin')) return 'track_ins016';
        if (n.includes('guitar')) return 'track_ins001';
        if (n.includes('cello')) return 'track_ins010';
        if (n.includes('violin')) return 'track_ins003';
        if (n.includes('piano')) return 'track_ins002';
        if (n.includes('keyboard')) return 'track_ins006';
        if (n.includes('organ')) return 'track_ins023';
        if (n.includes('accordion')) return 'track_ins022';
        if (n.includes('flute')) return 'track_ins005';
        if (n.includes('clarinet')) return 'track_ins013';
        if (n.includes('harmonica')) return 'track_ins014';
        if (n.includes('oboe')) return 'track_ins024';
        if (n.includes('saxophone')) return 'track_ins008';
        if (n.includes('trumpet')) return 'track_ins009';
        if (n.includes('trombone')) return 'track_ins025';
        if (n.includes('tuba')) return 'track_ins026';

        // Category fallbacks
        if (c.includes('percussion')) return 'track_ins004';
        if (c.includes('wind')) return 'track_ins005';
        if (c.includes('keyboard')) return 'track_ins002';
        if (c.includes('string')) return 'track_ins001';
        return 'track_ins001';
    }

    /**
     * Compatible instrument family identifier for synthesis
     */
    function getInstrumentType(category, name) {
        const key = getAudioFileKey(category, name);
        if (key === 'sitar' || key === 'veena') return 'sitar';
        if (key === 'violin' || key === 'cello') return 'bowed';
        if (key === 'piano' || key === 'organ' || key === 'accordion') return 'piano';
        if (key === 'flute' || key === 'clarinet' || key === 'harmonica') return 'woodwind';
        if (key === 'saxophone' || key === 'trumpet') return 'brass';
        if (key === 'drum_kit' || key === 'tabla' || key === 'mridangam' || key === 'djembe' || key === 'xylophone') return 'percussion';
        return 'plucked';
    }

    /**
     * Plays a single synthesized note in the instrument's authentic timbre
     */
    function playTone(freq, duration = 0.8, category = '', instrumentName = '', volume = 0.35) {
        const ctx = getAudioContext();
        const type = getInstrumentType(category, instrumentName);
        const now = ctx.currentTime;

        const masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(volume, now);
        masterGain.connect(ctx.destination);

        switch (type) {
            case 'piano': {
                const osc1 = ctx.createOscillator();
                const osc2 = ctx.createOscillator();
                const gain = ctx.createGain();
                osc1.type = 'triangle';
                osc1.frequency.setValueAtTime(freq, now);
                osc2.type = 'sine';
                osc2.frequency.setValueAtTime(freq * 2, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume * 1.1, now + 0.012);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(masterGain);
                osc1.start(now);
                osc2.start(now);
                osc1.stop(now + duration);
                osc2.stop(now + duration);
                break;
            }

            case 'bowed': {
                const osc = ctx.createOscillator();
                const filter = ctx.createBiquadFilter();
                const gain = ctx.createGain();
                const lfo = ctx.createOscillator();
                const lfoGain = ctx.createGain();
                lfo.frequency.setValueAtTime(5.8, now);
                lfoGain.gain.setValueAtTime(freq * 0.02, now);
                lfo.connect(osc.frequency);
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(freq, now);
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(freq * 3.5, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume * 0.85, now + 0.08);
                gain.gain.linearRampToValueAtTime(0.0001, now + duration);
                osc.connect(filter);
                filter.connect(gain);
                gain.connect(masterGain);
                lfo.start(now);
                osc.start(now);
                lfo.stop(now + duration);
                osc.stop(now + duration);
                break;
            }

            case 'woodwind': {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume * 0.9, now + 0.05);
                gain.gain.linearRampToValueAtTime(0.0001, now + duration);
                osc.connect(gain);
                gain.connect(masterGain);
                osc.start(now);
                osc.stop(now + duration);
                break;
            }

            case 'brass': {
                const osc = ctx.createOscillator();
                const filter = ctx.createBiquadFilter();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(freq, now);
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(freq * 4.5, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume, now + 0.035);
                gain.gain.linearRampToValueAtTime(0.0001, now + duration);
                osc.connect(filter);
                filter.connect(gain);
                gain.connect(masterGain);
                osc.start(now);
                osc.stop(now + duration);
                break;
            }

            case 'sitar': {
                const osc1 = ctx.createOscillator();
                const osc2 = ctx.createOscillator();
                const gain = ctx.createGain();
                osc1.type = 'sawtooth';
                osc1.frequency.setValueAtTime(freq, now);
                osc1.frequency.linearRampToValueAtTime(freq * 1.03, now + 0.06);
                osc1.frequency.linearRampToValueAtTime(freq, now + 0.2);
                osc2.type = 'sine';
                osc2.frequency.setValueAtTime(freq * 3.98, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume * 1.1, now + 0.015);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + duration * 1.2);
                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(masterGain);
                osc1.start(now);
                osc2.start(now);
                osc1.stop(now + duration * 1.2);
                osc2.stop(now + duration * 1.2);
                break;
            }

            case 'percussion': {
                const key = getAudioFileKey(category, instrumentName);
                if (key === 'tabla' || key === 'mridangam') {
                    // Authentic Indian Classical Tabla Strokes (Bayan & Dayan)
                    if (freq < 280 || (freq > 370 && freq < 410) || freq > 500) {
                        // "Dha" / "Ghe" - Deep Bayan Bass Modulation
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(140, now);
                        osc.frequency.exponentialRampToValueAtTime(65, now + 0.12);
                        gain.gain.setValueAtTime(volume * 1.5, now);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);
                        osc.connect(gain);
                        gain.connect(masterGain);
                        osc.start(now);
                        osc.stop(now + 0.45);

                        // Accompanying Dayan rim ring for "Dha"
                        const oscD = ctx.createOscillator();
                        const gainD = ctx.createGain();
                        oscD.type = 'sine';
                        oscD.frequency.setValueAtTime(320, now);
                        gainD.gain.setValueAtTime(volume * 0.7, now);
                        gainD.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);
                        oscD.connect(gainD);
                        gainD.connect(masterGain);
                        oscD.start(now);
                        oscD.stop(now + 0.28);
                    } else if (freq < 335) {
                        // "Dhin" - Sustained Dayan Bell Chime
                        const osc1 = ctx.createOscillator();
                        const osc2 = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc1.type = 'sine';
                        osc1.frequency.setValueAtTime(320, now);
                        osc2.type = 'sine';
                        osc2.frequency.setValueAtTime(320 * 2.89, now);
                        gain.gain.setValueAtTime(volume * 1.1, now);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.55);
                        osc1.connect(gain);
                        osc2.connect(gain);
                        gain.connect(masterGain);
                        osc1.start(now);
                        osc2.start(now);
                        osc1.stop(now + 0.55);
                        osc2.stop(now + 0.55);
                    } else {
                        // "Ta" / "Tin" - Crisp Rim Stroke
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(420, now);
                        gain.gain.setValueAtTime(volume * 1.2, now);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
                        osc.connect(gain);
                        gain.connect(masterGain);
                        osc.start(now);
                        osc.stop(now + 0.22);
                    }
                } else {
                    // Drum Kit & Western Percussion (Kick, Snare, Hi-Hat, Toms, Crash)
                    if (freq < 275) {
                        // Kick Drum (Deep punchy 160Hz -> 45Hz sub-bass)
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(160, now);
                        osc.frequency.exponentialRampToValueAtTime(45, now + 0.08);
                        gain.gain.setValueAtTime(volume * 1.8, now);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
                        osc.connect(gain);
                        gain.connect(masterGain);
                        osc.start(now);
                        osc.stop(now + 0.35);
                    } else if (freq < 310) {
                        // Snare Drum (185Hz body + White Noise Wire Rattle)
                        const osc = ctx.createOscillator();
                        const oscGain = ctx.createGain();
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(185, now);
                        oscGain.gain.setValueAtTime(volume * 0.9, now);
                        oscGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
                        osc.connect(oscGain);
                        oscGain.connect(masterGain);
                        osc.start(now);
                        osc.stop(now + 0.18);

                        // White Noise Burst
                        const bufferSize = ctx.sampleRate * 0.18;
                        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                        const output = buffer.getChannelData(0);
                        for (let i = 0; i < bufferSize; i++) {
                            output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.04));
                        }
                        const whiteNoise = ctx.createBufferSource();
                        whiteNoise.buffer = buffer;
                        const filter = ctx.createBiquadFilter();
                        filter.type = 'highpass';
                        filter.frequency.value = 1000;
                        const noiseGain = ctx.createGain();
                        noiseGain.gain.setValueAtTime(volume * 1.2, now);
                        noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
                        whiteNoise.connect(filter);
                        filter.connect(noiseGain);
                        noiseGain.connect(masterGain);
                        whiteNoise.start(now);
                    } else if (freq < 360) {
                        // Closed Hi-Hat (Crisp Metallic Noise)
                        const bufferSize = ctx.sampleRate * 0.06;
                        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                        const output = buffer.getChannelData(0);
                        for (let i = 0; i < bufferSize; i++) {
                            output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.015));
                        }
                        const hihat = ctx.createBufferSource();
                        hihat.buffer = buffer;
                        const filter = ctx.createBiquadFilter();
                        filter.type = 'highpass';
                        filter.frequency.value = 7500;
                        const hGain = ctx.createGain();
                        hGain.gain.setValueAtTime(volume * 0.9, now);
                        hGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
                        hihat.connect(filter);
                        filter.connect(hGain);
                        hGain.connect(masterGain);
                        hihat.start(now);
                    } else if (freq < 450) {
                        // Rack & Floor Toms (Resonant downward sweep)
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(freq * 0.6, now);
                        osc.frequency.exponentialRampToValueAtTime(freq * 0.35, now + 0.15);
                        gain.gain.setValueAtTime(volume * 1.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);
                        osc.connect(gain);
                        gain.connect(masterGain);
                        osc.start(now);
                        osc.stop(now + 0.28);
                    } else {
                        // Crash Cymbal (High Frequency Sizzle Wash)
                        const bufferSize = ctx.sampleRate * 0.4;
                        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                        const output = buffer.getChannelData(0);
                        for (let i = 0; i < bufferSize; i++) {
                            output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.12));
                        }
                        const cymbal = ctx.createBufferSource();
                        cymbal.buffer = buffer;
                        const filter = ctx.createBiquadFilter();
                        filter.type = 'highpass';
                        filter.frequency.value = 5000;
                        const cGain = ctx.createGain();
                        cGain.gain.setValueAtTime(volume * 0.85, now);
                        cGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.4);
                        cymbal.connect(filter);
                        filter.connect(cGain);
                        cGain.connect(masterGain);
                        cymbal.start(now);
                    }
                }
                break;
            }

            case 'plucked':
            default: {
                const osc = ctx.createOscillator();
                const filter = ctx.createBiquadFilter();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(freq, now);
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(freq * 5, now);
                gain.gain.setValueAtTime(0.001, now);
                gain.gain.linearRampToValueAtTime(volume * 1.2, now + 0.008);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
                osc.connect(filter);
                filter.connect(gain);
                gain.connect(masterGain);
                osc.start(now);
                osc.stop(now + duration);
                break;
            }
        }
    }

    /**
     * Stops any currently playing audio demo
     */
    function stopDemo() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }

        activeTimeouts.forEach(t => clearTimeout(t));
        activeTimeouts = [];
        isPlayingDemo = false;

        const visualizer = document.getElementById('soundVisualizer');
        if (visualizer) visualizer.classList.remove('active');

        const btnPlay = document.getElementById('btnPlayDemo');
        if (btnPlay) {
            btnPlay.classList.remove('is-playing');
            const icon = document.getElementById('playIcon');
            const text = document.getElementById('playText');
            if (icon) icon.textContent = '▶️';
            if (text) text.textContent = 'Play Melody Demo';
        }

        const statusLabel = document.getElementById('soundStatusMsg');
        if (statusLabel) {
            statusLabel.textContent = 'Click "Play Melody Demo" or try note keys below';
            statusLabel.style.color = '#64748b';
        }
    }

    /**
     * Plays authentic studio audio recording for the instrument's iconic track
     */
    function playDemo(category, instrumentName, instrumentId) {
        if (isPlayingDemo) {
            stopDemo();
            return;
        }

        stopDemo();
        isPlayingDemo = true;

        const key = getAudioFileKey(category, instrumentName, instrumentId);
        const trackName = getTrackName(category, instrumentName, instrumentId);
        const audioUrl = `/static/audio/${key}.wav?v=20261125_iconic_v4`;

        const visualizer = document.getElementById('soundVisualizer');
        if (visualizer) visualizer.classList.add('active');

        const btnPlay = document.getElementById('btnPlayDemo');
        if (btnPlay) {
            btnPlay.classList.add('is-playing');
            const icon = document.getElementById('playIcon');
            const text = document.getElementById('playText');
            if (icon) icon.textContent = '⏹️';
            if (text) text.textContent = 'Stop Demo';
        }

        const statusLabel = document.getElementById('soundStatusMsg');
        if (statusLabel) {
            statusLabel.innerHTML = `🎵 Playing: <strong>${trackName}</strong> <span style="opacity:0.85">(${instrumentName || category})</span>`;
            statusLabel.style.color = '#16a34a';
        }

        const audio = new Audio(audioUrl);
        currentAudio = audio;

        audio.play().then(() => {
            // Audio playing successfully
        }).catch(err => {
            // If browser blocks audio tag or file loading, fall back to synthesizer
            playSynthMelodyFallback(category, instrumentName);
        });

        audio.onended = function () {
            stopDemo();
        };

        audio.onerror = function () {
            playSynthMelodyFallback(category, instrumentName);
        };
    }

    /**
     * Synthesizer fallback if HTML5 Audio is blocked
     */
    function playSynthMelodyFallback(category, instrumentName) {
        const type = getInstrumentType(category, instrumentName);
        const notes = [
            { note: 'C4', dur: 0.35, delay: 0 },
            { note: 'E4', dur: 0.35, delay: 300 },
            { note: 'G4', dur: 0.40, delay: 600 },
            { note: 'C5', dur: 0.70, delay: 950 }
        ];

        let totalDuration = 0;
        notes.forEach(item => {
            const freq = NOTES[item.note] || 440.0;
            const t = setTimeout(() => {
                if (isPlayingDemo) {
                    playTone(freq, item.dur, category, instrumentName, 0.4);
                    highlightKey(item.note);
                }
            }, item.delay);
            activeTimeouts.push(t);
            totalDuration = Math.max(totalDuration, item.delay + item.dur * 1000);
        });

        const endTimeout = setTimeout(() => stopDemo(), totalDuration + 200);
        activeTimeouts.push(endTimeout);
    }

    /**
     * Plays a single interactive musical note from virtual keyboard
     */
    function playSingleNote(noteLabel, freq, category, instrumentName) {
        getAudioContext();
        playTone(freq, 0.75, category, instrumentName, 0.45);

        const statusLabel = document.getElementById('soundStatusMsg');
        if (statusLabel) {
            statusLabel.textContent = `🎶 Note: ${noteLabel} (${Math.round(freq)} Hz)`;
            statusLabel.style.color = '#2563eb';
        }

        const visualizer = document.getElementById('soundVisualizer');
        if (visualizer) {
            visualizer.classList.add('active');
            setTimeout(() => {
                if (!isPlayingDemo) visualizer.classList.remove('active');
            }, 750);
        }
    }

    /**
     * Briefly highlights the corresponding virtual note button
     */
    function highlightKey(noteCode) {
        const btn = document.querySelector(`[data-note="${noteCode}"]`);
        if (btn) {
            btn.classList.add('active-key');
            setTimeout(() => btn.classList.remove('active-key'), 250);
        }
    }

    /**
     * Quick signature audio preview for storefront catalog cards
     * Plays the authentic studio recording uniquely crafted for that instrument!
     */
    function previewCardSound(category, instrumentName, buttonEl, instrumentId) {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }

        const key = getAudioFileKey(category, instrumentName, instrumentId);
        const trackName = getTrackName(category, instrumentName, instrumentId);
        const audioUrl = `/static/audio/${key}_preview.wav?v=20261125_iconic_v4`;

        if (buttonEl) {
            buttonEl.classList.add('playing-preview');
            const shortName = trackName.length > 13 ? trackName.slice(0, 13) + '..' : trackName;
            buttonEl.innerHTML = `<span>🔊 ${shortName}</span>`;
        }

        const audio = new Audio(audioUrl);
        currentAudio = audio;

        audio.play().then(() => {
            // Audio successfully playing
        }).catch(err => {
            // Fallback to synthesizer
            getAudioContext();
            playTone(320.0, 0.5, category, instrumentName, 0.4);
        });

        audio.onended = function () {
            if (buttonEl) {
                buttonEl.classList.remove('playing-preview');
                buttonEl.innerHTML = '<span>🔊 Preview</span>';
            }
        };

        audio.onerror = function () {
            if (buttonEl) {
                buttonEl.classList.remove('playing-preview');
                buttonEl.innerHTML = '<span>🔊 Preview</span>';
            }
        };

        // Safety timeout
        setTimeout(() => {
            if (buttonEl && buttonEl.classList.contains('playing-preview')) {
                buttonEl.classList.remove('playing-preview');
                buttonEl.innerHTML = '<span>🔊 Preview</span>';
            }
        }, 2800);
    }

    return {
        playTone: playTone,
        playDemo: playDemo,
        stopDemo: stopDemo,
        playSingleNote: playSingleNote,
        previewCardSound: previewCardSound,
        getTrackName: getTrackName,
        TRACK_INFO_MAP: TRACK_INFO_MAP,
        NOTES: NOTES
    };
})();
