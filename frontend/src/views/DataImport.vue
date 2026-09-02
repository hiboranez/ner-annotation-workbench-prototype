<!-- vue -->
<template>
  <div class="data-import-container">
    <div class="content-area">
      <div class="left-cards">
        <div class="card upload-section">
          <div class="drag-upload-area">
            <h3>文件上传</h3>
            <div class="upload-box" @drop.prevent="handleDrop" @dragover.prevent>
              <div class="upload-instructions">
                <p>拖拽文件到此处或点击上传</p>
                <p>支持PDF、DOCX、TXT、JSON格式文件</p>
              </div>
              <button class="upload-btn" @click="selectFile">选择文件</button>
              <input type="file" ref="fileInput" @change="handleFileChange" multiple class="file-input"/>
            </div>
          </div>
          <div class="file-type-cards">
            <button
                class="file-type-card"
                v-for="type in fileTypes"
                :key="type"
                :style="{ backgroundColor: fileTypeColors[type] }"
                @click="selectSpecificType(type)"
            >
              {{ type.toUpperCase() }}
            </button>
          </div>
        </div>

        <div class="card corpus-data">
          <div class="corpus-header">
            <h3>语料数据（共{{ store.corpus.length }}条）</h3>
            <button class="export-btn" @click="exportData">导出数据</button>
          </div>
          <div class="search-container">
            <input
                type="text"
                placeholder="搜索语料内容..."
                v-model="store.searchQuery"
                class="search-input"
                @keyup.enter="doSearch"
            />
            <button class="search-btn" @click="doSearch">搜索</button>
            <div class="filter-wrapper">
              <button class="filter-btn" :class="{ active: store.filterFileType }" @click="toggleFilterMenu">
                {{ store.filterFileType ? '筛选：' + store.filterFileType.toUpperCase() : '筛选' }}
              </button>
              <div v-if="showFilterMenu" class="filter-menu">
                <button @click="chooseFilterType('')">全部</button>
                <button v-for="t in fileTypes" :key="'flt-' + t" @click="chooseFilterType(t)">
                  {{ t.toUpperCase() }}
                </button>
              </div>
            </div>
          </div>

          <div class="corpus-list">
            <div class="corpus-list-header">
              <span>ID</span>
              <span>文件类型</span>
              <span>语料内容</span>
              <span>状态</span>
              <span>操作</span>
            </div>
            <div class="corpus-list-item" v-for="item in store.paginatedCorpus" :key="item.id">
              <span>{{ item.id }}</span>
              <span>{{ item.fileType.toUpperCase() }}</span>
              <span class="corpus-content" style="text-align:left;max-height:60px;overflow:auto;">{{
                  item.content
                }}</span>
              <span>{{ item.status }}</span>
              <span>
                <button class="edit-btn" @click="editCorpus(item)">编辑</button>
                <button class="delete-btn" @click="deleteCorpus(item)">删除</button>
              </span>
            </div>
          </div>

          <div v-if="store.corpusTotalPages > 1" class="pager">
            <button class="pager-btn" :disabled="store.corpusPage===1" @click="setCorpusPage(1)">«</button>
            <button class="pager-btn" :disabled="store.corpusPage===1" @click="setCorpusPage(store.corpusPage-1)">
              上一页
            </button>
            <span class="pager-info">
              第
              <span v-if="!editingCorpusPage" class="pager-current" @click="startEditCorpusPage"
                    title="点击输入页码跳转">
                {{ store.corpusPage }}</span>
              <input
                  v-else
                  ref="corpusPageInput"
                  class="pager-input"
                  type="number"
                  v-model="tempCorpusPage"
                  min="1"
                  :max="store.corpusTotalPages"
                  @blur="confirmCorpusPage"
                  @keyup.enter="confirmCorpusPage"
                  @keyup.esc="cancelCorpusPage"
              />
              / {{ store.corpusTotalPages }} 页
            </span>
            <button class="pager-btn" :disabled="store.corpusPage===store.corpusTotalPages"
                    @click="setCorpusPage(store.corpusPage+1)">下一页
            </button>
            <button class="pager-btn" :disabled="store.corpusPage===store.corpusTotalPages"
                    @click="setCorpusPage(store.corpusTotalPages)">»
            </button>
          </div>
        </div>
      </div>

      <div class="right-cards">
        <div class="card upload-status-card">
          <div class="overview-header">
            <h3>上传状态</h3>
            <span class="file-count-badge">当前 {{ store.uploads.length }} 个</span>
          </div>
          <div v-if="store.uploads.length === 0" class="empty-tip">暂无上传任务</div>
          <div v-else class="status-list">
            <div class="status-item" v-for="u in displayedUploads" :key="u.id">
              <div class="status-row">
                <span class="file-name" :title="u.name">{{ u.name }}</span>
                <span class="parse-status-text" :class="{
                      'is-uploading': u.status==='uploading',
                      'is-success': u.status==='success',
                      'is-failed': u.status==='failed'
                    }">{{ statusText(u.status) }}</span>
              </div>
              <div class="bar-wrap">
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: u.progress + '%' }"></div>
                </div>
                <span class="bar-percent">{{ Math.round(u.progress) }}%</span>
              </div>
            </div>
          </div>
          <div v-if="uploadTotalPages > 1" class="pager">
            <button class="pager-btn" :disabled="uploadPage===1" @click="uploadPage=1">«</button>
            <button class="pager-btn" :disabled="uploadPage===1" @click="uploadPage--">上一页</button>
            <span class="pager-info">
              第
              <span v-if="!editingUploadPage" class="pager-current" @click="startEditUploadPage"
                    title="点击输入页码跳转">
                {{ uploadPage }}</span>
              <input
                  v-else
                  ref="uploadPageInput"
                  class="pager-input"
                  type="number"
                  v-model="tempUploadPage"
                  min="1"
                  :max="uploadTotalPages"
                  @blur="confirmUploadPage"
                  @keyup.enter="confirmUploadPage"
                  @keyup.esc="cancelUploadPage"
              />
              / {{ uploadTotalPages }} 页
            </span>
            <button class="pager-btn" :disabled="uploadPage===uploadTotalPages" @click="uploadPage++">下一页</button>
            <button class="pager-btn" :disabled="uploadPage===uploadTotalPages" @click="uploadPage=uploadTotalPages">»
            </button>
          </div>
        </div>

        <div class="card file-distribution">
          <div class="overview-header">
            <h3>文件分布</h3>
            <span class="file-count-badge">共 {{ totalUploaded }} 个</span>
          </div>
          <div v-if="totalUploaded > 0" class="distribution-bar" @mousemove="handleDistMouseMove"
               @mouseleave="hideDistTooltip">
            <div v-for="type in fileTypes" :key="'seg-' + type" class="dist-segment" :style="segmentStyle(type)"
                 @mouseenter="showDistTooltip(type)"></div>
            <div v-if="distTooltip.visible" class="dist-tooltip"
                 :style="{ left: distTooltip.x + 'px', top: distTooltip.y + 'px' }">
              <div class="tt-type">{{ distTooltip.type.toUpperCase() }}</div>
              <div class="tt-percent">{{ percentFor(distTooltip.type) }}%</div>
            </div>
          </div>
          <div v-else class="distribution-bar is-empty"></div>

          <ul class="distribution-legend">
            <li v-for="type in fileTypes" :key="'legend-' + type">
              <span class="dot" :style="{ backgroundColor: fileTypeColors[type] }"></span>{{ type.toUpperCase() }}
            </li>
          </ul>
        </div>

        <div class="card file-type-summary">
          <div class="overview-header">
            <h3>文件统计</h3>
            <span class="file-count-badge">共 {{ totalUploaded }} 个</span>
          </div>
          <div class="file-type-grid">
            <div class="file-type-tile" v-for="type in fileTypes" :key="'tile-' + type">
              <div class="tile-fill" :style="{ backgroundColor: fileTypeColors[type] }"></div>
              <div class="tile-content">
                <div class="tile-type">{{ type.toUpperCase() }}</div>
                <div class="tile-count">{{ store.counts[type] }} 个</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue';
