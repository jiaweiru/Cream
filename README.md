# Cream – 音频与文本处理工具包

Cream 是一个轻量、易用的音频与文本数据处理工具包，提供统一的处理框架、命令行工具（CLI）以及常用的进度与日志工具。适合快速拼装数据处理流程或为后续模型/算法集成提供骨架。

- 语言/运行时：Python 3.13（见 `pixi.toml`）
- CLI：基于 Typer，输出使用 Rich
- 日志：使用 Loguru
- 并行：`multiprocessing` 封装，支持进度条

## 功能概览

- 音频处理
  - 重采样：`audio_resampler`（基于 librosa、soundfile）
  - 归一化：`audio_normalizer`（依赖外部 `ffmpeg-normalize` 命令）
- 文本处理与分析（模板）
  - `basic_text_normalizer`、`text_translator`、`text_statistics_analyzer` 当前为模板实现，会抛出未实现错误（便于后续接入真实逻辑）
- 工具
  - 文件采样/拷贝：`FileSampler` + CLI `cream utils sample`
  - 正则索引匹配：`IndexMatcher` + CLI `cream utils index-match`

## 代码架构

- `cream/core`
  - `config.py`：全局配置（支持格式列表、并行/进度开关、日志等）
  - `logging.py`：Loguru 日志封装（`setup`、`get_logger`）
  - `processor.py`：处理器基类与注册中心
    - `BaseProcessor`、`ModelBackedProcessor`
    - 全局注册表 `processor_registry`
    - 装饰器工厂 `register_processor(name)`
  - `parallel.py`：简单并行调度 + 进度显示
  - `exceptions.py`：自定义异常（`CreamError` 等）
- `cream/audio`
  - `audio_processor.py`：音频域基类 `BaseAudioProcessor` 与统一接口 `AudioProcessorInterface`
  - `processing.py`、`analysis.py`：具体处理器示例，通过 `@register_processor` 自动注册
- `cream/text`
  - `text_processor.py`：文本域基类与统一接口
  - `processing.py`、`analysis.py`：模板处理器（目前抛未实现错误）
- `cream/utils`
  - `progress.py`：Rich 进度工具，遵循 `config.enable_progress_bars`
  - `file_ops.py`：文件采样/拷贝与统计
  - `indexing.py`：基于正则的索引提取与匹配
- `cream/cli`
  - `main.py`：主入口 `cream`
  - `audio.py`、`text.py`、`utils.py`：对应子命令实现

注册机制：处理器模块通过 `@register_processor("unique_name")` 装饰器完成注册，CLI 与统一接口通过注册表发现并创建实例。

## 安装

项目使用 pixi（conda 生态）管理环境：

- 安装 pixi（参考 https://pixi.sh/ ）
- 在项目根目录执行：

```
pixi install
pixi run python -c "import cream; print(cream.__version__)"
```

注意：
- `audio_normalizer` 依赖外部命令 `ffmpeg-normalize`，需自行安装（参见其项目主页）。
- `audio_resampler` 需要 `librosa`、`soundfile`，已在 `pixi.toml` 中声明。

## 使用方法（CLI）

- 安装为命令后可直接使用 `cream`。若未安装控制台入口，可用 `python -m cream.cli.main` 替代下述命令中的 `cream`。

- 查看版本/帮助

```
cream --version
cream --help
cream audio --help
cream text --help
cream utils --help
```

- 列出可用方法

```
cream audio list-methods
cream text list-methods
```

- 音频处理

```
# 单文件重采样到 22.05 kHz（默认）
cream audio process input.wav audio_resampler --output out.wav

# 目录批处理（输出到目录，支持 --workers）
cream audio process ./data audio_resampler --output ./out --workers 4

# 归一化（需要安装 ffmpeg-normalize）
cream audio process input.wav audio_normalizer --output norm.wav
```

- 工具命令

```
# 随机采样文件
cream utils sample ./data ./sampled --count 100 --pattern "*.wav"

# 基于正则的索引匹配（结果默认打印前 10 条，可指定 --output 保存）
cream utils index-match ./labels.json ./transcripts \
  --pattern "(\\d+)" --output matches.json
```

## 编程接口（简要）

- 音频接口

```python
from pathlib import Path
from cream.audio.audio_processor import AudioProcessorInterface

processor = AudioProcessorInterface(method="audio_resampler")
result = processor.process_file(Path("input.wav"), Path("out.wav"))
```

- 文件采样

```python
from pathlib import Path
from cream.utils.file_ops import FileSampler

sampler = FileSampler(seed=42)
sampled = sampler.sample_directory(Path("./data"), Path("./out"), count=100, pattern="*.wav")
```

## 扩展处理器（模板）

新增一个处理器（以音频为例）：

```python
from pathlib import Path
from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor

@register_processor("my_audio_method")
class MyAudioProcessor(BaseAudioProcessor):
    def process_single(self, input_path: Path, output_path: Path | None = None, **kwargs):
        self.validate_input(input_path)
        # 在这里实现你的处理逻辑，并返回结果/输出路径
        return output_path or input_path
```

注册完成后，CLI 可通过 `cream audio process ... my_audio_method` 使用。

## 约定与注意事项

- 仅在需要时输出进度条：由 `config.enable_progress_bars` 控制。
- 并行度：优先由 CLI `--workers` 设置，底层读取 `config.max_workers`。
- 日志：使用 `cream.core.logging.get_logger(__name__)`；CLI 可通过 `--log-level`、`--log-file` 控制。
- 模板处理器当前会抛出未实现异常，属于占位用法，不会静默失败。

## 许可证

本仓库未附带许可证声明；如需开源发布，请根据需要添加。
