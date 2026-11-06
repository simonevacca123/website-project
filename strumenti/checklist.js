(() => {
  'use strict';
  const form = document.querySelector('#checklist-form'), result = document.querySelector('#checklist-result');
  const status = document.querySelector('#checklist-status'), report = document.querySelector('#checklist-report');
  const fields = [...form.querySelectorAll('select')];
  function clear() { result.hidden = true; report.value = ''; status.textContent = ''; document.querySelector('#report-status').textContent = ''; fields.forEach(field => field.removeAttribute('aria-invalid')); }
  form.addEventListener('change', clear);
  form.addEventListener('reset', () => { clear(); status.textContent = 'Risposte azzerate. Puoi ricominciare.'; });
  form.addEventListener('submit', event => {
    event.preventDefault(); clear();
    const missing = fields.find(field => !['yes', 'no', 'unknown'].includes(field.value));
    if (missing) { missing.setAttribute('aria-invalid', 'true'); missing.focus(); status.textContent = 'Rispondi a tutte le domande. Puoi scegliere “Non so”.'; return; }
    const strengths = [], issues = [], doubts = [];
    fields.forEach(field => {
      const title = field.dataset.title, advice = field.dataset.advice;
      if (field.value === 'yes') strengths.push('- ' + title + ': positivo secondo la tua risposta.');
      else if (field.value === 'no') issues.push({priority: Number(field.dataset.priority), text: title + ': ' + advice});
      else doubts.push('- ' + title + ': ' + advice);
    });
    issues.sort((a,b) => a.priority - b.priority);
    report.value = ['AUTOVALUTAZIONE DEL SITO', 'Basata su 8 risposte. Nessuna scansione tecnica automatica.', '', 'PUNTI DI FORZA', strengths.join('\n') || 'Nessun punto confermato dalle risposte.', '', 'PROBLEMI POTENZIALI E PRIORITÀ', issues.map(item => '- Priorità ' + (item.priority === 1 ? 'alta' : 'media') + ' — ' + item.text).join('\n') || 'Nessun problema segnalato: questo non certifica la qualità del sito.', '', 'ASPETTI DA VERIFICARE', doubts.join('\n') || 'Nessuna risposta “Non so”.', '', 'PROSSIMO PASSO', 'Verifica le priorità con una persona esterna e, per accessibilità e prestazioni, con prove tecniche. Puoi condividere questo report con Simone tramite i contatti del sito.'].join('\n');
    result.hidden = false; status.textContent = `Report pronto: ${strengths.length} punti positivi, ${issues.length} problemi potenziali e ${doubts.length} aspetti da verificare.`;
    document.querySelector('#report-title').focus();
  });
  document.querySelector('#report-copy').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(report.value); document.querySelector('#report-status').textContent = 'Report copiato.'; }
    catch { report.focus(); report.select(); document.querySelector('#report-status').textContent = 'Testo selezionato: usa Copia sul telefono, Ctrl+C su Windows o ⌘C su Mac.'; }
  });
  document.querySelector('#report-download').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([report.value], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'autovalutazione-sito.txt'; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    document.querySelector('#report-status').textContent = 'Download richiesto. Cerca autovalutazione-sito.txt nei download del browser.';
  });
})();
