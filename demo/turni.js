(() => {
  'use strict';
  const people = ['Persona A', 'Persona B', 'Persona C'];
  const days = ['Lunedì', 'Martedì', 'Mercoledì'];
  const initial = [['morning', 'morning', 'off'], ['morning', 'afternoon', 'afternoon'], ['afternoon', 'off', 'morning']];
  let assignments;
  const editor = document.querySelector('#schedule-editor');
  const target = document.querySelector('#coverage-target');
  const status = document.querySelector('#schedule-status');
  function update() {
    const needed = Number(target.value);
    const results = document.querySelector('#coverage-results');
    results.replaceChildren();
    if (!target.validity.valid || !Number.isInteger(needed) || needed < 1 || needed > 3) {
      target.setAttribute('aria-invalid', 'true'); status.textContent = 'Inserisci da 1 a 3 persone per fascia.'; document.querySelector('#schedule-total').textContent = ''; return;
    }
    target.removeAttribute('aria-invalid');
    let missing = 0, covered = 0;
    days.forEach((day, d) => {
      for (const [shift, label] of [['morning', 'Mattina'], ['afternoon', 'Pomeriggio']]) {
        const count = assignments.filter(person => person[d] === shift).length;
        const gap = Math.max(0, needed - count); missing += gap; if (!gap) covered++;
        const block = document.createElement('article'), heading = document.createElement('h3'), text = document.createElement('p');
        block.className = 'coverage-item' + (gap ? ' uncovered' : '');
        heading.textContent = day + ' · ' + label;
        text.textContent = count + ' / ' + needed + ' persone — ' + (gap ? 'Da assegnare: ' + gap : 'Copertura raggiunta');
        block.append(heading, text); results.append(block);
      }
    });
    const hours = assignments.flat().filter(value => value !== 'off').length * 6;
    status.textContent = `Fasce coperte: ${covered} su 6. Assegnazioni mancanti: ${missing}.`;
    document.querySelector('#schedule-total').textContent = `${hours} ore complessive assegnate nei tre giorni. È il totale della demo, non un conteggio presenze.`;
  }
  function reset() {
    assignments = initial.map(person => [...person]); target.value = 2; editor.replaceChildren();
    people.forEach((person, p) => {
      const fieldset = document.createElement('fieldset'), legend = document.createElement('legend'); legend.textContent = person + ' · dati sintetici'; fieldset.append(legend);
      days.forEach((day, d) => {
        const label = document.createElement('label'), select = document.createElement('select');
        select.id = `shift-${p}-${d}`; label.htmlFor = select.id; label.textContent = day;
        for (const [value, text] of [['off', 'Non assegnata'], ['morning', 'Mattina · 08–14'], ['afternoon', 'Pomeriggio · 14–20']]) {
          const option = document.createElement('option'); option.value = value; option.textContent = text; select.append(option);
        }
        select.value = assignments[p][d];
        select.addEventListener('change', () => { assignments[p][d] = select.value; update(); });
        fieldset.append(label, select);
      });
      editor.append(fieldset);
    });
    update();
  }
  target.addEventListener('input', update);
  document.querySelector('#schedule-reset').addEventListener('click', () => { reset(); status.textContent = 'Scenario ripristinato. ' + status.textContent; });
  reset();
})();
