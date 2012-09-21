import re
import ast

def clean_str(s):
  c=re.sub("[\x00-\x1F]", lambda x: "\\x%02X"%ord(x.group(0)), s.replace("\0", "").replace("\\","\\\\"))
  return c

RE_special = re.compile("(\\\\\\\\|\\\\x..)")

def decode(x):
    x=x.group(0)
    if x=="\\\\":
        return "\\"
    else:
        return chr(eval("0"+x[1:]))

def unclean_str(s):
    return RE_special.sub(decode, s)


if __name__ == "__main__":
    test="test\\test \n\1\2\3\26\32 demo\tdemo"
    print (test)
    test2=clean_str(test)
    print (test2)
    test3=unclean_str(test2)
    print (test3)
    print (test==test3)

    test='Re: \x1a\x1a\x1a\x1a'
    print (test)
    test2=clean_str(test)
    print (test2)
    test3=unclean_str(test2)
    print (test3)
    print (test==test3)
