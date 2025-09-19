// `frontend/src/utils/uploadManager.js`
import {reactive} from 'vue';

const API_BASE = '/api/data-import';

const state = reactive({
    // { id,name,progress,status,ext,_xhr }
    uploads: []
});

function notify() {
    // 触发依赖更新（替换数组引用）
    state.uploads = state.uploads.slice();
}

function startUpload(file, allowedTypes) {
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
        _xhr: null
    };
    state.uploads.unshift(item);
    notify();

    const form = new FormData();
    form.append('file', file);

    const xhr = new XMLHttpRequest();
    item._xhr = xhr;
    xhr.open('POST', `${API_BASE}/upload/`);

    xhr.upload.onprogress = ev => {
        if (ev.lengthComputable) {
            item.progress = +(ev.loaded / ev.total * 100).toFixed(2);
            notify();
        }
    };

    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            item.progress = 100;
            item.status = 'success';
        } else {
            item.status = 'failed';
        }
        notify();
    };

    xhr.onerror = () => {
        item.status = 'failed';
        notify();
    };

    xhr.onloadend = () => {
        if (item.status === 'uploading') {
            if (xhr.status >= 200 && xhr.status < 300) {
                item.progress = 100;
                item.status = 'success';
            } else {
                item.status = 'failed';
            }
            notify();
        }
    };

    xhr.send(form);
    return item;
}

function abortUpload(id) {
    const it = state.uploads.find(u => u.id === id);
    if (it && it._xhr && it.status === 'uploading') {
        try {
            it._xhr.abort();
        } catch (e) {
        }
        it.status = 'failed';
        notify();
    }
}

export default {
    state,
    startUpload,
    abortUpload
};