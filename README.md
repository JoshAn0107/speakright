# SpeakRight — 英语发音练习平台

在线英语发音练习与评测平台，服务于中国中小学英语教学。学生朗读单词/句子获得即时评分与反馈，老师管理班级、词库并布置作业。

**线上地址**: https://speakright.uk

## 功能

**学生端**
- 单词/词组朗读练习，多层评分（音素准确度、重音位置、韵律、流利度）
- 作业模式：连续朗读，后台并行评分，完成后查看成绩单
- 班级码加入班级，进度与连续练习天数统计

**老师端**
- 班级管理：班级码邀请、改名/备注、移除学生，学生平均分一览
- 词库管理：自建词库（支持按 Unit 分组）、批量导入、Excel 导出、回收站
- 词表文件上传适配（PDF/扫描件 → 人工适配为分组词库）
- 布置作业：按 Unit 一键选词 + 按班级一键分配
- 作业进度跟踪与逐词点评，意见反馈通道

**评分管线**（backend/app/services/）
- Azure Speech 发音评估 + 独立二次识别（防 reference 对齐脑补）
- 声学重音检测（CMUdict 词典重音 vs 元音响度/音高/时长突显度）
- 严格分数校准：读错词、漏读、重音错都会被压分并给出中文反馈
- 影子模式：每条录音同时发给自建 ML 模型（wav2vec2 GOP），双评分入库对照

## 目录结构

```
backend/           FastAPI 后端（评分管线、班级/词库/作业 API，SQLite）
frontend/          React + Vite 前端（Tailwind）
ml-service/        自建发音评分服务（wav2vec2 + CTC 对齐 + GOP，Azure 兼容 API）
ops/               部署与构建脚本（Kaldi GOP 管线等）
docker-deployment/ Docker 部署包
tests/             测试
DEPLOY.md          生产环境部署手册
```

## 快速开始

```bash
# 后端
cd backend
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env   # 填入 Azure Speech 密钥
./venv/bin/uvicorn app.main:app --port 8001

# 前端
cd frontend
npm install
npm run dev            # 开发
npm run build          # 生产构建（nginx 托管 dist/）
```

生产部署细节见 [DEPLOY.md](DEPLOY.md)。

## 技术路线

当前评分以 Azure Speech 为主，自建模型（GOP → GOPT，基于 speechocean762 校准）通过影子模式在真实数据上验证中，目标是国内部署（小程序）时替换云端依赖。
