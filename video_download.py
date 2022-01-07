import os
import re
import time

import requests
from Crypto.Cipher import AES
from selenium.webdriver import Chrome
from concurrent.futures import ThreadPoolExecutor

import shutil


def have_test_folder(folder_name, operation_method=None):
    if os.path.exists(f"{folder_name}/"):
        if operation_method == 0:
            os.rmdir(f"{folder_name}")
            print(f"已经删除{folder_name}文件夹")
        else:
            print(f"存在文件夹{folder_name}")
    else:
        if operation_method == 0:
            print(f"{folder_name}文件夹不存在,无法删除")
        else:
            os.mkdir(f"{folder_name}/")
            print(f"{folder_name}文件夹创建完成")


def open_file(file_name, open_file_mode, url_header=None):
    with open(file_name, mode=open_file_mode) as f:
        if open_file_mode == "r":
            flag_r_num = 0
            for line in f:
                if line.startswith("#"):
                    continue
                else:
                    flag_r_num += 1
                    line = line.strip()

                    if url_header is None:
                        download_ts_url = line
                    else:
                        download_ts_url = str(url_header) + line

                    print(download_ts_url)


def get_all_m3u8(url):
    obj1 = re.compile(r'<iframe id="fed-play.*?src="(?P<url>.*?)"></iframe>', re.S)
    web = Chrome()
    web.get(url)

    web.implicitly_wait(10)

    time.sleep(2)

    iframe = web.page_source
    result1 = obj1.finditer(iframe)

    for it in result1:
        url = it.group("url")

        url = url.rsplit("=", 1)[1]

        resp = requests.get(url)

        with open("index1.txt", "wb") as f:
            f.write(resp.content)
        f.close()
        resp.close()
        with open("index1.txt", "r", encoding="utf-8") as f:
            for line in f:

                if line.startswith("#"):
                    continue
                else:
                    if line.startswith("http"):
                        print("是一个完整的地址")
                        need_all_url = line.strip()
                        resp = requests.get(need_all_url)

                        with open("index2.txt", "wb") as f1:
                            f1.write(resp.content)
                        f1.close()
                    else:
                        line.strip()
                        need_end_url = line.split("/", 2)[1]

                        need_header_url = url.split("/" + need_end_url, 1)[0]

                        with open("need_url.txt", "w") as f1:
                            if need_header_url.endswith("index.m3u8"):
                                need_header_url = need_header_url.rstrip("index.m3u8")
                            else:
                                need_header_url = need_header_url
                            f1.write(need_header_url)
                        f1.close()

                        need_all_url = need_header_url + line.strip()

                        resp = requests.get(need_all_url)

                        with open("index2.txt", "wb") as f1:
                            f1.write(resp.content)
                        f1.close()

                        with open("need_url.txt", "w") as f1:
                            if need_all_url.endswith("index.m3u8"):
                                need_all_url = need_all_url.rstrip("index.m3u8")
                            else:
                                need_all_url = need_all_url
                            f1.write(need_all_url)
                        f1.close()
        f.close()


def have_key():
    obj = re.compile(r'.*?URI="(?P<url>.*?)"', re.S)
    with open("index2.txt", "r", encoding="utf-8") as f:

        for it in f:
            if it.startswith("#"):
                if it.strip().endswith('key.key\"'):
                    # print(it)

                    result = obj.finditer(it)

                    for i in result:
                        key_end_url = i.group("url")
                        # print(key_end_url)

                    break

                else:
                    key_end_url = ""
                    continue
    f.close()

    with open("need_url.txt", mode="r") as f:
        for i in f:
            if i == "":
                break
            else:

                key_url = i + "key.key"
    key_yes = ""
    if key_end_url != "":
        resp = requests.get(key_url)
        key_yes = resp.text
    return key_yes


def download_ts(folder_name, url, n):
    with open(f"{folder_name}/{n}.ts", mode="wb") as f1:
        resp = requests.get(url)
        f1.write(resp.content)
        print(f"{n}.ts下载完毕")


