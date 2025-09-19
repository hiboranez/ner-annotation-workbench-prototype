<template>
  <div class="data-import-container">
    <div class="content-area">
      <!-- 左侧 -->
      <div class="left-cards">
        <!-- 上传卡片 -->
        <div class="card upload-section">
          <div class="drag-upload-area">
            <h3>文件上传</h3>
            <div
                class="upload-box"
                @drop.prevent="handleDrop"
                @dragover.prevent
            >
              <div class="upload-instructions">
                <p>拖拽文件到此处或点击上传</p>
                <p>支持PDF、DOCX、TXT、JSON格式文件</p>
              </div>
              <button class="upload-btn" @click="selectFile">选择文件</button>
              <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileChange"
                  multiple
                  class="file-input"
              />
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

        <!-- 语料数据 -->
        <div class="card corpus-data">
          <div class="corpus-header">
            <h3>语料数据（共{{ corpusData.length }}条）</h3>
            <button class="export-btn" @click="exportData">导出数据</button>
          </div>
          <div class="search-container">
            <input
                type="text"
                placeholder="搜索语料内容..."
                v-model="searchQuery"
                class="search-input"
                @keyup.enter="fetchCorpusData"
            />
            <button class="search-btn" @click="fetchCorpusData">搜索</button>
            <div class="filter-wrapper">
              <button
                  class="filter-btn"
                  :class="{ active: filterFileType }"
                  @click="toggleFilterMenu"
              >
                {{ filterFileType ? '筛选：' + filterFileType.toUpperCase() : '筛选' }}
              </button>
              <div v-if="showFilterMenu" class="filter-menu">
                <button @click="chooseFilterType('')">全部</button>
                <button
                    v-for="t in fileTypes"
                    :key="'flt-' + t"
                    @click="chooseFilterType(t)"
                >{{ t.toUpperCase() }}
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
            <div
                class="corpus-list-item"
                v-for="item in paginatedCorpus"
                :key="item.id"
            >
              <span>{{ item.id }}</span>
              <span>{{ item.fileType.toUpperCase() }}</span>
              <span style="text-align:left;max-height:60px;overflow:auto;">{{ item.content }}</span>
              <span>{{ item.status }}</span>
              <span>
                    <button class="edit-btn" @click="editCorpus(item)">编辑</button>
                    <button class="delete-btn" @click="deleteCorpus(item)">删除</button>
                  </span>
            </div>
          </div>

          <div v-if="corpusTotalPages > 1" class="pager">
            <button class="pager-btn" :disabled="corpusPage===1" @click="corpusPage=1">«</button>
            <button class="pager-btn" :disabled="corpusPage===1" @click="corpusPage--">上一页</button>
            <span class="pager-info">
    第
    <span
        v-if="!editingCorpusPage"
        class="pager-current"
        @click="startEditCorpusPage"
        title="点击输入页码跳转"
    >{{ corpusPage }}</span>
    <input
        v-else
        ref="corpusPageInput"
        class="pager-input"
        type="number"
        v-model="tempCorpusPage"
        min="1"
        :max="corpusTotalPages"
        @blur="confirmCorpusPage"
        @keyup.enter="confirmCorpusPage"
        @keyup.esc="cancelCorpusPage"
    />
    / {{ corpusTotalPages }} 页
  </span>
            <button class="pager-btn" :disabled="corpusPage===corpusTotalPages" @click="corpusPage++">下一页</button>
            <button class="pager-btn" :disabled="corpusPage===corpusTotalPages" @click="corpusPage=corpusTotalPages">»
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧 -->
      <div class="right-cards">
        <!-- 上传状态（分页） -->
        <div class="card upload-status-card">
          <div class="overview-header">
            <h3>上传状态</h3>
            <span class="file-count-badge">当前 {{ uploads.length }} 个</span>
          </div>
          <div v-if="uploads.length === 0" class="empty-tip">暂无上传任务</div>
          <div v-else class="status-list">
            <div
                class="status-item"
                v-for="u in displayedUploads"
                :key="u.id"
            >
              <div class="status-row">
                <span class="file-name" :title="u.name">{{ u.name }}</span>
                <span
                    class="parse-status-text"
                    :class="{
                      'is-uploading': u.status==='uploading',
                      'is-success': u.status==='success',
                      'is-failed': u.status==='failed'
                    }"
                >{{ statusText(u.status) }}</span>
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
    <span
        v-if="!editingUploadPage"
        class="pager-current"
        @click="startEditUploadPage"
        title="点击输入页码跳转"
    >{{ uploadPage }}</span>
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

        <!-- 文件分布 -->
        <div class="card file-distribution">
          <div class="overview-header">
            <h3>文件分布</h3>
            <span class="file-count-badge">共 {{ totalUploaded }} 个</span>
          </div>

          <div
              v-if="totalUploaded > 0"
              class="distribution-bar"
              @mousemove="handleDistMouseMove"
              @mouseleave="hideDistTooltip"
          >
            <div
                v-for="type in fileTypes"
                :key="'seg-' + type"
                class="dist-segment"
                :style="segmentStyle(type)"
                @mouseenter="showDistTooltip(type)"
            ></div>

            <div
                v-if="distTooltip.visible"
                class="dist-tooltip"
                :style="{ left: distTooltip.x + 'px', top: distTooltip.y + 'px' }"
            >
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

        <!-- 文件统计 -->
        <div class="card file-type-summary">
          <div class="overview-header">
            <h3>文件统计</h3>
            <span class="file-count-badge">共 {{ totalUploaded }} 个</span>
          </div>
          <div class="file-type-grid">
            <div
                class="file-type-tile"
                v-for="type in fileTypes"
                :key="'tile-' + type"
            >
              <div class="tile-fill" :style="{ backgroundColor: fileTypeColors[type] }"></div>
              <div class="tile-content">
                <div class="tile-type">{{ type.toUpperCase() }}</div>
                <div class="tile-count">{{ uploadedFiles[type] }} 个</div>
              </div>
            </div>
          </div>
        </div>

      </div> <!-- /right-cards -->
    </div>
  </div>
