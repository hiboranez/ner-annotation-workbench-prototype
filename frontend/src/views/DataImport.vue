<template>
  <div class="data-import-container">
    <div class="content-area">
      <!-- 左侧卡片区域 -->
      <div class="left-cards">
        <!-- 文件上传部分 -->
        <div class="card upload-section">
          <!-- 文件拖拽上传区域 -->
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

          <!-- 文件类型按钮卡片 -->
          <div class="file-type-cards">
            <button
                class="file-type-card"
                v-for="type in fileTypes"
                :key="type"
                :style="{ backgroundColor: fileTypeColors[type] }"
                @click="selectFileType(type)"
            >
              {{ type.toUpperCase() }}
            </button>
          </div>
        </div>

        <!-- 语料数据 -->
        <div class="card corpus-data">
          <div class="corpus-header">
            <h3>语料数据（共{{ totalCorpus }}条）</h3>
            <button class="export-btn" @click="exportData">导出数据</button>
          </div>
          <div class="search-container">
            <input
                type="text"
                placeholder="搜索语料内容..."
                v-model="searchQuery"
                class="search-input"
            />
            <button class="search-btn" @click="searchCorpus">搜索</button>
            <button class="filter-btn" @click="filterCorpus">筛选</button>
          </div>
          <!-- 数据列表 -->
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
                v-for="(item, index) in filteredCorpusData"
                :key="index"
            >
              <span>{{ item.id }}</span>
              <span>{{ item.fileType }}</span>
              <span>{{ item.content }}</span>
              <span>{{ item.status }}</span>
              <span>
                <button class="edit-btn" @click="editCorpus(item)">编辑</button>
                <button class="delete-btn" @click="deleteCorpus(item)">
                  删除
                </button>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧小卡片区域 -->
      <div class="right-cards">
        <!-- 新增：上传状态（合并上传进度与解析状态），放在文件概况上方 -->
        <div class="card upload-status-card">
          <div class="overview-header">
            <h3>上传状态</h3>
            <span class="file-count-badge">共 {{ uploads.length }} 个</span>
          </div>

          <!-- 无文件时 -->
          <div v-if="uploads.length === 0" class="empty-tip">未上传文件</div>

          <!-- 有文件时：每页最多4条 -->
          <div v-else class="status-list">
            <div
                class="status-item"
                v-for="(u, idx) in pagedUploads"
                :key="u.id"
            >
              <div class="status-row">
                <span class="file-name" :title="u.name">{{ u.name }}</span>
                <span
                    class="parse-status-text"
                    :class="{
                    'is-uploading': u.status === 'uploading',
                    'is-success': u.status === 'success',
                    'is-failed': u.status === 'failed'
                  }"
                >
                  {{ statusText(u.status) }}
                </span>
              </div>
              <div class="bar-wrap" aria-label="上传进度">
                <div class="bar-track">
                  <div
                      class="bar-fill"
                      :style="{ width: (u.progress || 0) + '%' }"
                  ></div>
                </div>
                <span class="bar-percent">{{ Math.round(u.progress) }}%</span>
              </div>
            </div>

            <!-- 分页器：仅当总数>4时显示 -->
            <div v-if="totalPages > 1" class="pager">
              <button
                  class="pager-btn"
                  :disabled="currentPage === 1"
                  @click="currentPage--"
              >
                上一页
              </button>
              <span class="pager-info">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <button
                  class="pager-btn"
                  :disabled="currentPage === totalPages"
                  @click="currentPage++"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <!-- 合并后的 文件概况（含类型进度条） -->
        <div class="card file-type-summary">
          <div class="overview-header">
            <h3>文件概况</h3>
            <span class="file-count-badge">共 {{ totalUploaded }} 个</span>
          </div>
          <div
              class="file-type-progress"
              v-for="type in fileTypes"
              :key="'summary-' + type"
          >
            <div class="label-row">
              <span class="type-name">{{ type.toUpperCase() }}</span>
            </div>
            <div class="progress-wrap">
              <div class="progress-track">
                <div
                    class="progress-fill"
                    :style="{
                    width: calculatePercentage(type) + '%',
                    backgroundColor: fileTypeColors[type]
                  }"
                ></div>
                <span class="progress-percent">{{ calculatePercentage(type) }}%</span>
              </div>
              <span class="progress-count">{{ uploadedFiles[type] }} 个</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      fileTypes: ["pdf", "docx", "txt", "json"], // 支持的文件类型（用于展示）
      fileTypeColors: {
        pdf: "#8FB2FF", // 蓝
        docx: "#8FFFB2", // 绿
        txt: "#FFF48F", // 黄
        json: "#D8B4FF", // 紫
      },
      uploadedFiles: {pdf: 0, docx: 0, txt: 0, json: 0},
      totalCorpus: 100, // 示例数据
      searchQuery: "",
      corpusData: [{id: "#001", fileType: "JSON", content: '{"text":"xx"}', status: "已解析"}],
      selectedFileType: "",

      /** ===== 新增：上传状态数据结构 =====
       * uploads: { id, name, progress(0-100), status: 'uploading'|'success'|'failed', ext }
       */
      uploads: [],
      currentPage: 1, // 上传状态分页（每页4条）
      pageSize: 4,
      _uidSeed: 1, // 简易id生成
      filteredCorpusData: [], // 存放筛选后的数据
    };
  },
  computed: {
    totalUploaded() {
      return Object.values(this.uploadedFiles).reduce((a, b) => a + b, 0);
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.uploads.length / this.pageSize));
    },
    pagedUploads() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.uploads.slice(start, start + this.pageSize);
    },
  },
  methods: {
    filterCorpusData() {
      // 筛选数据，支持搜索内容和文件类型筛选
      this.filteredCorpusData = this.corpusData.filter((item) => {
        return (
            item.content.includes(this.searchQuery) &&
            (this.selectedFileType ? item.fileType === this.selectedFileType : true)
        );
      });
    },
    searchCorpus() {
      this.filterCorpusData(); // 点击搜索时，重新过滤数据
    },
    filterCorpus() {
      this.filterCorpusData(); // 点击筛选时，重新过滤数据
    },
    exportData() {
      console.log("Exporting data");
    },
    editCorpus(item) {
      console.log("Editing corpus:", item);
    },
    deleteCorpus(item) {
      console.log("Deleting corpus:", item);
    },
    selectFile() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const files = event.target.files;
      Array.from(files).forEach((file) => {
        const ext = file.name.split(".").pop().toLowerCase();
        if (!this.selectedFileType || ext === this.selectedFileType) {
          this.uploadFile(file);
        } else {
          alert(`只能上传 ${this.selectedFileType.toUpperCase()} 文件`);
        }
      });
      // reset input
      event.target.value = "";
    },
    selectFileType(fileType) {
      this.selectedFileType = fileType;
      this.selectFile();
    },
    uploadFile(file) {
      const ext = file.name.split(".").pop().toLowerCase();
      const item = {
        id: `up_${this._uidSeed++}`,
        name: file.name,
        progress: 0,
        status: "uploading",
        ext,
      };
      this.uploads.unshift(item); // 新文件显示在最前
      this.currentPage = 1; // 回到第一页以便看到最新

      const speed = 15 + Math.random() * 25;
      const timer = setInterval(() => {
        if (item.status !== "uploading") {
          clearInterval(timer);
          return;
        }
        item.progress = Math.min(100, item.progress + speed * (0.2 + Math.random() * 0.8));
        if (item.progress >= 100) {
          const ok = Math.random() > 0.08;
          if (ok) {
            item.status = "success";
            item.progress = 100;
            if (this.uploadedFiles[ext] !== undefined) {
              this.uploadedFiles[ext]++;
            }
          } else {
            item.status = "failed";
            item.progress = 100;
          }
          clearInterval(timer);
        }
      }, 400);
    },
    calculatePercentage(fileType) {
      const total = Object.values(this.uploadedFiles).reduce((a, b) => a + b, 0);
      return total === 0 ? 0 : Math.round((this.uploadedFiles[fileType] / total) * 100);
    },
    handleDrop(event) {
      const files = event.dataTransfer.files;
      Array.from(files).forEach((file) => {
        const ext = file.name.split(".").pop().toLowerCase();
        if (!this.selectedFileType || ext === this.selectedFileType) {
          this.uploadFile(file);
        } else {
          alert(`只能上传 ${this.selectedFileType.toUpperCase()} 文件`);
        }
      });
    },
    statusText(status) {
      if (status === "uploading") return "上传中";
      if (status === "success") return "上传成功";
      if (status === "failed") return "上传失败";
      return status;
    },
  },
  mounted() {
    this.filteredCorpusData = this.corpusData; // 初始化时显示所有数据
  },
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

