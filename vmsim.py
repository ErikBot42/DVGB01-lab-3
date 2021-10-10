#!/usr/bin/python3
# Written by Erik Magnusson and Rasmus Angeleni Gjein

class color:
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

import sys
import operator
import copy

def print_usage():
    print()
    print("Usage:")
    print("./vmsim.py -a <FIFO | OPTIMAL | LRU> -n <number of frames> -f <trace file>")

algorithms = ["FIFO", "OPTIMAL", "LRU"]

filename = ""
algorithm = algorithms[0]
num_frames = 0 # number of frames in physical memory
i = 0
while i<len(sys.argv):
    curr = sys.argv[i];i+=1
    if curr == "-a":
        algorithm = sys.argv[i];i+=1
    if curr == "-n":
        num_frames = int(sys.argv[i]);i+=1
    if curr == "-f":
        filename = sys.argv[i];i+=1

if filename=="" or not algorithm in algorithms or num_frames<1:
    print_usage()
    exit(1)

print("-------------------")
print("Algorithm:",algorithm)
print("Number of frames:",num_frames)
print("-------------------")

page_size = 256 # bytes
number_of_pages = 256 # => 64 KB virtual address space

def addressToPage(address):
    return int(address/page_size)


page_faults = 0
page_hits = 0

def page_hit(address):
    print("Address", color.RED, toHex(address),color.END, "got a page hit")
    global page_hits
    page_hits+=1

def page_fault(address):
    print("Address", color.RED, toHex(address),color.END , "got a page", color.RED, "fault",color.END)
    global page_faults
    page_faults+=1

class Page_element:
    frame = -1
    valid = False
    time = -1

class Page_table:
    elements = []
    def __init__(self, number_of_pages):
        for i in range(number_of_pages):
            self.elements.append(Page_element())

    def testValid(self, page, time=-1):
        valid = self.elements[page].valid
        self.elements[page].time = time
        if valid:
            page_hit(address)
        else:
            page_fault(address)
        return valid
    
    # load page to physical memory, replacing specific slot in physical memory
    def loadReplace(self, newPage, oldFrame, time = -1):
        unloadedPage = self.invalidateFrame(oldFrame)
        element = self.elements[newPage]
        element.frame = oldFrame
        element.valid = True
        element.time = time
        print("Page", newPage, "is replacing page", unloadedPage, ", Currently loaded:", self.getLoadedPages())


    def invalidateFrame(self,frame):
        for i in range(len(self.elements)):
            page = self.elements[i] 
            if page.frame == frame:
                if page.valid:
                    page.valid = False
                    return i

    def getOldestFrame(self):
        oldestFrame = None
        oldestTime = 1000000000000000
        for i in range(len(self.elements)):
            page = self.elements[i] 
            if page.valid and page.time<oldestTime:
                oldestFrame = page.frame
                oldestTime = page.time
        print("oldest frame is", oldestFrame)
        return oldestFrame

    def getLoadedPages(self):
        return [i for i,page in enumerate(self.elements) if page.valid]

page_table = Page_table(number_of_pages)


         

class Frame:
    data = ""
physical_memory = []

for i in range(num_frames):
    physical_memory.append(Frame())

addresses = []
with open(filename) as f:
    for line in f.readlines():
        addresses.append(int(line,16))

def toHex(number, digits=6):
    return "{0:#0{1}x}".format(number,digits)

for address in addresses:
    print(toHex(address))




print("-------------------")

def calcRecency(page, addresses):
    recency = 100000000
    for j in range(i,len(addresses)):
        addr = addresses[j]
        if page == addressToPage(addr):
            recency = j
            break
    return recency

if algorithm == "FIFO":
    i = 0
    for address in addresses:
        page = addressToPage(address)
        if not page_table.testValid(page):
            page_table.loadReplace(page, i)
            i=(i+1)%num_frames
elif algorithm == "LRU":
    framesUsed = 0
    i = 0
    time = 0
    for address in addresses:
        time+=1
        page = addressToPage(address)
        if not page_table.testValid(page, time):
            if framesUsed < num_frames:
                framesUsed+=1
                page_table.loadReplace(page, i, time)
                i+=1
            else:
                page_table.loadReplace(page, page_table.getOldestFrame(), time)
elif algorithm == "OPTIMAL":
    framesUsed = 0
    k = 0
    for i, address in enumerate(addresses):
        page = addressToPage(address)
        if not page_table.testValid(page):
            if framesUsed < num_frames:
                framesUsed+=1
                page_table.loadReplace(page, k)
                k+=1
            else:
                loadedPages = page_table.getLoadedPages()
                #print(loadedPages)
                lam = lambda a : calcRecency(a, addresses)
                loadedPages.sort(key=lam, reverse=False)
                #print([[loadedPage, calcRecency(loadedPage, addresses)] for loadedPage in loadedPages])
                page_table.loadReplace(page, loadedPages[0])



                



print("-------------------")
print(page_hits, "page hits,", page_faults, "page faults")


