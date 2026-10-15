const $ = (id) => document.getElementById(id);
let scope = null;
let sourceNotes = '';
let quoteDocument = '';
let timer = null;

const sample = `I run Mira's bakery and need a small website. Please build a home page with our story and opening hours, a menu page with up to 12 items, and a contact page with our address and phone number. The website must work on phones. I will supply the logo, copy, and product photos. We do not need online ordering or payments in this version. I might want a newsletter later, but haven't decided. I would like to launch next month. Can you send me an estimate?`;

async function request(path, data) {
  const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The request failed. Try again.');
  return result;
}

function showError(message) { $('error').textContent = message; $('error').hidden = false; }
function clearError() { $('error').hidden = true; $('error').textContent = ''; }
function invalidateQuote() { quoteDocument = ''; $('quote').hidden = true; }
function invalidateReview() { $('reviewed').checked = false; invalidateQuote(); }

function renderScope() {
  $('deliverables').replaceChildren();
  scope.deliverables.forEach((item, index) => {
    const row = document.createElement('div'); row.className = 'scope-row';
    const content = document.createElement('div');
    const task = document.createElement('input'); task.className = 'task'; task.value = item.task; task.maxLength = 240; task.required = true;
    task.setAttribute('aria-label', `Scope item ${index + 1}`);
    task.addEventListener('input', () => { item.task = task.value; invalidateReview(); });
    const source = document.createElement('blockquote'); source.className = 'source';
    const caption = document.createElement('span'); caption.textContent = 'CLIENT SAID / QUOTE FOUND IN NOTES';
    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'text-button remove';
    remove.textContent = 'Remove item'; remove.setAttribute('aria-label', `Remove scope item ${index + 1}`);
    remove.addEventListener('click', () => { scope.deliverables.splice(index, 1); invalidateReview(); renderScope(); });
    source.append(caption, document.createTextNode(item.source)); content.append(task, source, remove);
    const hoursWrap = document.createElement('div');
    const hours = document.createElement('input'); hours.className = 'hour-input'; hours.id = `hours-${index}`;
    hours.type = 'number'; hours.min = '0.01'; hours.max = '10000'; hours.step = '0.01'; hours.placeholder = '—';
    hours.value = item.hours || '';
    hours.setAttribute('aria-label', `Hours for scope item ${index + 1}`);
    hours.addEventListener('input', () => { item.hours = hours.value; invalidateQuote(); });
    const label = document.createElement('label'); label.className = 'hour-label'; label.htmlFor = hours.id; label.textContent = 'hours';
    hoursWrap.append(hours, label); row.append(content, hoursWrap); $('deliverables').append(row);
  });
  $('exclusions').replaceChildren();
  scope.exclusions.forEach((item, index) => {
    const block = document.createElement('div'); block.className = 'exclusion';
    const name = document.createElement('strong'); name.textContent = item.task;
    const source = document.createElement('blockquote'); source.className = 'source'; source.textContent = item.source;
    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'text-button remove';
    remove.textContent = 'Remove exclusion';
    remove.addEventListener('click', () => { scope.exclusions.splice(index, 1); invalidateReview(); renderScope(); });
    block.append(name, source, remove); $('exclusions').append(block);
  });
  if (!scope.exclusions.length) $('exclusions').textContent = 'No explicit exclusions were found. Ask your client what is outside the scope.';
  $('questions').value = scope.questions.join('\n');
  $('empty').hidden = true; $('results').hidden = false; $('draft-badge').textContent = 'DRAFT / REVIEW REQUIRED';
}

$('sample').addEventListener('click', () => {
  $('project').value = "Mira's bakery website"; $('notes').value = sample;
  $('notes').dispatchEvent(new Event('input')); $('notes').focus();
});

$('notes').addEventListener('input', () => {
  $('char-count').textContent = `${$('notes').value.length.toLocaleString()} / 6,000`;
  scope = null; sourceNotes = ''; invalidateReview(); $('results').hidden = true; $('empty').hidden = false;
  $('draft-badge').textContent = 'AWAITING BRIEF'; $('status').textContent = ''; clearError();
});
$('project').addEventListener('input', invalidateQuote);
$('rate').addEventListener('input', invalidateQuote);
$('currency').addEventListener('change', invalidateQuote);
$('reviewed').addEventListener('change', invalidateQuote);
$('questions').addEventListener('input', () => {
  if (scope) scope.questions = $('questions').value.split('\n').map((q) => q.trim()).filter(Boolean);
  invalidateReview();
});

$('brief-form').addEventListener('submit', async (event) => {
  event.preventDefault(); clearError(); invalidateReview();
  const notes = $('notes').value.trim();
  if (!notes) { showError('Add the client notes before drafting a scope.'); return; }
  $('extract').disabled = true; $('sample').disabled = true; $('notes').readOnly = true;
  $('results').hidden = true; $('empty').hidden = true; scope = null;
  const started = Date.now();
  const progress = () => { $('status').textContent = `Reading your notes with the local model… ${Math.floor((Date.now() - started) / 1000)}s. This can take a few minutes. Keep this tab open.`; };
  progress(); timer = setInterval(progress, 1000);
  try {
    const result = await request('/api/extract', { notes });
    scope = result.scope; sourceNotes = notes; renderScope();
    $('generation').textContent = `${result.model} / ${result.seconds}s`;
    $('status').textContent = `Draft ready. ${scope.deliverables.length} scope items with matching source quotes. Review their meaning before estimating.`;
  } catch (error) {
    showError(error.message === 'Failed to fetch' ? 'The local app connection was interrupted. Check that app.py is running and try again.' : error.message);
    $('status').textContent = ''; $('empty').hidden = false;
  } finally {
    clearInterval(timer); $('extract').disabled = false; $('sample').disabled = false; $('notes').readOnly = false;
  }
});

$('quote-form').addEventListener('submit', async (event) => {
  event.preventDefault(); clearError(); invalidateQuote();
  if (!scope) { showError('Draft the scope first.'); return; }
  const hours = scope.deliverables.map((_, index) => $(`hours-${index}`).value);
  if (hours.some((value) => !value || Number(value) <= 0)) { showError('Enter your estimated hours for every scope item.'); return; }
  $('calculate').disabled = true;
  try {
    const result = await request('/api/quote', { project: $('project').value, notes: sourceNotes, scope,
      hours, rate: $('rate').value, currency: $('currency').value, reviewed: $('reviewed').checked });
    quoteDocument = result.document; $('total').textContent = `${result.currency} ${Number(result.total).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    $('quote-preview').textContent = quoteDocument; $('quote').hidden = false; $('status').textContent = 'Draft estimate calculated from your hours and rate. Ready to review and download.';
  } catch (error) { showError(error.message); }
  finally { $('calculate').disabled = false; }
});

$('download').addEventListener('click', () => {
  if (!quoteDocument) return;
  const url = URL.createObjectURL(new Blob([quoteDocument], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a'); link.href = url; link.download = 'brief-ledger-draft.txt'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

fetch('/api/status').then((r) => r.json()).then((data) => {
  $('runtime').textContent = data.ready ? `${data.model} ready` : 'Start Ollama to draft';
}).catch(() => { $('runtime').textContent = 'Local app unavailable'; });
