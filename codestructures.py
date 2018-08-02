typenames = {"int": 4}
operations = {"+=", "-="}


class VarNameCreator:
	state = 0

	def __init__(self, state=0):
		self.state = state

	def char2latin(self, char):
		x = ('%s' % hex(ord(char)))[2:]
		#print(x, char)
		ans = []
		#print(x)
		for el in x:
			if '0' <= el <= '9':
				ans.append(chr(ord(el) - ord('0') + ord('A')))
			else:
				ans.append(chr(ord(el) + 10))
		return "".join(ans)

	def newvar(self, readable_varname):
		self.state += 1
		#print("newvar ", len(readable_varname))
		name = []
		for char in readable_varname:
			name.append(self.char2latin(char))
		#name.append(self.char2latin(str(self.state)))
		res = "z".join(name) + 'variable'
		#print(readable_varname, "->", res)
		return res


VarGen = VarNameCreator()

class Codeline:
	
	def process(self):	
		#print("line 45: ", self.tokens)
		#print(self.declarated)
		if (len(self.tokens) == 0 or len(self.tokens) == 1 and self.tokens[0] == ''):
			return
		if (self.tokens[0] in typenames): #this is declaration
			if len(self.tokens) == 1:
				#print("Invalid declaration in: %s" % (" ".join(self.tokens)))
				exit(0)
			name = self.tokens[1]
			self.declarated.append(name)
			self.data = '%s dd 0x0\n' % VarGen.newvar(name)
			#print("Declaration") #debug
			if (len(self.tokens) > 2):
				print("Operations after declacation are not supported: %s" % " ".join(self.tokens))
				print("Use <type> <varname>")
				exit(0)
		else:
			if len(self.tokens) == 1: 
				if self.tokens[0][0] == 'p': # print(myvar)
					myvarname = self.tokens[0][len("print("):-1]
					#print("printing... ", myvarname)
					myvar = "[" + VarGen.newvar(myvarname) + "]"
					self.external.append(myvarname)
					self.code += "\npush rax\nmov rax,%s\ncall printInt\nmov rax,endl\ncall print\npop rax\n" % myvar
				else:
					myvarname = self.tokens[0][len("get("):-1]
					#print("reading...", myvarname)
					myvar = VarGen.newvar(myvarname)
					#print("myvar", myvar)
					self.external.append(myvarname)
					#print()
					self.code += "\nmov rax, __buff2__\ncall getInput\nmov rax, __buff2__\nmov rbx, %s\ncall StrToInt\n" % myvar
			elif (len(self.tokens) != 3):
				print("Invalid format in %s. Only <myvarname> <operation> <const value (not expression) or varname>"  % " ".join(self.tokens))
				exit(0)
			else:
				'''
					push rax;
					mov rax, myvar1;
					add/sub rax, myvar2/const num;
					mov myvar1, rax;
					pop rax;
				'''
				#print("operation")
				self.external.append(self.tokens[0])
				myvar1 = "[" + VarGen.newvar(self.tokens[0]) + "]"
				myvar2 = self.tokens[2]
				if '0' <= myvar2[0] <= '9' and (len(myvar2) < 3 or myvar2[1] != 'x'):
					myvar2 = str(hex(int(myvar2)))
				elif len(myvar2) >= 3 and myvar2[:2] == '0x':
					pass
				else:
					self.external.append(myvar2)
					myvar2 = "[" + VarGen.newvar(myvar2) + "]"
				operation = "add"
				if self.tokens[1] == '-=':
					operation = "sub"
				#print(myvar1, myvar2)
				self.code = "\n" + "push rax\n" + "mov rax,%s\n" % myvar1
				self.code += operation + " rax,%s\n" % myvar2 + "mov %s,rax\n" % myvar1
				self.code += "pop rax\n" + "\n"
		#print(self.declarated)
		'''
		situations:
		declacation
		calling
		'''


	def __init__(self, codeline):
		self.offset = 0
		self.tokens = []
		self.OFFSET_SYMB = "    "
		self.external = []
		self.declarated = []
		self.code = ''
		self.data = ''

		while codeline.find(self.OFFSET_SYMB) == 0:
			self.offset += 1
			codeline = codeline[len(self.OFFSET_SYMB):]	
		self.tokens = [token for token in codeline.split(" ") if token != " "]	
		self.process()

	def __str__(self):
		return "Codeline{" + "offset: " + str(self.offset) + " tokens: " + str(self.tokens) + "}" 

	__repr__ = __str__	