</template>

<script>
import uploadManager from '@/utils/uploadManager';

const API_BASE = '/api/data-import';

export default {
  data() {
    return {
      fileTypes: ['pdf', 'docx', 'txt', 'json'],
      fileTypeColors: {pdf: '#8FB2FF', docx: '#8FFFB2', txt: '#FFF48F', json: '#D8B4FF'},
      uploadedFiles: {pdf: 0, docx: 0, txt: 0, json: 0},
      corpusData: [],
      searchQuery: '',
      filterFileType: '',
      showFilterMenu: false,
      selectedFileType: '',
      distTooltip: {visible: false, type: '', x: 0, y: 0},
      corpusPage: 1,
      corpusPageSize: 8,
      uploadPage: 1,
      uploadPageSize: 4,
      editingCorpusPage: false,
      tempCorpusPage: '',
      editingUploadPage: false,
      tempUploadPage: ''
      // 移除 uploadState
    };
  },
  computed: {
    totalUploaded() {
      return Object.values(this.uploadedFiles).reduce((a, b) => a + b, 0);
    },
    corpusTotalPages() {
      return Math.max(1, Math.ceil(this.corpusData.length / this.corpusPageSize));
    },
    paginatedCorpus() {
      const start = (this.corpusPage - 1) * this.corpusPageSize;
      return this.corpusData.slice(start, start + this.corpusPageSize);
    },
    uploadTotalPages() {
      return Math.max(1, Math.ceil(this.uploads.length / this.uploadPageSize));
    },
    displayedUploads() {
      const start = (this.uploadPage - 1) * this.uploadPageSize;
      return this.uploads.slice(start, start + this.uploadPageSize);
    },
    uploads() {
      return uploadManager.state.uploads; // 直接引用
    }
  },
  watch: {
    uploads: {
      deep: true,
      handler(arr) {
        if (arr.some(u => u.status === 'success')) {
          this.fetchStats();
        }
        if (this.uploadPage > this.uploadTotalPages) {
          this.uploadPage = this.uploadTotalPages;
        }
      }
    },
    'corpusData.length'() {
      if (this.corpusPage > this.corpusTotalPages) this.corpusPage = this.corpusTotalPages;
    }
  },
  methods: {
    fetchStats() {
      fetch(`${API_BASE}/stats/`)
          .then(r => r.json())
          .then(data => {
            const counts = data.counts || {};
            this.fileTypes.forEach(t => {
              this.uploadedFiles[t] = counts[t] || 0;
            });
          })
          .catch(() => {
          });
    },
    fetchCorpusData() {
      const params = new URLSearchParams();
      if (this.searchQuery) params.append('query', this.searchQuery);
      if (this.filterFileType) params.append('file_type', this.filterFileType);
      fetch(`${API_BASE}/corpus-data/?` + params.toString())
          .then(r => r.json())
          .then(list => {
            this.corpusData = Array.isArray(list) ? list : [];
            if (this.corpusPage > this.corpusTotalPages) this.corpusPage = this.corpusTotalPages;
          })
          .catch(() => {
          });
    },
    toggleFilterMenu() {
      this.showFilterMenu = !this.showFilterMenu;
    },
    chooseFilterType(t) {
      this.filterFileType = t;
      this.showFilterMenu = false;
      this.corpusPage = 1;
      this.fetchCorpusData();
    },
    selectFile() {
      this.$refs.fileInput.click();
    },
    selectSpecificType(type) {
      this.selectedFileType = type;
      this.selectFile();
    },
    handleFileChange(e) {
      const files = e.target.files;
      Array.from(files).forEach(f => {
        const ext = f.name.split('.').pop().toLowerCase();
        if (!this.selectedFileType || ext === this.selectedFileType) {
          this.uploadFile(f);
        } else {
          alert(`只能上传 ${this.selectedFileType.toUpperCase()} 文件`);
        }
      });
      e.target.value = '';
    },
    handleDrop(e) {
      const files = e.dataTransfer.files;
      Array.from(files).forEach(f => this.uploadFile(f));
    },
    uploadFile(file) {
      const ret = uploadManager.startUpload(file, this.fileTypes);
      if (ret && ret.error) {
        alert(ret.error);
        return;
      }
      this.uploadPage = 1;
    },
    statusText(s) {
      if (s === 'uploading') return '上传中';
      if (s === 'success') return '上传成功';
      if (s === 'failed') return '上传失败';
      return s;
    },
    exportData() {
      const blob = new Blob([JSON.stringify(this.corpusData, null, 2)], {type: 'application/json'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'corpus_export.json';
      a.click();
      URL.revokeObjectURL(a.href);
    },
    editCorpus(item) {
      console.log('Edit', item);
    },
    deleteCorpus(item) {
      alert('示例：未实现删除接口');
    },
    /* 文件分布 */
    segmentStyle(type) {
      const total = this.totalUploaded;
      const ratio = total ? (this.uploadedFiles[type] / total) : 0;
      return {
        width: (ratio * 100) + '%',
        backgroundColor: this.fileTypeColors[type],
        minWidth: ratio > 0 && ratio * 100 < 0.8 ? '0.8%' : undefined
      };
    },
    percentFor(type) {
      if (!this.totalUploaded) return 0;
      return ((this.uploadedFiles[type] / this.totalUploaded) * 100).toFixed(1);
    },
    showDistTooltip(type) {
      this.distTooltip.type = type;
      this.distTooltip.visible = true;
    },
    handleDistMouseMove(e) {
      if (!this.distTooltip.visible) return;
      const rect = e.currentTarget.getBoundingClientRect();
      let x = e.clientX - rect.left;
      let y = e.clientY - rect.top;
      x = Math.min(Math.max(10, x), rect.width - 10);
      y = Math.min(Math.max(10, y), rect.height - 10);
      this.distTooltip.x = x;
      this.distTooltip.y = y;
    },
    hideDistTooltip() {
      this.distTooltip.visible = false;
    },
    startEditCorpusPage() {
      this.editingCorpusPage = true;
      this.tempCorpusPage = this.corpusPage;
      this.$nextTick(() => {
        this.$refs.corpusPageInput && this.$refs.corpusPageInput.select();
      });
    },
    confirmCorpusPage() {
      let v = parseInt(this.tempCorpusPage, 10);
      if (isNaN(v)) return this.cancelCorpusPage();
      if (v < 1) v = 1;
      if (v > this.corpusTotalPages) v = this.corpusTotalPages;
      this.corpusPage = v;
      this.editingCorpusPage = false;
    },
    cancelCorpusPage() {
      this.editingCorpusPage = false;
    },
    startEditUploadPage() {
      this.editingUploadPage = true;
      this.tempUploadPage = this.uploadPage;
      this.$nextTick(() => {
        this.$refs.uploadPageInput && this.$refs.uploadPageInput.select();
      });
    },
    confirmUploadPage() {
      let v = parseInt(this.tempUploadPage, 10);
      if (isNaN(v)) return this.cancelUploadPage();
      if (v < 1) v = 1;
      if (v > this.uploadTotalPages) v = this.uploadTotalPages;
      this.uploadPage = v;
      this.editingUploadPage = false;
    },
    cancelUploadPage() {
      this.editingUploadPage = false;
    },
  },
  mounted() {
    this.fetchStats();
    this.fetchCorpusData();
  }
};
</script>

<style scoped>
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
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-grow: 1;
}

.right-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 300px;
}

