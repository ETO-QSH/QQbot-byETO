# 定义一个函数来创建文件
def create_files(start, end):
    for i in range(end, start + 1):
        file_name = f"D:\\Desktop\\Desktop\\educoder\\{i}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('')  # 写入空字符以确保文件不是完全空的


# 调用函数，创建文件
create_files(-27, -36)