import {useCorpusStore} from '@/stores/corpusStore';
import {apiFetch} from '@/utils/http';

const store = useCorpusStore();

const fileTypes = ['pdf', 'docx', 'txt', 'json'];
const fileTypeColors = {pdf: '#fde68a', docx: '#bfdbfe', txt: '#bbf7d0', json: '#fecdd3'};
const uploadPage = ref(1);
const uploadPageSize = ref(4);
const editingCorpusPage = ref(false);
const tempCorpusPage = ref(1);
const editingUploadPage = ref(false);
const tempUploadPage = ref(1);
const showFilterMenu = ref(false);
const distTooltip = ref({visible: false, type: '', x: 0, y: 0});
const fileInput = ref(null);

function setCorpusPage(p) {
  const total = store.corpusTotalPages;
  const nv = Math.min(Math.max(1, p), total);
  store.corpusPage = nv;
}

function doSearch() {
  store.corpusPage = 1;
  store.refreshCorpus({query: store.searchQuery});
}

function toggleFilterMenu() {
  showFilterMenu.value = !showFilterMenu.value;
}

function chooseFilterType(t) {
  store.filterFileType = t;
  showFilterMenu.value = false;
  store.corpusPage = 1;
  store.refreshCorpus({});
}

async function deleteCorpus(item) {
  if (!confirm(`确认删除 #${item.id}?`)) return;
  try {
    const r = await apiFetch(`/api/data-import/corpus-data/${item.id}/`, {method: 'DELETE'});
    if (r.ok) {
      store.refreshCorpus({});
      store.refreshCounts();
    } else if (r.status === 403) {
      alert('无权限删除（仅管理员）');
    } else if (r.status === 401) {
      alert('请先登录');
    } else {
      alert('删除失败');
    }
  } catch {
  }
}

