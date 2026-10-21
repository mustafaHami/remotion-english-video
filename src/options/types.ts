import type {LessonData} from '../content/LessonContent';
export type VoiceClip={start:number;duration:number;src:string;text:string;voice:string;role:'intro'|'lesson'|'outro';peaks:number[]};
export type LessonInput={option:number;title:string;introText:string;timing:{introFrames:number;bodyFrames:number;outroFrames:number;pageFrames:number;answerAt:number;pauseAt:number;firstReveal:number;rowFrames:number};lessonData:Partial<LessonData>;narration:VoiceClip[];verb?:string;writingPaths?:Record<string,import('../components/WrittenText').WritingPath>};
