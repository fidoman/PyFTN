
def readline(s):
  l=b""
  while True:
    c=s.recv(1)
    if len(c)==0:
      raise Exception("EOF")
    if c==b"\n":
      break
    l+=c
  return l

def readdata(s, length):
  while length:
    chunk = s.recv(length)
    if len(chunk)==0:
      raise Exception("EOF before got all binary data")
    length -= len(chunk)
    if length<0:
      raise Exception("got more data from socket than asked, check your platform")
    yield chunk