function exportData() {
  const blob = new Blob([JSON.stringify(store.corpus, null, 2)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'corpus_export.json';
  a.click();
  URL.revokeObjectURL(a.href);
}

function startEditCorpusPage() {
  editingCorpusPage.value = true;
  tempCorpusPage.value = store.corpusPage;
}

function confirmCorpusPage() {
  const v = Number(tempCorpusPage.value) || 1;
  setCorpusPage(v);
  editingCorpusPage.value = false;
}

function cancelCorpusPage() {
  editingCorpusPage.value = false;
}

function startEditUploadPage() {
  editingUploadPage.value = true;
  tempUploadPage.value = uploadPage.value;
}

function confirmUploadPage() {
  let v = Number(tempUploadPage.value) || 1;
  v = Math.min(Math.max(1, v), uploadTotalPages.value);
  uploadPage.value = v;
  editingUploadPage.value = false;
}

function cancelUploadPage() {
  editingUploadPage.value = false;
}

function selectFile() {
  fileInput.value && fileInput.value.click();
}

function handleFileChange(e) {
  const files = e.target.files;
  Array.from(files).forEach(f => store.startUpload(f, fileTypes));
  uploadPage.value = 1;
  e.target.value = '';
}

function handleDrop(e) {
  const files = e.dataTransfer.files;
  Array.from(files).forEach(f => store.startUpload(f, fileTypes));
  uploadPage.value = 1;
}

const uploadTotalPages = computed(() => Math.max(1, Math.ceil(store.uploads.length / uploadPageSize.value)));
const displayedUploads = computed(() => {
  const start = (uploadPage.value - 1) * uploadPageSize.value;
  return store.uploads.slice(start, start + uploadPageSize.value);
});

function statusText(s) {
  if (s === 'uploading') return '上传中';
  if (s === 'success') return '上传成功';
  if (s === 'failed') return '上传失败';
  return s;
}

const totalUploaded = computed(() => store.totalUploaded);

function segmentStyle(type) {
  const total = totalUploaded.value || 1;
  const count = store.counts[type] || 0;
  return {width: (count / total) * 100 + '%', background: fileTypeColors[type]};
}

function percentFor(type) {
  const total = totalUploaded.value || 1;
  return ((store.counts[type] || 0) / total * 100).toFixed(1);
}

function showDistTooltip(type) {
  distTooltip.value.type = type;
  distTooltip.value.visible = true;
}

function handleDistMouseMove(e) {
  if (!distTooltip.value.visible) return;
  const container = e.currentTarget;
  const rect = container.getBoundingClientRect();
  distTooltip.value.x = e.clientX - rect.left;
  distTooltip.value.y = e.clientY - rect.top;
}

function hideDistTooltip() {
  distTooltip.value.visible = false;
}

function editCorpus() {
}

function selectSpecificType(type) {
  alert(`选择示例：${type.toUpperCase()}`);
}

onMounted(async () => {
  store.applySnapshot();
  store.initRealtime();
  if (!store.firstLoaded) {
    await store.refetchAll();
  } else {
    store.refetchAll();
  }
  if (store.corpusPage > store.corpusTotalPages) {
    setCorpusPage(store.corpusTotalPages);
  }
});
</script>

<style scoped>
/* 样式与原版一致，略 */
.edit-btn,
.delete-btn,
.file-type-card,
.upload-btn,
.export-btn,
.search-btn,
.filter-btn {
  position: relative;
  transition: background-color .25s ease, transform .15s ease, box-shadow .25s ease;
  will-change: transform;
}

.edit-btn:hover,
.delete-btn:hover,
.file-type-card:hover,
.upload-btn:hover,
.export-btn:hover,
.search-btn:hover,
.filter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px -4px rgba(0, 0, 0, 0.25);
}

.edit-btn:active,
.delete-btn:active,
.file-type-card:active,
.upload-btn:active,
.export-btn:active,
.search-btn:active,
.filter-btn:active {
  transform: translateY(0) scale(0.95);
  box-shadow: 0 3px 8px -2px rgba(0, 0, 0, 0.30);
  filter: brightness(0.95);
}

.edit-btn:focus-visible,
.delete-btn:focus-visible,
.file-type-card:focus-visible,
.upload-btn:focus-visible,
.export-btn:focus-visible,
.search-btn:focus-visible,
.filter-btn:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.data-import-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #f4f7fc;
}

