from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import datetime
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("缺少GOOGLE_API_KEY环境变量，请在.env文件中设置或直接添加到环境变量中")

# 初始化客户端
client = genai.Client(api_key=api_key)

# 获取用户提问
contents = input("请输入您的提问: ")
if not contents.strip():
    contents = '生成带插图的西班牙海鲜饭食谱'
    print(f"使用默认提问: {contents}")

# 创建时间戳，用于文件夹命名
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 从提问中提取关键词作为文件夹名称
# 移除特殊字符，取前几个词
folder_name = re.sub(r'[^\w\s]', '', contents)
folder_name = re.sub(r'\s+', '_', folder_name.strip())
folder_name = folder_name[:30]  # 限制长度
folder_name = f"{timestamp}_{folder_name}"

# 创建主文件夹
main_folder = os.path.join("generated_content", folder_name)
os.makedirs(main_folder, exist_ok=True)

# 创建图片文件夹
image_folder = os.path.join(main_folder, "images")
os.makedirs(image_folder, exist_ok=True)

# 生成内容
response = client.models.generate_content(
    model="models/gemini-2.0-flash-exp",
    contents=contents,
    config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
)

# 创建Markdown文件
md_file_path = os.path.join(main_folder, f"{folder_name}.md")
markdown_content = f"# {contents}\n\n"
image_paths = []

# 处理响应
for i, part in enumerate(response.candidates[0].content.parts):
    if part.text is not None:
        # 添加文本到Markdown内容
        print(part.text)
        markdown_content += part.text + "\n\n"
    elif part.inline_data is not None:
        # 生成图片文件名
        image_filename = f"image_{i+1}.png"
        image_path = os.path.join(image_folder, image_filename)
        image_rel_path = os.path.join("images", image_filename)
        
        # 保存图片
        image = Image.open(BytesIO(part.inline_data.data))
        image.save(image_path)
        print(f"图片已保存到: {image_path}")
        
        # 添加图片链接到Markdown
        markdown_content += f"![生成图片 {i+1}]({image_rel_path})\n\n"
        image_paths.append(image_path)
        
        # 显示图片
        image.show()

# 保存Markdown文件
with open(md_file_path, "w", encoding="utf-8") as md_file:
    md_file.write(markdown_content)

print(f"\n内容已保存到Markdown文件: {md_file_path}")
print(f"所有内容已保存在文件夹: {main_folder}")