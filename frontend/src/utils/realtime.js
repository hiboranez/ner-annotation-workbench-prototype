// javascript
import {useAuthStore} from '@/stores/authStore';

let subscribers = [];
let sockets = [];
let inited = false;

function connect(path, onmsg) {
    const auth = useAuthStore();
    auth.load();
    const token = auth.accessToken ? `?token=${encodeURIComponent(auth.accessToken)}` : '';
    const url = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws${path}${token}`;
    let ws = null;
    let closed = false;
    let retry = 0;

    const emit = (payload) => {
        try {
            subscribers.forEach(fn => fn(payload));
        } catch {
        }
    };

    const open = () => {
        ws = new WebSocket(url);
        ws.onopen = () => {
            retry = 0;
        };
        ws.onmessage = (ev) => {
            try {
                const data = JSON.parse(ev.data);
                const payload = data.payload || data; // 兼容直接发送 payload
                onmsg && onmsg(payload);
                emit(payload);
            } catch {
            }
        };
        ws.onclose = () => {
            if (closed) return;
            const wait = Math.min(5000, 300 + retry * 500);
            retry++;
            setTimeout(() => {
                open();
                if (retry === 1) emit({event: 'ws.reconnected'});
            }, wait);
        };
    };
    open();

    return {
        close() {
            try {
                closed = true;
                ws && ws.close();
            } catch {
            }
        }
    };
}

export function initWS() {
    if (inited) return;
    inited = true;
    sockets = [
        connect('/corpus/', null),
        connect('/stats/', null),
    ];
}

export function onWSEvent(cb) {
    subscribers.push(cb);
    return () => {
        subscribers = subscribers.filter(f => f !== cb);
    };
}
