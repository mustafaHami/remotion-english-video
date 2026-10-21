import React from 'react';
import {color, border, ledge, radius} from '../design/tokens';
import {type} from '../design/typography';
import {bump, curve, pop, progress, reveal, tween} from '../design/motion';
import {Icon} from './LessonPrimitives';

export type SentenceData = {before: string; after: string; answer: string; translationLines: readonly string[]};
export const Sentence: React.FC<{frame: number; data: SentenceData; answerAt: number}> = ({frame, data, answerAt}) => {
  const drop = tween(frame, answerAt, 14, curve.drop);
  const breathing = frame >= 78 && frame < answerAt ? 1 + .04 * (.5 - .5 * Math.cos((frame - 78) * 2 * Math.PI / 30)) : 1;
  return <div data-safe="sentence" style={{...type.sentence, position: 'absolute', left: 20, top: 212, width: 280, ...reveal(frame, 70)}}>
    <div style={{display: 'flex', alignItems: 'baseline', gap: 8, whiteSpace: 'nowrap'}}><span>{data.before}</span>
      <span style={{position: 'relative', display: 'inline-block', width: 92, height: 40, transform: 'translateY(8px)', flexShrink: 0}}>
        <span style={{boxSizing: 'border-box', position: 'absolute', inset: 0, border: `${border.blank}px dotted ${color.coral}`, borderRadius: radius.chip, transform: `scale(${breathing})`, opacity: 1 - progress(frame, answerAt, 4)}}/>
        <span style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: radius.chip, background: color.successBg, color: color.success, padding: '0 12px', opacity: progress(frame, answerAt, 8), transform: `translateY(${-16 * (1-drop)}px) scale(${.8 + .2*drop})`}}>{data.answer}</span>
      </span>
    </div><div>{data.after}</div>
  </div>;
};
export const Options: React.FC<{frame: number; choices: readonly string[]; answer: string; successAt: number}> = ({frame, choices, answer, successAt}) => <div style={{position: 'absolute', left: 24, top: 398, width: 272, display: 'flex', gap: 8}}>
  {choices.map((choice, i) => {
    const selected = choice === answer;
    const active = frame >= successAt;
    const faded = active && !selected;
    const fade = 1 - .55 * tween(frame, successAt, 8);
    return <div key={choice} style={{flex: 1, minWidth: 0, ...reveal(frame, 82+i*4, 16), opacity: progress(frame, 82+i*4, 8) * (faded ? fade : 1)}}>
      <div data-safe={`option-${choice}`} style={{...type.option, boxSizing: 'border-box', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: radius.option,
        background: active && selected ? color.successBg : color.surface,
        color: active && selected ? color.success : color.ink,
        border: `${border.normal}px solid ${active && selected ? color.success : color.line}`,
        boxShadow: faded ? 'none' : ledge(4, active && selected ? color.success : color.ledge),
        transform: `scale(${selected ? bump(frame, successAt, 16, .05) : 1})`}}>
        {active && selected ? <Icon name="check" size={16} stroke={3.4} tint={color.success}/> : null}{choice}
      </div>
    </div>;
  })}
</div>;

export const Timer: React.FC<{frame: number; start: number; end: number}> = ({frame, start, end}) => {
  const remaining = Math.max(0, 1 - progress(frame, start, end-start));
  const elapsed = Math.max(0, frame-start);
  const digit = Math.max(1, 3 - Math.floor(elapsed/30));
  const digitStart = start + Math.min(2, Math.floor(elapsed/30))*30;
  const fade = 1 - progress(frame, end, 6);
  return <div data-safe="timer" style={{position: 'absolute', left: 246, top: 108, width: 68, height: 68, borderRadius: '50%', background: color.surface, boxShadow: ledge(), ...pop(frame, start, 0, 14, curve.drop), opacity: progress(frame, start, 8)*fade, transform: `scale(${tween(frame, start, 14, curve.drop)*(1-.4*progress(frame,end,6))})`}}>
    <svg width="68" height="68" style={{position:'absolute', inset:0}}><circle cx="34" cy="34" r="27" fill="none" stroke={color.track} strokeWidth="7"/><circle cx="34" cy="34" r="27" fill="none" stroke={color.coral} strokeWidth="7" strokeLinecap="round" strokeDasharray={2*Math.PI*27} strokeDashoffset={2*Math.PI*27*(1-remaining)} transform="rotate(-90 34 34)"/></svg>
    <div style={{...type.timerDigit, position: 'absolute', inset: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', transform: `scale(${1+.15*(1-tween(frame,digitStart,6,curve.reveal))})`}}>{digit}</div>
  </div>;
};
