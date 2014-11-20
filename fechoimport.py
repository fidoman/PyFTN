#!/usr/local/bin/python3 -bb

import sys
import os
import re
import time
import hashlib

re_UTIME=re.compile(".*? (\d{9,10}) .*")
re_FTRACK=re.compile(".*? (@\d\d\d\d\d\d\d\d\.\d\d\d\d\d\d)\.UTC .*?")
re_FTRACK3=re.compile(".*? (@\d\d\d\d\d\d\d\d\.\d\d\d\d\d\d)\.UTC\+3 .*?")
re_FTRACKUX=re.compile(".*? (\d\d \S\S\S \d\d\d\d \d\d:\d\d:\d\d) UTC\+(\d\d\d\d)")

re_CREATED=re.compile("(\S+) \(exported( .*?)? ([Bb]y .*)\)$")

import ftnconfig
import ftntic

fareas = ftnconfig.FAREASDIR

def read_info(f):
  tic = {}
  addto = None
  for l in open(f, encoding="cp866"):
    l = l.rstrip()
    if l.startswith("AREA: "):
      tic["AREA"]=[l[6:]]
    elif l.startswith("AREADESC: "):
      tic["AREADESC"]=[l[10:]]
    elif l.startswith("RECEIVED AS: "):
      tic["FILE"]=[l[13:]]
    elif l.startswith("RECEIVED FROM: "):
      infofrom=l[15:]
      m_crt=re_CREATED.match(infofrom)
      if m_crt:
        infofrom = m_crt.group(1)
        infodate = m_crt.group(2)
        infocrt = m_crt.group(3)
        print ("Complex from:", ", ".join(map(str, (infofrom, infodate, infocrt))))
        tic["CREATED"] = [infocrt]
        if infodate:
          tic["DATE"] = [infodate.strip()]
      tic["FROM"]=[infofrom]
    elif l.startswith("FROM: "):
      tic["DOWNLOADED"]=[l[6:]]
    elif l.startswith("REPLACED: "):
      tic["REPLACES"]=[l[10:]]
    elif l.startswith("ORIGIN: "):
      tic["ORIGIN"]=[l[8:]]
    elif l.startswith("FILE DATE: "):
      tic["DATE"]=[l[11:]]
    elif l.startswith("DATE: "):
      tic["DATE"]=[l[6:]]
    elif l.startswith("CRC: "):
      tic["CRC"]=[l[5:]]
    elif l.startswith("FREQ AS: "):
      tic["FREQ"]=[l[9:]]
    elif l.startswith("DECLARED SIZE: "):
      tic["SIZE"]=[l[15:]]
    elif l=="PATH ->":
      addto = tic.setdefault("PATH", [])
    elif l=="SEENBY ->":
      addto = tic.setdefault("SEENBY", [])
    elif l=="REPLACED ->":
      addto = tic.setdefault("REPLACES", [])
    else:
      if addto is not None:
        addto.append(l)
      else:
        raise Exception("cannot interpret [%s]"%repr(l))
  return tic

def filehash(f):
  h=hashlib.sha512()
  h.update(open(f,"rb").read())
  return h.hexdigest()

def filedigest(f):
  h=hashlib.sha512()
  h.update(open(f,"rb").read())
  return h.digest()