class Codeblock:
	commands = []
	external = []
	declarated = []

	code = ''
	data = ''
	
	def process(self):
		#print("line 117")
		code = []
		data = []
		declvars = []
		extvars = []
		for el in self.commands:
			#print(el, el.declarated, el.external)
			data.append(el.data)
			code.append(el.code)
			declvars += (el.declarated)
			extvars += (el.external)
		
		self.code = "".join(code)
		self.data = "".join(data)

		if len(declvars) != len(set(declvars)):
			var = ''
			was = set()
			for el in declvars:
				if el not in was:
					was.add(el)
				else:
					var = el 
			print("Double declaration of variable %s" % var)	
			exit(0)

		new_vars = set(declvars)

		for el in extvars:
			if el not in new_vars:
				self.external.append(el)

		self.declarated = declvars

	
	def __init__(self, code):
		self.commands = code # codeblocks and codelines
		self.process()

	
	def __str__(self):
		if len(self.commands) != 0:
			OFFSET = self.commands[0].OFFSET_SYMB * self.commands[0].offset
		else:
			OFFSET = ""
		repr_string = [OFFSET + "{\n"]
		for el in self.commands:
			repr_string.append(OFFSET + str(el) + "\n")
		repr_string.append(OFFSET + "}\n")
		return "".join(repr_string)

	__repr__ = __str__


	def make_program(self):
		code = '''
section .bss
    __buff__ resb 100 ;only for nums
    __buff2__ resb 100
__buffsize__ equ 100

section .text
global _start
exit:
	mov	ebx,0
    mov eax,1
	int 0x80
	ret
StrToInt:
	push rdx
	mov rdx, rax
	dec rdx;
	xor rax, rax
	;mov rax, 13;
StrToIntLoop:
	inc rdx
	cmp byte [rdx], 0x30
	jl eNd
	push rdx
	mov dl, 0xA
	mul dl; al = al * 10
	pop rdx
	add al, [rdx]
	sub al, '0'
	jmp StrToIntLoop 
eNd: 
	mov byte [rbx], al; not correct value in al
	pop rdx
	ret
getInput:
	push rsi
	push rdi
	mov rdi, __buffsize__ - 1 + __buff2__
loopInput:
	mov byte [rdi], 0
	dec rdi
	cmp rdi, __buff2__
	jne loopInput
	mov rsi, rax
	xor rax, rax
	xor rdi, rdi
	mov rdx, __buffsize__
	syscall
	pop rdi
	pop rsi
	ret
print:
	push rdx
	push rcx
	push rbx
	xor rdx, rdx
loopPrint:
	cmp byte [rax + rdx], 0x0;
	je loopPrintEnd
	inc rdx; 
	jmp loopPrint
loopPrintEnd:
	mov rcx, rax
	mov rax, 4
    mov rbx, 1    ; first argument: file handle (stdout).
    int 0x80	  ; call kernel.
	pop rbx
	pop rcx
	pop rdx
	ret
printInt:
	push rbx
	push rdx
	mov rbx, __buff__ + __buffsize__ - 1;
	dec rbx;
	mov word [rbx], 0x0;
loopPrintInt:
	push rbx
	mov ebx, 10
	xor rdx, rdx
	div ebx; 
	pop rbx;
	dec rbx;
	mov [rbx], dl;
	add word [rbx], '0'
	cmp rax, 0
	jne loopPrintInt
	mov rax, rbx
	call print
	pop rdx
	pop rbx
	ret\n'''.replace("\t", " " * 4)
		code += "_start:\n" + self.code.replace("\n", "\n" + " " * 4) + "\n\n    call exit\n\n"
		code += "section .data\n" + self.data + "\nendl db 0xA, 0x0"
		return code