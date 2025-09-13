<template>
  <div class="data-import-container">
    <!-- 文件上传区 -->
    <div class="upload-section card">
      <h3>文件上传</h3>
      <p>拖拽文件到此处或点击选择文件进行上传</p>
      <input type="file" @change="handleFileChange" multiple/>
    </div>

    <!-- 文件统计区 -->
    <div class="upload-info card">
      <h3>文件统计</h3>
      <div class="statistics-box">
        <div class="stat-item">
          <p>总文件数: {{ fileStats.totalFiles }}</p>
        </div>
        <div class="stat-item">
          <p>已解析: {{ fileStats.processedFiles }}</p>
        </div>
        <div class="stat-item">
          <p>解析失败: {{ fileStats.failedFiles }}</p>
        </div>
      </div>
    </div>

    <!-- 文件类型分布 -->
    <div class="file-type-distribution card">
      <h3>文件类型分布</h3>
      <div class="type-item" v-for="(value, type) in fileStats" :key="type">
        <p>{{ type }}: {{ value }}%</p>
      </div>
    </div>

    <!-- 上传进度 -->
    <div class="upload-progress card">
      <h3>上传进度</h3>
      <div v-for="(file, index) in uploadProgress" :key="index" class="progress-item">
        <span>{{ file.name }}</span>
        <progress :value="file.progress" max="100">{{ file.progress }}%</progress>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      fileStats: {
        totalFiles: 0,
        processedFiles: 0,
        failedFiles: 0,
        pdfFiles: 0,
        wordFiles: 0,
        jsonFiles: 0,
        txtFiles: 0
      },
      uploadProgress: []
    };
  },
  methods: {
    handleFileChange(event) {
      const files = event.target.files;
      this.fileStats.totalFiles = files.length;
      this.uploadFiles(files);
    },
    uploadFiles(files) {
      Array.from(files).forEach((file) => {
        this.uploadProgress.push({name: file.name, progress: 0});
        const formData = new FormData();
        formData.append("file", file);
        axios
            .post("http://localhost:8000/api/data-import/upload/", formData, {
              headers: {
                "Content-Type": "multipart/form-data"
              },
              onUploadProgress: (progressEvent) => {
                const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                const fileProgress = this.uploadProgress.find((item) => item.name === file.name);
                if (fileProgress) fileProgress.progress = percent;
              }
            })
            .then((response) => {
              this.fileStats.processedFiles++;
            })
            .catch((error) => {
              this.fileStats.failedFiles++;
            });
      });
    }
  }
};
</script>

<style scoped>
/* 基本容器样式 */
.data-import-container {
  padding: 20px;
  background-color: #f4f7fc;
  font-family: 'Noto Sans SC', sans-serif;
}

/* 卡片式样式 */
.card {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

/* 文件上传区 */
.upload-section {
  background-color: #e3f2fd;
  border-left: 8px solid #1e88e5;
  text-align: center;
}

.upload-section input {
  margin-top: 20px;
  padding: 10px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

/* 文件统计区 */
.upload-info {
  background-color: #f1f8e9;
  border-left: 8px solid #388e3c;
}

.statistics-box {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  width: 30%;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 文件类型分布 */
.file-type-distribution {
  background-color: #fff8e1;
  border-left: 8px solid #fbc02d;
}

.type-item {
  margin: 10px 0;
  font-weight: bold;
}

/* 上传进度条 */
.upload-progress {
  background-color: #fff3e0;
  border-left: 8px solid #fb8c00;
}

.progress-item {
  margin-bottom: 10px;
}

progress {
  width: 100%;
  height: 20px;
  border-radius: 10px;
}
</style>
