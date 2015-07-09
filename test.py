g = open('FT/positive-words.txt')
pos_words_string = str(g.read())
pos_words_list = pos_words_string.split()

h = open('FT/negative-words.txt')
neg_words_string = str(h.read())
neg_words_list = neg_words_string.split()

pos = 0
neg = 0 

wordslist = ['resourceful', 'respect', 'restful', 'revel']

for word_index in range (0,4):
	word = wordslist[word_index]
	# if check(wordslist[word_index], 'FT/positive-words.txt'):
	# 	pos += 1
	# elif check(wordslist[word_index], 'FT/negative-words.txt'):
	# 	neg += 1
	if word in pos_words_list:
		print word
		pos += 1
	elif word in neg_words_list:
		neg +=1

print 'Positive words = ', pos
print 'Negative words = ', neg