<!-- hide empty table header -->
<style>
    th:empty {
        display: none;
    }
</style>

# Python Project Structure

Reference: <https://docs.python-guide.org/writing/structure/>

## Structure of the Repository

### Sample Repository

```txt
README.rst
LICENSE
setup.py
requirements.txt
sample/__init__.py
sample/core.py
sample/helpers.py
docs/conf.py
docs/index.rst
tests/test_basic.py
tests/test_advanced.py
```

### The Actual Module

|||
| --- | --- |
| **Location** | `./sample/` or `./sample.py` |
| **Purpose**  | The code of interest |

If your module consists of only a single file, you can place it directly in the root of your repository.

### Setup.py

|||
| --- | --- |
| **Location** | `./setup.py` |
| **Purpose**  | Package and distribution management |

### Requirements File

|||
| --- | --- |
| **Location** | `./requirements.txt` |
| **Purpose**  | Development dependencies |

A pip requirements file should be placed at the root of the repository. It should specify the dependencies required to contribute to the project: testing, building, and generating documentation.

If your project has no development dependencies, or if you prefer setting up a development environment via setup.py, this file may be unnecessary.

### Documentation

|||
| --- | --- |
| **Location** | `./docs/` |
| **Purpose**  | Package reference documentation |

### Test Suite

|||
| --- | --- |
| **Location** | `./test_sample.py` or `./tests` |
| **Purpose**  | Package reference documentation |

To give the individual tests import context, create a `tests/context.py` file:

```python
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sample
```

Then, within the individual test modules, import the module like so:

```python
from .context import sample
```

This will always work as expected, regardless of installation method.

### Makefile

|||
| --- | --- |
| **Location** | `./Makefile` |
| **Purpose**  | Generic management tasks |

Make is an incredibly useful tool for defining generic tasks for your project.

Sample Makefile:

```makefile
init:
    pip install -r requirements.txt

test:
    py.test tests

.PHONY: init test
```

### Regarding Django Applications

Many developers are structuring their repositories poorly due to the new bundled application templates.

How? Well, they go to their bare and fresh repository and run the following, as they always have:

```sh
django-admin.py startproject samplesite
```

The resulting repository structure looks like this:

```txt
README.rst
samplesite/manage.py
samplesite/samplesite/settings.py
samplesite/samplesite/wsgi.py
samplesite/samplesite/sampleapp/models.py
```

Repetitive paths are confusing for both your tools and your developers. Unnecessary nesting doesn’t help anybody (unless they’re nostalgic for monolithic SVN repos).

Let’s do it properly:

```sh
django-admin.py startproject samplesite .
```

The resulting structure:

```txt
README.rst
manage.py
samplesite/settings.py
samplesite/wsgi.py
samplesite/sampleapp/models.py
```

## Structure of Code is Key

Some signs of a poorly structured project include:

- Multiple and messy circular dependencies
- Hidden coupling
- Heavy usage of global state or context
- Spaghetti code: unstructured and difficult-to-maintain source code
- Ravioli code: metaphor for small, self-contained classes of code, which resemble individual pieces of pasta. It describes code that comprises well-structured classes that are easy to understand in isolation, but difficult to understand as a whole.

## Modules

Python modules are one of the main abstraction layers available and probably the most natural one. Abstraction layers allow separating code into parts holding related data and functionality.

For example, a layer of a project can handle interfacing with user actions, while another would handle low-level manipulation of data. The most natural way to separate these two layers is to regroup all interfacing functionality in one file, and all low-level operations in another file. In this case, the interface file needs to import the low-level file. This is done with the `import` and `from ... import` statements.

To keep in line with the style guide, keep module names short, lowercase, and be sure to avoid using special symbols like the dot (`.`) or question mark (`?`).

In the case of `my.spam.py` Python expects to find a `spam.py` file in a folder named `my` which is not the case.

