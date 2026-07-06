# AI 综述项目

这是一个用于整理文献、提取文本和分析结果的本地项目。

## 目录说明

- `analyze.py`：主要分析脚本
- `extract_pdfs.py`：PDF 提取脚本
- `data/`：结构化数据和文章文本
- `sentiment_pdfs/`：情感分析相关 PDF
- `参考文献/`：参考资料与补充文件

## 本地运行

如果你只是查看或修改文件，直接用编辑器打开即可。

如果要运行脚本，请先确认你的 Python 环境已经安装好相关依赖，然后执行：

```powershell
python analyze.py
```

## GitHub 同步方式

1. 在 GitHub 上新建一个空仓库。
2. 在当前目录执行：

```powershell
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

## 给同学的使用方式

### 下载项目

```powershell
git clone https://github.com/你的用户名/你的仓库名.git
cd 仓库名
```

### 更新到最新版本

在项目目录里执行：

```powershell
git pull
```

### 提交自己的修改

```powershell
git add .
git commit -m "update"
git push
```

### 如果两个人都在改同一个仓库

建议每次改动前先：

```powershell
git pull
```

改完以后再：

```powershell
git add .
git commit -m "说明这次改了什么"
git push
```

这样可以避免版本冲突。
