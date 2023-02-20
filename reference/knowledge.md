# 相关知识

## 验证主密码

https://wooyun.js.org/drops/%E5%8A%A0%E7%9B%90hash%E4%BF%9D%E5%AD%98%E5%AF%86%E7%A0%81%E7%9A%84%E6%AD%A3%E7%A1%AE%E6%96%B9%E5%BC%8F.html

### 基础

Hash算法是一种单向的函数。它可以把任意数量的数据转换成固定长度的“指纹”，这个过程是不可逆的。而且只要输入发生改变，哪怕只有一个bit，输出的hash值也会有很大不同。这种特性恰好合适用来用来保存密码。因为我们希望使用一种不可逆的算法来加密保存的密码，同时又需要在用户登陆的时候验证密码是否正确。

在一个使用hash的账号系统中，用户注册和认证的大致流程如下：

1. 用户创建自己的账号
2. 用户密码经过hash操作之后存储在数据库中。没有任何明文的密码存储在服务器的硬盘上。
3. 用户登陆的时候，将用户输入的密码进行hash操作后与数据库里保存的密码hash值进行对比。
4. 如果hash值完全一样，则认为用户输入的密码是正确的。否则就认为用户输入了无效的密码。
5. 每次用户尝试登陆的时候就重复步骤3和步骤4。

### 加盐

查表和彩虹表的方式之所以有效是因为每一个密码的都是通过同样的方式来进行hash的。如果两个用户使用了同样的密码，那么一定他们的密码hash也一定相同。我们可以通过让每一个hash随机化，同一个密码hash两次，得到的不同的hash来避免这种攻击。

具体的操作就是给密码加一个随即的前缀或者后缀，然后再进行hash。这个随即的后缀或者前缀成为“盐”。正如上面给出的例子一样，通过加盐，相同的密码每次hash都是完全不一样的字符串了。检查用户输入的密码是否正确的时候，我们也还需要这个盐，所以盐一般都是跟hash一起保存在数据库里，或者作为hash字符串的一部分。

盐不需要保密，只要盐是随机的话，查表，彩虹表都会失效。因为攻击者无法事先知道盐是什么，也就没有办法预先计算出查询表和彩虹表。如果每个用户都是使用了不同的盐，那么反向查表攻击也没法成功。

每一个用户，每一个密码都要使用不同的盐。用户每次创建账户或者修改密码都要使用一个新的随机盐。永远不要重复使用盐。盐的长度要足够，一个经验规则就是盐的至少要跟hash函数输出的长度一致。盐应该跟hash一起存储在用户信息表里。

### 总结

存储一个密码：

1. 使用CSPRNG生成一个长的随机盐。
2. 将密码和盐拼接在一起，使用标准的加密hash函数比如SHA256进行hash
3. 将盐和hash记录在用户数据库中

验证一个密码：

1. 从数据库中取出用户的盐和hash
2. 将用户输入的密码和盐按相同方式拼接在一起，使用相同的hash函数进行hash
3. 比较计算出的hash跟存储的hash是否相同。如果相同则密码正确。反之则密码错误。

```shell
>>> import hashlib
>>> m = hashlib.sha256()
>>> m.update(b"Nobody inspects")
>>> m.update(b" the spammish repetition")
>>> m.digest()
b'\x03\x1e\xdd}Ae\x15\x93\xc5\xfe\\\x00o\xa5u+7\xfd\xdf\xf7\xbcN\x84:\xa6\xaf\x0c\x95\x0fK\x94\x06'
>>> m.digest_size
32
>>> m.block_size
64
```

## 加密内容信息

We can use module `cryptography` in Python that generates a symmetric key for encrypting and decrypting data. Once we encrypted data using a symmetric key, it generates encrypted text for input data. Later, we require the same symmetric key for decrypting the encrypted text. We must preserve this symmetric key in a safe and secure location; otherwise, we cannot retrieve the decrypted data.

```Python
# Description: This program will be executed only when we have a new password file.

from cryptography.fernet import Fernet
import os

### 1. read your password file
with open('pwd.txt') as f:
    mypwd = ''.join(f.readlines())

### 2. generate key and write it in a file
key = Fernet.generate_key()
f = open("refKey.txt", "wb")
f.write(key)
f.close()

### 3. encrypt the password and write it in a file
refKey = Fernet(key)
mypwdbyt = bytes(mypwd, 'utf-8') # convert into byte
encryptedPWD = refKey.encrypt(mypwdbyt)
f = open("encryptedPWD.txt", "wb")
f.write(encryptedPWD)
f.close()
### 4. delete the password file
if os.path.exists("pwd.txt"):
  os.remove("pwd.txt")
else:
  print("File is not available")
```

## 转码

字符串在Python内部的表示是 unicode编码，因此，在做编码转换时，通常需要以unicode作为中间编码，即先将其他编码的字符串解码（decode）成unicode，再从unicode编码（encode）成另一种编码。

decode的作用是将其他编码的字符串转换成unicode编码，如str1.decode('gb2312')，表示将gb2312编码的字符串str1转换成unicode编码。

encode的作用是将unicode编码转换成其他编码的字符串，如str2.encode('gb2312')，表示将unicode编码的字符串str2转换成gb2312编码。

因此，转码的时候一定要先搞明白，字符串str是什么编码，然后decode成unicode，然后再encode成其他编码。
