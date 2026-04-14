const EPSILON = "\u03b5";

function computeEpsilonClosure(nfa, states) {
    let closure = new Set(states);
    let stack = [...states];
    
    while (stack.length > 0) {
        let s = stack.pop();
        let transitions = nfa[`${s},${EPSILON}`] || [];
        for (let ns of transitions) {
            if (!closure.has(ns)) {
                closure.add(ns);
                stack.push(ns);
            }
        }
    }
    return Array.from(closure).sort();
}

function parseInput(text, extraAlphaStr = "") {
    const lines = text.trim().split('\n').map(l => l.trim()).filter(l => l);
    if (lines.length === 0) return { error: "No transitions provided." };

    const nfa = {};
    const statesSet = new Set();
    const alphaSet = new Set();
    const errors = [];

    lines.forEach((line, i) => {
        let sep = "=";
        if (line.includes("->")) sep = "->";
        else if (!line.includes("=")) {
            errors.push(`Line ${i + 1}: Invalid format. Use state,symbol=next1,next2`);
            return;
        }

        const [left, right] = line.split(sep).map(p => p.trim());
        if (!left.includes(",")) {
            errors.push(`Line ${i + 1}: Missing comma in '${left}'`);
            return;
        }

        const commaIndex = left.lastIndexOf(",");
        const state = left.substring(0, commaIndex).trim();
        const sym = left.substring(commaIndex + 1).trim();

        if (!state || !sym || !right) {
            errors.push(`Line ${i + 1}: Incomplete transition`);
            return;
        }

        const dests = right.split(",").map(d => d.trim()).filter(d => d);
        if (dests.length === 0) {
            errors.push(`Line ${i + 1}: No destination states`);
            return;
        }

        statesSet.add(state);
        if (sym !== EPSILON) alphaSet.add(sym);
        dests.forEach(d => statesSet.add(d));

        const key = `${state},${sym}`;
        if (!nfa[key]) nfa[key] = [];
        dests.forEach(d => {
            if (!nfa[key].includes(d)) nfa[key].push(d);
        });
    });

    if (errors.length > 0) return { error: errors.join("\n") };

    if (extraAlphaStr.trim()) {
        extraAlphaStr.split(",").forEach(a => {
            const sym = a.trim();
            if (sym && sym !== EPSILON) alphaSet.add(sym);
        });
    }

    const firstLine = lines[0];
    const sep = firstLine.includes("->") ? "->" : "=";
    const initial = firstLine.split(sep)[0].split(",")[0].trim();

    return {
        nfa,
        states: Array.from(statesSet).sort(),
        alphabets: Array.from(alphaSet).sort(),
        initial,
        hasEpsilon: Object.keys(nfa).some(k => k.split(',').pop() === EPSILON)
    };
}

function frozensetToStr(states) {
    if (!states || states.length === 0) return "qd";
    return states.sort().join(",");
}

function runSubsetConstruction(parsed) {
    const { nfa, alphabets, initial, finalStates = [] } = parsed;
    const deadStateLabel = "qd";

    const initialClosure = computeEpsilonClosure(nfa, [initial]);
    const initialStr = frozensetToStr(initialClosure);

    const queue = [initialClosure];
    const visited = new Map();
    const dfaTransitions = {};
    const order = [];
    const discovered = new Set([initialStr]);
    const stepsLog = [];
    let hasDead = false;

    while (queue.length > 0) {
        const currentFrozen = queue.shift();
        const currentStr = frozensetToStr(currentFrozen);

        if (visited.has(currentStr)) continue;
        visited.set(currentStr, currentFrozen);
        order.push(currentStr);

        const stepInfo = {
            state: currentStr,
            epsilonClosure: currentFrozen,
            transitions: []
        };

        for (const sym of alphabets) {
            let reachable = new Set();
            for (const s of currentFrozen) {
                const nsList = nfa[`${s},${sym}`] || [];
                nsList.forEach(ns => reachable.add(ns));
            }

            let nextStr;
            let reachableAfterClosure = [];

            if (reachable.size === 0) {
                nextStr = deadStateLabel;
                hasDead = true;
                stepInfo.transitions.push({
                    sym,
                    nxt: nextStr,
                    isNew: false,
                    isDead: true,
                    isFirstDead: !discovered.has(deadStateLabel),
                    fromDead: false,
                    reachableAfterClosure: []
                });
                if (!discovered.has(deadStateLabel)) discovered.add(deadStateLabel);
            } else {
                reachableAfterClosure = computeEpsilonClosure(nfa, Array.from(reachable));
                nextStr = frozensetToStr(reachableAfterClosure);

                const isNew = !discovered.has(nextStr);
                if (isNew) {
                    discovered.add(nextStr);
                    queue.push(reachableAfterClosure);
                }

                stepInfo.transitions.push({
                    sym,
                    nxt: nextStr,
                    isNew,
                    isDead: false,
                    fromDead: false,
                    reachableAfterClosure
                });
            }
            dfaTransitions[`${currentStr},${sym}`] = nextStr;
        }
        stepsLog.push(stepInfo);
    }

    if (hasDead) {
        const deadStep = {
            state: deadStateLabel,
            epsilonClosure: [],
            transitions: []
        };
        for (const sym of alphabets) {
            dfaTransitions[`${deadStateLabel},${sym}`] = deadStateLabel;
            deadStep.transitions.push({
                sym,
                nxt: deadStateLabel,
                isNew: false,
                isDead: true,
                fromDead: true,
                reachableAfterClosure: []
            });
        }
        stepsLog.push(deadStep);
        order.push(deadStateLabel);
    }

    const dfaFinal = order.filter(sStr => {
        if (sStr === "qd") return false;
        const members = sStr.split(",");
        return members.some(m => finalStates.includes(m));
    });

    return {
        order,
        dfaTransitions,
        dfaFinal,
        hasDead,
        stepsLog
    };
}
