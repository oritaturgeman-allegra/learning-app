/**
 * Audio module — AudioContext tones + Web Speech API TTS.
 * Ported from shared.js (lines 62-111) and english-game.js (lines 17-37).
 *
 * These are pure functions (not a React hook) since AudioContext is a
 * singleton that doesn't need React state management.
 */

let audioCtx: AudioContext | null = null;

/** Initialize AudioContext. Must be called on a user gesture (e.g., button click). */
export function initAudio(): void {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }
}

function playTone(freq: number, duration: number, type: OscillatorType, startTime: number): void {
  if (!audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.3, startTime);
  gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.start(startTime);
  osc.stop(startTime + duration);
}

/** Ascending C5-E5-G5 chime for correct answers. */
export function playCorrect(): void {
  initAudio();
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  playTone(523.25, 0.15, "sine", now);       // C5
  playTone(659.25, 0.15, "sine", now + 0.1); // E5
  playTone(783.99, 0.25, "sine", now + 0.2); // G5
}

/** Low 150Hz sawtooth buzz for wrong answers. */
export function playWrong(): void {
  initAudio();
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  playTone(150, 0.3, "sawtooth", now);
}

/** Four-note C5-E5-G5-C6 celebration melody (~1s). */
export function playCelebration(): void {
  initAudio();
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  playTone(523.25, 0.2, "sine", now);        // C5
  playTone(659.25, 0.2, "sine", now + 0.2);  // E5
  playTone(783.99, 0.2, "sine", now + 0.4);  // G5
  playTone(1046.5, 0.4, "sine", now + 0.6);  // C6
}

/**
 * Text-to-speech for English words.
 * Voice priority: Samantha > Female > en-US > any English.
 */
export function speak(text: string): void {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.85;
  utterance.pitch = 1.1;

  const voices = window.speechSynthesis.getVoices();
  const voice =
    voices.find((v) => v.lang === "en-US" && v.name.includes("Samantha")) ||
    voices.find((v) => v.lang === "en-US" && v.name.includes("Female")) ||
    voices.find((v) => v.lang === "en-US") ||
    voices.find((v) => v.lang.startsWith("en"));
  if (voice) utterance.voice = voice;

  window.speechSynthesis.speak(utterance);
}
