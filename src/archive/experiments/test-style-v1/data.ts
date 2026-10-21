import type {GapQuizData} from '../../../templates/GapQuiz';
export const testStyleV1 = {
  tag: 'Phrase à trou · Le piège du jour',
  hookLines: ['Un mot manque.', 'Tu le trouves ?'], hookLead: 'Tu as 3 secondes.', topicLines: ['Make', 'ou do ?'],
  sentence: {before:'Can you', after:'me a favor?', answer:'do', translationLines:['Tu peux me rendre', 'un service ?']},
  choices: ['make','do','give'], hintLines:['Écris ta réponse', 'en commentaire'], feedbackLines:['Bien joué si tu', 'as dit do !'],
  tipTag:'Astuce · Make ou do ?', tipTitleLines:['Make ou do ?', 'Un repère utile.'],
  tipColumns:[
    {word:'do',subtitleLines:['+ une action'],examples:['a favor','homework','the dishes','your best'],correctExample:'a favor'},
    {word:'make',subtitleLines:['+ créer,','fabriquer'],examples:['a cake','a mistake','money','a decision']},
  ],
  tipNoteLines:['Un repère simplifié,', 'pas une règle universelle.'],
  endLines:['Un piège','par jour.'], endLeadLines:['Abonne-toi pour', 'le prochain piège.'], next:{meta:'Demain',teaser:'say ou tell ?'},
  timing:{question:60,timer:156,answer:242,success:244,tip:300,end:420},
} as const satisfies GapQuizData;
