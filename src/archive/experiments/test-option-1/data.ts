export type TenseRow = {present:string;past:string;future:string};
export type WritingEvent = {column:1|2;row:number;text:string;start:number;duration:number};
import rows from './rows.json';
import renderConfig from './render-config.json';
export const optionOne = {
  title:'Présent, passé, futur.',
  columns:['Présent','Passé','Futur'],
  rows:rows satisfies TenseRow[],
  events:[
    ...rows.map((row,index):WritingEvent=>({column:1,row:index,text:row.past,start:210+index*48,duration:36})),
    ...rows.map((row,index):WritingEvent=>({column:2,row:index,text:row.future,start:870+index*54,duration:44})),
  ] satisfies WritingEvent[],
  waits:[{start:60,end:210},{start:720,end:870}],
  futureAt:720,
  completeAt:1410,
  duration:renderConfig.durationInFrames,
} as const;
