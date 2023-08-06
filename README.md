Chinese below 中文在下面
# Charmsit
Charmsbar is an interesting tool in Win8.

I want to bring it back to Win11 or other systems,even unix-like systems!

but my computer is too weak to test it in other systems,so it may not work properly in other systems.

# Code
it is writen in python 3.6.6 and tkinter tcl8.6

maybe it's not as good as charmsbar win win8, but i tried to make it better :)

now, it supports non-linar animation and multi-language

the project is just for fun, so i can't promise to make it perfect.

## Change Language
open config.json, set "main.language" to your language.the language files are in ./lang/yourlang.json.

## change max FPS
set "main.fps" to some other number, if not exists, it will be 30.

## animation
"main.animation":if true, you can enjoy the non-linar animation. if your computer is not so good, try to disable it.

# Chinese中文
我平时打代码懒得换输入法，所以注释也经常是(蹩脚的)英文，请见谅。

# Charmsit
Win8中有一个有意思的功能，Charmsbar。

我比较喜欢Metro的设计方式，正好从Win10开始Charmsbar也被移除了，我就打算自己写一个。

由于是用python写的，它支持多系统，但兼容性不保证，希望有人能帮忙测试。

# 代码
反正我就自己写写，几乎所有核心代码都挤在一个文件中，不过好歹比我以前的码风好多了。

这是用Python3.6.6和tk8.6写的，在python3.4下也能通过运行。

这个软件不一定会像原生的一样好，但我会努力做的好一点，还有，我希望做的更实用些，所以不会和原生的功能一样。

现在，这个软件已经支持非线性动画和多语言了。

本项目算是娱乐的，没法保证完善。

## 切换语言
（目前的开发板本）默认已经是中文了，还有这个必要吗？

修改config.json，设置"main.language"为目标语言，可以在./lang/语言.json 翻译，目前有中英两种。

## 修改最大帧率
"main.fps"这一项设置，没有默认为30。

## 动画
这个动画在电脑空闲时还挺不错，但电脑要是很卡可以考虑把"main.animation"设为零禁用动画效果。

建议设为1来看看这些界面动画，写出来可不容易qwq