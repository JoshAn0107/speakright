# speakright.uk 部署说明（本机即生产服务器）

服务器：阿里云 47.82.101.191（Ubuntu 24.04，2GB swap 已配置）
域名：speakright.uk / www.speakright.uk（Let's Encrypt，certbot.timer 自动续期）

## 架构
- 前端：React + Vite，源码 /root/ilp_chinese/frontend，构建产物 frontend/dist 由 nginx 直接托管
- 后端：FastAPI (uvicorn :8001)，systemd 服务 ilp-cn-backend，代码 /root/ilp_chinese/backend
- 数据库：SQLite /root/ilp_chinese/backend/app.db
- nginx 配置：/etc/nginx/sites-available/speakright.uk（/ -> dist 静态文件；/api /docs /uploads -> :8001）

## 常用操作
- 改前端后发布：cd /root/ilp_chinese/frontend && npm run build && chmod -R o+rX dist
- 改后端后发布：systemctl restart ilp-cn-backend
- 看后端日志：journalctl -u ilp-cn-backend -f
- 后端依赖：backend/venv（pip install -r requirements.txt）
- 环境变量：backend/.env（AZURE_SPEECH_KEY / AZURE_REGION / DATABASE_URL）

## 备份
- 每日自动备份：/etc/cron.daily/backup-ilp -> /root/backups/ilp/（app.db + 上传的词表文件，保留14天）

## 词表适配流程
老师在网页词库页上传文件 -> 文件存 backend/wordlist_uploads/，记录在 wordlist_uploads 表（status=pending）
-> 人工解析导入 word_database_words（带 unit 分组）-> 更新 status=done + result_message

## 影子评分（shadow mode）
每条学生录音评分后，后台线程会把音频发给 SGP 服务器（159.89.193.226:8002，speakright-ml wav2vec2 GOP 模型）
再打一次分，结果写入 app.db 的 shadow_scores 表（azure_score / final_score / ml_pron_score 对照）。
- 失败不影响用户结果（fire-and-forget，错误记录在 ml_error 列）
- SGP 的 8002 端口 iptables 只对本机和 47.82.101.191 开放
- 对照分析：SELECT word_text, azure_score, ml_pron_score, ml_recognized FROM shadow_scores;
