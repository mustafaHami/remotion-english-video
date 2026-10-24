import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const sdk=process.env.ARTIFACT_TOOL_MODULE;
const {Workbook,SpreadsheetFile}=await import(sdk?pathToFileURL(sdk).href:'@oai/artifact-tool');
const wb=Workbook.create();
const calendar=JSON.parse(await fs.readFile('planning/calendar.json','utf8'));
const records=JSON.parse(await fs.readFile('planning/publications.json','utf8'));
try {
 const production=JSON.parse(await fs.readFile('planning/production.json','utf8'));
 if(production.videos.some(r=>!r.external))throw new Error('Suivi de production présent : utiliser scripts/planning/maintain-tracking.py pour préserver le Journal existant.');
} catch(error) {if(error.code!=='ENOENT')throw error;}
const sheet=wb.worksheets.add('Calendrier');
sheet.showGridLines=false;sheet.tabColor='#6A3FD1';
sheet.getRange('A1:O21').format.font={name:'Arial',size:10,color:'#1E1B3A'};
sheet.getRange('A2').values=[['Calendrier des vidéos d’anglais']];sheet.getRange('A2').format.font={name:'Arial',size:14,bold:true};
sheet.getRange('A3').values=[['Publications connues au 21/10/2026. Les autres cellules restent disponibles pour le planning.']];
sheet.getRange('A5:O5').values=[['Date',...Array.from({length:14},(_,i)=>`Option ${i+1}`)]];
sheet.getRange('A5:O5').format={fill:'#1E1B3A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:28};
sheet.getRange('A6:O20').values=calendar.map(row=>[new Date(row.date+'T00:00:00Z'),...Array.from({length:14},(_,i)=>row.options[String(i+1)]??null)]);
sheet.getRange('A6:A20').setNumberFormat('dd/mm/yyyy');
sheet.getRange('A5:A20').format.columnWidth=14;sheet.getRange('B5:O20').format.columnWidth=23;
sheet.getRange('D5:E20').format.columnWidth=48;
sheet.getRange('B6:O20').format.wrapText=true;sheet.getRange('A6:O20').format.verticalAlignment='top';sheet.getRange('A6:O6').format.rowHeight=190;sheet.getRange('A7:O20').format.rowHeight=48;
sheet.getRange('D6:E6').format.fill='#D4F5E3';sheet.getRange('D6:E6').format.font={name:'Arial',size:10,color:'#137A4B'};
sheet.freezePanes.freezeRows(5);sheet.freezePanes.freezeColumns(1);
const journal=wb.worksheets.add('Journal');journal.showGridLines=false;journal.tabColor='#6FD6AE';
journal.getRange('A1:H8').format.font={name:'Arial',size:10,color:'#1E1B3A'};
journal.getRange('A2').values=[['Historique des publications']];journal.getRange('A2').format.font={name:'Arial',size:14,bold:true};
journal.getRange('A5:H5').values=[['Date','Option','Statut','Contenu utilisé','Identifiant','Plateformes','Liens','Source']];
journal.getRange('A5:H5').format={fill:'#1E1B3A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',rowHeight:28};
journal.getRange('A6:H7').values=records.map(r=>[new Date(r.date+'T00:00:00Z'),r.option,'Publié',r.content.join('\n'),r.id,r.platforms.join(', '),r.publicationUrls.join('\n'),r.source]);
journal.getRange('A6:A7').setNumberFormat('dd/mm/yyyy');journal.getRange('A5:H7').format.columnWidth=20;journal.getRange('A5:A7').format.columnWidth=14;journal.getRange('B5:C7').format.columnWidth=10;journal.getRange('D5:D7').format.columnWidth=58;journal.getRange('E5:E7').format.columnWidth=28;journal.getRange('H5:H7').format.columnWidth=44;journal.getRange('A6:H7').format.wrapText=true;journal.getRange('A6:H7').format.verticalAlignment='top';journal.getRange('A6:H7').format.rowHeight=190;
wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Calendrier!A5:E7',include:'values',tableMaxRows:3,tableMaxCols:5,maxChars:1500});console.log(check.ndjson);
await fs.mkdir('output/qa-planning',{recursive:true});
for(const [name,range,file] of [['Calendrier','A1:F8','calendar'],['Journal','A1:H7','journal']]){
 const preview=await wb.render({sheetName:name,range,scale:1.3,format:'png'});await fs.writeFile(`output/qa-planning/${file}.png`,new Uint8Array(await preview.arrayBuffer()));
}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save('planning/calendrier-publications.xlsx');
console.log('planning/calendrier-publications.xlsx');
