s = input()
start_char = ''
started = False
length = 0
longest = 0

for c in s:
	if c == 'o':
		
		if not started:
			started = True
		else:
			if start_char == '<':
				longest = max(longest, length + 2)
			length = 0
		start_char = 'o'
	elif c == '<':
		start_char = '<'
		started = True
		length = 0
	elif c == '>':
		if started and start_char == 'o':
			longest = max(longest, length + 2)
		length = 0
		started = False
		start_char = ''
	elif c == '*':
		if started:
			length += 1
	else:
		started = False
		start_char = ''
		length = 0


print(longest)