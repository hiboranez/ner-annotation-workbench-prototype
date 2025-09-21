import {defineStore} from 'pinia';
import {initWS, onWSEvent} from '@/ws';

const API_BASE = '/api/data-import';
const CACHE_VERSION = 1;
const CACHE_KEY = `CORPUS_CACHE_V${CACHE_VERSION}`;
const MAX_CACHE_CORPUS = 200;
let persistTimer = null;

function loadSnapshot() {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (parsed.version !== CACHE_VERSION) return null;
        return parsed;
    } catch {
        return null;
    }
}

function saveSnapshot(payload) {
    try {
        localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
    } catch {
    }
}

export const useCorpusStore = defineStore('corpus', {
    state: () => ({
        // 语料与分页
        corpus: [],
        searchQuery: '',
        filterFileType: '',
        corpusPage: 1,
        corpusPageSize: 8,
        // 统计
        counts: {pdf: 0, docx: 0, txt: 0, json: 0},
        // 上传任务
        uploads: [], // {id,name,progress,status,ext,xhr}
        // WS 连接状态
        wsConnectedAtLeastOnce: false,
        // 初始化/缓存
        firstLoaded: false,
        snapshotApplied: false,
        lastRefreshTs: 0,
        // 版本
        cacheVersion: CACHE_VERSION
    }),
    getters: {
        totalUploaded(state) {
            return Object.values(state.counts).reduce((a, b) => a + b, 0);
        },
        corpusTotalPages(state) {
            return Math.max(1, Math.ceil(state.corpus.length / state.corpusPageSize));
        },
        paginatedCorpus(state) {
            const start = (state.corpusPage - 1) * state.corpusPageSize;
            return state.corpus.slice(start, start + state.corpusPageSize);
        }
    },
    actions: {
        applySnapshot() {
            if (this.snapshotApplied) return;
            const snap = loadSnapshot();
            if (snap) {
                this.corpus = snap.corpus || [];
                this.counts = snap.counts || this.counts;
                this.firstLoaded = true;
            }
            this.snapshotApplied = true;
        },
        schedulePersist() {
            clearTimeout(persistTimer);
            persistTimer = setTimeout(() => {
                const slim = this.corpus.slice(0, MAX_CACHE_CORPUS);
                saveSnapshot({
                    version: CACHE_VERSION,
                    corpus: slim,
                    counts: this.counts,
                });
            }, 400);
        },
        mergeCorpus(list) {
            if (!Array.isArray(list)) return;
            const incoming = [...list].sort((a, b) => b.id - a.id);
            const oldMap = new Map(this.corpus.map(i => [i.id, i]));
            const next = [];
            for (const row of incoming) {
                const existed = oldMap.get(row.id);
                if (existed) {
                    existed.fileType = row.fileType;
                    existed.content = row.content;
                    existed.status = row.status;
                    existed.original_filename = row.original_filename;
                    existed.created_at = row.created_at;
                    next.push(existed);
                } else {
                    next.push({...row});
                }
            }
            this.corpus = next;
            this.firstLoaded = true;
            this.schedulePersist();
        },
        updateStats(counts) {
            this.counts = {...this.counts, ...counts};
            this.schedulePersist();
        },
        async refreshStats() {
            try {
                const r = await fetch(`${API_BASE}/stats/`);
                const d = await r.json();
                this.updateStats(d.counts || {});
            } catch {
            }
        },
        async refreshCorpus(params = {}) {
            const p = new URLSearchParams();
            if (params.query ?? this.searchQuery) p.append('query', params.query ?? this.searchQuery);
            if (params.file_type ?? this.filterFileType) p.append('file_type', params.file_type ?? this.filterFileType);
            try {
                const r = await fetch(`${API_BASE}/corpus-data/?${p.toString()}`);
                const list = await r.json();
                this.mergeCorpus(list);
                this.lastRefreshTs = Date.now();
            } catch {
            }
        },
        async refetchAll() {
            await Promise.all([this.refreshStats(), this.refreshCorpus({})]);
        },
        // 上传逻辑（整合）
        startUpload(file, allowedTypes = ['pdf', 'docx', 'txt', 'json']) {
            const ext = file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(ext)) {
                return {error: '不支持的文件类型: ' + ext};
            }
            const item = {
                id: 'local_' + Date.now() + '_' + Math.random().toString(16).slice(2),
                name: file.name,
                progress: 0,
                status: 'uploading',
                ext,
                xhr: null
            };
            this.uploads.unshift(item);

            const form = new FormData();
            form.append('file', file);

            const xhr = new XMLHttpRequest();
            item.xhr = xhr;
            xhr.open('POST', `${API_BASE}/upload/`);

            xhr.upload.onprogress = ev => {
                if (ev.lengthComputable) {
                    item.progress = +(ev.loaded / ev.total * 100).toFixed(2);
                }
            };
            const finalize = () => {
                // 成功上传数变化 -> 触发增量刷新
                const successCount = this.uploads.filter(u => u.status === 'success').length;
                if (successCount > 0) {
                    // 触发异步更新（避免频繁）
                    setTimeout(() => {
                        this.refreshStats();
                        this.refreshCorpus({});
                    }, 300);
                }
            };
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    item.progress = 100;
                    item.status = 'success';
                } else {
                    item.status = 'failed';
                }
                finalize();
            };
            xhr.onerror = () => {
                item.status = 'failed';
                finalize();
            };
            xhr.onloadend = () => {
                if (item.status === 'uploading') {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        item.progress = 100;
                        item.status = 'success';
                    } else {
                        item.status = 'failed';
                    }
                    finalize();
                }
            };
            xhr.send(form);
            return item;
        },
        abortUpload(id) {
            const it = this.uploads.find(u => u.id === id);
            if (it && it.xhr && it.status === 'uploading') {
                try {
                    it.xhr.abort();
                } catch {
                }
                it.status = 'failed';
            }
        },
        // WebSocket 初始化与消息处理
        initRealtime() {
            if (this._wsInited) return;
            this._wsInited = true;
            initWS();
            onWSEvent(msg => {
                if (msg.event === 'ws.reconnected') {
                    this.wsConnectedAtLeastOnce = true;
                    // 断线重连后做一次补拉
                    this.refetchAll();
                    return;
                }
                switch (msg.event) {
                    case 'corpus.created': {
                        const exists = this.corpus.find(c => c.id === msg.data.id);
                        if (!exists) {
                            this.corpus.unshift({
                                id: msg.data.id,
                                fileType: msg.data.fileType,
                                content: msg.data.content || '(解析中...)',
                                status: msg.data.status
                            });
                            // 控制缓存长度
                            if (this.corpus.length > MAX_CACHE_CORPUS) {
                                this.corpus.length = MAX_CACHE_CORPUS;
                            }
                            this.schedulePersist();
                        }
                        break;
                    }
                    case 'corpus.updated': {
                        const it = this.corpus.find(c => c.id === msg.data.id);
                        if (it) {
                            it.status = msg.data.status;
                            if (msg.data.content) it.content = msg.data.content;
                            this.schedulePersist();
                        } else {
                            this.corpus.unshift({
                                id: msg.data.id,
                                fileType: msg.data.fileType,
                                content: msg.data.content || '(解析中...)',
                                status: msg.data.status
                            });
                            if (this.corpus.length > MAX_CACHE_CORPUS) {
                                this.corpus.length = MAX_CACHE_CORPUS;
                            }
                            this.schedulePersist();
                        }
                        break;
                    }
                    case 'corpus.deleted': {
                        const idx = this.corpus.findIndex(c => c.id === msg.data.id);
                        if (idx >= 0) {
                            this.corpus.splice(idx, 1);
                            this.schedulePersist();
                        }
                        break;
                    }
                    case 'stats.update':
                        this.updateStats(msg.stats.counts || {});
                        break;
                }
            });
        }
    }
});
