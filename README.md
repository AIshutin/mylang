# MyLang

MyLang is a simple programming language designed by me for better understanding of how difficult is it and what process is looks like. 
Of course, it`s *not recommended to use it in production envienroment*. But I can not imagine how it could be done.

# Syntaxis

## Types
At this moment there is only one type: int which is type for unsinged integer in range 0...2 ** 8 - 1. You can not read integer violating it properly. But can store and print in range 0...2 ** 32 - 1.

## Declaration:
  int myvar
  
  You can also write ';' in the end of the string like: int myvar;
  
## Operations:
  MyLang supports only 2 operations: += and -=
  <variable> <operation> <variable or constant>

  To print myvar use: print(myvar)
  To read myvar use: get(myvar)

## Comments:

/* multi

  line
  
  comment*/
  
int codeline; // single line comment

You can set constants in decimal and hex:

int var = 0xa

var += 10

var -= 0xA

# Requirements:
   python3
   Linux x86_64
   NASM that is installed and is added to PATH
   
# How to run?
python3 MyLang.py source.mylang -o dest
