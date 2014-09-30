# Python 中的私有对象

<br>

和某些语言使用保留关键字来声明不同, Python 使用命名规则来区分一个对象是公有的还是私有的,
通常我们看到以 `__name` 双下划线开头的对象就表示它是一个私有对象:

- 私有函数不可以从它们的模块外部被调用
- 私有类方法不能够从它们的类外部被调用
- 私有属性不能从它们的类外部被访问

```python
class Person(object):
    '''
    example class
    '''
    def __init__(self, name):
        self.name = name

    def __work(self, job):
        '''
        print out occupation
        '''
        if job[0] in 'aeiou':
            print('{0} is an {1}'.format(self.name, job))
        else:
            print('{0} is a {1}'.format(self.name, job))


if __name__ == '__main__':
    p = Person('Tom')
    p.__work('Engineer')
```

在这个例子中, `__work` 就是一个私有方法, 如果我们执行这个例子,
就会得到一个 `AttributeError`, 显示 `Person` 的实例没有 `__work` 方法,
因为该方法只能在类内部被调用.

实际上, Python 只是对私有字段进行了简单的重命名操作,
故而如果想在外部调用私有方法或属性, 只需要使用它重命名后的名称访问即可,

```
In [1]: p = Person('Tom')
In [2]: Person.__dict__
Out[2]: mappingproxy({
                        '__doc__': None,
                        '_Person__work': <function Person.__work at 0x103b61840>,
                        '__init__': <function Person.__init__ at 0x103b617b8>,
                        '__dict__': <attribute '__dict__' of 'Person' objects>,
                        '__module__': '__main__',
                        '__weakref__': <attribute '__weakref__' of 'Person' objects>
                      })
In [3]: p.__dir__()
Out[3]: [
           '__le__',
           '__eq__',
           '__init__',
           '__ge__',
           '__dict__',
           '__gt__',
           '__delattr__',
           '__doc__',
           '__setattr__',
           '__getattribute__',
           '__class__',
           '__str__',
           '__module__',
           '_Person__work',
           '__repr__',
           '__weakref__',
           '__new__',
           '__ne__',
           '__hash__',
           '__dir__',
           '__sizeof__',
           '__reduce__',
           '__format__',
           '__lt__',
           '__reduce_ex__',
           'name',
           '__subclasshook__']
In [4]: p._Person__work('Engineer')
Out[4]: Tom is an Engineer
```

我们看到, `__work` 被重命名为 `_Person__work`.
于是就可以通过 `p._Person__work('Engineer')` 从外部调用这个私有方法.
当然, 这样做是不被推荐的...

对于一些不是很关键的私有对象, 还可以使用 `_` 单下划线开头来命名,
这样命名的私有对象只示意它是一个私有的对象, 但是不会被重命名.
将这个例子简单修改后:

```python
class Person(object):
    '''
    example class
    '''
    def __init__(self, name):
        self.name = name

    def _work(self, job):
        '''
        print out occupation
        '''
        if job[0] in 'aeiou':
            print('{0} is an {1}'.format(self.name, job))
        else:
            print('{0} is a {1}'.format(self.name, job))

    def work(self, job):
        self._work(job)


if __name__ == '__main__':
    p = Person('Tom')
    p.work('Engineer')
    p._work('Researcher')
```

我们将 `__work` 方法改为单下划线命名后再次查看则发现 `_work` 没有被重命名可以直接调用.


### 变量 `_`

有一个需要特别注意的变量 `_`.
在交互式解释器比如 IDLE 或 iPython 中,
可以使用 `_` 获取最后一次计算的值.

```
In [1]: 4 / 2
Out[1]: 2.0

In [2]: _
Out[2]: 2.0
```

在源码中, 如果遇到了 `_` 变量,
通常它就是用来暂时存放一些 "必须要有, 但是又不会去使用" 的变量,

```python
import random

seq = []

for _ in range(100):
    seq.append(random.randint(-1, 1))
```
