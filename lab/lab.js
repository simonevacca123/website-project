'use strict';

const form = document.querySelector('#cleaner-form');
const source = document.querySelector('#source-list');
const ignoreCase = document.querySelector('#ignore-case');
const result = document.querySelector('#cleaner-result');
const output = document.querySelector('#clean-list');
const status = document.querySelector('#cleaner-status');

function resetResult() {
  result.hidden = true;
  output.value = '';
  status.textContent = '';
  status.classList.remove('error-message');
  source.removeAttribute('aria-invalid');
}

source.addEventListener('input', resetResult);
ignoreCase.addEventListener('change', resetResult);
document.querySelector('#load-example').addEventListener('click', () => {
  resetResult();
  source.value = 'Controllare preventivo\nAggiornare catalogo\ncontrollare preventivo\nContattare fornitore\n Aggiornare catalogo ';
  status.textContent = 'Esempio caricato: premi Trova i doppioni per vedere il risultato.';
  source.focus();
});
document.querySelector('#clear-list').addEventListener('click', () => {
  form.reset();
  resetResult();
  status.textContent = 'Elenco svuotato. Puoi inserire nuovi dati.';
  source.focus();
});

form.addEventListener('submit', event => {
  event.preventDefault();
  resetResult();
  const lines = source.value.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
  if (!lines.length || lines.length > 500 || source.value.length > 20000) {
    status.classList.add('error-message');
    status.textContent = !lines.length ? 'Inserisci almeno una voce, oppure carica l’esempio.' : 'Usa al massimo 500 righe non vuote e 20.000 caratteri.';
    source.setAttribute('aria-invalid', 'true');
    source.focus();
    return;
  }
  const seen = new Set();
  const unique = lines.filter(line => {
    const normalized = line.normalize('NFC');
    const key = ignoreCase.checked ? normalized.toLocaleLowerCase('it-IT') : normalized;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  output.value = unique.join('\n');
  document.querySelector('#input-count').textContent = lines.length;
  document.querySelector('#unique-count').textContent = unique.length;
  document.querySelector('#duplicate-count').textContent = lines.length - unique.length;
  result.hidden = false;
  status.textContent = `Controllo completato: ${unique.length} voci uniche su ${lines.length}. Il risultato è pronto da verificare e copiare.`;
});

document.querySelector('#copy-list').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(output.value);
    status.textContent = 'Risultato copiato. Puoi incollarlo dove ti serve.';
  } catch {
    output.focus();
    output.select();
    status.textContent = 'Testo selezionato: usa Copia sul telefono, Ctrl+C su Windows o ⌘C su Mac.';
  }
});
