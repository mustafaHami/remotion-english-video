import React from 'react';
import {AbsoluteFill} from 'remotion';
import {color, layout, radius} from '../design/tokens';
import {type} from '../design/typography';

export const Stage: React.FC<React.PropsWithChildren> = ({children}) => <AbsoluteFill style={{backgroundColor: color.lavender}}>
  <div style={{position: 'absolute', width: layout.width, height: layout.height, transform: `scale(${layout.scale})`, transformOrigin: '0 0', overflow: 'hidden', color: color.ink}}>{children}</div>
</AbsoluteFill>;
export const Card: React.FC<React.PropsWithChildren<{background: string; y?: number}>> = ({background, y = 0, children}) =>
  <div style={{position: 'absolute', inset: 0, background, transform: `translateY(${y}px)`, overflow: 'hidden'}}>{children}</div>;
export const Sheet: React.FC<{top: number}> = ({top}) => <div style={{position: 'absolute', left: 0, top, width: layout.width, height: layout.height, borderRadius: `${radius.sheet}px ${radius.sheet}px 0 0`, background: color.sheet}}/>;
/** Keep platform chrome clear even while a complete card is travelling. */
export const SafeContent: React.FC<React.PropsWithChildren<{offset: number;top?:number;bottom?:number;right?:number}>> = ({offset,top=40,bottom=520,right=300, children}) => <div data-safe-mask style={{position:'absolute',inset:0,clipPath:`polygon(0px ${top-offset}px, 360px ${top-offset}px, 360px ${290-offset}px, ${right}px ${290-offset}px, ${right}px ${bottom-offset}px, 0px ${bottom-offset}px)`}}>{children}</div>;
export const Tag: React.FC<React.PropsWithChildren> = ({children}) => <div style={{...type.tag, position: 'absolute', top: 52, left: 20, padding: '7px 12px', borderRadius: radius.pill, background: color.ink, whiteSpace: 'nowrap'}}>{children}</div>;

const paths = {
  check: ['M5 12.5l4.5 4.5L19 7.5'], comment: ['M4.5 18.5l1.2-3.6A7.5 7.5 0 1 1 9 18.2z'],
  bell: ['M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15z', 'M10 20.5a2.2 2.2 0 0 0 4 0'],
};
export const Icon: React.FC<{name: keyof typeof paths; size: number; tint?: string; stroke?: number}> = ({name, size, tint = color.ink, stroke = 2.2}) =>
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={tint} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" style={{display: 'block', flexShrink: 0}} aria-hidden>{paths[name].map(d => <path key={d} d={d}/>)}</svg>;

export const Decor: React.FC<{frame: number; circle: [number, number, number, number]; sparks?: [number, number, number][]}> = ({frame, circle: [x, y, r, opacity], sparks = []}) => {
  const drift = -8 * (.5 - .5 * Math.cos(2 * Math.PI * frame / 120));
  return <svg width="360" height="640" style={{position: 'absolute', inset: 0, transform: `translateY(${drift}px)`}} aria-hidden>
    <circle cx={x} cy={y} r={r} fill={color.sheet} opacity={opacity}/>
    {sparks.map(([cx, cy, size]) => <path key={`${cx}-${cy}`} fill={color.sheet} d={`M${cx},${cy-size} l${.3125*size},${.6875*size} l${.6875*size},${.3125*size} l${-.6875*size},${.3125*size} l${-.3125*size},${.6875*size} l${-.3125*size},${-.6875*size} l${-.6875*size},${-.3125*size} l${.6875*size},${-.3125*size} z`}/>)}
  </svg>;
};