if __name__ == "__main__":
  if len(sys.argv)>1 and sys.argv[1]=="cleanup":
    db=ftnconfig.connectdb()
    for clean_dir in sys.argv[2:]:
      print ("cleaning files in", clean_dir)
      for folder, subfolders, files in os.walk(clean_dir):
        for file in files:
          if file in set(('files.bbs', 'FILES.FGN')):
            continue
          fullname=os.path.join(folder, file)
          hash = filedigest(fullname)
          for existing in db.prepare("select id, names from files where sha512=$1")(hash):
            print (fullname, existing)
            os.unlink(fullname)
            break
          else:
            n=db.prepare("select destination, (select length from files where id=filedata), filedata from file_post where filename=$1")(file.upper())
            if n:
              exist_dest, exist_len, exist_id = n[0]
              if os.path.getsize(fullname) == exist_len:
                print ("name and length match")
                os.unlink(fullname)
            print (fullname, "is new", n)

    exit()


  print ("FILEDATES")
  FILEDATES="filedates.dat"
  if not os.path.exists(FILEDATES):
    files=set()
    filedates = {}
    default_time = 1000018463
  
    for d in os.listdir(fareas):
      farea_dir = os.path.join(fareas, d)
      if not os.path.isdir(farea_dir):
        continue
      farea = d.upper()
  
      print (farea, farea_dir)
  
      for f in os.listdir(farea_dir):
        fname = os.path.join(farea_dir, f)
        if f.endswith(".desc"):
          #descs.add(f)
          pass
        elif f.endswith(".info"):
          #infos.add(f)
          try: 
            tic = read_info(fname)
          except Exception as e:
            print("error:", f, e)
            exit()
  
          sent = None
          if "DATE" in tic:
            try:
              sent = int(tic["DATE"][0])
            except:
              sent = time.mktime(time.strptime(tic["DATE"][0]))
  
          if sent is None and "PATH" in tic:
            chance = False
            for origin_rec in tic["PATH"]:
              if len(origin_rec)>30:
                chance = True
 
              try:
                sent=int(re_UTIME.match(origin_rec).group(1))
                break
              except Exception as e:
                print("no utime:", f, e, "\n", origin_rec)
  
              try:
                sent=re_FTRACK.match(origin_rec).group(1)
                sent=time.mktime(time.strptime(sent, "@%Y%m%d.%H%M%S"))
                break
              except Exception as e:
                print("no ftrtime:", f, e, "\n", origin_rec)
  
              try:
                sent=re_FTRACK3.match(origin_rec).group(1)
                sent=time.mktime(time.strptime(sent, "@%Y%m%d.%H%M%S"))+3*3600
                break
              except Exception as e:
                print("no ftr3time:", f, e, "\n", origin_rec)
   
              try:
                sent=re_FTRACKUX.match(origin_rec).group(1)
                senttz=re_FTRACKUX.match(origin_rec).group(2)
                sent=time.mktime(time.strptime(sent, "%d %b %Y %H:%M:%S"))+int(senttz[:2])*3600+int(senttz[2:4])*60
                break
              except Exception as e:
                print("no ftruxtime:", f, e, "\n", origin_rec)

 
            else:
              if chance:
                print("cannot get time from PATH", f)
                exit()
              else:
                print("no chances, continue...")
                sent = default_time
                default_time += 1

          filedates[fname[:-5]] = sent

        else:
          files.add(fname)


    fdfile = open(FILEDATES, "w")
    for f, d in filedates.items():
      print(f)
      fdfile.write(f+"\t"+str(int(d or default_time))+"\t"+filehash(f)+"\n")
      if not d:
        default_time += 1
      files.remove(f)
    for f in files:
      print(f)
      fdfile.write(f+"\t"+str(default_time)+"\t"+filehash(f)+"\n")
      default_time += 1
    fdfile.close()

  print ("read filedates by hash")
  fareas_hashes={}
  for l in open(FILEDATES):
    x=l.rstrip().split("\t")
    fareas_hashes.setdefault(x[2], []).append((x[0],x[1]))


  post_queue = open("post.dat","w")



# timestamp; type; filename
# type = "del" | "farea" | "arch"


  print("TIC ARCHIVE")
  TICARCHIVE="tics.dat"
  if not os.path.exists(TICARCHIVE):
    print("read tics")
    for inb in [ftnconfig.INBOUND, ftnconfig.DINBOUND]:
      #print (inb)
      for addr in os.listdir(inb):
        #print (addr)
        addrdir=os.path.join(inb, addr, "pwd-in-archive")
        if os.path.isdir(addrdir):
          for date in os.listdir(addrdir):
            #print (" ", date)
            datedir=os.path.join(addrdir, date)
            for hhmm in os.listdir(datedir):
              #print ("   ",hhmm)
              timedir=os.path.join(datedir,hhmm)
              #print(timedir)
              utime = time.mktime(time.strptime(date+hhmm, "%Y%m%d%H%M"))
              for f in os.listdir(timedir):
                fname=os.path.join(timedir, f)
                if f[-4:].upper()==".TIC":
                  tic=ftntic.read_tic(fname)
                  ticfile=os.path.split(ftntic.get_single(tic, "FILE"))[1]
                  try:
                    ticfname=ftntic.find_file(ticfile, timedir)
                  except ftntic.NoFile as e:
                    print("no file", utime, f, ticfile, e)
                    exit()
                  tichash=filehash(ticfname)
                  try:
                    fareas_same = fareas_hashes.pop(tichash)
                    for fs1, fs2 in fareas_same: # drop all files in areas if the same exists in posting
                      post_queue.write("\t".join((str(fs2), "del", fs1))+"\n")
                  except KeyError:
                    pass
                  post_queue.write("\t".join((str(int(utime)), "tic", fname))+"\n")

  for x in fareas_hashes.values():
    for fs1, fs2 in x:
      post_queue.write("\t".join((str(fs2), "farea", fs1))+"\n")

  post_queue.close()

# sort file with sort -n

# stop old tic processing
# import newly appeared files
# for links that have files in outbox make lastrecv as before oldest file
# clean outboxes
# make all new files to get to database
