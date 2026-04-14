document.addEventListener('DOMContentLoaded', () => {

    let _uid = 0;
    const uid = () => _uid++;

    const EPSILON = "\u03b5";

    let parsed  = null;
    let cData   = null;
    let selFinals = new Set();

    let liveModeActive = false;

    let nfaTimer  = null;
    let dfaTimer  = null;
    let navTimer  = null;

    let nfaRunning  = false;
    let dfaRunning  = false;

    let nfaCardsShown = false;
    let dfaCardsShown = false;

    let curNfaIdx = 0;
    let curDfaIdx = 0;

    let nfaNet    = null;
    let constrNet    = null;
    let finalNet  = null;

    const $  = id => document.getElementById(id);
    const navPills = document.querySelectorAll('.nav-pill');
    const sections = document.querySelectorAll('.sec');

    const transInput  = $('trans-input');
    const extraAlpha  = $('extra-alpha');
    const finalChips  = $('final-chips');
    const parseBtn    = $('parse-btn');
    const convertBtn  = $('convert-btn');
    const inputErr    = $('input-err');
    const copyEpsBtn  = $('copy-eps-btn');
    const copyConfirm = $('copy-confirm');

    const nfaStepPill   = $('nfa-step-pill');
    const nfaAnimMsg    = $('nfa-anim-msg');
    const nfaLoopBadge  = $('nfa-loop-badge');
    const nfaGraph      = $('nfa-graph');
    const nfaStepLog    = $('nfa-step-log');
    const nfaTable      = $('nfa-table');

    const nfaStepsList  = $('nfa-steps-list');

    const stepPill    = $('step-pill');
    const animMsg     = $('anim-msg');
    const loopBadge   = $('loop-badge');
    const constrGraph = $('construction-graph');
    const stepLog     = $('step-log');

    const dfaSummary  = $('dfa-summary');
    const dfaGraph    = $('dfa-graph');
    const dfaTable    = $('dfa-table');

    const stepsList   = $('steps-list');

    navPills.forEach(p => p.addEventListener('click', () => {
        if (p.classList.contains('locked')) return;
        switchSec(p.dataset.sec);
    }));

    function switchSec(id) {
        navPills.forEach(p => p.classList.toggle('active', p.dataset.sec === id));
        sections.forEach(s => s.classList.toggle('active', s.id === `${id}-section`));

        if (!cData) return;

        if (id === 'nfa' && !nfaRunning) {
            startNFAAnimation();
        }
        if (id === 'construction' && !dfaRunning) {
            startDFAAnimation();
        }
        if (id === 'nfa-steps') {
            if (!nfaCardsShown) nfaCardsShown = true;
            revealCards(nfaStepsList);
        }
        if (id === 'step-diagrams') {
            if (!dfaCardsShown) dfaCardsShown = true;
            revealCards(stepsList);
        }

        setTimeout(() => {
            if (id === 'nfa' && nfaNet) nfaNet.fit();
            if (id === 'construction' && constrNet) constrNet.fit();
            if (id === 'final' && finalNet) finalNet.fit();
        }, 50);
    }

    function revealCards(container) {
        const cards = container.querySelectorAll('.step-card');
        if (!cards.length) return;

        const isNfa = container.id === 'nfa-steps-list';
        const nav = $(isNfa ? 'nfa-nav' : 'dfa-nav');
        if (nav) {
            nav.style.display = 'flex';
            if (isNfa) curNfaIdx = 0; else curDfaIdx = 0;
            showStep(container, 0);
        }
    }

    function showStep(container, idx) {
        const cards = container.querySelectorAll('.step-card');
        const isNfa = container.id === 'nfa-steps-list';
        const nav   = $(isNfa ? 'nfa-nav' : 'dfa-nav');

        cards.forEach((c, i) => {
            c.classList.toggle('active-step', i === idx);
        });

        if (nav) {
            const counter = nav.querySelector('.nav-counter');
            if (counter) counter.textContent = `Step ${idx + 1} of ${cards.length}`;
            
            const prevBtn = nav.querySelector('.nav-prev');
            const nextBtn = nav.querySelector('.nav-next');
            if (prevBtn) prevBtn.disabled = (idx === 0);
            if (nextBtn) nextBtn.disabled = (idx === cards.length - 1 || cards.length === 0);
        }
    }

    document.querySelectorAll('.nav-prev').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const container = $(targetId);
            const isNfa = targetId === 'nfa-steps-list';
            if (isNfa) { if (curNfaIdx > 0) showStep(container, --curNfaIdx); }
            else       { if (curDfaIdx > 0) showStep(container, --curDfaIdx); }
        });
    });
    document.querySelectorAll('.nav-next').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const container = $(targetId);
            const isNfa = targetId === 'nfa-steps-list';
            const cards = container.querySelectorAll('.step-card');
            if (isNfa) { if (curNfaIdx < cards.length - 1) showStep(container, ++curNfaIdx); }
            else       { if (curDfaIdx < cards.length - 1) showStep(container, ++curDfaIdx); }
        });
    });

    copyEpsBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(EPSILON).then(() => {
            copyConfirm.textContent = '✓ copied!';
            setTimeout(() => { copyConfirm.textContent = ''; }, 1800);
        }).catch(() => { copyConfirm.textContent = '(select & copy manually)'; });
    });

    parseBtn.addEventListener('click', doParse);
    
    let liveTimer = null;

    transInput.addEventListener('input', () => {
        const r = parseInput(transInput.value, extraAlpha.value);
        if (!r.error && r.states.length) {
            parsed = r; 
            
            const newStates = new Set(r.states);
            const toKeep = Array.from(selFinals).filter(s => newStates.has(s));
            selFinals = new Set(toKeep);
            
            buildChips(r.states); 
            convertBtn.disabled = false;

            updateBasicNfaPreview();

            if (liveModeActive) {
                clearTimeout(liveTimer);
                liveTimer = setTimeout(() => {
                    updateFullDynamicResults();
                }, 150);
            }
        }
    });

    function updateBasicNfaPreview() {
        if (!parsed) return;
        const tempFinals = Array.from(selFinals);
        const { nfa, states } = parsed;
        const edges = [];
        for (const [key, dests] of Object.entries(nfa)) {
            const ci = key.lastIndexOf(',');
            const from = key.substring(0, ci), sym = key.substring(ci + 1);
            dests.forEach(to => edges.push([from, to, sym]));
        }
        const data = buildVis(states, edges, parsed.initial, tempFinals);
        if (!nfaNet) nfaNet = new vis.Network(nfaGraph, data, GOPTS);
        else nfaNet.setData(data);
        renderNFATable(parsed, tempFinals);
        unlockAllTabs();
    }

    extraAlpha.addEventListener('input', () => {
        if (parsed) {
            const r = parseInput(transInput.value, extraAlpha.value);
            if (!r.error) {
                parsed = r;
                updateBasicNfaPreview();
                if (liveModeActive) {
                    clearTimeout(liveTimer);
                    liveTimer = setTimeout(updateFullDynamicResults, 150);
                }
            }
        }
    });

    function unlockAllTabs() {
        navPills.forEach(p => p.classList.remove('locked'));
    }

    function updateFullDynamicResults() {
        if (!parsed) return;
        
        clearTimeout(nfaTimer); 
        clearTimeout(dfaTimer); 
        clearTimeout(navTimer);
        nfaRunning = false; 
        dfaRunning = false;
        nfaLoopBadge.style.display = 'none';
        loopBadge.style.display = 'none';

        const tempFinals = Array.from(selFinals);
        const { nfa, states } = parsed;
        const edges = [];
        for (const [key, dests] of Object.entries(nfa)) {
            const ci = key.lastIndexOf(',');
            const from = key.substring(0, ci), sym = key.substring(ci + 1);
            dests.forEach(to => edges.push([from, to, sym]));
        }
        
        const data = buildVis(states, edges, parsed.initial, tempFinals);
        if (!nfaNet) nfaNet = new vis.Network(nfaGraph, data, GOPTS);
        else nfaNet.setData(data);
        renderNFATable(parsed, tempFinals);

        const currentParsed = { ...parsed, finalStates: tempFinals };
        cData = runSubsetConstruction(currentParsed);

        renderFinalDFA();
        buildNFAStepCards(tempFinals);
        buildDFAStepCards();

        const dfaEdges = [];
        for (const [k, to] of Object.entries(cData.dfaTransitions)) {
            const ci = k.lastIndexOf(',');
            dfaEdges.push([k.substring(0, ci), to, k.substring(ci + 1)]);
        }
        const constructionData = buildVis(cData.order, dfaEdges, cData.order[0], cData.dfaFinal);
        if (constrNet) constrNet.setData(constructionData);

        nfaCardsShown = false;
        dfaCardsShown = false;
        $('nfa-nav').style.display = 'none';
        $('dfa-nav').style.display = 'none';

        const activePill = document.querySelector('.nav-pill.active');
        if (activePill) {
            const id = activePill.dataset.sec;
            if (id === 'nfa-steps')     { nfaCardsShown = true; revealCards(nfaStepsList); }
            if (id === 'step-diagrams') { dfaCardsShown = true; revealCards(stepsList); }
        }

        nfaStepPill.textContent = 'Live Sync';
        nfaAnimMsg.textContent = 'NFA updated live.';
        stepPill.textContent = 'Live Sync';
        animMsg.textContent = 'DFA construction updated live.';
    }

    function doParse() {
        const r = parseInput(transInput.value, extraAlpha.value);
        if (r.error) { showErr(r.error); return; }
        hideErr(); 
        parsed = r; 
        selFinals.clear();
        buildChips(r.states); 
        convertBtn.disabled = false;
    }

    function buildChips(states) {
        finalChips.innerHTML = '';
        states.forEach(s => {
            const c = document.createElement('div');
            c.className = 'chip'; c.textContent = s; c.title = 'Click to toggle as final';
            if (selFinals.has(s)) c.classList.add('selected');
            
            c.addEventListener('click', () => {
                if (selFinals.has(s)) { selFinals.delete(s); c.classList.remove('selected'); }
                else                  { selFinals.add(s);    c.classList.add('selected');    }
                updateFullDynamicResults();
            });
            finalChips.appendChild(c);
        });
    }

    convertBtn.addEventListener('click', () => {
        const r = parseInput(transInput.value, extraAlpha.value);
        if (r.error) { showErr(r.error); return; }
        hideErr();
        parsed = r; 
        parsed.finalStates = Array.from(selFinals);

        clearTimeout(nfaTimer); clearTimeout(dfaTimer); clearTimeout(navTimer);
        nfaRunning = false; dfaRunning = false;
        nfaCardsShown = false; dfaCardsShown = false;
        nfaNet = null; constrNet = null;

        navPills.forEach(p => p.classList.remove('locked'));
        $('nfa-nav').style.display = 'none';
        $('dfa-nav').style.display = 'none';

        cData = runSubsetConstruction(parsed);

        liveModeActive = true;
        const liveIndicator = $('live-indicator');
        if (liveIndicator) liveIndicator.style.display = 'flex';

        renderNFATable();
        buildNFAStepCards();
        renderFinalDFA();
        buildDFAStepCards();

        switchSec('nfa');
        startNFAAnimation();

        navTimer = setTimeout(() => {
            switchSec('construction');
            startDFAAnimation();
        }, 2000);
    });

    function showErr(m) { inputErr.textContent = m; inputErr.style.display = 'block'; }
    function hideErr()  { inputErr.style.display = 'none'; }

    const GOPTS = {
        interaction: { hover: true, zoomView: true, dragView: true },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 0.9 } },
            font:  { face: 'Nunito', size: 13, strokeWidth: 2, strokeColor: '#fff', color: '#4a148c' },
            width: 2, color: { color: '#8e24aa', highlight: '#e91e63', hover: '#c2185b' }
        },
        nodes: {
            shape: 'ellipse', font: { face: 'Nunito', size: 13, bold: true, color: '#2d1f3d' },
            borderWidth: 2.5, size: 32,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.12)', size: 8, x: 2, y: 2 }
        },
        physics: {
            enabled: true, stabilization: { iterations: 240, updateInterval: 28 },
            barnesHut: { gravitationalConstant: -4200, springLength: 145, springConstant: 0.04 }
        }
    };

    function buildVis(states, edges, initial, finals, hiliteNode = null, hiliteEdges = []) {
        const nodes = states.map(s => {
            const isF = finals && finals.includes(s);
            const isI = initial && s === initial;
            const isH = s === hiliteNode;
            const isD = s === 'qd';
            let bg, bd;
            if      (isD)         { bg='#e0e0e0'; bd='#9e9e9e'; }
            else if (isF)         { bg='#f48fb1'; bd='#880e4f'; }
            else if (isI)         { bg='#80cbc4'; bd='#00695c'; }
            else                  { bg='#ce93d8'; bd='#7b1fa2'; }
            if (isH && !isD)      { bd='#f57f17'; }
            return {
                id: s, label: nodeLbl(s),
                color: { background: bg, border: bd, highlight: { background: bg, border: '#e65100' } },
                borderWidth: isH ? 5 : (isF ? 4 : 2.5), size: isH ? 40 : 32, title: s
            };
        });

        if (initial && states.includes(initial))
            nodes.push({ id:'__S__', label:'', size:1, shape:'dot', color:{ background:'transparent', border:'transparent' } });

        const eMap = new Map();
        edges.forEach(([from, to, lbl]) => {
            const k = `${from}||${to}`;
            if (!eMap.has(k)) eMap.set(k, { from, to, labels:[], hi:false });
            eMap.get(k).labels.push(lbl);
        });
        hiliteEdges.forEach(([hf, ht]) => {
            const k = `${hf}||${ht}`;
            if (eMap.has(k)) eMap.get(k).hi = true;
        });

        const edgeArr = [];
        eMap.forEach(({ from, to, labels, hi }) => {
            const self = from === to;
            edgeArr.push({
                from, to, label: labels.sort().join(', '),
                width: hi ? 4 : 2, color: hi ? '#e91e63' : '#8e24aa',
                smooth: { type: self ? 'curvedCCW' : 'curvedCW', roundness: self ? 0.42 : 0.22 }
            });
        });
        if (initial && states.includes(initial))
            edgeArr.push({ from:'__S__', to:initial, label:'start', color:{ color:'#00695c' },
                           width:2, smooth:{ type:'straight' }, font:{ color:'#00695c', size:11, strokeWidth:0 } });

        return { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edgeArr) };
    }

    function nodeLbl(s) {
        if (s === 'qd' || !s.includes(',')) return s;
        return '[' + s.split(',').map(p => p.trim()).join(',\n') + ']';
    }

    function renderNFATable(dataObj = parsed, finals = null) {
        const { states, alphabets, initial, finalStates, nfa, hasEpsilon } = dataObj;
        const activeFinals = finals || finalStates;
        
        let h = `<table><thead><tr><th>State</th>`;
        if (hasEpsilon) h += `<th>${EPSILON}</th>`;
        alphabets.forEach(a => h += `<th>${a}</th>`);
        h += `</tr></thead><tbody>`;
        states.forEach(s => {
            let lbl = s;
            if (s === initial)          lbl = '\u2192 ' + lbl;
            if (activeFinals.includes(s)) lbl += ' \u2605';
            h += `<tr><td>${lbl}</td>`;
            if (hasEpsilon) { const t = nfa[`${s},${EPSILON}`]||[]; h += `<td>${t.length?t.join(', '):'∅'}</td>`; }
            alphabets.forEach(a => { const t = nfa[`${s},${a}`]||[]; h += `<td>${t.length?t.join(', '):'∅'}</td>`; });
            h += `</tr>`;
        });
        h += `</tbody></table>`;
        nfaTable.innerHTML = h;
    }

    function startNFAAnimation() {
        if (nfaRunning) return;
        nfaRunning = true;
        clearTimeout(nfaTimer);
        nfaStepLog.innerHTML = ''; nfaGraph.innerHTML = ''; nfaNet = null;
        nfaLoopBadge.style.display = 'none';

        const { states, nfa } = parsed;
        const events = [];
        states.forEach(state => {
            events.push({ type: 'STATE', state });
            for (const [key, dests] of Object.entries(nfa)) {
                const ci = key.lastIndexOf(',');
                const from = key.substring(0, ci), sym = key.substring(ci + 1);
                if (from === state) dests.forEach(to => events.push({ type: 'EDGE', from, to, sym }));
            }
        });

        const revS = [], revE = [];
        let ei = 0;
        const tick = () => {
            if (ei >= events.length) {
                redrawNFA([...revS], [...revE], null, []);
                nfaStepPill.textContent = 'Complete \u2713';
                nfaAnimMsg.textContent = 'Replaying in 3 s\u2026';
                nfaLoopBadge.style.display = '';
                nfaTimer = setTimeout(() => {
                    revS.length = 0; revE.length = 0; ei = 0; nfaNet = null;
                    nfaStepLog.innerHTML = ''; nfaLoopBadge.style.display = 'none';
                    tick();
                }, 3000);
                return;
            }
            const ev = events[ei++];
            if (ev.type === 'STATE') {
                if (!revS.includes(ev.state)) revS.push(ev.state);
                nfaStepPill.textContent = `Step ${ei}/${events.length}`;
                nfaAnimMsg.textContent = `Showing state: [${ev.state}]`;
                nfaLog(`\u25b6 State [${ev.state}]`, 'log-info');
                redrawNFA([...revS], [...revE], ev.state, []);
                nfaTimer = setTimeout(tick, 1100);
            } else {
                if (!revS.includes(ev.to)) revS.push(ev.to);
                revE.push([ev.from, ev.to, ev.sym]);
                nfaStepPill.textContent = `Step ${ei}/${events.length}`;
                nfaAnimMsg.textContent = `Transition on '${ev.sym}': [${ev.from}] \u2192 [${ev.to}]`;
                nfaLog(`  on '${ev.sym}': [${ev.from}] \u2192 [${ev.to}]`, 'log-info');
                redrawNFA([...revS], [...revE], ev.from, [[ev.from, ev.to]]);
                nfaTimer = setTimeout(tick, 750);
            }
        };
        tick();
    }

    function redrawNFA(s, e, hN, hE) {
        const data = buildVis(s, e, parsed.initial, Array.from(selFinals), hN, hE);
        if (!nfaNet) { nfaNet = new vis.Network(nfaGraph, data, GOPTS); nfaNet.once('stabilizationIterationsDone',()=>nfaNet.fit()); }
        else { nfaNet.setData(data); nfaNet.once('stabilizationIterationsDone',()=>nfaNet.fit()); }
    }

    function nfaLog(m, c) {
        const d = document.createElement('div'); d.className=`log-item ${c}`; d.textContent=m;
        nfaStepLog.insertBefore(d, nfaStepLog.firstChild);
    }

    function startDFAAnimation() {
        if (dfaRunning) return;
        dfaRunning = true;
        clearTimeout(dfaTimer);
        stepLog.innerHTML = ''; constrGraph.innerHTML = ''; constrNet = null;
        loopBadge.style.display = 'none';

        const { stepsLog, order, dfaFinal } = cData;
        const dfaStart = order[0];
        const events = [];
        stepsLog.forEach(step => {
            events.push({ type:'STATE', state:step.state });
            step.transitions.forEach(t => events.push({ type:'EDGE', from:step.state, to:t.nxt, sym:t.sym, meta:t }));
        });

        const revS = [], revE = [];
        let ei = 0;
        const tick = () => {
            if (ei >= events.length) {
                redrawDFA(dfaStart, dfaFinal, [...revS], [...revE], null, []);
                stepPill.textContent = 'Complete \u2713';
                animMsg.textContent = 'Replaying in 3 s\u2026';
                loopBadge.style.display = '';
                dfaTimer = setTimeout(() => {
                    revS.length = 0; revE.length = 0; ei = 0; constrNet = null;
                    stepLog.innerHTML = ''; loopBadge.style.display = 'none';
                    tick();
                }, 3000);
                return;
            }
            const ev = events[ei++];
            if (ev.type === 'STATE') {
                if (!revS.includes(ev.state)) revS.push(ev.state);
                stepPill.textContent = `Step ${ei}/${events.length}`;
                animMsg.textContent = `Processing DFA state: [${ev.state}]`;
                dfaLog(`\u25b6 State [${ev.state}]`, 'log-info');
                redrawDFA(dfaStart, dfaFinal, [...revS], [...revE], ev.state, []);
                dfaTimer = setTimeout(tick, 1100);
            } else {
                if (!revS.includes(ev.to)) revS.push(ev.to);
                revE.push([ev.from, ev.to, ev.sym]);
                stepPill.textContent = `Step ${ei}/${events.length}`;
                let cls = ev.meta.isNew ? 'log-new' : ev.meta.isDead ? 'log-dead' : 'log-known';
                let txt = `  on '${ev.sym}': [${ev.from}] \u2192 [${ev.to}] ${ev.meta.isNew?'(new)':''}`;
                animMsg.textContent = txt;
                dfaLog(txt, cls);
                redrawDFA(dfaStart, dfaFinal, [...revS], [...revE], ev.from, [[ev.from, ev.to]]);
                dfaTimer = setTimeout(tick, 750);
            }
        };
        tick();
    }

    function redrawDFA(start, fin, s, e, hN, hE) {
        const data = buildVis(s, e, start, fin, hN, hE);
        if (!constrNet) { constrNet = new vis.Network(constrGraph, data, GOPTS); constrNet.once('stabilizationIterationsDone',()=>constrNet.fit()); }
        else { constrNet.setData(data); constrNet.once('stabilizationIterationsDone',()=>constrNet.fit()); }
    }

    function dfaLog(m, c) {
        const d = document.createElement('div'); d.className=`log-item ${c}`; d.textContent=m;
        stepLog.insertBefore(d, stepLog.firstChild);
    }

    function renderFinalDFA() {
        const { order, dfaFinal, dfaTransitions } = cData;
        const { alphabets } = parsed;
        const dfaStart = order[0];

        dfaSummary.innerHTML = `
            <div class="sum-item"><strong>Start State</strong><span class="badge b-start">${dfaStart}</span></div>
            <div class="sum-item"><strong>Final States</strong>${
                dfaFinal.length ? dfaFinal.map(s=>`<span class="badge b-final">${s}</span>`).join('') : '<i>None</i>'
            }</div>`;

        let h = `<table><thead><tr><th>State</th>${alphabets.map(a=>`<th>${a}</th>`).join('')}</tr></thead><tbody>`;
        order.forEach(s => {
            let lbl = s; if (s===dfaStart) lbl='\u2192 '+lbl; if (dfaFinal.includes(s)) lbl+=' \u2605';
            h += `<tr><td>${lbl}</td>${alphabets.map(a=>`<td>${dfaTransitions[`${s},${a}`]||'qd'}</td>`).join('')}</tr>`;
        });
        h += `</tbody></table>`;
        dfaTable.innerHTML = h;

        const edges = [];
        for (const [k, to] of Object.entries(dfaTransitions)) {
            const ci=k.lastIndexOf(','); edges.push([k.substring(0,ci), to, k.substring(ci+1)]);
        }
        finalNet = new vis.Network(dfaGraph, buildVis(order, edges, dfaStart, dfaFinal), GOPTS);
    }

    function buildNFAStepCards(liveFinals) {
        nfaStepsList.innerHTML = '';
        const { states, nfa, finalStates } = parsed;
        const activeFinals = liveFinals !== undefined ? liveFinals : finalStates;
        let counter = 1;
        states.forEach(state => {
            for (const [key, dests] of Object.entries(nfa)) {
                const ci = key.lastIndexOf(',');
                const from = key.substring(0, ci), sym = key.substring(ci + 1);
                if (from !== state) continue;
                dests.forEach(to => {
                    nfaStepsList.appendChild(makeStepCard(counter++, from, to, sym, activeFinals.includes(from), activeFinals.includes(to), from==='qd', to==='qd', false, false, `nfa-${counter}`, activeFinals));
                });
            }
        });
    }

    function buildDFAStepCards() {
        stepsList.innerHTML = '';
        const { stepsLog, dfaFinal } = cData;
        let counter = 1;
        stepsLog.forEach((step, si) => {
            step.transitions.forEach((t, ti) => {
                stepsList.appendChild(makeStepCard(counter++, step.state, t.nxt, t.sym, dfaFinal.includes(step.state), dfaFinal.includes(t.nxt), step.state==='qd', t.nxt==='qd', t.isNew, t.isDead, `dfa-${si}-${ti}`, dfaFinal));
            });
        });
    }

    function makeStepCard(counter, from, to, sym, isFF, isFT, isDF, isDT, isNew, isDead, prefix, finals) {
        const card = document.createElement('div'); card.className = 'step-card';
        let tag = isNew ? '<span class="tag-new">NEW</span>' : isDead ? '<span class="tag-dead">DEAD</span>' : '';
        const sId = `${prefix}-s`, mId = `${prefix}-m`, dId = `${prefix}-d`;
        card.innerHTML = `
            <div class="step-tag">Step ${counter}</div>
            <div class="step-desc">From <b>[${from}]</b> on '${sym}' \u2192 <b>[${to}]</b> ${tag}</div>
            <div class="diag-panels">
                <div class="diag-panel"><div class="diag-svg-wrap" id="${sId}"></div></div>
                <div class="diag-panel"><div class="diag-svg-wrap" id="${mId}"></div></div>
                <div class="diag-panel"><div class="diag-svg-wrap" id="${dId}"></div></div>
            </div>`;
        requestAnimationFrame(() => {
            drawSingleState(sId, from, isFF, isDF, true);
            drawTransition(mId, from, to, sym, finals);
            drawSingleState(dId, to, isFT, isDT, false);
        });
        return card;
    }

    function drawSingleState(elId, label, isFinal, isDead, isHi) {
        const el = $(elId); if (!el) return;
        const { fill, stroke } = nodeClr(label, isFinal, isDead, isHi);
        const parts = splitLabel(label);
        const fs = parts.length > 3 ? 9 : 12;
        const W=200, H=170, cx=W/2, cy=H/2, rx=52, ry=34;
        let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="100%">`;
        if (isFinal) s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx+8}" ry="${ry+8}" fill="none" stroke="${stroke}" stroke-width="2"/>`;
        s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${fill}" stroke="${stroke}" stroke-width="3"/>`;
        parts.forEach((p,i) => s += `<text x="${cx}" y="${cy+(i-(parts.length-1)/2)*14}" text-anchor="middle" dominant-baseline="central" font-family="Nunito" font-size="${fs}" font-weight="bold" fill="#2d1f3d">${p}</text>`);
        el.innerHTML = s + '</svg>';
    }

    function drawTransition(elId, from, to, sym, finals) {
        const el = $(elId); if (!el) return;
        const mId = `arr-${uid()}`;
        const W=330, H=165, cx1=60, cx2=270, cy=H/2;
        let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="100%">
            <defs>
                <marker id="${mId}" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="#e91e63" />
                </marker>
            </defs>`;
        s += `<path d="M${cx1+40},${cy} Q${W/2},${cy-40} ${cx2-40},${cy}" fill="none" stroke="#e91e63" stroke-width="3" marker-end="url(#${mId})"/>`;
        s += `<text x="${W/2}" y="${cy-50}" text-anchor="middle" font-family="Nunito" font-size="14" font-weight="bold" fill="#e91e63">${sym}</text>`;
        el.innerHTML = s + '</svg>';
    }

    function nodeClr(l, f, d, h) {
        if (d) return { fill:'#e0e0e0', stroke:'#9e9e9e' };
        if (h) return { fill:'#ffd54f', stroke:'#f57f17' };
        if (f) return { fill:'#f48fb1', stroke:'#880e4f' };
        return { fill:'#ce93d8', stroke:'#7b1fa2' };
    }
    function splitLabel(l) { return l.split(',').map(s=>s.trim()).filter(Boolean); }

    transInput.value = `q0,a=q0,q1\nq0,b=q0\nq1,${EPSILON}=q2\nq2,a=q2`;
    doParse();
});
