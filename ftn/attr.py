attrs=[	"Private",
	"Crash",
	"Recd",
	"Sent",
	"FileAttached",
	"InTransit",
	"Orphan",
	"KillSent",
	"Local",
	"HoldForPickup",
	"unused",
	"FileRequest",
	"ReturnReceiptRequest",
	"IsReturnReceipt",
	"AuditRequest",
	"FileUpdateReq"
      ]

att=[	"Pvt",
	"Cra",
	"Rcd",
	"Snt",
	"Att",
	"Trs",
	"Orp",
	"K/S",
	"Loc",
	"HFP",
	"unused",
	"FRq",
	"RRq",
	"IRc",
	"ARq",
	"URq"
      ]

def short_to_long(a):
  for s, l in zip(att, attrs):
    if a.lower()==s.lower():
      return l
  raise Exception("unknown short attribute %s"%repr(a))

#def decode(a):
#  res=0
#  a=a.capitalize()
#  for i in range(16):#
#    if a.count(att[i].capitalize()):#
#      res+=1<<i
#  return res

def binary_to_text(a):
  r=[]
  for i in range(16):
    if (a&1)==1:
      r.append(attrs[i])
    a=a>>1
  return r

def text_to_binary(a):
  if type(a) is list:
    a=",".join(a)
  res=0
  a=a.upper()
  for i in range(16):
    if a.count(attrs[i].upper()):
      res+=1<<i
  return res
  