If you like, you could name your module `my_spam.py`, but even our trusty friend the underscore, should not be seen that often in module names. However, using other characters (spaces or hyphens) in module names will prevent importing (`-` is the subtract operator). **Try to keep module names short so there is no need to separate words.** And, most of all, don’t namespace with underscores; use **submodules** instead.

```python
# OK
import library.plugin.foo
# not OK
import library.foo_plugin
```

You need to understand the import mechanism in order to use this concept properly and avoid some issues.

Concretely, the `import modu` statement will look for the proper file, which is `modu.py` in the same directory as the caller, if it exists. If it is not found, the Python interpreter will search for `modu.py` in the “path” recursively and raise an `ImportError` exception when it is not found.

When `modu.py` is found, the Python interpreter will execute the module in an isolated scope. Any top-level statement in `modu.py` will be executed, including other imports if any. Function and class definitions are stored in the module’s dictionary.

Then, the module’s variables, functions, and classes will be available to the caller through the module’s namespace.

In many languages, an include file directive is used by the preprocessor to take all code found in the file and ‘copy’ it into the caller’s code. It is different in Python: the included code is *isolated* in a **module namespace**, which means that you generally don’t have to worry that the included code could have unwanted effects, e.g. override an existing function with the same name.

It is possible to simulate the more standard behavior by using a special syntax of the import statement: `from modu import *`. This is generally considered bad practice. Using `import *` makes the code harder to read and makes dependencies less compartmentalized.

**Very bad**

```python
[...]
from modu import *
[...]
x = sqrt(4)  # Is sqrt part of modu? A builtin? Defined above?
```

**Better**

```python
from modu import sqrt
[...]
x = sqrt(4)  # sqrt may be part of modu, if not redefined in between
```

**Best**

```python
import modu
[...]
x = modu.sqrt(4)  # sqrt is visibly part of modu's namespace
```

## Packages

Python provides a very straightforward packaging system, which is simply an extension of the *module* mechanism to a *directory*.

Any directory with an `__init__.py` file is considered a Python package. Different modules in the package are imported in a similar manner as plain modules, but with a special behavior for the `__init__.py` file, which is used to gather all package-wide definitions.

A file `modu.py` in the directory `pack/` is imported with the statement `import pack.modu`. This statement will look for `__init__.py` file in pack and execute all of its top-level statements. Then it will look for a file named `pack/modu.py` and execute all of its top-level statements. After these operations, any variable, function, or class defined in `modu.py` is available in the `pack.modu` namespace.

A commonly seen issue is adding too much code to `__init__.py` files. When the project complexity grows, there may be *sub-packages* and sub-sub-packages in a deep directory structure. In this case, importing a single item from a sub-sub-package will require executing all `__init__.py` files met while traversing the tree.

Leaving an `__init__.py` file empty is considered normal and even good practice, if the package’s modules and sub-packages do not need to share any code.

Lastly, a convenient syntax is available for importing deeply nested packages: `import very.deep.module as mod`. This allows you to use mod in place of the verbose repetition of `very.deep.module`.

### Difference between modules, sub-modules, packages and sub-packages

```txt
package
├── __init__.py
├── module.py
└── sub_package
    ├── __init__.py
    └── sub_module.py
```

Consider packages and sub-packages as folders and sub-folders containing `__init__.py` file with other python files.

Modules are the python files inside the package.

Sub-modules are the python files inside the sub-package.

## Object-oriented programming

In Python, everything is an object, and can be handled as such. This is what is meant when we say, for example, that functions are first-class objects. Functions, classes, strings, and even types are objects in Python: like any object, they have a type, they can be passed as function arguments, and they may have methods and properties.

However, unlike Java, Python does not impose object-oriented programming as the main programming paradigm. It is perfectly viable for a Python project to not be object-oriented, i.e. to use no or very few class definitions, class inheritance, or any other mechanisms that are specific to object-oriented programming languages.