.card {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
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
  background-color: #1d4e89;
  color: white;
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
  border: 2px solid #ccc;
}

.corpus-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.export-btn {
  background-color: #2d6a4f;
  color: white;
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
  margin-top: 10px;
  margin-bottom: 10px;
}

.search-btn,
.filter-btn,
.export-btn {
  background-color: #2d6a4f;
  color: white;
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
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
  background-color: #1b5e20;
}

.corpus-list-header,
.corpus-list-item {
  display: grid;
  grid-template-columns:
      minmax(50px, 0.8fr)
      minmax(70px, 1fr)
      minmax(200px, 2.5fr)
      minmax(70px, 1fr)
      minmax(120px, 1fr);
  column-gap: 12px;
  align-items: center;
  text-align: center;
  padding: 10px 10px;
  box-sizing: border-box;
}

.corpus-list-header {
  font-weight: bold;
  background-color: #f0f0f0;
  border-radius: 8px;
}

.corpus-list-item {
  margin-top: 5px;
  background-color: #fff;
  border-radius: 8px;
}

.edit-btn,
.delete-btn {
  background-color: #d9d9d9;
  padding: 5px 10px;
  margin-left: 5px;
  margin-right: 5px;
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

.overview-header h3 {
  flex: 1;
  margin: 0;
  font-size: 16px;
  line-height: 1.2;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-count-badge {
  flex-shrink: 0;
  white-space: nowrap;
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
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: #22c55e;
  width: 0%;
  transition: width 0.3s ease;
}

.bar-percent {
  font-size: 12px;
  color: #374151;
  margin-top: 4px;
  display: inline-block;
}

/* 四宫格文件概况 */
.file-type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.file-type-tile {
  position: relative;
  height: 100px;
  border: 1px solid #ccc;
  border-radius: 10px;
  overflow: hidden;
  cursor: default;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.2);
  transition: transform .15s ease;
}

.file-type-tile:hover {
  transform: translateY(-2px);
}

.tile-fill {
  position: absolute;
  inset: 0;
  opacity: 0.9;
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
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.4);
}

.tile-type {
  font-size: 16px;
  line-height: 1.1;
  margin-bottom: 4px;
}

.tile-count {
  font-size: 14px;
  line-height: 1.1;
}

/* 文件分布 */
.file-distribution {
  position: relative;
}

.distribution-bar {
  position: relative;
  display: flex;
  width: 100%;
  height: 36px;
  border: 1px solid #ccc;
  border-radius: 8px;
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
  outline: 2px solid rgba(255, 255, 255, 0.9);
  outline-offset: -2px;
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
  border-radius: 50%;
  border: 1px solid #666;
}

.dist-tooltip {
  position: absolute;
  z-index: 20;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  transform: translate(-50%, -120%);
  white-space: nowrap;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
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

/* 分页器 */
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.pager-btn {
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.pager-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pager-info {
  font-size: 12px;
  color: #6b7280;
}

.pager-current {
  cursor: pointer;
  padding: 0 4px;
  color: #2563eb;
  font-weight: 600;
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