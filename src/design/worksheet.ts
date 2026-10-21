import {type} from './typography';
const gridLeft=24, columnWidth=104;
export const worksheet = {
  card:{left:12,top:134,width:336,height:342,radius:28,border:2},
  grid:{left:gridLeft,width:312,top:190,rowHeight:27,rowCount:10},
  columns:Array.from({length:3},(_,index)=>({x:gridLeft+index*columnWidth,width:columnWidth,center:gridLeft+(index+.5)*columnWidth})),
  rows:Array.from({length:10},(_,index)=>191.5+index*27),
  headers:{top:148,width:96,height:30},
  statusBox:{left:12,top:488,width:336,height:26},
  title:{...type.hookTitle,fontSize:28,lineHeight:1.12,whiteSpace:'nowrap' as const},
  header:{...type.pill,fontSize:13},
  status:{...type.hint,fontSize:14,whiteSpace:'nowrap' as const},
} as const;
