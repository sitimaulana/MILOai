/**
 * MILO Live2D Companion Controller
 * Multimodal Interactive Learning Companion
 * 
 * Handles:
 * - Live2D Cubism 4 initialization via PixiJS & pixi-live2d-display
 * - Half-body (bust/chest-up) viewport framing and responsive resizing
 * - Natural micro-animations (breathing, eye blinking, hair physics, cursor gaze tracking)
 * - State management ('idle', 'listening', 'thinking', 'speaking')
 * - Dynamic lip-sync during AI speech
 * - Graceful fallback to static image on failure or unsupported environments
 */

(function () {
    'use strict';

    class MiloLive2DCompanion {
        constructor(options = {}) {
            this.canvasId = options.canvasId || 'miloLive2DCanvas';
            this.fallbackImgId = options.fallbackImgId || 'miloCharacterImg';
            this.stageId = options.stageId || 'miloCompanionStage';
            this.modelPath = options.modelPath || 'assets/live2d/MILO Model.model3.json?v=20261123f';

            // Half-body framing configuration based on Image 2 reference:
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
                // High-DPI resolution for razor-sharp rendering (supersampling at least 2x)
                const dpr = Math.max(window.devicePixelRatio || 1, 2);

                if (PIXI.settings) {
                    PIXI.settings.RESOLUTION = dpr;
                    PIXI.settings.ROUND_PIXELS = true;
                    PIXI.settings.ANISOTROPIC_LEVEL = 16;
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

                // Create PixiJS Application with transparent background and 2x resolution
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

                // Ensure base textures are sharp and do not downsample via blurry mipmaps
                this._ensureCrispTextures();

                // Setup event listeners
                window.addEventListener('resize', this._onResize, { passive: true });
                window.addEventListener('pointermove', this._onMouseMove, { passive: true });
                document.addEventListener('mouseleave', this._onMouseLeave, { passive: true });
                this._initResizeObserver();

                // Start Pixi ticker loop
                this.app.ticker.add(this._animate);
                this.app.start();

                this.isReady = true;
                console.log('✅ [MiloLive2D] Milo Live2D companion ready in crisp half-body mode!');

                // Smoothly reveal canvas and hide fallback image
                if (this.fallbackImg) {
                    this.fallbackImg.style.display = 'none';
                }
                this.canvas.style.opacity = '1';
                this.canvas.classList.add('live2d-loaded');

                // Delayed resize to ensure layout is fully settled after styles load
                setTimeout(() => this._onResize(), 150);

            } catch (err) {
                console.error('❌ [MiloLive2D] Failed to initialize Live2D model:', err);
                // Ensure static image remains visible
                if (this.fallbackImg) {
                    this.fallbackImg.style.display = '';
                }
            }
        }

        _ensureCrispTextures() {
            if (!this.model) return;
            try {
                if (this.model.textures && Array.isArray(this.model.textures)) {
                    this.model.textures.forEach(tex => {
                        if (tex && tex.baseTexture) {
                            tex.baseTexture.scaleMode = PIXI.SCALE_MODES.LINEAR;
                            tex.baseTexture.mipmap = PIXI.MIPMAP_MODES.OFF;
                            tex.baseTexture.update();
                        }
                    });
                }
            } catch (e) {
                // Ignore transient texture mode setup
            }
        }

        _initResizeObserver() {
            if (window.ResizeObserver && this.canvas && this.canvas.parentElement) {
                this.resizeObserver = new ResizeObserver(() => {
                    this._onResize();
                });
                this.resizeObserver.observe(this.canvas.parentElement);
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

            const dpr = Math.max(window.devicePixelRatio || 1, 2);
            if (this.app.renderer.resolution !== dpr) {
                this.app.renderer.resolution = dpr;
            }

            this.app.renderer.resize(cw, ch);
            this._applyHalfBodyFraming(cw, ch);
            this._ensureCrispTextures();
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

            // 4. State-specific Modulations
            let finalAngleX = this.currentAngleX;
            let finalAngleY = this.currentAngleY;
            let finalAngleZ = 0;
            let finalEyeX = this.currentEyeX;
            let finalEyeY = this.currentEyeY;
            let eyeSmile = 0.1;
            let cheek = 0.15;
            let mouthForm = 0.2;

            if (this.currentState === 'listening') {
                // Listening state: attentive head tilt, alert eyes
                finalAngleZ = -4.0 + Math.sin(this.time * 1.5) * 1.0;
                finalAngleY += 3.0;
                eyeOpen = Math.min(1.0, eyeOpen * 1.05);
                cheek = 0.2;
            } else if (this.currentState === 'thinking') {
                // Thinking state: upward & slightly sideways thoughtful glance
                finalAngleY += 10.0;
                finalAngleX += -6.0;
                finalAngleZ = 3.0;
                finalEyeY = Math.max(finalEyeY, 0.55);
                finalEyeX = -0.3;
                eyeOpen = Math.max(0.65, eyeOpen);
                mouthForm = -0.1;
            } else if (this.currentState === 'speaking') {
                // Speaking state: cheerful smile, gentle rhythmic nodding, active lip-sync
                eyeSmile = 0.5;
                cheek = 0.45;
                mouthForm = 0.5;
                const nod = Math.sin(this.time * 5.5) * 2.5;
                finalAngleY += nod;

                // Speech Lip-Sync: composite rhythmic wave mimicking speech phonemes
                const speechWave = Math.abs(Math.sin(this.time * 13.0)) * 0.65 
                                 + Math.abs(Math.sin(this.time * 6.5)) * 0.35;
                this.targetMouthOpen = speechWave;
            } else {
                // Idle state: subtle idle head float
                finalAngleY += Math.sin(this.time * 1.2) * 1.2;
                finalAngleZ = Math.sin(this.time * 0.9) * 0.8;
                this.targetMouthOpen = 0;
            }

            // Smooth mouth closing/opening transition
            this.mouthOpenValue += (this.targetMouthOpen - this.mouthOpenValue) * 0.25;

            // 5. Apply Values to Live2D Parameters
            this._setParam(coreModel, 'ParamAngleX', finalAngleX);
            this._setParam(coreModel, 'ParamAngleY', finalAngleY);
            this._setParam(coreModel, 'ParamAngleZ', finalAngleZ);

            this._setParam(coreModel, 'ParamEyeBallX', finalEyeX);
            this._setParam(coreModel, 'ParamEyeBallY', finalEyeY);

            this._setParam(coreModel, 'ParamEyeLOpen', eyeOpen);
            this._setParam(coreModel, 'ParamEyeROpen', eyeOpen);
            this._setParam(coreModel, 'ParamEyeLSmile', eyeSmile);
            this._setParam(coreModel, 'ParamEyeRSmile', eyeSmile);

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
    window.setCompanionState = function (state, text) {
        if (typeof prevSetCompanionState === 'function') {
            prevSetCompanionState(state, text);
        }
        if (window.miloLive2D && typeof window.miloLive2D.setState === 'function') {
            window.miloLive2D.setState(state);
        }
    };

    // Auto-initialize when DOM is ready if canvas exists
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('miloLive2DCanvas');
        if (canvas && !window.miloLive2D) {
            window.miloLive2D = new MiloLive2DCompanion({
                canvasId: 'miloLive2DCanvas',
                fallbackImgId: 'miloCharacterImg',
                modelPath: 'assets/live2d/MILO Model.model3.json?v=20261123f'
            });
        }
    });

})();