.content-area {
  display: flex;
  justify-content: space-between;
  width: 100%;
  gap: 30px;
}

.left-cards {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-grow: 1;
}

.right-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 0 0 400px;
  width: 400px;
  flex-shrink: 0;
}

.card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, .1);
  transition: all .3s ease;
}

.card:hover {
  box-shadow: 0 6px 15px rgba(0, 0, 0, .15);
}

.upload-section {
  padding: 20px;
}

.drag-upload-area {
  border: 2px dashed #ccc;
  border-radius: 12px;
  text-align: center;
  padding-bottom: 20px;
}

.upload-btn {
  background: #1d4e89;
  color: #fff;
  padding: 10px 20px;
  margin-top: 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.file-input {
  display: none;
}

.file-type-cards {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.file-type-card {
  width: 22%;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  color: #111;
  border: 1px solid #ccc;
}

.corpus-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.export-btn {
  background: #2d6a4f;
  color: #fff;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
}

.search-container {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.search-input {
  flex-grow: 1;
  padding: 10px;
  margin: 10px 0;
}

.search-btn, .filter-btn, .export-btn {
  background: #2d6a4f;
  color: #fff;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  margin-left: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}

.filter-wrapper {
  position: relative;
}

.filter-menu {
  position: absolute;
  top: 42px;
  right: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, .08);
  padding: 6px 0;
  z-index: 20;
  width: 120px;
}

.filter-menu button {
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}

.filter-menu button:hover {
  background: #f3f4f6;
}

.filter-btn.active {
  background: #1b5e20;
}

.corpus-list-header, .corpus-list-item {
  display: grid;
  grid-template-columns:60px 90px minmax(0, 1fr) 80px 140px;
  column-gap: 12px;
  align-items: center;
  text-align: center;
  padding: 10px;
  box-sizing: border-box;
}

.corpus-content {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  white-space: normal;
  word-break: break-word;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.corpus-list-header {
  font-weight: bold;
  background: #f0f0f0;
  border-radius: 8px;
}

.corpus-list-item {
  margin-top: 5px;
  background: #fff;
  border-radius: 8px;
}

.edit-btn, .delete-btn {
  background: #d9d9d9;
  padding: 5px 10px;
  margin: 0 5px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 0 0 8px;
}

.file-count-badge {
  background: #eef2ff;
  color: #1d4ed8;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
}

.empty-tip {
  padding: 8px 0;
  font-size: 14px;
  color: #666;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 8px;
}

.status-item .status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  line-height: 1.2;
  margin-bottom: 6px;
}

.status-item .file-name {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  font-size: 14px;
  color: #111827;
}

.parse-status-text {
  font-size: 13px;
  font-weight: 600;
}

.parse-status-text.is-uploading {
  color: #1f2937;
}

.parse-status-text.is-success {
  color: #16a34a;
}

.parse-status-text.is-failed {
  color: #dc2626;
}

.bar-track {
  width: 100%;
  height: 10px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #22c55e;
  width: 0%;
  transition: width .3s ease;
}

.bar-percent {
  font-size: 12px;
  color: #374151;
  margin-top: 4px;
  display: inline-block;
}

.file-type-grid {
  display: grid;
  grid-template-columns:repeat(2, 1fr);
  gap: 12px;
}

.file-type-tile {
  position: relative;
  height: 100px;
  border: 1px solid #ccc;
  border-radius: 10px;
  overflow: hidden;
  cursor: default;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .2);
  transition: transform .15s;
}

.file-type-tile:hover {
  transform: translateY(-2px);
}

.tile-fill {
  position: absolute;
  inset: 0;
  opacity: .9;
}

.tile-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #111;
  text-shadow: 0 1px 2px rgba(255, 255, 255, .4);
}

.tile-type {
  font-size: 16px;
  margin-bottom: 4px;
}

.tile-count {
  font-size: 14px;
}

.file-distribution {
  position: relative;
}

.distribution-bar {
  position: relative;
  display: flex;
  width: 100%;
  height: 36px;
  border: 1px solid #ccc;
  overflow: visible;
  background: #f5f5f5;
  cursor: default;
}

.distribution-bar.is-empty {
  background: #555;
}

.dist-segment {
  height: 100%;
  transition: width .35s ease, filter .2s;
  position: relative;
}

.dist-segment:hover {
  filter: brightness(1.15);
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, .9);
}

.distribution-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.distribution-legend li {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #333;
}

.distribution-legend .dot {
  width: 10px;
  height: 10px;
  border-radius: 6px;
  border: 1px solid #666;
}

.dist-tooltip {
  position: absolute;
  z-index: 20;
  background: rgba(0, 0, 0, .75);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  transform: translate(-50%, -120%);
  white-space: nowrap;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, .35);
}

.dist-tooltip .tt-type {
  font-weight: 600;
  font-size: 12px;
  text-align: center;
}

.dist-tooltip .tt-percent {
  font-size: 11px;
  text-align: center;
  margin-top: 2px;
}

.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.pager-btn {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.pager-btn:disabled {
  opacity: .5;
  cursor: not-allowed;
}

.pager-info {
  font-size: 12px;
  color: #6b7280;
}

.pager-current {
  cursor: pointer;
  color: #2563eb;
  font-weight: 800;
}

.pager-input {
  width: 50px;
  padding: 2px 4px;
  font-size: 12px;
  text-align: center;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  outline: none;
}

.pager-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px #2563eb33;
}
</style>