.upload-instructions p {
  margin: 5px 0;
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

/* 文件类型按钮 */
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
  border: 2px solid #ccc; /* 增加灰色描边 */
}

/* 语料数据部分 */
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
  margin-top: 20px;
}

.search-input {
  flex-grow: 1;
  padding: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.search-btn,
.filter-btn {
  background-color: #2d6a4f;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  margin-left: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.corpus-list-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  background-color: #f0f0f0;
  padding: 10px;
}

.corpus-list-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  margin-top: 5px;
  background-color: #fff;
  border-radius: 8px;
}

.edit-btn,
.delete-btn {
  background-color: #d9d9d9;
  padding: 5px 10px;
  margin-right: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

/* ===== 文件类型进度条（右侧“文件概况”卡片） ===== */
.file-type-summary .file-type-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  font-size: 14px;
}

/* 进度条容器与文本定位 */
.progress-wrap {
  position: relative;
}

/* 进度条本体：黑色描边，百分比居中 */
.progress-track {
  position: relative;
  width: 100%;
  height: 18px;
  background-color: #f0f2f5; /* 灰色背景 */
  border-radius: 6px;
  border: 1px solid #ccc; /* 灰色边框 */
  overflow: hidden;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 6px;
  transition: width 0.35s ease;
}

/* 百分比文本居中显示在进度条上 */
.progress-percent {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 600;
  color: #111;
  pointer-events: none;
}

