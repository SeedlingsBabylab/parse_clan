#This Script was written by Tessa Eagle, 2/2015.
from Tkinter import Tk
from tkFileDialog import askopenfilename
import os
import sys
import re

def output(f, s):
   f.write(s)
   #comment out next line if you don't want to see output in console
   sys.stdout.write(s)

class Parser:

   def __init__(self, ifile, ofile):
      self.out = ofile
      self.input_file = ifile
      self.timestamps = {}
      self.comment_pending = False
      self.skipping = False

   def process_line(self, line):
      line = line.replace('&cv', '').strip()
      line = line.replace('&CV', '').strip()
      line = line.strip()
      comment = "NA"
      if line.find("Total number of items") != -1:
         file_total = int(line.split()[0])
         print("file total: %d" % file_total)
         return
      elif line.startswith("%com"):
         com = line.split()
         if len(com) > 1:
            #use a regular epxression to test for weird comments
            m = re.search("^(\|)?([0-9a-zA-Z]+\|)+[0-9a-zA-Z]+(\|)?$", com[1])
            if not m:
               #not a weird comment
               if line[5:].strip() == 'begin skip':
                  self.skipping = True
               elif line[5:].strip() == 'end skip':
                  self.skipping = False
               else:
                  #not a weird comment so keep it
                  comment = line[5:].strip()
         if self.comment_pending:
            output(self.out, "%s\n" % comment)
         self.comment_pending = False
      elif not self.skipping and not line.startswith('@'):
         #not a comment so clear any pending comment state
         if self.comment_pending:
            output(self.out, "%s\n" % comment)
         self.comment_pending = False
         parts = line.split('\x15')
         if len(parts) != 3:
            #not enough parts
            return
         timestamp = parts[1]

         #test if we have seen this timestamp before, and if we have then
         #discard this line and continue onto the next
         if timestamp in self.timestamps:
            return
         self.timestamps[timestamp] = line
         text = parts[0].replace("&=vocalization",'')

         text = text.replace("&=crying",'')# EB added this
         text = text.replace("&=vfx",'') # EB added this
         text = text.replace('&cv', '')

         parts = text.split()
         colon = text.find(':')
         tier = text[:colon]
         text = text[colon+1:].strip()
         have_output = False
         while True:
            amp = text.find('&')
            if amp == -1:
               break
            word = text[:amp].strip()
            text = text[amp+1:]
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
            if have_output:
               #generating multiple lines of output from single input line
               output(self.out, 'NA\n')
            #print everything but the possible succeeding comment
            output(self.out, "%s,%s,%s,%s,%s,%s," % (tier, word, utterance_type, object_present, speaker, timestamp))
            have_output = True
            #what to do about multiple words on same line
            text = text[4 + len(speaker):].strip()
            #we generated some output so indicate that we should be ready for a comment
            self.comment_pending = True

   def parse(self):
      #print the header line
      output(self.out, "tier,word,utterance_type,object_present,speaker,timestamp,comment,basic_level\n")

      full_line = ''
      with open(self.input_file) as f:
         for line in f:
            if line.startswith('\t'):
               full_line = "%s %s" % (full_line.strip(), line.strip())
               continue
            elif len(full_line) > 0:
               self.process_line(full_line)
            full_line = line
      if len(full_line) > 0:
         self.process_line(full_line)
         if self.comment_pending:
            output(self.out, "NA\n")

      self.out.close()

if __name__ == "__main__":
   print(sys.platform)

   Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
   filename = askopenfilename(filetypes=[("cex files", "*.cex")]) # show an "Open" dialog box and return the path to the selected file
   #print(os.path.split(filename))
   #subID = os.path.split(filename)[1].split("_")
   #subID = subID[0] + '_' + subID[1]
   #print(subID)

   #input_file = os.path.join(os.path.dirname(os.path.realpath(filename)), subID + '_consensus.cex')
   input_file = os.path.realpath(filename)

   output_file = input_file[:-4] + '_processed.csv'
   print("saving to %s" % output_file)
   out = open(output_file, 'w')
   p = Parser(input_file, out)
   p.parse()
