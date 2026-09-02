const LISTENERS = new Set();
let wsCorpus = null;
let wsStats = null;
let reconnecting = false;
let started = false;
const RETRY_MS = 3000;

function baseURL() {
    return (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host;
}

function emit(msg) {
    LISTENERS.forEach(fn => {
        try {
            fn(msg);
        } catch {
        }
    });
}

function attach(ws, name) {
    ws.onopen = () => emit({event: 'ws.reconnected', channel: name});
    ws.onmessage = ev => {
        try {
            const data = JSON.parse(ev.data);
            emit(data);
        } catch {
        }
    };
    ws.onclose = () => scheduleReconnect();
    ws.onerror = () => {
        try {
            ws.close();
        } catch {
        }
    };
}

function connect() {
    if (reconnecting) return;
    reconnecting = true;
    try {
        wsCorpus && wsCorpus.close();
        wsStats && wsStats.close();
    } catch {
    }
    const base = baseURL();
    wsCorpus = new WebSocket(`${base}/ws/corpus/`);
    wsStats = new WebSocket(`${base}/ws/stats/`);
    attach(wsCorpus, 'corpus');
    attach(wsStats, 'stats');
    setTimeout(() => {
        reconnecting = false;
    }, 250);
}

function scheduleReconnect() {
    if (reconnecting) return;
    setTimeout(connect, RETRY_MS);
}

export function initWS() {
    if (started) return;
    started = true;
    connect();
}

export function onWSEvent(cb) {
    LISTENERS.add(cb);
    return () => LISTENERS.delete(cb);
}