def dec_ts_video(folder_name, aes1, n):
    with open(f"{folder_name}/{n}.ts", mode="rb") as f121, open(f"temp/{n}.ts", mode="wb") as f122:
        bs = f121.read()
        f122.write(aes1.decrypt(bs))
        print(f"{n}.ts解码完成")


def merge_video(ts_folder_name, movie_name):
    print("开始合并视频")
    lst = []
    with open("index2.txt", mode="r", encoding="utf-8") as f:
        n = 1
        for line in f:
            if line.startswith("#"):
                continue
            else:
                line = line.strip()
                if line == "":
                    break
                else:
                    lst.append(f"{ts_folder_name}\\{n}.ts")
                    n += 1

        n = int((n / 400) + 2)

        for it in range(1, n):
            s = ""
            if it == n:
                s = "+".join(lst[it * 400:])
                commend = "copy /b " + s + f" {it}.mp4"
                os.system(commend)
            else:
                t = it - 1
                s = "+".join(lst[t * 400:it * 400])
                commend = "copy /b " + s + f" {it}.mp4"
                os.system(commend)
        #
        sd = ""
        for i in range(1, n):
            if i == n - 1:
                sd += f"{i}.mp4"
            else:
                sd += f"{i}.mp4" + "+"

        sd.rstrip("+")
        # print(sd)
        commend = "copy /b " + sd + f" {movie_name}"
        os.system(commend)
        print(n)
        for i in range(1, n):
            os.remove(f"{i}.mp4")


def download_all_video(download_ts_folder_name, movie_name):
    need_url = ""
    with open("need_url.txt", "r") as f:
        for i in f:
            need_url = i.strip()
    f.close()
    num = 0

    have_test_folder(download_ts_folder_name)

    with open("index2.txt", "r") as f:
        with ThreadPoolExecutor(50) as t:

            for line in f:
                if line.startswith("#"):
                    continue
                else:
                    if line.startswith("http"):
                        num += 1
                        line.strip()
                        url_all_ts = line.strip()

                        # print(url_all_ts)
                        if url_all_ts == "":
                            break
                        else:
                            url_all_ts.strip()
                            t.submit(download_ts, download_ts_folder_name, url_all_ts, num)
                    else:
                        num += 1
                        line.strip()
                        if line.startswith("/"):
                            line = line.rsplit("/", 1)[-1]
                        url_all_ts = need_url + line.strip()
                        # print(line)
                        # print(url_all_ts)
                        if url_all_ts == "":
                            break
                        else:
                            url_all_ts.strip()
                            t.submit(download_ts, download_ts_folder_name, url_all_ts, num)
    f.close()
    key = have_key().strip()
    if key == "":
        print("不需要解码直接合并视频")
        merge_video(download_ts_folder_name, movie_name)
        shutil.rmtree("video")
        os.remove("index1.txt")
        os.remove("index2.txt")
        os.remove("need_url.txt")
    else:
        have_test_folder("temp")
        num = 0
        with open("index2.txt", "r") as f1:

            with ThreadPoolExecutor(50) as t1:

                for line in f1:
                    if line.startswith("#"):
                        continue
                    else:
                        num += 1
                        if line == "":
                            break
                        else:
                            aes = AES.new(key=key, IV="0000000000000000", mode=AES.MODE_CBC)
                            t1.submit(dec_ts_video, download_ts_folder_name, aes, num)
        f1.close()
        print("解码成功！！")

        merge_video("temp", movie_name)
        shutil.rmtree("video")
        shutil.rmtree("temp")
        os.remove("index1.txt")
        os.remove("index2.txt")
        os.remove("need_url.txt")


if __name__ == '__main__':
    print("输入网站url:", end="")
    main_url = input()
    print("输入电影的文件名:", end="")
    movie_name = input()
    print("Hello World !!!")
    movie_name = f"D:\\华为云盘\\{movie_name}.mp4"

    get_all_m3u8(main_url)

    download_all_video("video", movie_name)
