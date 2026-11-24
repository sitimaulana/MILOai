/**
 * MILO Live2D Companion Controller
 * Multimodal Interactive Learning Companion
 * 
 * Handles:
 * - Live2D Cubism 4 initialization via PixiJS & pixi-live2d-display
 * - Half-body (bust/chest-up) viewport framing and responsive resizing
 * - Natural micro-animations (breathing, eye blinking, hair physics, cursor gaze tracking)
 * - True Audio-driven Lip-Sync via Web Audio API AnalyserNode
 * - LLM Feedback-driven emotional expressions ('happy', 'supportive', 'curious', 'friendly')
 * - State management ('idle', 'listening', 'thinking', 'speaking')
 * - Graceful fallback to static image on unsupported environments
 */

(function () {
    'use strict';

    class MiloLive2DCompanion {
        constructor(options = {}) {
            this.canvasId = options.canvasId || 'miloLive2DCanvas';
            this.fallbackImgId = options.fallbackImgId || 'miloCharacterImg';
            this.stageId = options.stageId || 'miloCompanionStage';
            this.modelPath = options.modelPath || 'assets/live2d/MILO Model.model3.json?v=20261124a';

            // Half-body framing configuration:
            // Hair top is at Y ~ 16, skirt waistband/belt is at Y ~ 1420 out of 3224 model height
            this.config = Object.assign({
                targetVisibleHeight: 1420, // Height in model coordinates from top of hair to waistband
                targetVisibleWidth: 1050,  // Width in model coordinates (includes shoulders, braids, wrists)
                headroomRatio: 0.035,      // Headroom above hair (~3.5% of canvas height)
                minHeadroom: 14,           // Minimum pixel headroom so hair is never cut off
                blinkIntervalMin: 3.0,     // Seconds between blinks
                blinkIntervalMax: 5.5,
                mouseTrackEasing: 0.08,
                gazeMaxAngleX: 16,
                gazeMaxAngleY: 12,
                gazeMaxEye: 0.6
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

            // Audio & Web Audio API lip-sync variables
            this.audioContext = null;
            this.analyser = null;
            this.audioDataArray = null;
            this.boundAudioElement = null;
            this.pendingAudio = null;
            this.manualSpeakingPulse = 0;

            // Animation state variables
            this.time = 0;
            this.lastFrameTime = performance.now();
            this.blinkTimer = 0;
            this.nextBlinkTime = this._randomBlinkInterval();
            this.isBlinking = false;
            this.blinkProgress = 0;

            // Cursor tracking targets & currents
            this.targetAngleX = 0;
            this.targetAngleY = 0;
            this.targetEyeX = 0;
            this.targetEyeY = 0;
            this.currentAngleX = 0;
            this.currentAngleY = 0;
            this.currentEyeX = 0;
            this.currentEyeY = 0;

            // Lip-sync state
            this.mouthOpenValue = 0;
            this.targetMouthOpen = 0;

            // Bind methods
            this._onResize = this._onResize.bind(this);
            this._onMouseMove = this._onMouseMove.bind(this);
            this._onMouseLeave = this._onMouseLeave.bind(this);
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
                window.addEventListener('pointermove', this._onMouseMove, { passive: true });
                document.addEventListener('mouseleave', this._onMouseLeave, { passive: true });
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
                    const { audio, emotion, feedback } = this.pendingAudio;
                    this.pendingAudio = null;
                    this.bindAudio(audio, emotion, feedback);
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
         * and harsh artificial over-sharpening ("terlalu HD").
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

        _onMouseMove(e) {
            if (!this.canvas) return;
            const rect = this.canvas.getBoundingClientRect();

            // Calculate cursor offset relative to canvas center (-1.0 to 1.0)
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height * 0.45; // Focus on eye level

            const dx = (e.clientX - centerX) / (rect.width || 1);
            const dy = (e.clientY - centerY) / (rect.height || 1);

            // Clamp and scale
            const clampedX = Math.max(-1, Math.min(1, dx));
            const clampedY = Math.max(-1, Math.min(1, dy));

            this.targetAngleX = clampedX * this.config.gazeMaxAngleX;
            this.targetAngleY = -clampedY * this.config.gazeMaxAngleY;
            this.targetEyeX = clampedX * this.config.gazeMaxEye;
            this.targetEyeY = -clampedY * this.config.gazeMaxEye;
        }

        _onMouseLeave() {
            // When mouse exits viewport, return gaze smoothly to center
            this.targetAngleX = 0;
            this.targetAngleY = 0;
            this.targetEyeX = 0;
            this.targetEyeY = 0;
        }

        _randomBlinkInterval() {
            const min = this.config.blinkIntervalMin;
            const max = this.config.blinkIntervalMax;
            return min + Math.random() * (max - min);
        }

        /**
         * State management: sets companion emotional & active pose
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
            this.currentEmotion = emotion || 'friendly';
            if (feedback !== undefined) {
                this.currentFeedback = feedback;
            }
        }

        /**
         * Pulse lip opening for Web Speech API synthesis or syllable triggers
         * @param {number} intensity (0.0 to 1.0)
         */
        setSpeakingPulse(intensity = 0.75) {
            this.manualSpeakingPulse = Math.max(0, Math.min(1.0, intensity));
            this.targetMouthOpen = this.manualSpeakingPulse;
        }

        /**
         * Binds an HTMLAudioElement to the Live2D model for real-time lip-sync
         * @param {HTMLAudioElement} audioElement 
         * @param {string} emotion 
         * @param {Object} feedback 
         */
        bindAudio(audioElement, emotion, feedback) {
            if (!audioElement) return;

            if (!this.isReady) {
                this.pendingAudio = { audio: audioElement, emotion, feedback };
                return;
            }

            this.boundAudioElement = audioElement;
            this.currentState = 'speaking';
            if (emotion) this.setEmotion(emotion, feedback);

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
                        analyser.smoothingTimeConstant = 0.45;
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
                // fallback to audio-time based lip-sync seamlessly.
                this.analyser = null;
            }

            // Cleanup handlers when audio ends or pauses
            const onEndOrPause = () => {
                if (this.boundAudioElement === audioElement) {
                    this.boundAudioElement = null;
                    this.targetMouthOpen = 0;
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

            const now = performance.now();
            const dt = (now - this.lastFrameTime) / 1000;
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

            // 3. Smooth Damping (Lerp) for Gaze & Head Angles
            const easing = this.config.mouseTrackEasing;
            this.currentAngleX += (this.targetAngleX - this.currentAngleX) * easing;
            this.currentAngleY += (this.targetAngleY - this.currentAngleY) * easing;
            this.currentEyeX += (this.targetEyeX - this.currentEyeX) * easing;
            this.currentEyeY += (this.targetEyeY - this.currentEyeY) * easing;

            // 4. Lip-Sync Computation based on real audio feedback
            const isAudioActive = this.boundAudioElement && 
                                 !this.boundAudioElement.paused && 
                                 !this.boundAudioElement.ended;

            if (isAudioActive) {
                if (this.analyser && this.audioDataArray) {
                    // Extract frequency energy in speech range (~150Hz to ~3200Hz)
                    this.analyser.getByteFrequencyData(this.audioDataArray);
                    let energy = 0;
                    let count = 0;
                    for (let i = 2; i < 28; i++) {
                        energy += this.audioDataArray[i];
                        count++;
                    }
                    const avg = energy / (count || 1); // 0 to 255

                    if (avg > 14) {
                        // Dynamic speech volume mapping to mouth opening (range 0.1 to 0.85)
                        const norm = Math.min(1.0, (avg - 14) / 100);
                        let openVal = Math.pow(norm, 0.8) * 0.85;

                        // Add gentle phoneme modulation
                        const phonemeMod = 0.85 + 0.15 * Math.sin(this.time * 16.0);
                        this.targetMouthOpen = openVal * phonemeMod;
                    } else {
                        this.targetMouthOpen = 0.05; // Resting small opening during micro-pauses
                    }
                } else {
                    // Fallback when Web Audio Analyser is unavailable:
                    // Rhythmic natural phoneme wave strictly bounded to active audio playback
                    const syll = Math.abs(Math.sin(this.time * 14.0)) * 0.55 
                               + Math.abs(Math.sin(this.time * 7.5)) * 0.3;
                    this.targetMouthOpen = Math.min(0.85, syll);
                }
            } else if (this.currentState === 'speaking') {
                // Decay manual speaking pulse (e.g. from Web Speech API word boundaries)
                if (this.manualSpeakingPulse > 0.05) {
                    this.manualSpeakingPulse -= dt * 3.5;
                    this.targetMouthOpen = this.manualSpeakingPulse;
                } else {
                    this.targetMouthOpen = 0;
                }
            } else {
                this.targetMouthOpen = 0;
            }

            // Smooth interpolation to target mouth opening
            this.mouthOpenValue += (this.targetMouthOpen - this.mouthOpenValue) * 0.35;

            // 5. LLM Feedback & Emotion Expression Computation
            let finalAngleX = this.currentAngleX;
            let finalAngleY = this.currentAngleY;
            let finalAngleZ = 0;
            let finalEyeX = this.currentEyeX;
            let finalEyeY = this.currentEyeY;
            let eyeLOpen = eyeOpen;
            let eyeROpen = eyeOpen;
            let eyeSmile = 0.15;
            let cheek = 0.15;
            let mouthForm = 0.25;
            let browLY = 0;
            let browRY = 0;
            let browLAngle = 0;
            let browRAngle = 0;

            const emotion = this.currentEmotion || 'friendly';
            const overallScore = (this.currentFeedback && typeof this.currentFeedback.overall_score === 'number') 
                ? this.currentFeedback.overall_score 
                : 0;
            const hasCorrections = Boolean(
                this.currentFeedback && 
                this.currentFeedback.corrections && 
                this.currentFeedback.corrections.length > 0
            );

            if (this.currentState === 'speaking') {
                // Speech rhythmic nodding
                const nod = Math.sin(this.time * 4.8) * 1.8;
                finalAngleY += nod;

                if (emotion === 'happy' || overallScore >= 85) {
                    // High praise / excellent score: joyous crinkled eyes, radiant smile, cute blush
                    eyeSmile = 0.85;
                    cheek = 0.55;
                    mouthForm = 0.8;
                    browLY = 0.35;
                    browRY = 0.35;
                    finalAngleZ = -2.5 + Math.sin(this.time * 2.2) * 1.2;
                } else if (emotion === 'supportive' || hasCorrections) {
                    // Supportive feedback: empathetic caring expression, gentle encouraging nod
                    eyeSmile = 0.4;
                    cheek = 0.25;
                    mouthForm = 0.35;
                    browLAngle = 0.25;
                    browRAngle = 0.25;
                    browLY = 0.2;
                    browRY = 0.2;
                    finalAngleZ = 2.0 + Math.sin(this.time * 1.8) * 0.9;
                } else if (emotion === 'curious') {
                    // Inquisitive inquiry / question: wide alert eyes, raised brows, inquisitive tilt
                    eyeLOpen = Math.min(1.15, eyeOpen * 1.15);
                    eyeROpen = Math.min(1.15, eyeOpen * 1.15);
                    browLY = 0.45;
                    browRY = 0.45;
                    mouthForm = 0.35;
                    cheek = 0.2;
                    finalAngleZ = -4.0;
                    finalAngleX += 2.5;
                } else {
                    // Friendly conversational default
                    eyeSmile = 0.45;
                    cheek = 0.3;
                    mouthForm = 0.5;
                    finalAngleZ = Math.sin(this.time * 1.6) * 1.0;
                }
            } else if (this.currentState === 'listening') {
                // Listening state: attentive forward tilt, alert eyes
                finalAngleZ = -3.5 + Math.sin(this.time * 1.4) * 0.8;
                finalAngleY += 3.0;
                eyeLOpen = Math.min(1.05, eyeOpen * 1.05);
                eyeROpen = Math.min(1.05, eyeOpen * 1.05);
                cheek = 0.2;
                mouthForm = 0.25;
            } else if (this.currentState === 'thinking') {
                // Thinking state: thoughtful upward & sideways glance
                finalAngleY += 8.0;
                finalAngleX += -5.0;
                finalAngleZ = 3.0;
                finalEyeY = Math.max(finalEyeY, 0.5);
                finalEyeX = -0.3;
                eyeLOpen = Math.max(0.7, eyeOpen);
                eyeROpen = Math.max(0.7, eyeOpen);
                browLY = -0.1;
                browRY = -0.1;
                mouthForm = -0.1;
            } else {
                // Idle state: subtle idle head float, retaining gentle warmth from recent feedback
                if (overallScore >= 85) {
                    eyeSmile = 0.35;
                    mouthForm = 0.45;
                    cheek = 0.28;
                } else if (hasCorrections) {
                    eyeSmile = 0.25;
                    mouthForm = 0.3;
                    cheek = 0.2;
                } else {
                    eyeSmile = 0.2;
                    mouthForm = 0.3;
                    cheek = 0.18;
                }
                finalAngleY += Math.sin(this.time * 1.2) * 1.2;
                finalAngleZ = Math.sin(this.time * 0.9) * 0.8;
            }

            // 6. Apply Values to Live2D Parameters
            this._setParam(coreModel, 'ParamAngleX', finalAngleX);
            this._setParam(coreModel, 'ParamAngleY', finalAngleY);
            this._setParam(coreModel, 'ParamAngleZ', finalAngleZ);

            this._setParam(coreModel, 'ParamEyeBallX', finalEyeX);
            this._setParam(coreModel, 'ParamEyeBallY', finalEyeY);

            this._setParam(coreModel, 'ParamEyeLOpen', eyeLOpen);
            this._setParam(coreModel, 'ParamEyeROpen', eyeROpen);
            this._setParam(coreModel, 'ParamEyeLSmile', eyeSmile);
            this._setParam(coreModel, 'ParamEyeRSmile', eyeSmile);

            this._setParam(coreModel, 'ParamBrowLY', browLY);
            this._setParam(coreModel, 'ParamBrowRY', browRY);
            this._setParam(coreModel, 'ParamBrowLAngle', browLAngle);
            this._setParam(coreModel, 'ParamBrowRAngle', browRAngle);

            this._setParam(coreModel, 'ParamMouthOpenY', this.mouthOpenValue);
            this._setParam(coreModel, 'ParamMouthForm', mouthForm);
            this._setParam(coreModel, 'ParamCheek', cheek);

            // Subtle hair sway
            const hairSway = Math.sin(this.time * 2.0) * 0.15 + (finalAngleX / 20.0) * 0.2;
            this._setParam(coreModel, 'ParamHairFront', hairSway);
            this._setParam(coreModel, 'ParamHairSide', hairSway);
            this._setParam(coreModel, 'ParamHairBack', hairSway * 0.6);

            // Render current frame
            this.app.render();
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
            window.removeEventListener('pointermove', this._onMouseMove);
            document.removeEventListener('mouseleave', this._onMouseLeave);

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
                modelPath: 'assets/live2d/MILO Model.model3.json?v=20261124a'
            });
        }
    });

})();
