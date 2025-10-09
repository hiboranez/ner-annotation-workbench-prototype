// javascript
import {defineStore} from 'pinia';

const LS_KEY = 'auth_store_v1';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: '',
        refreshToken: '',
        user: null, // { id, username, groups: [...] }
        loaded: false,
    }),
    getters: {
        isAuthenticated: (s) => !!s.accessToken,
        groups: (s) => (s.user?.groups || []).map(x => String(x).toLowerCase()),
        isAdmin: (s) => !!(s.user && (s.user.is_staff || s.user.is_superuser || s.groups.includes('admin'))),
        isAnnotator: (s) => s.groups.includes('annotator'),
        isViewer: (s) => s.groups.includes('viewer'),
        authHeader: (s) => s.accessToken ? {Authorization: `Bearer ${s.accessToken}`} : {},
    },
    actions: {
        load() {
            if (this.loaded) return;
            try {
                const raw = localStorage.getItem(LS_KEY);
                if (raw) {
                    const v = JSON.parse(raw);
                    this.accessToken = v.accessToken || '';
                    this.refreshToken = v.refreshToken || '';
                    this.user = v.user || null;
                }
            } catch {
            }
            this.loaded = true;
        },
        persist() {
            localStorage.setItem(LS_KEY, JSON.stringify({
                accessToken: this.accessToken,
                refreshToken: this.refreshToken,
                user: this.user,
            }));
        },
        async login(username, password) {
            this.load();
            const resp = await fetch('/api/token/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password}),
            });
            if (!resp.ok) throw new Error('登录失败');
            const data = await resp.json();
            this.accessToken = data.access;
            this.refreshToken = data.refresh;
            await this.fetchMe();
            this.persist();
        },
        async register(username, password, role = 'viewer') {
            this.load();
            const resp = await fetch('/api/data-import/auth/register/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, role}),
            });
            const json = await resp.json();
            if (!resp.ok || json.code !== 0) {
                throw new Error(json.message || '注册失败');
            }
            this.accessToken = json.data.access;
            this.refreshToken = json.data.refresh;
            this.user = json.data.user;
            this.persist();
        },
        async fetchMe() {
            const resp = await fetch('/api/data-import/auth/me/', {
                headers: {...this.authHeader},
            });
            if (!resp.ok) throw new Error('获取用户信息失败');
            const json = await resp.json();
            if (json.code !== 0) throw new Error(json.message || '获取用户信息失败');
            this.user = json.data;
            this.persist();
        },
        async tryRefresh() {
            if (!this.refreshToken) return false;
            const r = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({refresh: this.refreshToken}),
            });
            if (!r.ok) return false;
            const data = await r.json();
            if (!data.access) return false;
            this.accessToken = data.access;
            this.persist();
            return true;
        },
        logout() {
            this.accessToken = '';
            this.refreshToken = '';
            this.user = null;
            this.persist();
        },
    },
});
