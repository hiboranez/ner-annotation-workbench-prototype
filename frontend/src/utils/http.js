// javascript
import {useAuthStore} from '@/stores/authStore';

export async function apiFetch(url, options = {}, retry = true) {
    const auth = useAuthStore();
    auth.load();

    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }
    if (auth.accessToken) {
        headers.set('Authorization', `Bearer ${auth.accessToken}`);
    }

    const resp = await fetch(url, {...options, headers});
    if (resp.status === 401 && retry && await auth.tryRefresh()) {
        return apiFetch(url, options, false);
    }
    return resp;
}
