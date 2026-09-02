<div align="center">

# NER Annotation Workbench Prototype

### NER 标注工作台原型

一个基于 Vue 3 与 Django 搭建的命名实体识别（NER）数据标注 Web 项目骨架。

[![Vue](https://img.shields.io/badge/Vue-3.5-42b883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.0-646cff?logo=vite&logoColor=white)](https://vite.dev/)
[![Django](https://img.shields.io/badge/Django-4.2-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-Planned-a30000)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Archived-lightgrey.svg)](#项目状态)

[English](README.md) | **简体中文**

</div>

> [!IMPORTANT]
> 本仓库是用于学习前后端分离架构与 NER 标注业务拆分的练习项目，当前停留在脚手架阶段。项目已结束且不再更新，不应直接用于生产环境。

## 项目简介

NER Annotation Workbench Prototype 最初用于探索一个面向命名实体识别任务的数据标注工作台。项目采用前后端分离结构，计划覆盖从原始文本导入、实体标注、数据概览到标注结果导出的基础流程。

当前仓库完成了 Vue 前端、Django 后端及业务模块的初始搭建，尚未实现完整的标注界面、数据模型和 REST API。仓库保留为学习记录和项目结构参考。

## 设计目标

项目规划的数据流如下：

```text
文本数据导入 → 命名实体标注 → 标注数据概览 → 标注结果导出
```

| 模块 | 规划职责 | 当前状态 |
| --- | --- | :---: |
| 数据导入 | 导入并解析待标注文本 | 仅创建 Django App |
| 数据标注 | 选择文本片段并分配实体标签 | 仅创建 Django App |
| 数据概览 | 展示数据量、标签和标注进度 | 仅创建 Django App |
| 数据导出 | 导出结构化标注结果 | 仅创建 Django App |
| Web 前端 | 提供标注与管理界面 | Vue 默认页面 |
| REST API | 连接前端与后端业务 | 尚未实现 |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite |
| 后端 | Python、Django、Django REST Framework |
| 数据库 | SQLite（Django 默认配置） |
| 项目结构 | 前后端分离 |

## 项目结构

```text
ner-annotation-workbench-prototype/
├── backend/
│   ├── config/                 # Django 项目配置
│   ├── data_import/            # 数据导入模块（骨架）
│   ├── data_annotation/        # 数据标注模块（骨架）
│   ├── data_overview/          # 数据概览模块（骨架）
│   ├── data_export/            # 数据导出模块（骨架）
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.vue             # Vue 默认示例页面
│   │   └── main.js             # 前端入口
│   ├── package.json
│   └── vite.config.js
├── docs/                       # 项目文档目录
├── CHANGELOG.zh-CN.md          # 简体中文更新日志
├── LICENSE
├── README.md                   # 英文文档
└── README.zh-CN.md             # 简体中文文档
```

## 快速开始

以下步骤仅用于运行当前脚手架，不能获得完整的 NER 标注功能。

### 环境要求

- Python 3.9 或更高版本
- Node.js 20.19+ 或 22.12+
- npm

### 运行后端

```bash
cd backend

# 建议使用虚拟环境
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

后端默认运行于 `http://127.0.0.1:8000/`。当前仅配置了 Django Admin 路由，业务 API 尚未实现。

### 运行前端

打开另一个终端：

```bash
cd frontend
npm install
npm run dev
```

根据终端提示访问本地开发地址。当前页面为 Vue 初始化示例页面。

### 构建前端

```bash
cd frontend
npm run build
```

## 当前限制

- 未定义文本、实体标签和标注结果的数据模型。
- 未实现数据导入、标注、统计或导出逻辑。
- 未提供 REST API、序列化器及业务路由。
- 未实现可交互的 NER 标注界面。
- 未集成任何 NER 模型，不支持模型训练、推理或自动预标注。
- 未提供完整的自动化测试和部署配置。
- Django 当前使用开发配置，不适合生产部署。

## 项目状态

**Archived / 已归档**

本项目作为个人练习项目保留，开发已经结束，后续不再维护或增加功能。仓库内容反映的是项目停止时的实际完成状态。

如需实际的文本标注能力，建议选择仍在维护的成熟标注平台；如需继续开发，可在现有模块划分基础上补充数据模型、API、前端交互及测试。

## 学习内容

该项目主要用于练习：

- Vue 与 Django 的前后端项目初始化；
- Django 多业务 App 的目录划分；
- NER 数据标注流程的模块化设计；
- 前后端分离项目的基础组织方式。

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

<div align="center">

该仓库仅作为学习记录保留。

</div>
