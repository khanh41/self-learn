import cython_example_proj.wrapped as wd
import persons.person as ps

wd.c_hello()


per = ps.Person()

p = ps.Person()
p.name = b'zhangsan'
p.age = 18
p.say_hello()
print(p.name)
print(p.age)
