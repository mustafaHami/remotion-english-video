import type {CSSProperties} from 'react';
import {Easing, interpolate, spring} from 'remotion';
export const curve = {
  standard: Easing.bezier(.2, .9, .3, 1), reveal: Easing.bezier(.2, 1.2, .3, 1),
  drop: Easing.bezier(.2, 1.5, .4, 1), press: Easing.bezier(.3, .7, .4, 1),
};
export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
export const progress = (frame: number, start: number, duration: number) => clamp01((frame - start) / duration);
export const tween = (frame: number, start: number, duration: number, easing = curve.standard) => easing(progress(frame, start, duration));
export const reveal = (frame: number, start: number, distance = 12, duration = 8): CSSProperties => ({
  opacity: progress(frame, start, duration), transform: `translateY(${distance * (1 - tween(frame, start, duration, curve.reveal))}px)`,
});
export const pop = (frame: number, start: number, from = .8, duration = 8, easing = curve.reveal): CSSProperties => ({
  opacity: progress(frame, start, duration), transform: `scale(${from + (1 - from) * tween(frame, start, duration, easing)})`,
});
export const swipe = (frame: number, start: number, fps: number) => {
  if (frame <= start) return 0;
  if (frame >= start + 14) return 1;
  return clamp01(spring({frame: frame - start, fps, durationInFrames: 14, config: {damping: 20, stiffness: 180, mass: 1}}));
};
export const bump = (frame: number, start: number, duration: number, amount: number) =>
  1 + amount * Math.sin(Math.PI * tween(frame, start, duration));
export const ringAngle = (frame: number) => interpolate(frame, [456, 459, 462, 465, 468], [0, 12, -10, 6, 0], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: curve.standard,
});
