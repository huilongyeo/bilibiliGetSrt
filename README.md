### bilibiliGetSrt
**1. install library**
```
pip install selenium
pip install msedge-selenium-tools
```

**2. insert url**
If you are used bilibiliGetSrt first time, you need to login bilibili acount manual(cause some video need VIP, and after login, this application can locate correct episode) and save cookies.pcikle. With cookie, next time you would not to login again.

bilibiliGetSrt will find subtitle(if video has cc subtitle) and title of video automatically, but sometime title of video can't to open a file to save srt(maybe problem of special cahracter or to long title), bilibiliGetSrt will create a ``temp.srt`` and print the title, you can copy this title to rename the file.

Also, sometime bilibiliGetSrt can't find the srt even though video have cc subtuitle actually, you can run function again or change function sleep time at
```
# access again after driver get cookies
driver.get(url)
time.sleep(3)  # wait cc file response
# get video title
```
let driver wait cc subtitle response
