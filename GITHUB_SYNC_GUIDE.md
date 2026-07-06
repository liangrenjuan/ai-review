# GitHub 同步与协作说明

这份说明可以直接发给同学。

## 1. 项目怎么获取

先安装 Git，然后执行：

```powershell
git clone https://github.com/你的用户名/你的仓库名.git
cd 仓库名
```

如果你已经有本地目录，也可以直接在目录里执行：

```powershell
git pull
```

## 2. 日常同步流程

### 先同步别人最新改动

```powershell
git pull
```

### 再修改文件

改代码、改文档、加数据都可以。

### 提交并上传

```powershell
git add .
git commit -m "本次修改说明"
git push
```

## 3. 冲突怎么处理

如果两个人改了同一个文件，`git pull` 可能会提示冲突。

处理原则：

1. 先打开冲突文件
2. 保留需要的内容
3. 删除冲突标记
4. 再执行 `git add .`
5. 再执行 `git commit`
6. 最后 `git push`

## 4. 不要提交的文件

下面这些文件通常不建议提交到 GitHub：

- 超大的压缩包
- 临时日志
- 缓存文件

当前项目里已经把 `seniment文献汇总.rar` 和 `run.log` 排除了。

## 5. 推荐协作习惯

- 每次开始干活前先 `git pull`
- 每次完成一小段就提交一次
- 提交信息写清楚改了什么
- 尽量不要两个人同时改同一个文件