Moreover, the way Python handles modules and namespaces gives the developer a natural way to ensure the encapsulation and separation of abstraction layers. Therefore, Python programmers have more latitude as to not use object-orientation, when it is not required by the business model.

There are some reasons to avoid unnecessary object-orientation. Defining custom classes is useful when we want to glue some state and some functionality together. The problem comes from the “state” part of the equation.

In some architectures, typically web applications, multiple instances of Python processes are spawned as a response to external requests that happen simultaneously. In this case, holding some state in instantiated objects, which means keeping some static information about the world, is prone to concurrency problems or race conditions. Sometimes, between the initialization of the state of an object (usually done with the `__init__()` method) and the actual use of the object state through one of its methods, the world may have changed, and the retained state may be outdated. For example, a request may load an item in memory and mark it as read by a user. If another request requires the deletion of this item at the same time, the deletion may actually occur after the first process loaded the item, and then we have to mark a deleted object as read.

This and other issues led to the idea that using stateless functions is a better programming paradigm.

Another way to say the same thing is to suggest using functions and procedures with as few implicit contexts and side-effects as possible. A function’s **implicit context** is made up of any of the global variables or items in the persistence layer that are accessed from within the function. **Side-effects** are the changes that a function makes to its implicit context. If a function saves or deletes data in a global variable or in the persistence layer, it is said to have a side-effect.

Carefully isolating functions with context and side-effects from functions with logic (called pure functions) allows the following benefits:

- Pure functions are deterministic: given a fixed input, the output will always be the same.
- Pure functions are much easier to change or replace if they need to be refactored or optimized.
- Pure functions are easier to test with unit tests: There is less - need for complex context setup and data cleaning afterwards.
- Pure functions are easier to manipulate, decorate, and pass around.

In summary, pure functions are more efficient building blocks than classes and objects for some architectures because they have no context or side-effects.

## Decorators

A decorator is a function or a class that wraps (or decorates) a function or a method. The ‘decorated’ function or method will replace the original ‘undecorated’ function or method. Because functions are first-class objects in Python, this can be done ‘manually’, but using the `@decorator` syntax is clearer and thus preferred.

```python
def foo():
    # do something

def decorator(func):
    # manipulate func
    return func

foo = decorator(foo)  # Manually decorate

@decorator
def bar():
    # Do something
# bar() is decorated
```

This mechanism is useful for separating concerns and avoiding external unrelated logic ‘polluting’ the core logic of the function or method. A good example of a piece of functionality that is better handled with decoration is **memoization** or **caching**: you want to store the results of an expensive function in a table and use them directly instead of recomputing them when they have already been computed. This is clearly not part of the function logic.

## Context Managers

A context manager is a Python object that provides extra contextual information to an action. This extra information takes the form of running a *callable* upon initiating the context using the with statement, as well as running a callable upon completing all the code inside the with block. The most well known example of using a context manager is shown here, opening on a file:

```python
with open('file.txt') as f:
    contents = f.read()
```

Anyone familiar with this pattern knows that invoking open in this fashion ensures that `f`’s `close` method will be called at some point. This reduces a developer’s cognitive load and makes the code easier to read.

There are two easy ways to implement this functionality yourself: using a *class* or using a *generator*. Let’s implement the above functionality ourselves, starting with the class approach:

```python
class CustomOpen(object):
    def __init__(self, filename):
        self.file = open(filename)

    def __enter__(self):
        return self.file

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.file.close()

with CustomOpen('file') as f:
    contents = f.read()
```

`CustomOpen` is first instantiated and then its `__enter__` method is called and whatever `__enter__` returns is assigned to `f` in the `as f` part of the statement. When the contents of the with block is finished executing, the `__exit__` method is then called.

The generator approach using Python’s own contextlib:

```python
from contextlib import contextmanager

@contextmanager
def custom_open(filename):
    f = open(filename)
    try:
        yield f
    finally:
        f.close()

with custom_open('file') as f:
    contents = f.read()
```

