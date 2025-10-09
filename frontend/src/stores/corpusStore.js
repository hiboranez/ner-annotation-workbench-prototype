// javascript
import {defineStore} from 'pinia';
import {apiFetch} from '@/utils/http';
import {initWS, onWSEvent} from '@/utils/realtime';
import {useAuthStore} from '@/stores/authStore';

const MAX_CACHE_CORPUS = 1000;
const LS_KEY = 'corpus_store_v1';

export const useCorpusStore = defineStore('corpus', {
    state: () => ({
        corpus: [],
        counts: {pdf: 0, docx: 0, txt: 0, json: 0},
        total: 0,

        searchQuery: '',
        filterFileType: '',
        corpusPage: 1,
        corpusPageSize: 10,

        uploads: [],

        _wsInited: false,
        wsConnectedAtLeastOnce: false,
        firstLoaded: false,
    }),
    getters: {
        totalUploaded: (s) => Object.values(s.counts || {}).reduce((a, b) => a + (b || 0), 0),
        corpusTotalPages: (s) => Math.max(1, Math.ceil(s.corpus.length / s.corpusPageSize)),
        paginatedCorpus: (s) => {
            const start = (s.corpusPage - 1) * s.corpusPageSize;
            return s.corpus.slice(start, start + s.corpusPageSize);
        },
    },
    actions: {
        applySnapshot() {
            try {
                const raw = localStorage.getItem(LS_KEY);
                if (!raw) return;
                const v = JSON.parse(raw);
                this.corpus = v.corpus || [];
                this.counts = v.counts || {pdf: 0, docx: 0, txt: 0, json: 0};
                this.total = v.total || 0;
                this.searchQuery = v.searchQuery || '';
                this.filterFileType = v.filterFileType || '';
                this.corpusPage = v.corpusPage || 1;
            } catch {
            }
        },
        schedulePersist() {
            try {
                localStorage.setItem(LS_KEY, JSON.stringify({
                    corpus: this.corpus,
                    counts: this.counts,
                    total: this.total,
                    searchQuery: this.searchQuery,
                    filterFileType: this.filterFileType,
                    corpusPage: this.corpusPage,
                }));
            } catch {
            }
        },
        updateStats(counts) {
            this.counts = {...{pdf: 0, docx: 0, txt: 0, json: 0}, ...counts};
            this.total = Object.values(this.counts).reduce((a, b) => a + (b || 0), 0);
            this.schedulePersist();
        },
        async refreshCounts() {
            const r = await apiFetch('/api/data-import/stats/');
            if (!r.ok) return;
            const json = await r.json();
            const counts = json.counts || json.data?.counts || {};
            this.updateStats(counts);
        },
        async refreshCorpus({query} = {}) {
            if (typeof query === 'string') this.searchQuery = query;
            const params = new URLSearchParams();
            if (this.searchQuery) params.set('query', this.searchQuery);
            if (this.filterFileType) params.set('file_type', this.filterFileType);
            const r = await apiFetch(`/api/data-import/corpus-data/${params.toString() ? '?' + params.toString() : ''}`);
            if (!r.ok) return;
            const data = await r.json();
            this.corpus = Array.isArray(data) ? data : (data.data || []);
            if (this.corpus.length > MAX_CACHE_CORPUS) this.corpus.length = MAX_CACHE_CORPUS;
            this.firstLoaded = true;
            this.schedulePersist();
        },
        async refetchAll() {
            await Promise.all([this.refreshCounts(), this.refreshCorpus({})]);
        },

        startUpload(file, allowedTypes = ['pdf', 'docx', 'txt', 'json']) {
            const auth = useAuthStore();
            auth.load();

            const ext = file.name.includes('.') ? file.name.split('.').pop().toLowerCase() : '';
            if (!allowedTypes.includes(ext)) {
                alert(`不支持的类型: ${ext}`);
                return null;
            }
            const id = Date.now() + Math.random();
            const item = {id, name: file.name, size: file.size, progress: 0, status: 'uploading', xhr: null};
            this.uploads.unshift(item);
            if (this.uploads.length > 200) this.uploads.length = 200;

            const form = new FormData();
            form.append('file', file);

            const xhr = new XMLHttpRequest();
            item.xhr = xhr;
            xhr.open('POST', '/api/data-import/upload/', true);
            if (auth.accessToken) {
                xhr.setRequestHeader('Authorization', `Bearer ${auth.accessToken}`);
            }

            const finalize = () => {
                item.progress = 100;
                setTimeout(() => {
                    item.xhr = null;
                }, 300);
            };

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    item.progress = Math.min(99, (e.loaded / e.total) * 100);
                }
            };

            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    try {
                        const ok = xhr.status >= 200 && xhr.status < 300;
                        if (ok) {
                            const resp = JSON.parse(xhr.responseText || '{}');
                            if ((resp.code ?? 0) === 0) {
                                item.status = 'success';
                                this.refreshCounts().catch(() => {
                                });
                            } else {
                                item.status = 'failed';
                            }
                        } else if (xhr.status === 401) {
                            item.status = 'failed';
                            alert('未登录或无权限上传');
                        } else {
                            item.status = 'failed';
                        }
                    } catch {
                        item.status = 'failed';
                    }
                    finalize();
                }
            };

            xhr.onerror = () => {
                item.status = 'failed';
                finalize();
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

        initRealtime() {
            if (this._wsInited) return;
            this._wsInited = true;
            initWS();
            onWSEvent(msg => {
                if (msg.event === 'ws.reconnected') {
                    this.wsConnectedAtLeastOnce = true;
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
                            if (this.corpus.length > MAX_CACHE_CORPUS) this.corpus.length = MAX_CACHE_CORPUS;
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
                            if (this.corpus.length > MAX_CACHE_CORPUS) this.corpus.length = MAX_CACHE_CORPUS;
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
                        this.updateStats(msg.stats?.counts || {});
                        break;
                }
            });
        },
    }
});
