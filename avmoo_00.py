from gevent import monkey
monkey.patch_all()

import gevent,requests,time,os
from gevent.queue import Queue
from bs4 import BeautifulSoup

# 下载同一类别/演员的所有 大封面图 & 样品图像

headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
# work = Queue()
start = time.time()

def get_path():                                                # 确认域名及演员/类别，准备下载路径
    dominate = input ('请选择爬取对象(0=女优,1=类别): ')   
    series = input ('请输入演员或者类别名称：')
    path_0 = r'D:\Python项目\下载' 

    if dominate   ==   '0':
        path_1 = os.path.join(path_0,'AVMOO\\0.女优')
        path = os.path.join(path_1,series)

    elif dominate ==   '1':
        path_1 = os.path.join(path_0,'AVMOO\\1.类别')
        path = os.path.join(path_1,series)
    
    else:
        path_1 = os.path.join(path_0,'接驳车')
        path = os.path.join(path_1,series)                    

    
    if os.path.exists(path):
        print ('文件夹已存在:',path)
    else:
        os.mkdir(path)
        os.mkdir(path+'\\'+'样品图像')
        print ('新建文件夹:',path,'& .\样品图像(子文件夹)')

    return path

def collection ():                                             # 页数(电影数)确认 & 链接整理
    start = time.time()
    headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    
    url_00 = input('请输入类别/演员/系列链接：')
    url_0 = url_00 + '/page/'
    n = 1 
    url_list = [ ]
    movies = { }

    with open ('1.txt','w') as file:                           # 创建临时记事本
        file.write('类别/系列/演员:'+ url_00 +'\n' )

    while requests.get(url_0+str(n)):                          # 逐页请求直至无响应，并把相应地址装入请求列表：url_list = [ ]。
        url = url_0 + str(n)
        print (url)
        url_list.append(url)
        time.sleep(0.2)
        n = n + 1
  
        res = requests.get(url,headers=headers)                # 请求信息
        soup = BeautifulSoup(res.text,'html.parser')           # 解析信息
        items = soup.find_all(class_ ='movie-box')             # 提取信息

        
        for item in items:                                     # 提取影片番号/标题/下级链接
            href = 'https:'+item['href']
            fh = item.find('date').text
            src = item.find('img')['src']
            title = item.find('img')['title']
            
            movies[href] = fh
            print (fh,href)                                    # movie信息

            with open ('1.txt','a') as file:                   # 储存影片链接，字典封装
                file.write(href+'\n')

    tell_me = '系列电影搜集结果：共 {} 页 ({}部), 用时：{}秒'.format(len(url_list),len(movies),int(time.time()-start))
    print (tell_me)
    time.sleep(3)

    return [url_list,movies,tell_me]           # 多返回值打包成列表输出待用，就很棒 [ [链接列表] , {影片链接:番号} ] 

    result = collection ()             # 调用方法备注
    list = result[0]                   #
    dict = result[1]                   #

def dlmovieimg (url):                                        # 爬取/下载一部电影里的封面图&样品图像

    res = requests.get(url,headers=headers)
    print (url,res.status_code,int(time.time()-start),'秒响应,开始下图')           # 检查请求是否正常回应
    time.sleep (0.1)

    soup = BeautifulSoup(res.text,'html.parser')            # 解析网站，到此为止一切正常

    bigimage = soup.find(class_='bigImage')['href']         # 提取信息封面图片下载地址
    title = soup.find(class_='bigImage')['title']           # 获取影片番号及影片名

    res = requests.get(bigimage,headers=headers)
    pic = res.content

    a = 0
    path_1 = path + '\\' + title + ' - 封面图像 - 0.jpg'
    with open (path_1,'wb') as p:
        p.write(pic)
        a = a + 1

    b = 0    
    items = soup.find_all(class_='sample-box')              # 提取影片截图下载地址                 
    for item in items:                                      # 下载其他图片
        src = item['href']
        title1 = item['title']
        
        res = requests.get(src)
        pic = res.content

        path_2 = path + '\\' + '样品图像\\' + title1 + '.jpg'  
        with open (path_2,'wb') as p:
            p.write(pic)
            b = b + 1
                     
    print('下载完成,去检查文件夹吧~，本片用时：{}秒，{}张样品图像; '.format(int(time.time()-start),b),title[0:30])    # 
    return [a,b]
    

def main():

    start = time.time()
    cl = collection()                  # 调用collect函数准备
    list = cl[0]                       
    movies = cl[1]
    tell_me = cl[2]

    tasks_list = []

    for url in movies:
        task = gevent.spawn(dlmovieimg,url)
        tasks_list.append(task)
    gevent.joinall(tasks_list)

    print (tell_me)
    print ('系列电影下载结果：用时:{}秒 {}张封面 {}张样品图像'.format(int(time.time()-start),len(movies),len(tasks_list)))


path = get_path()
main ()