This works in exactly the same way as the class example above, albeit it’s more terse. The `custom_open` function executes until it reaches the `yield` statement. It then gives control back to the `with` statement, which assigns whatever was `yield`’ed to `f` in the `as f` portion. The `finally` clause ensures that `close()` is called whether or not there was an exception inside the `with`.

The class approach might be better if there’s a considerable amount of logic to encapsulate. The function approach might be better for situations where we’re dealing with a simple action.

## Dynamic typing

Python is dynamically typed, which means that variables do not have a fixed type. Variables are not a segment of the computer’s memory where some value is written, they are ‘tags’ or ‘names’ pointing to objects.

The dynamic typing of Python is often considered to be a weakness, and indeed it can lead to complexities and hard-to-debug code. Something named ‘a’ can be set to many different things, and the developer or the maintainer needs to track this name in the code to make sure it has not been set to a completely unrelated object.

Some guidelines help to avoid this issue:

- Avoid using the same variable name for different things.

**Bad**

```python
a = 1
a = 'a string'
def a():
    pass  # Do something
```

**Good**

```python
count = 1
msg = 'a string'
def func():
    pass  # Do something
```

It is better to use different names even for things that are related, when they have a different type:

**Bad**

```python
items = 'a b c d'  # This is a string...
items = items.split(' ')  # ...becoming a list
items = set(items)  # ...and then a set
```

There is no efficiency gain when reusing names: the assignments will have to create new objects anyway. However, when the complexity grows and each assignment is separated by other lines of code, including ‘if’ branches and loops, it becomes harder to ascertain what a given variable’s type is.

Some coding practices, like functional programming, recommend never reassigning a variable. In Java this is done with the *final* keyword. Python does not have a *final* keyword and it would be against its philosophy anyway. However, it may be a good discipline to avoid assigning to a variable more than once, and it helps in grasping the concept of mutable and immutable types.

## Mutable and immutable types

Mutable types are those that allow in-place modification of the content. Typical mutables are lists and dictionaries: All lists have mutating methods, like `list.append()` or `list.pop()`, and can be modified in place. The same goes for dictionaries.

Immutable types provide no method for changing their content. For instance, the variable `x` set to the integer `6` has no “increment” method. If you want to compute `x + 1`, you have to create another integer and give it a name.

```python
my_list = [1, 2, 3]
my_list[0] = 4
print(my_list)  # [4, 2, 3] <- The same list has changed

x = 6
x = x + 1  # The new x is another object
```

Using properly mutable types for things that are mutable in nature and immutable types for things that are fixed in nature helps to clarify the intent of the code.

One peculiarity of Python that can surprise beginners is that strings are immutable. This means that when constructing a string from its parts, appending each part to the string is inefficient because the entirety of the string is copied on each append. Instead, it is much more efficient to accumulate the parts in a list, which is mutable, and then glue (`join`) the parts together when the full string is needed. *List comprehensions* are usually the fastest and most idiomatic way to do this.

**Bad**

```python
# create a concatenated string from 0 to 19 (e.g. "012..1819")
nums = ""
for n in range(20):
    nums += str(n)   # slow and inefficient
print(nums)
```

**Better**

```python
# create a concatenated string from 0 to 19 (e.g. "012..1819")
nums = []
for n in range(20):
    nums.append(str(n))
print("".join(nums))  # much more efficient
```

**Best**

```python
# create a concatenated string from 0 to 19 (e.g. "012..1819")
nums = [str(n) for n in range(20)]
print("".join(nums))
```

One final thing to mention about strings is that using `join()` is not always best. In the instances where you are creating a new string from a pre-determined number of strings, using the addition operator is actually faster. But in cases like above or in cases where you are adding to an existing string, using `join()` should be your preferred method.

```python
foo = 'foo'
bar = 'bar'

foobar = foo + bar  # This is good
foo += 'ooo'  # This is bad, instead you should do:
foo = ''.join([foo, 'ooo'])
```
