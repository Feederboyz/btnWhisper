# BtnWhisper
![BtnWhisper Icon](images/128x128.png)

按下組合鍵，將語音轉換為文字。

## Prerequisite

-   Git
-   Anaconda

## Usage

-   程式開啟後，按下組合鍵（預設為 Ctrl+Alt+J）便開始錄音，按下第二次後便可將語音轉換成文字，並將文字貼在游標處
-   組合鍵可透過托盤系統（桌面右下角的小圖示）來設定

## Installation

使用 BtnWhisper 之前，需要先去 OpenAI 申請 [API key](https://platform.openai.com/api-keys)，價格為 [$0.006/minute](https://openai.com/api/pricing)。

### 使用執行檔

1. 創建檔案 `.env`，並於檔案中加入 `OPENAI_API_KEY=${YOUR_API_KEY}`
2. [下載](https://drive.google.com/file/d/1ihdYdQyQ5qwg1B7CjlP5vnZ0h5HrhPWf/view?usp=sharing)執行檔，並將檔案放在與 `.env` 放在同樣目錄中
3. 執行執行檔

### 自行架設環境

1. Clone repo

```
git clone https://github.com/Feederboyz/btnWhisper.git
cd btnWhisper
```

2. 建立、啟動環境

```
conda env create -f environment.yml
conda activate btnWhisper
```

3. 創建檔案 `.env`，並於檔案中加入 `OPENAI_API_KEY=${YOUR_API_KEY}`
4. 將 `.env` 放置於專案中
5. 執行 `python main.py`
