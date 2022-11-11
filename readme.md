[原文](https://medium.com/@oleg.agapov/full-stack-single-page-application-with-vue-js-and-flask-b1e036315532  )

[中文版教學網址](https://learnku.com/python/t/24985)

## VUE2環境創建

``` bash
#創建檔案資料夾
mkdir FLASKVUE

#創建前端環境
cd FLASKVUE
vue init webpack frontend

#創建後端環境
mkdir backend
cd backend
virtualenv -p python3 venv  #初始化一個虛擬環境
npm run build #在根目錄執行創建dist資校夾

#最後在根目錄中創建一個run.py

```
## 路徑調整  
>* 在 frontend/src/router/index.js 檔案中調整路徑  
>* 在 frontend/config/index.js 檔案中調整輸出目錄，讓帶有靜態檔案(css/html/js)的/dist資料夾跟/frontend資料夾同一個等級  
>* 在run.py中更改static_folder跟template_folder路徑  ([詳細資訊](https://medium.com/seaniap/python-web-flask-%E4%BD%BF%E7%94%A8%E9%9D%9C%E6%85%8B%E6%AA%94%E6%A1%88-ac00e863a470))
  

## VUE3環境創建

``` bash
#創建新專案
npm create vite@latest //選項中創建frontend

#安裝router
npm install vue-router@4

#安裝vuex
npm install vuex@next --save

#安裝scss
npm install --save-dev sass

#創建後端環境
mkdir backend
cd backend
virtualenv -p python3 venv  #初始化一個虛擬環境
npm run build #在根目錄執行創建dist資校夾

#最後在根目錄中創建一個run.py

```
## 使用element來美化網頁  
>* [element官網](https://element-plus.org/zh-CN/)  
>* 在'frontend\src\main.js'檔案中import ElementPlus from 'element-plus' 