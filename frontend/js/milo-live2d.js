/**
 * MILO Live2D Companion Controller
 * Multimodal Interactive Learning Companion
 * 
 * Handles:
 * - Live2D Cubism 4 initialization via PixiJS & pixi-live2d-display
 * - Half-body (bust/chest-up) viewport framing and responsive resizing
 * - Natural micro-animations (breathing, eye blinking, hair physics, cursor gaze tracking)
 * - Syllable-Vowel Lip-Sync (A, I, U, E, O + Bilabial M, B, P) paced naturally to human speech
 * - LLM Feedback-driven emotional expressions ('happy', 'supportive', 'curious', 'friendly')
 * - Persistent emotional posture across speaking & idle states
 * - Graceful fallback to static image on unsupported environments
 */

(function () {
    'use strict';

    // Live2D Cubism Vowel Form & Open Targets
    // ParamMouthOpenY: 0.0 (closed) to 1.0 (wide open)
    // ParamMouthForm: -1.0 (puckered/rounded) to +1.0 (wide smiling/stretched)
    const VOWEL_SHAPES = {
        'A': { open: 0.88, form: 0.15, label: 'A (open)' },
        'I': { open: 0.35, form: 0.88, label: 'I (wide smile)' },
        'U': { open: 0.30, form: -0.88, label: 'U (puckered round)' },
        'E': { open: 0.58, form: 0.68, label: 'E (mid smile)' },
        'O': { open: 0.82, form: -0.65, label: 'O (tall round)' },
        'M': { open: 0.02, form: 0.00, label: 'M/B/P (closed lips)' },
        'pause': { open: 0.04, form: 0.35, label: 'Pause (resting)' }
    };

    class MiloLive2DCompanion {
        constructor(options = {}) {
            this.canvasId = options.canvasId || 'miloLive2DCanvas';
            this.fallbackImgId = options.fallbackImgId || 'miloCharacterImg';
            this.stageId = options.stageId || 'miloCompanionStage';
            this.modelPath = options.modelPath || 'assets/live2d/MILO Model.model3.json?v=20261124g';

            // Half-body framing configuration:
            // Hair top is at Y ~ 16, skirt waistband/belt is at Y ~ 1420 out of 3224 model height
            this.config = Object.assign({
                targetVisibleHeight: 1420, // Height in model coordinates from top of hair to waistband
                targetVisibleWidth: 1050,  // Width in model coordinates (includes shoulders, braids, wrists)
                headroomRatio: 0.035,      // Headroom above hair (~3.5% of canvas height)
                minHeadroom: 14,           // Minimum pixel headroom so hair is never cut off
                blinkIntervalMin: 3.0,     // Seconds between blinks
                blinkIntervalMax: 5.5
            }, options.config || {});

            this.canvas = null;
            this.fallbackImg = null;
            this.app = null;
            this.model = null;
            this.isReady = false;
            this.currentState = 'idle';

            // Emotional feedback states from LLM
            this.currentEmotion = 'friendly';
            this.currentFeedback = null;

            // Smoothed emotional facial parameters (interpolated smoothly to prevent snapping)
            this.currentEyeSmile = 0.25;
            this.currentCheek = 0.20;
            this.currentBrowLY = 0.10;
            this.currentBrowRY = 0.10;
            this.currentBrowLAngle = 0.0;
            this.currentBrowRAngle = 0.0;
            this.currentBodyAngleY = 0.0;
            this.currentBodyAngleZ = 0.0;

            // Audio & Web Audio API lip-sync variables
            this.audioContext = null;
            this.analyser = null;
            this.audioDataArray = null;
            this.boundAudioElement = null;
            this.pendingAudio = null;
            this.manualSpeakingPulse = 0;

            // Syllable-vowel timeline & spoken text
            this.syllableTimeline = [];
            this.spokenText = '';
            this.speechStartTime = 0;
            this.speechDuration = 0;

            // Animation state variables
            this.time = 0;
            this.lastFrameTime = performance.now();
            this.blinkTimer = 0;
            this.nextBlinkTime = this._randomBlinkInterval();
            this.isBlinking = false;
            this.blinkProgress = 0;

            // Natural eye gaze & head targets (expression & question driven, NOT mouse following)
            this.targetAngleX = 0;
            this.targetAngleY = 0;
            this.targetEyeX = 0;
            this.targetEyeY = 0;
            this.currentAngleX = 0;
            this.currentAngleY = 0;
            this.currentEyeX = 0;
            this.currentEyeY = 0;

            // Subtle lifelike gaze micro-saccades (natural subconscious eye focus adjustments)
            this.saccadeTimer = 0;
            this.saccadeInterval = 2.8;
            this.saccadeOffsetX = 0;
            this.saccadeOffsetY = 0;

            // Lip-sync state: dynamic mouth opening (ParamMouthOpenY) & alphabet vowel shape (ParamMouthForm)
            this.mouthOpenValue = 0;
            this.targetMouthOpen = 0;
            this.mouthFormValue = 0.35;
            this.targetMouthForm = 0.35;

            // Bind methods
            this._onResize = this._onResize.bind(this);
            this._animate = this._animate.bind(this);

            this._init();
        }

        async _init() {
            this.canvas = document.getElementById(this.canvasId);
            this.fallbackImg = document.getElementById(this.fallbackImgId);

            if (!this.canvas) {
                console.warn(`[MiloLive2D] Canvas with ID "${this.canvasId}" not found. Keeping static fallback.`);
                return;
            }

            // Check if PixiJS and Live2D libraries are available
            if (typeof PIXI === 'undefined' || !PIXI.live2d || !PIXI.live2d.Live2DModel) {
                console.warn('[MiloLive2D] PixiJS or pixi-live2d-display library not loaded. Keeping static fallback.');
                return;
            }

            try {
                // Resolution: natural DPR between 1 and 2 for crisp yet smooth rendering
                const dpr = Math.min(Math.max(window.devicePixelRatio || 1, 1), 2);

                if (PIXI.settings) {
                    PIXI.settings.RESOLUTION = dpr;
                    PIXI.settings.ROUND_PIXELS = false; // Smooth sub-pixel mesh deformation
                }

                const parent = this.canvas.parentElement || this.canvas;
                const containerH = Math.max(parent.clientHeight || 500, 300);
                const containerW = Math.max(parent.clientWidth || 400, 200);
                const targetAspect = 803 / 1024; // ~0.7842 from Image 2 reference

                let ch = containerH;
                let cw = Math.round(ch * targetAspect);
                if (cw > containerW) {
                    cw = containerW;
                    ch = Math.round(cw / targetAspect);
                }

                this._currentWidth = cw;
                this._currentHeight = ch;

                // Create PixiJS Application with transparent background and antialiasing
                this.app = new PIXI.Application({
                    view: this.canvas,
                    autoStart: false,
                    backgroundAlpha: 0,
                    width: cw,
                    height: ch,
                    resolution: dpr,
                    autoDensity: true,
                    antialias: true,
                    powerPreference: 'high-performance'
                });

                // Load Live2D Cubism 4 model
                console.log(`[MiloLive2D] Loading model from: ${this.modelPath}`);
                this.model = await PIXI.live2d.Live2DModel.from(this.modelPath, {
                    autoInteract: false // We handle custom half-body interactivity and state expressions
                });

                // Add model to Pixi stage
                this.app.stage.addChild(this.model);

                // Set up half-body viewport framing
                this._applyHalfBodyFraming(cw, ch);

                // Ensure textures are rendered cleanly with standard linear filtering and mipmaps
                this._ensureNaturalTextures();

                // Setup event listeners
                window.addEventListener('resize', this._onResize, { passive: true });
                this._initResizeObserver();

                // Hide static fallback image and show canvas cleanly
                if (this.fallbackImg) {
                    this.fallbackImg.style.display = 'none';
                }
                this.canvas.style.display = 'block';
                this.canvas.style.opacity = '1';
                this.canvas.classList.add('live2d-loaded');

                this.isReady = true;

                // Handle any pending audio binding that occurred during model load
                if (this.pendingAudio) {
                    const { audio, emotion, feedback, text } = this.pendingAudio;
                    this.pendingAudio = null;
                    this.bindAudio(audio, emotion, feedback, text);
                }

                // Start Pixi render ticker
                this.app.ticker.add(this._animate);
                this.app.start();

                console.log('[MiloLive2D] Half-body Live2D companion initialized successfully.');
            } catch (err) {
                console.error('[MiloLive2D] Initialization failed:', err);
                if (this.fallbackImg) {
                    this.fallbackImg.style.display = 'block';
                }
                if (this.canvas) {
                    this.canvas.style.display = 'none';
                }
            }
        }

        _initResizeObserver() {
            if (typeof ResizeObserver === 'undefined') return;

            const parent = this.canvas.parentElement;
            if (!parent) return;

            let resizeTimeout = null;
            this.resizeObserver = new ResizeObserver(entries => {
                for (const entry of entries) {
                    const rect = entry.contentRect;
                    if (rect.width > 50 && rect.height > 50) {
                        clearTimeout(resizeTimeout);
                        resizeTimeout = setTimeout(() => {
                            this._onResize();
                        }, 60);
                    }
                }
            });

            this.resizeObserver.observe(parent);
        }

        /**
         * Sets up natural texture filtering:
         * Uses linear interpolation and standard mipmapping to avoid both blurriness
         * and harsh artificial over-sharpening.
         */
        _ensureNaturalTextures() {
            if (!this.model) return;
            try {
                const meshes = this.model.internalModel ? this.model.internalModel.drawables : null;
                if (meshes && meshes.length > 0) {
                    meshes.forEach(m => {
                        if (m.texture && m.texture.baseTexture) {
                            m.texture.baseTexture.scaleMode = PIXI.SCALE_MODES.LINEAR;
                        }
                    });
                }
            } catch (e) {
                console.warn('[MiloLive2D] Texture filtering notice:', e);
            }
        }

        /**
         * Calculates half-body scaling and positioning:
         * Pins top of hair to headroom so it is NEVER cut off,
         * scales to fit head down to waistband/belt at the bottom of canvas,
         * and cleanly hides the long skirt and legs below the canvas.
         */
        _applyHalfBodyFraming(cw, ch) {
            if (!this.model || !this.app) return;

            if (!cw || !ch) {
                cw = this.app.renderer.width / (this.app.renderer.resolution || 1);
                ch = this.app.renderer.height / (this.app.renderer.resolution || 1);
            }

            // Headroom from top so hair is NEVER cut off (~3.5% of height)
            const headroom = Math.max(this.config.minHeadroom, ch * this.config.headroomRatio);

            // Target vertical height in model coordinates (hair top Y=16 to belt Y=1420)
            const targetH = this.config.targetVisibleHeight; // 1420

            // Scale to fit exactly from headroom to canvas bottom
            const scale = (ch - headroom) / targetH;

            // Uniform scale - NEVER different between X and Y to prevent distortion
            this.model.scale.set(scale, scale);

            // Anchor at TOP CENTER (0.5, 0.0) of model
            this.model.anchor.set(0.5, 0.0);

            // Center horizontally, position at top headroom
            this.model.x = cw / 2;
            this.model.y = headroom;
        }

        _onResize() {
            if (!this.app || !this.canvas) return;

            const parent = this.canvas.parentElement;
            if (!parent) return;

            const containerH = Math.max(parent.clientHeight || 500, 100);
            const containerW = Math.max(parent.clientWidth || 400, 100);

            // Target aspect ratio matching the reference crop (Image 2: 803 / 1024)
            const targetAspect = 803 / 1024; // ~0.7842

            // Fit inside container while strictly locking aspect ratio
            let ch = containerH;
            let cw = ch * targetAspect;

            if (cw > containerW) {
                cw = containerW;
                ch = cw / targetAspect;
            }

            cw = Math.round(cw);
            ch = Math.round(ch);

            // Avoid redundant resize if dimensions haven't changed
            if (this._currentWidth === cw && this._currentHeight === ch) {
                return;
            }

            this._currentWidth = cw;
            this._currentHeight = ch;

            const dpr = Math.min(Math.max(window.devicePixelRatio || 1, 1), 2);
            if (this.app.renderer.resolution !== dpr) {
                this.app.renderer.resolution = dpr;
            }

            this.app.renderer.resize(cw, ch);
            this._applyHalfBodyFraming(cw, ch);
            this._ensureNaturalTextures();
        }

        _randomBlinkInterval() {
            const min = this.config.blinkIntervalMin;
            const max = this.config.blinkIntervalMax;
            return min + Math.random() * (max - min);
        }

        /**
         * State management: sets companion state ('idle', 'listening', 'thinking', 'speaking')
         * @param {'idle'|'listening'|'thinking'|'speaking'} state 
         */
        setState(state) {
            this.currentState = state || 'idle';
            if (state !== 'speaking' && !this.boundAudioElement) {
                this.targetMouthOpen = 0;
            }
        }

        /**
         * Sets emotion and feedback data from LLM
         * @param {'happy'|'supportive'|'curious'|'friendly'|string} emotion 
         * @param {Object} feedback 
         */
        setEmotion(emotion, feedback) {
            if (emotion) {
                this.currentEmotion = emotion;
            }
            if (feedback !== undefined && feedback !== null) {
                this.currentFeedback = feedback;
            }
        }

        /**
         * Pulse lip opening for Web Speech API synthesis or syllable triggers
         * @param {number} intensity (0.0 to 1.0)
         * @param {number} form (-1.0 to 1.0)
         */
        setSpeakingPulse(intensity = 0.75, form = 0.5) {
            this.manualSpeakingPulse = Math.max(0, Math.min(1.0, intensity));
            this.targetMouthOpen = this.manualSpeakingPulse;
            this.targetMouthForm = Math.max(-1.0, Math.min(1.0, form));
        }

        /**
         * Sets spoken text for phonetic syllable timeline synchronization
         * Used for Web Speech API synthesis or when audio is not provided
         * @param {string} text 
         * @param {number} duration Estimated speech duration in seconds
         */
        setSpeakingText(text, duration = 0) {
            if (text && typeof text === 'string') {
                this.spokenText = text;
                const words = text.trim().split(/\s+/).length;
                this.speechDuration = duration > 0 ? duration : Math.max(2.5, words / 2.6);
                this.speechStartTime = performance.now();
                this.syllableTimeline = this._buildSyllableTimeline(text, this.speechDuration);
                this.currentState = 'speaking';
            }
        }

        /**
         * Robust English vowel & syllable extractor:
         * Maps a word to its dominant vowel nuclei sequence (A, I, U, E, O)
         * and detects bilabial consonant closures (M, B, P).
         */
        _extractSyllableVowels(word) {
            const clean = word.toLowerCase().replace(/[^a-z]/g, '');
            if (!clean) return [];

            // High frequency conversational word mappings for exact phonetic naturalness
            const commonMap = {
                'the': ['E'],
                'to': ['U'],
                'do': ['U'],
                'you': ['U'],
                'your': ['O'],
                'we': ['I'],
                'be': ['I'],
                'me': ['I'],
                'my': ['I'],
                'i': ['I'],
                'a': ['A'],
                'and': ['A'],
                'in': ['I'],
                'on': ['O'],
                'it': ['I'],
                'is': ['I'],
                'at': ['A'],
                'of': ['O'],
                'for': ['O'],
                'are': ['A'],
                'hello': ['E', 'O'],
                'welcome': ['E', 'U'],
                'practice': ['A', 'I'],
                'interview': ['I', 'E', 'U'],
                'today': ['U', 'E'],
                'focus': ['O', 'U'],
                'background': ['A', 'A', 'U'],
                'people': ['I', 'U'],
                'learn': ['E'],
                'point': ['O', 'I'],
                'things': ['I'],
                'new': ['U'],
                'english': ['I', 'I'],
                'grammar': ['A', 'A'],
                'good': ['U'],
                'great': ['E'],
                'job': ['O'],
                'help': ['E'],
                'could': ['U'],
                'would': ['U'],
                'about': ['A', 'U'],
                'little': ['I', 'U']
            };

            if (commonMap[clean]) {
                return commonMap[clean];
            }

            let working = clean;
            // Silent 'e' at end of multi-letter words (e.g., 'make', 'like', 'take')
            if (working.length > 3 && working.endsWith('e') && !working.endsWith('ee')) {
                working = working.slice(0, -1);
            }

            const matches = working.match(/[aeiouy]+/g);
            if (!matches) {
                return ['A'];
            }

            const vowels = [];
            for (const group of matches) {
                if (group === 'ee' || group === 'ea' || group === 'ie') {
                    vowels.push('I');
                } else if (group === 'oo') {
                    vowels.push('U');
                } else if (group === 'ou' || group === 'ow') {
                    vowels.push('O');
                } else if (group === 'ai' || group === 'ay' || group === 'ey') {
                    vowels.push('E');
                } else if (group === 'oa' || group === 'aw' || group === 'au' || group === 'oi' || group === 'oy') {
                    vowels.push('O');
                } else {
                    const char = group[0];
                    if (char === 'a') vowels.push('A');
                    else if (char === 'i' || char === 'y') vowels.push('I');
                    else if (char === 'u') vowels.push('U');
                    else if (char === 'e') vowels.push('E');
                    else if (char === 'o') vowels.push('O');
                    else vowels.push('A');
                }
            }

            return vowels.length > 0 ? vowels : ['A'];
        }

        /**
         * Builds a realistic human-paced syllable-vowel timeline (~3.5-4.5 syllables/sec).
         * Each vowel is held for ~180-280 ms so the mouth shape is clearly visible,
         * with brief lip closures for bilabials (M, B, P) and punctuation pauses.
         */
        _buildSyllableTimeline(text, totalDurationSec = 4.5) {
            if (!text || typeof text !== 'string') return [];

            const rawTokens = text.split(/(\s+|[.,!?;:]+)/).filter(t => t.trim().length > 0);
            const units = [];

            for (const token of rawTokens) {
                if (/^[.,!?;:]+$/.test(token)) {
                    // Punctuation clause pause (150 - 300 ms)
                    units.push({
                        type: 'pause',
                        durationWeight: 1.4,
                        ...VOWEL_SHAPES['pause']
                    });
                    continue;
                }

                const vowels = this._extractSyllableVowels(token);
                const lower = token.toLowerCase();
                const hasBilabial = /[mbp]/.test(lower);

                vowels.forEach((v, idx) => {
                    const shape = VOWEL_SHAPES[v] || VOWEL_SHAPES['A'];
                    units.push({
                        type: v,
                        durationWeight: 1.0,
                        open: shape.open,
                        form: shape.form
                    });

                    // If word ends with bilabial consonant (M, B, P), insert brief lip contact
                    if (hasBilabial && idx === vowels.length - 1 && /[mbp]$/.test(lower)) {
                        units.push({
                            type: 'M',
                            durationWeight: 0.35,
                            ...VOWEL_SHAPES['M']
                        });
                    }
                });

                // Small conversational inter-word micro gap
                units.push({
                    type: 'pause',
                    durationWeight: 0.22,
                    ...VOWEL_SHAPES['pause']
                });
            }

            if (units.length === 0) return [];

            // Normalize weights to the exact total audio duration
            const totalWeight = units.reduce((acc, u) => acc + u.durationWeight, 0);
            const secPerWeight = Math.max(0.05, totalDurationSec / totalWeight);

            let curTime = 0;
            return units.map(u => {
                const dur = u.durationWeight * secPerWeight;
                const start = curTime;
                const end = curTime + dur;
                curTime = end;
                return {
                    type: u.type,
                    start,
                    end,
                    dur,
                    open: u.open,
                    form: u.form
                };
            });
        }

        /**
         * Binds an HTMLAudioElement to the Live2D model for real-time lip-sync
         * @param {HTMLAudioElement} audioElement 
         * @param {string} emotion 
         * @param {Object} feedback 
         * @param {string} text Spoken response text for syllable-vowel timeline alignment
         */
        bindAudio(audioElement, emotion, feedback, text = '') {
            if (!audioElement) return;

            if (text && typeof text === 'string') {
                this.spokenText = text;
            }

            if (!this.isReady) {
                this.pendingAudio = { audio: audioElement, emotion, feedback, text };
                return;
            }

            this.boundAudioElement = audioElement;
            this.currentState = 'speaking';
            if (emotion) this.setEmotion(emotion, feedback);

            // Compute syllable timeline when audio duration is resolved
            const initTimeline = () => {
                const dur = (audioElement.duration && !isNaN(audioElement.duration) && audioElement.duration > 0)
                    ? audioElement.duration
                    : (this.spokenText ? (this.spokenText.split(/\s+/).length / 2.6) : 4.5);
                this.syllableTimeline = this._buildSyllableTimeline(this.spokenText, dur);
            };

            initTimeline();
            if (isNaN(audioElement.duration) || audioElement.duration === 0) {
                audioElement.addEventListener('loadedmetadata', initTimeline, { once: true });
            }

            // Set up Web Audio API AnalyserNode if supported
            try {
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (AudioCtx) {
                    if (!this.audioContext) {
                        this.audioContext = new AudioCtx();
                    }
                    if (this.audioContext.state === 'suspended') {
                        this.audioContext.resume().catch(() => {});
                    }

                    if (!audioElement._hasLive2DSource) {
                        const source = this.audioContext.createMediaElementSource(audioElement);
                        const analyser = this.audioContext.createAnalyser();
                        analyser.fftSize = 256;
                        analyser.smoothingTimeConstant = 0.35;
                        source.connect(analyser);
                        analyser.connect(this.audioContext.destination);

                        audioElement._hasLive2DSource = true;
                        audioElement._live2dAnalyser = analyser;
                    }

                    this.analyser = audioElement._live2dAnalyser;
                    this.audioDataArray = new Uint8Array(this.analyser.frequencyBinCount);
                }
            } catch (err) {
                // If browser restricts createMediaElementSource (e.g. CORS or audio routing),
                // fallback to audio-time based lip-sync smoothly.
                this.analyser = null;
            }

            // Cleanup handlers when audio ends or pauses
            // Note: Does NOT reset currentEmotion so feedback emotion remains active!
            const onEndOrPause = () => {
                if (this.boundAudioElement === audioElement) {
                    this.boundAudioElement = null;
                    this.targetMouthOpen = 0;
                    this.syllableTimeline = [];
                    this.setState('idle');
                }
            };

            audioElement.addEventListener('ended', onEndOrPause, { once: true });
            audioElement.addEventListener('pause', onEndOrPause, { once: true });
            audioElement.addEventListener('error', onEndOrPause, { once: true });
        }

        /**
         * Primary animation tick loop executed every frame
         */
        _animate(delta) {
            if (!this.model || !this.isReady) return;

            try {
                const now = performance.now();
                let dt = (now - this.lastFrameTime) / 1000;
                if (isNaN(dt) || dt <= 0.0005) {
                    dt = typeof delta === 'number' && delta > 0 ? (delta / 60.0) : (1 / 60.0);
                }
                dt = Math.min(0.1, Math.max(0.001, dt)); // Guard against delta spikes or negative time
                this.lastFrameTime = now;
                this.time += dt;

                const coreModel = this.model.internalModel ? this.model.internalModel.coreModel : null;
                if (!coreModel) return;

                // 1. Natural Breathing cycle (continuous sinusoidal wave)
                const breath = (Math.sin(this.time * 2.2) + 1) * 0.5;
                this._setParam(coreModel, 'ParamBreath', breath);

                // 2. Eye Blinking logic
                this.blinkTimer += dt;
                if (!this.isBlinking && this.blinkTimer >= this.nextBlinkTime) {
                    this.isBlinking = true;
                    this.blinkProgress = 0;
                }

                let eyeOpen = 1.0;
                if (this.isBlinking) {
                    this.blinkProgress += dt * 8.0; // Blink duration ~ 125ms
                    if (this.blinkProgress < 0.5) {
                        eyeOpen = 1.0 - (this.blinkProgress * 2.0);
                    } else if (this.blinkProgress < 1.0) {
                        eyeOpen = (this.blinkProgress - 0.5) * 2.0;
                    } else {
                        eyeOpen = 1.0;
                        this.isBlinking = false;
                        this.blinkTimer = 0;
                        this.nextBlinkTime = this._randomBlinkInterval();
                    }
                }

                // 3. Natural Lifelike Gaze Micro-Saccades (subconscious eye focus adjustments)
                this.saccadeTimer += dt;
                if (this.saccadeTimer >= this.saccadeInterval) {
                    this.saccadeTimer = 0;
                    this.saccadeInterval = 2.2 + Math.random() * 2.3; // Shifts micro-focus every 2-4.5s
                    this.saccadeOffsetX = (Math.random() - 0.5) * 0.08;
                    this.saccadeOffsetY = (Math.random() - 0.5) * 0.05;
                }

                // 4. LLM Feedback & Emotion Evaluation
                const emotion = this.currentEmotion || 'friendly';
                let overallScore = 0;
                let hasCorrections = false;

                if (this.currentFeedback) {
                    if (typeof this.currentFeedback.overall_score === 'number') {
                        overallScore = this.currentFeedback.overall_score;
                    }
                    if (Array.isArray(this.currentFeedback.corrections) && this.currentFeedback.corrections.length > 0) {
                        hasCorrections = true;
                    }
                }

                // Determine high-level emotion category (explicit emotion takes precedence)
                let isHappy = false;
                let isSupportive = false;
                let isCurious = false;

                if (emotion === 'happy') {
                    isHappy = true;
                } else if (emotion === 'supportive') {
                    isSupportive = true;
                } else if (emotion === 'curious') {
                    isCurious = true;
                } else if (overallScore >= 85 && !hasCorrections) {
                    isHappy = true;
                } else if (hasCorrections || (overallScore > 0 && overallScore < 80)) {
                    isSupportive = true;
                } else if (this.spokenText && this.spokenText.trim().endsWith('?')) {
                    isCurious = true;
                }

                // Natural expression & question driven gaze targets (no mouse tracking)
                let targetEyeX = 0.0 + this.saccadeOffsetX;
                let targetEyeY = 0.0 + this.saccadeOffsetY;
                let targetAngleX = 0.0;
                let targetAngleY = 0.0;
                let targetAngleZ = 0.0;

                // Target facial parameters for each emotion
                let targetEyeSmile = 0.35;
                let targetCheek = 0.22;
                let targetBrowLY = 0.12;
                let targetBrowRY = 0.12;
                let targetBrowLAngle = 0.0;
                let targetBrowRAngle = 0.0;
                let targetBodyAngleY = 0.0;
                let targetBodyAngleZ = 0.0;
                let restingMouthForm = 0.35;
                let targetEyeOpen = eyeOpen;

                if (this.currentState === 'thinking') {
                    // Thinking state: thoughtful upward & sideways glance in contemplation
                    targetEyeX = -0.28 + this.saccadeOffsetX;
                    targetEyeY = 0.45 + this.saccadeOffsetY;
                    targetAngleX = -4.5;
                    targetAngleY = 6.0;
                    targetAngleZ = 3.0;
                    targetBrowLY = -0.10;
                    targetBrowRY = -0.10;
                    targetCheek = 0.20;
                    restingMouthForm = 0.30;
                } else if (this.currentState === 'listening') {
                    // Listening state: attentive direct eye contact, forward listening tilt
                    targetEyeX = 0.0 + this.saccadeOffsetX;
                    targetEyeY = 0.12 + this.saccadeOffsetY;
                    targetAngleX = 0.0;
                    targetAngleY = 3.5;
                    targetAngleZ = -2.0;
                    targetEyeOpen = Math.min(1.10, eyeOpen * 1.08);
                    targetCheek = 0.28;
                    restingMouthForm = 0.35;
                } else if (isHappy) {
                    // High praise / Excellent score:
                    // Radiantly smiling eyes, cute bright blush, raised cheerful brows, playful head tilt
                    targetEyeX = 0.0 + this.saccadeOffsetX;
                    targetEyeY = 0.05 + this.saccadeOffsetY; // Joyful direct eye contact
                    targetEyeSmile = 0.92;
                    targetCheek = 0.70;
                    targetBrowLY = 0.38;
                    targetBrowRY = 0.38;
                    targetBrowLAngle = -0.15;
                    targetBrowRAngle = -0.15;
                    targetAngleZ = -3.8;
                    targetBodyAngleZ = -2.0;
                    restingMouthForm = 0.65;
                } else if (isSupportive) {
                    // Supportive / Corrections / Encouraging:
                    // Empathetic caring brow tilt (inner brow raised), warm comforting eyes, sweet blush, caring head tilt
                    targetEyeX = 0.0 + this.saccadeOffsetX;
                    targetEyeY = 0.08 + this.saccadeOffsetY; // Warm caring eye contact
                    targetAngleX = -1.0;
                    targetAngleY = 2.0;
                    targetBrowLAngle = 0.58;
                    targetBrowRAngle = 0.58;
                    targetBrowLY = 0.30;
                    targetBrowRY = 0.30;
                    targetEyeSmile = 0.48;
                    targetCheek = 0.40;
                    targetAngleZ = 3.6;
                    targetBodyAngleY = 3.0; // Leaned slightly forward towards student in active encouragement
                    restingMouthForm = 0.38;
                } else if (isCurious) {
                    // Inquisitive / Asking a Question:
                    // Inquisitive eye contact, quizzical head turn & tilt, asymmetric brows, wide alert eyes
                    targetEyeX = -0.06 + this.saccadeOffsetX;
                    targetEyeY = 0.10 + this.saccadeOffsetY; // Attentive focus on user
                    targetAngleX = 2.2;
                    targetAngleY = 1.0;
                    targetAngleZ = -4.8;
                    targetBrowLY = 0.52;
                    targetBrowRY = 0.20;
                    targetBrowLAngle = 0.25;
                    targetBrowRAngle = 0.0;
                    targetEyeOpen = eyeOpen * 1.15;
                    targetEyeSmile = 0.25;
                    targetCheek = 0.28;
                    restingMouthForm = 0.30;
                } else {
                    // Friendly conversational default
                    targetEyeX = 0.0 + this.saccadeOffsetX;
                    targetEyeY = 0.0 + this.saccadeOffsetY;
                    targetAngleX = 0.0;
                    targetAngleY = 0.0;
                    targetEyeSmile = 0.35;
                    targetCheek = 0.22;
                    targetBrowLY = 0.12;
                    targetBrowRY = 0.12;
                    targetAngleZ = 0.0;
                    restingMouthForm = 0.35;
                }

                // Smooth interpolation for gaze & facial expression (natural organic transitions)
                const lerpGaze = Math.min(1.0, dt * 5.5);
                this.currentEyeX += (targetEyeX - this.currentEyeX) * lerpGaze;
                this.currentEyeY += (targetEyeY - this.currentEyeY) * lerpGaze;
                this.currentAngleX += (targetAngleX - this.currentAngleX) * lerpGaze;
                this.currentAngleY += (targetAngleY - this.currentAngleY) * lerpGaze;

                const lerpFace = Math.min(1.0, dt * 6.0);
                this.currentEyeSmile += (targetEyeSmile - this.currentEyeSmile) * lerpFace;
                this.currentCheek += (targetCheek - this.currentCheek) * lerpFace;
                this.currentBrowLY += (targetBrowLY - this.currentBrowLY) * lerpFace;
                this.currentBrowRY += (targetBrowRY - this.currentBrowRY) * lerpFace;
                this.currentBrowLAngle += (targetBrowLAngle - this.currentBrowLAngle) * lerpFace;
                this.currentBrowRAngle += (targetBrowRAngle - this.currentBrowRAngle) * lerpFace;
                this.currentBodyAngleY += (targetBodyAngleY - this.currentBodyAngleY) * lerpFace;
                this.currentBodyAngleZ += (targetBodyAngleZ - this.currentBodyAngleZ) * lerpFace;

                // 5. Natural Syllable-Vowel Lip-Sync Computation
                const isAudioActive = this.boundAudioElement && 
                                     !this.boundAudioElement.paused && 
                                     !this.boundAudioElement.ended;

                let targetMouthOpen = 0;
                let targetMouthForm = restingMouthForm;

                let currentPlaybackTime = 0;
                let isSpeakingActive = false;

                if (isAudioActive) {
                    currentPlaybackTime = this.boundAudioElement.currentTime;
                    isSpeakingActive = true;
                } else if (this.currentState === 'speaking' && this.speechStartTime > 0) {
                    // Fallback to elapsed time for Web Speech API synthesis
                    currentPlaybackTime = (now - this.speechStartTime) / 1000;
                    if (currentPlaybackTime <= this.speechDuration) {
                        isSpeakingActive = true;
                    }
                }

                if (isSpeakingActive) {
                    // A. Locate active syllable from the generated timeline
                    let activeUnit = null;
                    if (this.syllableTimeline && this.syllableTimeline.length > 0) {
                        for (let i = 0; i < this.syllableTimeline.length; i++) {
                            const u = this.syllableTimeline[i];
                            if (currentPlaybackTime >= u.start && currentPlaybackTime <= u.end) {
                                activeUnit = u;
                                break;
                            }
                        }
                        if (!activeUnit && currentPlaybackTime > 0) {
                            activeUnit = this.syllableTimeline[this.syllableTimeline.length - 1];
                        }
                    }

                    // B. Compute audio volume scaling
                    let audioVol = 0;
                    if (this.analyser && this.audioDataArray) {
                        this.analyser.getByteFrequencyData(this.audioDataArray);
                        let sum = 0;
                        const bins = Math.min(16, this.audioDataArray.length);
                        for (let i = 1; i <= bins; i++) sum += this.audioDataArray[i];
                        const avg = sum / bins;
                        if (avg > 12) {
                            audioVol = Math.min(1.2, (avg - 12) / 60.0);
                        } else {
                            audioVol = 0.05;
                        }
                    } else if (activeUnit && activeUnit.type !== 'pause' && activeUnit.type !== 'M') {
                        // Smooth syllable acoustic bell curve envelope
                        const span = activeUnit.end - activeUnit.start;
                        const progress = span > 0 ? (currentPlaybackTime - activeUnit.start) / span : 0.5;
                        const bell = Math.pow(Math.sin(Math.PI * Math.max(0, Math.min(1, progress))), 0.6);
                        audioVol = 0.35 + bell * 0.65;
                    } else {
                        audioVol = 0.05;
                    }

                    // C. Apply vowel shape & mouth opening
                    if (activeUnit) {
                        if (activeUnit.type === 'M') {
                            // Bilabial consonant (M, B, P): lips closed firmly
                            targetMouthOpen = 0.02;
                            targetMouthForm = 0.0;
                        } else if (activeUnit.type === 'pause') {
                            // Sentence or clause pause: resting mouth
                            targetMouthOpen = 0.04;
                            targetMouthForm = restingMouthForm;
                        } else {
                            // Vowel nucleus (A, I, U, E, O): open jaw modulated by volume
                            const volScale = Math.max(0.25, Math.min(1.25, audioVol * 1.25));
                            targetMouthOpen = Math.min(1.0, activeUnit.open * volScale);
                            // Hold the vowel form stably for the syllable duration (~180-250ms)
                            targetMouthForm = activeUnit.form;
                        }
                    } else {
                        targetMouthOpen = Math.min(0.85, audioVol * 0.9);
                        targetMouthForm = restingMouthForm;
                    }
                } else if (this.currentState === 'speaking') {
                    if (this.manualSpeakingPulse > 0.05) {
                        this.manualSpeakingPulse -= dt * 3.5;
                        targetMouthOpen = this.manualSpeakingPulse;
                        targetMouthForm = this.targetMouthForm || 0.5;
                    } else {
                        targetMouthOpen = 0;
                        targetMouthForm = restingMouthForm;
                    }
                } else {
                    targetMouthOpen = 0;
                    targetMouthForm = restingMouthForm;
                }

                // D. Smooth interpolation for jaw opening and vowel form
                // Frame-rate independent lerp: jaw opens/closes cleanly, lips hold distinct vowel shape
                const lerpOpen = Math.min(1.0, dt * 16.0);
                const lerpForm = Math.min(1.0, dt * 12.0);
                this.mouthOpenValue += (targetMouthOpen - this.mouthOpenValue) * lerpOpen;
                this.mouthFormValue += (targetMouthForm - this.mouthFormValue) * lerpForm;

                // 6. Pose & Posture Modulations based on State
                let finalAngleX = this.currentAngleX;
                let finalAngleY = this.currentAngleY;
                let finalAngleZ = targetAngleZ;
                let finalEyeX = this.currentEyeX;
                let finalEyeY = this.currentEyeY;

                if (this.currentState === 'speaking') {
                    // Rhythmic conversational head nod
                    if (isHappy) {
                        finalAngleY += Math.sin(this.time * 4.8) * 1.8;
                    } else if (isSupportive) {
                        finalAngleY += Math.sin(this.time * 3.6) * 1.4;
                    } else {
                        finalAngleY += Math.sin(this.time * 4.0) * 1.5;
                    }
                } else if (this.currentState === 'listening') {
                    finalAngleZ += (targetAngleZ < 0 ? -1.0 : 1.0) * 1.2;
                } else if (this.currentState === 'thinking') {
                    finalAngleZ = 3.0;
                } else {
                    // Idle state: subtle idle head float, retaining emotional posture & warmth
                    finalAngleY += Math.sin(this.time * 1.2) * 0.8;
                    finalAngleZ += Math.sin(this.time * 0.9) * 0.6;
                }

                // 7. Apply Values to Live2D Parameters
                this._setParam(coreModel, 'ParamAngleX', finalAngleX);
                this._setParam(coreModel, 'ParamAngleY', finalAngleY);
                this._setParam(coreModel, 'ParamAngleZ', finalAngleZ);

                this._setParam(coreModel, 'ParamBodyAngleX', (finalAngleX / 20.0) * 3.0);
                this._setParam(coreModel, 'ParamBodyAngleY', this.currentBodyAngleY);
                this._setParam(coreModel, 'ParamBodyAngleZ', this.currentBodyAngleZ);

                this._setParam(coreModel, 'ParamEyeBallX', finalEyeX);
                this._setParam(coreModel, 'ParamEyeBallY', finalEyeY);

                this._setParam(coreModel, 'ParamEyeLOpen', targetEyeOpen);
                this._setParam(coreModel, 'ParamEyeROpen', targetEyeOpen);
                this._setParam(coreModel, 'ParamEyeLSmile', this.currentEyeSmile);
                this._setParam(coreModel, 'ParamEyeRSmile', this.currentEyeSmile);

                this._setParam(coreModel, 'ParamBrowLY', this.currentBrowLY);
                this._setParam(coreModel, 'ParamBrowRY', this.currentBrowRY);
                this._setParam(coreModel, 'ParamBrowLAngle', this.currentBrowLAngle);
                this._setParam(coreModel, 'ParamBrowRAngle', this.currentBrowRAngle);

                this._setParam(coreModel, 'ParamMouthOpenY', this.mouthOpenValue);
                this._setParam(coreModel, 'ParamMouthForm', this.mouthFormValue);
                this._setParam(coreModel, 'ParamCheek', this.currentCheek);

                // Subtle natural hair sway
                const hairSway = Math.sin(this.time * 2.0) * 0.15 + (finalAngleX / 20.0) * 0.2;
                this._setParam(coreModel, 'ParamHairFront', hairSway);
                this._setParam(coreModel, 'ParamHairSide', hairSway);
                this._setParam(coreModel, 'ParamHairBack', hairSway * 0.6);

                // Render current frame
                if (this.app) {
                    this.app.render();
                }
            } catch (err) {
                console.warn('[MiloLive2D] Animation tick notice:', err);
            }
        }

        _setParam(coreModel, paramId, value) {
            try {
                if (typeof coreModel.setParameterValueById === 'function') {
                    coreModel.setParameterValueById(paramId, value);
                } else if (coreModel._parameterValues && coreModel._parameterIds) {
                    const idx = coreModel._parameterIds.indexOf(paramId);
                    if (idx !== -1) {
                        coreModel._parameterValues[idx] = value;
                    }
                }
            } catch (e) {
                // Ignore transient parameter update errors
            }
        }

        destroy() {
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
                this.resizeObserver = null;
            }
            window.removeEventListener('resize', this._onResize);

            if (this.app) {
                this.app.stop();
                this.app.destroy(true, { children: true, texture: true, baseTexture: true });
                this.app = null;
            }
            this.model = null;
            this.isReady = false;
        }
    }

    // Expose to global window
    window.MiloLive2DCompanion = MiloLive2DCompanion;

    // Automatic hook to window.setCompanionState
    const prevSetCompanionState = window.setCompanionState;
    window.setCompanionState = function (state, text, emotion, feedback) {
        if (typeof prevSetCompanionState === 'function') {
            prevSetCompanionState(state, text, emotion, feedback);
        }
        if (window.miloLive2D) {
            if (typeof window.miloLive2D.setState === 'function') {
                window.miloLive2D.setState(state);
            }
            if ((emotion || feedback) && typeof window.miloLive2D.setEmotion === 'function') {
                window.miloLive2D.setEmotion(emotion, feedback);
            }
        }
    };

    // Auto-initialize when DOM is ready if canvas exists
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('miloLive2DCanvas');
        if (canvas && !window.miloLive2D) {
            window.miloLive2D = new MiloLive2DCompanion({
                canvasId: 'miloLive2DCanvas',
                fallbackImgId: 'miloCharacterImg',
                modelPath: 'assets/live2d/MILO Model.model3.json?v=20261124g'
            });
        }
    });

})();
