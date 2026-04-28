import os
def get_file():
    #获取文件的绝对路径，稳定工程的路径
    current_file = os.path.abspath(__file__)
    #获取文件的目录
    current_dir = os.path.dirname(current_file)
    #获取文件的目录
    current_project = os.path.dirname(current_dir)
    return current_project
def get_file_path(file_name):
    path=get_file()
    return os.path.join(path,file_name)

if __name__ == '__main__':
    print(get_file_path("config/config.txt"))