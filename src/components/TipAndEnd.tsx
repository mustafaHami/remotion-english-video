import React from 'react';
import {color, border, ledge, radius} from '../design/tokens';
import {type} from '../design/typography';
import {bump, pop, reveal, ringAngle} from '../design/motion';
import {Icon} from './LessonPrimitives';

export type TipColumnData = {word: string; subtitleLines: readonly string[]; examples: readonly string[]; correctExample?: string};
export const TipColumns: React.FC<{frame: number; columns: readonly TipColumnData[]}> = ({frame, columns}) => <div style={{position: 'absolute', left: 20, top: 254, width: 280, display: 'flex', gap: 14}}>
  {columns.map((column, col) => <div key={column.word} style={{width: 133}}>
    <div data-safe={`tip-${column.word}`} style={{...type.tipHeading, display:'inline-block', ...pop(frame, 318+col*8)}}>{column.word}</div>
    <div data-safe={`tip-sub-${col}`} style={{...type.tipSub, height: 37, marginTop: 4, marginBottom: 8, ...reveal(frame, 322+col*8, 6)}}>{column.subtitleLines.map((line,i) => <React.Fragment key={line}>{i>0?<br/>:null}{line}</React.Fragment>)}</div>
    {column.examples.map((example, row) => {
      const correct = example === column.correctExample;
      return <div key={example} style={{marginBottom: 8, ...reveal(frame,334+row*4+col*2,10)}}>
        <div data-safe={`pill-${example}`} style={{...type.pill, display: 'inline-flex', alignItems: 'center', gap: 6, boxSizing: 'border-box', height: 34, padding: '0 12px', borderRadius: radius.chip, whiteSpace: 'nowrap',
          border: `${border.normal}px solid ${correct ? color.success : color.lineSoft}`, background: correct ? color.successBg : color.surface, color: correct ? color.success : color.ink,
          boxShadow: ledge(3, correct ? color.success : color.ledge), transformOrigin: 'left center', transform: `scale(${correct ? bump(frame,360,16,.06) : 1})`}}>
          {correct ? <Icon name="check" size={12} stroke={3.6} tint={color.success}/> : null}{example}
        </div>
      </div>;
    })}
  </div>)}
</div>;
export const EndCard: React.FC<{frame: number; meta: string; teaser: string}> = ({frame, meta, teaser}) => <div data-safe="end-card" style={{position:'absolute', left:20, top:340, width:280, height:84, borderRadius:radius.card, border:`${border.normal}px solid ${color.lineSoft}`, boxSizing:'border-box', background:color.surface, boxShadow:ledge(), padding:'0 14px 0 18px', display:'flex', alignItems:'center', justifyContent:'space-between', ...reveal(frame,438,20,10)}}>
  <div><div style={type.meta}>{meta}</div><div style={{...type.teaser, marginTop:2}}>{teaser}</div></div>
  <div style={{width:44,height:44,borderRadius:'50%',background:color.mintSoft,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{transform:`rotate(${ringAngle(frame)}deg)`,transformOrigin:'50% 0'}}><Icon name="bell" size={22}/></div></div>
</div>;
