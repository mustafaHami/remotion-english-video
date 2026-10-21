import React,{createContext,useContext} from 'react';
import defaults from './defaults.json';
export type LessonData=typeof defaults;
export const LessonContentContext=createContext<LessonData>(defaults);
export const useLessonContent=()=>useContext(LessonContentContext);
export {defaults};