/* 文件个数显示在进度条右上方 */
.progress-count {
  position: absolute;
  right: 0;
  top: -18px;
  font-size: 12px;
  color: #555;
}

/* ===== 新增：上传状态卡片样式 ===== */
.upload-status-card .overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 调整文件概况卡片样式 */
.file-type-summary .overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px; /* 减小文件概况标题与文件数量之间的间隙 */
}

.file-count-badge {
  background: #eef2ff;
  color: #1d4ed8;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px; /* 增加“共x个”下方的间隙 */
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

/* 右侧状态文字颜色 */
.parse-status-text {
  font-size: 13px;
  font-weight: 600;
}

.parse-status-text.is-uploading {
  color: #1f2937; /* 深灰 */
}

.parse-status-text.is-success {
  color: #16a34a; /* 绿色 */
}

.parse-status-text.is-failed {
  color: #dc2626; /* 红色 */
}

/* 灰底绿色填充的进度条（要求） */
.bar-wrap {
  position: relative;
}

.bar-track {
  width: 100%;
  height: 10px;
  background-color: #e5e7eb; /* 灰底 */
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: #22c55e; /* 绿色填充 */
  width: 0%;
  transition: width 0.3s ease;
}

.bar-percent {
  font-size: 12px;
  color: #374151;
  margin-top: 4px;
  display: inline-block;
}

/* 分页器 */
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
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
</style>
