# 浙江旅行地图

一个交互式浙江省旅行足迹地图，覆盖 11 座城市、90+ 个区县，使用真实行政区划边界渲染。

![Zhejiang Travel Map](https://img.shields.io/badge/浙江省-11城市·90区县-667EEA)

## 功能

- **真实地理边界**：基于 DataV.GeoAtlas 的行政区划 GeoJSON 数据，SVG 渲染真实省市/区县形状
- **Catmull-Rom 曲线平滑**：地图边界使用样条曲线平滑处理，视觉效果圆润
- **6 级色阶足迹**：从"初探"到"老朋友"，打卡次数越多颜色越深
- **城市热力**：已打卡区县比例越高，城市颜色越深
- **旅行笔记**：每个区县可记录文字笔记和上传照片，自动保存到浏览器本地存储
- **数据导入/导出**：支持 JSON 格式备份与恢复，换设备也不丢数据
- **地图导出**：支持将标记后的地图导出为 3x 高清 PNG 图片
- **响应式布局**：适配桌面和移动端

## 在线体验

部署在 Vercel 上，访问：[你的 Vercel 链接]

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/zhejiang-travel-map.git
cd zhejiang-travel-map

# 直接用浏览器打开即可使用
open index.html

# 如需重新构建（更新 GeoJSON 数据）
cd build
npm install
python3 build_travel_map.py
# 生成的 travel-map.html 复制为根目录的 index.html
cp travel-map.html ../index.html
```

## 构建说明

构建脚本 `build/build_travel_map.py` 会：

1. 从 DataV.GeoAtlas API 拉取浙江省及 11 市的行政区划 GeoJSON
2. 压缩坐标精度（3 位小数）以减小文件体积
3. 将数据注入 HTML 模板
4. 通过 Babel 预编译 JSX 为 `React.createElement` 调用
5. 输出单文件 `travel-map.html`（约 800KB）

依赖：Python 3.8+、Node.js（用于 Babel 编译）

## 技术栈

- React 18（CDN UMD）
- SVG + Catmull-Rom 曲线投影
- Babel 预编译（classic JSX runtime）
- localStorage 持久化
- Python 构建流水线

## 数据来源

- 行政区划边界：[DataV.GeoAtlas](https://datav.aliyun.com/portal/school/atlas/area_selector)
- 旅游攻略：手工整理

## License

MIT
