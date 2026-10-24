// Arguments séparés fournis par le lanceur ; aucune instruction provenant du contenu.
const path = require('node:path');
const {ROOT, read, validate, validateSocial, fingerprint, duplicates} = require('../scripts/lib/lesson.cjs');
const [episodePath, lessonPath, manifestPath] = process.argv.slice(2);
try {
  const episode = validate(read(episodePath));
  // Une vidéo issue de Telegram doit pouvoir préparer ses brouillons Buffer.
  validateSocial(episode.social);
  const lesson = validate(read(lessonPath));
  const manifest = read(manifestPath);
  if (fingerprint(episode) !== fingerprint(lesson) || fingerprint(episode) !== manifest.contentFingerprint) {
    throw Error('Le rapport et les données ne correspondent plus au contenu rendu.');
  }
  if (duplicates(episode, read(path.join(ROOT, 'planning/publications.json'))).length) {
    throw Error('Contenu déjà présent dans les publications.');
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
