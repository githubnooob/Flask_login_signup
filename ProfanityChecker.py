from profanityfilter import ProfanityFilter
profanityChecker = ProfanityFilter()


def check_word(word):
	if profanityChecker.is_clean(word):
		return word 
	else:
		return profanityChecker.censor(word)

