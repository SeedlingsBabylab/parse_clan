#This Script was written by Tessa Eagle, 2/2015.
from Tkinter import Tk
from tkFileDialog import askopenfilename
import os
import sys
print sys.platform
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print os.path.split(filename)
subID = os.path.split(filename)[1].split("_")
subID = subID[0]+'_'+subID[1]
print subID
out = open(os.path.join(os.path.dirname(os.path.realpath(filename)),subID+'_consensus.frq.csv'), 'w')
out.write("tier,word,utterance_type,object_present,speaker,timestamp\n")

#print the header line
#print("tier,word,utterance_type,object_present,speaker,timestamp")
file_total = 0

timestamps = {}

with open(filename) as f:
   for line in f:
      line = line.replace('&cv', '').strip()
      line = line.strip()
      if line.find("Total number of items") != -1:
         file_total = int(line.split()[0])
         print("file total: %d" % file_total)
      if not line.startswith('*'):
         continue
      parts = line.split('\x15')
      if len(parts) != 3:
         continue
      timestamp = parts[1]

      #test if we have seen this timestamp before, and if we have then 
      #discard this line and continue onto the next
      if timestamp in timestamps:
         continue
      timestamps[timestamp] = line
      
      # drop out vocalizations, crying, and vfx codes from file
      
      text = parts[0].replace("&=vocalization",'')
      text = text.replace("&=crying",'')
      text = text.replace("&=vfx",'')
      print(text)
      parts = text.split()
      colon = text.find(':')
      tier = text[:colon]
      text = text[colon+1:].strip()
      while True:
         #ampersand seems to introduce utterance_type
         amp = text.find('&')
         if amp == -1:
            break
         word = text[:amp].strip()
         text = text[amp+1:]
         #can't split on | because one line had {# EB woops that was a typo should've been |; I fixed it in the input file)
         utterance_type = text[0]
         object_present = text[2]
         #speaker either extends to end of text at this point
         #or is followed by a space to introduce another word
         space = text.find(' ')
         if space != -1:
            speaker = text[4:space]
         else:
            speaker = text[4:]
         #print text
         #print ("%s,%s,%s,%s,%s,%s" % (tier, word, utterance_type, object_present, speaker, timestamp))
         out.write("%s,%s,%s,%s,%s,%s\n" % (tier, word, utterance_type, object_present, speaker, timestamp))
         #what to do about multiple words on same line
         text = text[4 + len(speaker):].strip()
           
out.close()
